from datetime import date

from src.scenarios.v2_fatiga import crear_escenario
from src.simulator import (
    buscar_indice_asignacion,
    simular_swap,
    simular_swap_por_fecha,
    evaluar_swap,
)


def test_simular_swap_devuelve_estructura_esperada():
    asignaciones = crear_escenario()

    resultado = simular_swap(asignaciones, 2, 3)

    assert "roster" in resultado
    assert "resultados" in resultado
    assert "valido" in resultado
    assert "score" in resultado
    assert "swap" in resultado


def test_simular_swap_detecta_roster_invalido_en_escenario_fatiga():
    asignaciones = crear_escenario()

    resultado = simular_swap(asignaciones, 2, 3)

    assert resultado["valido"] is False


def test_buscar_indice_asignacion_por_fecha():
    asignaciones = crear_escenario()

    idx = buscar_indice_asignacion(asignaciones, fecha=date(2026, 3, 3))

    assert idx == 2


def test_simular_swap_por_fecha_devuelve_estructura_valida():
    asignaciones = crear_escenario()

    resultado = simular_swap_por_fecha(
        asignaciones,
        fecha_a=date(2026, 3, 3),
        fecha_b=date(2026, 3, 4),
    )

    assert "roster" in resultado
    assert "resultados" in resultado
    assert "valido" in resultado
    assert "score" in resultado
    assert "swap" in resultado


def test_evaluar_swap_devuelve_comparacion_antes_y_despues():
    asignaciones = crear_escenario()

    resultado = evaluar_swap(asignaciones, 2, 3)

    assert "valido_original" in resultado
    assert "score_original" in resultado
    assert "valido_nuevo" in resultado
    assert "score_nuevo" in resultado
    assert "delta_score" in resultado
    assert "mejora" in resultado
    assert "empeora" in resultado
    assert "igual" in resultado
    assert "resultado_swap" in resultado