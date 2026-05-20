from __future__ import annotations

from datetime import datetime

from src.models import SwapRequest
from src.offer_workflow_service import resumir_requests_creados_desde_oferta
from src.request_store import guardar_request, limpiar_requests


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


def setup_function() -> None:
    limpiar_requests()


def test_resumir_requests_creados_desde_oferta_desde_store() -> None:
    guardar_request(
        _crear_request(
            request_id="req-1",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-2",
            estado="EVALUADO",
            selected_by="SUP_TMA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="BENEFICIOSO",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-3",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="DIAGNOSTICO_COMPLETO",
            clasificacion_observada="ACEPTABLE",
        )
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


def test_resumir_requests_creados_desde_oferta_desde_store_con_filtros() -> None:
    guardar_request(
        _crear_request(
            request_id="req-match",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="OFERTA_RAPIDA",
            clasificacion_observada="ACEPTABLE",
        )
    )
    guardar_request(
        _crear_request(
            request_id="req-no-match",
            estado="PENDIENTE",
            selected_by="SUP_ACC_CBA",
            modo_exploracion="DIAGNOSTICO_COMPLETO",
            clasificacion_observada="ACEPTABLE",
        )
    )

    resumen = resumir_requests_creados_desde_oferta(
        estado="PENDIENTE",
        selected_by="SUP_ACC_CBA",
        modo_exploracion="OFERTA_RAPIDA",
        clasificacion_observada="ACEPTABLE",
    )

    assert resumen.total == 1
    assert resumen.por_estado == {"PENDIENTE": 1}
    assert resumen.por_clasificacion_observada == {"ACEPTABLE": 1}
    assert resumen.por_selected_by == {"SUP_ACC_CBA": 1}
    assert resumen.por_modo_exploracion == {"OFERTA_RAPIDA": 1}