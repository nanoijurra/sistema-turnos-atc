from __future__ import annotations

import inspect
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from statistics import mean
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.candidate_generation import generate_candidates
from src.candidate_selection import seleccionar_candidatos
from src.exploration_modes import (
    CRITERIO_SELECCION_CANDIDATE_SELECTION_V1,
    ModoExploracion,
    construir_metadata_diagnostico_completo,
    construir_metadata_oferta_rapida,
)
from src.roster_index import build_roster_index
from src.simulator import evaluar_swap
from src.technical_prefilter import filter_technically_plausible_candidates
from tools import benchmark_safe_builder_v2

def _obtener_config_file_benchmark_normal_denso() -> str:
    return CONFIG_FILE_BENCHMARK


def _normalizar_escenario_normal_denso(resultado: Any) -> dict[str, Any]:
    if isinstance(resultado, dict):
        if "config" not in resultado and "configuracion" not in resultado:
            resultado = dict(resultado)
            resultado["config"] = _crear_config_benchmark_normal_denso()

        if "config" not in resultado and "configuracion" in resultado:
            resultado = dict(resultado)
            resultado["config"] = resultado["configuracion"]

        return resultado

    asignaciones = getattr(resultado, "asignaciones", None)
    config = getattr(resultado, "config", None)
    metadata = getattr(resultado, "metadata", None)

    if config is None:
        config = getattr(resultado, "configuracion", None)

    if config is None:
        config = _obtener_config_file_benchmark_normal_denso()

    if metadata is None:
        if is_dataclass(resultado):
            data = asdict(resultado)
            metadata = {
                clave: valor
                for clave, valor in data.items()
                if clave not in {"asignaciones", "config", "configuracion"}
            }
        else:
            metadata = {
                clave: valor
                for clave, valor in vars(resultado).items()
                if clave not in {"asignaciones", "config", "configuracion"}
            }

    if asignaciones is None:
        raise RuntimeError(
            "El escenario NORMAL_DENSO no tiene la estructura esperada. "
            "Se requiere campo/atributo 'asignaciones'. "
            f"Tipo recibido: {type(resultado)!r}. "
            f"Contenido disponible: {resultado!r}"
        )

    return {
        "asignaciones": asignaciones,
        "config": config,
        "metadata": metadata,
    }


def _construir_escenario_normal_denso(escala_controladores: int) -> dict[str, Any]:
    nombres_posibles = (
        "crear_escenario_benchmark_safe_v2",
        "construir_roster_normal_denso",
        "construir_escenario_normal_denso",
        "construir_normal_denso",
        "build_roster_normal_denso",
        "build_normal_denso_roster",
    )

    for nombre in nombres_posibles:
        funcion = getattr(benchmark_safe_builder_v2, nombre, None)

        if callable(funcion):
            resultado = funcion(escala_controladores)
            return _normalizar_escenario_normal_denso(resultado)

    funciones_disponibles = sorted(
        nombre
        for nombre, valor in inspect.getmembers(benchmark_safe_builder_v2)
        if callable(valor) and not nombre.startswith("_")
    )

    raise RuntimeError(
        "No se encontro una funcion compatible para construir NORMAL_DENSO en "
        "tools/benchmark_safe_builder_v2.py. "
        f"Nombres probados: {nombres_posibles}. "
        f"Funciones disponibles: {funciones_disponibles}"
    )

CONFIG_FILE_BENCHMARK = "config_equilibrado.json"


TOP_N_VALUES = [20, 40, 50, 80, 100]
ESCALAS_CONTROLADORES = [80, 120, 180]
ORIGENES_POR_ESCALA = 3


@dataclass(frozen=True)
class ResultadoBenchmarkTopN:
    escala_controladores: int
    modo_exploracion: str
    top_n: int | None
    origenes: int
    candidatos_generados: int
    candidatos_prefiltrados: int
    candidatos_seleccionados: int
    candidatos_evaluados: int
    tiempo_total_ms: float
    clasificaciones: dict[str, int]
    transiciones_diagnosticas: dict[str, int]
    diversidad_controladores: int
    metadata: dict[str, Any]


def _clasificar_transicion_diagnostica(evaluacion: dict[str, Any]) -> str:
    antes = evaluacion.get("antes", {})
    despues = evaluacion.get("despues", {})

    hard_antes = int(antes.get("hard", 0))
    hard_despues = int(despues.get("hard", 0))
    score_antes = float(antes.get("score", 0))
    score_despues = float(despues.get("score", 0))

    antes_valido = hard_antes == 0
    despues_valido = hard_despues == 0

    if antes_valido and despues_valido:
        if score_despues > score_antes:
            return "VV_MEJORA"
        if score_despues == score_antes:
            return "VV_IGUAL"
        return "VV_EMPEORA"

    if antes_valido and not despues_valido:
        return "VI_DEGRADA"

    if not antes_valido and despues_valido:
        return "IV_RECUPERA"

    if hard_despues < hard_antes:
        return "II_MEJORA"
    if hard_despues == hard_antes:
        return "II_IGUAL"
    return "II_EMPEORA"


def _extraer_controlador(asignacion: Any) -> str:
    if isinstance(asignacion, dict):
        return str(asignacion.get("controlador", ""))

    return str(getattr(asignacion, "controlador", ""))


def _seleccionar_origenes(asignaciones: list[Any], cantidad: int) -> list[Any]:
    return asignaciones[:cantidad]

def _generar_candidatos_future(
    *,
    asignacion_origen: Any,
    asignaciones: list[Any],
    roster_index: Any,
) -> list[Any]:
    firma = inspect.signature(generate_candidates)
    parametros = list(firma.parameters)
    if parametros == ["asignacion_origen", "roster_index", "mode"]:
        return generate_candidates(
            asignacion_origen,
            roster_index,
            "future",
        )
    
    if parametros == ["asignacion_origen", "asignaciones", "roster_index", "mode"]:
        return generate_candidates(
            asignacion_origen,
            asignaciones,
            roster_index,
            "future",
        )

    if parametros == ["asignacion_origen", "asignaciones", "roster_index", "modo"]:
        return generate_candidates(
            asignacion_origen,
            asignaciones,
            roster_index,
            "future",
        )

    if parametros == ["asignacion_origen", "asignaciones", "mode"]:
        return generate_candidates(
            asignacion_origen,
            asignaciones,
            "future",
        )

    if parametros == ["asignacion_origen", "asignaciones", "modo"]:
        return generate_candidates(
            asignacion_origen,
            asignaciones,
            "future",
        )

    if parametros == ["asignaciones", "roster_index", "asignacion_origen", "mode"]:
        return generate_candidates(
            asignaciones,
            roster_index,
            asignacion_origen,
            "future",
        )

    if parametros == ["asignaciones", "roster_index", "asignacion_origen", "modo"]:
        return generate_candidates(
            asignaciones,
            roster_index,
            asignacion_origen,
            "future",
        )

    if parametros == ["mode", "asignacion_origen", "asignaciones", "roster_index"]:
        return generate_candidates(
            "future",
            asignacion_origen,
            asignaciones,
            roster_index,
        )

    if parametros == ["modo", "asignacion_origen", "asignaciones", "roster_index"]:
        return generate_candidates(
            "future",
            asignacion_origen,
            asignaciones,
            roster_index,
        )

    try:
        return generate_candidates(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            roster_index=roster_index,
            mode="future",
        )
    except TypeError:
        pass

    try:
        return generate_candidates(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            roster_index=roster_index,
            modo="future",
        )
    except TypeError:
        pass

    raise RuntimeError(
        "No se pudo invocar generate_candidates con una firma compatible. "
        f"Firma detectada: {firma}"
    )

def _obtener_indice_asignacion(
    asignaciones: list[Any],
    asignacion_buscada: Any,
) -> int:
    for idx, asignacion in enumerate(asignaciones):
        if asignacion is asignacion_buscada:
            return idx

    for idx, asignacion in enumerate(asignaciones):
        if asignacion == asignacion_buscada:
            return idx

    raise RuntimeError(
        "No se encontro la asignacion dentro del roster base. "
        f"Asignacion buscada: {asignacion_buscada!r}"
    )

def _evaluar_candidatos(
    *,
    asignacion_origen: Any,
    candidatos: list[Any],
    asignaciones: list[Any],
    config: str,
) -> tuple[list[dict[str, Any]], int]:
    evaluaciones: list[dict[str, Any]] = []
    controladores = {_extraer_controlador(asignacion_origen)}

    idx_origen = _obtener_indice_asignacion(asignaciones, asignacion_origen)

    for candidato in candidatos:
        idx_candidato = _obtener_indice_asignacion(asignaciones, candidato)
        controladores.add(_extraer_controlador(candidato))

        evaluacion = evaluar_swap(
            asignaciones,
            idx_origen,
            idx_candidato,
            config,
        )
        evaluaciones.append(evaluacion)

    return evaluaciones, len(controladores)


def _resumir_evaluaciones(
    evaluaciones: list[dict[str, Any]],
) -> tuple[dict[str, int], dict[str, int]]:
    clasificaciones = Counter()
    transiciones = Counter()

    for evaluacion in evaluaciones:
        clasificacion = str(evaluacion.get("clasificacion", "SIN_CLASIFICACION"))
        clasificaciones[clasificacion] += 1

        transicion = _clasificar_transicion_diagnostica(evaluacion)
        transiciones[transicion] += 1

    return dict(clasificaciones), dict(transiciones)


def _medir_diagnostico_completo(
    *,
    escala_controladores: int,
    asignaciones: list[Any],
    config: str,
    origenes: list[Any],
) -> ResultadoBenchmarkTopN:
    inicio_total = time.perf_counter()

    total_generados = 0
    total_prefiltrados = 0
    evaluaciones_totales: list[dict[str, Any]] = []
    diversidad_total = 0
    t_generation = 0.0
    t_prefilter = 0.0
    t_simulator = 0.0

    roster_index = build_roster_index(asignaciones)

    for asignacion_origen in origenes:
        inicio_generation = time.perf_counter()
        candidatos_generados = _generar_candidatos_future(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            roster_index=roster_index,
        )
        t_generation += (time.perf_counter() - inicio_generation) * 1000

        inicio_prefilter = time.perf_counter()
        candidatos_prefiltrados = filter_technically_plausible_candidates(
            asignacion_origen,
            candidatos_generados,
            asignaciones,
            config,
        )
        t_prefilter += (time.perf_counter() - inicio_prefilter) * 1000

        inicio_simulator = time.perf_counter()
        evaluaciones, diversidad = _evaluar_candidatos(
            asignacion_origen=asignacion_origen,
            candidatos=candidatos_prefiltrados,
            asignaciones=asignaciones,
            config=config,
        )
        diversidad_total += diversidad

        t_simulator += (time.perf_counter() - inicio_simulator) * 1000

        total_generados += len(candidatos_generados)
        total_prefiltrados += len(candidatos_prefiltrados)
        evaluaciones_totales.extend(evaluaciones)

    tiempo_total_ms = (time.perf_counter() - inicio_total) * 1000

    clasificaciones, transiciones = _resumir_evaluaciones(evaluaciones_totales)

    metadata = construir_metadata_diagnostico_completo(
        candidatos_generados=total_generados,
        candidatos_prefiltrados=total_prefiltrados,
        candidatos_evaluados=len(evaluaciones_totales),
        tiempos_por_etapa={
            "candidate_generation_ms": t_generation,
            "technical_prefilter_ms": t_prefilter,
            "simulator_ms": t_simulator,
            "total_ms": tiempo_total_ms,
        },
    )

    return ResultadoBenchmarkTopN(
        escala_controladores=escala_controladores,
        modo_exploracion=ModoExploracion.DIAGNOSTICO_COMPLETO.value,
        top_n=None,
        origenes=len(origenes),
        candidatos_generados=total_generados,
        candidatos_prefiltrados=total_prefiltrados,
        candidatos_seleccionados=total_prefiltrados,
        candidatos_evaluados=len(evaluaciones_totales),
        tiempo_total_ms=tiempo_total_ms,
        clasificaciones=clasificaciones,
        transiciones_diagnosticas=transiciones,
        diversidad_controladores=diversidad_total,
        metadata=metadata.to_dict(),
    )


def _medir_oferta_rapida(
    *,
    escala_controladores: int,
    asignaciones: list[Any],
    config: str,
    origenes: list[Any],
    top_n: int,
) -> ResultadoBenchmarkTopN:
    inicio_total = time.perf_counter()

    total_generados = 0
    total_prefiltrados = 0
    total_seleccionados = 0
    evaluaciones_totales: list[dict[str, Any]] = []
    diversidad_total = 0

    t_generation = 0.0
    t_prefilter = 0.0
    t_selection = 0.0
    t_simulator = 0.0

    roster_index = build_roster_index(asignaciones)

    for asignacion_origen in origenes:
        inicio_generation = time.perf_counter()
        candidatos_generados = _generar_candidatos_future(
            asignacion_origen=asignacion_origen,
            asignaciones=asignaciones,
            roster_index=roster_index,
        )
        t_generation += (time.perf_counter() - inicio_generation) * 1000

        inicio_prefilter = time.perf_counter()
        candidatos_prefiltrados = filter_technically_plausible_candidates(
            asignacion_origen,
            candidatos_generados,
            asignaciones,
            config,
        )
        t_prefilter += (time.perf_counter() - inicio_prefilter) * 1000

        inicio_selection = time.perf_counter()
        candidatos_seleccionados = seleccionar_candidatos(
            asignacion_origen,
            candidatos_prefiltrados,
            asignaciones,
            top_n=top_n,
        )
        t_selection += (time.perf_counter() - inicio_selection) * 1000

        inicio_simulator = time.perf_counter()
        evaluaciones, diversidad = _evaluar_candidatos(
            asignacion_origen=asignacion_origen,
            candidatos=candidatos_prefiltrados,
            asignaciones=asignaciones,
            config=config,
        )
        diversidad_total += diversidad
        t_simulator += (time.perf_counter() - inicio_simulator) * 1000

        total_generados += len(candidatos_generados)
        total_prefiltrados += len(candidatos_prefiltrados)
        total_seleccionados += len(candidatos_seleccionados)
        evaluaciones_totales.extend(evaluaciones)

    tiempo_total_ms = (time.perf_counter() - inicio_total) * 1000

    clasificaciones, transiciones = _resumir_evaluaciones(evaluaciones_totales)

    metadata = construir_metadata_oferta_rapida(
        candidatos_generados=total_generados,
        candidatos_prefiltrados=total_prefiltrados,
        candidatos_seleccionados=total_seleccionados,
        candidatos_evaluados=len(evaluaciones_totales),
        top_n=top_n,
        tiempos_por_etapa={
            "candidate_generation_ms": t_generation,
            "technical_prefilter_ms": t_prefilter,
            "candidate_selection_ms": t_selection,
            "simulator_ms": t_simulator,
            "total_ms": tiempo_total_ms,
        },
    )

    return ResultadoBenchmarkTopN(
        escala_controladores=escala_controladores,
        modo_exploracion=ModoExploracion.OFERTA_RAPIDA.value,
        top_n=top_n,
        origenes=len(origenes),
        candidatos_generados=total_generados,
        candidatos_prefiltrados=total_prefiltrados,
        candidatos_seleccionados=total_seleccionados,
        candidatos_evaluados=len(evaluaciones_totales),
        tiempo_total_ms=tiempo_total_ms,
        clasificaciones=clasificaciones,
        transiciones_diagnosticas=transiciones,
        diversidad_controladores=diversidad_total,
        metadata=metadata.to_dict(),
    )


def _formatear_counter(data: dict[str, int]) -> str:
    if not data:
        return "-"

    return ", ".join(f"{clave}={valor}" for clave, valor in sorted(data.items()))


def _imprimir_resultado(
    *,
    resultado: ResultadoBenchmarkTopN,
    baseline: ResultadoBenchmarkTopN | None = None,
) -> None:
    ahorro_ms = 0.0
    ahorro_pct = 0.0

    if baseline is not None:
        ahorro_ms = baseline.tiempo_total_ms - resultado.tiempo_total_ms
        if baseline.tiempo_total_ms > 0:
            ahorro_pct = ahorro_ms / baseline.tiempo_total_ms * 100

    top_n_texto = "-" if resultado.top_n is None else str(resultado.top_n)

    print(
        f"{resultado.modo_exploracion:22} "
        f"top_n={top_n_texto:>3} "
        f"eval={resultado.candidatos_evaluados:>5} "
        f"sel={resultado.candidatos_seleccionados:>5} "
        f"total_ms={resultado.tiempo_total_ms:>10.1f} "
        f"ahorro_ms={ahorro_ms:>10.1f} "
        f"ahorro_pct={ahorro_pct:>6.1f}% "
        f"diversidad={resultado.diversidad_controladores:>4}"
    )

    print(f"  clasificacion: {_formatear_counter(resultado.clasificaciones)}")
    print(f"  diagnostico:    {_formatear_counter(resultado.transiciones_diagnosticas)}")
    print(
        "  metadata:       "
        f"modo={resultado.metadata['modo_exploracion']}, "
        f"generados={resultado.metadata['candidatos_generados']}, "
        f"prefiltrados={resultado.metadata['candidatos_prefiltrados']}, "
        f"seleccionados={resultado.metadata['candidatos_seleccionados']}, "
        f"evaluados={resultado.metadata['candidatos_evaluados']}, "
        f"top_n={resultado.metadata['top_n']}, "
        f"criterio={resultado.metadata['criterio_seleccion']}"
    )


def ejecutar_benchmark() -> None:
    print()
    print("Benchmark OFERTA_RAPIDA top-N vs DIAGNOSTICO_COMPLETO")
    print("Sistema de swaps ATC")
    print()
    print("Flujo DIAGNOSTICO_COMPLETO:")
    print("candidate_generation -> technical_prefilter -> simulator")
    print()
    print("Flujo OFERTA_RAPIDA:")
    print("candidate_generation -> technical_prefilter -> candidate_selection -> simulator")
    print()
    print(f"top_n evaluados: {TOP_N_VALUES}")
    print(f"origenes por escala: {ORIGENES_POR_ESCALA}")
    print(f"criterio selection: {CRITERIO_SELECCION_CANDIDATE_SELECTION_V1}")
    print()

    resumen_por_escala: list[tuple[int, ResultadoBenchmarkTopN, list[ResultadoBenchmarkTopN]]] = []

    for escala in ESCALAS_CONTROLADORES:
        escenario = _construir_escenario_normal_denso(escala)
        asignaciones = escenario["asignaciones"]
        config = escenario["config"]
        metadata_escenario = escenario["metadata"]

        origenes = _seleccionar_origenes(asignaciones, ORIGENES_POR_ESCALA)

        print("=" * 150)
        print(f"ESCALA {escala} CONTROLADORES - NORMAL_DENSO")
        print(
            "Metadata escenario: "
            f"modo={metadata_escenario.get('modo')}, "
            f"safe={metadata_escenario.get('safe')}, "
            f"useful={metadata_escenario.get('useful')}, "
            f"valido={metadata_escenario.get('valido')}, "
            f"hard={metadata_escenario.get('hard')}, "
            f"soft={metadata_escenario.get('soft')}, "
            f"score={metadata_escenario.get('score')}, "
            f"asignaciones={metadata_escenario.get('asignaciones')}, "
            f"candidate_count={metadata_escenario.get('candidate_count')}, "
            f"simulable_count={metadata_escenario.get('simulable_count')}, "
            f"densidad={metadata_escenario.get('densidad')}"
        )
        print("-" * 150)

        baseline = _medir_diagnostico_completo(
            escala_controladores=escala,
            asignaciones=asignaciones,
            config=config,
            origenes=origenes,
        )

        _imprimir_resultado(resultado=baseline)

        resultados_topn: list[ResultadoBenchmarkTopN] = []

        for top_n in TOP_N_VALUES:
            resultado = _medir_oferta_rapida(
                escala_controladores=escala,
                asignaciones=asignaciones,
                config=config,
                origenes=origenes,
                top_n=top_n,
            )
            resultados_topn.append(resultado)
            _imprimir_resultado(resultado=resultado, baseline=baseline)

        resumen_por_escala.append((escala, baseline, resultados_topn))
        print()

    print("=" * 150)
    print("RESUMEN COMPARATIVO")
    print("-" * 150)
    print(
        f"{'Escala':>8} | {'top_n':>5} | {'Eval':>6} | {'Total ms':>10} | "
        f"{'Ahorro ms':>10} | {'Ahorro %':>8} | {'Diversidad':>10} | "
        f"{'Clasificacion':<28} | {'Diagnostico':<28}"
    )
    print("-" * 150)

    for escala, baseline, resultados_topn in resumen_por_escala:
        for resultado in resultados_topn:
            ahorro_ms = baseline.tiempo_total_ms - resultado.tiempo_total_ms
            ahorro_pct = (
                ahorro_ms / baseline.tiempo_total_ms * 100
                if baseline.tiempo_total_ms > 0
                else 0.0
            )

            print(
                f"{escala:>8} | "
                f"{resultado.top_n:>5} | "
                f"{resultado.candidatos_evaluados:>6} | "
                f"{resultado.tiempo_total_ms:>10.1f} | "
                f"{ahorro_ms:>10.1f} | "
                f"{ahorro_pct:>7.1f}% | "
                f"{resultado.diversidad_controladores:>10} | "
                f"{_formatear_counter(resultado.clasificaciones):<28} | "
                f"{_formatear_counter(resultado.transiciones_diagnosticas):<28}"
            )

    promedios_por_top_n: dict[int, list[float]] = {top_n: [] for top_n in TOP_N_VALUES}

    for _, baseline, resultados_topn in resumen_por_escala:
        for resultado in resultados_topn:
            if baseline.tiempo_total_ms > 0 and resultado.top_n is not None:
                ahorro_pct = (
                    baseline.tiempo_total_ms - resultado.tiempo_total_ms
                ) / baseline.tiempo_total_ms * 100
                promedios_por_top_n[resultado.top_n].append(ahorro_pct)

    print()
    print("AHORRO PROMEDIO POR top_n")
    print("-" * 150)

    for top_n, ahorros in promedios_por_top_n.items():
        promedio = mean(ahorros) if ahorros else 0.0
        print(f"top_n={top_n:>3}: ahorro_promedio={promedio:>6.1f}%")


if __name__ == "__main__":
    ejecutar_benchmark()