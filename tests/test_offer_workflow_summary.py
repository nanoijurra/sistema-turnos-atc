from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models import SwapRequest
from src.offer_workflow_service import (
    OfferRequestSummary,
    resumir_requests_creados_desde_oferta,
)


def _crear_request(
    *,
    request_id: str,
    estado: str,
    selected_by: str | None,
    modo_exploracion: str | None,
    clasificacion_observada: str | None,
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


def _crear_requests_base() -> list[SwapRequest]:
    return [
        _crear_request(
            request_id="req-1",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        ),
        _crear_request(
            request_id="req-2",
            estado="EVALUADO",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
        ),
        _crear_request(
            request_id="req-3",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="DIAGNOSTICO_COMPLETO",
            clasificacion_observada="ACEPTABLE",
        ),
    ]


def test_resumir_requests_creados_desde_oferta_calcula_conteos(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: _crear_requests_base(),
    )

    resumen = resumir_requests_creados_desde_oferta()

    assert resumen.total == 3
    assert resumen.por_estado == {
        "PENDIENTE": 2,
        "EVALUADO": 1,
    }
    assert resumen.por_clasificacion_observada == {
        "ACEPTABLE": 2,
        "BENEFICIOSO": 1,
    }
    assert resumen.por_selected_by == {
        "SUP_ACC_CBA": 2,
        "SUP_TMA": 1,
    }
    assert resumen.por_modo_exploracion == {
        "OFERTA_RAPIDA": 2,
        "DIAGNOSTICO_COMPLETO": 1,
    }


def test_resumen_to_dict_devuelve_estructura_serializable() -> None:
    resumen = OfferRequestSummary(
        total=2,
        por_estado={"PENDIENTE": 2},
        por_clasificacion_observada={"ACEPTABLE": 2},
        por_selected_by={"SUP_ACC_CBA": 2},
        por_modo_exploracion={"OFERTA_RAPIDA": 2},
    )

    assert resumen.to_dict() == {
        "total": 2,
        "por_estado": {"PENDIENTE": 2},
        "por_clasificacion_observada": {"ACEPTABLE": 2},
        "por_selected_by": {"SUP_ACC_CBA": 2},
        "por_modo_exploracion": {"OFERTA_RAPIDA": 2},
    }


def test_resumir_requests_creados_desde_oferta_respeta_filtros(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    filtros_recibidos = []

    def listar_filtrado_fake(**kwargs: Any) -> list[SwapRequest]:
        filtros_recibidos.append(kwargs)
        return [
            _crear_request(
                request_id="req-1",
                estado="PENDIENTE",
                selected_by="SUP_ACC_CBA",
                modo_exploracion="OFERTA_RAPIDA",
                clasificacion_observada="ACEPTABLE",
            )
        ]

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        listar_filtrado_fake,
    )

    resumen = resumir_requests_creados_desde_oferta(
        estado="PENDIENTE",
        selected_by="SUP_ACC_CBA",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
    )

    assert filtros_recibidos == [
        {
            "estado": "PENDIENTE",
            "selected_by": "SUP_ACC_CBA",
            "modo_exploracion": "OFERTA_RAPIDA",
            "clasificacion_observada": "ACEPTABLE",
        }
    ]

    assert resumen.total == 1
    assert resumen.por_estado == {"PENDIENTE": 1}


def test_resumir_requests_creados_desde_oferta_usa_sin_dato_si_falta_metadata(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    request = _crear_request(
        request_id="req-1",
        estado="PENDIENTE",
        selected_by=None,
        modo_exploracion=None,
        clasificacion_observada=None,
    )

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: [request],
    )

    resumen = resumir_requests_creados_desde_oferta()

    assert resumen.total == 1
    assert resumen.por_estado == {"PENDIENTE": 1}
    assert resumen.por_clasificacion_observada == {"SIN_DATO": 1}
    assert resumen.por_selected_by == {"SIN_DATO": 1}
    assert resumen.por_modo_exploracion == {"SIN_DATO": 1}


def test_resumir_requests_creados_desde_oferta_no_evalua_no_decide_no_aplica(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    monkeypatch.setattr(
        modulo,
        "listar_requests_creados_desde_oferta_filtrados",
        lambda **kwargs: _crear_requests_base(),
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resumen = resumir_requests_creados_desde_oferta()

    assert resumen.total == 3
    