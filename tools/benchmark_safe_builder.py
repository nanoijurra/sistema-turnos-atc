from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.engine import validar_todo
from src.models import Asignacion, Controlador, crear_esquema_8h
from src.scoring import calcular_score, es_roster_valido


NORMAL = "NORMAL"
RECUPERACION = "RECUPERACION"
STRESS_CONTAMINADO = "STRESS_CONTAMINADO"


@dataclass(frozen=True)
class BenchmarkSafeScenario:
    asignaciones: list
    metadata: dict


def _contar_violaciones(resultados: list, severidad: str) -> int:
    return sum(
        1
        for resultado in resultados
        for violacion in resultado.violaciones
        if violacion.severidad == severidad
    )


def evaluar_metadata_benchmark(
    asignaciones: list,
    modo: str = NORMAL,
    config_file: str = "config_equilibrado.json",
) -> dict:
    resultados = validar_todo(asignaciones, config_file)

    hard_original = _contar_violaciones(resultados, "hard")
    soft_original = _contar_violaciones(resultados, "soft")
    score_original = calcular_score(resultados)
    valido_original = es_roster_valido(resultados)
    benchmark_safe = hard_original == 0

    metadata = {
        "modo": modo,
        "valido_original": valido_original,
        "hard_original": hard_original,
        "soft_original": soft_original,
        "score_original": score_original,
        "benchmark_safe": benchmark_safe,
    }

    if modo == NORMAL and not benchmark_safe:
        raise ValueError(
            f"Benchmark NORMAL abortado: roster base invalido "
            f"(hard_original={hard_original})."
        )

    return metadata


def crear_escenario_benchmark_safe(
    cantidad_controladores: int,
    fecha_inicio: date = date(2026, 3, 1),
    turno_codigo: str = "A",
    modo: str = NORMAL,
    config_file: str = "config_equilibrado.json",
) -> BenchmarkSafeScenario:
    esquema = crear_esquema_8h()
    turno = esquema.obtener_turno(turno_codigo)

    asignaciones = [
        Asignacion(
            fecha=fecha_inicio,
            turno=turno,
            controlador=Controlador(f"ATC_{idx + 1:03d}"),
        )
        for idx in range(cantidad_controladores)
    ]

    metadata = evaluar_metadata_benchmark(
        asignaciones=asignaciones,
        modo=modo,
        config_file=config_file,
    )

    return BenchmarkSafeScenario(
        asignaciones=asignaciones,
        metadata=metadata,
    )


def main() -> None:
    print()
    print("Demo benchmark-safe builder - sistema de swaps ATC")
    print("-" * 100)
    print(
        f"{'Controladores':>14} | {'Asignaciones':>12} | {'Modo':>8} | "
        f"{'Safe':>6} | {'Valido':>6} | {'Hard':>6} | {'Soft':>6} | {'Score':>8}"
    )
    print("-" * 100)

    for cantidad in [80, 120, 180]:
        escenario = crear_escenario_benchmark_safe(cantidad_controladores=cantidad)
        metadata = escenario.metadata

        print(
            f"{cantidad:>14} | "
            f"{len(escenario.asignaciones):>12} | "
            f"{metadata['modo']:>8} | "
            f"{str(metadata['benchmark_safe']):>6} | "
            f"{str(metadata['valido_original']):>6} | "
            f"{metadata['hard_original']:>6} | "
            f"{metadata['soft_original']:>6} | "
            f"{metadata['score_original']:>8}"
        )

    print("-" * 100)
    print()
    print("Nota:")
    print("- Este builder genera una base sintetica benchmark-safe de baja densidad.")
    print("- No representa aun un roster operativo completo.")
    print("- Sirve para benchmarks NORMAL sin contaminacion hard inicial.")
    print()


if __name__ == "__main__":
    main()