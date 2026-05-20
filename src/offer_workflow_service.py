from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.models import SwapRequest
from src.offer_reporting import OfferReport
from src.offer_service import generar_oferta_para_asignacion
from src.offer_to_request_service import crear_request_formal_desde_reporte_oferta
from src.request_store import guardar_request, listar_requests


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


@dataclass(frozen=True)
class OfferRequestSummary:
    total: int
    por_estado: dict[str, int]
    por_clasificacion_observada: dict[str, int]
    por_selected_by: dict[str, int]
    por_modo_exploracion: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "por_estado": dict(self.por_estado),
            "por_clasificacion_observada": dict(self.por_clasificacion_observada),
            "por_selected_by": dict(self.por_selected_by),
            "por_modo_exploracion": dict(self.por_modo_exploracion),
        }

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
    selected_by: str | None = None,
    selection_reason: str | None = None,
    selection_note: str | None = None,
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
        selected_by=selected_by,
        selection_reason=selection_reason,
        selection_note=selection_note,
    )

    return OfferSelectionResult(
        reporte=reporte,
        request=request,
    )

def persistir_request_creado_desde_oferta(
    *,
    request: SwapRequest,
) -> SwapRequest:
    if request.estado != "PENDIENTE":
        raise ValueError(
            "Solo se puede persistir desde oferta un request en estado PENDIENTE."
        )

    if request.decision_sugerida is not None:
        raise ValueError(
            "No se puede persistir desde oferta un request que ya tiene decision_sugerida."
        )

    if request.offer_origin is None:
        raise ValueError(
            "No se puede persistir como request desde oferta sin offer_origin."
        )

    return guardar_request(request)

def generar_oferta_crear_y_persistir_request(
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
    selected_by: str | None = None,
    selection_reason: str | None = None,
    selection_note: str | None = None,
) -> OfferSelectionResult:
    resultado = generar_oferta_y_crear_request(
        asignacion_origen=asignacion_origen,
        asignaciones=asignaciones,
        config_file=config_file,
        posicion_oferta=posicion_oferta,
        modo_exploracion=modo_exploracion,
        top_n=top_n,
        historial_controladores=historial_controladores,
        limite_reporte=limite_reporte,
        roster_version_id_vigente=roster_version_id_vigente,
        roster_hash_vigente=roster_hash_vigente,
        selected_by=selected_by,
        selection_reason=selection_reason,
        selection_note=selection_note,
    )

    request_persistido = persistir_request_creado_desde_oferta(
        request=resultado.request,
    )

    return OfferSelectionResult(
        reporte=resultado.reporte,
        request=request_persistido,
    )

def es_request_creado_desde_oferta(
    *,
    request: SwapRequest,
) -> bool:
    offer_origin = request.offer_origin

    if not isinstance(offer_origin, dict):
        return False

    return (
        offer_origin.get("created_from_offer") is True
        and offer_origin.get("source_type") == "OFERTA_EVALUADA"
    )


def listar_requests_creados_desde_oferta() -> list[SwapRequest]:
    return [
        request
        for request in listar_requests()
        if es_request_creado_desde_oferta(request=request)
    ]

def listar_requests_creados_desde_oferta_filtrados(
    *,
    estado: str | None = None,
    selected_by: str | None = None,
    modo_exploracion: str | None = None,
    clasificacion_observada: str | None = None,
) -> list[SwapRequest]:
    requests = listar_requests_creados_desde_oferta()

    if estado is not None:
        requests = [
            request
            for request in requests
            if request.estado == estado
        ]

    if selected_by is not None:
        requests = [
            request
            for request in requests
            if isinstance(request.offer_origin, dict)
            and request.offer_origin.get("selected_by") == selected_by
        ]

    if modo_exploracion is not None:
        requests = [
            request
            for request in requests
            if isinstance(request.offer_origin, dict)
            and request.offer_origin.get("modo_exploracion") == modo_exploracion
        ]

    if clasificacion_observada is not None:
        requests = [
            request
            for request in requests
            if isinstance(request.offer_origin, dict)
            and request.offer_origin.get("clasificacion_observada")
            == clasificacion_observada
        ]

    return requests

def _incrementar_conteo(
    conteos: dict[str, int],
    clave: str | None,
) -> None:
    clave_normalizada = clave if clave else "SIN_DATO"
    conteos[clave_normalizada] = conteos.get(clave_normalizada, 0) + 1


def resumir_requests_creados_desde_oferta(
    *,
    estado: str | None = None,
    selected_by: str | None = None,
    modo_exploracion: str | None = None,
    clasificacion_observada: str | None = None,
) -> OfferRequestSummary:
    requests = listar_requests_creados_desde_oferta_filtrados(
        estado=estado,
        selected_by=selected_by,
        modo_exploracion=modo_exploracion,
        clasificacion_observada=clasificacion_observada,
    )

    por_estado: dict[str, int] = {}
    por_clasificacion_observada: dict[str, int] = {}
    por_selected_by: dict[str, int] = {}
    por_modo_exploracion: dict[str, int] = {}

    for request in requests:
        offer_origin = request.offer_origin if isinstance(request.offer_origin, dict) else {}

        _incrementar_conteo(por_estado, request.estado)
        _incrementar_conteo(
            por_clasificacion_observada,
            offer_origin.get("clasificacion_observada"),
        )
        _incrementar_conteo(
            por_selected_by,
            offer_origin.get("selected_by"),
        )
        _incrementar_conteo(
            por_modo_exploracion,
            offer_origin.get("modo_exploracion"),
        )

    return OfferRequestSummary(
        total=len(requests),
        por_estado=por_estado,
        por_clasificacion_observada=por_clasificacion_observada,
        por_selected_by=por_selected_by,
        por_modo_exploracion=por_modo_exploracion,
    )