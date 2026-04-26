from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario
from src.simulator import explorar_y_evaluar_candidatos_con_prefiltro


ESCALAS = [80, 120, 180]
CLASIFICACIONES = ["BENEFICIOSO", "ACEPTABLE", "RECHAZABLE"]
DIAGNOSTICOS = [
    "VV_MEJORA",
    "VV_IGUAL",
    "VV_EMPEORA",
    "VI_DEGRADA",
    "IV_RECUPERA",
    "II_MEJORA",
    "II_IGUAL",
    "II_EMPEORA",
    "SIN_DATO",
]


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


def diagnosticar_transicion_tecnica(resultado: dict) -> str:
    valido_original = resultado.get("valido_original")
    valido_nuevo = resultado.get("valido_nuevo")
    delta_hard = resultado.get("delta_hard")
    delta_soft = resultado.get("delta_soft")
    delta_score = resultado.get("delta_score")

    if valido_original is None or valido_nuevo is None:
        return "SIN_DATO"

    if valido_original is True and valido_nuevo is True:
        if delta_hard is not None and delta_hard < 0:
            return "VV_MEJORA"
        if delta_hard is not None and delta_hard > 0:
            return "VV_EMPEORA"
        if delta_soft is not None and delta_soft < 0:
            return "VV_MEJORA"
        if delta_soft is not None and delta_soft > 0:
            return "VV_EMPEORA"
        if delta_score is not None and delta_score > 0:
            return "VV_MEJORA"
        if delta_score is not None and delta_score < 0:
            return "VV_EMPEORA"
        if delta_hard is not None or delta_soft is not None or delta_score is not None:
            return "VV_IGUAL"
        return "SIN_DATO"

    if valido_original is True and valido_nuevo is False:
        return "VI_DEGRADA"

    if valido_original is False and valido_nuevo is True:
        return "IV_RECUPERA"

    if valido_original is False and valido_nuevo is False:
        if delta_hard is None:
            return "SIN_DATO"
        if delta_hard < 0:
            return "II_MEJORA"
        if delta_hard == 0:
            return "II_IGUAL"
        return "II_EMPEORA"

    return "SIN_DATO"


def _conteos_vacios(claves: list[str]) -> dict[str, int]:
    return {clave: 0 for clave in claves}


def _sumar_conteos(destino: dict[str, int], origen: dict[str, int]) -> None:
    for clave, valor in origen.items():
        destino[clave] += valor


def _medir_origen(idx_origen: int, asignaciones: list) -> dict:
    resultados = explorar_y_evaluar_candidatos_con_prefiltro(
        asignacion_origen=asignaciones[idx_origen],
        asignaciones=asignaciones,
        modo="auto",
    )
    clasificaciones = _conteos_vacios(CLASIFICACIONES)
    diagnosticos = _conteos_vacios(DIAGNOSTICOS)

    for resultado in resultados:
        clasificacion = resultado.get("clasificacion")
        if clasificacion in clasificaciones:
            clasificaciones[clasificacion] += 1
        else:
            diagnosticos["SIN_DATO"] += 1

        diagnostico = diagnosticar_transicion_tecnica(resultado)
        diagnosticos[diagnostico] += 1

    return {
        "evaluados": len(resultados),
        "clasificaciones": clasificaciones,
        "diagnosticos": diagnosticos,
    }


def _fmt_conteos(conteos: dict[str, int], claves: list[str]) -> str:
    return ", ".join(f"{clave}={conteos[clave]}" for clave in claves if conteos[clave] > 0) or "sin_datos"


def _imprimir_origen(idx_origen: int, asignacion_origen, medicion: dict) -> None:
    print(
        f"{idx_origen:>10} | "
        f"{asignacion_origen.controlador.nombre:>18} | "
        f"{str(asignacion_origen.fecha):>12} | "
        f"{asignacion_origen.turno.codigo:>5} | "
        f"{medicion['evaluados']:>8} | "
        f"{_fmt_conteos(medicion['clasificaciones'], CLASIFICACIONES):<44} | "
        f"{_fmt_conteos(medicion['diagnosticos'], DIAGNOSTICOS)}"
    )


def main() -> None:
    print()
    print("Benchmark transiciones diagnosticas - sistema de swaps ATC")
    print("Nota: esta taxonomia no cambia la clasificacion tecnica, el ranking ni la decision.")

    for escala in ESCALAS:
        asignaciones = _crear_escenario_escalado(escala)
        indices_origen = [0, len(asignaciones) - 1]
        total_clasificaciones = _conteos_vacios(CLASIFICACIONES)
        total_diagnosticos = _conteos_vacios(DIAGNOSTICOS)
        total_evaluados = 0

        print()
        print(f"ESCALA {escala} CONTROLADORES")
        print("-" * 170)
        print(
            f"{'Idx origen':>10} | "
            f"{'Controlador':>18} | "
            f"{'Fecha':>12} | "
            f"{'Turno':>5} | "
            f"{'Eval':>8} | "
            f"{'Clasificacion tecnica':<44} | "
            f"Diagnostico"
        )
        print("-" * 170)

        for idx_origen in indices_origen:
            medicion = _medir_origen(idx_origen, asignaciones)
            total_evaluados += medicion["evaluados"]
            _sumar_conteos(total_clasificaciones, medicion["clasificaciones"])
            _sumar_conteos(total_diagnosticos, medicion["diagnosticos"])
            _imprimir_origen(idx_origen, asignaciones[idx_origen], medicion)

        print("-" * 170)
        print(f"Resumen escala {escala}: evaluados={total_evaluados}")
        print(f"Clasificacion tecnica: {_fmt_conteos(total_clasificaciones, CLASIFICACIONES)}")
        print(f"Transicion diagnostica: {_fmt_conteos(total_diagnosticos, DIAGNOSTICOS)}")

    print()
    print("Notas:")
    print("- La taxonomia diagnostica es solo reporting de benchmark.")
    print("- No modifica clasificacion tecnica, ranking ni decision operativa.")
    print()


if __name__ == "__main__":
    main()
