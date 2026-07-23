from __future__ import annotations

from pathlib import Path

import pytest

from src.roster_calendar_aware_report import (
    ESTADO_VALIDO_SIN_HARD,
    MENSAJE_REPORTE_CALENDAR_AWARE,
    generar_reporte_operativo_importacion_calendar_aware,
)
from src.roster_import_service import importar_roster_desde_csv


CSV_REAL_LOCAL = Path("data/imports/csv_ok.csv")


def test_smoke_reporte_operativo_calendar_aware_sobre_csv_real_local():
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

    reporte = generar_reporte_operativo_importacion_calendar_aware(
        resultado_importacion
    )

    assert reporte.mensaje == MENSAJE_REPORTE_CALENDAR_AWARE
    assert reporte.estado_general == ESTADO_VALIDO_SIN_HARD
    assert reporte.total_dias_importados == 450
    assert reporte.total_violaciones == 1
    assert reporte.total_hard == 0
    assert reporte.total_soft == 1
    assert reporte.valido_sin_hard is True

    assert [codigo.to_dict() for codigo in reporte.codigos_principales] == [
        {
            "codigo": "EXCESO_LIBRES_CONSECUTIVOS",
            "cantidad": 1,
        }
    ]

    assert len(reporte.detalles) == 1
    assert reporte.detalles[0].codigo == "EXCESO_LIBRES_CONSECUTIVOS"
    assert reporte.detalles[0].severidad == "SOFT"
    assert reporte.detalles[0].metadata["cantidad_dias"] == 6

    assert reporte.to_dict()["estado_general"] == ESTADO_VALIDO_SIN_HARD
    assert reporte.to_dict()["metadata"] == {
        "fuente": "calendar-aware",
        "tipo": "diagnostico",
        "limite_detalles": None,
        "total_detalles_disponibles": 1,
    }
