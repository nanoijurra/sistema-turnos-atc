from src.roster_store import (
    guardar_roster,
    obtener_roster,
    obtener_roster_vigente,
    limpiar_rosters,
)
from src.models import RosterVersion
from datetime import datetime


def setup_function():
    limpiar_rosters()


def test_guardar_y_obtener_roster():
    roster = RosterVersion(
        id="v1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
    )

    guardar_roster(roster)

    recuperado = obtener_roster("v1")

    assert recuperado is not None
    assert recuperado.id == "v1"


def test_obtener_roster_vigente():
    r1 = RosterVersion(
        id="v1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=False,
    )

    r2 = RosterVersion(
        id="v2",
        version_number=2,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
    )

    guardar_roster(r1)
    guardar_roster(r2)

    vigente = obtener_roster_vigente()

    assert vigente is not None
    assert vigente.id == "v2"