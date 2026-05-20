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


@dataclass(frozen=True)
class OfferRequestSummaryReport:
    mensaje: str
    filtros: dict[str, Any]
    resumen: OfferRequestSummary

    def to_dict(self) -> dict[str, Any]:
        return {
            "mensaje": self.mensaje,
            "filtros": dict(self.filtros),
            "resumen": self.resumen.to_dict(),
        }
    
@dataclass(frozen=True)
class OfferRequestDetail:
    request_id: str
    estado: str
    controlador_a: str
    controlador_b: str
    idx_a: int
    idx_b: int
    roster_version_id: str | None
    fecha_creacion: str | None
    selected_by: str | None
    selection_reason: str | None
    selection_note: str | None
    modo_exploracion: str | None
    clasificacion_observada: str | None
    offer_rank_observado: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "estado": self.estado,
            "controlador_a": self.controlador_a,
            "controlador_b": self.controlador_b,
            "idx_a": self.idx_a,
            "idx_b": self.idx_b,
            "roster_version_id": self.roster_version_id,
            "fecha_creacion": self.fecha_creacion,
            "selected_by": self.selected_by,
            "selection_reason": self.selection_reason,
            "selection_note": self.selection_note,
            "modo_exploracion": self.modo_exploracion,
            "clasificacion_observada": self.clasificacion_observada,
            "offer_rank_observado": self.offer_rank_observado,
        }


@dataclass(frozen=True)
class OfferRequestDetailReport:
    mensaje: str
    filtros: dict[str, Any]
    total: int
    detalles: list[OfferRequestDetail]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mensaje": self.mensaje,
            "filtros": dict(self.filtros),
            "total": self.total,
            "detalles": [
                detalle.to_dict()
                for detalle in self.detalles
            ],
        }

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

MENSAJE_RESUMEN_REQUESTS_DESDE_OFERTA = (
    "Resumen de solicitudes creadas desde ofertas evaluadas."
)


def _construir_filtros_resumen_requests_desde_oferta(
    *,
    estado: str | None = None,
    selected_by: str | None = None,
    modo_exploracion: str | None = None,
    clasificacion_observada: str | None = None,
) -> dict[str, Any]:
    return {
        "estado": estado,
        "selected_by": selected_by,
        "modo_exploracion": modo_exploracion,
        "clasificacion_observada": clasificacion_observada,
    }


def generar_reporte_resumen_requests_creados_desde_oferta(
    *,
    estado: str | None = None,
    selected_by: str | None = None,
    modo_exploracion: str | None = None,
    clasificacion_observada: str | None = None,
) -> OfferRequestSummaryReport:
    resumen = resumir_requests_creados_desde_oferta(
        estado=estado,
        selected_by=selected_by,
        modo_exploracion=modo_exploracion,
        clasificacion_observada=clasificacion_observada,
    )

    filtros = _construir_filtros_resumen_requests_desde_oferta(
        estado=estado,
        selected_by=selected_by,
        modo_exploracion=modo_exploracion,
        clasificacion_observada=clasificacion_observada,
    )

    return OfferRequestSummaryReport(
        mensaje=MENSAJE_RESUMEN_REQUESTS_DESDE_OFERTA,
        filtros=filtros,
        resumen=resumen,
    )

MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA = (
    "Listado de solicitudes creadas desde ofertas evaluadas."
)


def _serializar_fecha_creacion_request(request: SwapRequest) -> str | None:
    fecha_creacion = request.fecha_creacion

    if fecha_creacion is None:
        return None

    if hasattr(fecha_creacion, "isoformat"):
        return fecha_creacion.isoformat()

    return str(fecha_creacion)


def _obtener_offer_origin_dict(request: SwapRequest) -> dict[str, Any]:
    if isinstance(request.offer_origin, dict):
        return request.offer_origin

    return {}


def construir_detalle_request_creado_desde_oferta(
    *,
    request: SwapRequest,
) -> OfferRequestDetail:
    offer_origin = _obtener_offer_origin_dict(request)

    return OfferRequestDetail(
        request_id=request.id,
        estado=request.estado,
        controlador_a=request.controlador_a,
        controlador_b=request.controlador_b,
        idx_a=request.idx_a,
        idx_b=request.idx_b,
        roster_version_id=request.roster_version_id,
        fecha_creacion=_serializar_fecha_creacion_request(request),
        selected_by=offer_origin.get("selected_by"),
        selection_reason=offer_origin.get("selection_reason"),
        selection_note=offer_origin.get("selection_note"),
        modo_exploracion=offer_origin.get("modo_exploracion"),
        clasificacion_observada=offer_origin.get("clasificacion_observada"),
        offer_rank_observado=offer_origin.get("offer_rank_observado"),
    )


def generar_reporte_detalle_requests_creados_desde_oferta(
    *,
    estado: str | None = None,
    selected_by: str | None = None,
    modo_exploracion: str | None = None,
    clasificacion_observada: str | None = None,
) -> OfferRequestDetailReport:
    requests = listar_requests_creados_desde_oferta_filtrados(
        estado=estado,
        selected_by=selected_by,
        modo_exploracion=modo_exploracion,
        clasificacion_observada=clasificacion_observada,
    )

    detalles = [
        construir_detalle_request_creado_desde_oferta(request=request)
        for request in requests
    ]

    filtros = _construir_filtros_resumen_requests_desde_oferta(
        estado=estado,
        selected_by=selected_by,
        modo_exploracion=modo_exploracion,
        clasificacion_observada=clasificacion_observada,
    )

    return OfferRequestDetailReport(
        mensaje=MENSAJE_DETALLE_REQUESTS_DESDE_OFERTA,
        filtros=filtros,
        total=len(detalles),
        detalles=detalles,
    )