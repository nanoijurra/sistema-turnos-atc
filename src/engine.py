import json
from validator import *

def cargar_config(nombre_config="config_equilibrado.json"):
    import os
    import json

    base_dir = os.path.dirname(os.path.dirname(__file__))
    ruta = os.path.join(base_dir, "config", nombre_config)

    with open(ruta, "r") as f:
        return json.load(f)

def validar_todo(asignaciones, config_file="config_equilibrado.json"):
    config = cargar_config(config_file)
    resultados = []

    for regla in config["reglas"]:
        nombre = regla["nombre"]
        funcion = globals()[regla["funcion"]]
        prioridad = regla["prioridad"]
        parametros = regla.get("parametros", {})

        ok, mensaje = funcion(asignaciones, **parametros)

        resultados.append({
            "regla": nombre,
            "ok": ok,
            "mensaje": mensaje,
            "prioridad": prioridad
        })

    return resultados