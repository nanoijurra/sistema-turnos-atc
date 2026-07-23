from __future__ import annotations

from pathlib import Path

import pytest

from src.roster_calendar_aware_multimonth import importar_roster_acc_cba_desde_csv
from src.simulator import evaluar_swap


CSV_ACC_CBA_DIR = Path.home() / "Documents" / "ACC CBA"
CSV_JUNIO = CSV_ACC_CBA_DIR / "junio.csv"


def test_smoke_swap_simulado_sobre_junio_acc_cba_real_no_aplica_cambios():
    if not CSV_JUNIO.exists():
        pytest.skip(
            "CSV real ACC CBA junio no disponible: "
            f"{CSV_JUNIO}"
        )

    resultado_importacion = importar_roster_acc_cba_desde_csv(
        CSV_JUNIO,
        anio=2026,
        mes=6,
        strict=True,
    )
    asignaciones = resultado_importacion.asignaciones_operativas
    idx_a, idx_b = _buscar_par_swap_simulado(asignaciones)

    asignacion_a_original = asignaciones[idx_a]
    asignacion_b_original = asignaciones[idx_b]

    evaluacion = evaluar_swap(
        asignaciones=asignaciones,
        idx_a=idx_a,
        idx_b=idx_b,
    )

    roster_simulado = evaluacion["resultado_swap"]["roster"]

    assert len(resultado_importacion.errors) == 0
    assert len(asignaciones) == 909

    assert evaluacion["swap"] == {
        "idx_a": idx_a,
        "idx_b": idx_b,
    }
    assert evaluacion["clasificacion"] in {
        "BENEFICIOSO",
        "ACEPTABLE",
        "RECHAZABLE",
    }
    assert "decision_sugerida" not in evaluacion

    assert roster_simulado is not asignaciones
    assert roster_simulado[idx_a].turno == asignacion_b_original.turno
    assert roster_simulado[idx_b].turno == asignacion_a_original.turno

    assert asignaciones[idx_a] == asignacion_a_original
    assert asignaciones[idx_b] == asignacion_b_original


def _buscar_par_swap_simulado(asignaciones: list) -> tuple[int, int]:
    for idx_a, asignacion_a in enumerate(asignaciones):
        for idx_b in range(idx_a + 1, len(asignaciones)):
            asignacion_b = asignaciones[idx_b]

            if asignacion_a.controlador is None or asignacion_b.controlador is None:
                continue

            if asignacion_a.controlador.nombre == asignacion_b.controlador.nombre:
                continue

            if asignacion_a.turno.codigo == asignacion_b.turno.codigo:
                continue

            return idx_a, idx_b

    raise AssertionError("No se encontro un par de asignaciones apto para smoke.")
