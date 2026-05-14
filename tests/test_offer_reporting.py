from __future__ import annotations

import pytest

from src.exploration_flow import ExplorationFlowResult
from src.exploration_modes import MENSAJE_REPORTING_OFERTA_RAPIDA
from src.offer_reporting import generar_reporte_oferta


def _crear_resultado_fake() -> ExplorationFlowResult:
    return ExplorationFlowResult(
        modo_exploracion="OFERTA_RAPIDA",
        evaluaciones=[
            {
                "idx_a": 0,
                "idx_b": 2,
                "clasificacion": "BENEFICIOSO",
                "delta_score": 10,
                "delta_hard": 0,
                "delta_soft": -1,
                "impacto": {
                    "ATC_001": {"hard": 0, "soft": 0},
                    "ATC_003": {"hard": 0, "soft": -1},
                },
            },
            {
                "idx_a": 0,
                "idx_b": 1,
                "clasificacion": "ACEPTABLE",
                "delta_score": 0,
                "delta_hard": 0,
                "delta_soft": 0,
                "impacto": {
                    "ATC_001": {"hard": 0, "soft": 0},
                    "ATC_002": {"hard": 0, "soft": 0},
                },
            },
            {
                "idx_a": 0,
                "idx_b": 3,
                "clasificacion": "RECHAZABLE",
                "delta_score": -5,
                "delta_hard": 1,
                "delta_soft": 0,
                "impacto": {
                    "ATC_001": {"hard": 1, "soft": 0},
                    "ATC_004": {"hard": 0, "soft": 0},
                },
            },
        ],
        metadata={
            "modo_exploracion": "OFERTA_RAPIDA",
            "candidatos_generados": 100,
            "candidatos_prefiltrados": 80,
            "candidatos_seleccionados": 50,
            "candidatos_evaluados": 50,
            "top_n": 50,
            "criterio_seleccion": "candidate_selection_v1",
            "priorizacion_historica_aplicada": True,
            "tiempos_por_etapa": {
                "candidate_generation_ms": 1.0,
                "technical_prefilter_ms": 2.0,
                "candidate_selection_ms": 3.0,
                "simulator_ms": 4.0,
                "technical_ranking_ms": 5.0,
                "historical_prioritization_ms": 6.0,
                "total_ms": 21.0,
            },
            "campo_interno_no_visible": "no debe copiarse",
        },
    )


def test_generar_reporte_oferta_incluye_mensaje_seguro() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    assert reporte.mensaje == MENSAJE_REPORTING_OFERTA_RAPIDA
    assert "todos los swaps posibles" not in reporte.mensaje.lower()
    assert "mejores candidatos evaluados" in reporte.mensaje.lower()


def test_generar_reporte_oferta_preserva_modo_y_cantidad() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    assert reporte.modo_exploracion == "OFERTA_RAPIDA"
    assert reporte.cantidad_ofertas == 3


def test_generar_reporte_oferta_enumera_posiciones() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    assert [oferta.posicion for oferta in reporte.ofertas] == [1, 2, 3]


def test_generar_reporte_oferta_preserva_orden_del_flujo() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    assert [
        oferta.clasificacion
        for oferta in reporte.ofertas
    ] == [
        "BENEFICIOSO",
        "ACEPTABLE",
        "RECHAZABLE",
    ]


def test_generar_reporte_oferta_no_modifica_evaluacion_tecnica() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    primera = reporte.ofertas[0]

    assert primera.clasificacion == "BENEFICIOSO"
    assert primera.delta_score == 10
    assert primera.delta_hard == 0
    assert primera.delta_soft == -1
    assert primera.idx_a == 0
    assert primera.idx_b == 2
    assert primera.evaluacion["impacto"] == {
        "ATC_001": {"hard": 0, "soft": 0},
        "ATC_003": {"hard": 0, "soft": -1},
    }


def test_generar_reporte_oferta_incluye_metadata_visible() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    assert reporte.metadata == {
        "modo_exploracion": "OFERTA_RAPIDA",
        "candidatos_generados": 100,
        "candidatos_prefiltrados": 80,
        "candidatos_seleccionados": 50,
        "candidatos_evaluados": 50,
        "top_n": 50,
        "criterio_seleccion": "candidate_selection_v1",
        "priorizacion_historica_aplicada": True,
        "tiempos_por_etapa": {
            "candidate_generation_ms": 1.0,
            "technical_prefilter_ms": 2.0,
            "candidate_selection_ms": 3.0,
            "simulator_ms": 4.0,
            "technical_ranking_ms": 5.0,
            "historical_prioritization_ms": 6.0,
            "total_ms": 21.0,
        },
    }


def test_generar_reporte_oferta_no_expone_metadata_interna_no_visible() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado)

    assert "campo_interno_no_visible" not in reporte.metadata


def test_generar_reporte_oferta_respeta_limite() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado, limite=2)

    assert reporte.cantidad_ofertas == 2
    assert [oferta.posicion for oferta in reporte.ofertas] == [1, 2]
    assert [
        oferta.clasificacion
        for oferta in reporte.ofertas
    ] == [
        "BENEFICIOSO",
        "ACEPTABLE",
    ]


def test_generar_reporte_oferta_rechaza_limite_invalido() -> None:
    resultado = _crear_resultado_fake()

    with pytest.raises(ValueError, match="limite debe ser mayor que cero"):
        generar_reporte_oferta(resultado, limite=0)


def test_reporte_to_dict_devuelve_estructura_serializable() -> None:
    resultado = _crear_resultado_fake()

    reporte = generar_reporte_oferta(resultado, limite=1)

    data = reporte.to_dict()

    assert data["mensaje"] == MENSAJE_REPORTING_OFERTA_RAPIDA
    assert data["modo_exploracion"] == "OFERTA_RAPIDA"
    assert data["metadata"]["top_n"] == 50
    assert data["ofertas"] == [
        {
            "posicion": 1,
            "clasificacion": "BENEFICIOSO",
            "delta_score": 10.0,
            "delta_hard": 0,
            "delta_soft": -1,
            "idx_a": 0,
            "idx_b": 2,
            "evaluacion": {
                "idx_a": 0,
                "idx_b": 2,
                "clasificacion": "BENEFICIOSO",
                "delta_score": 10,
                "delta_hard": 0,
                "delta_soft": -1,
                "impacto": {
                    "ATC_001": {"hard": 0, "soft": 0},
                    "ATC_003": {"hard": 0, "soft": -1},
                },
            },
        }
    ]


def test_reporte_tolera_evaluaciones_incompletas() -> None:
    resultado = ExplorationFlowResult(
        modo_exploracion="OFERTA_RAPIDA",
        evaluaciones=[
            {},
        ],
        metadata={
            "modo_exploracion": "OFERTA_RAPIDA",
        },
    )

    reporte = generar_reporte_oferta(resultado)

    assert reporte.cantidad_ofertas == 1
    assert reporte.ofertas[0].clasificacion == "SIN_CLASIFICACION"
    assert reporte.ofertas[0].delta_score == 0
    assert reporte.ofertas[0].delta_hard == 0
    assert reporte.ofertas[0].delta_soft == 0
    assert reporte.ofertas[0].idx_a is None
    assert reporte.ofertas[0].idx_b is None