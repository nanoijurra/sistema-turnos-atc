from datetime import date, timedelta

from src.models import Asignacion, Controlador, SwapRequest, crear_esquema_8h
from src.simulator import (
    explorar_candidatos_acotados,
    explorar_swaps_entre_controladores,
)


def _crear_asignaciones():
    esquema = crear_esquema_8h()
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")
    fecha_base = date(2026, 3, 1)

    return [
        Asignacion(fecha_base, turno_b, controlador_a),
        Asignacion(fecha_base, turno_c, controlador_b),
        Asignacion(fecha_base - timedelta(days=1), turno_b, controlador_b),
        Asignacion(fecha_base + timedelta(days=1), turno_c, controlador_b),
    ]


def test_explorar_candidatos_acotados_devuelve_lista():
    asignaciones = _crear_asignaciones()

    candidatos = explorar_candidatos_acotados(asignaciones[0], asignaciones)

    assert isinstance(candidatos, list)


def test_explorar_candidatos_acotados_same_day_funciona():
    asignaciones = _crear_asignaciones()

    candidatos = explorar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="same_day",
    )

    assert candidatos == [asignaciones[1]]


def test_explorar_candidatos_acotados_future_funciona():
    asignaciones = _crear_asignaciones()

    candidatos = explorar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="future",
    )

    assert asignaciones[1] in candidatos
    assert asignaciones[3] in candidatos
    assert asignaciones[2] not in candidatos


def test_explorar_candidatos_acotados_no_rompe_simulator_existente():
    asignaciones = _crear_asignaciones()

    ranking = explorar_swaps_entre_controladores(asignaciones, limite=1)

    assert isinstance(ranking, list)


def test_explorar_candidatos_acotados_no_devuelve_requests():
    asignaciones = _crear_asignaciones()

    candidatos = explorar_candidatos_acotados(asignaciones[0], asignaciones)

    assert all(not isinstance(candidato, SwapRequest) for candidato in candidatos)


def test_explorar_candidatos_acotados_no_clasifica_por_si_mismo():
    asignaciones = _crear_asignaciones()

    candidatos = explorar_candidatos_acotados(asignaciones[0], asignaciones)

    assert candidatos
    assert all(not hasattr(candidato, "clasificacion") for candidato in candidatos)
    assert all(not hasattr(candidato, "decision") for candidato in candidatos)


def test_explorar_candidatos_acotados_usa_candidate_generation_correctamente():
    asignaciones = _crear_asignaciones()

    candidatos = explorar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="same_day",
    )

    assert all(candidato.fecha == asignaciones[0].fecha for candidato in candidatos)
    assert all(
        candidato.controlador.nombre != asignaciones[0].controlador.nombre
        for candidato in candidatos
    )
