from datetime import date, timedelta

from src.models import Asignacion, crear_esquema_8h


def crear_escenario() -> list[Asignacion]:
    """
    Escenario de fatiga:

    - 3 noches consecutivas
    - seguido de un turno tarde con descanso insuficiente

    Diseñado para disparar la regla de descanso mínimo.
    """
    esquema = crear_esquema_8h()

    turno_noche = esquema.obtener_turno("C")
    turno_tarde = esquema.obtener_turno("B")

    fecha_base = date(2026, 3, 1)

    return [
        # 3 noches consecutivas
        Asignacion(fecha=fecha_base + timedelta(days=0), turno=turno_noche),
        Asignacion(fecha=fecha_base + timedelta(days=1), turno=turno_noche),
        Asignacion(fecha=fecha_base + timedelta(days=2), turno=turno_noche),

        # transición a tarde (descanso insuficiente)
        Asignacion(fecha=fecha_base + timedelta(days=3), turno=turno_tarde),
    ]