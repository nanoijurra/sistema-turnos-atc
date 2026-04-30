from __future__ import annotations

from dataclasses import replace
from time import perf_counter

try:
    from tools.bootstrap_path import ensure_project_root_on_path
except ModuleNotFoundError:
    from bootstrap_path import ensure_project_root_on_path

ensure_project_root_on_path()

from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import (
    explorar_candidatos_acotados,
    explorar_y_evaluar_candidatos_con_prefiltro,
)
from src.technical_prefilter import filter_technically_plausible_candidates


ESCALAS = [80, 120, 180]


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


def _promedio(valores: list[float]) -> float:
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


def _medir_origen(asignacion_origen, asignaciones: list) -> dict:
    inicio = perf_counter()
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
    fin = perf_counter()

    clasificaciones = _conteo_clasificaciones(resultados)

    return {
        "generados": len(candidatos),
        "prefiltrados": len(candidatos_prefiltrados),
        "tiempo_total_ms": (fin - inicio) * 1000.0,
        "BENEFICIOSO": clasificaciones["BENEFICIOSO"],
        "ACEPTABLE": clasificaciones["ACEPTABLE"],
        "RECHAZABLE": clasificaciones["RECHAZABLE"],
    }


def main() -> None:
    print()
    print("Benchmark de origenes prefiltrados - sistema de swaps ATC")

    for cantidad_controladores in ESCALAS:
        asignaciones = _crear_escenario_escalado(cantidad_controladores)
        indices_origen = _indices_origen_representativos(len(asignaciones))

        print()
        print(f"ESCALA {cantidad_controladores} CONTROLADORES")
        print("-" * 166)
        print(
            f"{'Idx origen':>10} | "
            f"{'Controlador origen':>20} | "
            f"{'Fecha origen':>12} | "
            f"{'Turno':>5} | "
            f"{'Generados':>10} | "
            f"{'Pref/Sim':>10} | "
            f"{'Total ms':>10} | "
            f"{'BENEF':>7} | "
            f"{'ACEPT':>7} | "
            f"{'RECH':>7}"
        )
        print("-" * 166)

        tiempos: list[float] = []
        simulados: list[int] = []
        total_beneficioso = 0
        total_aceptable = 0
        total_rechazable = 0

        for idx_origen in indices_origen:
            asignacion_origen = asignaciones[idx_origen]
            medicion = _medir_origen(asignacion_origen, asignaciones)

            tiempos.append(medicion["tiempo_total_ms"])
            simulados.append(medicion["prefiltrados"])
            total_beneficioso += medicion["BENEFICIOSO"]
            total_aceptable += medicion["ACEPTABLE"]
            total_rechazable += medicion["RECHAZABLE"]

            print(
                f"{idx_origen:>10} | "
                f"{asignacion_origen.controlador.nombre:>20} | "
                f"{str(asignacion_origen.fecha):>12} | "
                f"{asignacion_origen.turno.codigo:>5} | "
                f"{medicion['generados']:>10} | "
                f"{medicion['prefiltrados']:>10} | "
                f"{medicion['tiempo_total_ms']:>10.2f} | "
                f"{medicion['BENEFICIOSO']:>7} | "
                f"{medicion['ACEPTABLE']:>7} | "
                f"{medicion['RECHAZABLE']:>7}"
            )

        print("-" * 166)
        print(
            f"Resumen escala {cantidad_controladores}: "
            f"promedio_tiempo_ms={_promedio(tiempos):.2f}, "
            f"promedio_simulados={_promedio(simulados):.2f}, "
            f"total_BENEFICIOSO={total_beneficioso}, "
            f"total_ACEPTABLE={total_aceptable}, "
            f"total_RECHAZABLE={total_rechazable}"
        )

    print()


if __name__ == "__main__":
    main()
