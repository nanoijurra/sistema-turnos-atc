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
        

    
def test_aplicar_swap_request_actualiza_historial_si_se_provee(monkeypatch):
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

    historial = {"dummy": {"beneficios_recientes": 0}}
    evaluacion_tracking = {
        "resumen_por_controlador_original": {
            "CTRL_X": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 2},
            },
        },
        "resumen_por_controlador_nuevo": {
            "CTRL_X": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
        },
    }

    llamado = {}

    def fake_actualizar_historial_beneficios(historial_por_controlador, evaluacion):
        llamado["historial"] = historial_por_controlador
        llamado["evaluacion"] = evaluacion
        return historial_por_controlador

    monkeypatch.setattr(
        "src.swap_service.actualizar_historial_beneficios",
        fake_actualizar_historial_beneficios,
    )

    aplicar_swap_request(
        asignaciones,
        request,
        evaluacion=evaluacion_tracking,
        historial_por_controlador=historial,
    )

    assert llamado["historial"] is historial
    assert llamado["evaluacion"] is evaluacion_tracking