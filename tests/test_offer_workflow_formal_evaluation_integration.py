from __future__ import annotations

from datetime import date, time

from src.engine import calcular_roster_hash, crear_roster_version_inicial
from src.models import Asignacion, Controlador, Turno
from src.offer_reporting import OfertaEvaluada, OfferReport
from src.offer_workflow_service import crear_request_desde_oferta_y_evaluar_formalmente
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


def test_crear_request_desde_oferta_y_evaluar_formalmente_persiste_evaluado(
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

    def evaluar_swap_fake(*, asignaciones, idx_a, idx_b, config_file):
        return {
            "idx_a": idx_a,
            "idx_b": idx_b,
            "clasificacion": "ACEPTABLE",
            "delta_score": 0,
            "delta_hard": 0,
            "delta_soft": 0,
            "impacto": {
                "ATC_001": {"hard": 0, "soft": 0},
                "ATC_002": {"hard": 0, "soft": 0},
            },
        }

    resultado = crear_request_desde_oferta_y_evaluar_formalmente(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        evaluar_swap_fn=evaluar_swap_fake,
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
        selected_by="SUP_ACC_CBA",
        selection_reason="Mejor alternativa disponible",
        selection_note="Evaluacion formal posterior a oferta",
    )

    recuperado = obtener_request(resultado.request.id)

    assert recuperado is not None
    assert recuperado.id == resultado.request.id
    assert recuperado.estado == "EVALUADO"
    assert recuperado.decision_sugerida == "OBSERVAR"
    assert recuperado.controlador_a == "ATC_001"
    assert recuperado.controlador_b == "ATC_002"
    assert recuperado.idx_a == 0
    assert recuperado.idx_b == 1
    assert recuperado.roster_version_id == roster.id
    assert recuperado.roster_hash == calcular_roster_hash(asignaciones)

    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["created_from_offer"] is True
    assert recuperado.offer_origin["source_type"] == "OFERTA_EVALUADA"
    assert recuperado.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert recuperado.offer_origin["selected_by"] == "SUP_ACC_CBA"

    assert resultado.request.estado == "EVALUADO"
    assert resultado.estado == "EVALUADO"
    assert resultado.decision_sugerida == "OBSERVAR"
    assert resultado.evaluacion_formal["clasificacion"] == "ACEPTABLE"
    assert resultado.evaluacion_formal["decision"] == "OBSERVAR"

    assert any("CREADO_DESDE_OFERTA" in evento for evento in recuperado.history)
    assert any("REQUEST_EVALUADO" in evento for evento in recuperado.history)


def test_crear_request_desde_oferta_y_evaluar_formalmente_no_reemplaza_clasificacion_observada(
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

    def evaluar_swap_fake(*, asignaciones, idx_a, idx_b, config_file):
        return {
            "idx_a": idx_a,
            "idx_b": idx_b,
            "clasificacion": "BENEFICIOSO",
            "delta_score": 10,
            "delta_hard": 0,
            "delta_soft": -1,
            "impacto": {},
        }

    resultado = crear_request_desde_oferta_y_evaluar_formalmente(
        asignacion_origen=asignaciones[0],
        asignaciones=asignaciones,
        config_file="config_equilibrado.json",
        posicion_oferta=1,
        evaluar_swap_fn=evaluar_swap_fake,
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
    )

    recuperado = obtener_request(resultado.request.id)

    assert recuperado is not None
    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert resultado.evaluacion_formal["clasificacion"] == "BENEFICIOSO"
    assert resultado.evaluacion_formal["decision"] == "VIABLE"
    assert recuperado.decision_sugerida == "VIABLE"