from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import List


@dataclass(frozen=True)
class Turno:
    """
    Define un turno dentro de un esquema operativo.

    No representa una ocurrencia en el tiempo, sino una plantilla:
    código, hora de inicio, duración y propiedades operativas.
    """
    codigo: str
    hora_inicio: time
    duracion_horas: int
    categoria: str
    es_nocturno: bool = False
    habilitado: bool = True

    @property
    def hora_fin_teorica(self) -> time:
        """
        Calcula la hora de fin teórica del turno, sin asociarla a una fecha.
        Si cruza medianoche, la hora resultante será del día siguiente
        en términos conceptuales, pero acá solo se devuelve la componente time.
        """
        inicio_dummy = datetime.combine(date.today(), self.hora_inicio)
        fin_dummy = inicio_dummy + timedelta(hours=self.duracion_horas)
        return fin_dummy.time()


@dataclass(frozen=True)
class ShiftScheme:
    """
    Representa un esquema completo de turnos, por ejemplo:
    - 3x8 horas
    - 4x6 horas
    """
    codigo: str
    nombre: str
    turnos: List[Turno] = field(default_factory=list)

    def obtener_turno(self, codigo_turno: str) -> Turno:
        """
        Devuelve un turno por código. Lanza error si no existe.
        """
        for turno in self.turnos:
            if turno.codigo == codigo_turno:
                return turno
        raise ValueError(
            f"No existe un turno con código '{codigo_turno}' en el esquema '{self.codigo}'."
        )

    def turnos_habilitados(self) -> List[Turno]:
        """
        Devuelve solo los turnos habilitados del esquema.
        """
        return [turno for turno in self.turnos if turno.habilitado]


@dataclass(frozen=True)
class Asignacion:
    """
    Representa una asignación concreta de un turno en una fecha determinada.
    """
    fecha: date
    turno: Turno


def obtener_inicio_fin_asignacion(asignacion: Asignacion) -> tuple[datetime, datetime]:
    """
    Construye el intervalo temporal real de una asignación.

    Ejemplo:
    - fecha = 2026-03-10
    - turno = C, 22:30, duración 8h

    Resultado:
    - inicio = 2026-03-10 22:30
    - fin    = 2026-03-11 06:30
    """
    inicio_dt = datetime.combine(asignacion.fecha, asignacion.turno.hora_inicio)
    fin_dt = inicio_dt + timedelta(hours=asignacion.turno.duracion_horas)
    return inicio_dt, fin_dt


def crear_esquema_8h() -> ShiftScheme:
    """
    Esquema clásico de 3 turnos de 8 horas.
    """
    return ShiftScheme(
        codigo="8H",
        nombre="Esquema 3x8",
        turnos=[
            Turno(
                codigo="A",
                hora_inicio=time(6, 30),
                duracion_horas=8,
                categoria="MANANA",
                es_nocturno=False,
            ),
            Turno(
                codigo="B",
                hora_inicio=time(14, 30),
                duracion_horas=8,
                categoria="TARDE",
                es_nocturno=False,
            ),
            Turno(
                codigo="C",
                hora_inicio=time(22, 30),
                duracion_horas=8,
                categoria="NOCHE",
                es_nocturno=True,
            ),
        ],
    )


def crear_esquema_6h() -> ShiftScheme:
    """
    Esquema de contingencia de 4 turnos de 6 horas.

    Los horarios son configurables. Estos valores son una base de ejemplo
    coherente con una partición completa del día en bloques de 6 horas.
    """
    return ShiftScheme(
        codigo="6H",
        nombre="Esquema 4x6",
        turnos=[
            Turno(
                codigo="A",
                hora_inicio=time(0, 30),
                duracion_horas=6,
                categoria="MADRUGADA",
                es_nocturno=True,
            ),
            Turno(
                codigo="B",
                hora_inicio=time(6, 30),
                duracion_horas=6,
                categoria="MANANA",
                es_nocturno=False,
            ),
            Turno(
                codigo="C",
                hora_inicio=time(12, 30),
                duracion_horas=6,
                categoria="TARDE",
                es_nocturno=False,
            ),
            Turno(
                codigo="D",
                hora_inicio=time(18, 30),
                duracion_horas=6,
                categoria="NOCHE",
                es_nocturno=True,
            ),
        ],
    )