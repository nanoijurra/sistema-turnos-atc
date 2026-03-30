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
    
def test_obtener_roster_por_version_number():
    from datetime import datetime
    from src.models import RosterVersion
    from src.roster_store import (
        guardar_roster,
        obtener_roster_por_version_number,
        limpiar_rosters,
    )

    limpiar_rosters()

    r1 = RosterVersion(
        id="r1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=False,
        base_version_id=None,
        regimen_horario="6H",
    )
    r2 = RosterVersion(
        id="r2",
        version_number=2,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
        base_version_id="r1",
        regimen_horario="6H",
    )

    guardar_roster(r1)
    guardar_roster(r2)

    encontrado = obtener_roster_por_version_number(2)

    assert encontrado is not None
    assert encontrado.id == "r2"
    assert encontrado.version_number == 2

def test_listar_rosters_ordenados_por_version():
    from datetime import datetime
    from src.models import RosterVersion
    from src.roster_store import (
        guardar_roster,
        listar_rosters_ordenados_por_version,
        limpiar_rosters,
    )

    limpiar_rosters()

    r2 = RosterVersion(
        id="r2",
        version_number=2,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
        base_version_id="r1",
        regimen_horario="6H",
    )
    r1 = RosterVersion(
        id="r1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=False,
        base_version_id=None,
        regimen_horario="6H",
    )

    guardar_roster(r2)
    guardar_roster(r1)

    rosters = listar_rosters_ordenados_por_version()

    assert [r.version_number for r in rosters] == [1, 2]

def test_listar_rosters_hijos():
    from datetime import datetime
    from src.models import RosterVersion
    from src.roster_store import (
        guardar_roster,
        listar_rosters_hijos,
        limpiar_rosters,
    )

    limpiar_rosters()

    base = RosterVersion(
        id="r1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=False,
        base_version_id=None,
        regimen_horario="6H",
    )

    hijo = RosterVersion(
        id="r2",
        version_number=2,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
        base_version_id="r1",
        regimen_horario="6H",
    )

    guardar_roster(base)
    guardar_roster(hijo)

    hijos = listar_rosters_hijos("r1")

    assert len(hijos) == 1
    assert hijos[0].id == "r2"

def test_obtener_roster_padre():
    from datetime import datetime
    from src.models import RosterVersion
    from src.roster_store import (
        guardar_roster,
        obtener_roster_padre,
        limpiar_rosters,
    )

    limpiar_rosters()

    base = RosterVersion(
        id="r1",
        version_number=1,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=False,
        base_version_id=None,
        regimen_horario="6H",
    )

    hijo = RosterVersion(
        id="r2",
        version_number=2,
        created_at=datetime.now(),
        asignaciones=[],
        vigente=True,
        base_version_id="r1",
        regimen_horario="6H",
    )

    guardar_roster(base)
    guardar_roster(hijo)

    padre = obtener_roster_padre(hijo)

    assert padre is not None
    assert padre.id == "r1"

