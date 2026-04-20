from datetime import datetime, timedelta

from src.db import get_connection


DEFAULT_VENTANA_DIAS = 90


def init_historical_store() -> None:
    """
    Inicializa tablas de historial de equidad.

    Se mantiene tabla legacy `historical_equity` por compatibilidad.
    La nueva fuente de verdad es `historical_equity_events`.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS historical_equity (
            controlador TEXT PRIMARY KEY,
            beneficios_recientes INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS historical_equity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            controlador TEXT NOT NULL,
            swap_request_id TEXT,
            fecha_evento TEXT NOT NULL,
            tipo_evento TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def obtener_historial_controlador(nombre: str) -> dict:
    """
    Compatibilidad legacy: devuelve contador agregado simple.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT beneficios_recientes
        FROM historical_equity
        WHERE controlador = ?
        """,
        (nombre,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"beneficios_recientes": 0}

    return {"beneficios_recientes": row[0]}


def incrementar_beneficio_controlador(nombre: str) -> None:
    """
    Compatibilidad legacy: incrementa contador agregado simple.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO historical_equity (controlador, beneficios_recientes)
        VALUES (?, 1)
        ON CONFLICT(controlador)
        DO UPDATE SET beneficios_recientes = beneficios_recientes + 1
        """,
        (nombre,),
    )

    conn.commit()
    conn.close()


def obtener_historial_para_controladores(nombres: list[str]) -> dict:
    """
    Compatibilidad legacy: devuelve historial agregado simple.
    """
    return {
        nombre: obtener_historial_controlador(nombre)
        for nombre in nombres
    }


def registrar_evento_beneficio_controlador(
    nombre: str,
    swap_request_id: str | None = None,
    fecha_evento: datetime | None = None,
) -> None:
    """
    Registra un evento historico valido de beneficio aplicado.
    """
    fecha = fecha_evento or datetime.now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO historical_equity_events (
            controlador,
            swap_request_id,
            fecha_evento,
            tipo_evento
        ) VALUES (?, ?, ?, ?)
        """,
        (
            nombre,
            swap_request_id,
            fecha.isoformat(),
            "BENEFICIO_APLICADO",
        ),
    )

    conn.commit()
    conn.close()


def listar_eventos_equidad_controlador(
    nombre: str,
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> list[dict]:
    """
    Lista eventos historicos de un controlador dentro de un rango opcional.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT controlador, swap_request_id, fecha_evento, tipo_evento
        FROM historical_equity_events
        WHERE controlador = ?
        ORDER BY fecha_evento ASC
        """,
        (nombre,),
    )
    rows = cursor.fetchall()
    conn.close()

    eventos = []
    for row in rows:
        fecha = datetime.fromisoformat(row[2])

        if desde is not None and fecha < desde:
            continue
        if hasta is not None and fecha > hasta:
            continue

        eventos.append(
            {
                "controlador": row[0],
                "swap_request_id": row[1],
                "fecha_evento": fecha,
                "tipo_evento": row[3],
            }
        )

    return eventos


def _peso_decaimiento_lineal(
    fecha_evento: datetime,
    fecha_referencia: datetime,
    ventana_dias: int,
) -> float:
    """
    Calcula peso lineal dentro de la ventana temporal.
    Evento reciente -> peso cercano a 1
    Evento al final de ventana -> peso cercano a 0
    """
    if ventana_dias <= 0:
        return 0.0

    delta_dias = (fecha_referencia - fecha_evento).total_seconds() / 86400.0

    if delta_dias < 0:
        return 1.0

    if delta_dias > ventana_dias:
        return 0.0

    peso = 1.0 - (delta_dias / ventana_dias)
    return max(peso, 0.0)


def obtener_historial_equidad_derivado(
    nombres: list[str],
    ventana_dias: int = DEFAULT_VENTANA_DIAS,
    fecha_referencia: datetime | None = None,
) -> dict:
    """
    Devuelve historial derivado desde eventos aplicando:
    - ventana temporal deslizante
    - decaimiento lineal en lectura

    Formato compatible con priorizacion historica:
    {
        "ATC_A": {"beneficios_recientes": 1.7},
        ...
    }
    """
    referencia = fecha_referencia or datetime.now()
    desde = referencia - timedelta(days=ventana_dias)

    historial = {}

    for nombre in nombres:
        eventos = listar_eventos_equidad_controlador(
            nombre=nombre,
            desde=desde,
            hasta=referencia,
        )

        score = 0.0
        for evento in eventos:
            if evento["tipo_evento"] != "BENEFICIO_APLICADO":
                continue

            score += _peso_decaimiento_lineal(
                fecha_evento=evento["fecha_evento"],
                fecha_referencia=referencia,
                ventana_dias=ventana_dias,
            )

        historial[nombre] = {"beneficios_recientes": score}

    return historial