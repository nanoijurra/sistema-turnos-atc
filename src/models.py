from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TipoTurno(Enum):
    MANANA = "M"
    TARDE = "T"
    NOCHE = "N"
    FRANCO = "F"

@dataclass
class Turno:
    tipo: TipoTurno
    inicio: datetime
    fin: datetime

@dataclass
class Asignacion:
    fecha: datetime
    turno: Turno

@dataclass
class Controlador:
    nombre: str
    asignaciones: list