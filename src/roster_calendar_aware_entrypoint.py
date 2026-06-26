from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from src.roster_timeline_diagnostics import (
    DiagnosticoTimelineImportada,
    generar_diagnostico_desde_importacion,
    generar_diagnostico_timeline_importada,
)


@dataclass(frozen=True)
class ResultadoDiagnosticoCalendarAware:
    total_dias_importados: int
    total_violaciones: int
    total_hard: int
    total_soft: int
    valido_sin_hard: bool
    por_codigo: dict[str, int]
    por_severidad: dict[str, int]
    violaciones: tuple[Any, ...]


def diagnosticar_dias_importados_calendar_aware(
    dias_importados: Iterable[Any],
) -> ResultadoDiagnosticoCalendarAware:
    diagnostico = generar_diagnostico_timeline_importada(dias_importados)

    return _crear_resultado_calendar_aware(diagnostico)


def diagnosticar_importacion_calendar_aware(
    resultado_importacion: Any,
) -> ResultadoDiagnosticoCalendarAware:
    diagnostico = generar_diagnostico_desde_importacion(resultado_importacion)

    return _crear_resultado_calendar_aware(diagnostico)


def _crear_resultado_calendar_aware(
    diagnostico: DiagnosticoTimelineImportada,
) -> ResultadoDiagnosticoCalendarAware:
    return ResultadoDiagnosticoCalendarAware(
        total_dias_importados=diagnostico.total_dias_importados,
        total_violaciones=diagnostico.total_violaciones,
        total_hard=diagnostico.total_hard,
        total_soft=diagnostico.total_soft,
        valido_sin_hard=diagnostico.valido_sin_hard,
        por_codigo=diagnostico.resumen.por_codigo,
        por_severidad=diagnostico.resumen.por_severidad,
        violaciones=diagnostico.violaciones,
    )