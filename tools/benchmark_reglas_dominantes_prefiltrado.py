from __future__ import annotations

import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import (
    explorar_candidatos_acotados,
    explorar_y_evaluar_candidatos_con_prefiltro,
)
from src.technical_prefilter import filter_technically_plausible_candidates


ESCALAS = [80, 120, 180]
TOP_REGLAS_POR_ORIGEN = 5
TOP_REGLAS_POR_ESCALA = 10


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


def _indices_origen_representativos(total_asignaciones: int) -> list[int]:
    candidatos = [
        0,
        total_asignaciones // 4,
        total_asignaciones // 2,
        (total_asignaciones * 3) // 4,
        total_asignaciones - 1,
    ]

    resultado: list[int] = []
    vistos: set[int] = set()
    for indice in candidatos:
        if indice in vistos:
            continue
        vistos.add(indice)
        resultado.append(indice)

    return resultado


def _conteo_clasificaciones(resultados: list[dict]) -> dict[str, int]:
    conteo = {
        "BENEFICIOSO": 0,
        "ACEPTABLE": 0,
        "RECHAZABLE": 0,
    }

    for resultado in resultados:
        conteo[resultado["clasificacion"]] += 1

    return conteo


def _extraer_reglas_hard_dominantes(resultado: dict) -> tuple[Counter, Counter]:
    reglas_presentes = Counter()
    carga_hard = Counter()

    resumen_por_regla_nuevo = resultado.get("resumen_por_regla_nuevo")
    if not isinstance(resumen_por_regla_nuevo, dict):
        return reglas_presentes, carga_hard

    for regla, datos in resumen_por_regla_nuevo.items():
        if not isinstance(datos, dict):
            continue

        hard = datos.get("hard", 0)
        if hard > 0:
            reglas_presentes[regla] += 1
            carga_hard[regla] += hard

    return reglas_presentes, carga_hard


def _formatear_top_reglas(reglas_presentes: Counter, carga_hard: Counter, limite: int) -> str:
    if not reglas_presentes:
        return "sin_regla_hard_clara"

    partes = []
    for regla, cantidad in reglas_presentes.most_common(limite):
        partes.append(f"{regla}={cantidad}(hard_total={carga_hard.get(regla, 0)})")

    return ", ".join(partes)


def _diagnosticar_origen(asignacion_origen, asignaciones: list) -> dict:
    candidatos = explorar_candidatos_acotados(
        asignacion_origen=asignacion_origen,
        asignaciones=asignaciones,
        modo="auto",
    )
    candidatos_prefiltrados = filter_technically_plausible_candidates(
        asignacion_origen=asignacion_origen,
        candidatos=candidatos,
        asignaciones=asignaciones,
    )
    resultados = explorar_y_evaluar_candidatos_con_prefiltro(
        asignacion_origen=asignacion_origen,
        asignaciones=asignaciones,
        modo="auto",
    )

    clasificaciones = _conteo_clasificaciones(resultados)
    reglas_presentes = Counter()
    carga_hard = Counter()
    keys_ejemplo = sorted(list(resultados[0].keys())) if resultados else []
    resultado_swap_keys = []

    for resultado in resultados:
        if not resultado_swap_keys and isinstance(resultado.get("resultado_swap"), dict):
            resultado_swap_keys = sorted(list(resultado["resultado_swap"].keys()))

        if resultado.get("clasificacion") != "RECHAZABLE":
            continue

        if resultado.get("valido_nuevo") is not False:
            continue

        reglas_resultado, carga_resultado = _extraer_reglas_hard_dominantes(resultado)
        reglas_presentes.update(reglas_resultado)
        carga_hard.update(carga_resultado)

    return {
        "simulados": len(candidatos_prefiltrados),
        "rechazables": clasificaciones["RECHAZABLE"],
        "reglas_presentes": reglas_presentes,
        "carga_hard": carga_hard,
        "keys_ejemplo": keys_ejemplo,
        "resultado_swap_keys": resultado_swap_keys,
    }


def main() -> None:
    print()
    print("Benchmark de reglas dominantes prefiltrado - sistema de swaps ATC")

    for cantidad_controladores in ESCALAS:
        asignaciones = _crear_escenario_escalado(cantidad_controladores)
        indices_origen = _indices_origen_representativos(len(asignaciones))

        print()
        print(f"ESCALA {cantidad_controladores} CONTROLADORES")
        print("-" * 190)
        print(
            f"{'Idx origen':>10} | "
            f"{'Controlador origen':>20} | "
            f"{'Fecha origen':>12} | "
            f"{'Turno':>5} | "
            f"{'Simulados':>10} | "
            f"{'Rechazables':>12} | "
            f"{'Top reglas responsables':<95}"
        )
        print("-" * 190)

        reglas_escala = Counter()
        carga_hard_escala = Counter()
        total_simulados = 0
        total_rechazables = 0
        keys_ejemplo_escala: list[str] = []
        resultado_swap_keys_escala: list[str] = []

        for idx_origen in indices_origen:
            asignacion_origen = asignaciones[idx_origen]
            diagnostico = _diagnosticar_origen(asignacion_origen, asignaciones)

            total_simulados += diagnostico["simulados"]
            total_rechazables += diagnostico["rechazables"]
            reglas_escala.update(diagnostico["reglas_presentes"])
            carga_hard_escala.update(diagnostico["carga_hard"])

            if not keys_ejemplo_escala and diagnostico["keys_ejemplo"]:
                keys_ejemplo_escala = diagnostico["keys_ejemplo"]
            if not resultado_swap_keys_escala and diagnostico["resultado_swap_keys"]:
                resultado_swap_keys_escala = diagnostico["resultado_swap_keys"]

            print(
                f"{idx_origen:>10} | "
                f"{asignacion_origen.controlador.nombre:>20} | "
                f"{str(asignacion_origen.fecha):>12} | "
                f"{asignacion_origen.turno.codigo:>5} | "
                f"{diagnostico['simulados']:>10} | "
                f"{diagnostico['rechazables']:>12} | "
                f"{_formatear_top_reglas(diagnostico['reglas_presentes'], diagnostico['carga_hard'], TOP_REGLAS_POR_ORIGEN):<95}"
            )

        print("-" * 190)
        print(
            f"Resumen escala {cantidad_controladores}: total_simulados={total_simulados}, total_rechazables={total_rechazables}"
        )
        print(
            f"Ranking agregado de reglas hard dominantes: {_formatear_top_reglas(reglas_escala, carga_hard_escala, TOP_REGLAS_POR_ESCALA)}"
        )

        if keys_ejemplo_escala:
            print(f"Keys resultado tecnico: {', '.join(keys_ejemplo_escala)}")
        else:
            print("Keys resultado tecnico: sin_resultados")

        if resultado_swap_keys_escala:
            print(f"Keys resultado_swap: {', '.join(resultado_swap_keys_escala)}")
        else:
            print("Keys resultado_swap: sin_resultado_swap")

    print()


if __name__ == "__main__":
    main()
