from __future__ import annotations

from pathlib import Path

import pytest

from src.roster_calendar_aware_entrypoint import (
    diagnosticar_importacion_calendar_aware,
)
from src.roster_import_service import importar_roster_desde_csv


CSV_REAL_LOCAL = Path("data/imports/csv_ok.csv")


def test_smoke_entrypoint_calendar_aware_sobre_csv_real_local():
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

    resultado_calendar_aware = diagnosticar_importacion_calendar_aware(
        resultado_importacion
    )

    assert resultado_calendar_aware.total_dias_importados == 450
    assert resultado_calendar_aware.total_violaciones == 1
    assert resultado_calendar_aware.total_hard == 0
    assert resultado_calendar_aware.total_soft == 1
    assert resultado_calendar_aware.valido_sin_hard is True

    assert resultado_calendar_aware.por_codigo == {
        "EXCESO_LIBRES_CONSECUTIVOS": 1,
    }

    assert resultado_calendar_aware.por_severidad == {
        "SOFT": 1,
    }

    assert len(resultado_calendar_aware.violaciones) == 1