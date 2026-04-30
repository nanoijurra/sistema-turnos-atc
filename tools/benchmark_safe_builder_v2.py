from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

try:
    from tools.bootstrap_path import ensure_project_root_on_path
except ModuleNotFoundError:
    from bootstrap_path import ensure_project_root_on_path

ensure_project_root_on_path()

from src.engine import validar_todo
from src.models import Asignacion, Controlador, crear_esquema_8h
from src.scoring import calcular_score, es_roster_valido
from src.simulator import explorar_candidatos_acotados
from src.technical_prefilter import filter_technically_plausible_candidates


NORMAL_DENSO = "NORMAL_DENSO"


@dataclass(frozen=True)
class BenchmarkSafeScenarioV2:
    asignaciones: list[Asignacion]
    metadata: dict


def _contar_violaciones(resultados: list, severidad: str) -> int:
    return sum(
        1
        for resultado in resultados
        for violacion in resultado.violaciones
        if violacion.severidad == severidad
    )


def _crear_controladores(cantidad_controladores: int) -> list[Controlador]:
    return [
        Controlador(f"ATC_{idx + 1:03d}")
        for idx in range(cantidad_controladores)
    ]


def _crear_asignaciones_normal_denso(
    cantidad_controladores: int,
    fecha_inicio: date,
    attempt: int,
    asignaciones_por_controlador: int,
) -> list[Asignacion]:
    esquema = crear_esquema_8h()
    turnos = [
        esquema.obtener_turno("A"),
        esquema.obtener_turno("B"),
        esquema.obtener_turno("C"),
    ]
    controladores = _crear_controladores(cantidad_controladores)
    asignaciones: list[Asignacion] = []

    # Las fechas quedan separadas por cuatro dias para mantener descanso amplio.
    # El offset por attempt cambia la grilla sin volver aleatoria la demo.
    for idx_controlador, controlador in enumerate(controladores):
        offset_dia = (idx_controlador + attempt) % 4

        for idx_asignacion in range(asignaciones_por_controlador):
            fecha = fecha_inicio + timedelta(days=offset_dia + idx_asignacion * 4)
            idx_turno = idx_asignacion % len(turnos)

            asignaciones.append(
                Asignacion(
                    fecha=fecha,
                    turno=turnos[idx_turno],
                    controlador=controlador,
                )
            )

    asignaciones.sort(
        key=lambda item: (
            item.fecha,
            item.turno.codigo,
            item.controlador.nombre if item.controlador else "",
        )
    )
    return asignaciones


def _calcular_densidad_promedio(asignaciones: list[Asignacion]) -> float:
    if not asignaciones:
        return 0.0

    controladores = {
        asignacion.controlador.nombre
        for asignacion in asignaciones
        if asignacion.controlador is not None
    }
    if not controladores:
        return 0.0

    return round(len(asignaciones) / len(controladores), 2)


def _contar_utilidad_minima(
    asignaciones: list[Asignacion],
    config_file: str,
    max_origenes_utilidad: int,
) -> tuple[int, int, int]:
    candidate_count = 0
    simulable_count = 0
    origenes_con_candidatos: set[int] = set()

    for idx, asignacion_origen in enumerate(asignaciones[:max_origenes_utilidad]):
        candidatos = explorar_candidatos_acotados(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            modo="auto",
        )
        simulables = filter_technically_plausible_candidates(
            asignacion_origen=asignacion_origen,
            candidatos=candidatos,
            asignaciones=asignaciones,
            config_file=config_file,
        )

        candidate_count += len(candidatos)
        simulable_count += len(simulables)

        if simulables:
            origenes_con_candidatos.add(idx)

    return candidate_count, simulable_count, len(origenes_con_candidatos)


def _evaluar_metadata(
    asignaciones: list[Asignacion],
    config_file: str,
    max_origenes_utilidad: int,
) -> dict:
    resultados = validar_todo(asignaciones, config_file)
    hard_original = _contar_violaciones(resultados, "hard")
    soft_original = _contar_violaciones(resultados, "soft")
    score_original = calcular_score(resultados)
    valido_original = es_roster_valido(resultados)
    candidate_count, simulable_count, origenes_con_candidatos = _contar_utilidad_minima(
        asignaciones=asignaciones,
        config_file=config_file,
        max_origenes_utilidad=max_origenes_utilidad,
    )
    benchmark_safe = hard_original == 0 and valido_original is True
    benchmark_useful = (
        candidate_count > 0
        and simulable_count > 0
        and origenes_con_candidatos > 0
    )

    controladores = {
        asignacion.controlador.nombre
        for asignacion in asignaciones
        if asignacion.controlador is not None
    }

    return {
        "modo": NORMAL_DENSO,
        "benchmark_safe": benchmark_safe,
        "benchmark_useful": benchmark_useful,
        "controladores": len(controladores),
        "asignaciones": len(asignaciones),
        "hard_original": hard_original,
        "soft_original": soft_original,
        "score_original": score_original,
        "valido_original": valido_original,
        "candidate_count": candidate_count,
        "simulable_count": simulable_count,
        "origenes_con_candidatos": origenes_con_candidatos,
        "densidad_promedio": _calcular_densidad_promedio(asignaciones),
    }


def crear_escenario_benchmark_safe_v2(
    cantidad_controladores: int,
    fecha_inicio: date = date(2026, 3, 1),
    config_file: str = "config_equilibrado.json",
    max_attempts: int = 10,
    asignaciones_por_controlador: int = 3,
    max_origenes_utilidad: int = 30,
    abortar_si_no_util: bool = True,
) -> BenchmarkSafeScenarioV2:
    if cantidad_controladores <= 0:
        raise ValueError("cantidad_controladores debe ser mayor a cero.")

    if max_attempts <= 0:
        raise ValueError("max_attempts debe ser mayor a cero.")

    if asignaciones_por_controlador < 2:
        raise ValueError("asignaciones_por_controlador debe ser al menos 2.")

    if max_origenes_utilidad <= 0:
        raise ValueError("max_origenes_utilidad debe ser mayor a cero.")

    ultimo_metadata: dict | None = None

    for attempt in range(max_attempts):
        asignaciones = _crear_asignaciones_normal_denso(
            cantidad_controladores=cantidad_controladores,
            fecha_inicio=fecha_inicio,
            attempt=attempt,
            asignaciones_por_controlador=asignaciones_por_controlador,
        )
        metadata = _evaluar_metadata(
            asignaciones=asignaciones,
            config_file=config_file,
            max_origenes_utilidad=max_origenes_utilidad,
        )
        ultimo_metadata = metadata

        if metadata["hard_original"] > 0 or not metadata["valido_original"]:
            continue

        if metadata["benchmark_useful"]:
            return BenchmarkSafeScenarioV2(
                asignaciones=asignaciones,
                metadata=metadata,
            )

        if not abortar_si_no_util:
            return BenchmarkSafeScenarioV2(
                asignaciones=asignaciones,
                metadata=metadata,
            )

    if ultimo_metadata is None:
        raise ValueError("No se pudo generar ningun escenario NORMAL_DENSO.")

    if ultimo_metadata["hard_original"] > 0 or not ultimo_metadata["valido_original"]:
        raise ValueError(
            "No se pudo generar escenario NORMAL_DENSO benchmark-safe "
            f"en {max_attempts} intentos: "
            f"hard_original={ultimo_metadata['hard_original']}, "
            f"valido_original={ultimo_metadata['valido_original']}."
        )

    raise ValueError(
        "No se pudo generar escenario NORMAL_DENSO util "
        f"en {max_attempts} intentos: "
        f"candidate_count={ultimo_metadata['candidate_count']}, "
        f"simulable_count={ultimo_metadata['simulable_count']}, "
        "origenes_con_candidatos="
        f"{ultimo_metadata['origenes_con_candidatos']}."
    )


def _imprimir_tabla(escenarios: list[BenchmarkSafeScenarioV2]) -> None:
    print()
    print("Benchmark-safe builder v2 - NORMAL_DENSO")
    print("-" * 140)
    print(
        f"{'Controladores':>14} | {'Asignaciones':>12} | {'Modo':>13} | "
        f"{'Safe':>5} | {'Useful':>6} | {'Hard':>4} | {'Soft':>4} | "
        f"{'Score':>5} | {'Candidates':>10} | {'Simulables':>10} | "
        f"{'Origenes':>8} | {'Densidad':>8}"
    )
    print("-" * 140)

    for escenario in escenarios:
        metadata = escenario.metadata
        print(
            f"{metadata['controladores']:>14} | "
            f"{metadata['asignaciones']:>12} | "
            f"{metadata['modo']:>13} | "
            f"{str(metadata['benchmark_safe']):>5} | "
            f"{str(metadata['benchmark_useful']):>6} | "
            f"{metadata['hard_original']:>4} | "
            f"{metadata['soft_original']:>4} | "
            f"{metadata['score_original']:>5} | "
            f"{metadata['candidate_count']:>10} | "
            f"{metadata['simulable_count']:>10} | "
            f"{metadata['origenes_con_candidatos']:>8} | "
            f"{metadata['densidad_promedio']:>8}"
        )

    print("-" * 140)


def main() -> None:
    escenarios = [
        crear_escenario_benchmark_safe_v2(cantidad_controladores=cantidad)
        for cantidad in (80, 120, 180)
    ]
    _imprimir_tabla(escenarios)


if __name__ == "__main__":
    main()
