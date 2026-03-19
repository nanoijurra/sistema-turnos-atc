from src.models import obtener_inicio_fin_asignacion
from src.rule_types import Violation


def build_violation(codigo, mensaje, severidad="hard", penalizacion=0, metadata=None) -> Violation:
    return Violation(
        codigo=codigo,
        mensaje=mensaje,
        severidad=severidad,
        penalizacion=penalizacion,
        metadata=metadata or {},
    )


def validar_descanso_minimo(asignaciones, horas_minimas=12) -> list[Violation]:
    violaciones = []

    asignaciones_ordenadas = sorted(
        asignaciones,
        key=lambda a: obtener_inicio_fin_asignacion(a)[0]
    )

    for i in range(len(asignaciones_ordenadas) - 1):
        actual = asignaciones_ordenadas[i]
        siguiente = asignaciones_ordenadas[i + 1]

        _, fin_actual = obtener_inicio_fin_asignacion(actual)
        inicio_siguiente, _ = obtener_inicio_fin_asignacion(siguiente)

        descanso_horas = (inicio_siguiente - fin_actual).total_seconds() / 3600

        if descanso_horas < horas_minimas:
            violaciones.append(
                build_violation(
                    codigo="DESCANSO_INSUFICIENTE",
                    mensaje=(
                        f"Descanso insuficiente entre "
                        f"{actual.fecha} ({actual.turno.codigo}) y "
                        f"{siguiente.fecha} ({siguiente.turno.codigo}): "
                        f"{descanso_horas:.1f}h < {horas_minimas}h"
                    ),
                    severidad="hard",
                    penalizacion=0,
                    metadata={
                        "fecha_actual": str(actual.fecha),
                        "turno_actual": actual.turno.codigo,
                        "fecha_siguiente": str(siguiente.fecha),
                        "turno_siguiente": siguiente.turno.codigo,
                        "horas_descanso": descanso_horas,
                        "horas_minimas": horas_minimas,
                    }
                )
            )

    return violaciones


def validar_secuencia(asignaciones) -> list[Violation]:
    violaciones = []

    asignaciones_ordenadas = sorted(
        asignaciones,
        key=lambda a: obtener_inicio_fin_asignacion(a)[0]
    )

    secuencias_prohibidas = [
        ("NOCHE", "MANANA"),
        ("NOCHE", "TARDE"),
    ]

    for i in range(len(asignaciones_ordenadas) - 1):
        actual = asignaciones_ordenadas[i]
        siguiente = asignaciones_ordenadas[i + 1]

        categoria_actual = actual.turno.categoria
        categoria_siguiente = siguiente.turno.categoria

        if (categoria_actual, categoria_siguiente) in secuencias_prohibidas:
            violaciones.append(
                build_violation(
                    codigo="SECUENCIA_PROHIBIDA",
                    mensaje=(
                        f"Secuencia prohibida entre "
                        f"{actual.fecha} ({categoria_actual}) y "
                        f"{siguiente.fecha} ({categoria_siguiente})"
                    ),
                    severidad="hard",
                    penalizacion=0,
                    metadata={
                        "fecha_actual": str(actual.fecha),
                        "turno_actual": actual.turno.codigo,
                        "categoria_actual": categoria_actual,
                        "fecha_siguiente": str(siguiente.fecha),
                        "turno_siguiente": siguiente.turno.codigo,
                        "categoria_siguiente": categoria_siguiente,
                    }
                )
            )

    return violaciones


def validar_noches_consecutivas(asignaciones, max_noches=3) -> list[Violation]:
    violaciones = []

    asignaciones_ordenadas = sorted(
        asignaciones,
        key=lambda a: obtener_inicio_fin_asignacion(a)[0]
    )

    contador = 0

    for asignacion in asignaciones_ordenadas:
        if asignacion.turno.es_nocturno:
            contador += 1

            if contador > max_noches:
                violaciones.append(
                    build_violation(
                        codigo="EXCESO_NOCHES_CONSECUTIVAS",
                        mensaje=(
                            f"Exceso de noches consecutivas al {asignacion.fecha}: "
                            f"{contador} > {max_noches}"
                        ),
                        severidad="hard",
                        penalizacion=0,
                        metadata={
                            "fecha": str(asignacion.fecha),
                            "turno": asignacion.turno.codigo,
                            "contador_noches": contador,
                            "max_noches": max_noches,
                        }
                    )
                )
        else:
            contador = 0

    return violaciones