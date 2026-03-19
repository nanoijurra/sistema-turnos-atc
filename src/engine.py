import json
import os

from src import validator


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


def validar_estructura_violacion(violacion: dict, nombre_regla: str) -> None:
    campos_obligatorios = ["codigo", "mensaje", "severidad", "penalizacion"]

    for campo in campos_obligatorios:
        if campo not in violacion:
            raise ValueError(
                f"La regla '{nombre_regla}' devolvió una violación sin el campo obligatorio '{campo}'."
            )

    if violacion["severidad"] not in ("hard", "soft"):
        raise ValueError(
            f"La regla '{nombre_regla}' devolvió una severidad inválida: {violacion['severidad']}"
        )


def ejecutar_regla(asignaciones, regla_config: dict) -> dict:
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
        if not isinstance(violacion, dict):
            raise TypeError(
                f"La regla '{nombre_funcion}' devolvió una violación de tipo "
                f"{type(violacion).__name__}. Cada violación debe ser un dict."
            )

        validar_estructura_violacion(violacion, nombre_funcion)

    return {
        "regla": nombre_regla,
        "prioridad": prioridad,
        "ok": len(violaciones) == 0,
        "violaciones": violaciones,
    }


def validar_todo(asignaciones, config_file: str = "config_equilibrado.json") -> list[dict]:
    config = cargar_config(config_file)
    resultados = []

    for regla_config in config["reglas"]:
        resultado = ejecutar_regla(asignaciones, regla_config)
        resultados.append(resultado)

    resultados.sort(key=lambda r: r["prioridad"])
    return resultados