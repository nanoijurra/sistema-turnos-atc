from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models import SwapRequest
from src.offer_workflow_service import listar_requests_creados_desde_oferta_filtrados


def _crear_request(
    *,
    request_id: str,
    estado: str,
    selected_by: str | None,
    modo_exploracion: str,
    clasificacion_observada: str,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado=estado,
        fecha_creacion=datetime.now(),
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "selected_by": selected_by,
            "modo_exploracion": modo_exploracion,
            "clasificacion_observada": clasificacion_observada,
        },
    )


def _crear_requests_base() -> list[SwapRequest]:
    return [
        _crear_request(
            request_id="req-1",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        ),
        _crear_request(
            request_id="req-2",
            estado="EVALUADO",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
        ),
        _crear_request(
            request_id="req-3",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="DIAGNOSTICO_COMPLETO",
            clasificacion_observada="RECHAZABLE",
        ),
    ]


def test_filtra_requests_creados_desde_oferta_por_estado(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        _crear_requests_base,
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        estado="PENDIENTE",
    )

    assert [request.id for request in resultado] == ["req-1", "req-3"]


def test_filtra_requests_creados_desde_oferta_por_selected_by(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        _crear_requests_base,
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        selected_by="SUP_TMA",
    )

    assert [request.id for request in resultado] == ["req-2"]


def test_filtra_requests_creados_desde_oferta_por_modo_exploracion(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        _crear_requests_base,
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        modo_exploracion="DIAGNOSTICO_COMPLETO",
    )

    assert [request.id for request in resultado] == ["req-3"]


def test_filtra_requests_creados_desde_oferta_por_clasificacion_observada(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        _crear_requests_base,
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        clasificacion_observada="BENEFICIOSO",
    )

    assert [request.id for request in resultado] == ["req-2"]


def test_filtra_requests_creados_desde_oferta_por_multiples_criterios(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        _crear_requests_base,
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        estado="PENDIENTE",
        selected_by="SUP_ACC_CBA",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
    )

    assert [request.id for request in resultado] == ["req-1"]


def test_filtrar_sin_criterios_devuelve_todos_los_creados_desde_oferta(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    requests = _crear_requests_base()

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        lambda: requests,
    )

    resultado = listar_requests_creados_desde_oferta_filtrados()

    assert resultado == requests


def test_filtrar_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta",
        _crear_requests_base,
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resultado = listar_requests_creados_desde_oferta_filtrados(
        estado="PENDIENTE",
    )

    assert [request.id for request in resultado] == ["req-1", "req-3"]