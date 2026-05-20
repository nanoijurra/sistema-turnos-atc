from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import (
    MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA,
    generar_reporte_detalle_requests_creados_desde_oferta,
)
from src.request_store import guardar_request, limpiar_requests


def _crear_request(
    *,
    request_id: str,
    estado: str,
    selected_by: str | None,
    modo_exploracion: str | None,
    clasificacion_observada: str | None,
    offer_rank_observado: int | None,
) -> SwapRequest:
    return SwapRequest(
        id=request_id,
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado=estado,
        fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
        roster_version_id="rv-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "selected_by": selected_by,
            "selection_reason": "Motivo de seleccion",
            "selection_note": "Nota operativa",
            "modo_exploracion": modo_exploracion,
            "clasificacion_observada": clasificacion_observada,
            "offer_rank_observado": offer_rank_observado,
        },
    )


def setup_function() -> None:
    limpiar_requests()


def test_generar_reporte_detalle_requests_creados_desde_oferta_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
            offer_rank_observado=1,
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-2",
            estado="EVALUADO",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
            offer_rank_observado=2,
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta()

    assert reporte.mensaje == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA
    assert reporte.total == 2
    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-1",
        "req-2",
    ]

    detalle_1 = reporte.detalles[0]

    assert detalle_1.estado == "PENDIENTE"
    assert detalle_1.controlador_a == "ATC_001"
    assert detalle_1.controlador_b == "ATC_002"
    assert detalle_1.idx_a == 0
    assert detalle_1.idx_b == 1
    assert detalle_1.roster_version_id == "rv-1"
    assert detalle_1.fecha_creacion == "2026-05-19T18:30:00"
    assert detalle_1.selected_by == "SUP_ACC_CBA"
    assert detalle_1.selection_reason == "Motivo de seleccion"
    assert detalle_1.selection_note == "Nota operativa"
    assert detalle_1.modo_exploracion == "OFERTA_RAPIDA"
    assert detalle_1.clasificacion_observada == "ACEPTABLE"
    assert detalle_1.offer_rank_observado == 1


def test_generar_reporte_detalle_requests_creados_desde_oferta_desde_store_con_filtros() -> None:
    guardar_request(
        _crear_request(
            request_id="req-match",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
            offer_rank_observado=1,
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-no-match",
            estado="EVALUADO",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
            offer_rank_observado=2,
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        estado="PENDIENTE",
        selected_by="SUP_ACC_CBA",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
    )

    assert reporte.filtros == {
        "estado": "PENDIENTE",
        "selected_by": "SUP_ACC_CBA",
        "modo_exploracion": "OFERTA_RAPIDA",
        "clasificacion_observada": "ACEPTABLE",
        "ordenar_por": None,
        "direccion": "asc",
        "limit": None,
        "offset": 0,
    }
    assert reporte.total == 1
    assert len(reporte.detalles) == 1
    assert reporte.detalles[0].request_id == "req-match"


def test_reporte_detalle_to_dict_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
            offer_rank_observado=1,
        )
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta()
    datos = reporte.to_dict()

    assert datos["mensaje"] == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA
    assert datos["total"] == 1
    assert datos["detalles"][0]["request_id"] == "req-1"
    assert datos["detalles"][0]["estado"] == "PENDIENTE"
    assert datos["detalles"][0]["selected_by"] == "SUP_ACC_CBA"