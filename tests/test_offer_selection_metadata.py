from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from src.models import Controlador, SwapRequest
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_to_request_service import (
    crear_request_formal_desde_oferta,
    crear_request_formal_desde_reporte_oferta,
)


@dataclass(frozen=True)
class TurnoFake:
    codigo: str


@dataclass(frozen=True)
class AsignacionFake:
    fecha: str
    turno: TurnoFake
    controlador: Controlador | None


def _crear_asignaciones_fake() -> list[AsignacionFake]:
    return [
        AsignacionFake(
            fecha="2026-03-01",
            turno=TurnoFake("A"),
            controlador=Controlador("ATC_001"),
        ),
        AsignacionFake(
            fecha="2026-03-02",
            turno=TurnoFake("B"),
            controlador=Controlador("ATC_002"),
        ),
    ]


def _crear_oferta_fake() -> OfertaEvaluada:
    return OfertaEvaluada(
        posicion=1,
        clasificacion="ACEPTABLE",
        delta_score=0.0,
        delta_hard=0,
        delta_soft=0,
        idx_a=0,
        idx_b=1,
        evaluacion={
            "idx_a": 0,
            "idx_b": 1,
            "clasificacion": "ACEPTABLE",
            "delta_score": 0,
            "delta_hard": 0,
            "delta_soft": 0,
        },
    )


def _crear_metadata_fake() -> dict[str, Any]:
    return {
        "modo_exploracion": "OFERTA_RAPIDA",
        "candidatos_generados": 20,
        "candidatos_prefiltrados": 12,
        "candidatos_seleccionados": 2,
        "candidatos_evaluados": 2,
        "top_n": 50,
        "criterio_seleccion": "candidate_selection_v1",
        "priorizacion_historica_aplicada": False,
        "roster_version_id_origen": "rv-1",
        "roster_hash_origen": "hash-1",
    }


def _crear_reporte_fake() -> OfferReport:
    return OfferReport(
        mensaje="Mostrando mejores candidatos evaluados segun filtros actuales.",
        modo_exploracion="OFERTA_RAPIDA",
        ofertas=[_crear_oferta_fake()],
        metadata=_crear_metadata_fake(),
    )


def _crear_request_fake(
    *,
    controlador_a: str,
    controlador_b: str,
    idx_a: int,
    idx_b: int,
    motivo: str | None = None,
) -> SwapRequest:
    return SwapRequest(
        id="req-selection-metadata",
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=idx_a,
        idx_b=idx_b,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo=motivo,
        roster_version_id="rv-1",
    )


def test_crear_request_desde_oferta_adjunta_metadata_de_seleccion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta_fake(),
        asignaciones=_crear_asignaciones_fake(),
        metadata=_crear_metadata_fake(),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
        selected_by="SUP_ACC_CBA",
        selection_reason="Mejor equilibrio operativo observado",
        selection_note="Seleccionado durante prueba operativa",
    )

    assert request.offer_origin is not None
    assert request.offer_origin["selected_by"] == "SUP_ACC_CBA"
    assert (
        request.offer_origin["selection_reason"]
        == "Mejor equilibrio operativo observado"
    )
    assert request.offer_origin["selection_note"] == "Seleccionado durante prueba operativa"

    assert any(
        "selected_by=SUP_ACC_CBA" in evento
        for evento in request.history
    )


def test_crear_request_desde_oferta_sin_metadata_de_seleccion_deja_campos_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta_fake(),
        asignaciones=_crear_asignaciones_fake(),
        metadata=_crear_metadata_fake(),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
    )

    assert request.offer_origin is not None
    assert request.offer_origin["selected_by"] is None
    assert request.offer_origin["selection_reason"] is None
    assert request.offer_origin["selection_note"] is None


def test_crear_request_desde_reporte_propaga_metadata_de_seleccion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_reporte_oferta(
        reporte=_crear_reporte_fake(),
        posicion_oferta=1,
        asignaciones=_crear_asignaciones_fake(),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
        selected_by="SUP_TMA",
        selection_reason="Candidato preferido por disponibilidad",
        selection_note="Sin observaciones adicionales",
    )

    assert request.offer_origin is not None
    assert request.offer_origin["selected_by"] == "SUP_TMA"
    assert (
        request.offer_origin["selection_reason"]
        == "Candidato preferido por disponibilidad"
    )
    assert request.offer_origin["selection_note"] == "Sin observaciones adicionales"


def test_metadata_de_seleccion_no_decide_no_evalua_no_persiste(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe evaluar, decidir ni persistir")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "guardar_request", prohibido, raising=False)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta_fake(),
        asignaciones=_crear_asignaciones_fake(),
        metadata=_crear_metadata_fake(),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
        selected_by="SUP_ACC_CBA",
        selection_reason="Motivo operativo",
        selection_note="Nota operativa",
    )

    assert request.estado == "PENDIENTE"
    assert request.decision_sugerida is None