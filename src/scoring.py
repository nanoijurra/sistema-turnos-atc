from src.rule_types import RuleResult


def es_roster_valido(resultados: list[RuleResult]) -> bool:
    """
    Un roster es inválido si existe al menos una violación HARD.
    """
    for resultado in resultados:
        for violacion in resultado.violaciones:
            if violacion.severidad == "hard":
                return False
    return True


def calcular_score(
    resultados: list[RuleResult],
    score_inicial: int | float = 100
) -> int | float:
    """
    Calcula el score del roster.

    - Parte de score_inicial
    - Resta penalizaciones SOLO de violaciones SOFT
    - Nunca baja de 0
    """
    score = score_inicial

    for resultado in resultados:
        for violacion in resultado.violaciones:
            if violacion.severidad == "soft":
                score -= violacion.penalizacion

    return max(score, 0)