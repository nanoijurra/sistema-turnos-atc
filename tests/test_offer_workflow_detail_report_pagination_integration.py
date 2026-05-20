from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import generar_reporte_detalle_requests_creados_desde_oferta
from src.request_store import guardar_request, limpiar_requests


def _crear_request(
    *,
    request_id: str,
    fecha_creacion: datetime,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=fecha_creacion,
        roster_version_id="rv-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "selected_by": "SUP_ACC_CBA",
            "selection_reason": "Motivo",
            "selection_note": "Nota",
            "modo_exploracion": "OFERTA_RAPIDA",
            "clasificacion_observada": "ACEPTABLE",
            "offer_rank_observado": 1,
        },
    )


def setup_function() -> None:
    limpiar_requests()


def test_reporte_detalle_pagina_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-2",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-3",
            fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        ordenar_por="request_id",
        direccion="asc",
        limit=1,
        offset=1,
    )

    assert reporte.total == 3
    assert [detalle.request_id for detalle in reporte.detalles] == ["req-2"]
    assert reporte.paginacion.limit == 1
    assert reporte.paginacion.offset == 1
    assert reporte.paginacion.total == 3
    assert reporte.paginacion.returned == 1
    assert reporte.paginacion.has_more is True
    assert reporte.filtros["ordenar_por"] == "request_id"
    assert reporte.filtros["direccion"] == "asc"
    assert reporte.filtros["limit"] == 1
    assert reporte.filtros["offset"] == 1


def test_reporte_detalle_pagina_final_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-2",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        ordenar_por="request_id",
        direccion="asc",
        limit=1,
        offset=1,
    )

    assert reporte.total == 2
    assert [detalle.request_id for detalle in reporte.detalles] == ["req-2"]
    assert reporte.paginacion.has_more is False


def test_reporte_detalle_paginacion_to_dict_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        limit=1,
        offset=0,
    )
    datos = reporte.to_dict()

    assert datos["total"] == 1
    assert datos["paginacion"] == {
        "limit": 1,
        "offset": 0,
        "total": 1,
        "returned": 1,
        "has_more": False,
    }
    assert datos["filtros"]["limit"] == 1
    assert datos["filtros"]["offset"] == 0