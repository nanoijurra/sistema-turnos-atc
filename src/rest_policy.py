"""Shared minimum-rest parameter contract (hours, not swap lead time)."""
import math

DEFAULT_MIN_REST_HOURS = 16


def validate_rest_hours(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError("horas_minimas debe ser un numero finito positivo")
    return value


def rest_hours_from_parameters(parameters):
    unknown = set(parameters) - {"horas_minimas", "min_horas"}
    if unknown:
        raise ValueError(f"Parametros de descanso desconocidos: {sorted(unknown)}")
    for value in parameters.values():
        validate_rest_hours(value)
    if "horas_minimas" in parameters and "min_horas" in parameters and parameters["horas_minimas"] != parameters["min_horas"]:
        raise ValueError("horas_minimas y min_horas son contradictorios")
    return parameters.get("horas_minimas", parameters.get("min_horas", DEFAULT_MIN_REST_HOURS))
