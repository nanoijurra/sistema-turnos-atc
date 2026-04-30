from __future__ import annotations

from collections import Counter
from time import perf_counter

try:
    from tools.bootstrap_path import ensure_project_root_on_path
except ModuleNotFoundError:
    from bootstrap_path import ensure_project_root_on_path

ensure_project_root_on_path()

from src.candidate_generation import generate_candidates
from src.roster_index import build_roster_index
from src.simulator import explorar_y_evaluar_candidatos_con_prefiltro
from src.technical_prefilter import filter_technically_plausible_candidates

from tools.diagnostic_transition_helper import diagnosticar_transicion
import tools.benchmark_safe_builder_v2 as builder_v2


ESCALAS = [80, 120, 180]
MODO = "NORMAL_DENSO"
MAX_ORIGENES_POR_ESCALA = 3
MAX_SIMULADOS_POR_ORIGEN = 250


def _crear_escenario_normal_denso(cantidad_controladores: int):
    posibles_nombres = [
        "crear_escenario_benchmark_safe_v2",
        "crear_escenario_benchmark_safe_denso",
        "crear_escenario_normal_denso",
        "build_benchmark_safe_scenario_v2",
        "build_normal_denso_scenario",
        "crear_escenario_benchmark_safe",
    ]

    for nombre in posibles_nombres:
        funcion = getattr(builder_v2, nombre, None)
        if funcion is None:
            continue

        intentos = [
            {"cantidad_controladores": cantidad_controladores, "modo": MODO},
            {"controladores": cantidad_controladores, "modo": MODO},
            {"cantidad_controladores": cantidad_controladores},
            {"controladores": cantidad_controladores},
            {"cantidad": cantidad_controladores},
            {},
        ]

        for kwargs in intentos:
            try:
                if kwargs:
                    return funcion(**kwargs)
                return funcion(cantidad_controladores)
            except TypeError:
                continue

    raise RuntimeError(
        "No se encontro una funcion compatible en tools.benchmark_safe_builder_v2."
    )


def _extraer_asignaciones_y_metadata(resultado_builder):
    if hasattr(resultado_builder, "asignaciones") and hasattr(resultado_builder, "metadata"):
        return resultado_builder.asignaciones, resultado_builder.metadata

    if isinstance(resultado_builder, tuple) and len(resultado_builder) == 2:
        return resultado_builder[0], resultado_builder[1]

    if isinstance(resultado_builder, dict):
        asignaciones = resultado_builder.get("asignaciones")
        metadata = resultado_builder.get("metadata", resultado_builder)
        if asignaciones is not None:
            return asignaciones, metadata

    raise RuntimeError(
        "No se pudo interpretar la salida del builder v2. "
        "Se esperaba objeto con asignaciones/metadata, tupla o dict."
    )


def _contar_clasificaciones(resultados: list[dict]) -> Counter:
    contador: Counter = Counter()
    for resultado in resultados:
        contador[resultado.get("clasificacion", "SIN_DATO")] += 1
    return contador


def _contar_transiciones(resultados: list[dict]) -> Counter:
    contador: Counter = Counter()
    for resultado in resultados:
        contador[diagnosticar_transicion(resultado)] += 1
    return contador


def _formatear_counter(counter: Counter) -> str:
    if not counter:
        return "sin_datos"
    return ", ".join(f"{clave}={valor}" for clave, valor in sorted(counter.items()))


def _seleccionar_origenes_utiles(asignaciones: list, limite: int) -> list[tuple[int, object, int, int]]:
    index = build_roster_index(asignaciones)
    seleccionados: list[tuple[int, object, int, int]] = []

    for idx, origen in enumerate(asignaciones):
        candidatos = generate_candidates(origen, index, mode="auto")
        prefiltrados = filter_technically_plausible_candidates(
            asignacion_origen=origen,
            candidatos=candidatos,
            asignaciones=asignaciones,
        )

        if not candidatos or not prefiltrados:
            continue

        seleccionados.append((idx, origen, len(candidatos), len(prefiltrados)))

        if len(seleccionados) >= limite:
            break

    return seleccionados


def _imprimir_metadata(metadata: dict, asignaciones: list) -> None:
    print(
        "Metadata: "
        f"modo={metadata.get('modo', MODO)}, "
        f"safe={metadata.get('benchmark_safe')}, "
        f"useful={metadata.get('benchmark_useful')}, "
        f"valido={metadata.get('valido_original')}, "
        f"hard={metadata.get('hard_original')}, "
        f"soft={metadata.get('soft_original')}, "
        f"score={metadata.get('score_original')}, "
        f"asignaciones={len(asignaciones)}, "
        f"candidate_count={metadata.get('candidate_count')}, "
        f"simulable_count={metadata.get('simulable_count')}, "
        f"densidad={metadata.get('densidad_promedio')}"
    )


def _medir_escala(cantidad_controladores: int) -> None:
    resultado_builder = _crear_escenario_normal_denso(cantidad_controladores)
    asignaciones, metadata = _extraer_asignaciones_y_metadata(resultado_builder)

    print()
    print(f"ESCALA {cantidad_controladores} CONTROLADORES - NORMAL_DENSO")
    _imprimir_metadata(metadata, asignaciones)
    print("-" * 180)
    print(
        f"{'Idx':>6} | {'Controlador':>18} | {'Fecha':>10} | {'Turno':>5} | "
        f"{'Generados':>10} | {'Pref':>8} | {'Eval':>8} | "
        f"{'Gen+Pref ms':>12} | {'Sim ms':>12} | {'Total ms':>12} | "
        f"{'Clasificacion tecnica':<35} | {'Transicion diagnostica'}"
    )
    print("-" * 180)

    origenes = _seleccionar_origenes_utiles(asignaciones, MAX_ORIGENES_POR_ESCALA)

    total_clasificaciones: Counter = Counter()
    total_transiciones: Counter = Counter()
    total_generados = 0
    total_prefiltrados = 0
    total_evaluados = 0
    total_ms = 0.0

    if not origenes:
        print("No se encontraron origenes con candidatos prefiltrados.")
        return

    for idx, origen, generados, prefiltrados in origenes:
        total_generados += generados
        total_prefiltrados += prefiltrados

        t0 = perf_counter()

        if prefiltrados > MAX_SIMULADOS_POR_ORIGEN:
            print(
                f"{idx:>6} | "
                f"{origen.controlador.nombre:>18} | "
                f"{str(origen.fecha):>10} | "
                f"{origen.turno.codigo:>5} | "
                f"{generados:>10} | "
                f"{prefiltrados:>8} | "
                f"{'OMITIDO':>8} | "
                f"{0.0:>12.2f} | "
                f"{0.0:>12.2f} | "
                f"{0.0:>12.2f} | "
                f"{'prefiltrados > limite':<35} | "
                f"limite={MAX_SIMULADOS_POR_ORIGEN}"
            )
            continue

        t1 = perf_counter()
        resultados = explorar_y_evaluar_candidatos_con_prefiltro(
            asignacion_origen=origen,
            asignaciones=asignaciones,
            modo="auto",
        )
        t2 = perf_counter()

        clasificaciones = _contar_clasificaciones(resultados)
        transiciones = _contar_transiciones(resultados)

        total_clasificaciones.update(clasificaciones)
        total_transiciones.update(transiciones)
        total_evaluados += len(resultados)

        gen_pref_ms = (t1 - t0) * 1000.0
        sim_ms = (t2 - t1) * 1000.0
        fila_total_ms = (t2 - t0) * 1000.0
        total_ms += fila_total_ms

        print(
            f"{idx:>6} | "
            f"{origen.controlador.nombre:>18} | "
            f"{str(origen.fecha):>10} | "
            f"{origen.turno.codigo:>5} | "
            f"{generados:>10} | "
            f"{prefiltrados:>8} | "
            f"{len(resultados):>8} | "
            f"{gen_pref_ms:>12.2f} | "
            f"{sim_ms:>12.2f} | "
            f"{fila_total_ms:>12.2f} | "
            f"{_formatear_counter(clasificaciones):<35} | "
            f"{_formatear_counter(transiciones)}"
        )

    print("-" * 180)
    print(
        f"Resumen escala {cantidad_controladores}: "
        f"generados={total_generados}, "
        f"prefiltrados={total_prefiltrados}, "
        f"evaluados={total_evaluados}, "
        f"total_ms={total_ms:.2f}"
    )
    print(f"Clasificacion tecnica: {_formatear_counter(total_clasificaciones)}")
    print(f"Transicion diagnostica: {_formatear_counter(total_transiciones)}")


def main() -> None:
    print()
    print("Benchmark NORMAL_DENSO flujo tecnico - sistema de swaps ATC")
    print("Modo: NORMAL_DENSO")
    print("Nota: no modifica clasificacion tecnica, ranking ni decision.")
    print(
        f"Limites: origenes_por_escala={MAX_ORIGENES_POR_ESCALA}, "
        f"max_simulados_por_origen={MAX_SIMULADOS_POR_ORIGEN}"
    )

    for escala in ESCALAS:
        _medir_escala(escala)

    print()
    print("Interpretacion:")
    print("- Este benchmark usa base valida y densa.")
    print("- Deberian aparecer transiciones VV_* si el roster original permanece valido.")
    print("- Si aparecen VI_DEGRADA, esos swaps rompen un roster originalmente valido.")
    print("- Si aparecen II_*, hay contaminacion o invalidez heredada inesperada.")


if __name__ == "__main__":
    main()