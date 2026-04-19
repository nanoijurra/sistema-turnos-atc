from src.db import get_connection


def init_historical_store() -> None:
    """
    Inicializa la tabla de historial de equidad.
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

    conn.commit()
    conn.close()


def obtener_historial_controlador(nombre: str) -> dict:
    """
    Devuelve historial de un controlador.
    Si no existe, retorna valor neutro.
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
    Incrementa el contador de beneficios recientes de un controlador.
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
    Devuelve historial en formato compatible con priorizacion historica.
    """
    return {
        nombre: obtener_historial_controlador(nombre)
        for nombre in nombres
    }