from src.models import RosterVersion


_ROSTERS: dict[str, RosterVersion] = {}


def guardar_roster(roster: RosterVersion) -> RosterVersion:
    _ROSTERS[roster.id] = roster
    return roster


def obtener_roster(roster_id: str) -> RosterVersion | None:
    return _ROSTERS.get(roster_id)


def listar_rosters() -> list[RosterVersion]:
    return list(_ROSTERS.values())


def listar_rosters_vigentes() -> list[RosterVersion]:
    return [r for r in _ROSTERS.values() if r.vigente]


def validar_unico_roster_vigente() -> None:
    vigentes = listar_rosters_vigentes()
    if len(vigentes) > 1:
        ids = [r.id for r in vigentes]
        raise ValueError(f"Hay más de un roster vigente al mismo tiempo: {ids}")


def obtener_roster_vigente() -> RosterVersion | None:
    vigentes = listar_rosters_vigentes()

    if not vigentes:
        return None

    if len(vigentes) > 1:
        ids = [r.id for r in vigentes]
        raise ValueError(f"Hay más de un roster vigente al mismo tiempo: {ids}")

    return vigentes[0]


def desactivar_roster_vigente_actual() -> RosterVersion | None:
    vigente = obtener_roster_vigente()

    if vigente is None:
        return None

    vigente.vigente = False
    guardar_roster(vigente)
    return vigente


def limpiar_rosters() -> None:
    _ROSTERS.clear()