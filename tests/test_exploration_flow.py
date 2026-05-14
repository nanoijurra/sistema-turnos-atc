from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.exploration_flow import (
    DEFAULT_TOP_N_OFERTA_RAPIDA,
    explorar_candidatos_para_oferta,
    explorar_diagnostico_completo,
    explorar_oferta_rapida,
)


@dataclass(frozen=True)
class AsignacionFake:
    controlador: str
    fecha: str
    turno: str


def _crear_roster_fake() -> list[AsignacionFake]:
    return [
        AsignacionFake("ATC_001", "2026-03-01", "A"),
        AsignacionFake("ATC_002", "2026-03-02", "B"),
        AsignacionFake("ATC_003", "2026-03-03", "C"),
        AsignacionFake("ATC_004", "2026-03-04", "A"),
        AsignacionFake("ATC_005", "2026-03-05", "B"),
    ]


def _patch_flujo_base(monkeypatch: pytest.MonkeyPatch, modulo: Any) -> list[AsignacionFake]:
    asignaciones = _crear_roster_fake()
    candidatos_generados = asignaciones[1:]
    candidatos_prefiltrados = asignaciones[1:4]

    monkeypatch.setattr(
        modulo,
        "build_roster_index",
        lambda asignaciones: {"index": asignaciones},
    )

    monkeypatch.setattr(
        modulo,
        "generate_candidates",
        lambda asignacion_origen, roster_index, mode: candidatos_generados,
    )

    monkeypatch.setattr(
        modulo,
        "filter_technically_plausible_candidates",
        lambda asignacion_origen, candidatos, asignaciones, config_file: candidatos_prefiltrados,
    )

    def evaluar_swap_fake(
        asignaciones: list[AsignacionFake],
        idx_a: int,
        idx_b: int,
        config_file: str,
    ) -> dict[str, Any]:
        return {
            "idx_a": idx_a,
            "idx_b": idx_b,
            "clasificacion": "ACEPTABLE",
            "delta_score": idx_b,
            "delta_hard": 0,
            "delta_soft": 0,
        }

    monkeypatch.setattr(modulo, "evaluar_swap", evaluar_swap_fake)

    return asignaciones


def test_oferta_rapida_usa_candidate_selection_antes_de_simular(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)
    llamados_selection = []

    def seleccionar_fake(
        asignacion_origen: AsignacionFake,
        candidatos: list[AsignacionFake],
        asignaciones: list[AsignacionFake],
        top_n: int,
    ) -> list[AsignacionFake]:
        llamados_selection.append(
            {
                "candidatos_recibidos": len(candidatos),
                "top_n": top_n,
            }
        )
        return candidatos[:2]

    monkeypatch.setattr(modulo, "seleccionar_candidatos", seleccionar_fake)

    resultado = explorar_oferta_rapida(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        top_n=2,
    )

    assert resultado.modo_exploracion == "OFERTA_RAPIDA"
    assert resultado.cantidad_evaluaciones == 2
    assert llamados_selection == [
        {
            "candidatos_recibidos": 3,
            "top_n": 2,
        }
    ]

    assert resultado.metadata["candidatos_generados"] == 4
    assert resultado.metadata["candidatos_prefiltrados"] == 3
    assert resultado.metadata["candidatos_seleccionados"] == 2
    assert resultado.metadata["candidatos_evaluados"] == 2
    assert resultado.metadata["top_n"] == 2


def test_oferta_rapida_usa_top_n_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)
    top_n_recibido = []

    def seleccionar_fake(
        asignacion_origen: AsignacionFake,
        candidatos: list[AsignacionFake],
        asignaciones: list[AsignacionFake],
        top_n: int,
    ) -> list[AsignacionFake]:
        top_n_recibido.append(top_n)
        return candidatos

    monkeypatch.setattr(modulo, "seleccionar_candidatos", seleccionar_fake)

    resultado = explorar_oferta_rapida(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
    )

    assert top_n_recibido == [DEFAULT_TOP_N_OFERTA_RAPIDA]
    assert resultado.metadata["top_n"] == DEFAULT_TOP_N_OFERTA_RAPIDA


def test_diagnostico_completo_no_usa_candidate_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)

    def seleccionar_no_debe_llamarse(*args: Any, **kwargs: Any) -> list[Any]:
        raise AssertionError("DIAGNOSTICO_COMPLETO no debe usar candidate_selection")

    monkeypatch.setattr(modulo, "seleccionar_candidatos", seleccionar_no_debe_llamarse)

    resultado = explorar_diagnostico_completo(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
    )

    assert resultado.modo_exploracion == "DIAGNOSTICO_COMPLETO"
    assert resultado.cantidad_evaluaciones == 3
    assert resultado.metadata["candidatos_generados"] == 4
    assert resultado.metadata["candidatos_prefiltrados"] == 3
    assert resultado.metadata["candidatos_seleccionados"] == 3
    assert resultado.metadata["candidatos_evaluados"] == 3
    assert resultado.metadata["top_n"] is None
    assert resultado.metadata["criterio_seleccion"] is None


def test_flujo_operativo_default_es_oferta_rapida(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)

    monkeypatch.setattr(
        modulo,
        "seleccionar_candidatos",
        lambda asignacion_origen, candidatos, asignaciones, top_n: candidatos[:1],
    )

    resultado = explorar_candidatos_para_oferta(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
    )

    assert resultado.modo_exploracion == "OFERTA_RAPIDA"
    assert resultado.cantidad_evaluaciones == 1
    assert resultado.metadata["top_n"] == DEFAULT_TOP_N_OFERTA_RAPIDA


def test_flujo_operativo_permita_diagnostico_completo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)

    resultado = explorar_candidatos_para_oferta(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        modo_exploracion="DIAGNOSTICO_COMPLETO",
    )

    assert resultado.modo_exploracion == "DIAGNOSTICO_COMPLETO"
    assert resultado.cantidad_evaluaciones == 3


def test_flujo_operativo_rechaza_modo_no_soportado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)

    with pytest.raises(ValueError, match="Modo de exploracion no soportado"):
        explorar_candidatos_para_oferta(
            asignacion_origen=asignaciones[0],
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            modo_exploracion="EXHAUSTIVO",
        )


def test_oferta_rapida_rechaza_top_n_invalido() -> None:
    asignaciones = _crear_roster_fake()

    with pytest.raises(ValueError, match="top_n debe ser mayor que cero"):
        explorar_oferta_rapida(
            asignacion_origen=asignaciones[0],
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            top_n=0,
        )


def test_ranking_tecnico_ocurre_despues_de_simulator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.exploration_flow as modulo

    asignaciones = _patch_flujo_base(monkeypatch, modulo)

    monkeypatch.setattr(
        modulo,
        "seleccionar_candidatos",
        lambda asignacion_origen, candidatos, asignaciones, top_n: candidatos[:3],
    )

    def evaluar_swap_fake(
        asignaciones: list[AsignacionFake],
        idx_a: int,
        idx_b: int,
        config_file: str,
    ) -> dict[str, Any]:
        if idx_b == 1:
            return {
                "clasificacion": "RECHAZABLE",
                "delta_score": 100,
                "delta_hard": 1,
                "delta_soft": 0,
            }

        if idx_b == 2:
            return {
                "clasificacion": "BENEFICIOSO",
                "delta_score": 1,
                "delta_hard": 0,
                "delta_soft": 0,
            }

        return {
            "clasificacion": "ACEPTABLE",
            "delta_score": 50,
            "delta_hard": 0,
            "delta_soft": 0,
        }

    monkeypatch.setattr(modulo, "evaluar_swap", evaluar_swap_fake)

    resultado = explorar_oferta_rapida(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        top_n=3,
    )

    assert [
        evaluacion["clasificacion"]
        for evaluacion in resultado.evaluaciones
    ] == [
        "BENEFICIOSO",
        "ACEPTABLE",
        "RECHAZABLE",
    ]