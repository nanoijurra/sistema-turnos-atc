from datetime import date, timedelta

from src.models import Asignacion, Controlador, SwapRequest, crear_esquema_8h
from src.simulator import (
    explorar_candidatos_acotados,
    explorar_swaps_entre_controladores,
    explorar_y_evaluar_candidatos_con_prefiltro,
)


def _crear_asignaciones():
    esquema = crear_esquema_8h()
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")
    controlador_a = Controlador("ATC_A")
    controlador_b = Controlador("ATC_B")
    fecha_base = date(2026, 3, 1)

    return [
        Asignacion(fecha_base, turno_b, controlador_a),
        Asignacion(fecha_base, turno_c, controlador_b),
        Asignacion(fecha_base - timedelta(days=1), turno_b, controlador_b),
        Asignacion(fecha_base + timedelta(days=1), turno_c, controlador_b),
    ]


def test_explorar_y_evaluar_candidatos_con_prefiltro_devuelve_lista():
    asignaciones = _crear_asignaciones()

    resultado = explorar_y_evaluar_candidatos_con_prefiltro(asignaciones[0], asignaciones)

    assert isinstance(resultado, list)


def test_explorar_y_evaluar_candidatos_con_prefiltro_same_day_funciona():
    asignaciones = _crear_asignaciones()

    resultado = explorar_y_evaluar_candidatos_con_prefiltro(
        asignaciones[0],
        asignaciones,
        modo="same_day",
    )

    assert len(resultado) == 1
    assert resultado[0]["swap"] == {"idx_a": 0, "idx_b": 1}


def test_explorar_y_evaluar_candidatos_con_prefiltro_future_funciona():
    asignaciones = _crear_asignaciones()

    candidatos_future = explorar_candidatos_acotados(
        asignaciones[0],
        asignaciones,
        modo="future",
    )
    resultado = explorar_y_evaluar_candidatos_con_prefiltro(
        asignaciones[0],
        asignaciones,
        modo="future",
    )

    assert asignaciones[1] in candidatos_future
    assert asignaciones[3] in candidatos_future
    assert len(resultado) == 2


def test_explorar_y_evaluar_candidatos_con_prefiltro_usa_prefilter_antes_de_evaluar(monkeypatch):
    asignaciones = _crear_asignaciones()
    llamadas = []

    def fake_prefilter(asignacion_origen, candidatos, asignaciones):
        llamadas.append(("prefilter", len(candidatos)))
        return candidatos[:1]

    def fake_evaluar_swap(asignaciones, idx_a, idx_b, config_file="config_equilibrado.json"):
        llamadas.append(("evaluar", idx_a, idx_b))
        return {
            "swap": {"idx_a": idx_a, "idx_b": idx_b},
            "clasificacion": "RECHAZABLE",
            "valido_nuevo": False,
            "delta_hard": 0,
            "delta_total_violaciones": 0,
            "impacto": 0,
        }

    monkeypatch.setattr("src.simulator.filter_technically_plausible_candidates", fake_prefilter)
    monkeypatch.setattr("src.simulator.evaluar_swap", fake_evaluar_swap)

    resultado = explorar_y_evaluar_candidatos_con_prefiltro(asignaciones[0], asignaciones)

    assert isinstance(resultado, list)
    assert llamadas[0][0] == "prefilter"
    assert llamadas[1][0] == "evaluar"
    assert len(resultado) == 1


def test_explorar_y_evaluar_candidatos_con_prefiltro_no_rompe_simulator_existente():
    asignaciones = _crear_asignaciones()

    ranking_existente = explorar_swaps_entre_controladores(asignaciones, limite=1)

    assert isinstance(ranking_existente, list)


def test_explorar_y_evaluar_candidatos_con_prefiltro_no_crea_requests_ni_decide():
    asignaciones = _crear_asignaciones()

    resultado = explorar_y_evaluar_candidatos_con_prefiltro(asignaciones[0], asignaciones)

    assert resultado
    assert all(not isinstance(item, SwapRequest) for item in resultado)
    assert all("decision" not in item for item in resultado)


def test_explorar_y_evaluar_candidatos_con_prefiltro_mantiene_clasificacion_tecnica_real_en_salida():
    asignaciones = _crear_asignaciones()

    resultado = explorar_y_evaluar_candidatos_con_prefiltro(
        asignaciones[0],
        asignaciones,
        modo="same_day",
    )

    assert resultado
    assert resultado[0]["clasificacion"] in {"BENEFICIOSO", "ACEPTABLE", "RECHAZABLE"}
