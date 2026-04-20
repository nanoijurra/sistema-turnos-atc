from datetime import datetime

from src.historical_store import init_historical_store, listar_eventos_equidad_controlador
from src.historical_tracking import actualizar_historial_beneficios


def test_actualizar_historial_beneficios_no_hace_nada_sin_evaluacion():
    init_historical_store()

    historial = {"ATC_A": {"beneficios_recientes": 2}}

    resultado = actualizar_historial_beneficios(
        historial_por_controlador=historial,
        evaluacion=None,
    )

    assert resultado["ATC_A"]["beneficios_recientes"] == 2


def test_actualizar_historial_beneficios_incrementa_controlador_beneficiado():
    init_historical_store()

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
        swap_request_id="REQ-TRACK-1",
        fecha_evento=datetime(2026, 4, 7, 13, 0, 0),
    )

    assert resultado["ATC_A"]["beneficios_recientes"] == 2

    eventos = listar_eventos_equidad_controlador("ATC_A")
    assert len(eventos) >= 1


def test_actualizar_historial_beneficios_crea_controlador_si_no_existe():
    init_historical_store()

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
        swap_request_id="REQ-TRACK-2",
        fecha_evento=datetime(2026, 4, 7, 14, 0, 0),
    )

    assert resultado["ATC_B"]["beneficios_recientes"] == 1