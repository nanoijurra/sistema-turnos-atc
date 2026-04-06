import re


def extract_semantic_tokens(text: str) -> dict[str, set[str]]:
    return {
        "clasificacion_tecnica": set(
            re.findall(r"\b(BENEFICIOSO|ACEPTABLE|RECHAZABLE)\b", text)
        ),
        "decision_operativa": set(
            re.findall(r"\b(VIABLE|OBSERVAR|RECHAZAR)\b", text)
        ),
        "estado_workflow": set(
            re.findall(
                r"\b(PENDIENTE|EVALUADO|APROBADO|RECHAZADO|CANCELADO|APLICADO)\b",
                text,
            )
        ),
    }