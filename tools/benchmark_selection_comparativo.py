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
TOP_N = 50
ORIGENES_POR_ESCALA = 3


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


def _buscar_indice(asignaciones: list, asignacion_objetivo) -> int:
    for idx, asignacion in enumerate(asignaciones):
        if asignacion is asignacion_objetivo:
            return idx

    for idx, asignacion in enumerate(asignaciones):
        if asignacion == asignacion_objetivo:
            return idx

    raise ValueError("La asignacion indicada no pertenece al roster.")


def _evaluar_candidatos(
    asignacion_origen,
    candidatos: list,
    asignaciones: list,
) -> list[dict]:
    idx_origen = _buscar_indice(asignaciones, asignacion_origen)

    pares = [
        (idx_origen, _buscar_indice(asignaciones, candidato))
        for candidato in candidatos
    ]

    return explorar_swaps(
        asignaciones=asignaciones,
        pares=pares,
        config_file="config_equilibrado.json",
    )


def _seleccionar_origenes_utiles(asignaciones: list) -> list[tuple[int, object, list, list]]:
    index = build_roster_index(asignaciones)
    seleccionados: list[tuple[int, object, list, list]] = []

    for idx, origen in enumerate(asignaciones):
        candidatos = generate_candidates(origen, index, mode="auto")
        prefiltrados = filter_technically_plausible_candidates(
            asignacion_origen=origen,
            candidatos=candidatos,
            asignaciones=asignaciones,
        )

        if not candidatos or not prefiltrados:
            continue

        seleccionados.append((idx, origen, candidatos, prefiltrados))

        if len(seleccionados) >= ORIGENES_POR_ESCALA:
            break

    return seleccionados


def _medir_sin_seleccion(asignacion_origen, prefiltrados: list, asignaciones: list):
    inicio = perf_counter()
    resultados = _evaluar_candidatos(
        asignacion_origen=asignacion_origen,
        candidatos=prefiltrados,
        asignaciones=asignaciones,
    )
    fin = perf_counter()

    return resultados, (fin - inicio) * 1000.0


def _medir_con_seleccion(asignacion_origen, prefiltrados: list, asignaciones: list):
    inicio_seleccion = perf_counter()
    seleccionados = seleccionar_candidatos(
        asignacion_origen=asignacion_origen,
        candidatos=prefiltrados,
        asignaciones=asignaciones,
        top_n=TOP_N,
    )
    fin_seleccion = perf_counter()

    inicio_sim = perf_counter()
    resultados = _evaluar_candidatos(
        asignacion_origen=asignacion_origen,
        candidatos=seleccionados,
        asignaciones=asignaciones,
    )
    fin_sim = perf_counter()

    seleccion_ms = (fin_seleccion - inicio_seleccion) * 1000.0
    sim_ms = (fin_sim - inicio_sim) * 1000.0
    total_ms = seleccion_ms + sim_ms

    return seleccionados, resultados, seleccion_ms, sim_ms, total_ms


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

    print()
    print(f"ESCALA {cantidad_controladores} CONTROLADORES - NORMAL_DENSO")
    _imprimir_metadata(metadata, asignaciones)

    origenes = _seleccionar_origenes_utiles(asignaciones)

    print("-" * 190)
    print(
        f"{'Idx':>6} | {'Controlador':>18} | {'Fecha':>10} | {'Turno':>5} | "
        f"{'Gen':>6} | {'Pref':>6} | "
        f"{'Sin sel eval':>12} | {'Sin sel ms':>12} | "
        f"{'Con sel eval':>12} | {'Sel ms':>8} | {'Con sel sim':>12} | {'Con sel total':>13} | "
        f"{'Ahorro ms':>10} | {'Ahorro %':>8} | {'Clasif con sel':<25} | {'Diag con sel'}"
    )
    print("-" * 190)

    total_sin_eval = 0
    total_con_eval = 0
    total_sin_ms = 0.0
    total_con_ms = 0.0
    total_sel_ms = 0.0

    total_clasif: Counter = Counter()
    total_diag: Counter = Counter()

    for idx, origen, candidatos, prefiltrados in origenes:
        resultados_sin, sin_ms = _medir_sin_seleccion(
            asignacion_origen=origen,
            prefiltrados=prefiltrados,
            asignaciones=asignaciones,
        )

        seleccionados, resultados_con, sel_ms, con_sim_ms, con_total_ms = _medir_con_seleccion(
            asignacion_origen=origen,
            prefiltrados=prefiltrados,
            asignaciones=asignaciones,
        )

        ahorro_ms = sin_ms - con_total_ms
        ahorro_pct = (ahorro_ms / sin_ms * 100.0) if sin_ms else 0.0

        clasif = _contar_clasificaciones(resultados_con)
        diag = _contar_transiciones(resultados_con)

        total_clasif.update(clasif)
        total_diag.update(diag)

        total_sin_eval += len(resultados_sin)
        total_con_eval += len(resultados_con)
        total_sin_ms += sin_ms
        total_con_ms += con_total_ms
        total_sel_ms += sel_ms

        print(
            f"{idx:>6} | "
            f"{origen.controlador.nombre:>18} | "
            f"{str(origen.fecha):>10} | "
            f"{origen.turno.codigo:>5} | "
            f"{len(candidatos):>6} | "
            f"{len(prefiltrados):>6} | "
            f"{len(resultados_sin):>12} | "
            f"{sin_ms:>12.2f} | "
            f"{len(resultados_con):>12} | "
            f"{sel_ms:>8.2f} | "
            f"{con_sim_ms:>12.2f} | "
            f"{con_total_ms:>13.2f} | "
            f"{ahorro_ms:>10.2f} | "
            f"{ahorro_pct:>7.1f}% | "
            f"{_formatear_counter(clasif):<25} | "
            f"{_formatear_counter(diag)}"
        )

    ahorro_total_ms = total_sin_ms - total_con_ms
    ahorro_total_pct = (ahorro_total_ms / total_sin_ms * 100.0) if total_sin_ms else 0.0

    print("-" * 190)
    print(
        f"Resumen escala {cantidad_controladores}: "
        f"sin_sel_eval={total_sin_eval}, "
        f"con_sel_eval={total_con_eval}, "
        f"sin_sel_ms={total_sin_ms:.2f}, "
        f"con_sel_ms={total_con_ms:.2f}, "
        f"sel_ms={total_sel_ms:.2f}, "
        f"ahorro_ms={ahorro_total_ms:.2f}, "
        f"ahorro_pct={ahorro_total_pct:.1f}%"
    )
    print(f"Clasificacion con seleccion: {_formatear_counter(total_clasif)}")
    print(f"Transicion con seleccion: {_formatear_counter(total_diag)}")


def main() -> None:
    print()
    print("Benchmark comparativo candidate_selection - sistema de swaps ATC")
    print("Escenario: NORMAL_DENSO")
    print(f"top_n={TOP_N}, origenes_por_escala={ORIGENES_POR_ESCALA}")
    print("Nota: no modifica clasificacion tecnica, ranking ni decision.")

    for escala in ESCALAS:
        _medir_escala(escala)

    print()
    print("Interpretacion:")
    print("- Sin seleccion evalua todos los candidatos prefiltrados.")
    print("- Con seleccion evalua solo top_n por origen.")
    print("- candidate_selection no clasifica ni decide; solo reduce carga hacia simulator.")


if __name__ == "__main__":
    main()