from datetime import date, timedelta

from src.models import Asignacion, crear_esquema_8h


def crear_escenario() -> list[Asignacion]:
    """
    Escenario de prueba con 4 noches consecutivas.

    Está pensado para futuros validators de noches consecutivas,
    no para validar por sí mismo.
    """
    esquema = crear_esquema_8h()
    turno_noche = esquema.obtener_turno("C")

    fecha_base = date(2026, 3, 1)

    return [
        Asignacion(fecha=fecha_base + timedelta(days=0), turno=turno_noche),
        Asignacion(fecha=fecha_base + timedelta(days=1), turno=turno_noche),
        Asignacion(fecha=fecha_base + timedelta(days=2), turno=turno_noche),
        Asignacion(fecha=fecha_base + timedelta(days=3), turno=turno_noche),
    ]