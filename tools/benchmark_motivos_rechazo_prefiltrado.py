from __future__ import annotations

from collections import Counter
from dataclasses import replace

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
TOP_MOTIVOS_POR_ORIGEN = 5
TOP_MOTIVOS_POR_ESCALA = 10


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


def _reglas_con_incremento(
    resumen_original: dict | None,
    resumen_nuevo: dict | None,
) -> list[str]:
    if not isinstance(resumen_original, dict) or not isinstance(resumen_nuevo, dict):
        return []

    reglas = sorted(set(resumen_original.keys()) | set(resumen_nuevo.keys()))
    motivos: list[str] = []

    for regla in reglas:
        datos_original = resumen_original.get(regla, {})
        datos_nuevo = resumen_nuevo.get(regla, {})

        total_original = datos_original.get("total", 0)
        total_nuevo = datos_nuevo.get("total", 0)
        hard_original = datos_original.get("hard", 0)
        hard_nuevo = datos_nuevo.get("hard", 0)
        soft_original = datos_original.get("soft", 0)
        soft_nuevo = datos_nuevo.get("soft", 0)

        if hard_nuevo > hard_original:
            motivos.append(f"regla_hard:{regla}")
        elif total_nuevo > total_original:
            motivos.append(f"regla_total:{regla}")
        elif soft_nuevo > soft_original:
            motivos.append(f"regla_soft:{regla}")

    return motivos


def _extraer_motivos_rechazo(resultado: dict, keys_ejemplo: list[str]) -> list[str]:
    motivos: list[str] = []

    if resultado.get("valido_nuevo") is False:
        motivos.append("roster_invalido")

    if resultado.get("delta_hard", 0) > 0:
        motivos.append("aumento_hard")

    if resultado.get("delta_total_violaciones", 0) > 0:
        motivos.append("aumento_violaciones")

    motivos.extend(
        _reglas_con_incremento(
            resultado.get("resumen_por_regla_original"),
            resultado.get("resumen_por_regla_nuevo"),
        )
    )

    if not motivos:
        if keys_ejemplo:
            motivos.append(f"sin_motivo_claro(keys={','.join(keys_ejemplo)})")
        else:
            motivos.append("sin_motivo_claro")

    return motivos


def _formatear_top(counter: Counter, limite: int) -> str:
    if not counter:
        return "sin_motivo_claro"

    partes = [f"{motivo}={cantidad}" for motivo, cantidad in counter.most_common(limite)]
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
    keys_ejemplo = sorted(list(resultados[0].keys())) if resultados else []
    motivos = Counter()

    for resultado in resultados:
        if resultado.get("clasificacion") != "RECHAZABLE":
            continue
        motivos.update(_extraer_motivos_rechazo(resultado, keys_ejemplo))

    return {
        "generados": len(candidatos),
        "prefiltrados": len(candidatos_prefiltrados),
        "BENEFICIOSO": clasificaciones["BENEFICIOSO"],
        "ACEPTABLE": clasificaciones["ACEPTABLE"],
        "RECHAZABLE": clasificaciones["RECHAZABLE"],
        "motivos": motivos,
        "keys_ejemplo": keys_ejemplo,
    }


def main() -> None:
    print()
    print("Benchmark diagnostico de motivos de rechazo prefiltrado - sistema de swaps ATC")

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
            f"{'Generados':>10} | "
            f"{'Pref/Sim':>10} | "
            f"{'BENEF':>7} | "
            f"{'ACEPT':>7} | "
            f"{'RECH':>7} | "
            f"{'Top motivos o violaciones':<80}"
        )
        print("-" * 190)

        total_simulados = 0
        total_rechazables = 0
        motivos_escala = Counter()
        keys_ejemplo_escala: list[str] = []

        for idx_origen in indices_origen:
            asignacion_origen = asignaciones[idx_origen]
            diagnostico = _diagnosticar_origen(asignacion_origen, asignaciones)

            total_simulados += diagnostico["prefiltrados"]
            total_rechazables += diagnostico["RECHAZABLE"]
            motivos_escala.update(diagnostico["motivos"])
            if not keys_ejemplo_escala and diagnostico["keys_ejemplo"]:
                keys_ejemplo_escala = diagnostico["keys_ejemplo"]

            print(
                f"{idx_origen:>10} | "
                f"{asignacion_origen.controlador.nombre:>20} | "
                f"{str(asignacion_origen.fecha):>12} | "
                f"{asignacion_origen.turno.codigo:>5} | "
                f"{diagnostico['generados']:>10} | "
                f"{diagnostico['prefiltrados']:>10} | "
                f"{diagnostico['BENEFICIOSO']:>7} | "
                f"{diagnostico['ACEPTABLE']:>7} | "
                f"{diagnostico['RECHAZABLE']:>7} | "
                f"{_formatear_top(diagnostico['motivos'], TOP_MOTIVOS_POR_ORIGEN):<80}"
            )

        print("-" * 190)
        print(f"Resumen escala {cantidad_controladores}: total_simulados={total_simulados}, total_rechazables={total_rechazables}")
        print(
            f"Conteo agregado de motivos/violaciones: {_formatear_top(motivos_escala, TOP_MOTIVOS_POR_ESCALA)}"
        )

        if keys_ejemplo_escala:
            print(f"Keys ejemplo resultado tecnico: {', '.join(keys_ejemplo_escala)}")
        else:
            print("Keys ejemplo resultado tecnico: sin_resultados")

    print()


if __name__ == "__main__":
    main()
