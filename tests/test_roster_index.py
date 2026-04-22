from datetime import date, timedelta

from src.models import Asignacion, Controlador, crear_esquema_8h
from src.roster_index import build_roster_index


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
        Asignacion(fecha_base + timedelta(days=1), turno_b, controlador_a),
        Asignacion(fecha_base + timedelta(days=2), turno_c, controlador_b),
    ]


def test_build_roster_index_construye_by_date_correctamente():
    asignaciones = _crear_asignaciones()

    index = build_roster_index(asignaciones)

    assert index.by_date[asignaciones[0].fecha] == [asignaciones[0], asignaciones[1]]
    assert index.by_date[asignaciones[2].fecha] == [asignaciones[2]]


def test_build_roster_index_construye_by_date_turno_correctamente():
    asignaciones = _crear_asignaciones()

    index = build_roster_index(asignaciones)

    assert index.by_date_turno[(asignaciones[0].fecha, asignaciones[0].turno)] == [
        asignaciones[0],
    ]
    assert index.by_date_turno[(asignaciones[1].fecha, asignaciones[1].turno)] == [
        asignaciones[1],
    ]


def test_build_roster_index_construye_by_controller_correctamente():
    asignaciones = _crear_asignaciones()

    index = build_roster_index(asignaciones)

    assert index.by_controller["ATC_A"] == [asignaciones[0], asignaciones[2]]
    assert index.by_controller["ATC_B"] == [asignaciones[1], asignaciones[3]]


def test_build_roster_index_construye_future_window_correctamente():
    asignaciones = _crear_asignaciones()

    index = build_roster_index(asignaciones)

    assert index.future_window["ATC_A"] == [asignaciones[0], asignaciones[2]]
    assert index.future_window["ATC_B"] == [asignaciones[1], asignaciones[3]]


def test_build_roster_index_no_pierde_ni_duplica_asignaciones():
    asignaciones = _crear_asignaciones()

    index = build_roster_index(asignaciones)

    desde_by_date = [item for items in index.by_date.values() for item in items]
    desde_by_controller = [
        item
        for items in index.by_controller.values()
        for item in items
    ]

    assert desde_by_date == asignaciones
    assert len(desde_by_date) == len(asignaciones)
    assert len(desde_by_controller) == len(asignaciones)
