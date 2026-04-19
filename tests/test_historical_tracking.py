from src.historical_tracking import actualizar_historial_beneficios


def test_actualizar_historial_beneficios_no_hace_nada_sin_evaluacion():
    historial = {"ATC_A": {"beneficios_recientes": 2}}

    resultado = actualizar_historial_beneficios(
        historial_por_controlador=historial,
        evaluacion=None,
    )

    assert resultado["ATC_A"]["beneficios_recientes"] == 2


def test_actualizar_historial_beneficios_incrementa_controlador_beneficiado():
    historial = {"ATC_A": {"beneficios_recientes": 1}}

    evaluacion = {
        "resumen_por_controlador_original": {
            "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
        },
    }

    resultado = actualizar_historial_beneficios(
        historial_por_controlador=historial,
        evaluacion=evaluacion,
    )

    assert resultado["ATC_A"]["beneficios_recientes"] == 2


def test_actualizar_historial_beneficios_crea_controlador_si_no_existe():
    historial = {}

    evaluacion = {
        "resumen_por_controlador_original": {
            "ATC_B": {"valido": True, "violaciones": {"hard": 0, "total": 3}},
        },
        "resumen_por_controlador_nuevo": {
            "ATC_B": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
        },
    }

    resultado = actualizar_historial_beneficios(
        historial_por_controlador=historial,
        evaluacion=evaluacion,
    )

    assert resultado["ATC_B"]["beneficios_recientes"] == 1