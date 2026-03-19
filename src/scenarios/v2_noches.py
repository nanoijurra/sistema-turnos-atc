from datetime import datetime
from models import TipoTurno, Turno, Asignacion

def crear_escenario():
    return [
        Asignacion(datetime(2026,3,1), Turno(TipoTurno.NOCHE, datetime(2026,3,1,22,30), datetime(2026,3,2,6,0))),
        Asignacion(datetime(2026,3,2), Turno(TipoTurno.NOCHE, datetime(2026,3,2,22,30), datetime(2026,3,3,6,0))),
        Asignacion(datetime(2026,3,3), Turno(TipoTurno.NOCHE, datetime(2026,3,3,22,30), datetime(2026,3,4,6,0))),
        Asignacion(datetime(2026,3,4), Turno(TipoTurno.NOCHE, datetime(2026,3,4,22,30), datetime(2026,3,5,6,0))),
    ]