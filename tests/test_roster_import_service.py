from __future__ import annotations

from datetime import date


def _matriz_base():
    return [
        ["controlador", "01", "02", "03"],
        ["CONTROLADOR A", "A", "B", "C"],
        ["CONTROLADOR B", "", "C", "A"],
    ]


def test_importar_matriz_simple_genera_asignaciones_operativas() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    result = importar_roster_desde_matriz(_matriz_base(), anio=2026, mes=6)

    assert not result.errors
    assert len(result.asignaciones_operativas) == 5
    assert result.asignaciones_operativas[0].fecha == date(2026, 6, 1)
    assert result.asignaciones_operativas[0].turno.codigo == "A"
    assert result.asignaciones_operativas[0].controlador.nombre == "CONTROLADOR A"


def test_celda_vacia_no_genera_asignacion() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    result = importar_roster_desde_matriz(_matriz_base(), anio=2026, mes=6)

    asignaciones_b_dia_1 = [
        asignacion
        for asignacion in result.asignaciones_operativas
        if asignacion.controlador.nombre == "CONTROLADOR B"
        and asignacion.fecha == date(2026, 6, 1)
    ]

    assert asignaciones_b_dia_1 == []


def test_codigos_no_operativos_generan_eventos_y_no_asignaciones() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01", "02", "03", "04"],
        ["CONTROLADOR A", "LA", "PSI", "RTA", "RTB"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert not result.errors
    assert len(result.asignaciones_operativas) == 0
    assert len(result.eventos_no_operativos) == 4
    assert {evento.codigo for evento in result.eventos_no_operativos} == {
        "LA",
        "PSI",
        "RTA",
        "RTB",
    }
    assert any(
        warning.code == "CODIGO_NO_OPERATIVO_IGNORADO"
        for warning in result.warnings
    )


def test_codigo_desconocido_strict_true_produce_error() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01"],
        ["CONTROLADOR A", "XYZ"],
    ]

    result = importar_roster_desde_matriz(
        matriz,
        anio=2026,
        mes=6,
        strict=True,
    )

    assert any(error.code == "CODIGO_DESCONOCIDO" for error in result.errors)


def test_codigo_desconocido_strict_false_produce_warning() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01"],
        ["CONTROLADOR A", "XYZ"],
    ]

    result = importar_roster_desde_matriz(
        matriz,
        anio=2026,
        mes=6,
        strict=False,
    )

    assert not result.errors
    assert any(warning.code == "CODIGO_DESCONOCIDO" for warning in result.warnings)


def test_controlador_vacio_produce_error() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01"],
        ["", "A"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert any(error.code == "CONTROLADOR_VACIO" for error in result.errors)
    assert result.asignaciones_operativas == []


def test_controlador_duplicado_produce_error() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01"],
        ["CONTROLADOR A", "A"],
        ["CONTROLADOR A", "B"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert any(error.code == "CONTROLADOR_DUPLICADO" for error in result.errors)


def test_dia_invalido_produce_error() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "XX"],
        ["CONTROLADOR A", "A"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert any(error.code == "DIA_INVALIDO" for error in result.errors)
    assert result.asignaciones_operativas == []


def test_dia_fuera_de_mes_produce_error() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "31"],
        ["CONTROLADOR A", "A"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert any(error.code == "DIA_FUERA_DE_MES" for error in result.errors)
    assert result.asignaciones_operativas == []


def test_nombre_con_espacios_se_normaliza_y_genera_warning() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01"],
        ["  CONTROLADOR   A  ", "A"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert not result.errors
    assert result.asignaciones_operativas[0].controlador.nombre == "CONTROLADOR A"
    assert any(
        warning.code == "CONTROLADOR_NORMALIZADO"
        for warning in result.warnings
    )


def test_controlador_sin_turnos_operativos_genera_warning() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01", "02"],
        ["CONTROLADOR A", "", "LA"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert not result.errors
    assert result.asignaciones_operativas == []
    assert any(
        warning.code == "CONTROLADOR_SIN_TURNOS_OPERATIVOS"
        for warning in result.warnings
    )


def test_metadata_cuenta_controladores_asignaciones_y_eventos() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01", "02", "03"],
        ["CONTROLADOR A", "A", "LA", ""],
        ["CONTROLADOR B", "C", "PSI", "B"],
    ]

    result = importar_roster_desde_matriz(
        matriz,
        anio=2026,
        mes=6,
        strict=False,
    )

    assert result.metadata is not None
    assert result.metadata.anio == 2026
    assert result.metadata.mes == 6
    assert result.metadata.total_controladores == 2
    assert result.metadata.total_asignaciones_operativas == 3
    assert result.metadata.total_eventos_no_operativos == 2
    assert result.metadata.strict is False
    assert result.metadata.source_type == "MATRIZ_SIMPLE"


def test_importar_desde_csv_delega_correctamente_en_matriz() -> None:
    from src.roster_import_service import importar_roster_desde_csv

    csv_text = "controlador,01,02\nCONTROLADOR A,A,B\nCONTROLADOR B,,C\n"

    result = importar_roster_desde_csv(csv_text, anio=2026, mes=6)

    assert not result.errors
    assert len(result.asignaciones_operativas) == 3
    assert result.metadata is not None
    assert result.metadata.source_type == "CSV_SIMPLE"


def test_importar_no_persiste_automaticamente_roster_version() -> None:
    from src.roster_import_service import importar_roster_desde_matriz
    from src.roster_store import limpiar_rosters, obtener_roster_vigente

    limpiar_rosters()

    result = importar_roster_desde_matriz(_matriz_base(), anio=2026, mes=6)

    assert not result.errors
    assert result.roster_version is None
    assert obtener_roster_vigente() is None


def test_importador_no_llama_simulator_ni_crea_requests_ni_aplica(monkeypatch) -> None:
    import src.roster_import_service as modulo

    def prohibido(*args, **kwargs) -> None:
        raise AssertionError("El importador no debe ejecutar workflow ni simulacion.")

    monkeypatch.setattr(modulo, "evaluar_swap", prohibido, raising=False)
    monkeypatch.setattr(modulo, "crear_swap_request", prohibido, raising=False)
    monkeypatch.setattr(modulo, "aplicar_swap_request", prohibido, raising=False)

    result = modulo.importar_roster_desde_matriz(_matriz_base(), anio=2026, mes=6)

    assert not result.errors
    assert len(result.asignaciones_operativas) == 5


def test_codigos_no_operativos_quedan_fuera_del_motor_tecnico() -> None:
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01", "02", "03"],
        ["CONTROLADOR A", "A", "LA", "PSI"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    codigos_asignaciones = {
        asignacion.turno.codigo
        for asignacion in result.asignaciones_operativas
    }

    assert codigos_asignaciones == {"A"}
    assert {evento.codigo for evento in result.eventos_no_operativos} == {"LA", "PSI"}


def test_no_crea_roster_version_si_hay_errores() -> None:
    import pytest

    from src.roster_import_service import (
        crear_roster_version_desde_importacion,
        importar_roster_desde_matriz,
    )
    from src.roster_store import limpiar_rosters, obtener_roster_vigente

    limpiar_rosters()

    matriz = [
        ["controlador", "01"],
        ["CONTROLADOR A", "XYZ"],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    with pytest.raises(ValueError, match="importacion con errores"):
        crear_roster_version_desde_importacion(result)

    assert obtener_roster_vigente() is None


def test_crea_roster_version_si_no_hay_errores() -> None:
    from src.roster_import_service import (
        crear_roster_version_desde_importacion,
        importar_roster_desde_matriz,
    )
    from src.roster_store import limpiar_rosters, obtener_roster_vigente

    limpiar_rosters()

    result = importar_roster_desde_matriz(_matriz_base(), anio=2026, mes=6)

    roster = crear_roster_version_desde_importacion(result)

    assert roster.version_number == 1
    assert roster.vigente is True
    assert roster.regimen_horario == "8H"
    assert len(roster.asignaciones) == len(result.asignaciones_operativas)
    assert result.roster_version == roster
    assert obtener_roster_vigente() == roster