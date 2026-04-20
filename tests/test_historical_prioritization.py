from datetime import datetime, timedelta

from src.historical_store import (
    init_historical_store,
    registrar_evento_beneficio_controlador,
)
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

    assert calcular_score_equidad_swap(evaluacion, None) == 0.0


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
        "ATC_A": {"beneficios_recientes": 3.0},
    }

    assert calcular_score_equidad_swap(evaluacion, historial) == -3.0


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

    historial = {"ATC_A": {"beneficios_recientes": 1.0}}

    resultado = priorizar_por_equidad_historica(evaluaciones, historial)

    assert resultado[0]["clasificacion"] == "BENEFICIOSO"
    assert resultado[0]["score_equidad"] == -1.0


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
        "ATC_A": {"beneficios_recientes": 3.0},
        "ATC_B": {"beneficios_recientes": 0.0},
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
        "ATC_A": {"beneficios_recientes": 5.0},
        "ATC_B": {"beneficios_recientes": 0.0},
    }

    resultado = priorizar_por_equidad_historica(evaluaciones, historial)

    assert resultado[0]["clasificacion"] == "ACEPTABLE"
    assert resultado[1]["clasificacion"] == "RECHAZABLE"


def test_priorizar_por_equidad_historica_lee_historial_desde_sqlite_si_no_se_provee():
    init_historical_store()
    referencia = datetime(2026, 4, 7, 12, 0, 0)

    registrar_evento_beneficio_controlador(
        nombre="ATC_A",
        swap_request_id="REQ-A1",
        fecha_evento=referencia - timedelta(days=5),
    )
    registrar_evento_beneficio_controlador(
        nombre="ATC_A",
        swap_request_id="REQ-A2",
        fecha_evento=referencia - timedelta(days=10),
    )
    registrar_evento_beneficio_controlador(
        nombre="ATC_A",
        swap_request_id="REQ-A3",
        fecha_evento=referencia - timedelta(days=15),
    )

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

    resultado = priorizar_por_equidad_historica(
        evaluaciones,
        historial_por_controlador=None,
        ventana_dias=90,
        fecha_referencia=referencia,
    )

    assert resultado[0]["swap"] == {"idx_a": 2, "idx_b": 3}
    assert resultado[1]["swap"] == {"idx_a": 0, "idx_b": 1}