from __future__ import annotations

from datetime import date, time

from src.engine import calcular_roster_hash, crear_roster_version_inicial
from src.models import Asignacion, Controlador, Turno
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_workflow_service import generar_oferta_crear_y_persistir_request
from src.request_store import limpiar_requests, obtener_request
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


def _crear_reporte(
    *,
    roster_version_id: str,
    roster_hash: str,
) -> OfferReport:
    return OfferReport(
        mensaje="Mostrando mejores candidatos evaluados segun filtros actuales.",
        modo_exploracion="OFERTA_RAPIDA",
        ofertas=[
            OfertaEvaluada(
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
        ],
        metadata={
            "modo_exploracion": "OFERTA_RAPIDA",
            "candidatos_generados": 20,
            "candidatos_prefiltrados": 12,
            "candidatos_seleccionados": 1,
            "candidatos_evaluados": 1,
            "top_n": 50,
            "criterio_seleccion": "candidate_selection_v1",
            "priorizacion_historica_aplicada": False,
            "roster_version_id_origen": roster_version_id,
            "roster_hash_origen": roster_hash,
        },
    )


def setup_function() -> None:
    limpiar_requests()
    limpiar_rosters()


def test_generar_oferta_crear_y_persistir_request_se_recupera_desde_store(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)
    reporte = _crear_reporte(
        roster_version_id=roster.id,
        roster_hash=roster_hash,
    )

    monkeypatch.setattr(
        modulo,
        "generar_oferta_para_asignacion",
        lambda **kwargs: reporte,
    )

    resultado = generar_oferta_crear_y_persistir_request(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
        selected_by="SUP_ACC_CBA",
        selection_reason="Mejor alternativa disponible",
        selection_note="Persistencia desde fachada v60",
    )

    recuperado = obtener_request(resultado.request.id)

    assert recuperado is not None
    assert recuperado.id == resultado.request.id
    assert recuperado.estado == "PENDIENTE"
    assert recuperado.decision_sugerida is None
    assert recuperado.controlador_a == "ATC_001"
    assert recuperado.controlador_b == "ATC_002"
    assert recuperado.idx_a == 0
    assert recuperado.idx_b == 1
    assert recuperado.roster_version_id == roster.id

    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["created_from_offer"] is True
    assert recuperado.offer_origin["source_type"] == "OFERTA_EVALUADA"
    assert recuperado.offer_origin["offer_rank_observado"] == 1
    assert recuperado.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert recuperado.offer_origin["selected_by"] == "SUP_ACC_CBA"
    assert recuperado.offer_origin["selection_reason"] == "Mejor alternativa disponible"
    assert recuperado.offer_origin["selection_note"] == "Persistencia desde fachada v60"

    assert any("CREADO_DESDE_OFERTA" in evento for evento in recuperado.history)


def test_generar_oferta_crear_y_persistir_request_no_reemplaza_evaluacion_formal(
    monkeypatch,
) -> None:
    import src.offer_workflow_service as modulo

    asignaciones = _crear_asignaciones()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)
    reporte = _crear_reporte(
        roster_version_id=roster.id,
        roster_hash=roster_hash,
    )

    monkeypatch.setattr(
        modulo,
        "generar_oferta_para_asignacion",
        lambda **kwargs: reporte,
    )

    resultado = generar_oferta_crear_y_persistir_request(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
    )

    recuperado = obtener_request(resultado.request.id)

    assert recuperado is not None
    assert recuperado.estado == "PENDIENTE"
    assert recuperado.decision_sugerida is None
    assert not hasattr(recuperado, "clasificacion")
    assert not hasattr(recuperado, "decision_operativa")

    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["clasificacion_observada"] == "ACEPTABLE"