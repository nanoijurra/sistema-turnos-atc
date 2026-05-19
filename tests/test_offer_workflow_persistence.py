from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from src.models import SwapRequest
from src.offer_workflow_service import persistir_request_creado_desde_oferta


def _crear_request_desde_oferta_fake() -> SwapRequest:
    return SwapRequest(
        id="req-desde-oferta",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo="CREADO_DESDE_OFERTA",
        roster_version_id="rv-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "modo_exploracion": "OFERTA_RAPIDA",
            "offer_rank_observado": 1,
            "clasificacion_observada": "ACEPTABLE",
        },
    )


def test_persistir_request_creado_desde_oferta_delega_en_request_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    request = _crear_request_desde_oferta_fake()
    llamadas = []

    def guardar_request_fake(request: SwapRequest) -> SwapRequest:
        llamadas.append(request)
        return request

    monkeypatch.setattr(modulo, "guardar_request", guardar_request_fake)

    resultado = persistir_request_creado_desde_oferta(request=request)

    assert resultado is request
    assert llamadas == [request]


def test_persistir_request_creado_desde_oferta_requiere_estado_pendiente() -> None:
    request = _crear_request_desde_oferta_fake()
    request.estado = "EVALUADO"

    with pytest.raises(ValueError, match="estado PENDIENTE"):
        persistir_request_creado_desde_oferta(request=request)


def test_persistir_request_creado_desde_oferta_rechaza_request_con_decision() -> None:
    request = _crear_request_desde_oferta_fake()
    request.decision_sugerida = "OBSERVAR"

    with pytest.raises(ValueError, match="decision_sugerida"):
        persistir_request_creado_desde_oferta(request=request)


def test_persistir_request_creado_desde_oferta_requiere_offer_origin() -> None:
    request = _crear_request_desde_oferta_fake()
    request.offer_origin = None

    with pytest.raises(ValueError, match="offer_origin"):
        persistir_request_creado_desde_oferta(request=request)


def test_persistir_request_creado_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    request = _crear_request_desde_oferta_fake()

    monkeypatch.setattr(
        modulo,
        "guardar_request",
        lambda request: request,
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resultado = persistir_request_creado_desde_oferta(request=request)

    assert resultado.estado == "PENDIENTE"
    assert resultado.decision_sugerida is None
    assert resultado.offer_origin is not None