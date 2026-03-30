import json
import os
import sqlite3
from datetime import datetime, date, time

from src.models import RosterVersion, Asignacion, Turno, Controlador


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "swaps_atc.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roster_versions (
        id TEXT PRIMARY KEY,
        version_number INTEGER,
        created_at TEXT,
        asignaciones_json TEXT,
        vigente INTEGER,
        base_version_id TEXT,
        regimen_horario TEXT
    )
    """)

    conn.commit()
    conn.close()


def serialize_asignacion(asignacion: Asignacion) -> dict:
    return {
        "fecha": asignacion.fecha.isoformat(),
        "turno": {
            "codigo": asignacion.turno.codigo,
            "hora_inicio": asignacion.turno.hora_inicio.isoformat(),
            "duracion_horas": asignacion.turno.duracion_horas,
            "categoria": asignacion.turno.categoria,
            "es_nocturno": asignacion.turno.es_nocturno,
            "habilitado": asignacion.turno.habilitado,
        },
        "controlador": {
            "nombre": asignacion.controlador.nombre,
            "habilitado": asignacion.controlador.habilitado,
        } if asignacion.controlador is not None else None,
    }


def deserialize_asignacion(data: dict) -> Asignacion:
    turno_data = data["turno"]
    controlador_data = data["controlador"]

    turno = Turno(
        codigo=turno_data["codigo"],
        hora_inicio=time.fromisoformat(turno_data["hora_inicio"]),
        duracion_horas=turno_data["duracion_horas"],
        categoria=turno_data["categoria"],
        es_nocturno=turno_data["es_nocturno"],
        habilitado=turno_data["habilitado"],
    )

    controlador = None
    if controlador_data is not None:
        controlador = Controlador(
            nombre=controlador_data["nombre"],
            habilitado=controlador_data["habilitado"],
        )

    return Asignacion(
        fecha=date.fromisoformat(data["fecha"]),
        turno=turno,
        controlador=controlador,
    )


def serialize_roster(roster: RosterVersion) -> tuple:
    return (
        roster.id,
        roster.version_number,
        roster.created_at.isoformat() if roster.created_at else None,
        json.dumps([serialize_asignacion(a) for a in roster.asignaciones]),
        1 if roster.vigente else 0,
        roster.base_version_id,
        roster.regimen_horario,
    )


def deserialize_roster(row) -> RosterVersion:
    asignaciones_data = json.loads(row[3]) if row[3] else []
    asignaciones = [deserialize_asignacion(a) for a in asignaciones_data]

    return RosterVersion(
        id=row[0],
        version_number=row[1],
        created_at=datetime.fromisoformat(row[2]) if row[2] else None,
        asignaciones=asignaciones,
        vigente=bool(row[4]),
        base_version_id=row[5],
        regimen_horario=row[6],
    )


def guardar_roster(roster: RosterVersion) -> RosterVersion:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO roster_versions (
        id,
        version_number,
        created_at,
        asignaciones_json,
        vigente,
        base_version_id,
        regimen_horario
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, serialize_roster(roster))

    conn.commit()
    conn.close()
    return roster


def obtener_roster(roster_id: str) -> RosterVersion | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roster_versions WHERE id = ?", (roster_id,))
    row = cursor.fetchone()

    conn.close()

    return deserialize_roster(row) if row else None


def listar_rosters() -> list[RosterVersion]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roster_versions")
    rows = cursor.fetchall()

    conn.close()

    return [deserialize_roster(row) for row in rows]


def listar_rosters_vigentes() -> list[RosterVersion]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roster_versions WHERE vigente = 1")
    rows = cursor.fetchall()

    conn.close()

    return [deserialize_roster(row) for row in rows]


def validar_unico_roster_vigente() -> None:
    vigentes = listar_rosters_vigentes()
    if len(vigentes) > 1:
        ids = [r.id for r in vigentes]
        raise ValueError(f"Hay más de un roster vigente al mismo tiempo: {ids}")


def obtener_roster_vigente() -> RosterVersion | None:
    vigentes = listar_rosters_vigentes()

    if not vigentes:
        return None

    if len(vigentes) > 1:
        ids = [r.id for r in vigentes]
        raise ValueError(f"Hay más de un roster vigente al mismo tiempo: {ids}")

    return vigentes[0]


def desactivar_roster_vigente_actual() -> RosterVersion | None:
    vigente = obtener_roster_vigente()

    if vigente is None:
        return None

    vigente.vigente = False
    guardar_roster(vigente)
    return vigente


def limpiar_rosters() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM roster_versions")

    conn.commit()
    conn.close()


init_db()