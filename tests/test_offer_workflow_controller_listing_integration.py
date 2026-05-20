from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import listar_requests_creados_desde_oferta_por_controlador
from src.request_store import guardar_request, limpiar_requests


def _crear_request(
    *,
    request_id: str,
    controlador_a: str,
    controlador_b: str,
    created_from_offer: bool = True,
    source_type: str = "OFERTA_EVALUADA",
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        offer_origin={
            "created_from_offer": created_from_offer,
            "source_type": source_type,
        },
    )


def setup_function() -> None:
    limpiar_requests()


def test_listar_requests_creados_desde_oferta_por_controlador_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-como-a",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-como-b",
            controlador_a="ATC_003",
            controlador_b="ATC_001",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-no-participa",
            controlador_a="ATC_004",
            controlador_b="ATC_005",
        )
    )

    resultado = listar_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
    )

    assert [request.id for request in resultado] == [
        "req-como-a",
        "req-como-b",
    ]


def test_listar_requests_creados_desde_oferta_por_controlador_excluye_no_oferta_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-desde-oferta",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-otro-origen",
            controlador_a="ATC_001",
            controlador_b="ATC_003",
            source_type="OTRO_ORIGEN",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-no-created-from-offer",
            controlador_a="ATC_004",
            controlador_b="ATC_001",
            created_from_offer=False,
        )
    )

    resultado = listar_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
    )

    assert [request.id for request in resultado] == [
        "req-desde-oferta",
    ]


def test_listar_requests_creados_desde_oferta_por_controlador_devuelve_vacio_si_no_hay_match() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
        )
    )

    resultado = listar_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_999",
    )

    assert resultado == []