from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

import pytest

from src.roster_day_timeline import RosterDayStatus, RosterDiaImportado
from src.roster_timeline_diagnostics import (
    comparar_diagnostico_tradicional_vs_timeline,
    generar_diagnostico_desde_importacion,
    generar_diagnostico_timeline_importada,
    resumir_violaciones_timeline,
)


@dataclass(frozen=True)
class ViolacionFake:
    codigo: str
    severidad: str


def test_resumir_violaciones_timeline_sin_violaciones():
    resumen = resumir_violaciones_timeline([])

    assert resumen.total == 0
    assert resumen.hard == 0
    assert resumen.soft == 0
    assert resumen.por_codigo == {}
    assert resumen.por_severidad == {}


def test_resumir_violaciones_timeline_cuenta_por_codigo_y_severidad():
    violaciones = [
        ViolacionFake(
            codigo="EXCESO_AB_CONSECUTIVOS",
            severidad="hard",
        ),
        ViolacionFake(
            codigo="EXCESO_LIBRES_CONSECUTIVOS",
            severidad="soft",
        ),
        ViolacionFake(
            codigo="EXCESO_LIBRES_CONSECUTIVOS",
            severidad="soft",
        ),
    ]

    resumen = resumir_violaciones_timeline(violaciones)

    assert resumen.total == 3
    assert resumen.hard == 1
    assert resumen.soft == 2
    assert resumen.por_codigo == {
        "EXCESO_AB_CONSECUTIVOS": 1,
        "EXCESO_LIBRES_CONSECUTIVOS": 2,
    }
    assert resumen.por_severidad == {
        "HARD": 1,
        "SOFT": 2,
    }


def test_generar_diagnostico_timeline_importada_sin_violaciones():
    dias = [
        _dia_operativo("CONTROLADOR UNO", date(2026, 6, 1), "A"),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 2)),
        _dia_operativo("CONTROLADOR UNO", date(2026, 6, 3), "B"),
    ]

    diagnostico = generar_diagnostico_timeline_importada(dias)

    assert diagnostico.total_dias_importados == 3
    assert diagnostico.total_violaciones == 0
    assert diagnostico.total_hard == 0
    assert diagnostico.total_soft == 0
    assert diagnostico.valido_sin_hard is True
    assert diagnostico.violaciones == ()


def test_generar_diagnostico_timeline_importada_detecta_soft_libres():
    dias = [
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 1)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 2)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 3)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 4)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 5)),
        _dia_libre("CONTROLADOR UNO", date(2026, 6, 6)),
    ]

    diagnostico = generar_diagnostico_timeline_importada(dias)

    assert diagnostico.total_dias_importados == 6
    assert diagnostico.total_violaciones == 1
    assert diagnostico.total_hard == 0
    assert diagnostico.total_soft == 1
    assert diagnostico.valido_sin_hard is True
    assert diagnostico.resumen.por_codigo == {
        "EXCESO_LIBRES_CONSECUTIVOS": 1,
    }


def test_generar_diagnostico_desde_importacion_usa_dias_importados():
    resultado_importacion = SimpleNamespace(
        dias_importados=[
            _dia_operativo("CONTROLADOR UNO", date(2026, 6, 1), "A"),
            _dia_libre("CONTROLADOR UNO", date(2026, 6, 2)),
        ],
    )

    diagnostico = generar_diagnostico_desde_importacion(resultado_importacion)

    assert diagnostico.total_dias_importados == 2
    assert diagnostico.total_violaciones == 0
    assert diagnostico.valido_sin_hard is True


def test_generar_diagnostico_desde_importacion_falla_sin_dias_importados():
    with pytest.raises(ValueError, match="dias_importados"):
        generar_diagnostico_desde_importacion(SimpleNamespace())

def test_comparar_diagnostico_tradicional_vs_timeline_detecta_diferencia_hard():
    resumen_tradicional = {
        "total": 32,
        "hard": 32,
        "soft": 0,
    }
    diagnostico_timeline = SimpleNamespace(
        total_violaciones=1,
        total_hard=0,
        total_soft=1,
        valido_sin_hard=True,
    )

    comparacion = comparar_diagnostico_tradicional_vs_timeline(
        resumen_tradicional=resumen_tradicional,
        diagnostico_timeline=diagnostico_timeline,
    )

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


def test_comparar_diagnostico_tradicional_vs_timeline_sin_diferencia_hard():
    resumen_tradicional = SimpleNamespace(
        total=1,
        hard=0,
        soft=1,
    )
    diagnostico_timeline = SimpleNamespace(
        total_violaciones=1,
        total_hard=0,
        total_soft=1,
        valido_sin_hard=True,
    )

    comparacion = comparar_diagnostico_tradicional_vs_timeline(
        resumen_tradicional=resumen_tradicional,
        diagnostico_timeline=diagnostico_timeline,
    )

    assert comparacion.total_tradicional == 1
    assert comparacion.hard_tradicional == 0
    assert comparacion.soft_tradicional == 1
    assert comparacion.total_timeline == 1
    assert comparacion.hard_timeline == 0
    assert comparacion.soft_timeline == 1
    assert comparacion.diferencia_total == 0
    assert comparacion.diferencia_hard == 0
    assert comparacion.timeline_valido_sin_hard is True
    assert comparacion.requiere_revision_calendar_aware is False

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
