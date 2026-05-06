from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModoExploracion(str, Enum):
    OFERTA_RAPIDA = "OFERTA_RAPIDA"
    DIAGNOSTICO_COMPLETO = "DIAGNOSTICO_COMPLETO"
    EXHAUSTIVO = "EXHAUSTIVO"


CRITERIO_SELECCION_CANDIDATE_SELECTION_V1 = (
    "candidate_selection_v1: misma_fecha, distancia_temporal, "
    "turno_distinto, controlador, fecha, turno"
)


MENSAJE_REPORTING_OFERTA_RAPIDA = (
    "Mostrando mejores candidatos evaluados segun filtros actuales."
)


@dataclass(frozen=True)
class ExplorationMetadata:
    modo_exploracion: str
    candidatos_generados: int
    candidatos_prefiltrados: int
    candidatos_seleccionados: int
    candidatos_evaluados: int
    top_n: int | None
    criterio_seleccion: str | None
    tiempos_por_etapa: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "modo_exploracion": self.modo_exploracion,
            "candidatos_generados": self.candidatos_generados,
            "candidatos_prefiltrados": self.candidatos_prefiltrados,
            "candidatos_seleccionados": self.candidatos_seleccionados,
            "candidatos_evaluados": self.candidatos_evaluados,
            "top_n": self.top_n,
            "criterio_seleccion": self.criterio_seleccion,
            "tiempos_por_etapa": dict(self.tiempos_por_etapa),
        }


def construir_metadata_oferta_rapida(
    *,
    candidatos_generados: int,
    candidatos_prefiltrados: int,
    candidatos_seleccionados: int,
    candidatos_evaluados: int,
    top_n: int = 50,
    tiempos_por_etapa: dict[str, float] | None = None,
) -> ExplorationMetadata:
    return ExplorationMetadata(
        modo_exploracion=ModoExploracion.OFERTA_RAPIDA.value,
        candidatos_generados=candidatos_generados,
        candidatos_prefiltrados=candidatos_prefiltrados,
        candidatos_seleccionados=candidatos_seleccionados,
        candidatos_evaluados=candidatos_evaluados,
        top_n=top_n,
        criterio_seleccion=CRITERIO_SELECCION_CANDIDATE_SELECTION_V1,
        tiempos_por_etapa=tiempos_por_etapa or {},
    )


def construir_metadata_diagnostico_completo(
    *,
    candidatos_generados: int,
    candidatos_prefiltrados: int,
    candidatos_evaluados: int,
    tiempos_por_etapa: dict[str, float] | None = None,
) -> ExplorationMetadata:
    return ExplorationMetadata(
        modo_exploracion=ModoExploracion.DIAGNOSTICO_COMPLETO.value,
        candidatos_generados=candidatos_generados,
        candidatos_prefiltrados=candidatos_prefiltrados,
        candidatos_seleccionados=candidatos_prefiltrados,
        candidatos_evaluados=candidatos_evaluados,
        top_n=None,
        criterio_seleccion=None,
        tiempos_por_etapa=tiempos_por_etapa or {},
    )


def construir_metadata_exhaustivo(
    *,
    candidatos_generados: int,
    candidatos_evaluados: int,
    tiempos_por_etapa: dict[str, float] | None = None,
) -> ExplorationMetadata:
    return ExplorationMetadata(
        modo_exploracion=ModoExploracion.EXHAUSTIVO.value,
        candidatos_generados=candidatos_generados,
        candidatos_prefiltrados=candidatos_generados,
        candidatos_seleccionados=candidatos_generados,
        candidatos_evaluados=candidatos_evaluados,
        top_n=None,
        criterio_seleccion=None,
        tiempos_por_etapa=tiempos_por_etapa or {},
    )