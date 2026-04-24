from src.models import Asignacion


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


def is_candidate_technically_plausible(
    asignacion_origen: Asignacion,
    asignacion_candidata: Asignacion,
    asignaciones: list[Asignacion],
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

    return True


def filter_technically_plausible_candidates(
    asignacion_origen: Asignacion,
    candidatos: list[Asignacion],
    asignaciones: list[Asignacion],
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
        )
    ]
