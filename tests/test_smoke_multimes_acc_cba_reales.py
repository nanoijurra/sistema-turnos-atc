from __future__ import annotations

from pathlib import Path

import pytest

from src.roster_calendar_aware_multimonth import (
    EntradaCargaRosterMes,
    FORMATO_CSV_ACC_CBA,
    diagnosticar_carga_multimes_calendar_aware,
)


CSV_ACC_CBA_DIR = Path.home() / "Documents" / "ACC CBA"
CSV_JUNIO = CSV_ACC_CBA_DIR / "junio.csv"
CSV_JULIO = CSV_ACC_CBA_DIR / "julio.csv"
CSV_AGOSTO = CSV_ACC_CBA_DIR / "agosto.csv"


def test_smoke_diagnostico_multimes_acc_cba_reales_finales():
    faltantes = [
        path
        for path in (CSV_JUNIO, CSV_JULIO, CSV_AGOSTO)
        if not path.exists()
    ]
    if faltantes:
        pytest.skip(
            "CSV reales ACC CBA no disponibles: "
            + ", ".join(str(path) for path in faltantes)
        )

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(
                2026,
                6,
                CSV_JUNIO,
                formato=FORMATO_CSV_ACC_CBA,
            ),
            EntradaCargaRosterMes(
                2026,
                7,
                CSV_JULIO,
                formato=FORMATO_CSV_ACC_CBA,
            ),
            EntradaCargaRosterMes(
                2026,
                8,
                CSV_AGOSTO,
                formato=FORMATO_CSV_ACC_CBA,
            ),
        ],
        omitir_faltantes=False,
    )

    assert diagnostico.total_meses == 3
    assert diagnostico.meses_disponibles == 3
    assert diagnostico.meses_omitidos == 0
    assert diagnostico.meses_con_errors_importacion == 0
    assert diagnostico.meses_con_hard_calendar_aware == 0
    assert diagnostico.total_hard_calendar_aware == 0
    assert diagnostico.total_soft_calendar_aware == 17
    assert diagnostico.apto_para_revision_carga is True

    junio, julio, agosto = diagnostico.meses

    assert junio.mes == 6
    assert junio.total_controladores == 74
    assert junio.total_dias_importados == 2220
    assert junio.total_asignaciones_operativas == 909
    assert junio.total_eventos_no_operativos == 334
    assert junio.total_errors_importacion == 0
    assert junio.total_hard_calendar_aware == 0
    assert junio.total_soft_calendar_aware == 1

    assert julio.mes == 7
    assert julio.total_controladores == 74
    assert julio.total_dias_importados == 2294
    assert julio.total_asignaciones_operativas == 910
    assert julio.total_eventos_no_operativos == 442
    assert julio.total_errors_importacion == 0
    assert julio.total_hard_calendar_aware == 0
    assert julio.total_soft_calendar_aware == 11

    assert agosto.mes == 8
    assert agosto.total_controladores == 73
    assert agosto.total_dias_importados == 2263
    assert agosto.total_asignaciones_operativas == 930
    assert agosto.total_eventos_no_operativos == 339
    assert agosto.total_errors_importacion == 0
    assert agosto.total_hard_calendar_aware == 0
    assert agosto.total_soft_calendar_aware == 5
