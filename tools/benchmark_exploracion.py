from __future__ import annotations

from dataclasses import replace
from statistics import mean
from time import perf_counter

from src.engine import crear_roster_version_inicial
from src.roster_store import limpiar_rosters
from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import (
    explorar_swaps_entre_controladores,
    filtrar_swaps_validos,
    filtrar_swaps_utiles,
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

    max_repeticiones = repeticion - 1
    escenario_escalado: list = []

    for rep in range(1, max_repeticiones + 1):
        for asignacion in base:
            nombre_original = asignacion.controlador.nombre
            nombre_nuevo = nombre_por_repeticion.get((rep, nombre_original))
            if nombre_nuevo is None:
                continue

            controlador_nuevo = replace(asignacion.controlador, nombre=nombre_nuevo)
            asignacion_nueva = replace(asignacion, controlador=controlador_nuevo)
            escenario_escalado.append(asignacion_nueva)

    if not escenario_escalado:
        raise ValueError("No se pudo construir el escenario escalado.")

    return escenario_escalado


def medir_exploracion(asignaciones: list, repeticiones: int = 1) -> tuple[float, int, int, int]:
    tiempos: list[float] = []
    cantidad_total = 0
    cantidad_validos = 0
    cantidad_utiles = 0

    for _ in range(repeticiones):
        limpiar_rosters()
        crear_roster_version_inicial(asignaciones, regimen_horario="8H")

        inicio = perf_counter()
        explorados = explorar_swaps_entre_controladores(asignaciones)
        validos = filtrar_swaps_validos(explorados)
        utiles = filtrar_swaps_utiles(validos)
        fin = perf_counter()

        tiempos.append((fin - inicio) * 1000.0)
        cantidad_total = len(explorados)
        cantidad_validos = len(validos)
        cantidad_utiles = len(utiles)

    return mean(tiempos), cantidad_total, cantidad_validos, cantidad_utiles


def main() -> None:
    escalas = [80]

    print()
    print("Benchmark de exploracion - sistema de swaps ATC")
    print("-" * 108)
    print(
        f"{'Controladores':>14} | {'Asignaciones':>12} | {'Explor ms':>12} | {'Total':>10} | {'Validos':>10} | {'Utiles':>10}"
    )
    print("-" * 108)

    for cantidad_controladores in escalas:
        print(f"Procesando escala {cantidad_controladores} controladores...")
        asignaciones = _crear_escenario_escalado(cantidad_controladores)
        explor_ms, total, validos, utiles = medir_exploracion(asignaciones)

        print(
            f"{cantidad_controladores:>14} | "
            f"{len(asignaciones):>12} | "
            f"{explor_ms:>12.2f} | "
            f"{total:>10} | "
            f"{validos:>10} | "
            f"{utiles:>10}"
        )

    print("-" * 108)
    print()
    print("Referencia de lectura:")
    print("- Explor ms: tiempo promedio de exploracion + filtrado.")
    print("- Total: swaps explorados brutos.")
    print("- Validos: swaps sin violaciones hard.")
    print("- Utiles: swaps validos con mejora util.")
    print()


if __name__ == "__main__":
    main()