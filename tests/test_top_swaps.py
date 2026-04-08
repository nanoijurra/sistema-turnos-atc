from src.simulator import obtener_top_swaps


def test_obtener_top_swaps_limita_resultados(monkeypatch):
    evaluaciones_mock = [
        {
            "swap": {"idx_a": i, "idx_b": i + 1},
            "clasificacion": "BENEFICIOSO",
            "valido_nuevo": True,
            "delta_hard": 0,
            "delta_total_violaciones": -1,
            "impacto": 10,
        }
        for i in range(10)
    ]

    def fake_explorar(*args, **kwargs):
        return evaluaciones_mock

    monkeypatch.setattr(
        "src.simulator.explorar_swaps_entre_controladores",
        fake_explorar
    )

    resultado = obtener_top_swaps(asignaciones=[], limite=3)

    assert len(resultado) == 3