from datetime import date

from src.scenarios.v2_fatiga import crear_escenario
from src.simulator import (
    buscar_indice_asignacion,
    simular_swap,
    simular_swap_por_fecha,
    evaluar_swap,
    explorar_swaps,
    generar_pares_swap,
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


def test_explorar_swaps_devuelve_lista_ordenada():
    asignaciones = crear_escenario()

    pares = [(2, 3), (1, 3), (0, 3)]

    resultados = explorar_swaps(asignaciones, pares)

    assert isinstance(resultados, list)
    assert len(resultados) == 3

    for resultado in resultados:
        assert "swap" in resultado
        assert "valido_nuevo" in resultado
        assert "score_nuevo" in resultado
        assert "delta_score" in resultado


def test_generar_pares_swap_devuelve_combinaciones():
    asignaciones = [1, 2, 3, 4]

    pares = generar_pares_swap(asignaciones)

    assert (0, 1) in pares
    assert (0, 3) in pares
    assert (2, 3) in pares
    assert len(pares) == 6


def test_resumir_violaciones_y_evaluar_swap_incluyen_deltas():
    asignaciones = crear_escenario()

    resultado = evaluar_swap(asignaciones, 0, 3)

    assert "resumen_original" in resultado
    assert "resumen_nuevo" in resultado
    assert "delta_total_violaciones" in resultado
    assert "delta_hard" in resultado
    assert "delta_soft" in resultado