from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.exploration_flow import ExplorationFlowResult
from src.exploration_modes import MENSAJE_REPORTING_OFERTA_RAPIDA


@dataclass(frozen=True)
class OfertaEvaluada:
    posicion: int
    clasificacion: str
    delta_score: float
    delta_hard: int
    delta_soft: int
    idx_a: int | None
    idx_b: int | None
    evaluacion: dict[str, Any]


@dataclass(frozen=True)
class OfferReport:
    mensaje: str
    modo_exploracion: str
    ofertas: list[OfertaEvaluada]
    metadata: dict[str, Any]

    @property
    def cantidad_ofertas(self) -> int:
        return len(self.ofertas)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mensaje": self.mensaje,
            "modo_exploracion": self.modo_exploracion,
            "ofertas": [
                {
                    "posicion": oferta.posicion,
                    "clasificacion": oferta.clasificacion,
                    "delta_score": oferta.delta_score,
                    "delta_hard": oferta.delta_hard,
                    "delta_soft": oferta.delta_soft,
                    "idx_a": oferta.idx_a,
                    "idx_b": oferta.idx_b,
                    "evaluacion": dict(oferta.evaluacion),
                }
                for oferta in self.ofertas
            ],
            "metadata": dict(self.metadata),
        }


def _extraer_int_o_none(valor: Any) -> int | None:
    if valor is None:
        return None

    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _construir_oferta_evaluada(
    *,
    posicion: int,
    evaluacion: dict[str, Any],
) -> OfertaEvaluada:
    return OfertaEvaluada(
        posicion=posicion,
        clasificacion=str(evaluacion.get("clasificacion", "SIN_CLASIFICACION")),
        delta_score=float(evaluacion.get("delta_score", 0)),
        delta_hard=int(evaluacion.get("delta_hard", 0)),
        delta_soft=int(evaluacion.get("delta_soft", 0)),
        idx_a=_extraer_int_o_none(evaluacion.get("idx_a")),
        idx_b=_extraer_int_o_none(evaluacion.get("idx_b")),
        evaluacion=evaluacion,
    )


def _resumir_metadata_para_reporte(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    claves_visibles = [
        "modo_exploracion",
        "candidatos_generados",
        "candidatos_prefiltrados",
        "candidatos_seleccionados",
        "candidatos_evaluados",
        "top_n",
        "criterio_seleccion",
        "priorizacion_historica_aplicada",
        "tiempos_por_etapa",
    ]

    return {
        clave: metadata.get(clave)
        for clave in claves_visibles
        if clave in metadata
    }


def generar_reporte_oferta(
    resultado: ExplorationFlowResult,
    *,
    limite: int | None = None,
) -> OfferReport:
    if limite is not None and limite <= 0:
        raise ValueError("limite debe ser mayor que cero.")

    evaluaciones = resultado.evaluaciones

    if limite is not None:
        evaluaciones = evaluaciones[:limite]

    ofertas = [
        _construir_oferta_evaluada(
            posicion=posicion,
            evaluacion=evaluacion,
        )
        for posicion, evaluacion in enumerate(evaluaciones, start=1)
    ]

    metadata = _resumir_metadata_para_reporte(resultado.metadata)

    return OfferReport(
        mensaje=MENSAJE_REPORTING_OFERTA_RAPIDA,
        modo_exploracion=resultado.modo_exploracion,
        ofertas=ofertas,
        metadata=metadata,
    )