from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import (
    explorar_candidatos_acotados,
    explorar_swaps_entre_controladores,
    generar_pares_swap_entre_controladores,
)


ESCALAS = [80, 120, 180]
TIMEOUT_BRUTE_SEGUNDOS = 30
MAX_BRUTE_PARES = 10_000


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


def medir_brute_force(asignaciones: list) -> tuple[float, int]:
    inicio = perf_counter()
    resultados = explorar_swaps_entre_controladores(asignaciones)
    fin = perf_counter()

    return (fin - inicio) * 1000.0, len(resultados)


def medir_acotado(asignaciones: list, asignacion_origen) -> tuple[float, int]:
    inicio = perf_counter()
    candidatos = explorar_candidatos_acotados(
        asignacion_origen=asignacion_origen,
        asignaciones=asignaciones,
        modo="auto",
    )
    fin = perf_counter()

    return (fin - inicio) * 1000.0, len(candidatos)


def _formatear_ms(valor: float | None) -> str:
    if valor is None:
        return "NO_EJEC"
    return f"{valor:.2f}"


def _formatear_total(valor: int | None) -> str:
    if valor is None:
        return "NO_EJEC"
    return str(valor)


def _formatear_reduccion(brute_total: int, acotado_total: int) -> str:
    if acotado_total == 0:
        return "N/A"
    return f"{brute_total / acotado_total:.2f}x"


def main() -> None:
    print()
    print("Benchmark comparativo de exploracion - sistema de swaps ATC")
    print("-" * 112)
    print(
        f"{'Controladores':>14} | "
        f"{'Asignaciones':>12} | "
        f"{'Brute ms':>12} | "
        f"{'Acotado ms':>12} | "
        f"{'Brute total':>12} | "
        f"{'Acotado total':>13} | "
        f"{'Reduccion x':>12}"
    )
    print("-" * 112)

    escalas_no_ejecutadas: list[int] = []
    cortar_brute_restante = False

    for cantidad_controladores in ESCALAS:
        asignaciones = _crear_escenario_escalado(cantidad_controladores)
        asignacion_origen = asignaciones[0]

        brute_universo_total = len(generar_pares_swap_entre_controladores(asignaciones))
        acotado_ms, acotado_total = medir_acotado(asignaciones, asignacion_origen)

        if brute_universo_total > MAX_BRUTE_PARES:
            escalas_no_ejecutadas.append(cantidad_controladores)
            brute_ms = None
            brute_total = brute_universo_total
            cortar_brute_restante = True
        elif cortar_brute_restante:
            escalas_no_ejecutadas.append(cantidad_controladores)
            brute_ms = None
            brute_total = brute_universo_total
        else:
            brute_ms, brute_total = medir_brute_force(asignaciones)

            if brute_ms / 1000.0 > TIMEOUT_BRUTE_SEGUNDOS:
                cortar_brute_restante = True

        print(
            f"{cantidad_controladores:>14} | "
            f"{len(asignaciones):>12} | "
            f"{_formatear_ms(brute_ms):>12} | "
            f"{acotado_ms:>12.2f} | "
            f"{_formatear_total(brute_total):>12} | "
            f"{acotado_total:>13} | "
            f"{_formatear_reduccion(brute_universo_total, acotado_total):>12}"
        )

    print("-" * 112)
    print()
    print("Notas:")
    print("- Brute force usa explorar_swaps_entre_controladores sobre el universo global.")
    print("- Exploracion acotada usa explorar_candidatos_acotados desde asignaciones[0].")
    print("- La comparacion mide escalabilidad operativa, no equivalencia funcional exacta.")
    print(f"- Timeout de referencia brute force por escala: {TIMEOUT_BRUTE_SEGUNDOS}s.")
    print(f"- Modo seguro: no ejecuta brute force con mas de {MAX_BRUTE_PARES} pares.")

    if escalas_no_ejecutadas:
        print(f"- Escalas brute force no ejecutadas por estar fuera de rango: {', '.join(map(str, escalas_no_ejecutadas))}.")
    else:
        print("- Todas las escalas brute force se ejecutaron.")

    print()


if __name__ == "__main__":
    main()
