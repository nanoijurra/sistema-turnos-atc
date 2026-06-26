from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from src.roster_calendar_aware_entrypoint import (
    diagnosticar_dias_importados_calendar_aware,
    diagnosticar_importacion_calendar_aware,
)
from src.roster_day_timeline import RosterDayStatus, RosterDiaImportado


def test_diagnosticar_dias_importados_calendar_aware_sin_violaciones():
    dias = [
        _dia_operativo("CONTROLADOR UNO", date(2026, 6, 1), "A"),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 2)),
        _dia_operativo("CONTROLADOR UNO", date(2026, 6, 3), "B"),
    ]

    resultado = diagnosticar_dias_importados_calendar_aware(dias)

    assert resultado.total_dias_importados == 3
    assert resultado.total_violaciones == 0
    assert resultado.total_hard == 0
    assert resultado.total_soft == 0
    assert resultado.valido_sin_hard is True
    assert resultado.por_codigo == {}
    assert resultado.por_severidad == {}
    assert resultado.violaciones == ()


def test_diagnosticar_dias_importados_calendar_aware_detecta_soft_libres():
    dias = [
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 1)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 2)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 3)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 4)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 5)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 6)),
    ]

    resultado = diagnosticar_dias_importados_calendar_aware(dias)

    assert resultado.total_dias_importados == 6
    assert resultado.total_violaciones == 1
    assert resultado.total_hard == 0
    assert resultado.total_soft == 1
    assert resultado.valido_sin_hard is True
    assert resultado.por_codigo == {
        "EXCESO_LIBRES_CONSECUTIVOS": 1,
    }
    assert resultado.por_severidad == {
        "SOFT": 1,
    }


def test_diagnosticar_importacion_calendar_aware_usa_dias_importados():
    resultado_importacion = SimpleNamespace(
        dias_importados=[
            _dia_operativo("CONTROLADOR UNO", date(2026, 6, 1), "A"),
            _dia_libre("CONTROLADOR UNO", date(2026, 6, 2)),
        ],
    )

    resultado = diagnosticar_importacion_calendar_aware(resultado_importacion)

    assert resultado.total_dias_importados == 2
    assert resultado.total_violaciones == 0
    assert resultado.total_hard == 0
    assert resultado.total_soft == 0
    assert resultado.valido_sin_hard is True


def test_diagnosticar_importacion_calendar_aware_falla_sin_dias_importados():
    with pytest.raises(ValueError, match="dias_importados"):
        diagnosticar_importacion_calendar_aware(SimpleNamespace())


def _dia_operativo(
    controlador: str,
    fecha: date,
    codigo: str,
) -> RosterDiaImportado:
    return RosterDiaImportado(
        controlador=controlador,
        fecha=fecha,
        estado=RosterDayStatus.OPERATIVO,
        raw_value=codigo,
        codigo=codigo,
        codigo_normalizado=codigo,
    )


def _dia_libre(
    controlador: str,
    fecha: date,
) -> RosterDiaImportado:
    return RosterDiaImportado(
        controlador=controlador,
        fecha=fecha,
        estado=RosterDayStatus.LIBRE,
        raw_value="",
        codigo=None,
        codigo_normalizado=None,
    )