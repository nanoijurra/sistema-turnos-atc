from datetime import datetime
from models import TipoTurno, Turno, Asignacion

def crear_escenario():
    t1 = Turno(TipoTurno.MANANA, datetime(2026,3,1,6,0), datetime(2026,3,1,14,30))
    t2 = Turno(TipoTurno.NOCHE, datetime(2026,3,1,22,30), datetime(2026,3,2,6,0))

    return [
        Asignacion(datetime(2026,3,1), t1),
        Asignacion(datetime(2026,3,1), t2),
    ]