from __future__ import annotations

from collections import Counter
from time import perf_counter

try:
    from tools.bootstrap_path import ensure_project_root_on_path
except ModuleNotFoundError:
    from bootstrap_path import ensure_project_root_on_path

ensure_project_root_on_path()

from src.candidate_generation import generate_candidates
from src.candidate_selection import seleccionar_candidatos
from src.roster_index import build_roster_index
from src.simulator import explorar_swaps
from src.technical_prefilter import filter_technically_plausible_candidates

from tools.benchmark_safe_builder_v2 import crear_escenario_benchmark_safe_v2
from tools.diagnostic_transition_helper import diagnosticar_transicion


ESCALAS = [80, 120, 180]
MAX_ORIGENES_POR_ESCALA = 3
TOP_N = 50


def _buscar_indice_asignacion(asignaciones: list, asignacion_objetivo) -> int:
    for idx, asignacion in enumerate(asignaciones):
        if asignacion is asignacion_objetivo:
            return idx

    for idx, asignacion in enumerate(asignaciones):
        if asignacion == asignacion_objetivo:
            return idx

    raise ValueError("La asignacion seleccionada no pertenece al roster.")


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


def _imprimir_metadata(metadata: dict, asignaciones: list) -> None:
    print(
        "Metadata: "
        f"modo={metadata.get('modo')}, "
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
    escenario = crear_escenario_benchmark_safe_v2(
        cantidad_controladores=cantidad_controladores,
    )
    asignaciones = escenario.asignaciones
    metadata = escenario.metadata
    roster_index = build_roster_index(asignaciones)

    print()
    print(f"ESCALA {cantidad_controladores} CONTROLADORES - NORMAL_DENSO SELECTION")
    _imprimir_metadata(metadata, asignaciones)
    print("-" * 220)
    print(
        f"{'Idx':>6} | {'Controlador':>18} | {'Fecha':>10} | {'Turno':>5} | "
        f"{'Generados':>10} | {'Pref':>8} | {'Selec':>8} | {'Sim':>8} | "
        f"{'Gen ms':>10} | {'Pref ms':>10} | {'Sel ms':>10} | "
        f"{'Sim ms':>10} | {'Total ms':>10} | "
        f"{'Clasificacion final':<35} | {'Transicion diagnostica'}"
    )
    print("-" * 220)

    origenes_utiles = 0
    total_generados = 0
    total_prefiltrados = 0
    total_seleccionados = 0
    total_simulados = 0
    total_ms = 0.0
    total_clasificaciones: Counter = Counter()
    total_transiciones: Counter = Counter()

    for idx_origen, origen in enumerate(asignaciones):
        t0 = perf_counter()
        candidatos = generate_candidates(origen, roster_index, mode="auto")
        t1 = perf_counter()

        prefiltrados = filter_technically_plausible_candidates(
            asignacion_origen=origen,
            candidatos=candidatos,
            asignaciones=asignaciones,
        )
        t2 = perf_counter()

        seleccionados = seleccionar_candidatos(
            asignacion_origen=origen,
            candidatos=prefiltrados,
            asignaciones=asignaciones,
            top_n=TOP_N,
        )
        t3 = perf_counter()

        if not seleccionados:
            continue

        idx_origen_real = _buscar_indice_asignacion(asignaciones, origen)
        pares = [
            (idx_origen_real, _buscar_indice_asignacion(asignaciones, candidato))
            for candidato in seleccionados
        ]
        resultados = explorar_swaps(asignaciones=asignaciones, pares=pares)
        t4 = perf_counter()

        clasificaciones = _contar_clasificaciones(resultados)
        transiciones = _contar_transiciones(resultados)

        total_generados += len(candidatos)
        total_prefiltrados += len(prefiltrados)
        total_seleccionados += len(seleccionados)
        total_simulados += len(resultados)
        total_clasificaciones.update(clasificaciones)
        total_transiciones.update(transiciones)

        gen_ms = (t1 - t0) * 1000.0
        pref_ms = (t2 - t1) * 1000.0
        sel_ms = (t3 - t2) * 1000.0
        sim_ms = (t4 - t3) * 1000.0
        fila_total_ms = (t4 - t0) * 1000.0
        total_ms += fila_total_ms

        print(
            f"{idx_origen:>6} | "
            f"{origen.controlador.nombre:>18} | "
            f"{str(origen.fecha):>10} | "
            f"{origen.turno.codigo:>5} | "
            f"{len(candidatos):>10} | "
            f"{len(prefiltrados):>8} | "
            f"{len(seleccionados):>8} | "
            f"{len(resultados):>8} | "
            f"{gen_ms:>10.2f} | "
            f"{pref_ms:>10.2f} | "
            f"{sel_ms:>10.2f} | "
            f"{sim_ms:>10.2f} | "
            f"{fila_total_ms:>10.2f} | "
            f"{_formatear_counter(clasificaciones):<35} | "
            f"{_formatear_counter(transiciones)}"
        )

        origenes_utiles += 1
        if origenes_utiles >= MAX_ORIGENES_POR_ESCALA:
            break

    print("-" * 220)
    print(
        f"Resumen escala {cantidad_controladores}: "
        f"generados={total_generados}, "
        f"prefiltrados={total_prefiltrados}, "
        f"seleccionados={total_seleccionados}, "
        f"simulados={total_simulados}, "
        f"top_n={TOP_N}, "
        f"total_ms={total_ms:.2f}"
    )
    print(f"Clasificacion final: {_formatear_counter(total_clasificaciones)}")
    print(f"Transicion diagnostica: {_formatear_counter(total_transiciones)}")


def main() -> None:
    print()
    print("Benchmark NORMAL_DENSO con candidate_selection v1 - sistema de swaps ATC")
    print("Nota: no modifica simulator, clasificacion tecnica, ranking ni decision.")
    print(
        f"Limites: origenes_por_escala={MAX_ORIGENES_POR_ESCALA}, "
        f"top_n={TOP_N}"
    )
    print("Baseline simple esperado: antes 80=79, 120=119, 180=179 por origen.")
    print("Con selection v1: maximo 50 simulados por origen.")

    for escala in ESCALAS:
        _medir_escala(escala)


if __name__ == "__main__":
    main()
