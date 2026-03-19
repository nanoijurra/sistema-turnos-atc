from datetime import date, timedelta

from src.models import Asignacion, crear_esquema_8h


def crear_escenario_v1_basico() -> list[Asignacion]:
    """
    Escenario básico de ejemplo usando el esquema clásico de 3 turnos de 8 horas.

    Este escenario no valida nada por sí mismo.
    Solo construye una secuencia simple de asignaciones para pruebas iniciales.
    """
    esquema = crear_esquema_8h()

    turno_a = esquema.obtener_turno("A")
    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")

    fecha_base = date(2026, 3, 1)

    asignaciones = [
        Asignacion(fecha=fecha_base + timedelta(days=0), turno=turno_a),
        Asignacion(fecha=fecha_base + timedelta(days=1), turno=turno_b),
        Asignacion(fecha=fecha_base + timedelta(days=2), turno=turno_c),
    ]

    return asignaciones