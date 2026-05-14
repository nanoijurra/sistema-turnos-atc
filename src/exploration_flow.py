from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from src.candidate_generation import generate_candidates
from src.candidate_selection import seleccionar_candidatos
from src.exploration_modes import (
    ModoExploracion,
    construir_metadata_diagnostico_completo,
    construir_metadata_oferta_rapida,
)
from src.roster_index import build_roster_index
from src.simulator import evaluar_swap
from src.technical_prefilter import filter_technically_plausible_candidates


DEFAULT_TOP_N_OFERTA_RAPIDA = 50


ORDEN_CLASIFICACION_TECNICA = {
    "BENEFICIOSO": 0,
    "ACEPTABLE": 1,
    "RECHAZABLE": 2,
}


@dataclass(frozen=True)
class ExplorationFlowResult:
    modo_exploracion: str
    evaluaciones: list[dict[str, Any]]
    metadata: dict[str, Any]

    @property
    def cantidad_evaluaciones(self) -> int:
        return len(self.evaluaciones)


def _obtener_indice_asignacion(
    asignaciones: list[Any],
    asignacion_buscada: Any,
) -> int:
    for idx, asignacion in enumerate(asignaciones):
        if asignacion is asignacion_buscada:
            return idx

    for idx, asignacion in enumerate(asignaciones):
        if asignacion == asignacion_buscada:
            return idx

    raise ValueError(
        "La asignacion indicada no pertenece al roster base."
    )


def _ordenar_evaluaciones_por_ranking_tecnico(
    evaluaciones: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def clave(evaluacion: dict[str, Any]) -> tuple[int, float, int, int]:
        clasificacion = str(evaluacion.get("clasificacion", "RECHAZABLE"))
        orden_clasificacion = ORDEN_CLASIFICACION_TECNICA.get(clasificacion, 99)

        delta_score = float(evaluacion.get("delta_score", 0))
        delta_hard = int(evaluacion.get("delta_hard", 0))
        delta_soft = int(evaluacion.get("delta_soft", 0))

        return (
            orden_clasificacion,
            -delta_score,
            delta_hard,
            delta_soft,
        )

    return sorted(evaluaciones, key=clave)


def _evaluar_candidatos(
    *,
    asignacion_origen: Any,
    candidatos: list[Any],
    asignaciones: list[Any],
    config_file: str,
) -> list[dict[str, Any]]:
    idx_origen = _obtener_indice_asignacion(asignaciones, asignacion_origen)
    evaluaciones: list[dict[str, Any]] = []

    for candidato in candidatos:
        idx_candidato = _obtener_indice_asignacion(asignaciones, candidato)

        evaluacion = evaluar_swap(
            asignaciones,
            idx_origen,
            idx_candidato,
            config_file,
        )
        evaluaciones.append(evaluacion)

    return evaluaciones


def explorar_oferta_rapida(
    *,
    asignacion_origen: Any,
    asignaciones: list[Any],
    config_file: str,
    top_n: int = DEFAULT_TOP_N_OFERTA_RAPIDA,
) -> ExplorationFlowResult:
    if top_n <= 0:
        raise ValueError("top_n debe ser mayor que cero.")

    tiempos_por_etapa: dict[str, float] = {}
    inicio_total = time.perf_counter()

    inicio = time.perf_counter()
    roster_index = build_roster_index(asignaciones)
    tiempos_por_etapa["roster_index_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    candidatos_generados = generate_candidates(
        asignacion_origen,
        roster_index,
        "future",
    )
    tiempos_por_etapa["candidate_generation_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    candidatos_prefiltrados = filter_technically_plausible_candidates(
        asignacion_origen,
        candidatos_generados,
        asignaciones,
        config_file,
    )
    tiempos_por_etapa["technical_prefilter_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    candidatos_seleccionados = seleccionar_candidatos(
        asignacion_origen,
        candidatos_prefiltrados,
        asignaciones,
        top_n=top_n,
    )
    tiempos_por_etapa["candidate_selection_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    evaluaciones = _evaluar_candidatos(
        asignacion_origen=asignacion_origen,
        candidatos=candidatos_seleccionados,
        asignaciones=asignaciones,
        config_file=config_file,
    )
    tiempos_por_etapa["simulator_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    evaluaciones_ordenadas = _ordenar_evaluaciones_por_ranking_tecnico(evaluaciones)
    tiempos_por_etapa["technical_ranking_ms"] = (time.perf_counter() - inicio) * 1000

    tiempos_por_etapa["total_ms"] = (time.perf_counter() - inicio_total) * 1000

    metadata = construir_metadata_oferta_rapida(
        candidatos_generados=len(candidatos_generados),
        candidatos_prefiltrados=len(candidatos_prefiltrados),
        candidatos_seleccionados=len(candidatos_seleccionados),
        candidatos_evaluados=len(evaluaciones_ordenadas),
        top_n=top_n,
        tiempos_por_etapa=tiempos_por_etapa,
    )

    return ExplorationFlowResult(
        modo_exploracion=ModoExploracion.OFERTA_RAPIDA.value,
        evaluaciones=evaluaciones_ordenadas,
        metadata=metadata.to_dict(),
    )


def explorar_diagnostico_completo(
    *,
    asignacion_origen: Any,
    asignaciones: list[Any],
    config_file: str,
) -> ExplorationFlowResult:
    tiempos_por_etapa: dict[str, float] = {}
    inicio_total = time.perf_counter()

    inicio = time.perf_counter()
    roster_index = build_roster_index(asignaciones)
    tiempos_por_etapa["roster_index_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    candidatos_generados = generate_candidates(
        asignacion_origen,
        roster_index,
        "future",
    )
    tiempos_por_etapa["candidate_generation_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    candidatos_prefiltrados = filter_technically_plausible_candidates(
        asignacion_origen,
        candidatos_generados,
        asignaciones,
        config_file,
    )
    tiempos_por_etapa["technical_prefilter_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    evaluaciones = _evaluar_candidatos(
        asignacion_origen=asignacion_origen,
        candidatos=candidatos_prefiltrados,
        asignaciones=asignaciones,
        config_file=config_file,
    )
    tiempos_por_etapa["simulator_ms"] = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    evaluaciones_ordenadas = _ordenar_evaluaciones_por_ranking_tecnico(evaluaciones)
    tiempos_por_etapa["technical_ranking_ms"] = (time.perf_counter() - inicio) * 1000

    tiempos_por_etapa["total_ms"] = (time.perf_counter() - inicio_total) * 1000

    metadata = construir_metadata_diagnostico_completo(
        candidatos_generados=len(candidatos_generados),
        candidatos_prefiltrados=len(candidatos_prefiltrados),
        candidatos_evaluados=len(evaluaciones_ordenadas),
        tiempos_por_etapa=tiempos_por_etapa,
    )

    return ExplorationFlowResult(
        modo_exploracion=ModoExploracion.DIAGNOSTICO_COMPLETO.value,
        evaluaciones=evaluaciones_ordenadas,
        metadata=metadata.to_dict(),
    )


def explorar_candidatos_para_oferta(
    *,
    asignacion_origen: Any,
    asignaciones: list[Any],
    config_file: str,
    modo_exploracion: str = ModoExploracion.OFERTA_RAPIDA.value,
    top_n: int = DEFAULT_TOP_N_OFERTA_RAPIDA,
) -> ExplorationFlowResult:
    if modo_exploracion == ModoExploracion.OFERTA_RAPIDA.value:
        return explorar_oferta_rapida(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            config_file=config_file,
            top_n=top_n,
        )

    if modo_exploracion == ModoExploracion.DIAGNOSTICO_COMPLETO.value:
        return explorar_diagnostico_completo(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            config_file=config_file,
        )

    raise ValueError(
        "Modo de exploracion no soportado por el flujo operativo: "
        f"{modo_exploracion}"
    )