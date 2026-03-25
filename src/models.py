from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import List, Optional


@dataclass(frozen=True)
class Turno:
    codigo: str
    hora_inicio: time
    duracion_horas: int
    categoria: str
    es_nocturno: bool = False
    habilitado: bool = True

    @property
    def hora_fin_teorica(self) -> time:
        inicio_dummy = datetime.combine(date.today(), self.hora_inicio)
        fin_dummy = inicio_dummy + timedelta(hours=self.duracion_horas)
        return fin_dummy.time()


@dataclass(frozen=True)
class ShiftScheme:
    codigo: str
    nombre: str
    turnos: List[Turno] = field(default_factory=list)

    def obtener_turno(self, codigo_turno: str) -> Turno:
        for turno in self.turnos:
            if turno.codigo == codigo_turno:
                return turno
        raise ValueError(
            f"No existe un turno con código '{codigo_turno}' en el esquema '{self.codigo}'."
        )

    def turnos_habilitados(self) -> List[Turno]:
        return [turno for turno in self.turnos if turno.habilitado]


@dataclass(frozen=True)
class Controlador:
    nombre: str
    habilitado: bool = True


@dataclass(frozen=True)
class Asignacion:
    fecha: date
    turno: Turno
    controlador: Controlador | None = None


def obtener_inicio_fin_asignacion(asignacion: Asignacion) -> tuple[datetime, datetime]:
    inicio_dt = datetime.combine(asignacion.fecha, asignacion.turno.hora_inicio)
    fin_dt = inicio_dt + timedelta(hours=asignacion.turno.duracion_horas)
    return inicio_dt, fin_dt


def crear_esquema_8h() -> ShiftScheme:
    return ShiftScheme(
        codigo="8H",
        nombre="Esquema 3x8",
        turnos=[
            Turno("A", time(6, 30), 8, "MANANA", es_nocturno=False),
            Turno("B", time(14, 30), 8, "TARDE", es_nocturno=False),
            Turno("C", time(22, 30), 8, "NOCHE", es_nocturno=True),
        ],
    )


def crear_esquema_6h() -> ShiftScheme:
    return ShiftScheme(
        codigo="6H",
        nombre="Esquema 4x6",
        turnos=[
            Turno("A", time(0, 30), 6, "MADRUGADA", es_nocturno=True),
            Turno("B", time(6, 30), 6, "MANANA", es_nocturno=False),
            Turno("C", time(12, 30), 6, "TARDE", es_nocturno=False),
            Turno("D", time(18, 30), 6, "NOCHE", es_nocturno=True),
        ],
    )


@dataclass
class RosterVersion:
    """
    Representa una versión completa del roster.
    """
    id: str
    version_number: int
    created_at: datetime
    asignaciones: list
    vigente: bool = True
    base_version_id: Optional[str] = None
    regimen_horario: str = "6H"


@dataclass
class SwapRequest:
    """
    Representa una solicitud de intercambio de turnos entre dos controladores.
    """
    id: str
    controlador_a: str
    controlador_b: str
    idx_a: int
    idx_b: int
    estado: str  # PENDIENTE / ACEPTADO / RECHAZADO / CANCELADO
    fecha_creacion: datetime
    decision_sugerida: Optional[str] = None
    fecha_resolucion: Optional[datetime] = None
    motivo: Optional[str] = None
    history: list[str] = field(default_factory=list)
    roster_hash: str | None = None
    roster_version_id: Optional[str] = None

    def add_history_entry(self, mensaje: str) -> None:
        self.history.append(mensaje)