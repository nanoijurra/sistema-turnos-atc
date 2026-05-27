from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from src.models import SwapRequest
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_workflow_service import (
    OfferFormalEvaluationResult,
    OfferSelectionResult,
    crear_request_desde_oferta_y_evaluar_formalmente,
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
        },
    )


def _crear_request_pendiente() -> SwapRequest:
    return SwapRequest(
        id="req-v72",
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
            "clasificacion_observada": "ACEPTABLE",
            "delta_score_observado": 0,
            "selected_by": "SUP_ACC_CBA",
        },
    )


def test_crear_request_desde_oferta_y_evaluar_formalmente_crea_pendiente_y_luego_evalua(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()
    estados_observados = []

    def crear_y_persistir_fake(**kwargs: Any) -> OfferSelectionResult:
        estados_observados.append(request.estado)
        return OfferSelectionResult(
            reporte=reporte,
            request=request,
        )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        assert kwargs["request"] is request
        assert kwargs["request"].estado == "PENDIENTE"
        assert kwargs["request"].offer_origin is not None
        assert kwargs["evaluar_swap_fn"] == "evaluador-formal"
        assert kwargs["config_file"] == "config_equilibrado.json"

        request.estado = "EVALUADO"
        request.decision_sugerida = "OBSERVAR"

        return {
            "request_id": request.id,
            "clasificacion": "ACEPTABLE",
            "decision": "OBSERVAR",
            "evaluacion": {
                "clasificacion": "ACEPTABLE",
                "delta_score": 0,
                "delta_hard": 0,
                "delta_soft": 0,
            },
        }

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        crear_y_persistir_fake,
    )
    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    resultado = crear_request_desde_oferta_y_evaluar_formalmente(
        asignacion_origen="origen",
        asignaciones=["a", "b"],
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        evaluar_swap_fn="evaluador-formal",
        selected_by="SUP_ACC_CBA",
    )

    assert estados_observados == ["PENDIENTE"]
    assert isinstance(resultado, OfferFormalEvaluationResult)
    assert resultado.reporte is reporte
    assert resultado.request is request
    assert resultado.request.estado == "EVALUADO"
    assert resultado.estado == "EVALUADO"
    assert resultado.request_id == "req-v72"
    assert resultado.decision_sugerida == "OBSERVAR"
    assert resultado.evaluacion_formal["clasificacion"] == "ACEPTABLE"
    assert resultado.evaluacion_formal["decision"] == "OBSERVAR"


def test_crear_request_desde_oferta_y_evaluar_formalmente_preserva_offer_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()
    offer_origin_original = dict(request.offer_origin or {})

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        request.estado = "EVALUADO"
        request.decision_sugerida = "OBSERVAR"
        return {
            "request_id": request.id,
            "clasificacion": "BENEFICIOSO",
            "decision": "VIABLE",
            "evaluacion": {},
        }

    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    resultado = crear_request_desde_oferta_y_evaluar_formalmente(
        asignacion_origen="origen",
        asignaciones=["a", "b"],
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        evaluar_swap_fn="evaluador-formal",
    )

    assert resultado.request.offer_origin == offer_origin_original
    assert resultado.request.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert resultado.evaluacion_formal["clasificacion"] == "BENEFICIOSO"


def test_crear_request_desde_oferta_y_evaluar_formalmente_no_evalua_si_creacion_falla(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    def crear_y_persistir_fake(**kwargs: Any) -> OfferSelectionResult:
        raise ValueError("No existe una oferta con posicion 99 en el reporte.")

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        raise AssertionError("No debe evaluar si falla la creacion desde oferta.")

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        crear_y_persistir_fake,
    )
    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    with pytest.raises(ValueError, match="No existe una oferta"):
        crear_request_desde_oferta_y_evaluar_formalmente(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=99,
            evaluar_swap_fn="evaluador-formal",
        )


def test_crear_request_desde_oferta_y_evaluar_formalmente_rechaza_request_que_no_nace_pendiente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()
    request.estado = "EVALUADO"

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        raise AssertionError("No debe evaluar un request que no nacio PENDIENTE.")

    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    with pytest.raises(ValueError, match="PENDIENTE antes de la evaluacion formal"):
        crear_request_desde_oferta_y_evaluar_formalmente(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=1,
            evaluar_swap_fn="evaluador-formal",
        )


def test_crear_request_desde_oferta_y_evaluar_formalmente_rechaza_request_sin_offer_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()
    request.offer_origin = None

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        raise AssertionError("No debe evaluar un request sin offer_origin.")

    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    with pytest.raises(ValueError, match="conservar offer_origin"):
        crear_request_desde_oferta_y_evaluar_formalmente(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=1,
            evaluar_swap_fn="evaluador-formal",
        )


def test_crear_request_desde_oferta_y_evaluar_formalmente_propaga_error_de_evaluacion_formal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        raise ValueError("Error formal de evaluacion.")

    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    with pytest.raises(ValueError, match="Error formal de evaluacion"):
        crear_request_desde_oferta_y_evaluar_formalmente(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=1,
            evaluar_swap_fn="evaluador-formal",
        )


def test_crear_request_desde_oferta_y_evaluar_formalmente_rechaza_si_evaluacion_no_deja_evaluado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        request.estado = "PENDIENTE"
        return {
            "request_id": request.id,
            "clasificacion": "ACEPTABLE",
            "decision": "OBSERVAR",
            "evaluacion": {},
        }

    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    with pytest.raises(ValueError, match="estado EVALUADO"):
        crear_request_desde_oferta_y_evaluar_formalmente(
            asignacion_origen="origen",
            asignaciones=["a", "b"],
            config_file="config_equilibrado.json",
            posicion_oferta=1,
            evaluar_swap_fn="evaluador-formal",
        )


def test_crear_request_desde_oferta_y_evaluar_formalmente_no_aprueba_no_rechaza_no_aplica(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_workflow_service as modulo

    reporte = _crear_reporte_fake()
    request = _crear_request_pendiente()

    monkeypatch.setattr(
        modulo,
        "generar_oferta_crear_y_persistir_request",
        lambda **kwargs: OfferSelectionResult(reporte=reporte, request=request),
    )

    def evaluar_formal_fake(**kwargs: Any) -> dict[str, Any]:
        request.estado = "EVALUADO"
        request.decision_sugerida = "OBSERVAR"
        return {
            "request_id": request.id,
            "clasificacion": "ACEPTABLE",
            "decision": "OBSERVAR",
            "evaluacion": {},
        }

    monkeypatch.setattr(
        modulo,
        "evaluar_swap_request_formal",
        evaluar_formal_fake,
    )

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe resolver, cancelar ni aplicar.")

    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    resultado = crear_request_desde_oferta_y_evaluar_formalmente(
        asignacion_origen="origen",
        asignaciones=["a", "b"],
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        evaluar_swap_fn="evaluador-formal",
    )

    assert resultado.request.estado == "EVALUADO"
    assert resultado.request.decision_sugerida == "OBSERVAR"