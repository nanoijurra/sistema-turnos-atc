from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.roster_calendar_aware_entrypoint import (
    ResultadoDiagnosticoCalendarAware,
    diagnosticar_importacion_calendar_aware,
)


MENSAJE_REPORTE_CALENDAR_AWARE = "Reporte operativo calendar-aware"
ESTADO_VALIDO_SIN_HARD = "VALIDO_SIN_HARD"
ESTADO_INVALIDO_CON_HARD = "INVALIDO_CON_HARD"


@dataclass(frozen=True)
class ResumenCodigoCalendarAware:
    codigo: str
    cantidad: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "cantidad": self.cantidad,
        }


@dataclass(frozen=True)
class DetalleViolacionCalendarAware:
    codigo: str
    severidad: str
    mensaje: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "severidad": self.severidad,
            "mensaje": self.mensaje,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ReporteOperativoCalendarAware:
    mensaje: str
    estado_general: str
    total_dias_importados: int
    total_violaciones: int
    total_hard: int
    total_soft: int
    valido_sin_hard: bool
    codigos_principales: tuple[ResumenCodigoCalendarAware, ...]
    detalles: tuple[DetalleViolacionCalendarAware, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mensaje": self.mensaje,
            "estado_general": self.estado_general,
            "total_dias_importados": self.total_dias_importados,
            "total_violaciones": self.total_violaciones,
            "total_hard": self.total_hard,
            "total_soft": self.total_soft,
            "valido_sin_hard": self.valido_sin_hard,
            "codigos_principales": [
                codigo.to_dict()
                for codigo in self.codigos_principales
            ],
            "detalles": [
                detalle.to_dict()
                for detalle in self.detalles
            ],
            "metadata": dict(self.metadata),
        }


def generar_reporte_operativo_calendar_aware(
    resultado: ResultadoDiagnosticoCalendarAware,
    *,
    limite_detalles: int | None = None,
) -> ReporteOperativoCalendarAware:
    if limite_detalles is not None and limite_detalles <= 0:
        raise ValueError("limite_detalles debe ser mayor que cero.")

    detalles = tuple(
        _crear_detalle_violacion(violacion)
        for violacion in resultado.violaciones
    )

    if limite_detalles is not None:
        detalles = detalles[:limite_detalles]

    return ReporteOperativoCalendarAware(
        mensaje=MENSAJE_REPORTE_CALENDAR_AWARE,
        estado_general=_estado_general(resultado),
        total_dias_importados=resultado.total_dias_importados,
        total_violaciones=resultado.total_violaciones,
        total_hard=resultado.total_hard,
        total_soft=resultado.total_soft,
        valido_sin_hard=resultado.valido_sin_hard,
        codigos_principales=_ordenar_codigos(resultado.por_codigo),
        detalles=detalles,
        metadata={
            "fuente": "calendar-aware",
            "tipo": "diagnostico",
            "limite_detalles": limite_detalles,
            "total_detalles_disponibles": len(resultado.violaciones),
        },
    )


def generar_reporte_operativo_importacion_calendar_aware(
    resultado_importacion: Any,
    *,
    limite_detalles: int | None = None,
) -> ReporteOperativoCalendarAware:
    resultado = diagnosticar_importacion_calendar_aware(resultado_importacion)

    return generar_reporte_operativo_calendar_aware(
        resultado,
        limite_detalles=limite_detalles,
    )


def _estado_general(resultado: ResultadoDiagnosticoCalendarAware) -> str:
    if resultado.valido_sin_hard:
        return ESTADO_VALIDO_SIN_HARD

    return ESTADO_INVALIDO_CON_HARD


def _ordenar_codigos(
    por_codigo: dict[str, int],
) -> tuple[ResumenCodigoCalendarAware, ...]:
    return tuple(
        ResumenCodigoCalendarAware(codigo=codigo, cantidad=cantidad)
        for codigo, cantidad in sorted(
            por_codigo.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )


def _crear_detalle_violacion(
    violacion: Any,
) -> DetalleViolacionCalendarAware:
    return DetalleViolacionCalendarAware(
        codigo=str(_obtener_valor(violacion, "codigo", "DESCONOCIDO")),
        severidad=str(_obtener_valor(violacion, "severidad", "DESCONOCIDA")).upper(),
        mensaje=str(_obtener_valor(violacion, "mensaje", "")),
        metadata=dict(_obtener_valor(violacion, "metadata", {})),
    )


def _obtener_valor(objeto: Any, nombre: str, valor_default: Any) -> Any:
    if isinstance(objeto, dict):
        return objeto.get(nombre, valor_default)

    return getattr(objeto, nombre, valor_default)
