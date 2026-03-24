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

def test_evaluar_swap_incluye_resumen_por_regla():
    asignaciones = crear_escenario()

    resultado = evaluar_swap(asignaciones, 0, 3)

    assert "resumen_por_regla_original" in resultado
    assert "resumen_por_regla_nuevo" in resultado
    assert isinstance(resultado["resumen_por_regla_original"], dict)
    assert isinstance(resultado["resumen_por_regla_nuevo"], dict)

def test_explorar_swaps_incluye_impacto():
    asignaciones = crear_escenario()

    pares = [(0, 3), (1, 3)]
    resultados = explorar_swaps(asignaciones, pares)

    for r in resultados:
        assert "impacto" in r
        
def test_evaluar_swap_incluye_resumen_por_controlador():
    from src.scenarios.v3_controladores_mixto import crear_escenario

    asignaciones = crear_escenario()
    resultado = evaluar_swap(asignaciones, 2, 3)

    assert "resumen_por_controlador_original" in resultado
    assert "resumen_por_controlador_nuevo" in resultado
    assert isinstance(resultado["resumen_por_controlador_original"], dict)
    assert isinstance(resultado["resumen_por_controlador_nuevo"], dict)
          
def test_generar_pares_swap_entre_controladores_devuelve_pares():
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.simulator import generar_pares_swap_entre_controladores

    asignaciones = crear_escenario()
    pares = generar_pares_swap_entre_controladores(asignaciones)

    assert isinstance(pares, list)
    assert len(pares) > 0

    for i, j in pares:
        ctrl_i = asignaciones[i].controlador.nombre
        ctrl_j = asignaciones[j].controlador.nombre
        assert ctrl_i != ctrl_j


def test_explorar_swaps_entre_controladores_devuelve_lista():
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.simulator import explorar_swaps_entre_controladores

    asignaciones = crear_escenario()
    ranking = explorar_swaps_entre_controladores(asignaciones)

    assert isinstance(ranking, list)
    assert len(ranking) > 0
    assert "clasificacion" in ranking[0]      

def test_evaluar_swap_incluye_clasificacion():
    from src.scenarios.v3_controladores_mixto import crear_escenario

    asignaciones = crear_escenario()
    resultado = evaluar_swap(asignaciones, 2, 3)

    assert resultado["clasificacion"] in {
        "BENEFICIOSO",
        "ACEPTABLE",
        "RECHAZABLE",
    }

def test_escenario_beneficioso_devuelve_algun_swap_no_rechazable():
    from src.scenarios.v4_controladores_beneficioso import crear_escenario
    from src.simulator import explorar_swaps_entre_controladores

    asignaciones = crear_escenario()
    ranking = explorar_swaps_entre_controladores(asignaciones)

    assert len(ranking) > 0
    assert any(r["clasificacion"] in {"BENEFICIOSO", "ACEPTABLE"} for r in ranking)


def test_escenario_aceptable_devuelve_algun_swap_aceptable_o_beneficioso():
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.simulator import explorar_swaps_entre_controladores

    asignaciones = crear_escenario()
    ranking = explorar_swaps_entre_controladores(asignaciones)

    assert len(ranking) > 0
    assert any(r["clasificacion"] in {"ACEPTABLE", "BENEFICIOSO"} for r in ranking)

def test_crear_swap_request_devuelve_objeto_valido():
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.simulator import crear_swap_request

    asignaciones = crear_escenario()

    request = crear_swap_request(asignaciones, 0, 3)

    assert request.controlador_a != request.controlador_b
    assert request.estado == "PENDIENTE"

def test_evaluar_swap_request_devuelve_decision():
    from src.scenarios.v4_controladores_beneficioso import crear_escenario
    from src.simulator import crear_swap_request, evaluar_swap_request

    asignaciones = crear_escenario()

    request = crear_swap_request(asignaciones, 2, 3)
    resultado = evaluar_swap_request(asignaciones, request)

    assert resultado["decision"] in {"APROBABLE", "OBSERVAR", "RECHAZAR"}

def test_resolver_swap_request_cambia_estado():
    from src.scenarios.v3_controladores_mixto import crear_escenario
    from src.simulator import crear_swap_request, resolver_swap_request

    asignaciones = crear_escenario()

    request = crear_swap_request(asignaciones, 0, 3)

    request = resolver_swap_request(request, "RECHAZAR")

    assert request.estado == "RECHAZADO"
    assert request.fecha_resolucion is not None

def test_aplicar_swap_request_modifica_roster_si_esta_aceptado():
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.simulator import crear_swap_request, resolver_swap_request, aplicar_swap_request

    asignaciones = crear_escenario()

    request = crear_swap_request(asignaciones, 0, 3)
    request = resolver_swap_request(request, "ACEPTAR")

    roster_nuevo = aplicar_swap_request(asignaciones, request)

    assert roster_nuevo[0].turno.codigo == asignaciones[3].turno.codigo
    assert roster_nuevo[3].turno.codigo == asignaciones[0].turno.codigo