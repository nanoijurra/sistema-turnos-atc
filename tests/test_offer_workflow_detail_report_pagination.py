from __future__ import annotations

import pytest

from src.offer_workflow_service import (
    OfferRequestDetail,
    OfferRequestPagination,
    generar_reporte_detalle_requests_creados_desde_oferta,
    paginar_detalles_requests_desde_oferta,
)


def _crear_detalle(request_id: str) -> OfferRequestDetail:
    return OfferRequestDetail(
        request_id=request_id,
        estado="PENDIENTE",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        roster_version_id="rv-1",
        fecha_creacion=None,
        selected_by="SUP_ACC_CBA",
        selection_reason=None,
        selection_note=None,
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
        offer_rank_observado=None,
    )


def _crear_detalles() -> list[OfferRequestDetail]:
    return [
        _crear_detalle("req-1"),
        _crear_detalle("req-2"),
        _crear_detalle("req-3"),
        _crear_detalle("req-4"),
    ]


def test_offer_request_pagination_to_dict() -> None:
    paginacion = OfferRequestPagination(
        limit=2,
        offset=1,
        total=4,
        returned=2,
        has_more=True,
    )

    assert paginacion.to_dict() == {
        "limit": 2,
        "offset": 1,
        "total": 4,
        "returned": 2,
        "has_more": True,
    }


def test_paginar_detalles_con_limit_y_offset() -> None:
    detalles, paginacion = paginar_detalles_requests_desde_oferta(
        detalles=_crear_detalles(),
        limit=2,
        offset=1,
    )

    assert [detalle.request_id for detalle in detalles] == [
        "req-2",
        "req-3",
    ]
    assert paginacion.limit == 2
    assert paginacion.offset == 1
    assert paginacion.total == 4
    assert paginacion.returned == 2
    assert paginacion.has_more is True


def test_paginar_detalles_sin_limit_devuelve_desde_offset_hasta_final() -> None:
    detalles, paginacion = paginar_detalles_requests_desde_oferta(
        detalles=_crear_detalles(),
        limit=None,
        offset=2,
    )

    assert [detalle.request_id for detalle in detalles] == [
        "req-3",
        "req-4",
    ]
    assert paginacion.limit is None
    assert paginacion.offset == 2
    assert paginacion.total == 4
    assert paginacion.returned == 2
    assert paginacion.has_more is False


def test_paginar_detalles_offset_fuera_de_rango_devuelve_lista_vacia() -> None:
    detalles, paginacion = paginar_detalles_requests_desde_oferta(
        detalles=_crear_detalles(),
        limit=2,
        offset=10,
    )

    assert detalles == []
    assert paginacion.limit == 2
    assert paginacion.offset == 10
    assert paginacion.total == 4
    assert paginacion.returned == 0
    assert paginacion.has_more is False


def test_paginar_detalles_rechaza_limit_invalido() -> None:
    with pytest.raises(ValueError, match="limite de paginacion"):
        paginar_detalles_requests_desde_oferta(
            detalles=_crear_detalles(),
            limit=0,
            offset=0,
        )


def test_paginar_detalles_rechaza_offset_negativo() -> None:
    with pytest.raises(ValueError, match="offset de paginacion"):
        paginar_detalles_requests_desde_oferta(
            detalles=_crear_detalles(),
            limit=2,
            offset=-1,
        )


def test_generar_reporte_detalle_requests_creados_desde_oferta_aplica_paginacion(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    detalles_base = _crear_detalles()
    detalle_iter = iter(detalles_base)

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: ["req-1", "req-2", "req-3", "req-4"],
    )
    monkeypatch.setattr(
        modulo,
        "construir_detalle_request_creado_desde_oferta",
        lambda **kwargs: next(detalle_iter),
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        limit=2,
        offset=1,
    )

    assert reporte.total == 4
    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-2",
        "req-3",
    ]
    assert reporte.paginacion.limit == 2
    assert reporte.paginacion.offset == 1
    assert reporte.paginacion.total == 4
    assert reporte.paginacion.returned == 2
    assert reporte.paginacion.has_more is True
    assert reporte.filtros["limit"] == 2
    assert reporte.filtros["offset"] == 1


def test_generar_reporte_detalle_requests_creados_desde_oferta_pagina_despues_de_ordenar(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    detalles_base = [
        _crear_detalle("req-3"),
        _crear_detalle("req-1"),
        _crear_detalle("req-2"),
    ]
    detalle_iter = iter(detalles_base)

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: ["req-3", "req-1", "req-2"],
    )
    monkeypatch.setattr(
        modulo,
        "construir_detalle_request_creado_desde_oferta",
        lambda **kwargs: next(detalle_iter),
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        ordenar_por="request_id",
        direccion="asc",
        limit=2,
        offset=0,
    )

    assert [detalle.request_id for detalle in reporte.detalles] == [
        "req-1",
        "req-2",
    ]
    assert reporte.total == 3
    assert reporte.paginacion.returned == 2
    assert reporte.paginacion.has_more is True


def test_generar_reporte_detalle_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    detalle_iter = iter(_crear_detalles())

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: ["req-1", "req-2", "req-3", "req-4"],
    )
    monkeypatch.setattr(
        modulo,
        "construir_detalle_request_creado_desde_oferta",
        lambda **kwargs: next(detalle_iter),
    )

    def prohibido(*args, **kwargs) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
        limit=2,
        offset=1,
    )

    assert reporte.total == 4