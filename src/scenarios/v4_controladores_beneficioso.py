from datetime import date, timedelta

from src.models import Asignacion, Controlador, crear_esquema_8h


def crear_escenario() -> list[Asignacion]:
    """
    Escenario donde un swap entre controladores elimina una violación hard
    y deja el roster mejor que antes.
    """
    esquema = crear_esquema_8h()

    turno_b = esquema.obtener_turno("B")
    turno_c = esquema.obtener_turno("C")

    controlador_a = Controlador(nombre="ATC_A")
    controlador_b = Controlador(nombre="ATC_B")

    fecha_base = date(2026, 3, 1)

    return [
        Asignacion(
            fecha=fecha_base + timedelta(days=0),
            turno=turno_c,
            controlador=controlador_a,
        ),
        Asignacion(
            fecha=fecha_base + timedelta(days=1),
            turno=turno_c,
            controlador=controlador_a,
        ),
        Asignacion(
            fecha=fecha_base + timedelta(days=2),
            turno=turno_b,
            controlador=controlador_a,
        ),
        Asignacion(
            fecha=fecha_base + timedelta(days=2),
            turno=turno_c,
            controlador=controlador_b,
        ),
    ]   