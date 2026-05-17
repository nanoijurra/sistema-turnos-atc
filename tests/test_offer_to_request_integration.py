from __future__ import annotations

from datetime import date, time

from src.engine import calcular_roster_hash, crear_roster_version_inicial
from src.models import Asignacion, Controlador, Turno
from src.offer_reporting import OfertaEvaluada
from src.offer_to_request_service import crear_request_formal_desde_oferta
from src.request_store import guardar_request, limpiar_requests, obtener_request
from src.roster_store import limpiar_rosters, obtener_roster_vigente


def _crear_asignaciones_integracion() -> list[Asignacion]:
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
    turno_c = Turno(
        codigo="C",
        hora_inicio=time(22, 30),
        duracion_horas=8,
        categoria="NOCHE",
        es_nocturno=True,
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
        Asignacion(
            fecha=date(2026, 3, 3),
            turno=turno_c,
            controlador=Controlador("ATC_003"),
        ),
    ]


def _crear_oferta_integracion() -> OfertaEvaluada:
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


def _crear_metadata_integracion(
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


def test_request_creado_desde_oferta_se_puede_persistir_y_recuperar_con_offer_origin() -> None:
    asignaciones = _crear_asignaciones_integracion()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    oferta = _crear_oferta_integracion()
    metadata = _crear_metadata_integracion(
        roster_version_id=roster.id,
        roster_hash=roster_hash,
    )

    request = crear_request_formal_desde_oferta(
        oferta=oferta,
        asignaciones=asignaciones,
        metadata=metadata,
        config_file="config_equilibrado.json",
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
    )

    guardar_request(request)

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.id == request.id
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
    assert recuperado.offer_origin["modo_exploracion"] == "OFERTA_RAPIDA"
    assert recuperado.offer_origin["offer_rank_observado"] == 1
    assert recuperado.offer_origin["clasificacion_observada"] == "ACEPTABLE"
    assert recuperado.offer_origin["delta_score_observado"] == 0.0
    assert recuperado.offer_origin["delta_hard_observado"] == 0
    assert recuperado.offer_origin["delta_soft_observado"] == 0
    assert recuperado.offer_origin["roster_version_id_origen"] == roster.id
    assert recuperado.offer_origin["roster_hash_origen"] == roster_hash
    assert recuperado.offer_origin["config_file_origen"] == "config_equilibrado.json"

    assert any("CREADO_DESDE_OFERTA" in evento for evento in recuperado.history)


def test_request_creado_desde_oferta_no_reemplaza_evaluacion_formal() -> None:
    asignaciones = _crear_asignaciones_integracion()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta_integracion(),
        asignaciones=asignaciones,
        metadata=_crear_metadata_integracion(
            roster_version_id=roster.id,
            roster_hash=roster_hash,
        ),
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
    )

    guardar_request(request)

    recuperado = obtener_request(request.id)

    assert recuperado is not None
    assert recuperado.estado == "PENDIENTE"
    assert recuperado.decision_sugerida is None
    assert not hasattr(recuperado, "clasificacion")
    assert recuperado.offer_origin is not None
    assert recuperado.offer_origin["clasificacion_observada"] == "ACEPTABLE"


def test_request_desde_oferta_rechaza_conversion_si_roster_vigente_cambio() -> None:
    asignaciones = _crear_asignaciones_integracion()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    oferta = _crear_oferta_integracion()
    metadata = _crear_metadata_integracion(
        roster_version_id=roster.id,
        roster_hash=roster_hash,
    )

    try:
        crear_request_formal_desde_oferta(
            oferta=oferta,
            asignaciones=asignaciones,
            metadata=metadata,
            roster_version_id_vigente="otra-version",
            roster_hash_vigente=roster_hash,
        )
    except ValueError as exc:
        assert "otra version de roster" in str(exc)
    else:
        raise AssertionError("Debio rechazar oferta generada con otra version de roster.")


def test_request_desde_oferta_rechaza_conversion_si_hash_vigente_cambio() -> None:
    asignaciones = _crear_asignaciones_integracion()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    oferta = _crear_oferta_integracion()
    metadata = _crear_metadata_integracion(
        roster_version_id=roster.id,
        roster_hash=roster_hash,
    )

    try:
        crear_request_formal_desde_oferta(
            oferta=oferta,
            asignaciones=asignaciones,
            metadata=metadata,
            roster_version_id_vigente=roster.id,
            roster_hash_vigente="otro-hash",
        )
    except ValueError as exc:
        assert "roster distinto" in str(exc)
    else:
        raise AssertionError("Debio rechazar oferta generada con otro hash de roster.")


def test_request_desde_oferta_usa_roster_vigente_real_para_creacion_formal() -> None:
    asignaciones = _crear_asignaciones_integracion()
    roster = crear_roster_version_inicial(asignaciones, regimen_horario="8H")
    roster_hash = calcular_roster_hash(asignaciones)

    assert obtener_roster_vigente() is not None

    request = crear_request_formal_desde_oferta(
        oferta=_crear_oferta_integracion(),
        asignaciones=asignaciones,
        metadata=_crear_metadata_integracion(
            roster_version_id=roster.id,
            roster_hash=roster_hash,
        ),
        roster_version_id_vigente=roster.id,
        roster_hash_vigente=roster_hash,
    )

    assert request.roster_version_id == roster.id
    assert request.estado == "PENDIENTE"
    assert request.offer_origin is not None