from __future__ import annotations

from pathlib import Path

import pytest

from src.roster_import_service import importar_roster_desde_csv
from src.roster_timeline_diagnostics import (
    comparar_diagnostico_tradicional_vs_timeline,
    generar_diagnostico_desde_importacion,
)


CSV_REAL_LOCAL = Path("data/imports/csv_ok.csv")



def test_smoke_diagnostico_calendar_aware_sobre_csv_real_local():
    if not CSV_REAL_LOCAL.exists():
        pytest.skip(
            "CSV real local no disponible. "
            "Este smoke requiere data/imports/csv_ok.csv, "
            "archivo ignorado por Git."
        )

    resultado_importacion = importar_roster_desde_csv(
    CSV_REAL_LOCAL,
    anio=2026,
    mes=6,
    strict=True,
)

    diagnostico_timeline = generar_diagnostico_desde_importacion(
        resultado_importacion
    )

    resumen_tradicional_conocido = {
        "total": 32,
        "hard": 32,
        "soft": 0,
    }

    comparacion = comparar_diagnostico_tradicional_vs_timeline(
        resumen_tradicional=resumen_tradicional_conocido,
        diagnostico_timeline=diagnostico_timeline,
    )

    assert len(resultado_importacion.dias_importados) == 450
    assert len(resultado_importacion.asignaciones_operativas) == 213
    assert len(resultado_importacion.eventos_no_operativos) == 28

    assert diagnostico_timeline.total_dias_importados == 450
    assert diagnostico_timeline.total_violaciones == 1
    assert diagnostico_timeline.total_hard == 0
    assert diagnostico_timeline.total_soft == 1
    assert diagnostico_timeline.valido_sin_hard is True

    assert diagnostico_timeline.resumen.por_codigo == {
        "EXCESO_LIBRES_CONSECUTIVOS": 1,
    }

    assert comparacion.total_tradicional == 32
    assert comparacion.hard_tradicional == 32
    assert comparacion.soft_tradicional == 0

    assert comparacion.total_timeline == 1
    assert comparacion.hard_timeline == 0
    assert comparacion.soft_timeline == 1

    assert comparacion.diferencia_total == 31
    assert comparacion.diferencia_hard == 32
    assert comparacion.timeline_valido_sin_hard is True
    assert comparacion.requiere_revision_calendar_aware is True