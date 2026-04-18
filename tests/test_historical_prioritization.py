from src.historical_prioritization import (
    calcular_score_equidad_swap,
    priorizar_por_equidad_historica,
)


def test_calcular_score_equidad_swap_es_neutro_sin_historial():
    evaluacion = {
        "resumen_por_controlador_original": {
            "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
        },
    }

    assert calcular_score_equidad_swap(evaluacion, None) == 0


def test_calcular_score_equidad_swap_penaliza_controlador_ya_beneficiado():
    evaluacion = {
        "resumen_por_controlador_original": {
            "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
        },
    }

    historial = {
        "ATC_A": {"beneficios_recientes": 3},
    }

    assert calcular_score_equidad_swap(evaluacion, historial) == -3


def test_priorizar_por_equidad_historica_no_cambia_clasificacion():
    evaluaciones = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "BENEFICIOSO",
            "resumen_por_controlador_original": {
                "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
            },
            "resumen_por_controlador_nuevo": {
                "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
            },
        }
    ]

    historial = {"ATC_A": {"beneficios_recientes": 1}}

    resultado = priorizar_por_equidad_historica(evaluaciones, historial)

    assert resultado[0]["clasificacion"] == "BENEFICIOSO"
    assert resultado[0]["score_equidad"] == -1


def test_priorizar_por_equidad_historica_reordena_dentro_de_misma_clasificacion():
    evaluaciones = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "BENEFICIOSO",
            "resumen_por_controlador_original": {
                "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
            },
            "resumen_por_controlador_nuevo": {
                "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
            },
        },
        {
            "swap": {"idx_a": 2, "idx_b": 3},
            "clasificacion": "BENEFICIOSO",
            "resumen_por_controlador_original": {
                "ATC_B": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
            },
            "resumen_por_controlador_nuevo": {
                "ATC_B": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
            },
        },
    ]

    historial = {
        "ATC_A": {"beneficios_recientes": 3},
        "ATC_B": {"beneficios_recientes": 0},
    }

    resultado = priorizar_por_equidad_historica(evaluaciones, historial)

    assert resultado[0]["swap"] == {"idx_a": 2, "idx_b": 3}
    assert resultado[1]["swap"] == {"idx_a": 0, "idx_b": 1}


def test_priorizar_por_equidad_historica_no_promueve_rechazables():
    evaluaciones = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "ACEPTABLE",
            "resumen_por_controlador_original": {
                "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
            },
            "resumen_por_controlador_nuevo": {
                "ATC_A": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
            },
        },
        {
            "swap": {"idx_a": 2, "idx_b": 3},
            "clasificacion": "RECHAZABLE",
            "resumen_por_controlador_original": {
                "ATC_B": {"valido": True, "violaciones": {"hard": 0, "total": 2}},
            },
            "resumen_por_controlador_nuevo": {
                "ATC_B": {"valido": True, "violaciones": {"hard": 0, "total": 1}},
            },
        },
    ]

    historial = {
        "ATC_A": {"beneficios_recientes": 5},
        "ATC_B": {"beneficios_recientes": 0},
    }

    resultado = priorizar_por_equidad_historica(evaluaciones, historial)

    assert resultado[0]["clasificacion"] == "ACEPTABLE"
    assert resultado[1]["clasificacion"] == "RECHAZABLE"