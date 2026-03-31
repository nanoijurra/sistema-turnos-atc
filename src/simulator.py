from datetime import date

from src.engine import validar_todo
from src.swap_service import (
    crear_swap_request as crear_swap_request_core,
    evaluar_swap_request as evaluar_swap_request_core,
    resolver_swap_request as resolver_swap_request_core,
    aplicar_swap_request as aplicar_swap_request_core,
)
from src.scoring import es_roster_valido, calcular_score
from src.rule_types import RuleResult
from src.models import SwapRequest
from src.roster_diff import impacto_por_controlador


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


def clasificar_swap(evaluacion: dict) -> str:
    """
    Clasifica un swap según impacto global y por controlador.

    Reglas:
    - RECHAZABLE: si queda inválido o empeora a algún controlador
    - BENEFICIOSO: si mejora algo real y no perjudica a nadie
    - ACEPTABLE: si queda válido y no empeora a nadie, aunque no mejore mucho
    """
    if not evaluacion["valido_nuevo"]:
        return "RECHAZABLE"

    antes = evaluacion.get("resumen_por_controlador_original", {})
    despues = evaluacion.get("resumen_por_controlador_nuevo", {})

    algun_controlador_empeora = False

    for ctrl, datos_antes in antes.items():
        datos_despues = despues.get(ctrl)

        if not datos_despues:
            continue

        delta_hard_ctrl = (
            datos_despues["violaciones"]["hard"]
            - datos_antes["violaciones"]["hard"]
        )
        delta_total_ctrl = (
            datos_despues["violaciones"]["total"]
            - datos_antes["violaciones"]["total"]
        )

        if (
            delta_hard_ctrl > 0
            or delta_total_ctrl > 0
            or (datos_antes["valido"] and not datos_despues["valido"])
        ):
            algun_controlador_empeora = True

    if algun_controlador_empeora:
        return "RECHAZABLE"

    if evaluacion["delta_hard"] < 0 or evaluacion["delta_total_violaciones"] < 0:
        return "BENEFICIOSO"

    return "ACEPTABLE"


def calcular_impacto(evaluacion: dict) -> int:
    """
    Calcula un score de impacto para ordenar swaps.
    """
    hard = evaluacion["resumen_nuevo"]["hard"]
    total = evaluacion["resumen_nuevo"]["total"]

    delta_hard = evaluacion["delta_hard"]
    delta_total = evaluacion["delta_total_violaciones"]

    impacto = 0
    impacto -= hard * 100
    impacto -= total * 10
    impacto += (-delta_hard) * 50
    impacto += (-delta_total) * 5
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
    from copy import deepcopy
    from dataclasses import replace

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
    Evalúa un swap comparando explícitamente el estado antes y después.

    Contrato:
    - simulator evalúa técnicamente el escenario
    - calcula deltas
    - clasifica técnicamente
    - no toma decisión de negocio
    """
    from src.models import RosterVersion

    if idx_a == idx_b:
        raise ValueError("idx_a e idx_b deben ser distintos.")

    if not (0 <= idx_a < len(asignaciones)) or not (0 <= idx_b < len(asignaciones)):
        raise IndexError("Índices fuera de rango.")

    # Escenario antes
    escenario_original = asignaciones
    resultados_original = validar_todo(escenario_original, config_file)
    valido_original = es_roster_valido(resultados_original)
    score_original = calcular_score(resultados_original)
    resumen_original = resumir_violaciones(resultados_original)
    resumen_por_regla_original = resumir_violaciones_por_regla(resultados_original)
    resumen_por_controlador_original = resumir_violaciones_por_controlador(
        escenario_original,
        config_file,
    )

    # Escenario después
    resultado_swap = simular_swap(
        asignaciones=asignaciones,
        idx_a=idx_a,
        idx_b=idx_b,
        config_file=config_file,
    )
    escenario_nuevo = resultado_swap["roster"]
    resultados_nuevo = resultado_swap["resultados"]
    valido_nuevo = es_roster_valido(resultados_nuevo)
    score_nuevo = calcular_score(resultados_nuevo)
    resumen_nuevo = resumir_violaciones(resultados_nuevo)
    resumen_por_regla_nuevo = resumir_violaciones_por_regla(resultados_nuevo)
    resumen_por_controlador_nuevo = resumir_violaciones_por_controlador(
        escenario_nuevo,
        config_file,
    )

    # Deltas
    delta_score = score_nuevo - score_original
    delta_total_violaciones = resumen_nuevo["total"] - resumen_original["total"]
    delta_hard = resumen_nuevo["hard"] - resumen_original["hard"]
    delta_soft = resumen_nuevo["soft"] - resumen_original["soft"]

    igual = (
        delta_score == 0
        and delta_total_violaciones == 0
        and delta_hard == 0
        and delta_soft == 0
    )

    roster_actual = RosterVersion(
        id="ROSTER_ACTUAL",
        version_number=0,
        created_at=None,
        asignaciones=escenario_original,
        vigente=True,
        base_version_id=None,
        regimen_horario="",
    )
    roster_nuevo = RosterVersion(
        id="ROSTER_NUEVO",
        version_number=0,
        created_at=None,
        asignaciones=escenario_nuevo,
        vigente=True,
        base_version_id=None,
        regimen_horario="",
    )

    resultado = {
        "swap": {
            "idx_a": idx_a,
            "idx_b": idx_b,
        },
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
        "mejora": (
            delta_score > 0
            or delta_total_violaciones < 0
            or delta_hard < 0
            or delta_soft < 0
        ),
        "empeora": (
            delta_score < 0
            or delta_total_violaciones > 0
            or delta_hard > 0
            or delta_soft > 0
        ),
        "igual": igual,
        "resultado_swap": resultado_swap,
        "impacto_por_controlador": impacto_por_controlador(roster_actual, roster_nuevo),
    }

    resultado["clasificacion"] = clasificar_swap(resultado)
    resultado["impacto"] = calcular_impacto(resultado)

    return resultado


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
        evaluaciones.append(evaluacion)

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
    """
    pares = []
    n = len(asignaciones)

    for i in range(n):
        for j in range(i + 1, n):
            pares.append((i, j))

            if limite is not None and len(pares) >= limite:
                return pares

    return pares


def generar_pares_swap_entre_controladores(
    asignaciones: list,
    limite: int | None = None,
) -> list[tuple[int, int]]:
    """
    Genera pares de swap solamente entre asignaciones de controladores distintos.
    """
    pares = []
    n = len(asignaciones)

    for i in range(n):
        for j in range(i + 1, n):
            ctrl_i = (
                asignaciones[i].controlador.nombre
                if asignaciones[i].controlador is not None
                else None
            )
            ctrl_j = (
                asignaciones[j].controlador.nombre
                if asignaciones[j].controlador is not None
                else None
            )

            if ctrl_i == ctrl_j:
                continue

            pares.append((i, j))

            if limite is not None and len(pares) >= limite:
                return pares

    return pares


def explorar_swaps_entre_controladores(
    asignaciones: list,
    limite: int | None = None,
    config_file: str = "config_equilibrado.json",
) -> list[dict]:
    """
    Explora automáticamente swaps entre controladores distintos y los rankea.
    """
    pares = generar_pares_swap_entre_controladores(asignaciones, limite=limite)
    return explorar_swaps(asignaciones, pares, config_file=config_file)


def filtrar_swaps_validos(evaluaciones: list[dict]) -> list[dict]:
    """
    Devuelve solo los swaps cuyo resultado nuevo es válido.
    """
    return [e for e in evaluaciones if e["valido_nuevo"]]


def filtrar_swaps_utiles(evaluaciones: list[dict]) -> list[dict]:
    """
    Devuelve swaps considerados útiles.
    """
    return [
        e for e in evaluaciones
        if e["clasificacion"] in {"BENEFICIOSO", "ACEPTABLE"}
    ]


def generar_recomendacion_textual(evaluacion: dict) -> str:
    """
    Genera una explicación textual incluyendo impacto por controlador.
    """
    swap = evaluacion["swap"]
    idx_a = swap["idx_a"]
    idx_b = swap["idx_b"]

    partes = [f"Swap recomendado: {idx_a} ↔ {idx_b}."]

    if evaluacion["valido_nuevo"]:
        partes.append("El roster resultante queda válido.")
    else:
        partes.append("El roster resultante sigue siendo inválido.")

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

    antes = evaluacion.get("resumen_por_controlador_original", {})
    despues = evaluacion.get("resumen_por_controlador_nuevo", {})

    cambios_controladores = []

    for ctrl, datos_antes in antes.items():
        datos_despues = despues.get(ctrl)

        if not datos_despues:
            continue

        delta_hard_ctrl = (
            datos_despues["violaciones"]["hard"]
            - datos_antes["violaciones"]["hard"]
        )
        delta_total_ctrl = (
            datos_despues["violaciones"]["total"]
            - datos_antes["violaciones"]["total"]
        )
        cambio_validez = datos_antes["valido"] != datos_despues["valido"]

        if (
            delta_hard_ctrl < 0
            or delta_total_ctrl < 0
            or (datos_antes["valido"] is False and datos_despues["valido"] is True)
        ):
            cambios_controladores.append(
                f"{ctrl} mejora (hard {datos_antes['violaciones']['hard']}→{datos_despues['violaciones']['hard']})"
            )
        elif delta_hard_ctrl > 0 or delta_total_ctrl > 0 or cambio_validez:
            cambios_controladores.append(
                f"{ctrl} empeora (hard {datos_antes['violaciones']['hard']}→{datos_despues['violaciones']['hard']})"
            )

    if cambios_controladores:
        partes.append("Impacto por controlador: " + "; ".join(cambios_controladores) + ".")

    partes.append(f"Clasificación: {evaluacion['clasificacion']}.")
    partes.append(f"Impacto calculado: {evaluacion.get('impacto', 0)}.")

    return " ".join(partes)


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


def crear_swap_request(
    asignaciones: list,
    idx_a: int,
    idx_b: int,
    motivo: str | None = None,
) -> SwapRequest:
    """
    Crea un SwapRequest a partir de índices del roster y delega
    la creación de la entidad al engine.
    """
    if not (0 <= idx_a < len(asignaciones)) or not (0 <= idx_b < len(asignaciones)):
        raise IndexError("Índices fuera de rango para crear SwapRequest.")

    asignacion_a = asignaciones[idx_a]
    asignacion_b = asignaciones[idx_b]

    if asignacion_a.controlador is None or asignacion_b.controlador is None:
        raise ValueError("No se puede crear un SwapRequest sin controladores asignados.")

    controlador_a = asignacion_a.controlador.nombre
    controlador_b = asignacion_b.controlador.nombre

    return crear_swap_request_core(
        controlador_a=controlador_a,
        controlador_b=controlador_b,
        idx_a=idx_a,
        idx_b=idx_b,
        motivo=motivo,
    )


def evaluar_swap_request(
    asignaciones: list,
    request: SwapRequest,
    config_file: str = "config_equilibrado.json",
) -> dict:
    return evaluar_swap_request_core(
        asignaciones=asignaciones,
        request=request,
        evaluar_swap_fn=evaluar_swap,
        config_file=config_file,
    )


def resolver_swap_request(
    request: SwapRequest,
    accion: str,
) -> SwapRequest:
    return resolver_swap_request_core(
        request=request,
        accion=accion,
    )


def aplicar_swap_request(
    asignaciones: list,
    request: "SwapRequest",
):
    return aplicar_swap_request_core(asignaciones, request)


def mostrar_historial_swap_request(request: SwapRequest) -> str:
    """
    Devuelve una representación textual del historial del SwapRequest.
    """
    lineas = ["Historial del SwapRequest:"]

    if not request.history:
        lineas.append("  - sin eventos registrados -")
        return "\n".join(lineas)

    for i, evento in enumerate(request.history, start=1):
        lineas.append(f"  {i}. {evento}")

    return "\n".join(lineas)