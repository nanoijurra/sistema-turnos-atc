from __future__ import annotations

from typing import Any

from src.exploration_flow import (
    DEFAULT_TOP_N_OFERTA_RAPIDA,
    explorar_candidatos_para_oferta,
)
from src.exploration_modes import ModoExploracion
from src.offer_reporting import OfferReport, generar_reporte_oferta


def generar_oferta_para_asignacion(
    *,
    asignacion_origen: Any,
    asignaciones: list[Any],
    config_file: str,
    modo_exploracion: str = ModoExploracion.OFERTA_RAPIDA.value,
    top_n: int = DEFAULT_TOP_N_OFERTA_RAPIDA,
    historial_controladores: dict[str, Any] | None = None,
    limite: int | None = None,
) -> OfferReport:
    resultado_flujo = explorar_candidatos_para_oferta(
        asignacion_origen=asignacion_origen,
        asignaciones=asignaciones,
        config_file=config_file,
        modo_exploracion=modo_exploracion,
        top_n=top_n,
        historial_controladores=historial_controladores,
    )

    return generar_reporte_oferta(
        resultado_flujo,
        limite=limite,
    )