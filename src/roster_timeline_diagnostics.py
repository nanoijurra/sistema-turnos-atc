from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable

from src.roster_timeline_validator import validar_timeline_importada


@dataclass(frozen=True)
class ResumenDiagnosticoTimeline:
    total: int
    hard: int
    soft: int
    por_codigo: dict[str, int]
    por_severidad: dict[str, int]


@dataclass(frozen=True)
class DiagnosticoTimelineImportada:
    total_dias_importados: int
    total_violaciones: int
    total_hard: int
    total_soft: int
    valido_sin_hard: bool
    resumen: ResumenDiagnosticoTimeline
    violaciones: tuple[Any, ...]


def resumir_violaciones_timeline(
    violaciones: Iterable[Any],
) -> ResumenDiagnosticoTimeline:
    violaciones_normalizadas = tuple(violaciones)

    codigos = Counter(
        _obtener_valor_normalizado(
            violacion,
            nombres=("codigo", "code", "codigo_violacion", "rule_code"),
            valor_default="DESCONOCIDO",
        )
        for violacion in violaciones_normalizadas
    )

    severidades = Counter(
        _obtener_valor_normalizado(
            violacion,
            nombres=("severidad", "severity", "tipo", "nivel"),
            valor_default="DESCONOCIDA",
        )
        for violacion in violaciones_normalizadas
    )

    hard = severidades.get("HARD", 0)
    soft = severidades.get("SOFT", 0)

    return ResumenDiagnosticoTimeline(
        total=len(violaciones_normalizadas),
        hard=hard,
        soft=soft,
        por_codigo=dict(sorted(codigos.items())),
        por_severidad=dict(sorted(severidades.items())),
    )


def generar_diagnostico_timeline_importada(
    dias_importados: Iterable[Any],
) -> DiagnosticoTimelineImportada:
    dias = tuple(dias_importados)
    violaciones = tuple(validar_timeline_importada(dias))
    resumen = resumir_violaciones_timeline(violaciones)

    return DiagnosticoTimelineImportada(
        total_dias_importados=len(dias),
        total_violaciones=resumen.total,
        total_hard=resumen.hard,
        total_soft=resumen.soft,
        valido_sin_hard=resumen.hard == 0,
        resumen=resumen,
        violaciones=violaciones,
    )


def generar_diagnostico_desde_importacion(
    resultado_importacion: Any,
) -> DiagnosticoTimelineImportada:
    if not hasattr(resultado_importacion, "dias_importados"):
        raise ValueError(
            "El resultado de importacion no contiene dias_importados."
        )

    return generar_diagnostico_timeline_importada(
        resultado_importacion.dias_importados
    )


def _obtener_valor_normalizado(
    objeto: Any,
    *,
    nombres: tuple[str, ...],
    valor_default: str,
) -> str:
    valor = _obtener_valor(objeto, nombres=nombres, valor_default=valor_default)

    if hasattr(valor, "value"):
        valor = valor.value
    elif hasattr(valor, "name"):
        valor = valor.name

    return str(valor).upper()


def _obtener_valor(
    objeto: Any,
    *,
    nombres: tuple[str, ...],
    valor_default: str,
) -> Any:
    if isinstance(objeto, dict):
        for nombre in nombres:
            if nombre in objeto:
                return objeto[nombre]
        return valor_default

    for nombre in nombres:
        if hasattr(objeto, nombre):
            return getattr(objeto, nombre)

    return valor_default
