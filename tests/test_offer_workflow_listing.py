from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models import SwapRequest
from src.offer_workflow_service import (
    es_request_creado_desde_oferta,
    listar_requests_creados_desde_oferta,
)


def _crear_request(
    *,
    request_id: str,
    offer_origin: dict | None,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        offer_origin=offer_origin,
    )


def test_es_request_creado_desde_oferta_devuelve_true_con_offer_origin_valido() -> None:
    request = _crear_request(
        request_id="req-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
        },
    )

    assert es_request_creado_desde_oferta(request=request) is True


def test_es_request_creado_desde_oferta_devuelve_false_sin_offer_origin() -> None:
    request = _crear_request(
        request_id="req-1",
        offer_origin=None,
    )

    assert es_request_creado_desde_oferta(request=request) is False


def test_es_request_creado_desde_oferta_devuelve_false_si_created_from_offer_no_es_true() -> None:
    request = _crear_request(
        request_id="req-1",
        offer_origin={
            "created_from_offer": False,
            "source_type": "OFERTA_EVALUADA",
        },
    )

    assert es_request_creado_desde_oferta(request=request) is False


def test_es_request_creado_desde_oferta_devuelve_false_si_source_type_no_corresponde() -> None:
    request = _crear_request(
        request_id="req-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OTRO_ORIGEN",
        },
    )

    assert es_request_creado_desde_oferta(request=request) is False


def test_listar_requests_creados_desde_oferta_filtra_correctamente(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    request_desde_oferta = _crear_request(
        request_id="req-desde-oferta",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
        },
    )
    request_manual = _crear_request(
        request_id="req-manual",
        offer_origin=None,
    )
    request_otro_origen = _crear_request(
        request_id="req-otro-origen",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OTRO_ORIGEN",
        },
    )

    monkeypatch.setattr(
        modulo,
        "listar_requests",
        lambda: [
            request_desde_oferta,
            request_manual,
            request_otro_origen,
        ],
    )

    resultado = listar_requests_creados_desde_oferta()

    assert resultado == [request_desde_oferta]


def test_listar_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    request_desde_oferta = _crear_request(
        request_id="req-desde-oferta",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
        },
    )

    monkeypatch.setattr(
        modulo,
        "listar_requests",
        lambda: [request_desde_oferta],
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resultado = listar_requests_creados_desde_oferta()

    assert resultado == [request_desde_oferta]