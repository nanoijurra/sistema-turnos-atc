from datetime import date, timedelta

from src.models import Asignacion, Controlador, SwapRequest, crear_esquema_8h
from src.simulator import (
    explorar_swaps_entre_controladores,
    explorar_y_evaluar_candidatos_acotados,
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


def test_explorar_y_evaluar_candidatos_acotados_devuelve_lista():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
    )

    assert isinstance(resultados, list)


def test_explorar_y_evaluar_candidatos_acotados_same_day_funciona():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="same_day",
    )

    assert len(resultados) == 1
    assert resultados[0]["swap"] == {"idx_a": 0, "idx_b": 1}


def test_explorar_y_evaluar_candidatos_acotados_future_funciona():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="future",
    )

    swaps = {tuple(resultado["swap"].values()) for resultado in resultados}

    assert (0, 1) in swaps
    assert (0, 3) in swaps
    assert (0, 2) not in swaps


def test_explorar_y_evaluar_candidatos_acotados_contiene_evaluacion_tecnica_real():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="same_day",
    )

    resultado = resultados[0]

    assert "valido_original" in resultado
    assert "valido_nuevo" in resultado
    assert "score_original" in resultado
    assert "score_nuevo" in resultado
    assert "clasificacion" in resultado


def test_explorar_y_evaluar_candidatos_acotados_no_devuelve_requests():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
    )

    assert all(not isinstance(resultado, SwapRequest) for resultado in resultados)


def test_explorar_y_evaluar_candidatos_acotados_no_decide():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
    )

    assert resultados
    assert all("decision" not in resultado for resultado in resultados)
    assert all("decision_sugerida" not in resultado for resultado in resultados)


def test_explorar_y_evaluar_candidatos_acotados_no_rompe_simulator_existente():
    asignaciones = _crear_asignaciones()

    ranking = explorar_swaps_entre_controladores(asignaciones, limite=1)

    assert isinstance(ranking, list)


def test_explorar_y_evaluar_candidatos_acotados_mantiene_clasificacion_tecnica():
    asignaciones = _crear_asignaciones()

    resultados = explorar_y_evaluar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
    )

    assert all(
        resultado["clasificacion"] in {"BENEFICIOSO", "ACEPTABLE", "RECHAZABLE"}
        for resultado in resultados
    )
