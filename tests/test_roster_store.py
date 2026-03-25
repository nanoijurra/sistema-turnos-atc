from datetime import datetime

import pytest

from src.models import RosterVersion
from src.roster_store import (
    guardar_roster,
    obtener_roster,
    obtener_roster_vigente,
    listar_rosters_vigentes,
    validar_unico_roster_vigente,
    desactivar_roster_vigente_actual,
    limpiar_rosters,
)


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


def test_validar_unico_roster_vigente_falla_si_hay_dos():
    r1 = RosterVersion(
        id="v1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
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

    with pytest.raises(ValueError, match="más de un roster vigente"):
        validar_unico_roster_vigente()


def test_obtener_roster_vigente_falla_si_hay_dos():
    r1 = RosterVersion(
        id="v1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
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

    with pytest.raises(ValueError, match="más de un roster vigente"):
        obtener_roster_vigente()


def test_desactivar_roster_vigente_actual():
    r1 = RosterVersion(
        id="v1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
    )

    guardar_roster(r1)

    desactivado = desactivar_roster_vigente_actual()

    assert desactivado is not None
    assert desactivado.id == "v1"
    assert desactivado.vigente is False
    assert listar_rosters_vigentes() == []