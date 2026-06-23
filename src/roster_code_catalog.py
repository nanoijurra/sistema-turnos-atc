from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RosterCodeDocumentCategory(str, Enum):
    TURNO_BLOQUE_HORARIO = "TURNO_BLOQUE_HORARIO"
    INSTRUCCION_CAPACITACION = "INSTRUCCION_CAPACITACION"
    LICENCIA_AUSENCIA_ADMINISTRATIVA = "LICENCIA_AUSENCIA_ADMINISTRATIVA"
    OTRO = "OTRO"
    LOCAL_ACC = "LOCAL_ACC"
    LEGACY = "LEGACY"


class RosterCodeImportCategory(str, Enum):
    OPERATIVO_ACTIVO = "OPERATIVO_ACTIVO"
    OPERATIVO_CONFIGURABLE = "OPERATIVO_CONFIGURABLE"
    NO_OPERATIVO = "NO_OPERATIVO"
    NORMALIZABLE = "NORMALIZABLE"
    FUERA_DE_ALCANCE = "FUERA_DE_ALCANCE"


@dataclass(frozen=True)
class RosterCodeDefinition:
    codigo: str
    significado: str
    categoria_documental: RosterCodeDocumentCategory
    categoria_importacion: RosterCodeImportCategory
    genera_asignacion: bool
    entra_motor_tecnico: bool
    elegible_swap_acc_actual: bool
    fuente: str
    normaliza_a: str | None = None
    observaciones: str = ""


def _definicion(
    *,
    codigo: str,
    significado: str,
    categoria_documental: RosterCodeDocumentCategory,
    categoria_importacion: RosterCodeImportCategory,
    genera_asignacion: bool,
    entra_motor_tecnico: bool,
    elegible_swap_acc_actual: bool,
    fuente: str,
    normaliza_a: str | None = None,
    observaciones: str = "",
) -> RosterCodeDefinition:
    return RosterCodeDefinition(
        codigo=codigo,
        significado=significado,
        categoria_documental=categoria_documental,
        categoria_importacion=categoria_importacion,
        genera_asignacion=genera_asignacion,
        entra_motor_tecnico=entra_motor_tecnico,
        elegible_swap_acc_actual=elegible_swap_acc_actual,
        fuente=fuente,
        normaliza_a=normaliza_a,
        observaciones=observaciones,
    )


def obtener_catalogo_codigos_acc_default() -> dict[str, RosterCodeDefinition]:
    fuente_pr_gope = "PR-GOPE-044"
    fuente_local_acc = "Definicion local ACC Cordoba"
    fuente_legacy = "Codigo legacy/local historico"

    catalogo = [
        # Turnos / bloques horarios
        _definicion(
            codigo="A",
            significado="Turno operativo A / mañana",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.OPERATIVO_ACTIVO,
            genera_asignacion=True,
            entra_motor_tecnico=True,
            elegible_swap_acc_actual=True,
            fuente=fuente_pr_gope,
            observaciones="Para ACC actual: mañana.",
        ),
        _definicion(
            codigo="B",
            significado="Turno operativo B / tarde",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.OPERATIVO_ACTIVO,
            genera_asignacion=True,
            entra_motor_tecnico=True,
            elegible_swap_acc_actual=True,
            fuente=fuente_pr_gope,
            observaciones="Para ACC actual: tarde.",
        ),
        _definicion(
            codigo="C",
            significado="Turno operativo C / noche",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.OPERATIVO_ACTIVO,
            genera_asignacion=True,
            entra_motor_tecnico=True,
            elegible_swap_acc_actual=True,
            fuente=fuente_pr_gope,
            observaciones="Para ACC actual: noche.",
        ),
        _definicion(
            codigo="D",
            significado="Turno operativo D / trasnoche para esquemas de 6 horas",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.OPERATIVO_CONFIGURABLE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
            observaciones="Soporte normativo futuro; no activo por defecto en ACC actual.",
        ),
        _definicion(
            codigo="X",
            significado="Turno intermedio / refuerzo",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.OPERATIVO_CONFIGURABLE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
            observaciones="Soporte normativo futuro; no activo por defecto en ACC actual.",
        ),
        _definicion(
            codigo="OF",
            significado="Oficina / gestion",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="AE",
            significado="Apertura o extension asignada",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.FUERA_DE_ALCANCE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
            observaciones="Fuera de alcance para ACC actual en esta etapa.",
        ),
        _definicion(
            codigo="AEC",
            significado="Apertura o extension cumplimentada",
            categoria_documental=RosterCodeDocumentCategory.TURNO_BLOQUE_HORARIO,
            categoria_importacion=RosterCodeImportCategory.FUERA_DE_ALCANCE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
            observaciones="Fuera de alcance para ACC actual en esta etapa.",
        ),

        # Instruccion / capacitacion
        _definicion(
            codigo="OJT",
            significado="Instruccion OJT",
            categoria_documental=RosterCodeDocumentCategory.INSTRUCCION_CAPACITACION,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="SIM",
            significado="Instruccion en simulador",
            categoria_documental=RosterCodeDocumentCategory.INSTRUCCION_CAPACITACION,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="CAM",
            significado="Instruccion / capacitacion en Campus",
            categoria_documental=RosterCodeDocumentCategory.INSTRUCCION_CAPACITACION,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="CIPE",
            significado="Curso o comision en CIPE",
            categoria_documental=RosterCodeDocumentCategory.INSTRUCCION_CAPACITACION,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
            observaciones="Normalizado como CIPE para importacion.",
        ),
        _definicion(
            codigo="RT",
            significado="Recurrente teorico",
            categoria_documental=RosterCodeDocumentCategory.INSTRUCCION_CAPACITACION,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="EN",
            significado="Ingles",
            categoria_documental=RosterCodeDocumentCategory.INSTRUCCION_CAPACITACION,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),

        # Licencias / ausencias / medidas administrativas
        _definicion(
            codigo="LA",
            significado="Licencia anual",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LC",
            significado="Licencia COVID",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LN",
            significado="Licencia nacimiento",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LF",
            significado="Familiar enfermo",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LL",
            significado="Fallecimiento",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LM",
            significado="Matrimonio",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LX",
            significado="Examen",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LE",
            significado="Extraordinaria",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LD",
            significado="Licencia medica",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente="PR-GOPE-044 pagina 5",
        ),
        _definicion(
            codigo="LU",
            significado="Mudanza",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LR",
            significado="ART",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LP",
            significado="Preventiva",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="ACA",
            significado="Ausente con aviso",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="ASA",
            significado="Ausente sin aviso",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="LG",
            significado="Licencia gremial",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="SUS",
            significado="Suspension",
            categoria_documental=RosterCodeDocumentCategory.LICENCIA_AUSENCIA_ADMINISTRATIVA,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),

        # Otros
        _definicion(
            codigo="TW",
            significado="Taller / Workshop",
            categoria_documental=RosterCodeDocumentCategory.OTRO,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),
        _definicion(
            codigo="CO",
            significado="Comision",
            categoria_documental=RosterCodeDocumentCategory.OTRO,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_pr_gope,
        ),

        # Codigos locales / ACC Cordoba
        _definicion(
            codigo="RTA",
            significado="Recurrente teorico asociado al turno A / mañana",
            categoria_documental=RosterCodeDocumentCategory.LOCAL_ACC,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_local_acc,
        ),
        _definicion(
            codigo="RTB",
            significado="Recurrente teorico asociado al turno B / tarde",
            categoria_documental=RosterCodeDocumentCategory.LOCAL_ACC,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_local_acc,
        ),
        _definicion(
            codigo="IN",
            significado="Ingles / English",
            categoria_documental=RosterCodeDocumentCategory.LOCAL_ACC,
            categoria_importacion=RosterCodeImportCategory.NORMALIZABLE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_local_acc,
            normaliza_a="EN",
            observaciones="Codigo local normalizable a EN.",
        ),
        _definicion(
            codigo="PSI",
            significado="Psicofisico / turno medico para psicofisico",
            categoria_documental=RosterCodeDocumentCategory.LOCAL_ACC,
            categoria_importacion=RosterCodeImportCategory.NO_OPERATIVO,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_local_acc,
        ),

        # Legacy / historicos
        _definicion(
            codigo="REM",
            significado="Recurrente mañana del esquema viejo M/T/N",
            categoria_documental=RosterCodeDocumentCategory.LEGACY,
            categoria_importacion=RosterCodeImportCategory.NORMALIZABLE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_legacy,
            normaliza_a="RTA",
            observaciones="Legacy local; se normaliza por compatibilidad de importacion.",
        ),
        _definicion(
            codigo="RET",
            significado="Recurrente tarde del esquema viejo M/T/N",
            categoria_documental=RosterCodeDocumentCategory.LEGACY,
            categoria_importacion=RosterCodeImportCategory.NORMALIZABLE,
            genera_asignacion=False,
            entra_motor_tecnico=False,
            elegible_swap_acc_actual=False,
            fuente=fuente_legacy,
            normaliza_a="RTB",
            observaciones="Legacy local; se normaliza por compatibilidad de importacion.",
        ),
    ]

    return {definicion.codigo: definicion for definicion in catalogo}


def obtener_definicion_codigo_roster(
    codigo: str,
    catalogo: dict[str, RosterCodeDefinition] | None = None,
) -> RosterCodeDefinition | None:
    codigo_normalizado = codigo.strip().upper()
    catalogo_activo = catalogo or obtener_catalogo_codigos_acc_default()
    return catalogo_activo.get(codigo_normalizado)


def listar_codigos_por_categoria_importacion(
    categoria: RosterCodeImportCategory,
    catalogo: dict[str, RosterCodeDefinition] | None = None,
) -> list[str]:
    catalogo_activo = catalogo or obtener_catalogo_codigos_acc_default()
    return sorted(
        codigo
        for codigo, definicion in catalogo_activo.items()
        if definicion.categoria_importacion == categoria
    )


def listar_codigos_elegibles_swap_acc_actual(
    catalogo: dict[str, RosterCodeDefinition] | None = None,
) -> list[str]:
    catalogo_activo = catalogo or obtener_catalogo_codigos_acc_default()
    return sorted(
        codigo
        for codigo, definicion in catalogo_activo.items()
        if definicion.elegible_swap_acc_actual
    )