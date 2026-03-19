from datetime import timedelta

def validar_descanso_minimo(asignaciones, horas_minimas=12):
    for i in range(len(asignaciones) - 1):
        actual = asignaciones[i]
        siguiente = asignaciones[i + 1]

        descanso = siguiente.turno.inicio - actual.turno.fin

        if descanso < timedelta(hours=horas_minimas):
            return False, f"Descanso insuficiente entre {actual.turno.fin} y {siguiente.turno.inicio}"

    return True, "OK"
def validar_secuencia(asignaciones):
    secuencias_prohibidas = [
        ("NOCHE", "MANANA"),
        ("NOCHE", "TARDE"),   # opcional según criterio
    ]

    for i in range(len(asignaciones) - 1):
        actual = asignaciones[i].turno.tipo.name
        siguiente = asignaciones[i + 1].turno.tipo.name

        if (actual, siguiente) in secuencias_prohibidas:
            return False, f"Secuencia prohibida: {actual} → {siguiente}"

    return True, "OK"
def validar_noches_consecutivas(asignaciones, max_noches=3):
    contador = 0

    for asignacion in asignaciones:
        if asignacion.turno.tipo.name == "NOCHE":
            contador += 1
            if contador > max_noches:
                return False, f"Exceso de noches consecutivas: {contador}"
        else:
            contador = 0  # se corta la secuencia

    return True, "OK"