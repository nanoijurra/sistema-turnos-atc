from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.models import SwapRequest
from src.offer_reporting import OfferReport
from src.offer_service import generar_oferta_para_asignacion
from src.offer_to_request_service import crear_request_formal_desde_reporte_oferta


@dataclass(frozen=True)
class OfferSelectionResult:
    reporte: OfferReport
    request: SwapRequest

    @property
    def request_id(self) -> str:
        return self.request.id

    @property
    def cantidad_ofertas(self) -> int:
        return self.reporte.cantidad_ofertas


def generar_oferta_y_crear_request(
    *,
    asignacion_origen: Any,
    asignaciones: list[Any],
    config_file: str,
    posicion_oferta: int,
    modo_exploracion: str = "OFERTA_RAPIDA",
    top_n: int = 50,
    historial_controladores: dict[str, Any] | None = None,
    limite_reporte: int | None = None,
    roster_version_id_vigente: str | None = None,
    roster_hash_vigente: str | None = None,
) -> OfferSelectionResult:
    reporte = generar_oferta_para_asignacion(
        asignacion_origen=asignacion_origen,
        asignaciones=asignaciones,
        config_file=config_file,
        modo_exploracion=modo_exploracion,
        top_n=top_n,
        historial_controladores=historial_controladores,
        limite=limite_reporte,
    )

    request = crear_request_formal_desde_reporte_oferta(
        reporte=reporte,
        posicion_oferta=posicion_oferta,
        asignaciones=asignaciones,
        config_file=config_file,
        roster_version_id_vigente=roster_version_id_vigente,
        roster_hash_vigente=roster_hash_vigente,
    )

    return OfferSelectionResult(
        reporte=reporte,
        request=request,
    )