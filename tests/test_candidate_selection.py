from __future__ import annotations

from datetime import date

from src.candidate_selection import seleccionar_candidatos
from src.models import Asignacion, Controlador, crear_esquema_8h


def _asignacion(fecha: date, turno_codigo: str, controlador_nombre: str) -> Asignacion:
    turno = crear_esquema_8h().obtener_turno(turno_codigo)
    return Asignacion(
        fecha=fecha,
        turno=turno,
        controlador=Controlador(controlador_nombre),
    )


def test_devuelve_lista() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidato = _asignacion(date(2026, 3, 1), "B", "ATC_002")

    resultado = seleccionar_candidatos(origen, [candidato], [origen, candidato])

    assert isinstance(resultado, list)


def test_si_candidatos_menor_o_igual_top_n_devuelve_todos() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidatos = [
        _asignacion(date(2026, 3, 1), "B", "ATC_002"),
        _asignacion(date(2026, 3, 2), "C", "ATC_003"),
    ]

    resultado = seleccionar_candidatos(origen, candidatos, [origen] + candidatos, top_n=5)

    assert len(resultado) == len(candidatos)
    assert set(resultado) == set(candidatos)


def test_si_candidatos_mayor_top_n_recorta() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidatos = [
        _asignacion(date(2026, 3, dia), "B", f"ATC_{dia:03d}")
        for dia in range(1, 6)
    ]

    resultado = seleccionar_candidatos(origen, candidatos, [origen] + candidatos, top_n=3)

    assert len(resultado) == 3


def test_prioriza_mismo_dia() -> None:
    origen = _asignacion(date(2026, 3, 10), "A", "ATC_001")
    otro_dia_cercano = _asignacion(date(2026, 3, 9), "B", "ATC_002")
    mismo_dia = _asignacion(date(2026, 3, 10), "C", "ATC_003")

    resultado = seleccionar_candidatos(
        origen,
        [otro_dia_cercano, mismo_dia],
        [origen, otro_dia_cercano, mismo_dia],
    )

    assert resultado[0] is mismo_dia


def test_prioriza_menor_distancia_temporal() -> None:
    origen = _asignacion(date(2026, 3, 10), "A", "ATC_001")
    lejano = _asignacion(date(2026, 3, 20), "B", "ATC_002")
    cercano = _asignacion(date(2026, 3, 12), "C", "ATC_003")

    resultado = seleccionar_candidatos(
        origen,
        [lejano, cercano],
        [origen, lejano, cercano],
    )

    assert resultado[0] is cercano


def test_resultado_deterministico() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidatos = [
        _asignacion(date(2026, 3, 2), "C", "ATC_003"),
        _asignacion(date(2026, 3, 1), "B", "ATC_002"),
        _asignacion(date(2026, 3, 3), "A", "ATC_004"),
    ]

    primero = seleccionar_candidatos(origen, candidatos, [origen] + candidatos)
    segundo = seleccionar_candidatos(origen, candidatos, [origen] + candidatos)

    assert primero == segundo


def test_no_devuelve_swap_request() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidato = _asignacion(date(2026, 3, 1), "B", "ATC_002")

    resultado = seleccionar_candidatos(origen, [candidato], [origen, candidato])

    assert all(isinstance(item, Asignacion) for item in resultado)


def test_no_clasifica() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidato = _asignacion(date(2026, 3, 1), "B", "ATC_002")

    resultado = seleccionar_candidatos(origen, [candidato], [origen, candidato])

    assert not hasattr(resultado[0], "clasificacion")


def test_no_decide() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidato = _asignacion(date(2026, 3, 1), "B", "ATC_002")

    resultado = seleccionar_candidatos(origen, [candidato], [origen, candidato])

    assert not hasattr(resultado[0], "decision_sugerida")


def test_no_modifica_candidatos() -> None:
    origen = _asignacion(date(2026, 3, 1), "A", "ATC_001")
    candidatos = [
        _asignacion(date(2026, 3, 3), "B", "ATC_003"),
        _asignacion(date(2026, 3, 1), "C", "ATC_002"),
    ]
    candidatos_originales = list(candidatos)

    resultado = seleccionar_candidatos(origen, candidatos, [origen] + candidatos)

    assert candidatos == candidatos_originales
    assert resultado[0] is candidatos[1]
    assert resultado[1] is candidatos[0]
