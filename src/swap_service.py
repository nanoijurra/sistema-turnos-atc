from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from src.models import SwapRequest, RosterVersion
from src.request_store import guardar_request, listar_requests
from src.roster_store import obtener_roster_vigente
from src.engine import (
    calcular_roster_hash,
    cargar_config,
    _validar_ventana_operativa,
    registrar_evento_swap_request,
    crear_nueva_version_desde_roster_vigente,
)


def _validar_indices_request_en_roster(asignaciones: list, request: SwapRequest) -> None:
    if not (0 <= request.idx_a < len(asignaciones)) or not (0 <= request.idx_b < len(asignaciones)):
        raise IndexError("Los índices del SwapRequest no son válidos para el roster actual.")


def _validar_controladores_request_vs_roster(asignaciones: list, request: SwapRequest, contexto: str = "") -> None:
    asignacion_a = asignaciones[request.idx_a]
    asignacion_b = asignaciones[request.idx_b]

    if asignacion_a.controlador is None or asignacion_b.controlador is None:
        raise ValueError("Las asignaciones no tienen controlador asociado.")

    sufijo = f" {contexto}" if contexto else ""

    if asignacion_a.controlador.nombre != request.controlador_a:
        raise ValueError(
            f"Inconsistencia en controlador A{sufijo}: request={request.controlador_a}, roster={asignacion_a.controlador.nombre}"
        )

    if asignacion_b.controlador.nombre != request.controlador_b:
        raise ValueError(
            f"Inconsistencia en controlador B{sufijo}: request={request.controlador_b}, roster={asignacion_b.controlador.nombre}"
        )


def _obtener_y_validar_roster_vigente_para_request(
    request: SwapRequest,
    accion: str,
) -> RosterVersion:
    roster_vigente = obtener_roster_vigente()
    if roster_vigente is None:
        raise ValueError(f"No existe un roster vigente para {accion} el request.")

    if request.roster_version_id != roster_vigente.id:
        raise ValueError("El request no corresponde a la versión vigente del roster.")

    return roster_vigente


def crear_swap_request(
    controlador_a: str,
    controlador_b: str,
    idx_a: int,
    idx_b: int,
    motivo: str | None = None,
) -> SwapRequest:
    roster_vigente = obtener_roster_vigente()
    if roster_vigente is None:
        raise ValueError("No existe un roster vigente para crear el request.")

    request = SwapRequest(
        id=str(uuid4()),
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=idx_a,
        idx_b=idx_b,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo=motivo,
        roster_version_id=roster_vigente.id,
    )

    registrar_evento_swap_request(
        request,
        f"Request creado: {controlador_a}[{idx_a}] <-> {controlador_b}[{idx_b}] | roster_version_id={roster_vigente.id}",
    )

    return request


def evaluar_swap_request(
    asignaciones: list,
    request: SwapRequest,
    evaluar_swap_fn,
    config_file: str = "config_equilibrado.json",
) -> dict:
    if evaluar_swap_fn is None:
        raise ValueError("Se requiere una funcion de evaluacion tecnica para evaluar el request.")

    if request.decision_sugerida is not None:
        raise ValueError("El request ya fue evaluado.")

    if request.estado != "PENDIENTE":
        raise ValueError(
            f"Estado invalido para evaluar request: {request.estado}. Se esperaba PENDIENTE."
        )

    _validar_indices_request_en_roster(asignaciones, request)
    _validar_controladores_request_vs_roster(asignaciones, request)

    roster_vigente = _obtener_y_validar_roster_vigente_para_request(
        request,
        accion="evaluar",
    )

    roster_vigente = obtener_roster_vigente()
    if roster_vigente is None:
        raise ValueError("No existe un roster vigente para evaluar el request.")

    if request.roster_version_id != roster_vigente.id:
        raise ValueError("El request no corresponde a la versión vigente del roster.")

    config = cargar_config(config_file)

    if not _validar_ventana_operativa(asignaciones, request.idx_a, request.idx_b, config):
        request.estado = "EVALUADO"
        request.decision_sugerida = "RECHAZAR"
        request.roster_hash = calcular_roster_hash(asignaciones)
        guardar_request(request)

        registrar_evento_swap_request(
            request,
            (
                "REQUEST_EVALUADO_SIN_TECNICA: decision=RECHAZAR, "
                "motivo=SWAP_FUERA_DE_VENTANA_OPERATIVA, "
                f"roster_version_id={roster_vigente.id}, version_number={roster_vigente.version_number}"
            ),
        )

        return {
            "request_id": request.id,
            "controlador_a": request.controlador_a,
            "controlador_b": request.controlador_b,
            "clasificacion": None,
            "decision": "RECHAZAR",
            "evaluacion": None,
            "motivo": "SWAP_FUERA_DE_VENTANA_OPERATIVA",
            "roster_version_id": roster_vigente.id,
            "roster_version_number": roster_vigente.version_number,
        }

    evaluacion = evaluar_swap_fn(
        asignaciones=asignaciones,
        idx_a=request.idx_a,
        idx_b=request.idx_b,
        config_file=config_file,
    )

    clasificacion = evaluacion["clasificacion"]

    if clasificacion == "BENEFICIOSO":
        decision = "VIABLE"
    elif clasificacion == "ACEPTABLE":
        decision = "OBSERVAR"
    else:
        decision = "RECHAZAR"

    request.estado = "EVALUADO"
    request.decision_sugerida = decision
    request.roster_hash = calcular_roster_hash(asignaciones)
    guardar_request(request)

    registrar_evento_swap_request(
        request,
        (
            f"REQUEST_EVALUADO: clasificacion={clasificacion}, decision={decision}, "
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


def resolver_swap_request(request: SwapRequest, accion: str) -> SwapRequest:
    if accion not in ("APROBAR", "RECHAZAR", "CANCELAR"):
        raise ValueError(f"Acción inválida: {accion}")

    if request.decision_sugerida is None:
        raise ValueError("No se puede resolver un request sin evaluarlo primero.")

    if request.estado in ("APROBADO", "RECHAZADO", "CANCELADO", "APLICADO"):
        raise ValueError("El request ya fue resuelto.")

    if request.estado != "EVALUADO":
        raise ValueError(
            f"Estado inválido para resolver request: {request.estado}. Se esperaba EVALUADO."
        )

    if accion == "APROBAR":
        request.estado = "APROBADO"
    elif accion == "RECHAZAR":
        request.estado = "RECHAZADO"
    else:
        request.estado = "CANCELADO"

    request.fecha_resolucion = datetime.now()
    guardar_request(request)

    registrar_evento_swap_request(
        request,
        f"REQUEST_RESUELTO: accion={accion}, estado={request.estado}",
    )

    return request


def cancelar_requests_obsoletos(roster_version_id_viejo: str) -> int:
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


def aplicar_swap_request(asignaciones: list, request: SwapRequest) -> RosterVersion:
    if request.decision_sugerida is None:
        raise ValueError("No se puede aplicar un request que no fue evaluado.")

    if request.estado == "APLICADO":
        raise ValueError("No se puede aplicar un request que ya fue aplicado.")

    if request.estado != "APROBADO":
        raise ValueError("Solo se puede aplicar un SwapRequest con estado APROBADO.")

    roster_vigente = obtener_roster_vigente()
    if roster_vigente is None:
        raise ValueError("No existe un roster vigente para aplicar el request.")

    if request.roster_version_id != roster_vigente.id:
        raise ValueError("El request ya no apunta a la versión vigente del roster.")

    _validar_indices_request_en_roster(asignaciones, request)
    _validar_controladores_request_vs_roster(asignaciones, request, contexto="al aplicar")

    roster_version_id_viejo = roster_vigente.id

    nuevo = deepcopy(asignaciones)

    turno_a = nuevo[request.idx_a].turno
    turno_b = nuevo[request.idx_b].turno

    nuevo[request.idx_a] = replace(nuevo[request.idx_a], turno=turno_b)
    nuevo[request.idx_b] = replace(nuevo[request.idx_b], turno=turno_a)

    nueva_version = crear_nueva_version_desde_roster_vigente(
        nuevo,
        regimen_horario=roster_vigente.regimen_horario,
    )

    cancelar_requests_obsoletos(roster_version_id_viejo)

    request.estado = "APLICADO"
    request.fecha_resolucion = request.fecha_resolucion or datetime.now()
    guardar_request(request)

    registrar_evento_swap_request(
        request,
        f"SWAP_APLICADO: nueva_version={nueva_version.version_number}",
    )

    return nueva_version