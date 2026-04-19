def _controladores_beneficiados(evaluacion: dict) -> list[str]:
    """
    Detecta controladores beneficiados segun la evaluacion tecnica ya calculada.
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


def actualizar_historial_beneficios(
    historial_por_controlador: dict | None,
    evaluacion: dict | None,
) -> dict:
    """
    Actualiza historial minimo de beneficios recientes por controlador.

    Si no hay historial, crea uno nuevo.
    Si no hay evaluacion, no modifica nada.
    """
    historial = historial_por_controlador or {}

    if not evaluacion:
        return historial

    beneficiados = _controladores_beneficiados(evaluacion)

    for ctrl in beneficiados:
        if ctrl not in historial:
            historial[ctrl] = {"beneficios_recientes": 0}

        historial[ctrl]["beneficios_recientes"] = (
            historial[ctrl].get("beneficios_recientes", 0) + 1
        )

    return historial