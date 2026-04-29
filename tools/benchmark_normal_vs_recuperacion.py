from __future__ import annotations

from collections import Counter
from dataclasses import replace
from datetime import date
from typing import Iterable

from src.models import Asignacion, Controlador, crear_esquema_8h
from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import explorar_y_evaluar_candidatos_con_prefiltro

from tools.benchmark_safe_builder import crear_escenario_benchmark_safe
from tools.benchmark_safety import validar_benchmark_safe
from tools.diagnostic_transition_helper import diagnosticar_transicion


def _nombres_controladores_en_orden(asignaciones: list) -> list[str]:
    vistos: set[str] = set()
    nombres: list[str] = []

    for asignacion in asignaciones:
        nombre = asignacion.controlador.nombre
        if nombre not in vistos:
            vistos.add(nombre)
            nombres.append(nombre)

    return nombres


def _crear_escenario_contaminado_escalado(cantidad_controladores: int) -> list:
    base = crear_escenario()
    nombres_base = _nombres_controladores_en_orden(base)

    nombres_generados: list[str] = []
    repeticion = 1

    while len(nombres_generados) < cantidad_controladores:
        for nombre in nombres_base:
            if len(nombres_generados) >= cantidad_controladores:
                break
            nombres_generados.append(f"{nombre}_{repeticion:03d}")
        repeticion += 1

    nombre_por_repeticion: dict[tuple[int, str], str] = {}
    repeticion = 1
    indice_generado = 0

    while indice_generado < cantidad_controladores:
        for nombre in nombres_base:
            if indice_generado >= cantidad_controladores:
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
            asignacion_nueva = replace(asignacion, controlador=controlador_nuevo)
            escenario_escalado.append(asignacion_nueva)

    return escenario_escalado


def _origenes(asignaciones: list) -> list[tuple[int, object]]:
    indices = [0, len(asignaciones) - 1]
    vistos: set[int] = set()
    resultado: list[tuple[int, object]] = []

    for idx in indices:
        if idx in vistos:
            continue
        vistos.add(idx)
        resultado.append((idx, asignaciones[idx]))

    return resultado


def _contar_clasificaciones(resultados: Iterable[dict]) -> Counter:
    contador: Counter = Counter()
    for resultado in resultados:
        contador[resultado.get("clasificacion", "SIN_DATO")] += 1
    return contador


def _contar_transiciones(resultados: Iterable[dict]) -> Counter:
    contador: Counter = Counter()
    for resultado in resultados:
        contador[diagnosticar_transicion(resultado)] += 1
    return contador


def _formatear_counter(counter: Counter) -> str:
    if not counter:
        return "sin_datos"
    return ", ".join(f"{clave}={valor}" for clave, valor in sorted(counter.items()))


def _imprimir_escenario(nombre: str, modo: str, asignaciones: list) -> None:
    safety = validar_benchmark_safe(asignaciones, modo=modo)

    print()
    print(f"ESCENARIO {nombre}")
    hard_original = safety.get("hard_original")
    benchmark_safe = safety.get("benchmark_safe", hard_original == 0)

    print(
        "Safety: "
        f"modo={safety.get('modo', modo)}, "
        f"benchmark_safe={benchmark_safe}, "
        f"valido_original={safety.get('valido_original')}, "
        f"hard_original={hard_original}, "
        f"soft_original={safety.get('soft_original')}, "
        f"score_original={safety.get('score_original')}"
    )
    print("-" * 150)
    print(
        f"{'Idx':>6} | {'Controlador':>18} | {'Fecha':>10} | {'Turno':>5} | "
        f"{'Eval':>8} | {'Clasificacion tecnica':<40} | {'Transicion diagnostica'}"
    )
    print("-" * 150)

    total_clasificaciones: Counter = Counter()
    total_transiciones: Counter = Counter()
    total_evaluados = 0

    for idx, origen in _origenes(asignaciones):
        resultados = explorar_y_evaluar_candidatos_con_prefiltro(
            asignacion_origen=origen,
            asignaciones=asignaciones,
            modo="auto",
        )

        clasificaciones = _contar_clasificaciones(resultados)
        transiciones = _contar_transiciones(resultados)

        total_clasificaciones.update(clasificaciones)
        total_transiciones.update(transiciones)
        total_evaluados += len(resultados)

        print(
            f"{idx:>6} | "
            f"{origen.controlador.nombre:>18} | "
            f"{str(origen.fecha):>10} | "
            f"{origen.turno.codigo:>5} | "
            f"{len(resultados):>8} | "
            f"{_formatear_counter(clasificaciones):<40} | "
            f"{_formatear_counter(transiciones)}"
        )

    print("-" * 150)
    print(f"Resumen {nombre}: evaluados={total_evaluados}")
    print(f"Clasificacion tecnica: {_formatear_counter(total_clasificaciones)}")
    print(f"Transicion diagnostica: {_formatear_counter(total_transiciones)}")


def main() -> None:
    escala = 80

    escenario_normal = crear_escenario_benchmark_safe(
        cantidad_controladores=escala,
        modo="NORMAL",
    ).asignaciones

    escenario_recuperacion = _crear_escenario_contaminado_escalado(escala)

    print()
    print("Benchmark NORMAL vs RECUPERACION - sistema de swaps ATC")
    print("Nota: no cambia clasificacion tecnica, ranking ni decision.")
    print(f"Escala comparada: {escala} controladores")

    _imprimir_escenario(
        nombre="NORMAL benchmark-safe",
        modo="NORMAL",
        asignaciones=escenario_normal,
    )

    _imprimir_escenario(
        nombre="RECUPERACION contaminado",
        modo="RECUPERACION",
        asignaciones=escenario_recuperacion,
    )

    print()
    print("Interpretacion:")
    print("- NORMAL debe partir de benchmark_safe=True y hard_original=0.")
    print("- RECUPERACION puede partir de hard_original>0 y debe declararlo.")
    print("- Las transiciones diagnosticas no modifican la clasificacion tecnica.")


if __name__ == "__main__":
    main()