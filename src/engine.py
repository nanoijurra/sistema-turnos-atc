import json
import os

from src import validator
from src.rule_types import RuleResult, Violation


RULES_REGISTRY = {
    "validar_descanso_minimo": validator.validar_descanso_minimo,
    "validar_secuencia": validator.validar_secuencia,
    "validar_noches_consecutivas": validator.validar_noches_consecutivas,
}


def cargar_config(nombre_config: str = "config_equilibrado.json") -> dict:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ruta = os.path.join(base_dir, "config", nombre_config)

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def agrupar_por_controlador(asignaciones: list) -> dict:
    """
    Agrupa asignaciones por controlador.
    Si no hay controlador, usa SIN_CONTROLADOR para mantener compatibilidad.
    """
    grupos = {}

    for asignacion in asignaciones:
        nombre = (
            asignacion.controlador.nombre
            if asignacion.controlador is not None
            else "SIN_CONTROLADOR"
        )

        if nombre not in grupos:
            grupos[nombre] = []

        grupos[nombre].append(asignacion)

    for grupo in grupos.values():
        grupo.sort(key=lambda a: a.fecha)

    return grupos


def validar_estructura_violacion(violacion: Violation, nombre_regla: str) -> None:
    if not isinstance(violacion, Violation):
        raise TypeError(
            f"La regla '{nombre_regla}' devolvió un objeto de tipo "
            f"{type(violacion).__name__}. Debe devolver instancias de Violation."
        )

    if violacion.severidad not in ("hard", "soft"):
        raise ValueError(
            f"La regla '{nombre_regla}' devolvió una severidad inválida: {violacion.severidad}"
        )


def ejecutar_regla(asignaciones, regla_config: dict) -> RuleResult:
    nombre_regla = regla_config["nombre"]
    nombre_funcion = regla_config["funcion"]
    prioridad = regla_config["prioridad"]
    parametros = regla_config.get("parametros", {})

    if nombre_funcion not in RULES_REGISTRY:
        raise ValueError(f"Regla no registrada en RULES_REGISTRY: '{nombre_funcion}'")

    funcion = RULES_REGISTRY[nombre_funcion]
    violaciones = funcion(asignaciones, **parametros)

    if violaciones is None:
        raise ValueError(
            f"La regla '{nombre_funcion}' devolvió None. Debe devolver una lista."
        )

    if not isinstance(violaciones, list):
        raise TypeError(
            f"La regla '{nombre_funcion}' devolvió {type(violaciones).__name__}. Debe devolver una lista."
        )

    for violacion in violaciones:
        validar_estructura_violacion(violacion, nombre_funcion)

    return RuleResult(
        regla=nombre_regla,
        prioridad=prioridad,
        violaciones=violaciones,
    )


def validar_todo(asignaciones, config_file: str = "config_equilibrado.json") -> list[RuleResult]:
    config = cargar_config(config_file)
    resultados = []

    grupos = agrupar_por_controlador(asignaciones)

    for regla_config in config["reglas"]:
        nombre_regla = regla_config["nombre"]
        prioridad = regla_config["prioridad"]

        violaciones_totales = []

        for _, asignaciones_ctrl in grupos.items():
            resultado_ctrl = ejecutar_regla(asignaciones_ctrl, regla_config)
            violaciones_totales.extend(resultado_ctrl.violaciones)

        resultados.append(
            RuleResult(
                regla=nombre_regla,
                prioridad=prioridad,
                violaciones=violaciones_totales,
            )
        )

    resultados.sort(key=lambda r: r.prioridad)
    return resultados