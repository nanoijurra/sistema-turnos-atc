from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.offer_reporting import OfertaEvaluada


def crear_swap_request(*, idx_a: int, idx_b: int) -> Any:
    try:
        from src.swap_service import crear_swap_request as crear_desde_swap_service

        return crear_desde_swap_service(idx_a=idx_a, idx_b=idx_b)
    except ImportError as exc:
        raise RuntimeError(
            "No se encontro una funcion disponible para crear SwapRequest. "
            "offer_request necesita una fabrica de request compatible."
        ) from exc


@dataclass(frozen=True)
class OfferRequestContext:
    modo_exploracion: str
    top_n: int | None
    criterio_seleccion: str | None
    priorizacion_historica_aplicada: bool
    metadata_origen: dict[str, Any]


def _validar_oferta_con_indices(oferta: OfertaEvaluada) -> None:
    if oferta.idx_a is None:
        raise ValueError("La oferta seleccionada no tiene idx_a.")

    if oferta.idx_b is None:
        raise ValueError("La oferta seleccionada no tiene idx_b.")


def construir_contexto_offer_request(
    *,
    metadata: dict[str, Any],
) -> OfferRequestContext:
    return OfferRequestContext(
        modo_exploracion=str(metadata.get("modo_exploracion", "")),
        top_n=metadata.get("top_n"),
        criterio_seleccion=metadata.get("criterio_seleccion"),
        priorizacion_historica_aplicada=bool(
            metadata.get("priorizacion_historica_aplicada", False)
        ),
        metadata_origen=dict(metadata),
    )


def crear_swap_request_desde_oferta(
    *,
    oferta: OfertaEvaluada,
    metadata: dict[str, Any],
) -> Any:
    _validar_oferta_con_indices(oferta)

    request = crear_swap_request(
        idx_a=oferta.idx_a,
        idx_b=oferta.idx_b,
    )

    contexto = construir_contexto_offer_request(metadata=metadata)

    setattr(request, "offer_context", contexto)
    setattr(request, "offer_metadata", contexto.metadata_origen)
    setattr(request, "offer_clasificacion", oferta.clasificacion)
    setattr(request, "offer_delta_score", oferta.delta_score)
    setattr(request, "offer_delta_hard", oferta.delta_hard)
    setattr(request, "offer_delta_soft", oferta.delta_soft)

    return request