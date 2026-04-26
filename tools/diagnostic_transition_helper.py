from __future__ import annotations


def _primer_numero_disponible(resultado: dict, claves: list[str]):
    for clave in claves:
        valor = resultado.get(clave)
        if isinstance(valor, (int, float)):
            return valor
    return None


def _comparar_delta(delta) -> str | None:
    if delta is None:
        return None
    if delta < 0:
        return "MEJORA"
    if delta == 0:
        return "IGUAL"
    return "EMPEORA"


def diagnosticar_transicion(resultado: dict) -> str:
    valido_original = resultado.get("valido_original")
    valido_nuevo = resultado.get("valido_nuevo")

    if not isinstance(valido_original, bool) or not isinstance(valido_nuevo, bool):
        return "SIN_DATO"

    delta_hard = resultado.get("delta_hard")
    delta_soft = resultado.get("delta_soft")
    delta_score = resultado.get("delta_score")

    if valido_original and not valido_nuevo:
        return "VI_DEGRADA"

    if not valido_original and valido_nuevo:
        return "IV_RECUPERA"

    if not valido_original and not valido_nuevo:
        comparacion = _comparar_delta(delta_hard)
        if comparacion is None:
            return "SIN_DATO"
        return f"II_{comparacion}"

    comparacion = _comparar_delta(
        _primer_numero_disponible(
            resultado,
            ["delta_hard", "delta_soft", "delta_score"],
        )
    )
    if comparacion is None:
        return "SIN_DATO"

    return f"VV_{comparacion}"