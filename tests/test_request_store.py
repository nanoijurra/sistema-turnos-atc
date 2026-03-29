from src.request_store import (
    guardar_request,
    obtener_request,
    listar_requests,
    limpiar_requests,
)
from src.simulator import (
    crear_swap_request,
    evaluar_swap_request,
    resolver_swap_request,
)
from src.scenarios.v5_controladores_beneficioso_mutuo import (
    crear_escenario as escenario_beneficioso_mutuo,
)


def setup_function():
    limpiar_requests()


def test_guardar_y_obtener_request():
    asignaciones = escenario_beneficioso_mutuo()

    request = crear_swap_request(
        asignaciones=asignaciones,
        idx_a=0,
        idx_b=3,
        motivo="Intercambio personal",
    )

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.id == request.id
    assert recuperado.controlador_a == "ATC_A"
    assert recuperado.controlador_b == "ATC_B"


def test_listar_requests_devuelve_requests_guardados():
    asignaciones = escenario_beneficioso_mutuo()

    request_1 = crear_swap_request(
        asignaciones=asignaciones,
        idx_a=0,
        idx_b=3,
        motivo="Motivo 1",
    )

    request_2 = crear_swap_request(
        asignaciones=asignaciones,
        idx_a=1,
        idx_b=2,
        motivo="Motivo 2",
    )

    requests = listar_requests()
    ids = {r.id for r in requests}

    assert len(requests) == 2
    assert request_1.id in ids
    assert request_2.id in ids


def test_request_actualizado_permanece_recuperable_desde_store():
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters

    limpiar_rosters()
    asignaciones = escenario_beneficioso_mutuo()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = crear_swap_request(
        asignaciones=asignaciones,
        idx_a=0,
        idx_b=3,
        motivo="Intercambio personal",
    )

    evaluar_swap_request(asignaciones, request)
    resolver_swap_request(request, "ACEPTAR")

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.decision_sugerida == "APROBABLE"
    assert recuperado.estado == "ACEPTADO"
    assert recuperado.fecha_resolucion is not None
    assert recuperado.roster_version_id is not None
    assert len(recuperado.history) == 3


def test_limpiar_requests_vacia_el_store():
    asignaciones = escenario_beneficioso_mutuo()

    request = crear_swap_request(
        asignaciones=asignaciones,
        idx_a=0,
        idx_b=3,
        motivo="Intercambio personal",
    )

    guardar_request(request)
    assert len(listar_requests()) == 1

    limpiar_requests()

    assert listar_requests() == []
    assert obtener_request(request.id) is None

def test_listar_requests_por_estado_filtra_correctamente():
    from src.request_store import (
        guardar_request,
        listar_requests_por_estado,
        limpiar_requests,
    )
    from src.models import SwapRequest
    from datetime import datetime

    limpiar_requests()

    r1 = SwapRequest(id="1", controlador_a="A", controlador_b="B", idx_a=0, idx_b=1,
                     estado="PENDIENTE", fecha_creacion=datetime.now())
    r2 = SwapRequest(id="2", controlador_a="A", controlador_b="B", idx_a=0, idx_b=1,
                     estado="ACEPTADO", fecha_creacion=datetime.now())

    guardar_request(r1)
    guardar_request(r2)

    pendientes = listar_requests_por_estado("PENDIENTE")

    assert len(pendientes) == 1
    assert pendientes[0].id == "1"

    
def test_listar_requests_por_roster_version_filtra_correctamente():
    from src.request_store import (
        guardar_request,
        listar_requests_por_roster_version,
        limpiar_requests,
    )
    from src.models import SwapRequest
    from datetime import datetime

    limpiar_requests()

    r1 = SwapRequest(id="1", controlador_a="A", controlador_b="B", idx_a=0, idx_b=1,
                     estado="PENDIENTE", fecha_creacion=datetime.now())
    r1.roster_version_id = "v1"

    r2 = SwapRequest(id="2", controlador_a="A", controlador_b="B", idx_a=0, idx_b=1,
                     estado="PENDIENTE", fecha_creacion=datetime.now())
    r2.roster_version_id = "v2"

    guardar_request(r1)
    guardar_request(r2)

    v1_requests = listar_requests_por_roster_version("v1")

    assert len(v1_requests) == 1
    assert v1_requests[0].id == "1"

