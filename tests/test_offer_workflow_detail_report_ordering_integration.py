from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import generar_reporte_detalle_requests_creados_desde_oferta
from src.request_store import guardar_request, limpiar_requests


def _crear_request(
    *,
    request_id: str,
    estado: str,
    fecha_creacion: datetime,
    selected_by: str,
    clasificacion_observada: str,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado=estado,
        fecha_creacion=fecha_creacion,
        roster_version_id="rv-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "selected_by": selected_by,
            "selection_reason": "Motivo",
            "selection_note": "Nota",
            "modo_exploracion": "OFERTA_RAPIDA",
            "clasificacion_observada": clasificacion_observada,
            "offer_rank_observado": 1,
        },
    )


def setup_function() -> None:
    limpiar_requests()


def test_reporte_detalle_ordena_por_fecha_creacion_desc_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-antiguo",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
            selected_by="SUP_ACC_CBA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-nuevo",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
            selected_by="SUP_ACC_CBA",
            clasificacion_observada="BENEFICIOSO",
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        ordenar_por="fecha_creacion",
        direccion="desc",
    )

    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-nuevo",
        "req-antiguo",
    ]
    assert reporte.filtros["ordenar_por"] == "fecha_creacion"
    assert reporte.filtros["direccion"] == "desc"


def test_reporte_detalle_ordena_por_clasificacion_observada_asc_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-beneficioso",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
            selected_by="SUP_ACC_CBA",
            clasificacion_observada="BENEFICIOSO",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-aceptable",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
            selected_by="SUP_TMA",
            clasificacion_observada="ACEPTABLE",
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        ordenar_por="clasificacion_observada",
        direccion="asc",
    )

    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-aceptable",
        "req-beneficioso",
    ]
    assert reporte.filtros["ordenar_por"] == "clasificacion_observada"
    assert reporte.filtros["direccion"] == "asc"


def test_reporte_detalle_filtra_y_ordena_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-2",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
            selected_by="SUP_ACC_CBA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-1",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
            selected_by="SUP_ACC_CBA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-otro-supervisor",
            estado="PENDIENTE",
            fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
            selected_by="SUP_TMA",
            clasificacion_observada="ACEPTABLE",
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        selected_by="SUP_ACC_CBA",
        ordenar_por="request_id",
        direccion="asc",
    )

    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-1",
        "req-2",
    ]
    assert reporte.filtros["selected_by"] == "SUP_ACC_CBA"
    assert reporte.filtros["ordenar_por"] == "request_id"
    assert reporte.filtros["direccion"] == "asc"