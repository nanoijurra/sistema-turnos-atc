from __future__ import annotations

from src.simulator import evaluar_swap


def test_lifecycle_formal_completo_evaluar_resolver_aplicar() -> None:
    from src.engine import crear_roster_version_inicial
    from src.request_store import limpiar_requests, obtener_request
    from src.roster_store import limpiar_rosters, obtener_roster
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.swap_service import (
        aplicar_swap_request,
        crear_swap_request,
        evaluar_swap_request,
        resolver_swap_request,
    )

    limpiar_requests()
    limpiar_rosters()

    asignaciones = crear_escenario()
    roster_inicial = crear_roster_version_inicial(
        asignaciones,
        regimen_horario="8H",
    )

    request = crear_swap_request(
        controlador_a=asignaciones[0].controlador.nombre,
        controlador_b=asignaciones[3].controlador.nombre,
        idx_a=0,
        idx_b=3,
        motivo="TEST_LIFECYCLE_FORMAL",
    )

    assert request.estado == "PENDIENTE"
    assert request.decision_sugerida is None
    assert request.roster_version_id == roster_inicial.id

    evaluacion_formal = evaluar_swap_request(
        asignaciones=asignaciones,
        request=request,
        evaluar_swap_fn=evaluar_swap,
    )

    assert request.estado == "EVALUADO"
    assert request.decision_sugerida is not None
    assert evaluacion_formal["request_id"] == request.id
    assert evaluacion_formal["decision"] == request.decision_sugerida
    assert any(
    "REQUEST_EVALUADA" in evento
    and "event_type=REQUEST_EVALUADA" in evento
    and "estado_anterior=PENDIENTE" in evento
    and "estado_nuevo=EVALUADO" in evento
    for evento in request.history
)

    resolver_swap_request(
        request,
        "APROBAR",
        actor="SUP_ACC_CBA",
        motivo_resolucion="Aprobado para test de ciclo formal completo.",
    )

    assert request.estado == "APROBADO"
    assert request.decision_sugerida == evaluacion_formal["decision"]
    assert any(
        "REQUEST_RESUELTA" in evento
        and "event_type=REQUEST_RESUELTA" in evento
        and "accion=APROBAR" in evento
        and "resultado=APROBADO" in evento
        and "actor=SUP_ACC_CBA" in evento
        and "motivo_resolucion=Aprobado para test de ciclo formal completo." in evento
        for evento in request.history
    )

    nueva_version = aplicar_swap_request(
        asignaciones=asignaciones,
        request=request,
        evaluacion=evaluacion_formal,
    )

    roster_anterior = obtener_roster(roster_inicial.id)
    request_persistido = obtener_request(request.id)

    assert request.estado == "APLICADO"
    assert request.fecha_resolucion is not None
    assert request.decision_sugerida == evaluacion_formal["decision"]
    assert any("REQUEST_APLICADA" in evento for evento in request.history)

    assert nueva_version.version_number == roster_inicial.version_number + 1
    assert nueva_version.base_version_id == roster_inicial.id
    assert nueva_version.vigente is True

    assert roster_anterior is not None
    assert roster_anterior.vigente is False

    assert nueva_version.asignaciones[0].turno == asignaciones[3].turno
    assert nueva_version.asignaciones[3].turno == asignaciones[0].turno

    assert request_persistido is not None
    assert request_persistido.estado == "APLICADO"
    assert request_persistido.decision_sugerida == evaluacion_formal["decision"]
    assert request_persistido.roster_version_id == roster_inicial.id
    assert any(
    "REQUEST_EVALUADA" in evento
    and "event_type=REQUEST_EVALUADA" in evento
    and "estado_anterior=PENDIENTE" in evento
    and "estado_nuevo=EVALUADO" in evento
    for evento in request_persistido.history
    )
    assert any(
        "REQUEST_RESUELTA:" in evento
        and "event_type=REQUEST_RESUELTA" in evento
        and "accion=APROBAR" in evento
        and "resultado=APROBADO" in evento
        and "estado_anterior=EVALUADO" in evento
        and "estado_nuevo=APROBADO" in evento
        for evento in request_persistido.history
    )
    assert any(
        "REQUEST_APLICADA" in evento
        for evento in request_persistido.history
    )