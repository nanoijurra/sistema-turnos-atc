from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from src.models import SwapRequest
from src.offer_workflow_service import (
    MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA_POR_CONTROLADOR,
    generar_reporte_detalle_requests_creados_desde_oferta_por_controlador,
)


def _crear_request(
    *,
    request_id: str,
    controlador_a: str,
    controlador_b: str,
    fecha_creacion: datetime,
    clasificacion_observada: str,
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
            "clasificacion_observada": clasificacion_observada,
            "offer_rank_observado": 1,
        },
    )


def _crear_requests_base() -> list[SwapRequest]:
    return [
        _crear_request(
            request_id="req-3",
            controlador_a="ATC_001",
            controlador_b="ATC_002",
            fecha_creacion=datetime(2026, 5, 19, 18, 30, 0),
            clasificacion_observada="RECHAZABLE",
        ),
        _crear_request(
            request_id="req-1",
            controlador_a="ATC_003",
            controlador_b="ATC_001",
            fecha_creacion=datetime(2026, 5, 19, 18, 10, 0),
            clasificacion_observada="BENEFICIOSO",
        ),
        _crear_request(
            request_id="req-2",
            controlador_a="ATC_001",
            controlador_b="ATC_004",
            fecha_creacion=datetime(2026, 5, 19, 18, 20, 0),
            clasificacion_observada="ACEPTABLE",
        ),
    ]


def test_reporte_detalle_por_controlador_construye_salida_presentable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_por_controlador",
        lambda *, controlador: _crear_requests_base(),
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
    )

    assert reporte.mensaje == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA_POR_CONTROLADOR
    assert reporte.filtros == {
        "controlador": "ATC_001",
        "ordenar_por": None,
        "direccion": "asc",
        "limit": None,
        "offset": 0,
    }
    assert reporte.total == 3
    assert reporte.paginacion.total == 3
    assert reporte.paginacion.returned == 3
    assert reporte.paginacion.has_more is False
    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-3",
        "req-1",
        "req-2",
    ]


def test_reporte_detalle_por_controlador_ordena_por_request_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_por_controlador",
        lambda *, controlador: _crear_requests_base(),
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
        ordenar_por="request_id",
        direccion="asc",
    )

    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-1",
        "req-2",
        "req-3",
    ]
    assert reporte.filtros["ordenar_por"] == "request_id"
    assert reporte.filtros["direccion"] == "asc"


def test_reporte_detalle_por_controlador_pagina_resultados(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_por_controlador",
        lambda *, controlador: _crear_requests_base(),
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


def test_reporte_detalle_por_controlador_to_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_por_controlador",
        lambda *, controlador: _crear_requests_base(),
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
        ordenar_por="request_id",
        direccion="asc",
        limit=2,
        offset=0,
    )
    datos = reporte.to_dict()

    assert datos["mensaje"] == MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA_POR_CONTROLADOR
    assert datos["filtros"] == {
        "controlador": "ATC_001",
        "ordenar_por": "request_id",
        "direccion": "asc",
        "limit": 2,
        "offset": 0,
    }
    assert datos["total"] == 3
    assert datos["paginacion"] == {
        "limit": 2,
        "offset": 0,
        "total": 3,
        "returned": 2,
        "has_more": True,
    }
    assert [detalle["request_id"] for detalle in datos["detalles"]] == [
        "req-1",
        "req-2",
    ]


def test_reporte_detalle_por_controlador_propaga_error_de_controlador_vacio(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    def listar_fake(*, controlador: str) -> list[SwapRequest]:
        raise ValueError("El controlador no puede estar vacio.")

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_por_controlador",
        listar_fake,
    )

    with pytest.raises(ValueError, match="controlador no puede estar vacio"):
        generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
            controlador="",
        )


def test_reporte_detalle_por_controlador_no_evalua_no_decide_no_aplica(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_por_controlador",
        lambda *, controlador: _crear_requests_base(),
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    reporte = generar_reporte_detalle_requests_creados_desde_oferta_por_controlador(
        controlador="ATC_001",
    )

    assert reporte.total == 3