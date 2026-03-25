from src.models import RosterVersion


_ROSTERS: dict[str, RosterVersion] = {}


def guardar_roster(roster: RosterVersion) -> RosterVersion:
    _ROSTERS[roster.id] = roster
    return roster


def obtener_roster(roster_id: str) -> RosterVersion | None:
    return _ROSTERS.get(roster_id)


def listar_rosters() -> list[RosterVersion]:
    return list(_ROSTERS.values())


def obtener_roster_vigente() -> RosterVersion | None:
    for r in _ROSTERS.values():
        if r.vigente:
            return r
    return None


def limpiar_rosters() -> None:
    _ROSTERS.clear()