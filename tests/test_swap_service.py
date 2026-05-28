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
    
def test_cancelar_requests_obsoletos_cancela_aprobados_obsoletos():
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

    from src.request_store import obtener_request

    recuperado = obtener_request(request.id)

    assert cancelados == 1
    assert recuperado is not None
    assert recuperado.estado == "CANCELADO"
    assert recuperado.motivo == "request obsoleto por nueva version de roster vigente"
    assert any(
        "REQUEST_CANCELADO_POR_OBSOLESCENCIA" in evento
        for evento in recuperado.history
    )
    
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

def _crear_request_aprobado_para_aplicacion(
    *,
    request_id: str = "req-aplicacion-v77",
    roster_version_id: str | None = None,
    controlador_a: str = "ATC_001",
    controlador_b: str = "ATC_002",
):
    from datetime import datetime

    from src.models import SwapRequest

    return SwapRequest(
        id=request_id,
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=0,
        idx_b=1,
        estado="APROBADO",
        fecha_creacion=datetime.now(),
        fecha_resolucion=datetime.now(),
        decision_sugerida="VIABLE",
        motivo="CREADO_DESDE_OFERTA",
        roster_version_id=roster_version_id,
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "clasificacion_observada": "BENEFICIOSO",
            "delta_score_observado": 10,
        },
    )

def _crear_request_aprobado_desde_asignaciones(
    *,
    asignaciones,
    roster_version_id: str,
):
    return _crear_request_aprobado_para_aplicacion(
        roster_version_id=roster_version_id,
        controlador_a=asignaciones[0].controlador.nombre,
        controlador_b=asignaciones[1].controlador.nombre,
    )


def test_aplicar_swap_request_aprobado_pasa_a_aplicado_y_crea_nueva_version() -> None:
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters, obtener_roster
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_aprobado_desde_asignaciones(
    asignaciones=asignaciones,
    roster_version_id=roster.id,
)

    nueva_version = aplicar_swap_request(asignaciones, request)

    roster_anterior = obtener_roster(roster.id)

    assert request.estado == "APLICADO"
    assert request.decision_sugerida == "VIABLE"
    assert nueva_version.version_number == roster.version_number + 1
    assert nueva_version.base_version_id == roster.id
    assert nueva_version.vigente is True
    assert roster_anterior is not None
    assert roster_anterior.vigente is False

    assert nueva_version.asignaciones[0].turno == asignaciones[1].turno
    assert nueva_version.asignaciones[1].turno == asignaciones[0].turno
    assert any("SWAP_APLICADO" in evento for evento in request.history)


def test_aplicar_swap_request_persiste_estado_aplicado() -> None:
    from src.engine import crear_roster_version_inicial
    from src.request_store import guardar_request, limpiar_requests, obtener_request
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import aplicar_swap_request

    limpiar_requests()
    limpiar_rosters()

    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_aprobado_desde_asignaciones(
    asignaciones=asignaciones,
    roster_version_id=roster.id,
)
    guardar_request(request)

    aplicar_swap_request(asignaciones, request)

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.estado == "APLICADO"
    assert recuperado.decision_sugerida == "VIABLE"
    assert any("SWAP_APLICADO" in evento for evento in recuperado.history)


def test_aplicar_swap_request_no_modifica_offer_origin() -> None:
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_aprobado_desde_asignaciones(
    asignaciones=asignaciones,
    roster_version_id=roster.id,
)
    offer_origin_original = dict(request.offer_origin or {})

    aplicar_swap_request(asignaciones, request)

    assert request.offer_origin == offer_origin_original
    assert request.offer_origin["clasificacion_observada"] == "BENEFICIOSO"


def test_aplicar_swap_request_no_modifica_decision_sugerida() -> None:
    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_aprobado_desde_asignaciones(
    asignaciones=asignaciones,
    roster_version_id=roster.id,
)

    aplicar_swap_request(asignaciones, request)

    assert request.decision_sugerida == "VIABLE"


def test_aplicar_swap_request_cancelado_no_puede_aplicar() -> None:
    import pytest

    from src.swap_service import aplicar_swap_request

    request = _crear_request_aprobado_para_aplicacion()
    request.estado = "CANCELADO"

    with pytest.raises(ValueError, match="estado APROBADO"):
        aplicar_swap_request([], request)


def test_aplicar_swap_request_aplicado_no_puede_aplicar_otra_vez() -> None:
    import pytest

    from src.swap_service import aplicar_swap_request

    request = _crear_request_aprobado_para_aplicacion()
    request.estado = "APLICADO"

    with pytest.raises(ValueError, match="ya fue aplicado"):
        aplicar_swap_request([], request)


def test_aplicar_swap_request_no_aplica_si_roster_version_no_es_vigente() -> None:
    import pytest

    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import aplicar_swap_request

    limpiar_rosters()
    asignaciones = crear_escenario()
    crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_aprobado_para_aplicacion(
        roster_version_id="otra-version",
    )

    with pytest.raises(ValueError, match="versión vigente"):
        aplicar_swap_request(asignaciones, request)


def test_aplicar_swap_request_no_evalua_no_resuelve(monkeypatch) -> None:
    import src.swap_service as modulo

    from src.engine import crear_roster_version_inicial
    from src.roster_store import limpiar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario

    limpiar_rosters()
    asignaciones = crear_escenario()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")

    request = _crear_request_aprobado_desde_asignaciones(
    asignaciones=asignaciones,
    roster_version_id=roster.id,
)

    def prohibido(*args, **kwargs) -> None:
        raise AssertionError("Aplicar no debe evaluar ni resolver.")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)

    modulo.aplicar_swap_request(asignaciones, request)

    assert request.estado == "APLICADO"


def test_cancelar_requests_obsoletos_cancela_pendiente_evaluado_y_aprobado() -> None:
    from datetime import datetime

    from src.models import SwapRequest
    from src.request_store import guardar_request, limpiar_requests, obtener_request
    from src.swap_service import cancelar_requests_obsoletos

    limpiar_requests()

    version = "rv-obsoleta"

    req_pendiente = SwapRequest(
        id="req-pendiente",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        roster_version_id=version,
    )
    req_evaluado = SwapRequest(
        id="req-evaluado",
        controlador_a="ATC_003",
        controlador_b="ATC_004",
        idx_a=2,
        idx_b=3,
        estado="EVALUADO",
        fecha_creacion=datetime.now(),
        decision_sugerida="OBSERVAR",
        roster_version_id=version,
    )
    req_aprobado = SwapRequest(
        id="req-aprobado",
        controlador_a="ATC_005",
        controlador_b="ATC_006",
        idx_a=4,
        idx_b=5,
        estado="APROBADO",
        fecha_creacion=datetime.now(),
        decision_sugerida="VIABLE",
        fecha_resolucion=datetime.now(),
        roster_version_id=version,
    )

    guardar_request(req_pendiente)
    guardar_request(req_evaluado)
    guardar_request(req_aprobado)

    cancelados = cancelar_requests_obsoletos(version)

    assert cancelados == 3

    for request_id in ("req-pendiente", "req-evaluado", "req-aprobado"):
        recuperado = obtener_request(request_id)
        assert recuperado is not None
        assert recuperado.estado == "CANCELADO"
        assert recuperado.motivo == "request obsoleto por nueva version de roster vigente"
        assert any(
            "REQUEST_CANCELADO_POR_OBSOLESCENCIA" in evento
            for evento in recuperado.history
        )


def test_cancelar_requests_obsoletos_no_toca_rechazado_cancelado_aplicado() -> None:
    from datetime import datetime

    from src.models import SwapRequest
    from src.request_store import guardar_request, limpiar_requests, obtener_request
    from src.swap_service import cancelar_requests_obsoletos

    limpiar_requests()

    version = "rv-obsoleta"

    req_rechazado = SwapRequest(
        id="req-rechazado",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado="RECHAZADO",
        fecha_creacion=datetime.now(),
        decision_sugerida="RECHAZAR",
        fecha_resolucion=datetime.now(),
        motivo="rechazado operativo",
        roster_version_id=version,
    )
    req_cancelado = SwapRequest(
        id="req-cancelado",
        controlador_a="ATC_003",
        controlador_b="ATC_004",
        idx_a=2,
        idx_b=3,
        estado="CANCELADO",
        fecha_creacion=datetime.now(),
        decision_sugerida="OBSERVAR",
        fecha_resolucion=datetime.now(),
        motivo="cancelado operativo",
        roster_version_id=version,
    )
    req_aplicado = SwapRequest(
        id="req-aplicado",
        controlador_a="ATC_005",
        controlador_b="ATC_006",
        idx_a=4,
        idx_b=5,
        estado="APLICADO",
        fecha_creacion=datetime.now(),
        decision_sugerida="VIABLE",
        fecha_resolucion=datetime.now(),
        motivo="CREADO_DESDE_OFERTA",
        roster_version_id=version,
    )

    guardar_request(req_rechazado)
    guardar_request(req_cancelado)
    guardar_request(req_aplicado)

    cancelados = cancelar_requests_obsoletos(version)

    assert cancelados == 0

    assert obtener_request("req-rechazado").estado == "RECHAZADO"
    assert obtener_request("req-rechazado").motivo == "rechazado operativo"

    assert obtener_request("req-cancelado").estado == "CANCELADO"
    assert obtener_request("req-cancelado").motivo == "cancelado operativo"

    assert obtener_request("req-aplicado").estado == "APLICADO"
    assert obtener_request("req-aplicado").motivo == "CREADO_DESDE_OFERTA"    