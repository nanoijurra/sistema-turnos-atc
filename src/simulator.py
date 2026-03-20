from copy import deepcopy
from dataclasses import replace
from datetime import date

from src.engine import validar_todo
from src.scoring import es_roster_valido, calcular_score
from src.rule_types import RuleResult


def mostrar_roster(asignaciones: list) -> None:
    """
    Muestra el roster con índice, controlador, fecha, código y categoría.
    """
    for idx, asignacion in enumerate(asignaciones):
        nombre_controlador = (
            asignacion.controlador.nombre
            if asignacion.controlador is not None
            else "SIN_CONTROLADOR"
        )

        print(
            f"[{idx}] {nombre_controlador} | "
            f"{asignacion.fecha} | "
            f"{asignacion.turno.codigo} | "
            f"{asignacion.turno.categoria}"
        )

def generar_recomendacion_textual(evaluacion: dict) -> str:
    """
    Genera una explicación textual incluyendo impacto por controlador.
    """
    swap = evaluacion["swap"]
    idx_a = swap["idx_a"]
    idx_b = swap["idx_b"]

    partes = [f"Swap recomendado: {idx_a} ↔ {idx_b}."]

    # estado global
    if evaluacion["valido_nuevo"]:
        partes.append("El roster resultante queda válido.")
    else:
        partes.append("El roster resultante sigue siendo inválido.")

    # impacto global
    if evaluacion["delta_hard"] < 0:
        partes.append(f"Reduce violaciones hard en {abs(evaluacion['delta_hard'])}.")
    elif evaluacion["delta_hard"] > 0:
        partes.append(f"Aumenta violaciones hard en {evaluacion['delta_hard']}.")

    if evaluacion["delta_total_violaciones"] < 0:
        partes.append(
            f"Reduce violaciones totales en {abs(evaluacion['delta_total_violaciones'])}."
        )
    elif evaluacion["delta_total_violaciones"] > 0:
        partes.append(
            f"Aumenta violaciones totales en {evaluacion['delta_total_violaciones']}."
        )

    # 🔥 impacto por controlador
    antes = evaluacion.get("resumen_por_controlador_original", {})
    despues = evaluacion.get("resumen_por_controlador_nuevo", {})

    cambios_controladores = []

    for ctrl, datos_antes in antes.items():
        datos_despues = despues.get(ctrl)

        if not datos_despues:
            continue

        delta_hard = datos_despues["violaciones"]["hard"] - datos_antes["violaciones"]["hard"]
        delta_total = datos_despues["violaciones"]["total"] - datos_antes["violaciones"]["total"]
        cambio_validez = datos_antes["valido"] != datos_despues["valido"]

        if delta_hard < 0 or delta_total < 0 or (datos_antes["valido"] is False and datos_despues["valido"] is True):
            cambios_controladores.append(
                f"{ctrl} mejora (hard {datos_antes['violaciones']['hard']}→{datos_despues['violaciones']['hard']})"
            )

        elif delta_hard > 0 or delta_total > 0 or cambio_validez:
            cambios_controladores.append(
                f"{ctrl} empeora (hard {datos_antes['violaciones']['hard']}→{datos_despues['violaciones']['hard']})"
            )

    if cambios_controladores:
        partes.append("Impacto por controlador: " + "; ".join(cambios_controladores) + ".")

    partes.append(f"Impacto calculado: {evaluacion['impacto']}.")

    return " ".join(partes)

def buscar_indice_asignacion(
    asignaciones: list,
    fecha: date,
    codigo_turno: str | None = None,
) -> int:
    """
    Busca una asignación por fecha y, opcionalmente, código de turno.
    Devuelve el índice dentro de la lista.
    """
    candidatos = []

    for idx, asignacion in enumerate(asignaciones):
        if asignacion.fecha != fecha:
            continue

        if codigo_turno is not None and asignacion.turno.codigo != codigo_turno:
            continue

        candidatos.append(idx)

    if not candidatos:
        raise ValueError(
            f"No se encontró asignación para fecha={fecha} y codigo_turno={codigo_turno}."
        )

    if len(candidatos) > 1:
        raise ValueError(
            f"Búsqueda ambigua para fecha={fecha} y codigo_turno={codigo_turno}. "
            f"Se encontraron múltiples asignaciones: {candidatos}"
        )

    return candidatos[0]

def buscar_indice_asignacion_por_controlador(
    asignaciones: list,
    controlador_nombre: str,
    fecha: date,
    codigo_turno: str | None = None,
) -> int:
    """
    Busca una asignación por controlador, fecha y opcionalmente código de turno.
    """
    candidatos = []

    for idx, asignacion in enumerate(asignaciones):
        if asignacion.controlador is None:
            continue

        if asignacion.controlador.nombre != controlador_nombre:
            continue

        if asignacion.fecha != fecha:
            continue

        if codigo_turno is not None and asignacion.turno.codigo != codigo_turno:
            continue

        candidatos.append(idx)

    if not candidatos:
        raise ValueError(
            f"No se encontró asignación para controlador={controlador_nombre}, "
            f"fecha={fecha}, codigo_turno={codigo_turno}."
        )

    if len(candidatos) > 1:
        raise ValueError(
            f"Búsqueda ambigua para controlador={controlador_nombre}, "
            f"fecha={fecha}, codigo_turno={codigo_turno}. "
            f"Se encontraron múltiples asignaciones: {candidatos}"
        )

    return candidatos[0]


def resumir_violaciones(resultados: list[RuleResult]) -> dict:
    """
    Resume cantidad total de violaciones, hard y soft.
    """
    total = 0
    hard = 0
    soft = 0

    for resultado in resultados:
        for violacion in resultado.violaciones:
            total += 1
            if violacion.severidad == "hard":
                hard += 1
            elif violacion.severidad == "soft":
                soft += 1

    return {
        "total": total,
        "hard": hard,
        "soft": soft,
    }
def resumir_violaciones_por_regla(resultados: list[RuleResult]) -> dict:
    """
    Resume violaciones por regla, separando total, hard y soft.
    """
    resumen = {}

    for resultado in resultados:
        total = len(resultado.violaciones)
        hard = sum(1 for v in resultado.violaciones if v.severidad == "hard")
        soft = sum(1 for v in resultado.violaciones if v.severidad == "soft")

        resumen[resultado.regla] = {
            "total": total,
            "hard": hard,
            "soft": soft,
        }

    return resumen

def resumir_violaciones_por_controlador(
    asignaciones: list,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Evalúa el roster separando por controlador y devuelve un resumen por controlador.
    """
    from src.engine import agrupar_por_controlador

    grupos = agrupar_por_controlador(asignaciones)
    resumen = {}

    for nombre_controlador, asignaciones_ctrl in grupos.items():
        resultados = validar_todo(asignaciones_ctrl, config_file)
        resumen[nombre_controlador] = {
            "valido": es_roster_valido(resultados),
            "score": calcular_score(resultados),
            "violaciones": resumir_violaciones(resultados),
            "por_regla": resumir_violaciones_por_regla(resultados),
        }

    return resumen

def calcular_impacto(evaluacion: dict) -> int:
    """
    Calcula un score de impacto para ordenar swaps.
    Penaliza hard y total; bonifica mejoras.
    """
    # menos hard = mejor
    hard = evaluacion["resumen_nuevo"]["hard"]
    total = evaluacion["resumen_nuevo"]["total"]

    # deltas (negativos = mejora)
    delta_hard = evaluacion["delta_hard"]
    delta_total = evaluacion["delta_total_violaciones"]

    impacto = 0

    # prioridad fuerte: eliminar hard
    impacto -= hard * 100

    # luego total
    impacto -= total * 10

    # bonificar mejoras
    impacto += (-delta_hard) * 50
    impacto += (-delta_total) * 5

    # score como ajuste fino
    impacto += evaluacion["score_nuevo"]

    return impacto

def simular_swap(
    asignaciones: list,
    idx_a: int,
    idx_b: int,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Simula un swap entre dos posiciones del roster usando índices.
    """
    if idx_a == idx_b:
        raise ValueError("idx_a e idx_b deben ser distintos.")

    if not (0 <= idx_a < len(asignaciones)) or not (0 <= idx_b < len(asignaciones)):
        raise IndexError("Índices fuera de rango.")

    nuevo_roster = deepcopy(asignaciones)

    turno_a = nuevo_roster[idx_a].turno
    turno_b = nuevo_roster[idx_b].turno

    nuevo_roster[idx_a] = replace(nuevo_roster[idx_a], turno=turno_b)
    nuevo_roster[idx_b] = replace(nuevo_roster[idx_b], turno=turno_a)

    resultados: list[RuleResult] = validar_todo(nuevo_roster, config_file)

    valido = es_roster_valido(resultados)
    score = calcular_score(resultados)

    return {
        "roster": nuevo_roster,
        "resultados": resultados,
        "valido": valido,
        "score": score,
        "swap": {
            "idx_a": idx_a,
            "idx_b": idx_b,
        },
    }


def simular_swap_por_fecha(
    asignaciones: list,
    fecha_a: date,
    fecha_b: date,
    codigo_turno_a: str | None = None,
    codigo_turno_b: str | None = None,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Simula un swap buscando primero las asignaciones por fecha
    y opcionalmente por código de turno.
    """
    idx_a = buscar_indice_asignacion(
        asignaciones,
        fecha=fecha_a,
        codigo_turno=codigo_turno_a,
    )

    idx_b = buscar_indice_asignacion(
        asignaciones,
        fecha=fecha_b,
        codigo_turno=codigo_turno_b,
    )

    return simular_swap(
        asignaciones=asignaciones,
        idx_a=idx_a,
        idx_b=idx_b,
        config_file=config_file,
    )


def evaluar_swap(
    asignaciones: list,
    idx_a: int,
    idx_b: int,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Evalúa un swap comparando el estado antes y después.
    """
    resultados_original = validar_todo(asignaciones, config_file)
    valido_original = es_roster_valido(resultados_original)
    score_original = calcular_score(resultados_original)
    resumen_original = resumir_violaciones(resultados_original)
    resumen_por_regla_original = resumir_violaciones_por_regla(resultados_original)
    resumen_por_controlador_original = resumir_violaciones_por_controlador(
        asignaciones,
        config_file,
    )

    resultado_swap = simular_swap(
        asignaciones,
        idx_a,
        idx_b,
        config_file,
    )

    score_nuevo = resultado_swap["score"]
    valido_nuevo = resultado_swap["valido"]
    resumen_nuevo = resumir_violaciones(resultado_swap["resultados"])
    resumen_por_regla_nuevo = resumir_violaciones_por_regla(resultado_swap["resultados"])
    resumen_por_controlador_nuevo = resumir_violaciones_por_controlador(
        resultado_swap["roster"],
        config_file,
    )

    delta_score = score_nuevo - score_original
    delta_total_violaciones = resumen_nuevo["total"] - resumen_original["total"]
    delta_hard = resumen_nuevo["hard"] - resumen_original["hard"]
    delta_soft = resumen_nuevo["soft"] - resumen_original["soft"]

    return {
        "valido_original": valido_original,
        "score_original": score_original,
        "resumen_original": resumen_original,
        "resumen_por_regla_original": resumen_por_regla_original,
        "resumen_por_controlador_original": resumen_por_controlador_original,
        "valido_nuevo": valido_nuevo,
        "score_nuevo": score_nuevo,
        "resumen_nuevo": resumen_nuevo,
        "resumen_por_regla_nuevo": resumen_por_regla_nuevo,
        "resumen_por_controlador_nuevo": resumen_por_controlador_nuevo,
        "delta_score": delta_score,
        "delta_total_violaciones": delta_total_violaciones,
        "delta_hard": delta_hard,
        "delta_soft": delta_soft,
        "mejora": delta_score > 0 or delta_total_violaciones < 0 or delta_hard < 0,
        "empeora": delta_score < 0 or delta_total_violaciones > 0 or delta_hard > 0,
        "igual": (
            delta_score == 0
            and delta_total_violaciones == 0
            and delta_hard == 0
            and delta_soft == 0
        ),
        "resultado_swap": resultado_swap,
    }

def explorar_swaps(
    asignaciones: list,
    pares: list[tuple[int, int]],
    config_file: str = "config_equilibrado.json",
) -> list[dict]:
    """
    Evalúa múltiples swaps y devuelve un ranking basado en impacto.
    """
    evaluaciones = []

    for idx_a, idx_b in pares:
        evaluacion = evaluar_swap(
            asignaciones=asignaciones,
            idx_a=idx_a,
            idx_b=idx_b,
            config_file=config_file,
        )

        evaluacion["swap"] = {
            "idx_a": idx_a,
            "idx_b": idx_b,
        }

        # 👇 NUEVO: calcular impacto
        evaluacion["impacto"] = calcular_impacto(evaluacion)

        evaluaciones.append(evaluacion)

    # 👇 NUEVO ORDENAMIENTO
    evaluaciones.sort(
        key=lambda e: (
            e["valido_nuevo"],
            e["impacto"],
        ),
        reverse=True,
    )

    return evaluaciones


def generar_pares_swap(
    asignaciones: list,
    limite: int | None = None,
) -> list[tuple[int, int]]:
    """
    Genera pares de índices posibles para swaps.

    Si limite está definido, corta la cantidad de pares generados.
    """
    pares = []
    n = len(asignaciones)

    for i in range(n):
        for j in range(i + 1, n):
            pares.append((i, j))

            if limite is not None and len(pares) >= limite:
                return pares

    return pares


def filtrar_swaps_validos(evaluaciones: list[dict]) -> list[dict]:
    """
    Devuelve solo los swaps cuyo resultado nuevo es válido.
    """
    return [e for e in evaluaciones if e["valido_nuevo"]]


def filtrar_swaps_utiles(evaluaciones: list[dict]) -> list[dict]:
    """
    Devuelve swaps considerados útiles.

    En esta etapa, útil = swap válido y que reduzca violaciones hard o totales.
    """
    return [
        e for e in evaluaciones
        if e["valido_nuevo"] and (e["delta_hard"] < 0 or e["delta_total_violaciones"] < 0)
    ]
def simular_swap_entre_controladores(
    asignaciones: list,
    controlador_a: str,
    fecha_a: date,
    controlador_b: str,
    fecha_b: date,
    codigo_turno_a: str | None = None,
    codigo_turno_b: str | None = None,
    config_file: str = "config_equilibrado.json",
) -> dict:
    """
    Simula un swap entre asignaciones pertenecientes a dos controladores distintos.
    """
    idx_a = buscar_indice_asignacion_por_controlador(
        asignaciones=asignaciones,
        controlador_nombre=controlador_a,
        fecha=fecha_a,
        codigo_turno=codigo_turno_a,
    )

    idx_b = buscar_indice_asignacion_por_controlador(
        asignaciones=asignaciones,
        controlador_nombre=controlador_b,
        fecha=fecha_b,
        codigo_turno=codigo_turno_b,
    )

    return evaluar_swap(
        asignaciones=asignaciones,
        idx_a=idx_a,
        idx_b=idx_b,
        config_file=config_file,
    )