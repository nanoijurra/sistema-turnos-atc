from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from src.models import SwapRequest
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_workflow_service import (
    OfferSelectionResult,
    generar_oferta_crear_y_persistir_request,
)


def _crear_reporte_fake() -> OfferReport:
    return OfferReport(
        mensaje="Mostrando mejores candidatos evaluados segun filtros actuales.",
        modo_exploracion="OFERTA_RAPIDA",
        ofertas=[
            OfertaEvaluada(
                posicion=1,
                clasificacion="ACEPTABLE",
                delta_score=0.0,
                delta_hard=0,
                delta_soft=0,
                idx_a=0,
                idx_b=1,
                evaluacion={
                    "idx_a": 0,
                    "idx_b": 1,
                    "clasificacion": "ACEPTABLE",
                    "delta_score": 0,
                    "delta_hard": 0,
                    "delta_soft": 0,
                },
            )
        ],
        metadata={
            "modo_exploracion": "OFERTA_RAPIDA",
            "top_n": 50,
            "criterio_seleccion": "candidate_selection_v1",
            "roster_version_id_origen": "rv-1",
            "roster_hash_origen": "hash-1",
        },
    )


def _crear_request_fake() -> SwapRequest:
    return SwapRequest(
        id="req-v60",
        controlador_a="ATC_001",
        controlador_b="ATC_002",
        idx_a=0,
        idx_b=1,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo="CREADO_DESDE_OFERTA",
        roster_version_id="rv-1",
        offer_origin={
            "created_from_offer": True,
            "source_type": "OFERTA_EVALUADA",
            "offer_rank_observado": 1,
            "clasificacion_observada": "ACEPTABLE",
        },
    )


def test_generar_oferta_crear_y_persistir_request_combina_creacion_y_persistencia(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_fake()
    resultado_creacion = OfferSelectionResult(
        reporte=reporte,
        request=request,
    )

    llamadas_creacion = []
    llamadas_persistencia = []

    def generar_y_crear_fake(**kwargs: Any) -> OfferSelectionResult:
        llamadas_creacion.append(kwargs)
        return resultado_creacion

    def persistir_fake(*, request: SwapRequest) -> SwapRequest:
        llamadas_persistencia.append(request)
        return request

    monkeypatch.setattr(
        modulo,
        "generar_oferta_y_crear_request",
        generar_y_crear_fake,
    )
    monkeypatch.setattr(
        modulo,
        "persistir_request_creado_desde_oferta",
        persistir_fake,
    )

    resultado = generar_oferta_crear_y_persistir_request(
        asignacion_origen="asignacion-origen",
        asignaciones=["a", "b"],
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        modo_exploracion="OFERTA_RAPIDA",
        top_n=50,
        historial_controladores={"ATC_001": {"beneficios": 1}},
        limite_reporte=5,
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
        selected_by="SUP_ACC_CBA",
        selection_reason="Mejor alternativa disponible",
        selection_note="Seleccion y persistencia explicita",
    )

    assert llamadas_creacion == [
        {
            "asignacion_origen": "asignacion-origen",
            "asignaciones": ["a", "b"],
            "config_file": "config_equilibrado.json",
            "posicion_oferta": 1,
            "modo_exploracion": "OFERTA_RAPIDA",
            "top_n": 50,
            "historial_controladores": {"ATC_001": {"beneficios": 1}},
            "limite_reporte": 5,
            "roster_version_id_vigente": "rv-1",
            "roster_hash_vigente": "hash-1",
            "selected_by": "SUP_ACC_CBA",
            "selection_reason": "Mejor alternativa disponible",
            "selection_note": "Seleccion y persistencia explicita",
        }
    ]

    assert llamadas_persistencia == [request]
    assert resultado.reporte is reporte
    assert resultado.request is request
    assert resultado.request_id == "req-v60"
    assert resultado.cantidad_ofertas == 1


def test_generar_oferta_crear_y_persistir_request_usa_defaults_operativos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_fake()

    parametros_creacion = []

    def generar_y_crear_fake(**kwargs: Any) -> OfferSelectionResult:
        parametros_creacion.append(kwargs)
        return OfferSelectionResult(
            reporte=reporte,
            request=request,
        )

    monkeypatch.setattr(
        modulo,
        "generar_oferta_y_crear_request",
        generar_y_crear_fake,
    )
    monkeypatch.setattr(
        modulo,
        "persistir_request_creado_desde_oferta",
        lambda *, request: request,
    )

    resultado = generar_oferta_crear_y_persistir_request(
        asignacion_origen="origen",
        asignaciones=["a", "b"],
        config_file="config_equilibrado.json",
        posicion_oferta=1,
    )

    assert parametros_creacion[0]["modo_exploracion"] == "OFERTA_RAPIDA"
    assert parametros_creacion[0]["top_n"] == 50
    assert parametros_creacion[0]["historial_controladores"] is None
    assert parametros_creacion[0]["limite_reporte"] is None
    assert parametros_creacion[0]["selected_by"] is None
    assert parametros_creacion[0]["selection_reason"] is None
    assert parametros_creacion[0]["selection_note"] is None
    assert resultado.request.estado == "PENDIENTE"


def test_generar_oferta_crear_y_persistir_request_no_evalua_no_decide_no_aplica(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_fake()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_y_crear_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )
    monkeypatch.setattr(
        modulo,
        "persistir_request_creado_desde_oferta",
        lambda *, request: request,
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, resolver ni aplicar")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resultado = generar_oferta_crear_y_persistir_request(
        asignacion_origen="origen",
        asignaciones=["a", "b"],
        config_file="config_equilibrado.json",
        posicion_oferta=1,
    )

    assert resultado.request.estado == "PENDIENTE"
    assert resultado.request.decision_sugerida is None


def test_generar_oferta_crear_y_persistir_request_propaga_error_de_creacion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    def generar_y_crear_fake(**kwargs: Any) -> OfferSelectionResult:
        raise ValueError("No existe una oferta con posicion 99 en el reporte.")

    monkeypatch.setattr(
        modulo,
        "generar_oferta_y_crear_request",
        generar_y_crear_fake,
    )

    with pytest.raises(ValueError, match="No existe una oferta"):
        generar_oferta_crear_y_persistir_request(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=99,
        )


def test_generar_oferta_crear_y_persistir_request_propaga_error_de_persistencia(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_fake()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_y_crear_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def persistir_fake(*, request: SwapRequest) -> SwapRequest:
        raise ValueError("No se puede persistir como request desde oferta sin offer_origin.")

    monkeypatch.setattr(
        modulo,
        "persistir_request_creado_desde_oferta",
        persistir_fake,
    )

    with pytest.raises(ValueError, match="offer_origin"):
        generar_oferta_crear_y_persistir_request(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=1,
        )