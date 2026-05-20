from __future__ import annotations

import pytest

from src.offer_workflow_service import (
    OfferRequestDetail,
    generar_reporte_detalle_requests_creados_desde_oferta,
    ordenar_detalles_requests_desde_oferta,
)


def _crear_detalle(
    *,
    request_id: str,
    estado: str,
    fecha_creacion: str | None,
    selected_by: str | None,
    modo_exploracion: str | None,
    clasificacion_observada: str | None,
) -> OfferRequestDetail:
    return OfferRequestDetail(
        request_id=request_id,
        estado=estado,
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        roster_version_id="rv-1",
        fecha_creacion=fecha_creacion,
        selected_by=selected_by,
        selection_reason=None,
        selection_note=None,
        modo_exploracion=modo_exploracion,
        clasificacion_observada=clasificacion_observada,
        offer_rank_observado=None,
    )


def _crear_detalles_base() -> list[OfferRequestDetail]:
    return [
        _crear_detalle(
            request_id="req-3",
            estado="PENDIENTE",
            fecha_creacion="2026-05-19T18:30:00",
            selected_by="SUP_TMA",
            modo_exploracion="DIAGNOSTICO_COMPLETO",
            clasificacion_observada="RECHAZABLE",
        ),
        _crear_detalle(
            request_id="req-1",
            estado="EVALUADO",
            fecha_creacion="2026-05-19T18:10:00",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
        ),
        _crear_detalle(
            request_id="req-2",
            estado="PENDIENTE",
            fecha_creacion="2026-05-19T18:20:00",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        ),
    ]


def test_ordenar_detalles_por_request_id_asc() -> None:
    resultado = ordenar_detalles_requests_desde_oferta(
        detalles=_crear_detalles_base(),
        ordenar_por="request_id",
        direccion="asc",
    )

    assert [detalle.request_id for detalle in resultado] == [
        "req-1",
        "req-2",
        "req-3",
    ]


def test_ordenar_detalles_por_fecha_creacion_desc() -> None:
    resultado = ordenar_detalles_requests_desde_oferta(
        detalles=_crear_detalles_base(),
        ordenar_por="fecha_creacion",
        direccion="desc",
    )

    assert [detalle.request_id for detalle in resultado] == [
        "req-3",
        "req-2",
        "req-1",
    ]


def test_ordenar_detalles_por_estado() -> None:
    resultado = ordenar_detalles_requests_desde_oferta(
        detalles=_crear_detalles_base(),
        ordenar_por="estado",
        direccion="asc",
    )

    assert [detalle.estado for detalle in resultado] == [
        "EVALUADO",
        "PENDIENTE",
        "PENDIENTE",
    ]


def test_ordenar_detalles_sin_criterio_preserva_orden() -> None:
    detalles = _crear_detalles_base()

    resultado = ordenar_detalles_requests_desde_oferta(
        detalles=detalles,
        ordenar_por=None,
        direccion="asc",
    )

    assert resultado == detalles
    assert resultado is not detalles


def test_ordenar_detalles_rechaza_criterio_no_soportado() -> None:
    with pytest.raises(ValueError, match="Criterio de ordenamiento no soportado"):
        ordenar_detalles_requests_desde_oferta(
            detalles=_crear_detalles_base(),
            ordenar_por="decision_sugerida",
            direccion="asc",
        )


def test_ordenar_detalles_rechaza_direccion_no_soportada() -> None:
    with pytest.raises(ValueError, match="Direccion de ordenamiento no soportada"):
        ordenar_detalles_requests_desde_oferta(
            detalles=_crear_detalles_base(),
            ordenar_por="request_id",
            direccion="invalida",
        )


def test_generar_reporte_detalle_requests_creados_desde_oferta_aplica_ordenamiento(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    detalles = _crear_detalles_base()

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        modulo,
        "construir_detalle_request_creado_desde_oferta",
        lambda **kwargs: None,
    )

    def construir_detalles_fake(**kwargs):
        return detalles

    monkeypatch.setattr(
        modulo,
        "ordenar_detalles_requests_desde_oferta",
        lambda *, detalles, ordenar_por, direccion: sorted(
            detalles,
            key=lambda detalle: detalle.request_id,
            reverse=direccion == "desc",
        ),
    )

    # Evitamos depender de requests reales en este test:
    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: ["req-a", "req-b", "req-c"],
    )

    detalle_iter = iter(detalles)

    monkeypatch.setattr(
        modulo,
        "construir_detalle_request_creado_desde_oferta",
        lambda **kwargs: next(detalle_iter),
    )

    reporte = generar_reporte_detalle_requests_creados_desde_oferta(
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


def test_generar_reporte_detalle_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    detalles = _crear_detalles_base()

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: ["req-a", "req-b", "req-c"],
    )

    detalle_iter = iter(detalles)

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
        ordenar_por="fecha_creacion",
        direccion="desc",
    )

    assert reporte.total == 3