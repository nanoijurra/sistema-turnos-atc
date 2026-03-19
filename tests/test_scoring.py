from src.rule_types import RuleResult, Violation
from src.scoring import es_roster_valido, calcular_score


def test_es_roster_valido_devuelve_false_si_hay_hard():
    resultados = [
        RuleResult(
            regla="regla_demo",
            prioridad=1,
            violaciones=[
                Violation(
                    codigo="ERROR_HARD",
                    mensaje="Violación dura",
                    severidad="hard",
                    penalizacion=0,
                )
            ],
        )
    ]

    assert es_roster_valido(resultados) is False


def test_es_roster_valido_devuelve_true_si_no_hay_hard():
    resultados = [
        RuleResult(
            regla="regla_demo",
            prioridad=1,
            violaciones=[
                Violation(
                    codigo="ADVERTENCIA",
                    mensaje="Violación blanda",
                    severidad="soft",
                    penalizacion=10,
                )
            ],
        )
    ]

    assert es_roster_valido(resultados) is True


def test_calcular_score_resta_solo_soft():
    resultados = [
        RuleResult(
            regla="regla_soft",
            prioridad=1,
            violaciones=[
                Violation(
                    codigo="SOFT_1",
                    mensaje="Violación soft 1",
                    severidad="soft",
                    penalizacion=10,
                ),
                Violation(
                    codigo="SOFT_2",
                    mensaje="Violación soft 2",
                    severidad="soft",
                    penalizacion=15,
                ),
                Violation(
                    codigo="HARD_1",
                    mensaje="Violación hard",
                    severidad="hard",
                    penalizacion=999,
                ),
            ],
        )
    ]

    score = calcular_score(resultados, score_inicial=100)

    assert score == 75