from src.models import Asignacion
from src.roster_index import RosterIndex


def _nombre_controlador(asignacion: Asignacion) -> str | None:
    if asignacion.controlador is None:
        return None
    return asignacion.controlador.nombre


def _es_candidato_distinto(asignacion_origen: Asignacion, candidato: Asignacion) -> bool:
    if candidato is asignacion_origen:
        return False

    return _nombre_controlador(candidato) != _nombre_controlador(asignacion_origen)


def _ordenar_candidatos(candidatos: list[Asignacion]) -> list[Asignacion]:
    return sorted(
        candidatos,
        key=lambda item: (
            item.fecha,
            item.turno.codigo,
            _nombre_controlador(item) or "",
        ),
    )


def _deduplicar_candidatos(candidatos: list[Asignacion]) -> list[Asignacion]:
    vistos = set()
    resultado = []

    for candidato in candidatos:
        identificador = id(candidato)
        if identificador in vistos:
            continue

        vistos.add(identificador)
        resultado.append(candidato)

    return resultado


def generate_same_day_candidates(
    asignacion_origen: Asignacion,
    roster_index: RosterIndex,
) -> list[Asignacion]:
    candidatos = [
        candidato
        for candidato in roster_index.by_date.get(asignacion_origen.fecha, [])
        if _es_candidato_distinto(asignacion_origen, candidato)
    ]

    return _ordenar_candidatos(candidatos)


def generate_future_candidates(
    asignacion_origen: Asignacion,
    roster_index: RosterIndex,
) -> list[Asignacion]:
    candidatos = []
    controlador_origen = _nombre_controlador(asignacion_origen)

    for controlador, asignaciones in roster_index.future_window.items():
        if controlador == controlador_origen:
            continue

        candidatos.extend(
            candidato
            for candidato in asignaciones
            if candidato.fecha >= asignacion_origen.fecha
            and _es_candidato_distinto(asignacion_origen, candidato)
        )

    return _ordenar_candidatos(candidatos)


def generate_candidates(
    asignacion_origen: Asignacion,
    roster_index: RosterIndex,
    mode: str = "auto",
) -> list[Asignacion]:
    if mode == "same_day":
        return generate_same_day_candidates(asignacion_origen, roster_index)

    if mode == "future":
        return generate_future_candidates(asignacion_origen, roster_index)

    if mode == "auto":
        return _deduplicar_candidatos(
            generate_same_day_candidates(
                asignacion_origen,
                roster_index,
            )
            + generate_future_candidates(asignacion_origen, roster_index)
        )

    raise ValueError(f"Modo de generacion de candidatos no soportado: {mode}")
