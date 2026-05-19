from __future__ import annotations

from datetime import date, time

from src.engine import calcular_roster_hash, crear_roster_version_inicial
from src.models import Asignacion, Controlador, Turno
from src.offer_reporting import OfertaEvaluada
from src.offer_to_request_service import crear_request_formal_desde_oferta
from src.request_store import guardar_request, limpiar_requests, obtener_request
from src.roster_store import limpiar_rosters


def _crear_asignaciones() -> list[Asignacion]:
    turno_a = Turno(
        codigo="A",
        hora_inicio=time(6, 30),
        duracion_horas=8,
        categoria="MANANA",
        es_nocturno=False,
    )
    turno_b = Turno(
        codigo="B",
        hora_inicio=time(14, 30),
        duracion_horas=8,
        categoria="TARDE",
        es_nocturno=False,
    )

    return [
        Asignacion(
            fecha=date(2026, 3, 1),
            turno=turno_a,
            controlador=Controlador("ATC_001"),
        ),
        Asignacion(
            fecha=date(2026, 3, 2),
            turno=turno_b,
            controlador=Controlador("ATC_002"),
        ),
    ]


def _crear_oferta() -> OfertaEvaluada:
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


def _crear_metadata(
    *,
    roster_version_id: str,
    roster_hash: str,
) -> dict:
    return {
        "modo_exploracion": "OFERTA_RAPIDA",
        "candidatos_generados": 20,
        "candidatos_prefiltrados": 12,
        "candidatos_seleccionados": 5,
        "candidatos_evaluados": 5,
        "top_n": 50,
        "criterio_seleccion": "candidate_selection_v1",
        "priorizacion_historica_aplicada": False,
        "roster_version_id_origen": roster_version_id,
        "roster_hash_origen": roster_hash,
    }


def setup_function() -> None:
    limpiar_requests()
    limpiar_rosters()


def test_metadata_de_seleccion_se_persiste_en_offer_origin() -> None:
    asignaciones = _crear_asignaciones()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta(),
        asignaciones=asignaciones,
        metadata=_crear_metadata(
            roster_version_id=roster.id,
            roster_hash=roster_hash,
        ),
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
        selected_by="SUP_ACC_CBA",
        selection_reason="Mejor alternativa disponible",
        selection_note="Seleccion validada durante prueba operativa",
    )

    guardar_request(request)

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["selected_by"] == "SUP_ACC_CBA"
    assert recuperado.offer_origin["selection_reason"] == "Mejor alternativa disponible"
    assert (
        recuperado.offer_origin["selection_note"]
        == "Seleccion validada durante prueba operativa"
    )

    assert recuperado.estado == "PENDIENTE"
    assert recuperado.decision_sugerida is None


def test_metadata_de_seleccion_none_se_persiste_como_none() -> None:
    asignaciones = _crear_asignaciones()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta(),
        asignaciones=asignaciones,
        metadata=_crear_metadata(
            roster_version_id=roster.id,
            roster_hash=roster_hash,
        ),
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
    )

    guardar_request(request)

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["selected_by"] is None
    assert recuperado.offer_origin["selection_reason"] is None
    assert recuperado.offer_origin["selection_note"] is None


def test_metadata_de_seleccion_persistida_no_reemplaza_decision_formal() -> None:
    asignaciones = _crear_asignaciones()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta(),
        asignaciones=asignaciones,
        metadata=_crear_metadata(
            roster_version_id=roster.id,
            roster_hash=roster_hash,
        ),
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
        selected_by="SUP_ACC_CBA",
        selection_reason="Motivo de seleccion, no decision",
        selection_note="Nota informativa",
    )

    guardar_request(request)

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.estado == "PENDIENTE"
    assert recuperado.decision_sugerida is None
    assert not hasattr(recuperado, "decision_operativa")
    assert not hasattr(recuperado, "aprobado_por")
    assert not hasattr(recuperado, "rechazado_por")

    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["selected_by"] == "SUP_ACC_CBA"
    assert recuperado.offer_origin["selection_reason"] == "Motivo de seleccion, no decision"