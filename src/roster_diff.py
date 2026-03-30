def comparar_rosters(roster_a, roster_b) -> dict:
    cambios = []

    asignaciones_a = roster_a.asignaciones
    asignaciones_b = roster_b.asignaciones

    if len(asignaciones_a) != len(asignaciones_b):
        raise ValueError("Los rosters no tienen la misma cantidad de asignaciones")

    for i, (a, b) in enumerate(zip(asignaciones_a, asignaciones_b)):
        turno_a = a.turno.codigo
        turno_b = b.turno.codigo

        if turno_a != turno_b:
            cambios.append(
                {
                    "idx": i,
                    "controlador": a.controlador.nombre if a.controlador else None,
                    "antes": turno_a,
                    "despues": turno_b,
                }
            )

    return {
        "cambios": cambios,
        "total_cambios": len(cambios),
    }

def impacto_por_controlador(roster_a, roster_b) -> dict:
    impacto = {}

    asignaciones_a = roster_a.asignaciones
    asignaciones_b = roster_b.asignaciones

    for a, b in zip(asignaciones_a, asignaciones_b):
        ctrl = a.controlador.nombre if a.controlador else "SIN_CONTROLADOR"

        turno_a = a.turno.codigo
        turno_b = b.turno.codigo

        if turno_a != turno_b:
            if ctrl not in impacto:
                impacto[ctrl] = []

            impacto[ctrl].append({
                "antes": turno_a,
                "despues": turno_b,
            })

    return impacto