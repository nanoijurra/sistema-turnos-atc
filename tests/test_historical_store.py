from src.historical_store import (
    init_historical_store,
    obtener_historial_controlador,
    incrementar_beneficio_controlador,
    obtener_historial_para_controladores,
)


def test_obtener_historial_controlador_devuelve_neutro_si_no_existe():
    init_historical_store()

    resultado = obtener_historial_controlador("CTRL_TEST_NEUTRO")

    assert resultado["beneficios_recientes"] == 0


def test_incrementar_beneficio_controlador_persiste_incremento():
    init_historical_store()

    nombre = "CTRL_TEST_INCREMENTO"

    incrementar_beneficio_controlador(nombre)

    resultado = obtener_historial_controlador(nombre)

    assert resultado["beneficios_recientes"] == 1


def test_incrementar_beneficio_controlador_acumula():
    init_historical_store()

    nombre = "CTRL_TEST_ACUMULA"

    incrementar_beneficio_controlador(nombre)
    incrementar_beneficio_controlador(nombre)

    resultado = obtener_historial_controlador(nombre)

    assert resultado["beneficios_recientes"] == 2


def test_obtener_historial_para_controladores_devuelve_formato_compatible():
    init_historical_store()

    incrementar_beneficio_controlador("CTRL_A")

    resultado = obtener_historial_para_controladores(["CTRL_A", "CTRL_B"])

    assert resultado["CTRL_A"]["beneficios_recientes"] == 1
    assert resultado["CTRL_B"]["beneficios_recientes"] == 0