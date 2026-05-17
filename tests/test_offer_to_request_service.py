from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from src.engine import calcular_roster_hash
from src.models import Controlador, SwapRequest
from src.offer_reporting import OfertaEvaluada
from src.offer_to_request_service import (
    HISTORY_EVENT_CREADO_DESDE_OFERTA,
    SOURCE_TYPE_OFERTA_EVALUADA,
    crear_request_formal_desde_oferta,
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


def _crear_oferta_fake() -> OfertaEvaluada:
    return OfertaEvaluada(
        posicion=2,
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


def _crear_metadata_fake(
    *,
    roster_version_id_origen: str | None = "rv-1",
    roster_hash_origen: str | None = None,
) -> dict[str, Any]:
    metadata = {
        "modo_exploracion": "OFERTA_RAPIDA",
        "candidatos_generados": 100,
        "candidatos_prefiltrados": 80,
        "candidatos_seleccionados": 50,
        "candidatos_evaluados": 50,
        "top_n": 50,
        "criterio_seleccion": "candidate_selection_v1",
        "priorizacion_historica_aplicada": True,
        "roster_version_id_origen": roster_version_id_origen,
        "roster_hash_origen": roster_hash_origen,
    }

    return metadata


def _crear_request_fake(
    *,
    controlador_a: str,
    controlador_b: str,
    idx_a: int,
    idx_b: int,
    motivo: str | None = None,
) -> SwapRequest:
    return SwapRequest(
        id="req-1",
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=idx_a,
        idx_b=idx_b,
        estado="PENDIENTE",
        fecha_creacion=datetime.now(),
        motivo=motivo,
        roster_version_id="rv-1",
    )


def test_crea_request_formal_desde_oferta_en_estado_pendiente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

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

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    assert llamadas == [
        {
            "controlador_a": "ATC_001",
            "controlador_b": "ATC_002",
            "idx_a": 0,
            "idx_b": 1,
            "motivo": "CREADO_DESDE_OFERTA",
        }
    ]

    assert request.estado == "PENDIENTE"
    assert request.decision_sugerida is None


def test_adjunta_offer_origin_con_nombres_observados_origen_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        config_file="config_equilibrado.json",
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    assert request.offer_origin is not None
    assert request.offer_origin["created_from_offer"] is True
    assert request.offer_origin["source_type"] == SOURCE_TYPE_OFERTA_EVALUADA
    assert request.offer_origin["modo_exploracion"] == "OFERTA_RAPIDA"
    assert request.offer_origin["top_n"] == 50
    assert request.offer_origin["criterio_seleccion"] == "candidate_selection_v1"
    assert request.offer_origin["priorizacion_historica_aplicada"] is True
    assert request.offer_origin["offer_rank_observado"] == 2
    assert request.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert request.offer_origin["delta_score_observado"] == 0.0
    assert request.offer_origin["delta_hard_observado"] == 0
    assert request.offer_origin["delta_soft_observado"] == 0
    assert request.offer_origin["roster_version_id_origen"] == "rv-1"
    assert request.offer_origin["roster_hash_origen"] == roster_hash
    assert request.offer_origin["config_file_origen"] == "config_equilibrado.json"
    assert "created_from_offer_at" in request.offer_origin


def test_agrega_history_event_creado_desde_oferta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    assert any(
        HISTORY_EVENT_CREADO_DESDE_OFERTA in evento
        for evento in request.history
    )


def test_no_setea_decision_ni_estado_evaluado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    assert request.estado == "PENDIENTE"
    assert request.decision_sugerida is None
    assert not hasattr(request, "decision_operativa")
    assert not hasattr(request, "evaluacion_formal")


def test_no_llama_evaluacion_formal_resolucion_ni_aplicar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    def prohibido(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("No debe llamarse workflow formal en offer_to_request_service")

    monkeypatch.setattr(modulo, "evaluar_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "resolver_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    assert request.estado == "PENDIENTE"


def test_rechaza_oferta_sin_idx_a() -> None:
    oferta = OfertaEvaluada(
        posicion=1,
        clasificacion="ACEPTABLE",
        delta_score=0,
        delta_hard=0,
        delta_soft=0,
        idx_a=None,
        idx_b=1,
        evaluacion={},
    )

    with pytest.raises(ValueError, match="idx_a"):
        crear_request_formal_desde_oferta(
            oferta=oferta,
            asignaciones=_crear_asignaciones_fake(),
            metadata=_crear_metadata_fake(),
        )


def test_rechaza_oferta_sin_idx_b() -> None:
    oferta = OfertaEvaluada(
        posicion=1,
        clasificacion="ACEPTABLE",
        delta_score=0,
        delta_hard=0,
        delta_soft=0,
        idx_a=0,
        idx_b=None,
        evaluacion={},
    )

    with pytest.raises(ValueError, match="idx_b"):
        crear_request_formal_desde_oferta(
            oferta=oferta,
            asignaciones=_crear_asignaciones_fake(),
            metadata=_crear_metadata_fake(),
        )


def test_rechaza_roster_version_distinta() -> None:
    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    with pytest.raises(ValueError, match="otra version de roster"):
        crear_request_formal_desde_oferta(
            oferta=oferta,
            asignaciones=asignaciones,
            metadata=_crear_metadata_fake(
                roster_version_id_origen="rv-vieja",
                roster_hash_origen=roster_hash,
            ),
            roster_version_id_vigente="rv-1",
            roster_hash_vigente=roster_hash,
        )


def test_rechaza_roster_hash_inconsistente() -> None:
    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()

    with pytest.raises(ValueError, match="roster distinto"):
        crear_request_formal_desde_oferta(
            oferta=oferta,
            asignaciones=asignaciones,
            metadata=_crear_metadata_fake(
                roster_version_id_origen="rv-1",
                roster_hash_origen="hash-viejo",
            ),
            roster_version_id_vigente="rv-1",
            roster_hash_vigente="hash-vigente",
        )


def test_preserva_clasificacion_observada_sin_convertirla_en_formal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    assert request.offer_origin is not None
    assert request.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert not hasattr(request, "clasificacion")
    assert request.decision_sugerida is None
    assert request.estado == "PENDIENTE"


def test_request_creado_desde_oferta_puede_ser_evaluado_formalmente_despues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.offer_to_request_service as modulo
    from src.swap_service import evaluar_swap_request

    asignaciones = _crear_asignaciones_fake()
    oferta = _crear_oferta_fake()
    roster_hash = calcular_roster_hash(asignaciones)

    monkeypatch.setattr(modulo, "crear_swap_request", _crear_request_fake)

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=_crear_metadata_fake(roster_hash_origen=roster_hash),
        roster_version_id_vigente="rv-1",
        roster_hash_vigente=roster_hash,
    )

    def evaluar_swap_fn(
        *,
        asignaciones: list[Any],
        idx_a: int,
        idx_b: int,
        config_file: str,
    ) -> dict[str, Any]:
        assert idx_a == 0
        assert idx_b == 1
        return {
            "clasificacion": "ACEPTABLE",
            "delta_score": 0,
            "delta_hard": 0,
            "delta_soft": 0,
        }

    monkeypatch.setattr(
        "src.swap_service.obtener_roster_vigente",
        lambda: type(
            "RosterFake",
            (),
            {
                "id": "rv-1",
                "version_number": 1,
            },
        )(),
    )

    monkeypatch.setattr(
        "src.swap_service.guardar_request",
        lambda request: request,
    )

    monkeypatch.setattr(
        "src.swap_service._validar_ventana_operativa",
        lambda asignaciones, idx_a, idx_b, config: True,
    )

    monkeypatch.setattr(
        "src.swap_service.cargar_config",
        lambda config_file: {},
    )

    resultado = evaluar_swap_request(
        asignaciones=asignaciones,
        request=request,
        evaluar_swap_fn=evaluar_swap_fn,
        config_file="config_equilibrado.json",
    )

    assert request.estado == "EVALUADO"
    assert request.decision_sugerida == "OBSERVAR"
    assert resultado["clasificacion"] == "ACEPTABLE"
    assert resultado["decision"] == "OBSERVAR"