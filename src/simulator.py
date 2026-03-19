from copy import deepcopy
from dataclasses import replace
from datetime import date

from src.engine import validar_todo
from src.scoring import es_roster_valido, calcular_score
from src.rule_types import RuleResult


def mostrar_roster(asignaciones: list) -> None:
    """
    Muestra el roster con índice, fecha, código y categoría de turno.
    """
    for idx, asignacion in enumerate(asignaciones):
        print(
            f"[{idx}] {asignacion.fecha} | "
            f"{asignacion.turno.codigo} | "
            f"{asignacion.turno.categoria}"
        )


def buscar_indice_asignacion(
    asignaciones: list,
    fecha: date,
    codigo_turno: str | None = None,
) -> int:
    """
    Busca una asignación por fecha y, opcionalmente, código de turno.
    Devuelve el índice dentro de la lista.
    """
    candidatos = []

    for idx, asignacion in enumerate(asignaciones):
        if asignacion.fecha != fecha:
            continue

        if codigo_turno is not None and asignacion.turno.codigo != codigo_turno:
            continue

        candidatos.append(idx)

    if not candidatos:
        raise ValueError(
            f"No se encontró asignación para fecha={fecha} y codigo_turno={codigo_turno}."
        )

    if len(candidatos) > 1:
        raise ValueError(
            f"Búsqueda ambigua para fecha={fecha} y codigo_turno={codigo_turno}. "
            f"Se encontraron múltiples asignaciones: {candidatos}"
        )

    return candidatos[0]


def simular_swap(
    asignaciones: list,
    idx_a: int,
    idx_b: int,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Simula un swap entre dos posiciones del roster usando índices.
    """
    if idx_a == idx_b:
        raise ValueError("idx_a e idx_b deben ser distintos.")

    if not (0 <= idx_a < len(asignaciones)) or not (0 <= idx_b < len(asignaciones)):
        raise IndexError("Índices fuera de rango.")

    nuevo_roster = deepcopy(asignaciones)

    turno_a = nuevo_roster[idx_a].turno
    turno_b = nuevo_roster[idx_b].turno

    nuevo_roster[idx_a] = replace(nuevo_roster[idx_a], turno=turno_b)
    nuevo_roster[idx_b] = replace(nuevo_roster[idx_b], turno=turno_a)

    resultados: list[RuleResult] = validar_todo(nuevo_roster, config_file)

    valido = es_roster_valido(resultados)
    score = calcular_score(resultados)

    return {
        "roster": nuevo_roster,
        "resultados": resultados,
        "valido": valido,
        "score": score,
        "swap": {
            "idx_a": idx_a,
            "idx_b": idx_b,
        },
    }


def simular_swap_por_fecha(
    asignaciones: list,
    fecha_a: date,
    fecha_b: date,
    codigo_turno_a: str | None = None,
    codigo_turno_b: str | None = None,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Simula un swap buscando primero las asignaciones por fecha
    y opcionalmente por código de turno.
    """
    idx_a = buscar_indice_asignacion(
        asignaciones,
        fecha=fecha_a,
        codigo_turno=codigo_turno_a,
    )

    idx_b = buscar_indice_asignacion(
        asignaciones,
        fecha=fecha_b,
        codigo_turno=codigo_turno_b,
    )

    return simular_swap(
        asignaciones=asignaciones,
        idx_a=idx_a,
        idx_b=idx_b,
        config_file=config_file,
    )


def evaluar_swap(
    asignaciones: list,
    idx_a: int,
    idx_b: int,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Evalúa un swap comparando el estado antes y después.
    """

    # Estado original
    resultados_original = validar_todo(asignaciones, config_file)
    valido_original = es_roster_valido(resultados_original)
    score_original = calcular_score(resultados_original)

    # Estado simulado
    resultado_swap = simular_swap(
        asignaciones,
        idx_a,
        idx_b,
        config_file,
    )

    score_nuevo = resultado_swap["score"]
    valido_nuevo = resultado_swap["valido"]

    delta_score = score_nuevo - score_original

    return {
        "valido_original": valido_original,
        "score_original": score_original,
        "valido_nuevo": valido_nuevo,
        "score_nuevo": score_nuevo,
        "delta_score": delta_score,
        "mejora": delta_score > 0,
        "empeora": delta_score < 0,
        "igual": delta_score == 0,
        "resultado_swap": resultado_swap,
    }