from __future__ import annotations

from src.models import Asignacion


def _nombre_controlador(asignacion: Asignacion) -> str:
    if asignacion.controlador is None:
        return ""
    return asignacion.controlador.nombre


def _candidate_sort_key(asignacion_origen: Asignacion, candidato: Asignacion) -> tuple:
    distancia_dias = abs((candidato.fecha - asignacion_origen.fecha).days)

    return (
        candidato.fecha != asignacion_origen.fecha,
        distancia_dias,
        candidato.turno == asignacion_origen.turno,
        _nombre_controlador(candidato),
        candidato.fecha,
        candidato.turno.codigo,
    )


def seleccionar_candidatos(
    asignacion_origen,
    candidatos: list,
    asignaciones: list,
    top_n: int = 50,
) -> list:
    if top_n <= 0:
        return []

    return sorted(
        candidatos,
        key=lambda candidato: _candidate_sort_key(asignacion_origen, candidato),
    )[:top_n]
