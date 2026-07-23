from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from src.roster_calendar_aware_report import (
    ReporteOperativoCalendarAware,
    generar_reporte_operativo_importacion_calendar_aware,
)
from src.roster_import_service import (
    RosterImportResult,
    generar_resumen_importacion,
    importar_roster_desde_matriz,
    importar_roster_desde_csv,
)


FORMATO_CSV_SIMPLE = "CSV_SIMPLE"
FORMATO_CSV_ACC_CBA = "CSV_ACC_CBA"


@dataclass(frozen=True)
class EntradaCargaRosterMes:
    anio: int
    mes: int
    csv_path: Path
    formato: str = FORMATO_CSV_SIMPLE


@dataclass(frozen=True)
class DiagnosticoCargaRosterMes:
    anio: int
    mes: int
    fuente: str
    disponible: bool
    omitido_motivo: str | None
    total_controladores: int
    total_dias_importados: int
    total_asignaciones_operativas: int
    total_eventos_no_operativos: int
    total_warnings_importacion: int
    total_errors_importacion: int
    puede_crear_roster_version: bool
    estado_general_calendar_aware: str | None
    total_violaciones_calendar_aware: int
    total_hard_calendar_aware: int
    total_soft_calendar_aware: int
    por_codigo_calendar_aware: dict[str, int]
    por_severidad_calendar_aware: dict[str, int]
    reporte: ReporteOperativoCalendarAware | None

    @property
    def apto_para_revision_carga(self) -> bool:
        return (
            self.disponible
            and self.puede_crear_roster_version
            and self.total_hard_calendar_aware == 0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "anio": self.anio,
            "mes": self.mes,
            "fuente": self.fuente,
            "disponible": self.disponible,
            "omitido_motivo": self.omitido_motivo,
            "total_controladores": self.total_controladores,
            "total_dias_importados": self.total_dias_importados,
            "total_asignaciones_operativas": self.total_asignaciones_operativas,
            "total_eventos_no_operativos": self.total_eventos_no_operativos,
            "total_warnings_importacion": self.total_warnings_importacion,
            "total_errors_importacion": self.total_errors_importacion,
            "puede_crear_roster_version": self.puede_crear_roster_version,
            "estado_general_calendar_aware": self.estado_general_calendar_aware,
            "total_violaciones_calendar_aware": self.total_violaciones_calendar_aware,
            "total_hard_calendar_aware": self.total_hard_calendar_aware,
            "total_soft_calendar_aware": self.total_soft_calendar_aware,
            "por_codigo_calendar_aware": dict(self.por_codigo_calendar_aware),
            "por_severidad_calendar_aware": dict(self.por_severidad_calendar_aware),
            "apto_para_revision_carga": self.apto_para_revision_carga,
            "reporte": self.reporte.to_dict() if self.reporte is not None else None,
        }


@dataclass(frozen=True)
class DiagnosticoCargaMultiMesCalendarAware:
    meses: tuple[DiagnosticoCargaRosterMes, ...]

    @property
    def total_meses(self) -> int:
        return len(self.meses)

    @property
    def meses_disponibles(self) -> int:
        return sum(1 for mes in self.meses if mes.disponible)

    @property
    def meses_omitidos(self) -> int:
        return sum(1 for mes in self.meses if not mes.disponible)

    @property
    def meses_con_errors_importacion(self) -> int:
        return sum(
            1
            for mes in self.meses
            if mes.total_errors_importacion > 0
        )

    @property
    def meses_con_hard_calendar_aware(self) -> int:
        return sum(
            1
            for mes in self.meses
            if mes.total_hard_calendar_aware > 0
        )

    @property
    def total_hard_calendar_aware(self) -> int:
        return sum(mes.total_hard_calendar_aware for mes in self.meses)

    @property
    def total_soft_calendar_aware(self) -> int:
        return sum(mes.total_soft_calendar_aware for mes in self.meses)

    @property
    def apto_para_revision_carga(self) -> bool:
        return (
            self.total_meses > 0
            and self.meses_omitidos == 0
            and self.meses_con_errors_importacion == 0
            and self.meses_con_hard_calendar_aware == 0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_meses": self.total_meses,
            "meses_disponibles": self.meses_disponibles,
            "meses_omitidos": self.meses_omitidos,
            "meses_con_errors_importacion": self.meses_con_errors_importacion,
            "meses_con_hard_calendar_aware": self.meses_con_hard_calendar_aware,
            "total_hard_calendar_aware": self.total_hard_calendar_aware,
            "total_soft_calendar_aware": self.total_soft_calendar_aware,
            "apto_para_revision_carga": self.apto_para_revision_carga,
            "meses": [
                mes.to_dict()
                for mes in self.meses
            ],
        }


def diagnosticar_carga_multimes_calendar_aware(
    entradas: Iterable[EntradaCargaRosterMes],
    *,
    strict: bool = True,
    omitir_faltantes: bool = True,
    limite_detalles: int | None = None,
) -> DiagnosticoCargaMultiMesCalendarAware:
    diagnosticos = [
        _diagnosticar_mes(
            entrada,
            strict=strict,
            omitir_faltantes=omitir_faltantes,
            limite_detalles=limite_detalles,
        )
        for entrada in entradas
    ]

    return DiagnosticoCargaMultiMesCalendarAware(
        meses=tuple(diagnosticos),
    )


def importar_roster_acc_cba_desde_csv(
    csv_path: Path,
    *,
    anio: int,
    mes: int,
    strict: bool = True,
) -> RosterImportResult:
    return importar_roster_desde_matriz(
        _leer_matriz_acc_cba(csv_path),
        anio=anio,
        mes=mes,
        strict=strict,
        source_type=FORMATO_CSV_ACC_CBA,
    )


def _diagnosticar_mes(
    entrada: EntradaCargaRosterMes,
    *,
    strict: bool,
    omitir_faltantes: bool,
    limite_detalles: int | None,
) -> DiagnosticoCargaRosterMes:
    if not entrada.csv_path.exists():
        if not omitir_faltantes:
            raise FileNotFoundError(str(entrada.csv_path))

        return DiagnosticoCargaRosterMes(
            anio=entrada.anio,
            mes=entrada.mes,
            fuente=str(entrada.csv_path),
            disponible=False,
            omitido_motivo="CSV_NO_DISPONIBLE",
            total_controladores=0,
            total_dias_importados=0,
            total_asignaciones_operativas=0,
            total_eventos_no_operativos=0,
            total_warnings_importacion=0,
            total_errors_importacion=0,
            puede_crear_roster_version=False,
            estado_general_calendar_aware=None,
            total_violaciones_calendar_aware=0,
            total_hard_calendar_aware=0,
            total_soft_calendar_aware=0,
            por_codigo_calendar_aware={},
            por_severidad_calendar_aware={},
            reporte=None,
        )

    resultado_importacion = _importar_entrada(entrada, strict=strict)
    resumen_importacion = generar_resumen_importacion(resultado_importacion)
    reporte = generar_reporte_operativo_importacion_calendar_aware(
        resultado_importacion,
        limite_detalles=limite_detalles,
    )

    return DiagnosticoCargaRosterMes(
        anio=entrada.anio,
        mes=entrada.mes,
        fuente=str(entrada.csv_path),
        disponible=True,
        omitido_motivo=None,
        total_controladores=resumen_importacion.total_controladores,
        total_dias_importados=reporte.total_dias_importados,
        total_asignaciones_operativas=(
            resumen_importacion.total_asignaciones_operativas
        ),
        total_eventos_no_operativos=(
            resumen_importacion.total_eventos_no_operativos
        ),
        total_warnings_importacion=resumen_importacion.total_warnings,
        total_errors_importacion=resumen_importacion.total_errors,
        puede_crear_roster_version=resumen_importacion.puede_crear_roster_version,
        estado_general_calendar_aware=reporte.estado_general,
        total_violaciones_calendar_aware=reporte.total_violaciones,
        total_hard_calendar_aware=reporte.total_hard,
        total_soft_calendar_aware=reporte.total_soft,
        por_codigo_calendar_aware={
            codigo.codigo: codigo.cantidad
            for codigo in reporte.codigos_principales
        },
        por_severidad_calendar_aware=_contar_totales_por_severidad(reporte),
        reporte=reporte,
    )


def _importar_entrada(
    entrada: EntradaCargaRosterMes,
    *,
    strict: bool,
) -> RosterImportResult:
    if entrada.formato == FORMATO_CSV_SIMPLE:
        return importar_roster_desde_csv(
            entrada.csv_path,
            anio=entrada.anio,
            mes=entrada.mes,
            strict=strict,
        )

    if entrada.formato == FORMATO_CSV_ACC_CBA:
        return importar_roster_acc_cba_desde_csv(
            entrada.csv_path,
            anio=entrada.anio,
            mes=entrada.mes,
            strict=strict,
        )

    raise ValueError(f"Formato de entrada no soportado: {entrada.formato}")


def _leer_matriz_acc_cba(csv_path: Path) -> list[list[str]]:
    csv_text = _leer_texto_csv(csv_path)
    delimiter = _detectar_delimitador(csv_text)
    rows = list(csv.reader(csv_text.splitlines(), delimiter=delimiter))
    header_index = _buscar_indice_header_dias(rows)
    header = rows[header_index]
    day_positions = [
        index
        for index, value in enumerate(header)
        if value.strip().isdigit()
    ]
    name_position = day_positions[0] - 1

    matriz = [["controlador"] + [header[index].strip() for index in day_positions]]

    for row in rows[header_index + 1 :]:
        if len(row) <= name_position or not row[name_position].strip():
            continue

        matriz.append(
            [row[name_position].strip()]
            + [
                row[index].strip() if index < len(row) else ""
                for index in day_positions
            ]
        )

    return matriz


def _leer_texto_csv(csv_path: Path) -> str:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return csv_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return csv_path.read_text(encoding="latin-1", errors="replace")


def _detectar_delimitador(csv_text: str) -> str:
    first_line = csv_text.splitlines()[0] if csv_text.splitlines() else ""
    if first_line.count(";") > first_line.count(","):
        return ";"

    return ","


def _buscar_indice_header_dias(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows[:3]):
        if any(value.strip().isdigit() for value in row):
            return index

    raise ValueError("No se encontro encabezado de dias en CSV ACC CBA.")


def _contar_totales_por_severidad(
    reporte: ReporteOperativoCalendarAware,
) -> dict[str, int]:
    conteos: dict[str, int] = {}

    if reporte.total_hard:
        conteos["HARD"] = reporte.total_hard

    if reporte.total_soft:
        conteos["SOFT"] = reporte.total_soft

    return dict(sorted(conteos.items()))
