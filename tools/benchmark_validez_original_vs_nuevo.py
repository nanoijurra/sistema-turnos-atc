from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import explorar_y_evaluar_candidatos_con_prefiltro


ESCALA = 80


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


def _metricas_vacias() -> dict[str, int]:
    return {
        "original_valido_nuevo_valido": 0,
        "original_valido_nuevo_invalido": 0,
        "original_invalido_nuevo_valido": 0,
        "original_invalido_nuevo_invalido": 0,
        "invalido_invalido_mejora": 0,
        "invalido_invalido_igual": 0,
        "invalido_invalido_empeora": 0,
        "BENEFICIOSO": 0,
        "ACEPTABLE": 0,
        "RECHAZABLE": 0,
    }


def _sumar_metricas(destino: dict[str, int], origen: dict[str, int]) -> None:
    for clave, valor in origen.items():
        destino[clave] += valor


def _clasificar_transicion(resultado: dict, metricas: dict[str, int]) -> None:
    valido_original = resultado.get("valido_original")
    valido_nuevo = resultado.get("valido_nuevo")
    hard_original = resultado.get("resumen_original", {}).get("hard")
    hard_nuevo = resultado.get("resumen_nuevo", {}).get("hard")
    clasificacion = resultado.get("clasificacion")

    if clasificacion in {"BENEFICIOSO", "ACEPTABLE", "RECHAZABLE"}:
        metricas[clasificacion] += 1

    if valido_original is True and valido_nuevo is True:
        metricas["original_valido_nuevo_valido"] += 1
        return

    if valido_original is True and valido_nuevo is False:
        metricas["original_valido_nuevo_invalido"] += 1
        return

    if valido_original is False and valido_nuevo is True:
        metricas["original_invalido_nuevo_valido"] += 1
        return

    if valido_original is False and valido_nuevo is False:
        metricas["original_invalido_nuevo_invalido"] += 1

        if hard_original is None or hard_nuevo is None:
            return
        if hard_nuevo < hard_original:
            metricas["invalido_invalido_mejora"] += 1
        elif hard_nuevo == hard_original:
            metricas["invalido_invalido_igual"] += 1
        else:
            metricas["invalido_invalido_empeora"] += 1


def _medir_origen(idx_origen: int, asignaciones: list) -> dict:
    resultados = explorar_y_evaluar_candidatos_con_prefiltro(
        asignacion_origen=asignaciones[idx_origen],
        asignaciones=asignaciones,
        modo="auto",
    )
    metricas = _metricas_vacias()

    for resultado in resultados:
        _clasificar_transicion(resultado, metricas)

    return {
        "evaluados": len(resultados),
        "metricas": metricas,
    }


def _imprimir_fila(idx_origen: int, asignacion_origen, evaluados: int, metricas: dict[str, int]) -> None:
    print(
        f"{idx_origen:>10} | "
        f"{asignacion_origen.controlador.nombre:>18} | "
        f"{str(asignacion_origen.fecha):>12} | "
        f"{asignacion_origen.turno.codigo:>5} | "
        f"{evaluados:>8} | "
        f"{metricas['original_valido_nuevo_valido']:>4} | "
        f"{metricas['original_valido_nuevo_invalido']:>4} | "
        f"{metricas['original_invalido_nuevo_valido']:>4} | "
        f"{metricas['original_invalido_nuevo_invalido']:>4} | "
        f"{metricas['invalido_invalido_mejora']:>9} | "
        f"{metricas['invalido_invalido_igual']:>8} | "
        f"{metricas['invalido_invalido_empeora']:>10} | "
        f"{metricas['BENEFICIOSO']:>7} | "
        f"{metricas['ACEPTABLE']:>7} | "
        f"{metricas['RECHAZABLE']:>7}"
    )


def main() -> None:
    asignaciones = _crear_escenario_escalado(ESCALA)
    indices_origen = [0, len(asignaciones) - 1]
    total_metricas = _metricas_vacias()
    total_evaluados = 0

    print()
    print("Benchmark validez original vs nuevo - sistema de swaps ATC")
    print(f"Escala: {ESCALA} controladores")
    print("-" * 151)
    print(
        f"{'Idx origen':>10} | "
        f"{'Controlador':>18} | "
        f"{'Fecha':>12} | "
        f"{'Turno':>5} | "
        f"{'Eval':>8} | "
        f"{'VV':>4} | "
        f"{'VI':>4} | "
        f"{'IV':>4} | "
        f"{'II':>4} | "
        f"{'II_mej':>9} | "
        f"{'II_igual':>8} | "
        f"{'II_empeora':>10} | "
        f"{'BENEF':>7} | "
        f"{'ACEPT':>7} | "
        f"{'RECH':>7}"
    )
    print("-" * 151)

    for idx_origen in indices_origen:
        medicion = _medir_origen(idx_origen, asignaciones)
        metricas = medicion["metricas"]
        total_evaluados += medicion["evaluados"]
        _sumar_metricas(total_metricas, metricas)
        _imprimir_fila(idx_origen, asignaciones[idx_origen], medicion["evaluados"], metricas)

    print("-" * 151)
    print("Resumen total")
    _imprimir_fila(-1, asignaciones[0], total_evaluados, total_metricas)
    print()


if __name__ == "__main__":
    main()
