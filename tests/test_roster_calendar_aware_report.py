from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from src.roster_calendar_aware_entrypoint import ResultadoDiagnosticoCalendarAware
from src.roster_calendar_aware_report import (
    ESTADO_INVALIDO_CON_HARD,
    ESTADO_VALIDO_SIN_HARD,
    MENSAJE_REPORTE_CALENDAR_AWARE,
    generar_reporte_operativo_calendar_aware,
    generar_reporte_operativo_importacion_calendar_aware,
)


@dataclass(frozen=True)
class ViolacionFake:
    codigo: str
    severidad: str
    mensaje: str
    metadata: dict


def test_generar_reporte_operativo_calendar_aware_sin_hard():
    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=450,
        total_violaciones=1,
        total_hard=0,
        total_soft=1,
        valido_sin_hard=True,
        por_codigo={
            "EXCESO_LIBRES_CONSECUTIVOS": 1,
        },
        por_severidad={
            "SOFT": 1,
        },
        violaciones=(
            ViolacionFake(
                codigo="EXCESO_LIBRES_CONSECUTIVOS",
                severidad="soft",
                mensaje="Mas de 5 dias libres consecutivos.",
                metadata={
                    "controlador": "CONTROLADOR UNO",
                    "cantidad_dias": 6,
                },
            ),
        ),
    )

    reporte = generar_reporte_operativo_calendar_aware(resultado)

    assert reporte.mensaje == MENSAJE_REPORTE_CALENDAR_AWARE
    assert reporte.estado_general == ESTADO_VALIDO_SIN_HARD
    assert reporte.total_dias_importados == 450
    assert reporte.total_violaciones == 1
    assert reporte.total_hard == 0
    assert reporte.total_soft == 1
    assert reporte.valido_sin_hard is True
    assert reporte.codigos_principales[0].codigo == "EXCESO_LIBRES_CONSECUTIVOS"
    assert reporte.codigos_principales[0].cantidad == 1
    assert reporte.detalles[0].severidad == "SOFT"
    assert reporte.detalles[0].metadata["cantidad_dias"] == 6
    assert reporte.metadata == {
        "fuente": "calendar-aware",
        "tipo": "diagnostico",
        "limite_detalles": None,
        "total_detalles_disponibles": 1,
    }


def test_generar_reporte_operativo_calendar_aware_con_hard():
    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=6,
        total_violaciones=1,
        total_hard=1,
        total_soft=0,
        valido_sin_hard=False,
        por_codigo={
            "EXCESO_AB_CONSECUTIVOS": 1,
        },
        por_severidad={
            "HARD": 1,
        },
        violaciones=(
            {
                "codigo": "EXCESO_AB_CONSECUTIVOS",
                "severidad": "hard",
                "mensaje": "Exceso de dias consecutivos A/B.",
                "metadata": {
                    "cantidad_dias": 6,
                },
            },
        ),
    )

    reporte = generar_reporte_operativo_calendar_aware(resultado)

    assert reporte.estado_general == ESTADO_INVALIDO_CON_HARD
    assert reporte.total_hard == 1
    assert reporte.detalles[0].codigo == "EXCESO_AB_CONSECUTIVOS"
    assert reporte.detalles[0].severidad == "HARD"


def test_reporte_ordena_codigos_por_cantidad_y_codigo():
    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=10,
        total_violaciones=4,
        total_hard=2,
        total_soft=2,
        valido_sin_hard=False,
        por_codigo={
            "CODIGO_B": 1,
            "CODIGO_A": 2,
            "CODIGO_C": 1,
        },
        por_severidad={
            "HARD": 2,
            "SOFT": 2,
        },
        violaciones=(),
    )

    reporte = generar_reporte_operativo_calendar_aware(resultado)

    assert [codigo.codigo for codigo in reporte.codigos_principales] == [
        "CODIGO_A",
        "CODIGO_B",
        "CODIGO_C",
    ]


def test_reporte_limita_detalles():
    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=10,
        total_violaciones=2,
        total_hard=0,
        total_soft=2,
        valido_sin_hard=True,
        por_codigo={
            "CODIGO_A": 2,
        },
        por_severidad={
            "SOFT": 2,
        },
        violaciones=(
            ViolacionFake("CODIGO_A", "soft", "Detalle 1", {}),
            ViolacionFake("CODIGO_A", "soft", "Detalle 2", {}),
        ),
    )

    reporte = generar_reporte_operativo_calendar_aware(
        resultado,
        limite_detalles=1,
    )

    assert len(reporte.detalles) == 1
    assert reporte.detalles[0].mensaje == "Detalle 1"
    assert reporte.metadata["limite_detalles"] == 1
    assert reporte.metadata["total_detalles_disponibles"] == 2


def test_reporte_rechaza_limite_detalles_invalido():
    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=0,
        total_violaciones=0,
        total_hard=0,
        total_soft=0,
        valido_sin_hard=True,
        por_codigo={},
        por_severidad={},
        violaciones=(),
    )

    with pytest.raises(ValueError, match="limite_detalles"):
        generar_reporte_operativo_calendar_aware(
            resultado,
            limite_detalles=0,
        )


def test_reporte_to_dict_devuelve_estructura_presentable():
    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=1,
        total_violaciones=0,
        total_hard=0,
        total_soft=0,
        valido_sin_hard=True,
        por_codigo={},
        por_severidad={},
        violaciones=(),
    )

    reporte = generar_reporte_operativo_calendar_aware(resultado)

    assert reporte.to_dict() == {
        "mensaje": MENSAJE_REPORTE_CALENDAR_AWARE,
        "estado_general": ESTADO_VALIDO_SIN_HARD,
        "total_dias_importados": 1,
        "total_violaciones": 0,
        "total_hard": 0,
        "total_soft": 0,
        "valido_sin_hard": True,
        "codigos_principales": [],
        "detalles": [],
        "metadata": {
            "fuente": "calendar-aware",
            "tipo": "diagnostico",
            "limite_detalles": None,
            "total_detalles_disponibles": 0,
        },
    }


def test_generar_reporte_operativo_importacion_calendar_aware_usa_entrypoint(
    monkeypatch,
):
    import src.roster_calendar_aware_report as modulo

    resultado = ResultadoDiagnosticoCalendarAware(
        total_dias_importados=1,
        total_violaciones=0,
        total_hard=0,
        total_soft=0,
        valido_sin_hard=True,
        por_codigo={},
        por_severidad={},
        violaciones=(),
    )
    llamadas = []

    def diagnosticar_fake(resultado_importacion):
        llamadas.append(resultado_importacion)
        return resultado

    monkeypatch.setattr(
        modulo,
        "diagnosticar_importacion_calendar_aware",
        diagnosticar_fake,
    )

    resultado_importacion = SimpleNamespace(dias_importados=[])

    reporte = generar_reporte_operativo_importacion_calendar_aware(
        resultado_importacion
    )

    assert llamadas == [resultado_importacion]
    assert reporte.total_dias_importados == 1
    assert reporte.estado_general == ESTADO_VALIDO_SIN_HARD
