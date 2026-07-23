from __future__ import annotations

from pathlib import Path

import pytest

from src.roster_calendar_aware_multimonth import (
    EntradaCargaRosterMes,
    diagnosticar_carga_multimes_calendar_aware,
)
from src.roster_calendar_aware_report import (
    ESTADO_INVALIDO_CON_HARD,
    ESTADO_VALIDO_SIN_HARD,
)
from src.roster_store import limpiar_rosters, obtener_roster_vigente


def test_diagnosticar_carga_multimes_calendar_aware_resume_meses(tmp_path):
    junio = _crear_csv(
        tmp_path / "junio.csv",
        [
            ["controlador", "01", "02", "03"],
            ["CONTROLADOR A", "A", "", "B"],
        ],
    )
    julio = _crear_csv(
        tmp_path / "julio.csv",
        [
            ["controlador", "01", "02", "03", "04", "05", "06"],
            ["CONTROLADOR B", "", "", "", "", "", ""],
        ],
    )

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(2026, 6, junio),
            EntradaCargaRosterMes(2026, 7, julio),
        ],
    )

    assert diagnostico.total_meses == 2
    assert diagnostico.meses_disponibles == 2
    assert diagnostico.meses_omitidos == 0
    assert diagnostico.meses_con_errors_importacion == 0
    assert diagnostico.meses_con_hard_calendar_aware == 0
    assert diagnostico.total_hard_calendar_aware == 0
    assert diagnostico.total_soft_calendar_aware == 1
    assert diagnostico.apto_para_revision_carga is True

    mes_junio, mes_julio = diagnostico.meses

    assert mes_junio.mes == 6
    assert mes_junio.estado_general_calendar_aware == ESTADO_VALIDO_SIN_HARD
    assert mes_junio.total_dias_importados == 3
    assert mes_junio.total_asignaciones_operativas == 2

    assert mes_julio.mes == 7
    assert mes_julio.estado_general_calendar_aware == ESTADO_VALIDO_SIN_HARD
    assert mes_julio.total_soft_calendar_aware == 1
    assert mes_julio.por_codigo_calendar_aware == {
        "EXCESO_LIBRES_CONSECUTIVOS": 1,
    }
    assert mes_julio.apto_para_revision_carga is True


def test_diagnosticar_carga_multimes_calendar_aware_omite_faltantes(tmp_path):
    junio = _crear_csv(
        tmp_path / "junio.csv",
        [
            ["controlador", "01"],
            ["CONTROLADOR A", "A"],
        ],
    )
    faltante = tmp_path / "julio.csv"

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(2026, 6, junio),
            EntradaCargaRosterMes(2026, 7, faltante),
        ],
    )

    assert diagnostico.total_meses == 2
    assert diagnostico.meses_disponibles == 1
    assert diagnostico.meses_omitidos == 1
    assert diagnostico.apto_para_revision_carga is False

    mes_faltante = diagnostico.meses[1]

    assert mes_faltante.disponible is False
    assert mes_faltante.omitido_motivo == "CSV_NO_DISPONIBLE"
    assert mes_faltante.reporte is None


def test_diagnosticar_carga_multimes_calendar_aware_falla_si_faltante_requerido(
    tmp_path,
):
    with pytest.raises(FileNotFoundError):
        diagnosticar_carga_multimes_calendar_aware(
            [
                EntradaCargaRosterMes(2026, 7, tmp_path / "julio.csv"),
            ],
            omitir_faltantes=False,
        )


def test_diagnosticar_carga_multimes_calendar_aware_detecta_error_importacion(
    tmp_path,
):
    junio = _crear_csv(
        tmp_path / "junio.csv",
        [
            ["controlador", "01"],
            ["CONTROLADOR A", "XYZ"],
        ],
    )

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(2026, 6, junio),
        ],
        strict=True,
    )

    mes = diagnostico.meses[0]

    assert diagnostico.meses_con_errors_importacion == 1
    assert diagnostico.apto_para_revision_carga is False
    assert mes.total_errors_importacion == 1
    assert mes.puede_crear_roster_version is False


def test_diagnosticar_carga_multimes_calendar_aware_detecta_hard_calendar_aware(
    tmp_path,
):
    junio = _crear_csv(
        tmp_path / "junio.csv",
        [
            ["controlador", "01", "02", "03", "04", "05", "06"],
            ["CONTROLADOR A", "C", "C", "C", "C", "", ""],
        ],
    )

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(2026, 6, junio),
        ],
    )

    mes = diagnostico.meses[0]

    assert diagnostico.meses_con_hard_calendar_aware == 1
    assert diagnostico.total_hard_calendar_aware == 1
    assert diagnostico.apto_para_revision_carga is False
    assert mes.estado_general_calendar_aware == ESTADO_INVALIDO_CON_HARD
    assert mes.por_codigo_calendar_aware == {
        "EXCESO_C_CONSECUTIVOS": 1,
    }


def test_diagnostico_multimes_no_persiste_roster_version(tmp_path):
    limpiar_rosters()
    junio = _crear_csv(
        tmp_path / "junio.csv",
        [
            ["controlador", "01"],
            ["CONTROLADOR A", "A"],
        ],
    )

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(2026, 6, junio),
        ],
    )

    assert diagnostico.meses[0].apto_para_revision_carga is True
    assert obtener_roster_vigente() is None


def test_diagnostico_multimes_to_dict(tmp_path):
    junio = _crear_csv(
        tmp_path / "junio.csv",
        [
            ["controlador", "01"],
            ["CONTROLADOR A", "A"],
        ],
    )

    diagnostico = diagnosticar_carga_multimes_calendar_aware(
        [
            EntradaCargaRosterMes(2026, 6, junio),
        ],
    )

    data = diagnostico.to_dict()

    assert data["total_meses"] == 1
    assert data["meses_disponibles"] == 1
    assert data["apto_para_revision_carga"] is True
    assert data["meses"][0]["anio"] == 2026
    assert data["meses"][0]["mes"] == 6
    assert data["meses"][0]["reporte"]["estado_general"] == ESTADO_VALIDO_SIN_HARD


def _crear_csv(path: Path, filas: list[list[str]]) -> Path:
    contenido = "\n".join(
        ",".join(fila)
        for fila in filas
    )
    path.write_text(contenido, encoding="utf-8")
    return path
