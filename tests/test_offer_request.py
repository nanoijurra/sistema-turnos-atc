from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.offer_reporting import OfertaEvaluada
from src.offer_request import (
    OfferRequestContext,
    construir_contexto_offer_request,
    crear_swap_request_desde_oferta,
)


@dataclass
class SwapRequestFake:
    idx_a: int
    idx_b: int


def _crear_oferta_fake() -> OfertaEvaluada:
    return OfertaEvaluada(
        posicion=1,
        clasificacion="ACEPTABLE",
        delta_score=0.0,
        delta_hard=0,
        delta_soft=0,
        idx_a=3,
        idx_b=7,
        evaluacion={
            "idx_a": 3,
            "idx_b": 7,
            "clasificacion": "ACEPTABLE",
            "delta_score": 0,
            "delta_hard": 0,
            "delta_soft": 0,
        },
    )


def _crear_metadata_fake() -> dict[str, Any]:
    return {
        "modo_exploracion": "OFERTA_RAPIDA",
        "candidatos_generados": 100,
        "candidatos_prefiltrados": 80,
        "candidatos_seleccionados": 50,
        "candidatos_evaluados": 50,
        "top_n": 50,
        "criterio_seleccion": "candidate_selection_v1",
        "priorizacion_historica_aplicada": True,
        "tiempos_por_etapa": {
            "total_ms": 123.4,
        },
    }


def test_construir_contexto_offer_request_desde_metadata() -> None:
    metadata = _crear_metadata_fake()

    contexto = construir_contexto_offer_request(metadata=metadata)

    assert contexto == OfferRequestContext(
        modo_exploracion="OFERTA_RAPIDA",
        top_n=50,
        criterio_seleccion="candidate_selection_v1",
        priorizacion_historica_aplicada=True,
        metadata_origen=metadata,
    )


def test_crear_swap_request_desde_oferta_usa_indices_de_la_oferta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_request as modulo

    oferta = _crear_oferta_fake()
    metadata = _crear_metadata_fake()
    llamadas = []

    def crear_swap_request_fake(*, idx_a: int, idx_b: int) -> SwapRequestFake:
        llamadas.append(
            {
                "idx_a": idx_a,
                "idx_b": idx_b,
            }
        )
        return SwapRequestFake(idx_a=idx_a, idx_b=idx_b)

    monkeypatch.setattr(modulo, "crear_swap_request", crear_swap_request_fake)

    request = crear_swap_request_desde_oferta(
        oferta=oferta,
        metadata=metadata,
    )

    assert llamadas == [
        {
            "idx_a": 3,
            "idx_b": 7,
        }
    ]

    assert request.idx_a == 3
    assert request.idx_b == 7


def test_crear_swap_request_desde_oferta_agrega_contexto_de_origen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_request as modulo

    oferta = _crear_oferta_fake()
    metadata = _crear_metadata_fake()

    monkeypatch.setattr(
        modulo,
        "crear_swap_request",
        lambda *, idx_a, idx_b: SwapRequestFake(idx_a=idx_a, idx_b=idx_b),
    )

    request = crear_swap_request_desde_oferta(
        oferta=oferta,
        metadata=metadata,
    )

    assert request.offer_context == OfferRequestContext(
        modo_exploracion="OFERTA_RAPIDA",
        top_n=50,
        criterio_seleccion="candidate_selection_v1",
        priorizacion_historica_aplicada=True,
        metadata_origen=metadata,
    )

    assert request.offer_metadata == metadata


def test_crear_swap_request_desde_oferta_preserva_resumen_tecnico_de_la_oferta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_request as modulo

    oferta = _crear_oferta_fake()
    metadata = _crear_metadata_fake()

    monkeypatch.setattr(
        modulo,
        "crear_swap_request",
        lambda *, idx_a, idx_b: SwapRequestFake(idx_a=idx_a, idx_b=idx_b),
    )

    request = crear_swap_request_desde_oferta(
        oferta=oferta,
        metadata=metadata,
    )

    assert request.offer_clasificacion == "ACEPTABLE"
    assert request.offer_delta_score == 0.0
    assert request.offer_delta_hard == 0
    assert request.offer_delta_soft == 0


def test_crear_swap_request_desde_oferta_no_evalua_no_decide_no_persiste(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_request as modulo

    oferta = _crear_oferta_fake()
    metadata = _crear_metadata_fake()

    monkeypatch.setattr(
        modulo,
        "crear_swap_request",
        lambda *, idx_a, idx_b: SwapRequestFake(idx_a=idx_a, idx_b=idx_b),
    )

    request = crear_swap_request_desde_oferta(
        oferta=oferta,
        metadata=metadata,
    )

    assert not hasattr(request, "decision_sugerida")
    assert not hasattr(request, "decision_operativa")
    assert not hasattr(request, "evaluacion_tecnica")
    assert not hasattr(request, "persistido")
    assert not hasattr(request, "aplicado")


def test_crear_swap_request_desde_oferta_rechaza_oferta_sin_idx_a() -> None:
    oferta = OfertaEvaluada(
        posicion=1,
        clasificacion="ACEPTABLE",
        delta_score=0,
        delta_hard=0,
        delta_soft=0,
        idx_a=None,
        idx_b=7,
        evaluacion={},
    )

    with pytest.raises(ValueError, match="idx_a"):
        crear_swap_request_desde_oferta(
            oferta=oferta,
            metadata=_crear_metadata_fake(),
        )


def test_crear_swap_request_desde_oferta_rechaza_oferta_sin_idx_b() -> None:
    oferta = OfertaEvaluada(
        posicion=1,
        clasificacion="ACEPTABLE",
        delta_score=0,
        delta_hard=0,
        delta_soft=0,
        idx_a=3,
        idx_b=None,
        evaluacion={},
    )

    with pytest.raises(ValueError, match="idx_b"):
        crear_swap_request_desde_oferta(
            oferta=oferta,
            metadata=_crear_metadata_fake(),
        )