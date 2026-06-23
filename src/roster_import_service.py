from __future__ import annotations

import calendar
import csv
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any

from src.engine import crear_roster_version_inicial
from src.models import (
    Asignacion,
    Controlador,
    RosterVersion,
    crear_esquema_8h,
)


class RosterCodeCategory(str, Enum):
    OPERATIVO_ACTIVO = "OPERATIVO_ACTIVO"
    OPERATIVO_CONFIGURABLE = "OPERATIVO_CONFIGURABLE"
    NO_OPERATIVO = "NO_OPERATIVO"
    FUERA_DE_ALCANCE = "FUERA_DE_ALCANCE"
    DESCONOCIDO = "DESCONOCIDO"


@dataclass(frozen=True)
class RosterCodeConfig:
    operativos_activos: set[str]
    operativos_configurables: set[str]
    no_operativos: set[str]
    normalizaciones: dict[str, str]
    fuera_de_alcance: set[str]


def obtener_config_acc_default() -> RosterCodeConfig:
    return RosterCodeConfig(
        operativos_activos={"A", "B", "C"},
        operativos_configurables={"D", "X"},
        no_operativos={
            "LA",
            "PSI",
            "RTA",
            "RTB",
            "OJT",
            "SIM",
            "CAM",
            "CIPE",
            "EN",
            "CO",
            "TW",
            "OF",
        },
        normalizaciones={
            "IN": "EN",
            "REM": "RTA",
            "RET": "RTB",
        },
        fuera_de_alcance={"AE", "AEC"},
    )


def normalizar_codigo_roster(
    codigo: str,
    config: RosterCodeConfig,
) -> tuple[str, bool]:
    normalizado = config.normalizaciones.get(codigo, codigo)
    return normalizado, normalizado != codigo


def clasificar_codigo_roster(
    codigo: str,
    config: RosterCodeConfig,
) -> RosterCodeCategory:
    if codigo in config.operativos_activos:
        return RosterCodeCategory.OPERATIVO_ACTIVO

    if codigo in config.operativos_configurables:
        return RosterCodeCategory.OPERATIVO_CONFIGURABLE

    if codigo in config.no_operativos:
        return RosterCodeCategory.NO_OPERATIVO

    if codigo in config.fuera_de_alcance:
        return RosterCodeCategory.FUERA_DE_ALCANCE

    return RosterCodeCategory.DESCONOCIDO


@dataclass(frozen=True)
class RosterImportIssue:
    code: str
    message: str
    severity: str
    row: int | None = None
    column: int | None = None
    controlador: str | None = None
    fecha: date | None = None
    raw_value: str | None = None


@dataclass(frozen=True)
class EventoNoOperativoImportado:
    controlador: str
    fecha: date
    codigo: str
    raw_value: str
    tipo: str | None = None


@dataclass(frozen=True)
class ImportMetadata:
    anio: int
    mes: int
    total_controladores: int
    total_asignaciones_operativas: int
    total_eventos_no_operativos: int
    strict: bool
    source_type: str


@dataclass
class RosterImportResult:
    asignaciones_operativas: list[Asignacion] = field(default_factory=list)
    eventos_no_operativos: list[EventoNoOperativoImportado] = field(default_factory=list)
    warnings: list[RosterImportIssue] = field(default_factory=list)
    errors: list[RosterImportIssue] = field(default_factory=list)
    metadata: ImportMetadata | None = None
    roster_version: RosterVersion | None = None

    @property
    def tiene_errores(self) -> bool:
        return bool(self.errors)

@dataclass(frozen=True)
class RosterImportSummary:
    total_controladores: int
    total_asignaciones_operativas: int
    total_eventos_no_operativos: int
    total_warnings: int
    total_errors: int
    codigos_operativos: dict[str, int]
    codigos_eventos_no_operativos: dict[str, int]
    codigos_normalizados: dict[str, int]
    warnings_por_tipo: dict[str, int]
    errors_por_tipo: dict[str, int]
    codigos_con_warning: dict[str, int]
    codigos_con_error: dict[str, int]
    puede_crear_roster_version: bool    


def _normalizar_codigo(raw_value: Any) -> str:
    if raw_value is None:
        return ""

    return str(raw_value).strip().upper()


def _normalizar_nombre_controlador(raw_value: Any) -> tuple[str, bool]:
    if raw_value is None:
        return "", False

    original = str(raw_value)
    normalizado = " ".join(original.strip().split())
    return normalizado, normalizado != original


def _crear_issue(
    *,
    code: str,
    message: str,
    severity: str,
    row: int | None = None,
    column: int | None = None,
    controlador: str | None = None,
    fecha: date | None = None,
    raw_value: str | None = None,
) -> RosterImportIssue:
    return RosterImportIssue(
        code=code,
        message=message,
        severity=severity,
        row=row,
        column=column,
        controlador=controlador,
        fecha=fecha,
        raw_value=raw_value,
    )


def _validar_anio_mes(anio: int, mes: int) -> None:
    if anio < 1:
        raise ValueError("El año debe ser mayor o igual a 1.")

    if not (1 <= mes <= 12):
        raise ValueError("El mes debe estar entre 1 y 12.")


def _parsear_dia(raw_value: Any, *, column: int, result: RosterImportResult) -> int | None:
    raw = str(raw_value).strip() if raw_value is not None else ""

    if not raw:
        result.errors.append(
            _crear_issue(
                code="DIA_VACIO",
                message="El encabezado de dia no puede estar vacio.",
                severity="ERROR",
                column=column,
                raw_value=raw,
            )
        )
        return None

    try:
        return int(raw)
    except ValueError:
        result.errors.append(
            _crear_issue(
                code="DIA_INVALIDO",
                message=f"Dia invalido en encabezado: {raw}.",
                severity="ERROR",
                column=column,
                raw_value=raw,
            )
        )
        return None


def importar_roster_desde_matriz(
    matriz: list[list[Any]],
    *,
    anio: int,
    mes: int,
    strict: bool = True,
    source_type: str = "MATRIZ_SIMPLE",
    code_config: RosterCodeConfig | None = None,
) -> RosterImportResult:
    _validar_anio_mes(anio, mes)

    result = RosterImportResult()
    esquema = crear_esquema_8h()
    config = code_config or obtener_config_acc_default()
    ultimo_dia = calendar.monthrange(anio, mes)[1]

    if not matriz:
        result.errors.append(
            _crear_issue(
                code="MATRIZ_VACIA",
                message="La matriz de roster no puede estar vacia.",
                severity="ERROR",
            )
        )
        result.metadata = ImportMetadata(
            anio=anio,
            mes=mes,
            total_controladores=0,
            total_asignaciones_operativas=0,
            total_eventos_no_operativos=0,
            strict=strict,
            source_type=source_type,
        )
        return result

    encabezado = matriz[0]
    if not encabezado or str(encabezado[0]).strip().lower() != "controlador":
        result.errors.append(
            _crear_issue(
                code="ENCABEZADO_CONTROLADOR_INVALIDO",
                message="La primera columna debe llamarse controlador.",
                severity="ERROR",
                row=1,
                column=1,
                raw_value=str(encabezado[0]) if encabezado else None,
            )
        )

    dias_por_columna: dict[int, int] = {}
    dias_vistos: set[int] = set()

    for column, raw_dia in enumerate(encabezado[1:], start=2):
        dia = _parsear_dia(raw_dia, column=column, result=result)
        if dia is None:
            continue

        if not (1 <= dia <= ultimo_dia):
            result.errors.append(
                _crear_issue(
                    code="DIA_FUERA_DE_MES",
                    message=f"El dia {dia} esta fuera del mes {mes}/{anio}.",
                    severity="ERROR",
                    column=column,
                    raw_value=str(raw_dia),
                )
            )
            continue

        if dia in dias_vistos:
            result.errors.append(
                _crear_issue(
                    code="DIA_DUPLICADO",
                    message=f"El dia {dia} aparece mas de una vez en el encabezado.",
                    severity="ERROR",
                    column=column,
                    raw_value=str(raw_dia),
                )
            )
            continue

        dias_vistos.add(dia)
        dias_por_columna[column] = dia

    controladores_vistos: set[str] = set()
    total_controladores_validos = 0

    for row, fila in enumerate(matriz[1:], start=2):
        raw_controlador = fila[0] if fila else ""
        controlador, nombre_normalizado = _normalizar_nombre_controlador(raw_controlador)

        if not controlador:
            result.errors.append(
                _crear_issue(
                    code="CONTROLADOR_VACIO",
                    message="El nombre del controlador no puede estar vacio.",
                    severity="ERROR",
                    row=row,
                    column=1,
                    raw_value=str(raw_controlador) if raw_controlador is not None else None,
                )
            )
            continue

        if nombre_normalizado:
            result.warnings.append(
                _crear_issue(
                    code="CONTROLADOR_NORMALIZADO",
                    message="El nombre del controlador fue normalizado.",
                    severity="WARNING",
                    row=row,
                    column=1,
                    controlador=controlador,
                    raw_value=str(raw_controlador),
                )
            )

        if controlador in controladores_vistos:
            result.errors.append(
                _crear_issue(
                    code="CONTROLADOR_DUPLICADO",
                    message=f"Controlador duplicado: {controlador}.",
                    severity="ERROR",
                    row=row,
                    column=1,
                    controlador=controlador,
                    raw_value=str(raw_controlador),
                )
            )
            continue

        controladores_vistos.add(controlador)
        total_controladores_validos += 1
        asignaciones_controlador = 0

        for column, dia in dias_por_columna.items():
            raw_value = fila[column - 1] if column - 1 < len(fila) else ""
            codigo = _normalizar_codigo(raw_value)

            if codigo == "":
                continue

            fecha = date(anio, mes, dia)

            codigo_normalizado, fue_normalizado = normalizar_codigo_roster(
                codigo,
                config,
            )
            categoria = clasificar_codigo_roster(codigo_normalizado, config)

            if fue_normalizado:
                result.warnings.append(
                    _crear_issue(
                        code="CODIGO_NORMALIZADO",
                        message=(
                            f"Codigo de roster normalizado: "
                            f"{codigo} -> {codigo_normalizado}."
                        ),
                        severity="WARNING",
                        row=row,
                        column=column,
                        controlador=controlador,
                        fecha=fecha,
                        raw_value=str(raw_value),
                    )
                )

            if categoria == RosterCodeCategory.OPERATIVO_ACTIVO:
                turno = esquema.obtener_turno(codigo_normalizado)
                result.asignaciones_operativas.append(
                    Asignacion(
                        fecha=fecha,
                        turno=turno,
                        controlador=Controlador(controlador),
                    )
                )
                asignaciones_controlador += 1
                continue

            if categoria == RosterCodeCategory.NO_OPERATIVO:
                result.eventos_no_operativos.append(
                    EventoNoOperativoImportado(
                        controlador=controlador,
                        fecha=fecha,
                        codigo=codigo_normalizado,
                        raw_value=str(raw_value),
                        tipo=RosterCodeCategory.NO_OPERATIVO.value,
                    )
                )
                result.warnings.append(
                    _crear_issue(
                        code="CODIGO_NO_OPERATIVO_IGNORADO",
                        message=(
                            "Codigo no operativo conocido importado como evento "
                            "y excluido del motor tecnico."
                        ),
                        severity="WARNING",
                        row=row,
                        column=column,
                        controlador=controlador,
                        fecha=fecha,
                        raw_value=str(raw_value),
                    )
                )
                continue

            if categoria == RosterCodeCategory.OPERATIVO_CONFIGURABLE:
                issue = _crear_issue(
                    code="CODIGO_OPERATIVO_CONFIGURABLE_NO_ACTIVO",
                    message=(
                        f"Codigo operativo configurable no activo para esta "
                        f"configuracion: {codigo_normalizado}."
                    ),
                    severity="ERROR" if strict else "WARNING",
                    row=row,
                    column=column,
                    controlador=controlador,
                    fecha=fecha,
                    raw_value=str(raw_value),
                )
            elif categoria == RosterCodeCategory.FUERA_DE_ALCANCE:
                issue = _crear_issue(
                    code="CODIGO_FUERA_DE_ALCANCE",
                    message=(
                        f"Codigo fuera de alcance para la configuracion actual: "
                        f"{codigo_normalizado}."
                    ),
                    severity="ERROR" if strict else "WARNING",
                    row=row,
                    column=column,
                    controlador=controlador,
                    fecha=fecha,
                    raw_value=str(raw_value),
                )
            else:
                issue = _crear_issue(
                    code="CODIGO_DESCONOCIDO",
                    message=f"Codigo desconocido: {codigo_normalizado}.",
                    severity="ERROR" if strict else "WARNING",
                    row=row,
                    column=column,
                    controlador=controlador,
                    fecha=fecha,
                    raw_value=str(raw_value),
                )

            if strict:
                result.errors.append(issue)
            else:
                result.warnings.append(issue)    

        if asignaciones_controlador == 0:
            result.warnings.append(
                _crear_issue(
                    code="CONTROLADOR_SIN_TURNOS_OPERATIVOS",
                    message="El controlador no tiene turnos operativos importados.",
                    severity="WARNING",
                    row=row,
                    column=1,
                    controlador=controlador,
                )
            )

    result.metadata = ImportMetadata(
        anio=anio,
        mes=mes,
        total_controladores=total_controladores_validos,
        total_asignaciones_operativas=len(result.asignaciones_operativas),
        total_eventos_no_operativos=len(result.eventos_no_operativos),
        strict=strict,
        source_type=source_type,
    )

    return result


def importar_roster_desde_csv(
    csv_input: str | Path,
    *,
    anio: int,
    mes: int,
    strict: bool = True,
    code_config: RosterCodeConfig | None = None,
) -> RosterImportResult:
    if isinstance(csv_input, Path):
        csv_text = csv_input.read_text(encoding="utf-8-sig")
    else:
        posible_path = Path(csv_input)
        if "\n" not in csv_input and posible_path.exists():
            csv_text = posible_path.read_text(encoding="utf-8-sig")
        else:
            csv_text = csv_input

    reader = csv.reader(StringIO(csv_text))
    matriz = [list(row) for row in reader]

    return importar_roster_desde_matriz(
        matriz,
        anio=anio,
        mes=mes,
        strict=strict,
        source_type="CSV_SIMPLE",
        code_config=code_config,
    )

def _contar_issues_por_tipo(issues: list[RosterImportIssue]) -> dict[str, int]:
    return dict(Counter(issue.code for issue in issues))


def _contar_codigos_en_issues(issues: list[RosterImportIssue]) -> dict[str, int]:
    codigos: Counter[str] = Counter()

    for issue in issues:
        if not issue.code.startswith("CODIGO_"):
            continue

        codigo = _normalizar_codigo(issue.raw_value)
        if codigo:
            codigos[codigo] += 1

    return dict(codigos)


def generar_resumen_importacion(
    result: RosterImportResult,
) -> RosterImportSummary:
    codigos_operativos = Counter(
        asignacion.turno.codigo
        for asignacion in result.asignaciones_operativas
    )

    codigos_eventos_no_operativos = Counter(
        evento.codigo
        for evento in result.eventos_no_operativos
    )

    codigos_normalizados: Counter[str] = Counter()
    for evento in result.eventos_no_operativos:
        raw_codigo = _normalizar_codigo(evento.raw_value)
        if raw_codigo and raw_codigo != evento.codigo:
            codigos_normalizados[f"{raw_codigo}->{evento.codigo}"] += 1

    total_controladores = (
        result.metadata.total_controladores
        if result.metadata is not None
        else 0
    )

    return RosterImportSummary(
        total_controladores=total_controladores,
        total_asignaciones_operativas=len(result.asignaciones_operativas),
        total_eventos_no_operativos=len(result.eventos_no_operativos),
        total_warnings=len(result.warnings),
        total_errors=len(result.errors),
        codigos_operativos=dict(codigos_operativos),
        codigos_eventos_no_operativos=dict(codigos_eventos_no_operativos),
        codigos_normalizados=dict(codigos_normalizados),
        warnings_por_tipo=_contar_issues_por_tipo(result.warnings),
        errors_por_tipo=_contar_issues_por_tipo(result.errors),
        codigos_con_warning=_contar_codigos_en_issues(result.warnings),
        codigos_con_error=_contar_codigos_en_issues(result.errors),
        puede_crear_roster_version=not result.tiene_errores,
    )

def crear_roster_version_desde_importacion(
    result: RosterImportResult,
    *,
    regimen_horario: str = "8H",
) -> RosterVersion:
    if result.tiene_errores:
        raise ValueError("No se puede crear RosterVersion desde una importacion con errores.")

    roster_version = crear_roster_version_inicial(
        result.asignaciones_operativas,
        regimen_horario=regimen_horario,
    )
    result.roster_version = roster_version

    return roster_version