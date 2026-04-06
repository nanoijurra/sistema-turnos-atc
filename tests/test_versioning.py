from datetime import datetime

from src.engine import (
    crear_roster_version_inicial,
    crear_nueva_version_desde_roster_vigente,
    cancelar_requests_obsoletos,
)
from src.request_store import (
    guardar_request,
    limpiar_requests,
    obtener_request,
)
from src.roster_store import (
    limpiar_rosters,
    obtener_roster_vigente,
    obtener_roster_por_version_number,
)
from src.models import SwapRequest
from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario


def setup_function():
    limpiar_requests()
    limpiar_rosters()


def test_crear_roster_version_inicial_deja_version_1_vigente():
    asignaciones = crear_escenario()

    roster = crear_roster_version_inicial(asignaciones)

    vigente = obtener_roster_vigente()

    assert roster.version_number == 1
    assert roster.vigente is True
    assert vigente is not None
    assert vigente.id == roster.id


def test_crear_nueva_version_desde_roster_vigente_desactiva_anterior():
    asignaciones = crear_escenario()

    roster_v1 = crear_roster_version_inicial(asignaciones)
    roster_v2 = crear_nueva_version_desde_roster_vigente(asignaciones)

    vigente = obtener_roster_vigente()
    roster_v1_actualizado = obtener_roster_por_version_number(1)

    assert roster_v1.id != roster_v2.id
    assert roster_v2.version_number == roster_v1.version_number + 1
    assert roster_v2.base_version_id == roster_v1.id
    assert roster_v1_actualizado is not None
    assert roster_v1_actualizado.vigente is False
    assert roster_v2.vigente is True
    assert vigente is not None
    assert vigente.id == roster_v2.id


def test_cancelar_requests_obsoletos_cancela_pendientes_y_evaluados_de_una_version():
    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones)

    req_pendiente = SwapRequest(
        id="req-pend",
        controlador_a="A",
        controlador_b="B",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        roster_version_id=roster.id,
    )

    req_evaluado = SwapRequest(
        id="req-eval",
        controlador_a="A",
        controlador_b="B",
        idx_a=0,
        idx_b=1,
        estado="EVALUADO",
        fecha_creacion=datetime.now(),
        roster_version_id=roster.id,
    )

    req_aceptado = SwapRequest(
        id="req-ok",
        controlador_a="A",
        controlador_b="B",
        idx_a=0,
        idx_b=1,
        estado="ACEPTADO",
        fecha_creacion=datetime.now(),
        roster_version_id=roster.id,
    )

    req_otra_version = SwapRequest(
        id="req-other",
        controlador_a="A",
        controlador_b="B",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        roster_version_id="otra-version",
    )

    guardar_request(req_pendiente)
    guardar_request(req_evaluado)
    guardar_request(req_aceptado)
    guardar_request(req_otra_version)

    cancelados = cancelar_requests_obsoletos(roster.id)

    req_pendiente_db = obtener_request("req-pend")
    req_evaluado_db = obtener_request("req-eval")
    req_aceptado_db = obtener_request("req-ok")
    req_otra_version_db = obtener_request("req-other")

    assert cancelados == 2
    assert req_pendiente_db is not None
    assert req_evaluado_db is not None
    assert req_aceptado_db is not None
    assert req_otra_version_db is not None

    assert req_pendiente_db.estado == "CANCELADO"
    assert req_evaluado_db.estado == "CANCELADO"
    assert req_aceptado_db.estado == "ACEPTADO"
    assert req_otra_version_db.estado == "PENDIENTE"