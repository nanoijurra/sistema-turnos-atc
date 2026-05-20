from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models import SwapRequest
from src.offer_workflow_service import (
    MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA,
    OfferRequestDetail,
    OfferRequestDetailReport,
    construir_detalle_request_creado_desde_oferta,
    generar_reporte_detalle_requests_creados_desde_oferta,
)


def _crear_request(
    *,
    request_id: str = "req-1",
    estado: str = "PENDIENTE",
    selected_by: str | None = "SUP_ACC_CBA",
    selection_reason: str | None = "Mejor alternativa disponible",
    selection_note: str | None = "Nota operativa",
    modo_exploracion: str | None = "OFERTA_RAPIDA",
    clasificacion_observada: str | None = "ACEPTABLE",
    offer_rank_observado: int | None = 1,
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
            "selection_reason": selection_reason,
            "selection_note": selection_note,
            "modo_exploracion": modo_exploracion,
            "clasificacion_observada": clasificacion_observada,
            "offer_rank_observado": offer_rank_observado,
        },
    )


def test_construir_detalle_request_creado_desde_oferta_mapea_campos() -> None:
    request = _crear_request()

    detalle = construir_detalle_request_creado_desde_oferta(request=request)

    assert detalle.request_id == "req-1"
    assert detalle.estado == "PENDIENTE"
    assert detalle.controlador_a == "ATC_001"
    assert detalle.controlador_b == "ATC_002"
    assert detalle.idx_a == 0
    assert detalle.idx_b == 1
    assert detalle.roster_version_id == "rv-1"
    assert detalle.fecha_creacion == "2026-05-19T18:30:00"
    assert detalle.selected_by == "SUP_ACC_CBA"
    assert detalle.selection_reason == "Mejor alternativa disponible"
    assert detalle.selection_note == "Nota operativa"
    assert detalle.modo_exploracion == "OFERTA_RAPIDA"
    assert detalle.clasificacion_observada == "ACEPTABLE"
    assert detalle.offer_rank_observado == 1


def test_construir_detalle_request_creado_desde_oferta_tolera_offer_origin_incompleto() -> None:
    request = _crear_request()
    request.offer_origin = {
        "created_from_offer": True,
        "source_type": "OFERTA_EVALUADA",
    }

    detalle = construir_detalle_request_creado_desde_oferta(request=request)

    assert detalle.request_id == "req-1"
    assert detalle.selected_by is None
    assert detalle.selection_reason is None
    assert detalle.selection_note is None
    assert detalle.modo_exploracion is None
    assert detalle.clasificacion_observada is None
    assert detalle.offer_rank_observado is None


def test_offer_request_detail_to_dict_devuelve_estructura_serializable() -> None:
    detalle = OfferRequestDetail(
        request_id="req-1",
        estado="PENDIENTE",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        roster_version_id="rv-1",
        fecha_creacion="2026-05-19T18:30:00",
        selected_by="SUP_ACC_CBA",
        selection_reason="Motivo",
        selection_note="Nota",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
        offer_rank_observado=1,
    )

    assert detalle.to_dict() == {
        "request_id": "req-1",
        "estado": "PENDIENTE",
        "controlador_a": "ATC_001",
        "controlador_b": "ATC_002",
        "idx_a": 0,
        "idx_b": 1,
        "roster_version_id": "rv-1",
        "fecha_creacion": "2026-05-19T18:30:00",
        "selected_by": "SUP_ACC_CBA",
        "selection_reason": "Motivo",
        "selection_note": "Nota",
        "modo_exploracion": "OFERTA_RAPIDA",
        "clasificacion_observada": "ACEPTABLE",
        "offer_rank_observado": 1,
    }


def test_offer_request_detail_report_to_dict_devuelve_estructura_presentable() -> None:
    detalle = construir_detalle_request_creado_desde_oferta(
        request=_crear_request(),
    )
    reporte = OfferRequestDetailReport(
        mensaje=MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA,
        filtros={
            "estado": "PENDIENTE",
            "selected_by": "SUP_ACC_CBA",
        },
        total=1,
        detalles=[detalle],
    )

    datos = reporte.to_dict()

    assert datos["mensaje"] == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA
    assert datos["filtros"] == {
        "estado": "PENDIENTE",
        "selected_by": "SUP_ACC_CBA",
    }
    assert datos["total"] == 1
    assert datos["detalles"] == [detalle.to_dict()]


def test_generar_reporte_detalle_requests_creados_desde_oferta_respeta_filtros(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    request = _crear_request()
    llamadas = []

    def listar_filtrado_fake(**kwargs: Any) -> list[SwapRequest]:
        llamadas.append(kwargs)
        return [request]

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        listar_filtrado_fake,
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        estado="PENDIENTE",
        selected_by="SUP_ACC_CBA",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
    )

    assert llamadas == [
        {
            "estado": "PENDIENTE",
            "selected_by": "SUP_ACC_CBA",
            "modo_exploracion": "OFERTA_RAPIDA",
            "clasificacion_observada": "ACEPTABLE",
        }
    ]

    assert reporte.mensaje == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA
    assert reporte.filtros == {
        "estado": "PENDIENTE",
        "selected_by": "SUP_ACC_CBA",
        "modo_exploracion": "OFERTA_RAPIDA",
        "clasificacion_observada": "ACEPTABLE",
        "ordenar_por": None,
        "direccion": "asc",
    }
    assert reporte.total == 1
    assert len(reporte.detalles) == 1
    assert reporte.detalles[0].request_id == "req-1"


def test_generar_reporte_detalle_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: [_crear_request()],
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    reporte = generar_reporte_detalle_requests_creados_desde_oferta()

    assert reporte.total == 1