from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import listar_requests_creados_desde_oferta_filtrados
from src.request_store import guardar_request, limpiar_requests


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


def setup_function() -> None:
    limpiar_requests()


def test_filtra_requests_creados_desde_oferta_desde_store_por_estado() -> None:
    guardar_request(
        _crear_request(
            request_id="req-pendiente",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-evaluado",
            estado="EVALUADO",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
        )
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        estado="PENDIENTE",
    )

    assert [request.id for request in resultado] == ["req-pendiente"]


def test_filtra_requests_creados_desde_oferta_desde_store_por_selected_by() -> None:
    guardar_request(
        _crear_request(
            request_id="req-supervisor-acc",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-supervisor-tma",
            estado="PENDIENTE",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
        )
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        selected_by="SUP_TMA",
    )

    assert [request.id for request in resultado] == ["req-supervisor-tma"]


def test_filtra_requests_creados_desde_oferta_desde_store_por_multiples_criterios() -> None:
    guardar_request(
        _crear_request(
            request_id="req-match",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-no-match",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="DIAGNOSTICO_COMPLETO",
            clasificacion_observada="ACEPTABLE",
        )
    )

    resultado = listar_requests_creados_desde_oferta_filtrados(
        estado="PENDIENTE",
        selected_by="SUP_ACC_CBA",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
    )

    assert [request.id for request in resultado] == ["req-match"]