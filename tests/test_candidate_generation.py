from datetime import date, timedelta

from src.candidate_generation import (
    generate_candidates,
    generate_future_candidates,
    generate_same_day_candidates,
)
from src.models import Asignacion, Controlador, SwapRequest, crear_esquema_8h
from src.roster_index import build_roster_index


def _crear_asignaciones():
    esquema = crear_esquema_8h()
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")
    controlador_c = Controlador("ATC_C")
    fecha_base = date(2026, 3, 1)

    return [
        Asignacion(fecha_base, turno_b, controlador_a),
        Asignacion(fecha_base, turno_c, controlador_b),
        Asignacion(fecha_base - timedelta(days=1), turno_b, controlador_b),
        Asignacion(fecha_base + timedelta(days=1), turno_c, controlador_b),
        Asignacion(fecha_base + timedelta(days=2), turno_b, controlador_c),
    ]


def test_same_day_devuelve_candidatos_del_mismo_dia():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_same_day_candidates(asignaciones[0], index)

    assert candidatos == [asignaciones[1]]
    assert all(candidato.fecha == asignaciones[0].fecha for candidato in candidatos)


def test_same_day_excluye_mismo_controlador():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_same_day_candidates(asignaciones[0], index)

    assert asignaciones[0] not in candidatos
    assert all(
        candidato.controlador.nombre != asignaciones[0].controlador.nombre
        for candidato in candidatos
    )


def test_future_devuelve_candidatos_desde_fecha_origen_hacia_adelante():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_future_candidates(asignaciones[0], index)

    assert asignaciones[1] in candidatos
    assert asignaciones[3] in candidatos
    assert asignaciones[4] in candidatos
    assert all(candidato.fecha >= asignaciones[0].fecha for candidato in candidatos)


def test_future_excluye_fechas_anteriores():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_future_candidates(asignaciones[0], index)

    assert asignaciones[2] not in candidatos


def test_generate_candidates_auto_no_rompe_contrato():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_candidates(asignaciones[0], index)

    assert isinstance(candidatos, list)
    assert all(isinstance(candidato, Asignacion) for candidato in candidatos)


def test_candidate_generation_devuelve_asignaciones_no_requests():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_candidates(asignaciones[0], index, mode="same_day")

    assert all(not isinstance(candidato, SwapRequest) for candidato in candidatos)


def test_candidate_generation_no_clasifica_ni_decide():
    asignaciones = _crear_asignaciones()
    index = build_roster_index(asignaciones)

    candidatos = generate_candidates(asignaciones[0], index)

    assert candidatos
    assert all(not hasattr(candidato, "clasificacion") for candidato in candidatos)
    assert all(not hasattr(candidato, "decision") for candidato in candidatos)
