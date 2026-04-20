from copy import deepcopy
from datetime import datetime

from src.historical_store import obtener_historial_equidad_derivado


DEFAULT_VENTANA_DIAS = 90


def _controladores_beneficiados(evaluacion: dict) -> list[str]:
    """
    Detecta controladores beneficiados segun la semantica tecnica vigente:
    - reduce hard
    - reduce total
    - pasa de invalido a valido
    """
    antes = evaluacion.get("resumen_por_controlador_original", {})
    despues = evaluacion.get("resumen_por_controlador_nuevo", {})

    beneficiados = []

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

        mejora_validez = (
            datos_antes["valido"] is False
            and datos_despues["valido"] is True
        )

        if delta_hard_ctrl < 0 or delta_total_ctrl < 0 or mejora_validez:
            beneficiados.append(ctrl)

    return beneficiados


def _controladores_involucrados(evaluacion: dict) -> list[str]:
    """
    Devuelve todos los controladores presentes en la evaluacion.
    """
    antes = evaluacion.get("resumen_por_controlador_original", {})
    despues = evaluacion.get("resumen_por_controlador_nuevo", {})

    nombres = set(antes.keys()) | set(despues.keys())
    return sorted(nombres)


def calcular_score_equidad_swap(
    evaluacion: dict,
    historial_por_controlador: dict | None = None,
) -> float:
    """
    Calcula una señal soft de equidad historica.

    Regla:
    - controlador con menos beneficios recientes => mejor score
    - si no hay historial => score neutro
    """
    if not historial_por_controlador:
        return 0.0

    beneficiados = _controladores_beneficiados(evaluacion)
    if not beneficiados:
        return 0.0

    score = 0.0

    for ctrl in beneficiados:
        datos_hist = historial_por_controlador.get(ctrl, {})
        beneficios_recientes = datos_hist.get("beneficios_recientes", 0.0)
        score -= beneficios_recientes

    return score


def priorizar_por_equidad_historica(
    evaluaciones: list[dict],
    historial_por_controlador: dict | None = None,
    ventana_dias: int = DEFAULT_VENTANA_DIAS,
    fecha_referencia: datetime | None = None,
) -> list[dict]:
    """
    Reordena evaluaciones ya rankeadas tecnicamente usando equidad historica
    como señal soft adicional.

    Garantias:
    - no cambia clasificacion
    - no cambia contenido tecnico
    - no promueve swaps rechazables por encima de otras clasificaciones
    - solo reordena dentro de la misma clasificacion
    """
    evaluaciones_copia = [deepcopy(e) for e in evaluaciones]

    historial_cargado = historial_por_controlador

    if historial_cargado is None:
        controladores = set()

        for evaluacion in evaluaciones_copia:
            controladores.update(_controladores_involucrados(evaluacion))

        if controladores:
            historial_cargado = obtener_historial_equidad_derivado(
                nombres=sorted(controladores),
                ventana_dias=ventana_dias,
                fecha_referencia=fecha_referencia,
            )
        else:
            historial_cargado = {}

    if not historial_cargado:
        resultado = []
        for evaluacion in evaluaciones_copia:
            evaluacion["score_equidad"] = 0.0
            evaluacion["ajuste_equidad"] = "NEUTRO_SIN_HISTORIAL"
            resultado.append(evaluacion)
        return resultado

    grupos: dict[str, list[dict]] = {
        "BENEFICIOSO": [],
        "ACEPTABLE": [],
        "RECHAZABLE": [],
    }

    otros = []

    for evaluacion in evaluaciones_copia:
        score_equidad = calcular_score_equidad_swap(evaluacion, historial_cargado)
        evaluacion["score_equidad"] = score_equidad
        evaluacion["ajuste_equidad"] = "APLICADO"

        clasificacion = evaluacion.get("clasificacion")
        if clasificacion in grupos:
            grupos[clasificacion].append(evaluacion)
        else:
            otros.append(evaluacion)

    for clasificacion in ("BENEFICIOSO", "ACEPTABLE"):
        grupos[clasificacion].sort(
            key=lambda e: e.get("score_equidad", 0.0),
            reverse=True,
        )

    resultado = (
        grupos["BENEFICIOSO"]
        + grupos["ACEPTABLE"]
        + grupos["RECHAZABLE"]
        + otros
    )

    return resultado