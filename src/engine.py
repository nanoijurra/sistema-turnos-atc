import json
import os
from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from src import validator
from src.models import SwapRequest, RosterVersion
from src.request_store import guardar_request, listar_requests
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
    """
    Genera una firma simple del roster basada en controlador, fecha y turno.
    """
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
    violaciones = funcion(asignaciones, **parametros)

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


def registrar_evento_roster_versionado(
    request: SwapRequest,
    roster_anterior: RosterVersion,
    roster_nuevo: RosterVersion,
) -> None:
    registrar_evento_swap_request(
        request,
        (
            f"Nueva versión de roster generada: "
            f"anterior=v{roster_anterior.version_number} ({roster_anterior.id}), "
            f"nueva=v{roster_nuevo.version_number} ({roster_nuevo.id})"
        ),
    )


def crear_swap_request(
    controlador_a: str,
    controlador_b: str,
    idx_a: int,
    idx_b: int,
    motivo: str | None = None,
) -> SwapRequest:
    request = SwapRequest(
        id=str(uuid4()),
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=idx_a,
        idx_b=idx_b,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo=motivo,
    )

    registrar_evento_swap_request(
        request,
        f"Request creado: {controlador_a}[{idx_a}] <-> {controlador_b}[{idx_b}]",
    )

    return request


def evaluar_swap_request(
    asignaciones: list,
    request: SwapRequest,
    evaluar_swap_fn,
    config_file: str = "config_equilibrado.json",
) -> dict:
    if request.decision_sugerida is not None:
        raise ValueError("El request ya fue evaluado.")

    if not (0 <= request.idx_a < len(asignaciones)) or not (0 <= request.idx_b < len(asignaciones)):
        raise IndexError("Los índices del SwapRequest no son válidos para el roster actual.")

    asignacion_a = asignaciones[request.idx_a]
    asignacion_b = asignaciones[request.idx_b]

    if asignacion_a.controlador is None or asignacion_b.controlador is None:
        raise ValueError("Las asignaciones no tienen controlador asociado.")

    if asignacion_a.controlador.nombre != request.controlador_a:
        raise ValueError(
            f"Inconsistencia en controlador A: request={request.controlador_a}, roster={asignacion_a.controlador.nombre}"
        )

    if asignacion_b.controlador.nombre != request.controlador_b:
        raise ValueError(
            f"Inconsistencia en controlador B: request={request.controlador_b}, roster={asignacion_b.controlador.nombre}"
        )

    roster_vigente = obtener_roster_vigente()
    if roster_vigente is None:
        raise ValueError("No existe un roster vigente para evaluar el request.")

    evaluacion = evaluar_swap_fn(
        asignaciones=asignaciones,
        idx_a=request.idx_a,
        idx_b=request.idx_b,
        config_file=config_file,
    )

    clasificacion = evaluacion["clasificacion"]

    if clasificacion == "BENEFICIOSO":
        decision = "APROBABLE"
    elif clasificacion == "ACEPTABLE":
        decision = "OBSERVAR"
    else:
        decision = "RECHAZAR"

    request.estado = "EVALUADO"
    request.decision_sugerida = decision
    request.roster_hash = calcular_roster_hash(asignaciones)
    request.roster_version_id = roster_vigente.id
    guardar_request(request)

    registrar_evento_swap_request(
        request,
        (
            f"Request evaluado: clasificacion={clasificacion}, decision={decision}, "
            f"roster_version_id={roster_vigente.id}, version_number={roster_vigente.version_number}"
        ),
    )

    return {
        "request_id": request.id,
        "controlador_a": request.controlador_a,
        "controlador_b": request.controlador_b,
        "clasificacion": clasificacion,
        "decision": decision,
        "evaluacion": evaluacion,
        "roster_version_id": roster_vigente.id,
        "roster_version_number": roster_vigente.version_number,
    }


def resolver_swap_request(
    request: SwapRequest,
    accion: str,
) -> SwapRequest:
    if request.decision_sugerida is None:
        raise ValueError("No se puede resolver un request sin evaluarlo primero.")

    if request.estado in ("ACEPTADO", "RECHAZADO", "CANCELADO", "APLICADO"):
        raise ValueError("El request ya fue resuelto.")

    if request.estado != "EVALUADO":
        raise ValueError(
        f"Estado inválido para resolver request: {request.estado}. Se esperaba EVALUADO."
    )

    if accion == "ACEPTAR":
        request.estado = "ACEPTADO"
    elif accion == "RECHAZAR":
        request.estado = "RECHAZADO"
    elif accion == "CANCELAR":
        request.estado = "CANCELADO"
    else:
        raise ValueError(f"Acción inválida: {accion}")

    request.fecha_resolucion = datetime.now()
    guardar_request(request)

    registrar_evento_swap_request(
        request,
        f"Request resuelto: accion={accion}, estado={request.estado}",
    )

    return request


def cancelar_requests_obsoletos(roster_version_id_viejo: str) -> int:
    """
    Cancela automáticamente todos los SwapRequest que:
    - estén en estado PENDIENTE o EVALUADO
    - pertenezcan a una versión de roster que dejó de ser vigente
    """
    requests = listar_requests()
    cancelados = 0

    for req in requests:
        if req.roster_version_id != roster_version_id_viejo:
            continue

        if req.estado in ("PENDIENTE", "EVALUADO"):
            req.cancelar_por_obsolescencia()
            guardar_request(req)
            cancelados += 1

    return cancelados


def aplicar_swap_request(
    asignaciones: list,
    request: SwapRequest,
) -> RosterVersion:
    """
    Aplica el swap generando una NUEVA versión de roster y cancela requests
    obsoletos de la versión anterior.
    """
    # 🔒 Debe haber sido evaluado
    if request.decision_sugerida is None: 
        raise ValueError("No se puede aplicar un request que no fue evaluado.")

    if request.estado != "ACEPTADO":
        raise ValueError("Solo se puede aplicar un SwapRequest con estado ACEPTADO.")

    # 🔒 Debe existir roster vigente
    roster_vigente = obtener_roster_vigente()
    if roster_vigente is None:
        raise ValueError("No existe un roster vigente para aplicar el request.")

    # 🔒 Debe coincidir versión
    if request.roster_version_id != roster_vigente.id:
        raise ValueError("El request ya no apunta a la versión vigente del roster.")

    # 🔒 Validación de coherencia
    if not (0 <= request.idx_a < len(asignaciones)) or not (0 <= request.idx_b < len(asignaciones)):
        raise IndexError("Los índices del SwapRequest no son válidos para el roster actual.")

    asignacion_a = asignaciones[request.idx_a]
    asignacion_b = asignaciones[request.idx_b]

    if asignacion_a.controlador is None or asignacion_b.controlador is None:
        raise ValueError("Las asignaciones no tienen controlador asociado.")

    if asignacion_a.controlador.nombre != request.controlador_a:
        raise ValueError(
            f"Inconsistencia en controlador A al aplicar: request={request.controlador_a}, roster={asignacion_a.controlador.nombre}"
        )

    if asignacion_b.controlador.nombre != request.controlador_b:
        raise ValueError(
            f"Inconsistencia en controlador B al aplicar: request={request.controlador_b}, roster={asignacion_b.controlador.nombre}"
        )

    roster_version_id_viejo = roster_vigente.id

    # 🔁 Generar nuevo roster (swap)
    nuevo_roster = deepcopy(asignaciones)

    turno_a = nuevo_roster[request.idx_a].turno
    turno_b = nuevo_roster[request.idx_b].turno

    nuevo_roster[request.idx_a] = replace(nuevo_roster[request.idx_a], turno=turno_b)
    nuevo_roster[request.idx_b] = replace(nuevo_roster[request.idx_b], turno=turno_a)

    # 🧠 NUEVA VERSIÓN
    nueva_version = crear_nueva_version_desde_roster_vigente(
        nuevo_roster,
        regimen_horario=roster_vigente.regimen_horario,
    )

    # ❌ Cancelar requests obsoletos de la versión anterior
    cancelar_requests_obsoletos(roster_version_id_viejo)

    registrar_evento_swap_request(
        request,
        f"Swap aplicado → nueva version {nueva_version.version_number}",
    )

    return nueva_version