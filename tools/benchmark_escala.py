from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from statistics import mean
from time import perf_counter
from typing import Iterable

from src.engine import crear_roster_version_inicial
from src.roster_store import limpiar_rosters
from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import evaluar_swap
from src.swap_service import (
    aplicar_swap_request,
    crear_swap_request,
    evaluar_swap_request,
    resolver_swap_request,
)


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

    if not nombres_base:
        raise ValueError("El escenario base no contiene controladores.")

    nombres_objetivo: list[str] = []
    repeticion = 1
    while len(nombres_objetivo) < objetivo_controladores:
        for nombre in nombres_base:
            if len(nombres_objetivo) >= objetivo_controladores:
                break
            nombres_objetivo.append(f"{nombre}_{repeticion:03d}")
        repeticion += 1

    controladores_permitidos = set(nombres_objetivo)
    escenario_escalado: list = []

    repeticion = 1
    nombres_generados: list[str] = []
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

    max_repeticiones = repeticion - 1

    for rep in range(1, max_repeticiones + 1):
        for asignacion in base:
            nombre_original = asignacion.controlador.nombre
            nombre_nuevo = nombre_por_repeticion.get((rep, nombre_original))
            if nombre_nuevo is None or nombre_nuevo not in controladores_permitidos:
                continue

            controlador_nuevo = replace(asignacion.controlador, nombre=nombre_nuevo)
            asignacion_nueva = replace(asignacion, controlador=controlador_nuevo)
            escenario_escalado.append(asignacion_nueva)

    if not escenario_escalado:
        raise ValueError("No se pudo construir el escenario escalado.")

    return escenario_escalado


def _crear_request_desde_asignaciones(asignaciones: list, idx_a: int, idx_b: int):
    return crear_swap_request(
        controlador_a=asignaciones[idx_a].controlador.nombre,
        controlador_b=asignaciones[idx_b].controlador.nombre,
        idx_a=idx_a,
        idx_b=idx_b,
    )


def _ms(promedio_segundos: Iterable[float]) -> float:
    return mean(promedio_segundos) * 1000.0


def medir_evaluacion(asignaciones: list, repeticiones: int = 20) -> float:
    tiempos: list[float] = []

    for _ in range(repeticiones):
        limpiar_rosters()
        crear_roster_version_inicial(deepcopy(asignaciones), regimen_horario="8H")

        request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

        inicio = perf_counter()
        evaluar_swap_request(
            asignaciones,
            request,
            evaluar_swap_fn=evaluar_swap,
        )
        fin = perf_counter()

        tiempos.append(fin - inicio)

    return _ms(tiempos)


def medir_aplicacion(asignaciones: list, repeticiones: int = 20) -> float:
    tiempos: list[float] = []

    for _ in range(repeticiones):
        limpiar_rosters()
        crear_roster_version_inicial(deepcopy(asignaciones), regimen_horario="8H")

        request = _crear_request_desde_asignaciones(asignaciones, 0, 3)

        evaluar_swap_request(
            asignaciones,
            request,
            evaluar_swap_fn=evaluar_swap,
        )
        resolver_swap_request(request, "APROBAR")

        inicio = perf_counter()
        aplicar_swap_request(asignaciones, request)
        fin = perf_counter()

        tiempos.append(fin - inicio)

    return _ms(tiempos)


def main() -> None:
    escalas = [78, 100, 120, 150]

    print()
    print("Benchmark de escala - sistema de swaps ATC")
    print("-" * 72)
    print(
        f"{'Controladores':>14} | {'Asignaciones':>12} | {'Eval ms':>12} | {'Aplic ms':>12}"
    )
    print("-" * 72)

    for cantidad_controladores in escalas:
        asignaciones = _crear_escenario_escalado(cantidad_controladores)
        evaluacion_ms = medir_evaluacion(asignaciones)
        aplicacion_ms = medir_aplicacion(asignaciones)

        print(
            f"{cantidad_controladores:>14} | "
            f"{len(asignaciones):>12} | "
            f"{evaluacion_ms:>12.2f} | "
            f"{aplicacion_ms:>12.2f}"
        )

    print("-" * 72)
    print()
    print("Referencia de lectura:")
    print("- Eval ms: tiempo promedio de evaluar un swap ya construido.")
    print("- Aplic ms: tiempo promedio de aplicar un swap ya aprobado.")
    print("- Esto no mide aun exploracion/ranking masivo de candidatos.")
    print()


if __name__ == "__main__":
    main()