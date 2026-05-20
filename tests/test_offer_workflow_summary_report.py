from __future__ import annotations

from typing import Any

from src.offer_workflow_service import (
    MENSAJE_RESUMEN_REQUESTS_DESDE_OFERTA,
    OfferRequestSummary,
    OfferRequestSummaryReport,
    generar_reporte_resumen_requests_creados_desde_oferta,
)


def _crear_resumen_fake() -> OfferRequestSummary:
    return OfferRequestSummary(
        total=3,
        por_estado={
            "PENDIENTE": 2,
            "EVALUADO": 1,
        },
        por_clasificacion_observada={
            "ACEPTABLE": 2,
            "BENEFICIOSO": 1,
        },
        por_selected_by={
            "SUP_ACC_CBA": 2,
            "SUP_TMA": 1,
        },
        por_modo_exploracion={
            "OFERTA_RAPIDA": 2,
            "DIAGNOSTICO_COMPLETO": 1,
        },
    )


def test_offer_request_summary_no_expone_propiedades_de_selection_result() -> None:
    resumen = _crear_resumen_fake()

    assert not hasattr(resumen, "request_id")
    assert not hasattr(resumen, "cantidad_ofertas")


def test_offer_request_summary_report_to_dict_devuelve_estructura_presentable() -> None:
    resumen = _crear_resumen_fake()
    reporte = OfferRequestSummaryReport(
        mensaje=MENSAJE_RESUMEN_REQUESTS_DESDE_OFERTA,
        filtros={
            "estado": "PENDIENTE",
            "selected_by": "SUP_ACC_CBA",
            "modo_exploracion": "OFERTA_RAPIDA",
            "clasificacion_observada": "ACEPTABLE",
        },
        resumen=resumen,
    )

    assert reporte.to_dict() == {
        "mensaje": MENSAJE_RESUMEN_REQUESTS_DESDE_OFERTA,
        "filtros": {
            "estado": "PENDIENTE",
            "selected_by": "SUP_ACC_CBA",
            "modo_exploracion": "OFERTA_RAPIDA",
            "clasificacion_observada": "ACEPTABLE",
        },
        "resumen": resumen.to_dict(),
    }


def test_generar_reporte_resumen_requests_creados_desde_oferta_combina_filtros_y_resumen(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    resumen = _crear_resumen_fake()
    llamadas = []

    def resumir_fake(**kwargs: Any) -> OfferRequestSummary:
        llamadas.append(kwargs)
        return resumen

    monkeypatch.setattr(
        modulo,
        "resumir_requests_creados_desde_oferta",
        resumir_fake,
    )

    reporte = generar_reporte_resumen_requests_creados_desde_oferta(
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

    assert reporte.mensaje == MENSAJE_RESUMEN_REQUESTS_DESDE_OFERTA
    assert reporte.filtros == {
        "estado": "PENDIENTE",
        "selected_by": "SUP_ACC_CBA",
        "modo_exploracion": "OFERTA_RAPIDA",
        "clasificacion_observada": "ACEPTABLE",
    }
    assert reporte.resumen is resumen


def test_generar_reporte_resumen_requests_creados_desde_oferta_sin_filtros(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    resumen = _crear_resumen_fake()

    monkeypatch.setattr(
        modulo,
        "resumir_requests_creados_desde_oferta",
        lambda **kwargs: resumen,
    )

    reporte = generar_reporte_resumen_requests_creados_desde_oferta()

    assert reporte.filtros == {
        "estado": None,
        "selected_by": None,
        "modo_exploracion": None,
        "clasificacion_observada": None,
    }
    assert reporte.resumen is resumen


def test_reporte_resumen_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "resumir_requests_creados_desde_oferta",
        lambda **kwargs: _crear_resumen_fake(),
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    reporte = generar_reporte_resumen_requests_creados_desde_oferta()

    assert reporte.resumen.total == 3