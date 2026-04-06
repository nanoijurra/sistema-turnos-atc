import json
from datetime import datetime

from src.db import get_connection
from src.models import SwapRequest


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS swap_requests (
        id TEXT PRIMARY KEY,
        controlador_a TEXT,
        controlador_b TEXT,
        idx_a INTEGER,
        idx_b INTEGER,
        estado TEXT,
        fecha_creacion TEXT,
        fecha_resolucion TEXT,
        decision_sugerida TEXT,
        motivo TEXT,
        history TEXT,
        roster_hash TEXT,
        roster_version_id TEXT
    )
    """)

    conn.commit()
    conn.close()


def serialize_request(request: SwapRequest) -> tuple:
    return (
        request.id,
        request.controlador_a,
        request.controlador_b,
        request.idx_a,
        request.idx_b,
        request.estado,
        request.fecha_creacion.isoformat() if request.fecha_creacion else None,
        request.fecha_resolucion.isoformat() if request.fecha_resolucion else None,
        request.decision_sugerida,
        request.motivo,
        json.dumps(request.history or []),
        request.roster_hash,
        request.roster_version_id,
    )


def deserialize_request(row) -> SwapRequest:
    return SwapRequest(
        id=row[0],
        controlador_a=row[1],
        controlador_b=row[2],
        idx_a=row[3],
        idx_b=row[4],
        estado=row[5],
        fecha_creacion=datetime.fromisoformat(row[6]) if row[6] else None,
        fecha_resolucion=datetime.fromisoformat(row[7]) if row[7] else None,
        decision_sugerida=row[8],
        motivo=row[9],
        history=json.loads(row[10]) if row[10] else [],
        roster_hash=row[11],
        roster_version_id=row[12],  # 🔴 asegurado
    )


def guardar_request(request: SwapRequest) -> SwapRequest:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO swap_requests (
        id,
        controlador_a,
        controlador_b,
        idx_a,
        idx_b,
        estado,
        fecha_creacion,
        fecha_resolucion,
        decision_sugerida,
        motivo,
        history,
        roster_hash,
        roster_version_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, serialize_request(request))

    conn.commit()
    conn.close()
    return request


def obtener_request(request_id: str) -> SwapRequest | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM swap_requests WHERE id = ?", (request_id,))
    row = cursor.fetchone()

    conn.close()

    return deserialize_request(row) if row else None


def listar_requests() -> list[SwapRequest]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM swap_requests")
    rows = cursor.fetchall()

    conn.close()

    return [deserialize_request(row) for row in rows]


def limpiar_requests() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM swap_requests")

    conn.commit()
    conn.close()


def listar_requests_por_estado(estado: str) -> list[SwapRequest]:
    return [r for r in listar_requests() if r.estado == estado]


def listar_requests_por_roster_version(roster_version_id: str) -> list[SwapRequest]:
    return [
        r for r in listar_requests()
        if r.roster_version_id == roster_version_id
    ]


def listar_requests_activos() -> list[SwapRequest]:
    return [
        r for r in listar_requests()
        if r.estado in ("PENDIENTE", "EVALUADO")
    ]


def resumen_requests() -> dict:
    resumen = {}
    total = 0

    for r in listar_requests():
        resumen[r.estado] = resumen.get(r.estado, 0) + 1
        total += 1

    resumen["TOTAL"] = total
    return resumen


init_db()