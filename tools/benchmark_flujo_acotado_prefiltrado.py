from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import explorar_candidatos_acotados, explorar_swaps
from src.technical_prefilter import (
    filter_technically_plausible_candidates,
    get_candidate_prefilter_diagnostic_reasons,
)


ESCALAS = [80, 120, 180]
MAX_SIMULADOS_SEGURO = 250


def _nombres_controladores_en_orden(asignaciones: list) -> list[str]:
    vistos: set[str] = set()
    nombres: list[str] = []

    for asignacion in asignaciones:
        nombre = asignacion.controlador.nombre
        if nombre not in vistos:
            vistos.add(nombre)
            nombres.append(nombre)

    return nombres


def _crear_escenario_escalado(objetivo_controladores: int) -> list:
    base = crear_escenario()
    nombres_base = _nombres_controladores_en_orden(base)

    nombres_generados: list[str] = []
    repeticion = 1
    while len(nombres_generados) < objetivo_controladores:
        for nombre in nombres_base:
            if len(nombres_generados) >= objetivo_controladores:
                break
            nombres_generados.append(f"{nombre}_{repeticion:03d}")
        repeticion += 1

    nombre_por_repeticion: dict[tuple[int, str], str] = {}
    repeticion = 1
    indice_generado = 0
    while indice_generado < objetivo_controladores:
        for nombre in nombres_base:
            if indice_generado >= objetivo_controladores:
                break
            nombre_por_repeticion[(repeticion, nombre)] = nombres_generados[indice_generado]
            indice_generado += 1
        repeticion += 1

    escenario_escalado: list = []
    for rep in range(1, repeticion):
        for asignacion in base:
            nombre_original = asignacion.controlador.nombre
            nombre_nuevo = nombre_por_repeticion.get((rep, nombre_original))
            if nombre_nuevo is None:
                continue

            controlador_nuevo = replace(asignacion.controlador, nombre=nombre_nuevo)
            escenario_escalado.append(replace(asignacion, controlador=controlador_nuevo))

    return escenario_escalado


def _buscar_indice_asignacion(asignaciones: list, asignacion_objetivo) -> int:
    for idx, asignacion in enumerate(asignaciones):
        if asignacion is asignacion_objetivo:
            return idx

    for idx, asignacion in enumerate(asignaciones):
        if asignacion == asignacion_objetivo:
            return idx

    raise ValueError("La asignacion objetivo no pertenece al roster.")


def _conteo_clasificaciones(resultados: list[dict] | None) -> dict[str, int | str]:
    if resultados is None:
        return {
            "BENEFICIOSO": "NO_EJEC",
            "ACEPTABLE": "NO_EJEC",
            "RECHAZABLE": "NO_EJEC",
        }

    conteo = {
        "BENEFICIOSO": 0,
        "ACEPTABLE": 0,
        "RECHAZABLE": 0,
    }
    for resultado in resultados:
        conteo[resultado["clasificacion"]] += 1
    return conteo


def _formatear_ms(valor: float | None) -> str:
    if valor is None:
        return "NO_EJEC"
    return f"{valor:.2f}"


def main() -> None:
    print()
    print("Benchmark flujo acotado prefiltrado - sistema de swaps ATC")
    print("-" * 178)
    print(
        f"{'Controladores':>14} | "
        f"{'Asignaciones':>12} | "
        f"{'Generados':>10} | "
        f"{'Desc local':>10} | "
        f"{'Seq local':>10} | "
        f"{'Prefiltrados':>13} | "
        f"{'Simulados':>10} | "
        f"{'Gen ms':>10} | "
        f"{'Pref ms':>10} | "
        f"{'Sim ms':>10} | "
        f"{'Total ms':>10} | "
        f"{'BENEF':>7} | "
        f"{'ACEPT':>7} | "
        f"{'RECH':>7}"
    )
    print("-" * 178)

    for cantidad_controladores in ESCALAS:
        asignaciones = _crear_escenario_escalado(cantidad_controladores)
        asignacion_origen = asignaciones[0]

        inicio_generacion = perf_counter()
        candidatos = explorar_candidatos_acotados(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            modo="auto",
        )
        fin_generacion = perf_counter()

        inicio_prefiltro = perf_counter()
        diagnosticos = [
            get_candidate_prefilter_diagnostic_reasons(
                asignacion_origen=asignacion_origen,
                asignacion_candidata=candidato,
                asignaciones=asignaciones,
            )
            for candidato in candidatos
        ]
        descartados_descanso_local = sum(
            1
            for motivos in diagnosticos
            if "DESCANSO_LOCAL" in motivos
        )
        descartados_secuencia_local = sum(
            1
            for motivos in diagnosticos
            if "SECUENCIA_LOCAL" in motivos
        )
        candidatos_prefiltrados = filter_technically_plausible_candidates(
            asignacion_origen=asignacion_origen,
            candidatos=candidatos,
            asignaciones=asignaciones,
        )
        fin_prefiltro = perf_counter()

        resultados = None
        simulados = len(candidatos_prefiltrados)
        simulacion_ms = None

        if simulados <= MAX_SIMULADOS_SEGURO:
            idx_origen = _buscar_indice_asignacion(asignaciones, asignacion_origen)
            pares = [
                (idx_origen, _buscar_indice_asignacion(asignaciones, candidato))
                for candidato in candidatos_prefiltrados
            ]
            inicio_simulacion = perf_counter()
            resultados = explorar_swaps(asignaciones=asignaciones, pares=pares)
            fin_simulacion = perf_counter()
            simulacion_ms = (fin_simulacion - inicio_simulacion) * 1000.0

        clasificaciones = _conteo_clasificaciones(resultados)
        generacion_ms = (fin_generacion - inicio_generacion) * 1000.0
        prefiltro_ms = (fin_prefiltro - inicio_prefiltro) * 1000.0
        total_ms = None if simulacion_ms is None else generacion_ms + prefiltro_ms + simulacion_ms

        print(
            f"{cantidad_controladores:>14} | "
            f"{len(asignaciones):>12} | "
            f"{len(candidatos):>10} | "
            f"{descartados_descanso_local:>10} | "
            f"{descartados_secuencia_local:>10} | "
            f"{len(candidatos_prefiltrados):>13} | "
            f"{simulados:>10} | "
            f"{generacion_ms:>10.2f} | "
            f"{prefiltro_ms:>10.2f} | "
            f"{_formatear_ms(simulacion_ms):>10} | "
            f"{_formatear_ms(total_ms):>10} | "
            f"{str(clasificaciones['BENEFICIOSO']):>7} | "
            f"{str(clasificaciones['ACEPTABLE']):>7} | "
            f"{str(clasificaciones['RECHAZABLE']):>7}"
        )

    print("-" * 178)
    print(f"Modo seguro: omite simulacion cuando prefiltrados > {MAX_SIMULADOS_SEGURO}.")
    print()


if __name__ == "__main__":
    main()
