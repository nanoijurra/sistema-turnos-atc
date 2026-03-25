import json
import os
from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from src import validator
from src.models import SwapRequest
from src.request_store import guardar_request
from src.rule_types import RuleResult, Violation


RULES_REGISTRY = {
    "validar_descanso_minimo": validator.validar_descanso_minimo,
    "validar_secuencia": validator.validar_secuencia,
    "validar_noches_consecutivas": validator.validar_noches_consecutivas,
}


def cargar_config(nombre_config: str = "config_equilibrado.json") -> dict:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ruta = os.path.join(base_dir, "config", nombre_config)

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def agrupar_por_controlador(asignaciones: list) -> dict:
    """
    Agrupa asignaciones por controlador.
    Si no hay controlador, usa SIN_CONTROLADOR para mantener compatibilidad.
    """
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
    """
    Evalúa un SwapRequest usando una función de evaluación inyectada
    para evitar dependencia circular con simulator.py.
    """
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

    request.decision_sugerida = decision
    guardar_request(request)

    registrar_evento_swap_request(
        request,
        f"Request evaluado: clasificacion={clasificacion}, decision={decision}",
    )

    return {
        "request_id": request.id,
        "controlador_a": request.controlador_a,
        "controlador_b": request.controlador_b,
        "clasificacion": clasificacion,
        "decision": decision,
        "evaluacion": evaluacion,
    }


def resolver_swap_request(
    request: SwapRequest,
    accion: str,
) -> SwapRequest:
    """
    Cambia el estado del SwapRequest según la acción.
    """
    if request.estado != "PENDIENTE":
        raise ValueError("El request ya fue resuelto.")

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


def aplicar_swap_request(
    asignaciones: list,
    request: SwapRequest,
) -> list:
    """
    Aplica el swap al roster solamente si el request fue aceptado.
    Devuelve un nuevo roster con el intercambio realizado.
    """
    if request.estado != "ACEPTADO":
        raise ValueError("Solo se puede aplicar un SwapRequest con estado ACEPTADO.")

    if not (0 <= request.idx_a < len(asignaciones)) or not (0 <= request.idx_b < len(asignaciones)):
        raise IndexError("Los índices del SwapRequest están fuera de rango.")

    nuevo_roster = deepcopy(asignaciones)

    turno_a = nuevo_roster[request.idx_a].turno
    turno_b = nuevo_roster[request.idx_b].turno

    nuevo_roster[request.idx_a] = replace(nuevo_roster[request.idx_a], turno=turno_b)
    nuevo_roster[request.idx_b] = replace(nuevo_roster[request.idx_b], turno=turno_a)

    registrar_evento_swap_request(
        request,
        f"Swap aplicado al roster: idx_a={request.idx_a}, idx_b={request.idx_b}",
    )

    return nuevo_roster