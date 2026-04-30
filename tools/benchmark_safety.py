from __future__ import annotations

try:
    from tools.bootstrap_path import ensure_project_root_on_path
except ModuleNotFoundError:
    from bootstrap_path import ensure_project_root_on_path

ensure_project_root_on_path()

from src.engine import validar_todo
from src.scoring import calcular_score, es_roster_valido


NORMAL = "NORMAL"
RECUPERACION = "RECUPERACION"
STRESS_CONTAMINADO = "STRESS_CONTAMINADO"
MODOS_VALIDOS = {NORMAL, RECUPERACION, STRESS_CONTAMINADO}


def _contar_violaciones(resultados: list) -> dict[str, int]:
    hard = 0
    soft = 0

    for resultado in resultados:
        for violacion in resultado.violaciones:
            if violacion.severidad == "hard":
                hard += 1
            elif violacion.severidad == "soft":
                soft += 1

    return {
        "hard_original": hard,
        "soft_original": soft,
    }


def evaluar_roster_base(
    asignaciones: list,
    config_file: str = "config_equilibrado.json",
) -> dict:
    resultados = validar_todo(asignaciones, config_file)
    conteo = _contar_violaciones(resultados)

    return {
        "valido_original": es_roster_valido(resultados),
        "hard_original": conteo["hard_original"],
        "soft_original": conteo["soft_original"],
        "score_original": calcular_score(resultados),
    }


def validar_benchmark_safe(
    asignaciones: list,
    modo: str,
    config_file: str = "config_equilibrado.json",
) -> dict:
    if modo not in MODOS_VALIDOS:
        raise ValueError(f"Modo de benchmark no soportado: {modo}")

    diagnostico = evaluar_roster_base(
        asignaciones=asignaciones,
        config_file=config_file,
    )

    if modo == NORMAL and diagnostico["hard_original"] > 0:
        raise RuntimeError(
            "Benchmark NORMAL abortado: roster base invalido "
            f"(hard_original={diagnostico['hard_original']}). "
            "Usar RECUPERACION o STRESS_CONTAMINADO si el escenario contaminado es intencional."
        )

    return {
        "modo": modo,
        **diagnostico,
    }
