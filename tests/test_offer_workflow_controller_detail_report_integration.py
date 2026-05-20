from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import (
    MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA_POR_CONTROLADOR,
    generar_reporte_detalle_requests_creados_desde_oferta_por_controlador,
)
from src.request_store import guardar_request, limpiar_requests


def _crear_request(
    *,
    request_id: str,
    controlador_a: str,
    controlador_b: str,
    fecha_creacion: datetime,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a=controlador_a,
        controlador_b=controlador_b,
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


def test_reporte_detalle_por_controlador_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-como-a",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-como-b",
            controlador_a="ATC_003",
            controlador_b="ATC_001",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-no-participa",
            controlador_a="ATC_004",
            controlador_b="ATC_005",
            fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
        ordenar_por="request_id",
        direccion="asc",
    )

    assert reporte.mensaje == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA_POR_CONTROLADOR
    assert reporte.filtros == {
        "controlador": "ATC_001",
        "ordenar_por": "request_id",
        "direccion": "asc",
        "limit": None,
        "offset": 0,
    }
    assert reporte.total == 2
    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-como-a",
        "req-como-b",
    ]


def test_reporte_detalle_por_controlador_desde_store_con_paginacion() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-2",
            controlador_a="ATC_003",
            controlador_b="ATC_001",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-3",
            controlador_a="ATC_001",
            controlador_b="ATC_004",
            fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
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


def test_reporte_detalle_por_controlador_desde_store_devuelve_vacio_si_no_hay_match() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_999",
    )

    assert reporte.total == 0
    assert reporte.detalles == []
    assert reporte.paginacion.total == 0
    assert reporte.paginacion.returned == 0
    assert reporte.paginacion.has_more is False