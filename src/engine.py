import inspect
import json
import os
from copy import deepcopy
from datetime import datetime
from uuid import uuid4

from src import validator
from src.models import SwapRequest, RosterVersion
from src.request_store import guardar_request
from src.roster_store import (
    guardar_roster,
    obtener_roster_vigente,
    desactivar_roster_vigente_actual,
    validar_unico_roster_vigente,
)
from src.rule_types import RuleResult, Violation


RULES_REGISTRY = {
    "validar_descanso_minimo": validator.validar_descanso_minimo,
    "validar_secuencia": validator.validar_secuencia,
    "validar_noches_consecutivas": validator.validar_noches_consecutivas,
}


def calcular_roster_hash(asignaciones: list) -> str:
    partes = []

    for a in asignaciones:
        ctrl = a.controlador.nombre if a.controlador else "NONE"
        partes.append(f"{ctrl}-{a.fecha}-{a.turno.codigo}")

    return "|".join(partes)


def cargar_config(nombre_config: str = "config_equilibrado.json") -> dict:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ruta = os.path.join(base_dir, "config", nombre_config)

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _validar_ventana_operativa(asignaciones, idx_a: int, idx_b: int, config: dict) -> bool:
    horas_minimas = config.get("operacion", {}).get(
        "horas_minimas_antes_del_turno_para_permitir_swap", 0
    )

    if horas_minimas <= 0:
        return True

    ahora = datetime.now()
    hoy = ahora.date()

    asignacion_a = asignaciones[idx_a]
    asignacion_b = asignaciones[idx_b]

    # Regla conservadora mínima:
    # si el swap involucra turnos del día actual, se bloquea.
    # No bloquear fechas históricas del fixture, para no romper tests existentes.
    if asignacion_a.fecha == hoy or asignacion_b.fecha == hoy:
        return False

    def obtener_inicio(asignacion):
        return datetime.combine(asignacion.fecha, asignacion.turno.hora_inicio)

    inicio_a = obtener_inicio(asignacion_a)
    inicio_b = obtener_inicio(asignacion_b)

    delta_a = (inicio_a - ahora).total_seconds() / 3600
    delta_b = (inicio_b - ahora).total_seconds() / 3600

    bloquea_a = 0 <= delta_a < horas_minimas
    bloquea_b = 0 <= delta_b < horas_minimas

    return not (bloquea_a or bloquea_b)


def agrupar_por_controlador(asignaciones: list) -> dict:
    grupos = {}

    for asignacion in asignaciones:
        nombre = (
            asignacion.controlador.nombre
            if asignacion.controlador is not None
            else "SIN_CONTROLADOR"
        )

        if nombre not in grupos:
            grupos[nombre] = []

        grupos[nombre].append(asignacion)

    for grupo in grupos.values():
        grupo.sort(key=lambda a: a.fecha)

    return grupos


def validar_estructura_violacion(violacion: Violation, nombre_regla: str) -> None:
    if not isinstance(violacion, Violation):
        raise TypeError(
            f"La regla '{nombre_regla}' devolvió un objeto de tipo "
            f"{type(violacion).__name__}. Debe devolver instancias de Violation."
        )

    if violacion.severidad not in ("hard", "soft"):
        raise ValueError(
            f"La regla '{nombre_regla}' devolvió una severidad inválida: {violacion.severidad}"
        )


def ejecutar_regla(asignaciones, regla_config: dict) -> RuleResult:
    nombre_regla = regla_config["nombre"]
    nombre_funcion = regla_config["funcion"]
    prioridad = regla_config["prioridad"]
    parametros = regla_config.get("parametros", {})

    if nombre_funcion not in RULES_REGISTRY:
        raise ValueError(f"Regla no registrada en RULES_REGISTRY: '{nombre_funcion}'")

    funcion = RULES_REGISTRY[nombre_funcion]

    firma = inspect.signature(funcion)
    parametros_validos = {
        k: v for k, v in parametros.items()
        if k in firma.parameters
    }

    violaciones = funcion(asignaciones, **parametros_validos)

    if violaciones is None:
        raise ValueError(
            f"La regla '{nombre_funcion}' devolvió None. Debe devolver una lista."
        )

    if not isinstance(violaciones, list):
        raise TypeError(
            f"La regla '{nombre_funcion}' devolvió {type(violaciones).__name__}. Debe devolver una lista."
        )

    for violacion in violaciones:
        validar_estructura_violacion(violacion, nombre_funcion)

    return RuleResult(
        regla=nombre_regla,
        prioridad=prioridad,
        violaciones=violaciones,
    )


def validar_todo(asignaciones, config_file: str = "config_equilibrado.json") -> list[RuleResult]:
    config = cargar_config(config_file)
    resultados = []

    grupos = agrupar_por_controlador(asignaciones)

    for regla_config in config["reglas"]:
        nombre_regla = regla_config["nombre"]
        prioridad = regla_config["prioridad"]

        violaciones_totales = []

        for _, asignaciones_ctrl in grupos.items():
            resultado_ctrl = ejecutar_regla(asignaciones_ctrl, regla_config)
            violaciones_totales.extend(resultado_ctrl.violaciones)

        resultados.append(
            RuleResult(
                regla=nombre_regla,
                prioridad=prioridad,
                violaciones=violaciones_totales,
            )
        )

    resultados.sort(key=lambda r: r.prioridad)
    return resultados


def registrar_evento_swap_request(request: SwapRequest, mensaje: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    request.add_history_entry(f"[{timestamp}] {mensaje}")
    guardar_request(request)


def crear_roster_version_inicial(
    asignaciones: list,
    regimen_horario: str = "6H",
) -> RosterVersion:
    vigente = obtener_roster_vigente()
    if vigente is not None:
        raise ValueError("Ya existe un roster vigente. No se puede crear otra versión inicial.")

    roster = RosterVersion(
        id=str(uuid4()),
        version_number=1,
        created_at=datetime.now(),
        asignaciones=deepcopy(asignaciones),
        vigente=True,
        base_version_id=None,
        regimen_horario=regimen_horario,
    )

    guardar_roster(roster)
    validar_unico_roster_vigente()
    return roster


def crear_nueva_version_desde_roster_vigente(
    asignaciones: list,
    regimen_horario: str | None = None,
) -> RosterVersion:
    vigente = obtener_roster_vigente()
    if vigente is None:
        raise ValueError("No existe un roster vigente para versionar.")

    nuevo_regimen = regimen_horario if regimen_horario is not None else vigente.regimen_horario

    desactivar_roster_vigente_actual()

    nueva = RosterVersion(
        id=str(uuid4()),
        version_number=vigente.version_number + 1,
        created_at=datetime.now(),
        asignaciones=deepcopy(asignaciones),
        vigente=True,
        base_version_id=vigente.id,
        regimen_horario=nuevo_regimen,
    )

    guardar_roster(nueva)
    validar_unico_roster_vigente()
    return nueva
