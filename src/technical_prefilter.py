from dataclasses import replace

from src.engine import cargar_config
from src.models import Asignacion, obtener_inicio_fin_asignacion
from src.validator import validar_secuencia


def _nombre_controlador(asignacion: Asignacion) -> str | None:
    if asignacion.controlador is None:
        return None
    return asignacion.controlador.nombre


def _is_same_exact_assignment(
    asignacion_origen: Asignacion,
    asignacion_candidata: Asignacion,
) -> bool:
    return asignacion_origen == asignacion_candidata


def _is_trivial_swap_without_real_change(
    asignacion_origen: Asignacion,
    asignacion_candidata: Asignacion,
) -> bool:
    return asignacion_origen.turno == asignacion_candidata.turno


def _obtener_horas_minimas_descanso(config_file: str = "config_equilibrado.json") -> float | None:
    config = cargar_config(config_file)

    for regla in config.get("reglas", []):
        if regla.get("funcion") != "validar_descanso_minimo":
            continue

        parametros = regla.get("parametros", {})
        horas_minimas = parametros.get("horas_minimas", parametros.get("min_horas"))

        if isinstance(horas_minimas, (int, float)):
            return float(horas_minimas)

    return None


def _obtener_regla_config(
    funcion_regla: str,
    config_file: str = "config_equilibrado.json",
) -> dict | None:
    config = cargar_config(config_file)

    for regla in config.get("reglas", []):
        if regla.get("funcion") == funcion_regla:
            return regla

    return None


def _asignaciones_ordenadas_por_controlador(
    asignaciones: list[Asignacion],
    nombre_controlador: str | None,
) -> list[Asignacion]:
    if nombre_controlador is None:
        return []

    resultado = [
        asignacion
        for asignacion in asignaciones
        if _nombre_controlador(asignacion) == nombre_controlador
    ]
    resultado.sort(key=lambda asignacion: obtener_inicio_fin_asignacion(asignacion)[0])
    return resultado


def _buscar_posicion_asignacion(
    asignaciones_controlador: list[Asignacion],
    asignacion_objetivo: Asignacion,
) -> int | None:
    coincidencias_por_identidad = [
        idx
        for idx, asignacion in enumerate(asignaciones_controlador)
        if asignacion is asignacion_objetivo
    ]
    if len(coincidencias_por_identidad) == 1:
        return coincidencias_por_identidad[0]
    if len(coincidencias_por_identidad) > 1:
        return None

    coincidencias_por_igualdad = [
        idx
        for idx, asignacion in enumerate(asignaciones_controlador)
        if asignacion == asignacion_objetivo
    ]
    if len(coincidencias_por_igualdad) == 1:
        return coincidencias_por_igualdad[0]

    return None


def _descanso_entre_asignaciones_horas(
    asignacion_anterior: Asignacion,
    asignacion_siguiente: Asignacion,
) -> float:
    _, fin_anterior = obtener_inicio_fin_asignacion(asignacion_anterior)
    inicio_siguiente, _ = obtener_inicio_fin_asignacion(asignacion_siguiente)
    return (inicio_siguiente - fin_anterior).total_seconds() / 3600


def _tiene_descanso_local_inmediato_insuficiente(
    asignacion_objetivo: Asignacion,
    turno_nuevo,
    asignaciones: list[Asignacion],
    horas_minimas_descanso: float | None,
) -> bool:
    if horas_minimas_descanso is None:
        return False

    nombre_controlador = _nombre_controlador(asignacion_objetivo)
    asignaciones_controlador = _asignaciones_ordenadas_por_controlador(
        asignaciones=asignaciones,
        nombre_controlador=nombre_controlador,
    )
    posicion = _buscar_posicion_asignacion(asignaciones_controlador, asignacion_objetivo)

    if posicion is None:
        return False

    asignacion_actualizada = replace(asignacion_objetivo, turno=turno_nuevo)
    asignacion_anterior = (
        asignaciones_controlador[posicion - 1]
        if posicion > 0
        else None
    )
    asignacion_posterior = (
        asignaciones_controlador[posicion + 1]
        if posicion < len(asignaciones_controlador) - 1
        else None
    )

    if asignacion_anterior is not None:
        if _descanso_entre_asignaciones_horas(asignacion_anterior, asignacion_actualizada) < horas_minimas_descanso:
            return True

    if asignacion_posterior is not None:
        if _descanso_entre_asignaciones_horas(asignacion_actualizada, asignacion_posterior) < horas_minimas_descanso:
            return True

    return False


def _tiene_secuencia_local_inmediata_prohibida(
    asignacion_objetivo: Asignacion,
    turno_nuevo,
    asignaciones: list[Asignacion],
    config_file: str = "config_equilibrado.json",
) -> bool:
    regla_secuencia = _obtener_regla_config(
        funcion_regla="validar_secuencia",
        config_file=config_file,
    )
    if regla_secuencia is None:
        return False

    nombre_controlador = _nombre_controlador(asignacion_objetivo)
    asignaciones_controlador = _asignaciones_ordenadas_por_controlador(
        asignaciones=asignaciones,
        nombre_controlador=nombre_controlador,
    )
    posicion = _buscar_posicion_asignacion(asignaciones_controlador, asignacion_objetivo)

    if posicion is None:
        return False

    asignacion_actualizada = replace(asignacion_objetivo, turno=turno_nuevo)
    inicio = max(0, posicion - 1)
    fin = min(len(asignaciones_controlador), posicion + 2)
    ventana_local = list(asignaciones_controlador[inicio:fin])
    ventana_local[posicion - inicio] = asignacion_actualizada

    return len(validar_secuencia(ventana_local)) > 0


def get_candidate_prefilter_diagnostic_reasons(
    asignacion_origen: Asignacion,
    asignacion_candidata: Asignacion,
    asignaciones: list[Asignacion],
    config_file: str = "config_equilibrado.json",
) -> list[str]:
    motivos: list[str] = []
    horas_minimas_descanso = _obtener_horas_minimas_descanso(config_file=config_file)

    if _tiene_descanso_local_inmediato_insuficiente(
        asignacion_objetivo=asignacion_origen,
        turno_nuevo=asignacion_candidata.turno,
        asignaciones=asignaciones,
        horas_minimas_descanso=horas_minimas_descanso,
    ):
        motivos.append("DESCANSO_LOCAL")

    if asignacion_candidata.fecha == asignacion_origen.fecha:
        if _tiene_descanso_local_inmediato_insuficiente(
            asignacion_objetivo=asignacion_candidata,
            turno_nuevo=asignacion_origen.turno,
            asignaciones=asignaciones,
            horas_minimas_descanso=horas_minimas_descanso,
        ):
            motivos.append("DESCANSO_LOCAL")

    if _tiene_secuencia_local_inmediata_prohibida(
        asignacion_objetivo=asignacion_origen,
        turno_nuevo=asignacion_candidata.turno,
        asignaciones=asignaciones,
        config_file=config_file,
    ):
        motivos.append("SECUENCIA_LOCAL")

    if asignacion_candidata.fecha == asignacion_origen.fecha:
        if _tiene_secuencia_local_inmediata_prohibida(
            asignacion_objetivo=asignacion_candidata,
            turno_nuevo=asignacion_origen.turno,
            asignaciones=asignaciones,
            config_file=config_file,
        ):
            motivos.append("SECUENCIA_LOCAL")

    return sorted(set(motivos))


def is_candidate_technically_plausible(
    asignacion_origen: Asignacion,
    asignacion_candidata: Asignacion,
    asignaciones: list[Asignacion],
    config_file: str = "config_equilibrado.json",
) -> bool:
    """
    Descarta solo inviabilidad tecnica obvia y local.
    """
    if _nombre_controlador(asignacion_origen) == _nombre_controlador(asignacion_candidata):
        return False

    if _is_same_exact_assignment(asignacion_origen, asignacion_candidata):
        return False

    if _is_trivial_swap_without_real_change(asignacion_origen, asignacion_candidata):
        return False

    if get_candidate_prefilter_diagnostic_reasons(
        asignacion_origen=asignacion_origen,
        asignacion_candidata=asignacion_candidata,
        asignaciones=asignaciones,
        config_file=config_file,
    ):
        return False

    return True


def filter_technically_plausible_candidates(
    asignacion_origen: Asignacion,
    candidatos: list[Asignacion],
    asignaciones: list[Asignacion],
    config_file: str = "config_equilibrado.json",
) -> list[Asignacion]:
    """
    Mantiene solo candidatos tecnicamente plausibles segun chequeos minimos.
    """
    return [
        candidato
        for candidato in candidatos
        if is_candidate_technically_plausible(
            asignacion_origen=asignacion_origen,
            asignacion_candidata=candidato,
            asignaciones=asignaciones,
            config_file=config_file,
        )
    ]
