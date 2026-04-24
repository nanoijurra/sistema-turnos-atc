from dataclasses import replace
from datetime import date

from src.models import Asignacion, Controlador, SwapRequest, crear_esquema_8h
from src.technical_prefilter import (
    filter_technically_plausible_candidates,
    get_candidate_prefilter_diagnostic_reasons,
    is_candidate_technically_plausible,
)


def _crear_asignaciones():
    esquema = crear_esquema_8h()
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")
    controlador_c = Controlador("ATC_C")
    fecha_base = date(2026, 3, 1)

    origen = Asignacion(fecha_base, turno_b, controlador_a)
    mismo_controlador = Asignacion(fecha_base, turno_c, controlador_a)
    misma_asignacion_exacta = replace(origen)
    swap_trivial = Asignacion(fecha_base, turno_b, controlador_c)
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
    asignaciones = [origen, candidatos[3]]

    resultado = filter_technically_plausible_candidates(origen, [candidatos[3]], asignaciones)

    assert resultado
    assert all(not isinstance(candidato, SwapRequest) for candidato in resultado)
    assert all(not hasattr(candidato, "clasificacion") for candidato in resultado)
    assert all(not hasattr(candidato, "decision") for candidato in resultado)


def test_filter_technically_plausible_candidates_mantiene_candidatos_plausibles_simples():
    origen, candidatos = _crear_asignaciones()
    asignaciones = [origen, candidatos[3]]

    resultado = filter_technically_plausible_candidates(origen, [candidatos[3]], asignaciones)

    assert candidatos[3] in resultado


def test_filter_technically_plausible_candidates_descarta_descanso_local_obvio():
    esquema = crear_esquema_8h()
    turno_a = esquema.obtener_turno("A")
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")

    asignacion_previa = Asignacion(date(2026, 3, 1), turno_c, controlador_a)
    origen = Asignacion(date(2026, 3, 2), turno_b, controlador_a)
    candidata = Asignacion(date(2026, 3, 2), turno_a, controlador_b)
    asignaciones = [asignacion_previa, origen, candidata]

    resultado = filter_technically_plausible_candidates(origen, [candidata], asignaciones)
    motivos = get_candidate_prefilter_diagnostic_reasons(origen, candidata, asignaciones)

    assert candidata not in resultado
    assert "DESCANSO_LOCAL" in motivos


def test_filter_technically_plausible_candidates_descarta_secuencia_local_evidente():
    esquema = crear_esquema_8h()
    turno_a = esquema.obtener_turno("A")
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")

    asignacion_previa = Asignacion(date(2026, 3, 1), turno_c, controlador_a)
    origen = Asignacion(date(2026, 3, 2), turno_c, controlador_a)
    candidata = Asignacion(date(2026, 3, 2), turno_a, controlador_b)
    asignaciones = [asignacion_previa, origen, candidata]

    resultado = filter_technically_plausible_candidates(origen, [candidata], asignaciones)
    motivos = get_candidate_prefilter_diagnostic_reasons(origen, candidata, asignaciones)

    assert candidata not in resultado
    assert "SECUENCIA_LOCAL" in motivos


def test_is_candidate_technically_plausible_caso_ambiguo_deja_pasar():
    esquema = crear_esquema_8h()
    turno_a = esquema.obtener_turno("A")
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")
    controlador_c = Controlador("ATC_C")

    origen = Asignacion(date(2026, 3, 2), turno_b, controlador_a)
    candidata_fuera_roster = Asignacion(date(2026, 3, 3), turno_a, controlador_b)
    otra = Asignacion(date(2026, 3, 1), turno_c, controlador_c)

    assert is_candidate_technically_plausible(
        origen,
        candidata_fuera_roster,
        [origen, otra],
    ) is True


def test_is_candidate_technically_plausible_secuencia_local_ambigua_deja_pasar():
    esquema = crear_esquema_8h()
    turno_a = esquema.obtener_turno("A")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")

    origen = Asignacion(date(2026, 3, 2), turno_c, controlador_a)
    candidata_fuera_roster = Asignacion(date(2026, 3, 2), turno_a, controlador_b)

    assert is_candidate_technically_plausible(
        origen,
        candidata_fuera_roster,
        [origen],
    ) is True


def test_is_candidate_technically_plausible_sin_vecinos_deja_pasar():
    esquema = crear_esquema_8h()
    turno_a = esquema.obtener_turno("A")
    turno_b = esquema.obtener_turno("B")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")

    origen = Asignacion(date(2026, 3, 2), turno_b, controlador_a)
    candidata = Asignacion(date(2026, 3, 2), turno_a, controlador_b)

    assert is_candidate_technically_plausible(origen, candidata, [origen, candidata]) is True


def test_is_candidate_technically_plausible_secuencia_local_no_supera_limite_deja_pasar():
    esquema = crear_esquema_8h()
    turno_b = esquema.obtener_turno("B")
    turno_a = esquema.obtener_turno("A")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")

    asignacion_previa = Asignacion(date(2026, 3, 1), turno_a, controlador_a)
    origen = Asignacion(date(2026, 3, 2), turno_c, controlador_a)
    candidata = Asignacion(date(2026, 3, 2), turno_b, controlador_b)

    assert is_candidate_technically_plausible(
        origen,
        candidata,
        [asignacion_previa, origen, candidata],
    ) is True


def test_filter_technically_plausible_candidates_no_puntua():
    origen, candidatos = _crear_asignaciones()
    asignaciones = [origen, candidatos[3]]

    resultado = filter_technically_plausible_candidates(origen, [candidatos[3]], asignaciones)

    assert resultado
    assert all(not hasattr(candidato, "score") for candidato in resultado)
