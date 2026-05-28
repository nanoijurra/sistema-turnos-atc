from src.simulator import evaluar_swap
from src.swap_service import crear_swap_request, resolver_swap_request


def _crear_request_desde_asignaciones(
    asignaciones: list,
    idx_a: int,
    idx_b: int,
    motivo: str | None = None,
):
    return crear_swap_request(
        controlador_a=asignaciones[idx_a].controlador.nombre,
        controlador_b=asignaciones[idx_b].controlador.nombre,
        idx_a=idx_a,
        idx_b=idx_b,
        motivo=motivo,
    )
    
def test_evaluar_swap_request_setea_estado_y_decision():
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import evaluar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    evaluar_swap_request(
        asignaciones,
        request,
        evaluar_swap_fn=evaluar_swap,
    )

    assert request.estado == "EVALUADO"
    assert request.decision_sugerida is not None
    assert request.roster_hash is not None
    
def test_resolver_swap_request_aprobar_setea_estado_aprobado():
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import evaluar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    evaluar_swap_request(
        asignaciones,
        request,
        evaluar_swap_fn=evaluar_swap,
    )

    resolver_swap_request(request, "APROBAR")

    assert request.estado == "APROBADO"
    assert request.fecha_resolucion is not None
    
def test_cancelar_requests_obsoletos_no_afecta_resueltos():
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import evaluar_swap_request, cancelar_requests_obsoletos

    limpiar_rosters()
    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    evaluar_swap_request(
        asignaciones,
        request,
        evaluar_swap_fn=evaluar_swap,
    )

    resolver_swap_request(request, "APROBAR")

    cancelados = cancelar_requests_obsoletos(roster.id)

    assert cancelados == 0
    assert request.estado == "APROBADO"
    
def test_evaluar_swap_request_falla_si_no_hay_funcion_tecnica():
    import pytest
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.swap_service import evaluar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    with pytest.raises(ValueError, match="funcion de evaluacion tecnica"):
        evaluar_swap_request(asignaciones, request, evaluar_swap_fn=None)
        
def test_resolver_swap_request_falla_si_accion_invalida():
    import pytest
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.swap_service import evaluar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    evaluar_swap_request(
        asignaciones,
        request,
        evaluar_swap_fn=evaluar_swap,
    )

    with pytest.raises(ValueError, match="Acción inválida"):
        resolver_swap_request(request, "INVALIDA")
    
def test_aplicar_swap_request_falla_si_no_fue_evaluado():
    import pytest
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.swap_service import aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    with pytest.raises(ValueError, match="no fue evaluado"):
        aplicar_swap_request(asignaciones, request)  
        
def test_aplicar_swap_request_falla_si_no_esta_aprobado():
    import pytest
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v4_controladores_beneficioso import crear_escenario
    from src.swap_service import evaluar_swap_request, aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    evaluar_swap_request(
        asignaciones,
        request,
        evaluar_swap_fn=evaluar_swap,
    )

    # no aprobamos → queda en EVALUADO

    with pytest.raises(ValueError, match="estado APROBADO"):
        aplicar_swap_request(asignaciones, request)   
        
def test_aplicar_swap_request_falla_si_esta_rechazado() -> None:
    import pytest
    from datetime import datetime

    from src.swap_service import aplicar_swap_request, crear_swap_request
    from src.roster_store import obtener_roster_vigente

    roster = obtener_roster_vigente()
    assert roster is not None

    asignacion_a = roster.asignaciones[0]
    asignacion_b = roster.asignaciones[1]

    request = crear_swap_request(
        asignacion_a.controlador.nombre,
        asignacion_b.controlador.nombre,
        0,
        1,
    )

    request.decision_sugerida = "RECHAZAR"
    request.estado = "RECHAZADO"
    request.fecha_resolucion = datetime.now()

    with pytest.raises(ValueError):
        aplicar_swap_request(roster, request)
        
        
        

    
def test_aplicar_swap_request_no_requiere_evaluacion_tecnica(monkeypatch):
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import evaluar_swap_request, aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

    evaluar_swap_request(
        asignaciones,
        request,
        evaluar_swap_fn=evaluar_swap,
    )

    resolver_swap_request(request, "APROBAR")

    def fake_evaluar_swap_request_que_falla(*args, **kwargs):
        raise RuntimeError("NO DEBERIA LLAMARSE EN APLICAR")

    monkeypatch.setattr(
        "src.swap_service.evaluar_swap_request",
        fake_evaluar_swap_request_que_falla,
    )

    aplicar_swap_request(asignaciones, request)

    assert request.estado == "APLICADO"

def _crear_request_evaluado_para_resolucion(
    *,
    estado: str = "EVALUADO",
    decision_sugerida: str | None = "OBSERVAR",
):
    from datetime import datetime

    from src.models import SwapRequest

    return SwapRequest(
        id="req-resolucion-v75",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado=estado,
        fecha_creacion=datetime.now(),
        decision_sugerida=decision_sugerida,
        motivo="CREADO_DESDE_OFERTA",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "clasificacion_observada": "ACEPTABLE",
            "delta_score_observado": 0,
        },
    )


def test_resolver_swap_request_rechazar_setea_estado_rechazado() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion()

    resolver_swap_request(request, "RECHAZAR")

    assert request.estado == "RECHAZADO"
    assert request.fecha_resolucion is not None
    assert request.decision_sugerida == "OBSERVAR"


def test_resolver_swap_request_cancelar_setea_estado_cancelado() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion()

    resolver_swap_request(request, "CANCELAR")

    assert request.estado == "CANCELADO"
    assert request.fecha_resolucion is not None
    assert request.decision_sugerida == "OBSERVAR"


def test_resolver_swap_request_no_resuelve_desde_pendiente() -> None:
    import pytest

    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion(
        estado="PENDIENTE",
        decision_sugerida=None,
    )

    with pytest.raises(ValueError, match="sin evaluarlo primero"):
        resolver_swap_request(request, "APROBAR")


def test_resolver_swap_request_no_resuelve_desde_terminales() -> None:
    import pytest

    from src.swap_service import resolver_swap_request

    for estado in ("APROBADO", "RECHAZADO", "CANCELADO", "APLICADO"):
        request = _crear_request_evaluado_para_resolucion(
            estado=estado,
            decision_sugerida="OBSERVAR",
        )

        with pytest.raises(ValueError, match="ya fue resuelto"):
            resolver_swap_request(request, "APROBAR")


def test_resolver_swap_request_registra_history_con_actor_y_motivo_resolucion() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion()

    resolver_swap_request(
        request,
        "APROBAR",
        actor="SUP_ACC_CBA",
        motivo_resolucion="Autorizado por supervisor operativo.",
    )

    assert request.estado == "APROBADO"
    assert any(
        "REQUEST_RESUELTO: accion=APROBAR, estado=APROBADO" in evento
        and "actor=SUP_ACC_CBA" in evento
        and "motivo_resolucion=Autorizado por supervisor operativo." in evento
        for evento in request.history
    )


def test_resolver_swap_request_no_pisa_motivo_de_creacion() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion()
    motivo_original = request.motivo

    resolver_swap_request(
        request,
        "APROBAR",
        actor="SUP_ACC_CBA",
        motivo_resolucion="Motivo operativo de resolucion.",
    )

    assert request.motivo == motivo_original
    assert request.motivo == "CREADO_DESDE_OFERTA"


def test_resolver_swap_request_no_modifica_offer_origin() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion()
    offer_origin_original = dict(request.offer_origin or {})

    resolver_swap_request(
        request,
        "APROBAR",
        actor="SUP_ACC_CBA",
        motivo_resolucion="Motivo operativo.",
    )

    assert request.offer_origin == offer_origin_original
    assert request.offer_origin["clasificacion_observada"] == "ACEPTABLE"


def test_resolver_swap_request_conserva_decision_sugerida() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion(
        decision_sugerida="RECHAZAR",
    )

    resolver_swap_request(
        request,
        "APROBAR",
        actor="SUP_ACC_CBA",
        motivo_resolucion="Se aprueba explicitamente pese a decision sugerida.",
    )

    assert request.estado == "APROBADO"
    assert request.decision_sugerida == "RECHAZAR"


def test_resolver_swap_request_viable_no_autoaprueba() -> None:
    from src.swap_service import resolver_swap_request

    request = _crear_request_evaluado_para_resolucion(
        estado="EVALUADO",
        decision_sugerida="VIABLE",
    )

    assert request.estado == "EVALUADO"

    resolver_swap_request(request, "CANCELAR")

    assert request.estado == "CANCELADO"
    assert request.decision_sugerida == "VIABLE"


def test_resolver_swap_request_no_evalua_no_aplica(monkeypatch) -> None:
    import src.swap_service as modulo

    request = _crear_request_evaluado_para_resolucion()

    def prohibido(*args, **kwargs) -> None:
        raise AssertionError("No debe evaluar ni aplicar durante la resolucion.")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resolver = modulo.resolver_swap_request

    resolver(
        request,
        "APROBAR",
        actor="SUP_ACC_CBA",
        motivo_resolucion="Resolucion explicita.",
    )

    assert request.estado == "APROBADO"    