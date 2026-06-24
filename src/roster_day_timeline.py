from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class RosterDayStatus(str, Enum):
    OPERATIVO = "OPERATIVO"
    LIBRE = "LIBRE"
    NO_OPERATIVO_DOCUMENTADO = "NO_OPERATIVO_DOCUMENTADO"
    OPERATIVO_CONFIGURABLE_NO_ACTIVO = "OPERATIVO_CONFIGURABLE_NO_ACTIVO"
    FUERA_DE_ALCANCE = "FUERA_DE_ALCANCE"
    DESCONOCIDO = "DESCONOCIDO"


@dataclass(frozen=True)
class RosterDiaImportado:
    controlador: str
    fecha: date
    estado: RosterDayStatus
    raw_value: str
    codigo: str | None = None
    codigo_normalizado: str | None = None


def agrupar_timeline_por_controlador(
    dias_importados: list[RosterDiaImportado],
) -> dict[str, list[RosterDiaImportado]]:
    grupos: dict[str, list[RosterDiaImportado]] = {}

    for dia in dias_importados:
        grupos.setdefault(dia.controlador, []).append(dia)

    for dias in grupos.values():
        dias.sort(key=lambda item: item.fecha)

    return grupos


def contar_rachas_por_estado(
    dias: list[RosterDiaImportado],
    estado: RosterDayStatus,
) -> list[list[RosterDiaImportado]]:
    dias_ordenados = sorted(dias, key=lambda item: item.fecha)
    rachas: list[list[RosterDiaImportado]] = []
    racha_actual: list[RosterDiaImportado] = []

    fecha_anterior: date | None = None

    for dia in dias_ordenados:
        es_consecutivo = (
            fecha_anterior is not None
            and (dia.fecha - fecha_anterior).days == 1
        )

        if dia.estado == estado:
            if not racha_actual or es_consecutivo:
                racha_actual.append(dia)
            else:
                rachas.append(racha_actual)
                racha_actual = [dia]
        else:
            if racha_actual:
                rachas.append(racha_actual)
                racha_actual = []

        fecha_anterior = dia.fecha

    if racha_actual:
        rachas.append(racha_actual)

    return rachas


def contar_rachas_por_codigos_operativos(
    dias: list[RosterDiaImportado],
    codigos: set[str],
) -> list[list[RosterDiaImportado]]:
    dias_ordenados = sorted(dias, key=lambda item: item.fecha)
    rachas: list[list[RosterDiaImportado]] = []
    racha_actual: list[RosterDiaImportado] = []

    fecha_anterior: date | None = None

    for dia in dias_ordenados:
        es_consecutivo = (
            fecha_anterior is not None
            and (dia.fecha - fecha_anterior).days == 1
        )
        es_codigo_objetivo = (
            dia.estado == RosterDayStatus.OPERATIVO
            and dia.codigo_normalizado in codigos
        )

        if es_codigo_objetivo:
            if not racha_actual or es_consecutivo:
                racha_actual.append(dia)
            else:
                rachas.append(racha_actual)
                racha_actual = [dia]
        else:
            if racha_actual:
                rachas.append(racha_actual)
                racha_actual = []

        fecha_anterior = dia.fecha

    if racha_actual:
        rachas.append(racha_actual)

    return rachas


def obtener_rachas_libres_mayores_a(
    dias: list[RosterDiaImportado],
    max_dias: int,
) -> list[list[RosterDiaImportado]]:
    return [
        racha
        for racha in contar_rachas_por_estado(dias, RosterDayStatus.LIBRE)
        if len(racha) > max_dias
    ]


def obtener_rachas_ab_mayores_a(
    dias: list[RosterDiaImportado],
    max_dias: int,
) -> list[list[RosterDiaImportado]]:
    return [
        racha
        for racha in contar_rachas_por_codigos_operativos(dias, {"A", "B"})
        if len(racha) > max_dias
    ]


def obtener_rachas_c_mayores_a(
    dias: list[RosterDiaImportado],
    max_dias: int,
) -> list[list[RosterDiaImportado]]:
    return [
        racha
        for racha in contar_rachas_por_codigos_operativos(dias, {"C"})
        if len(racha) > max_dias
    ]