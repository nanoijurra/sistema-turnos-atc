from dataclasses import replace
from datetime import date

from src.models import Asignacion, Controlador, SwapRequest, crear_esquema_8h
from src.technical_prefilter import (
    filter_technically_plausible_candidates,
    is_candidate_technically_plausible,
)


def _crear_asignaciones():
    esquema = crear_esquema_8h()
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")
    fecha_base = date(2026, 3, 1)

    origen = Asignacion(fecha_base, turno_b, controlador_a)
    mismo_controlador = Asignacion(fecha_base, turno_c, controlador_a)
    misma_asignacion_exacta = replace(origen)
    swap_trivial = Asignacion(fecha_base, turno_b, controlador_b)
    plausible = Asignacion(fecha_base, turno_c, controlador_b)

    return origen, [
        mismo_controlador,
        misma_asignacion_exacta,
        swap_trivial,
        plausible,
    ]


def test_filter_technically_plausible_candidates_devuelve_lista():
    origen, candidatos = _crear_asignaciones()

    resultado = filter_technically_plausible_candidates(origen, candidatos, [origen, *candidatos])

    assert isinstance(resultado, list)


def test_is_candidate_technically_plausible_excluye_mismo_controlador():
    origen, candidatos = _crear_asignaciones()

    assert is_candidate_technically_plausible(origen, candidatos[0], [origen, *candidatos]) is False


def test_is_candidate_technically_plausible_excluye_misma_asignacion_exacta():
    origen, candidatos = _crear_asignaciones()

    assert is_candidate_technically_plausible(origen, candidatos[1], [origen, *candidatos]) is False


def test_filter_technically_plausible_candidates_excluye_swap_trivial_sin_cambio_real():
    origen, candidatos = _crear_asignaciones()

    resultado = filter_technically_plausible_candidates(origen, candidatos, [origen, *candidatos])

    assert candidatos[2] not in resultado


def test_filter_technically_plausible_candidates_no_clasifica_ni_decide_ni_devuelve_requests():
    origen, candidatos = _crear_asignaciones()

    resultado = filter_technically_plausible_candidates(origen, candidatos, [origen, *candidatos])

    assert resultado
    assert all(not isinstance(candidato, SwapRequest) for candidato in resultado)
    assert all(not hasattr(candidato, "clasificacion") for candidato in resultado)
    assert all(not hasattr(candidato, "decision") for candidato in resultado)


def test_filter_technically_plausible_candidates_mantiene_candidatos_plausibles_simples():
    origen, candidatos = _crear_asignaciones()

    resultado = filter_technically_plausible_candidates(origen, candidatos, [origen, *candidatos])

    assert candidatos[3] in resultado
