from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import listar_requests_creados_desde_oferta
from src.request_store import guardar_request, limpiar_requests


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


def setup_function() -> None:
    limpiar_requests()


def test_listar_requests_creados_desde_oferta_desde_store() -> None:
    request_desde_oferta = _crear_request(
        request_id="req-desde-oferta",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "selected_by": "SUP_ACC_CBA",
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

    guardar_request(request_desde_oferta)
    guardar_request(request_manual)
    guardar_request(request_otro_origen)

    resultado = listar_requests_creados_desde_oferta()

    assert len(resultado) == 1
    assert resultado[0].id == "req-desde-oferta"
    assert resultado[0].offer_origin is not None
    assert resultado[0].offer_origin["source_type"] == "OFERTA_EVALUADA"
    assert resultado[0].offer_origin["selected_by"] == "SUP_ACC_CBA"