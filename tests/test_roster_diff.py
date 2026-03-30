def test_comparar_rosters_detecta_cambios():
    from src.roster_diff import comparar_rosters
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.engine import crear_roster_version_inicial, crear_nueva_version_desde_roster_vigente
    from src.roster_store import limpiar_rosters

    limpiar_rosters()

    asignaciones = crear_escenario()
    v1 = crear_roster_version_inicial(asignaciones)

    # simular swap manual simple
    nuevas = asignaciones.copy()
    nuevas[0], nuevas[3] = nuevas[3], nuevas[0]

    v2 = crear_nueva_version_desde_roster_vigente(nuevas)

    diff = comparar_rosters(v1, v2)

    assert diff["total_cambios"] > 0

def test_impacto_por_controlador():
    from src.roster_diff import impacto_por_controlador
    from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
    from src.engine import crear_roster_version_inicial, crear_nueva_version_desde_roster_vigente
    from src.roster_store import limpiar_rosters

    limpiar_rosters()

    asignaciones = crear_escenario()
    v1 = crear_roster_version_inicial(asignaciones)

    nuevas = asignaciones.copy()
    nuevas[0], nuevas[3] = nuevas[3], nuevas[0]

    v2 = crear_nueva_version_desde_roster_vigente(nuevas)

    impacto = impacto_por_controlador(v1, v2)

    assert len(impacto) > 0