from copy import deepcopy


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


def calcular_score_equidad_swap(
    evaluacion: dict,
    historial_por_controlador: dict | None = None,
) -> int:
    """
    Calcula una señal soft de equidad historica.

    Regla minima:
    - controlador con menos beneficios recientes => mejor score
    - si no hay historial => score neutro
    """
    if not historial_por_controlador:
        return 0

    beneficiados = _controladores_beneficiados(evaluacion)
    if not beneficiados:
        return 0

    score = 0

    for ctrl in beneficiados:
        datos_hist = historial_por_controlador.get(ctrl, {})
        beneficios_recientes = datos_hist.get("beneficios_recientes", 0)
        score -= beneficios_recientes

    return score


def priorizar_por_equidad_historica(
    evaluaciones: list[dict],
    historial_por_controlador: dict | None = None,
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
    if not historial_por_controlador:
        resultado = []
        for evaluacion in evaluaciones:
            copia = deepcopy(evaluacion)
            copia["score_equidad"] = 0
            copia["ajuste_equidad"] = "NEUTRO_SIN_HISTORIAL"
            resultado.append(copia)
        return resultado

    grupos: dict[str, list[dict]] = {
        "BENEFICIOSO": [],
        "ACEPTABLE": [],
        "RECHAZABLE": [],
    }

    otros = []

    for evaluacion in evaluaciones:
        copia = deepcopy(evaluacion)
        score_equidad = calcular_score_equidad_swap(copia, historial_por_controlador)
        copia["score_equidad"] = score_equidad
        copia["ajuste_equidad"] = "APLICADO"

        clasificacion = copia.get("clasificacion")
        if clasificacion in grupos:
            grupos[clasificacion].append(copia)
        else:
            otros.append(copia)

    for clasificacion in ("BENEFICIOSO", "ACEPTABLE"):
        grupos[clasificacion].sort(
            key=lambda e: e.get("score_equidad", 0),
            reverse=True,
        )

    # RECHAZABLE queda en el mismo orden tecnico recibido
    resultado = (
        grupos["BENEFICIOSO"]
        + grupos["ACEPTABLE"]
        + grupos["RECHAZABLE"]
        + otros
    )

    return resultado