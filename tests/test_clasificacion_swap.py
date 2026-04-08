from src.simulator import clasificar_swap


def test_clasificar_swap_es_rechazable_si_roster_nuevo_no_es_valido():
    evaluacion = {
        "valido_nuevo": False,
        "delta_hard": 0,
        "delta_total_violaciones": 0,
        "resumen_por_controlador_original": {},
        "resumen_por_controlador_nuevo": {},
    }

    assert clasificar_swap(evaluacion) == "RECHAZABLE"


def test_clasificar_swap_es_rechazable_si_empeora_un_controlador():
    evaluacion = {
        "valido_nuevo": True,
        "delta_hard": 0,
        "delta_total_violaciones": 0,
        "resumen_por_controlador_original": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 0},
            },
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 2},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 0},
            },
        },
    }

    assert clasificar_swap(evaluacion) == "RECHAZABLE"


def test_clasificar_swap_es_beneficioso_si_mejora_global_sin_perjudicar():
    evaluacion = {
        "valido_nuevo": True,
        "delta_hard": 0,
        "delta_total_violaciones": -1,
        "resumen_por_controlador_original": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
        },
    }

    assert clasificar_swap(evaluacion) == "BENEFICIOSO"


def test_clasificar_swap_es_aceptable_si_no_empeora_ni_mejora():
    evaluacion = {
        "valido_nuevo": True,
        "delta_hard": 0,
        "delta_total_violaciones": 0,
        "resumen_por_controlador_original": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 0},
            },
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 0},
            },
        },
    }

    assert clasificar_swap(evaluacion) == "ACEPTABLE"
    
def test_clasificar_swap_es_beneficioso_si_hay_mejora_global_y_nadie_empeora():
    evaluacion = {
        "valido_nuevo": True,
        "delta_hard": -1,
        "delta_total_violaciones": 0,
        "resumen_por_controlador_original": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 1, "total": 2},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
        },
        "resumen_por_controlador_nuevo": {
            "ATC_A": {
                "valido": True,
                "violaciones": {"hard": 1, "total": 2},
            },
            "ATC_B": {
                "valido": True,
                "violaciones": {"hard": 0, "total": 1},
            },
        },
    }

    assert clasificar_swap(evaluacion) == "BENEFICIOSO"    