from src.simulator import generar_reporte_swaps


def test_generar_reporte_swaps_no_vacio(monkeypatch):
    fake_top = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "BENEFICIOSO",
            "impacto": 10,
            "recomendacion": "Mejora general sin impacto negativo.",
        }
    ]

    def fake_top_swaps(*args, **kwargs):
        return fake_top

    monkeypatch.setattr(
        "src.simulator.obtener_top_swaps",
        fake_top_swaps,
    )

    class Dummy:
        def __init__(self):
            self.controlador = type("C", (), {"nombre": "ATC_A"})()
            self.fecha = "2026-04-01"
            self.turno = type("T", (), {"codigo": "A"})()

    asignaciones = [Dummy(), Dummy()]

    reporte = generar_reporte_swaps(asignaciones, limite=1)

    assert "TOP 1 SWAPS RECOMENDADOS" in reporte
    assert "ATC_A" in reporte
    assert "Beneficioso" in reporte


def test_generar_reporte_swaps_tolera_datos_incompletos(monkeypatch):
    fake_top = [
        {
            "swap": {"idx_a": 0, "idx_b": 1},
            "clasificacion": "DESCONOCIDA",
        }
    ]

    def fake_top_swaps(*args, **kwargs):
        return fake_top

    monkeypatch.setattr(
        "src.simulator.obtener_top_swaps",
        fake_top_swaps,
    )

    class Dummy:
        def __init__(self, controlador=None, fecha=None, turno=None):
            self.controlador = controlador
            self.fecha = fecha
            self.turno = turno

    asignaciones = [
        Dummy(controlador=None, fecha=None, turno=None),
        Dummy(controlador=None, fecha=None, turno=None),
    ]

    reporte = generar_reporte_swaps(asignaciones, limite=1)

    assert "SIN_CTRL" in reporte
    assert "SIN_FECHA" in reporte
    assert "SIN_TURNO" in reporte
    assert "Clasificacion desconocida" in reporte