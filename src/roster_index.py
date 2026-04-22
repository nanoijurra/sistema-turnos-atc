from dataclasses import dataclass
from datetime import date

from src.models import Asignacion, Turno


@dataclass(frozen=True)
class RosterIndex:
    by_date: dict[date, list[Asignacion]]
    by_date_turno: dict[tuple[date, Turno], list[Asignacion]]
    by_controller: dict[str, list[Asignacion]]
    future_window: dict[str, list[Asignacion]]


def build_roster_index(asignaciones: list[Asignacion]) -> RosterIndex:
    by_date: dict[date, list[Asignacion]] = {}
    by_date_turno: dict[tuple[date, Turno], list[Asignacion]] = {}
    by_controller: dict[str, list[Asignacion]] = {}

    for asignacion in asignaciones:
        by_date.setdefault(asignacion.fecha, []).append(asignacion)
        by_date_turno.setdefault(
            (asignacion.fecha, asignacion.turno),
            [],
        ).append(asignacion)

        if asignacion.controlador is None:
            continue

        by_controller.setdefault(
            asignacion.controlador.nombre,
            [],
        ).append(asignacion)

    future_window = {
        controlador: sorted(items, key=lambda item: item.fecha)
        for controlador, items in by_controller.items()
    }

    return RosterIndex(
        by_date=by_date,
        by_date_turno=by_date_turno,
        by_controller=by_controller,
        future_window=future_window,
    )
