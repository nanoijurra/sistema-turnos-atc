from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from src.models import Controlador, SwapRequest
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_to_request_service import (
    crear_request_formal_desde_reporte_oferta,
    obtener_oferta_por_posicion,
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
        AsignacionFake(
            fecha="2026-03-03",
            turno=TurnoFake("C"),
            controlador=Controlador("ATC_003"),
        ),
    ]


def _crear_oferta(
    *,
    posicion: int,
    idx_a: int,
    idx_b: int,
    clasificacion: str,
    delta_score: float,
) -> OfertaEvaluada:
    return OfertaEvaluada(
        posicion=posicion,
        clasificacion=clasificacion,
        delta_score=delta_score,
        delta_hard=0,
        delta_soft=0,
        idx_a=idx_a,
        idx_b=idx_b,
        evaluacion={
            "idx_a": idx_a,
            "idx_b": idx_b,
            "clasificacion": clasificacion,
            "delta_score": delta_score,
            "delta_hard": 0,
            "delta_soft": 0,
        },
    )


def _crear_reporte_fake() -> OfferReport:
    return OfferReport(
        mensaje="Mostrando mejores candidatos evaluados segun filtros actuales.",
        modo_exploracion="OFERTA_RAPIDA",
        ofertas=[
            _crear_oferta(
                posicion=1,
                idx_a=0,
                idx_b=1,
                clasificacion="BENEFICIOSO",
                delta_score=10,
            ),
            _crear_oferta(
                posicion=2,
                idx_a=0,
                idx_b=2,
                clasificacion="ACEPTABLE",
                delta_score=0,
            ),
        ],
        metadata={
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
        },
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
        id="req-seleccion-oferta",
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=idx_a,
        idx_b=idx_b,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo=motivo,
        roster_version_id="rv-1",
    )


def test_obtener_oferta_por_posicion_devuelve_oferta_correcta() -> None:
    reporte = _crear_reporte_fake()

    oferta = obtener_oferta_por_posicion(
        reporte=reporte,
        posicion=2,
    )

    assert oferta.posicion == 2
    assert oferta.idx_a == 0
    assert oferta.idx_b == 2
    assert oferta.clasificacion == "ACEPTABLE"


def test_obtener_oferta_por_posicion_rechaza_posicion_cero() -> None:
    reporte = _crear_reporte_fake()

    with pytest.raises(ValueError, match="mayor que cero"):
        obtener_oferta_por_posicion(
            reporte=reporte,
            posicion=0,
        )


def test_obtener_oferta_por_posicion_rechaza_posicion_inexistente() -> None:
    reporte = _crear_reporte_fake()

    with pytest.raises(ValueError, match="No existe una oferta"):
        obtener_oferta_por_posicion(
            reporte=reporte,
            posicion=99,
        )


def test_crear_request_formal_desde_reporte_oferta_usa_oferta_seleccionada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    reporte = _crear_reporte_fake()
    asignaciones = _crear_asignaciones_fake()
    llamadas = []

    def crear_swap_request_fake(
        *,
        controlador_a: str,
        controlador_b: str,
        idx_a: int,
        idx_b: int,
        motivo: str | None = None,
    ) -> SwapRequest:
        llamadas.append(
            {
                "controlador_a": controlador_a,
                "controlador_b": controlador_b,
                "idx_a": idx_a,
                "idx_b": idx_b,
                "motivo": motivo,
            }
        )
        return _crear_request_fake(
            controlador_a=controlador_a,
            controlador_b=controlador_b,
            idx_a=idx_a,
            idx_b=idx_b,
            motivo=motivo,
        )

    monkeypatch.setattr(modulo, "crear_swap_request", crear_swap_request_fake)

    request = crear_request_formal_desde_reporte_oferta(
        reporte=reporte,
        posicion_oferta=2,
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
    )

    assert llamadas == [
        {
            "controlador_a": "ATC_001",
            "controlador_b": "ATC_003",
            "idx_a": 0,
            "idx_b": 2,
            "motivo": "CREADO_DESDE_OFERTA",
        }
    ]

    assert request.estado == "PENDIENTE"
    assert request.decision_sugerida is None
    assert request.idx_a == 0
    assert request.idx_b == 2
    assert request.controlador_a == "ATC_001"
    assert request.controlador_b == "ATC_003"


def test_crear_request_formal_desde_reporte_oferta_adjunta_offer_origin_del_reporte(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    reporte = _crear_reporte_fake()
    asignaciones = _crear_asignaciones_fake()

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_reporte_oferta(
        reporte=reporte,
        posicion_oferta=1,
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
    )

    assert request.offer_origin is not None
    assert request.offer_origin["created_from_offer"] is True
    assert request.offer_origin["source_type"] == "OFERTA_EVALUADA"
    assert request.offer_origin["modo_exploracion"] == "OFERTA_RAPIDA"
    assert request.offer_origin["top_n"] == 50
    assert request.offer_origin["criterio_seleccion"] == "candidate_selection_v1"
    assert request.offer_origin["offer_rank_observado"] == 1
    assert request.offer_origin["clasificacion_observada"] == "BENEFICIOSO"
    assert request.offer_origin["delta_score_observado"] == 10
    assert request.offer_origin["roster_version_id_origen"] == "rv-1"
    assert request.offer_origin["roster_hash_origen"] == "hash-1"


def test_crear_request_formal_desde_reporte_oferta_no_evalua_no_decide_no_persiste(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    reporte = _crear_reporte_fake()
    asignaciones = _crear_asignaciones_fake()

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe llamarse workflow formal ni persistencia")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "guardar_request", prohibido, raising=False)

    request = crear_request_formal_desde_reporte_oferta(
        reporte=reporte,
        posicion_oferta=1,
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        roster_version_id_vigente="rv-1",
        roster_hash_vigente="hash-1",
    )

    assert request.estado == "PENDIENTE"
    assert request.decision_sugerida is None


def test_crear_request_formal_desde_reporte_oferta_propaga_error_de_version_obsoleta() -> None:
    reporte = _crear_reporte_fake()
    asignaciones = _crear_asignaciones_fake()

    with pytest.raises(ValueError, match="otra version de roster"):
        crear_request_formal_desde_reporte_oferta(
            reporte=reporte,
            posicion_oferta=1,
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            roster_version_id_vigente="rv-2",
            roster_hash_vigente="hash-1",
        )


def test_crear_request_formal_desde_reporte_oferta_propaga_error_de_hash_obsoleto() -> None:
    reporte = _crear_reporte_fake()
    asignaciones = _crear_asignaciones_fake()

    with pytest.raises(ValueError, match="roster distinto"):
        crear_request_formal_desde_reporte_oferta(
            reporte=reporte,
            posicion_oferta=1,
            asignaciones=asignaciones,
            config_file="config_equilibrado.json",
            roster_version_id_vigente="rv-1",
            roster_hash_vigente="hash-2",
        )