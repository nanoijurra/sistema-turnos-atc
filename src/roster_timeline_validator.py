from __future__ import annotations

from src.models import (
    Asignacion,
    Controlador,
    crear_esquema_8h,
    obtener_inicio_fin_asignacion,
)
from src.roster_day_timeline import (
    RosterDayStatus,
    RosterDiaImportado,
    agrupar_timeline_por_controlador,
    obtener_rachas_ab_mayores_a,
    obtener_rachas_c_mayores_a,
    obtener_rachas_libres_mayores_a,
)
from src.rule_types import Violation


def _build_violation(
    codigo: str,
    mensaje: str,
    *,
    severidad: str = "hard",
    penalizacion: int | float = 0,
    metadata: dict | None = None,
) -> Violation:
    return Violation(
        codigo=codigo,
        mensaje=mensaje,
        severidad=severidad,
        penalizacion=penalizacion,
        metadata=metadata or {},
    )


def _metadata_racha(racha: list[RosterDiaImportado], max_dias: int) -> dict:
    return {
        "controlador": racha[0].controlador,
        "fecha_inicio": str(racha[0].fecha),
        "fecha_fin": str(racha[-1].fecha),
        "cantidad_dias": len(racha),
        "max_dias": max_dias,
        "codigos": [dia.codigo_normalizado for dia in racha],
    }


def _dias_operativos(dias: list[RosterDiaImportado]) -> list[RosterDiaImportado]:
    return sorted(
        [
            dia
            for dia in dias
            if dia.estado == RosterDayStatus.OPERATIVO
            and dia.codigo_normalizado in {"A", "B", "C"}
        ],
        key=lambda dia: dia.fecha,
    )


def _crear_asignacion_desde_dia(dia: RosterDiaImportado) -> Asignacion:
    if dia.codigo_normalizado is None:
        raise ValueError("No se puede crear una asignacion sin codigo_normalizado.")

    esquema = crear_esquema_8h()
    turno = esquema.obtener_turno(dia.codigo_normalizado)

    return Asignacion(
        fecha=dia.fecha,
        turno=turno,
        controlador=Controlador(dia.controlador),
    )


def validar_max_ab_consecutivos_timeline(
    dias: list[RosterDiaImportado],
    max_dias: int = 5,
) -> list[Violation]:
    violaciones: list[Violation] = []

    for racha in obtener_rachas_ab_mayores_a(dias, max_dias=max_dias):
        metadata = _metadata_racha(racha, max_dias)

        violaciones.append(
            _build_violation(
                codigo="EXCESO_AB_CONSECUTIVOS",
                mensaje=(
                    f"Exceso de dias consecutivos A/B para "
                    f"{metadata['controlador']}: "
                    f"{metadata['cantidad_dias']} > {max_dias} "
                    f"entre {metadata['fecha_inicio']} y {metadata['fecha_fin']}."
                ),
                severidad="hard",
                metadata=metadata,
            )
        )

    return violaciones


def validar_max_c_consecutivos_timeline(
    dias: list[RosterDiaImportado],
    max_dias: int = 3,
) -> list[Violation]:
    violaciones: list[Violation] = []

    for racha in obtener_rachas_c_mayores_a(dias, max_dias=max_dias):
        metadata = _metadata_racha(racha, max_dias)

        violaciones.append(
            _build_violation(
                codigo="EXCESO_C_CONSECUTIVOS",
                mensaje=(
                    f"Exceso de dias consecutivos C para "
                    f"{metadata['controlador']}: "
                    f"{metadata['cantidad_dias']} > {max_dias} "
                    f"entre {metadata['fecha_inicio']} y {metadata['fecha_fin']}."
                ),
                severidad="hard",
                metadata=metadata,
            )
        )

    return violaciones


def validar_libres_consecutivos_timeline(
    dias: list[RosterDiaImportado],
    max_dias: int = 5,
) -> list[Violation]:
    violaciones: list[Violation] = []

    for racha in obtener_rachas_libres_mayores_a(dias, max_dias=max_dias):
        metadata = _metadata_racha(racha, max_dias)

        violaciones.append(
            _build_violation(
                codigo="EXCESO_LIBRES_CONSECUTIVOS",
                mensaje=(
                    f"Mas de {max_dias} dias libres consecutivos para "
                    f"{metadata['controlador']}: "
                    f"{metadata['cantidad_dias']} dias entre "
                    f"{metadata['fecha_inicio']} y {metadata['fecha_fin']}."
                ),
                severidad="soft",
                metadata=metadata,
            )
        )

    return violaciones


def validar_descanso_minimo_timeline(
    dias: list[RosterDiaImportado],
    horas_minimas: int | float = 12,
) -> list[Violation]:
    violaciones: list[Violation] = []
    dias_operativos = _dias_operativos(dias)

    for indice in range(len(dias_operativos) - 1):
        dia_actual = dias_operativos[indice]
        dia_siguiente = dias_operativos[indice + 1]

        asignacion_actual = _crear_asignacion_desde_dia(dia_actual)
        asignacion_siguiente = _crear_asignacion_desde_dia(dia_siguiente)

        _, fin_actual = obtener_inicio_fin_asignacion(asignacion_actual)
        inicio_siguiente, _ = obtener_inicio_fin_asignacion(asignacion_siguiente)

        descanso_horas = (inicio_siguiente - fin_actual).total_seconds() / 3600

        if descanso_horas <= horas_minimas:
            violaciones.append(
                _build_violation(
                    codigo="DESCANSO_INSUFICIENTE_TIMELINE",
                    mensaje=(
                        f"Descanso insuficiente para {dia_actual.controlador} "
                        f"entre {dia_actual.fecha} ({dia_actual.codigo_normalizado}) "
                        f"y {dia_siguiente.fecha} ({dia_siguiente.codigo_normalizado}): "
                        f"{descanso_horas:.1f}h <= {horas_minimas}h."
                    ),
                    severidad="hard",
                    metadata={
                        "controlador": dia_actual.controlador,
                        "fecha_actual": str(dia_actual.fecha),
                        "turno_actual": dia_actual.codigo_normalizado,
                        "fecha_siguiente": str(dia_siguiente.fecha),
                        "turno_siguiente": dia_siguiente.codigo_normalizado,
                        "horas_descanso": descanso_horas,
                        "horas_minimas": horas_minimas,
                    },
                )
            )

    return violaciones


def validar_timeline_controlador(
    dias: list[RosterDiaImportado],
    *,
    max_ab_consecutivos: int = 5,
    max_c_consecutivos: int = 3,
    max_libres_consecutivos: int = 5,
    horas_minimas_descanso: int | float = 12,
) -> list[Violation]:
    violaciones: list[Violation] = []

    violaciones.extend(
        validar_max_ab_consecutivos_timeline(
            dias,
            max_dias=max_ab_consecutivos,
        )
    )
    violaciones.extend(
        validar_max_c_consecutivos_timeline(
            dias,
            max_dias=max_c_consecutivos,
        )
    )
    violaciones.extend(
        validar_descanso_minimo_timeline(
            dias,
            horas_minimas=horas_minimas_descanso,
        )
    )
    violaciones.extend(
        validar_libres_consecutivos_timeline(
            dias,
            max_dias=max_libres_consecutivos,
        )
    )

    return violaciones


def validar_timeline_importada(
    dias_importados: list[RosterDiaImportado],
    *,
    max_ab_consecutivos: int = 5,
    max_c_consecutivos: int = 3,
    max_libres_consecutivos: int = 5,
    horas_minimas_descanso: int | float = 12,
) -> list[Violation]:
    violaciones: list[Violation] = []
    grupos = agrupar_timeline_por_controlador(dias_importados)

    for dias_controlador in grupos.values():
        violaciones.extend(
            validar_timeline_controlador(
                dias_controlador,
                max_ab_consecutivos=max_ab_consecutivos,
                max_c_consecutivos=max_c_consecutivos,
                max_libres_consecutivos=max_libres_consecutivos,
                horas_minimas_descanso=horas_minimas_descanso,
            )
        )

    return violaciones