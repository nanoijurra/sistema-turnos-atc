from src.simulator import explorar_swaps


def test_explorar_swaps_prioriza_beneficioso_sobre_aceptable(monkeypatch):
    evaluaciones_mock = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "ACEPTABLE",
            "valido_nuevo": True,
            "delta_hard": 0,
            "delta_total_violaciones": 0,
            "impacto": 10,
        },
        {
            "swap": {"idx_a": 2, "idx_b": 3},
            "clasificacion": "BENEFICIOSO",
            "valido_nuevo": True,
            "delta_hard": 0,
            "delta_total_violaciones": -1,
            "impacto": 5,
        },
    ]

    def fake_evaluar_swap(**kwargs):
        idx_a = kwargs["idx_a"]
        idx_b = kwargs["idx_b"]

        for evaluacion in evaluaciones_mock:
            swap = evaluacion["swap"]
            if swap["idx_a"] == idx_a and swap["idx_b"] == idx_b:
                return evaluacion

        raise AssertionError("Swap no esperado en test")

    monkeypatch.setattr("src.simulator.evaluar_swap", fake_evaluar_swap)

    resultado = explorar_swaps(
        asignaciones=[],
        pares=[(0, 1), (2, 3)],
    )

    assert resultado[0]["clasificacion"] == "BENEFICIOSO"
    assert resultado[1]["clasificacion"] == "ACEPTABLE"


def test_explorar_swaps_prioriza_aceptable_sobre_rechazable(monkeypatch):
    evaluaciones_mock = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "RECHAZABLE",
            "valido_nuevo": False,
            "delta_hard": 1,
            "delta_total_violaciones": 2,
            "impacto": 100,
        },
        {
            "swap": {"idx_a": 2, "idx_b": 3},
            "clasificacion": "ACEPTABLE",
            "valido_nuevo": True,
            "delta_hard": 0,
            "delta_total_violaciones": 0,
            "impacto": 1,
        },
    ]

    def fake_evaluar_swap(**kwargs):
        idx_a = kwargs["idx_a"]
        idx_b = kwargs["idx_b"]

        for evaluacion in evaluaciones_mock:
            swap = evaluacion["swap"]
            if swap["idx_a"] == idx_a and swap["idx_b"] == idx_b:
                return evaluacion

        raise AssertionError("Swap no esperado en test")

    monkeypatch.setattr("src.simulator.evaluar_swap", fake_evaluar_swap)

    resultado = explorar_swaps(
        asignaciones=[],
        pares=[(0, 1), (2, 3)],
    )

    assert resultado[0]["clasificacion"] == "ACEPTABLE"
    assert resultado[1]["clasificacion"] == "RECHAZABLE"


def test_explorar_swaps_prioriza_mejor_delta_dentro_de_misma_clasificacion(monkeypatch):
    evaluaciones_mock = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "BENEFICIOSO",
            "valido_nuevo": True,
            "delta_hard": 0,
            "delta_total_violaciones": -1,
            "impacto": 20,
        },
        {
            "swap": {"idx_a": 2, "idx_b": 3},
            "clasificacion": "BENEFICIOSO",
            "valido_nuevo": True,
            "delta_hard": -1,
            "delta_total_violaciones": -2,
            "impacto": 10,
        },
    ]

    def fake_evaluar_swap(**kwargs):
        idx_a = kwargs["idx_a"]
        idx_b = kwargs["idx_b"]

        for evaluacion in evaluaciones_mock:
            swap = evaluacion["swap"]
            if swap["idx_a"] == idx_a and swap["idx_b"] == idx_b:
                return evaluacion

        raise AssertionError("Swap no esperado en test")

    monkeypatch.setattr("src.simulator.evaluar_swap", fake_evaluar_swap)

    resultado = explorar_swaps(
        asignaciones=[],
        pares=[(0, 1), (2, 3)],
    )

    assert resultado[0]["swap"] == {"idx_a": 2, "idx_b": 3}
    assert resultado[1]["swap"] == {"idx_a": 0, "idx_b": 1}