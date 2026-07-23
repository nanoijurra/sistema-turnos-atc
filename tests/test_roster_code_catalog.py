from __future__ import annotations


def test_catalogo_contiene_codigos_consolidados() -> None:
    from src.roster_code_catalog import obtener_catalogo_codigos_acc_default

    catalogo = obtener_catalogo_codigos_acc_default()

    codigos_esperados = {
        "A",
        "B",
        "C",
        "D",
        "X",
        "OF",
        "AE",
        "AEC",
        "OJT",
        "SIM",
        "CAM",
        "CIPE",
        "RT",
        "EN",
        "LA",
        "LC",
        "LN",
        "LF",
        "LL",
        "LM",
        "LX",
        "LE",
        "LD",
        "LU",
        "LR",
        "LP",
        "ACA",
        "ASA",
        "LG",
        "SUS",
        "TW",
        "CO",
        "RTA",
        "RTB",
        "FC",
        "IN",
        "IN/C",
        "PSI",
        "REM",
        "RET",
    }

    assert set(catalogo) == codigos_esperados


def test_catalogo_define_a_b_c_como_elegibles_acc_actual() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        obtener_catalogo_codigos_acc_default,
    )

    catalogo = obtener_catalogo_codigos_acc_default()

    for codigo in ["A", "B", "C"]:
        definicion = catalogo[codigo]
        assert definicion.categoria_importacion == RosterCodeImportCategory.OPERATIVO_ACTIVO
        assert definicion.genera_asignacion is True
        assert definicion.entra_motor_tecnico is True
        assert definicion.elegible_swap_acc_actual is True


def test_catalogo_define_d_x_como_operativos_configurables_no_activos() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        obtener_catalogo_codigos_acc_default,
    )

    catalogo = obtener_catalogo_codigos_acc_default()

    for codigo in ["D", "X"]:
        definicion = catalogo[codigo]
        assert (
            definicion.categoria_importacion
            == RosterCodeImportCategory.OPERATIVO_CONFIGURABLE
        )
        assert definicion.genera_asignacion is False
        assert definicion.entra_motor_tecnico is False
        assert definicion.elegible_swap_acc_actual is False


def test_catalogo_define_no_operativos_consolidados() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        obtener_catalogo_codigos_acc_default,
    )

    catalogo = obtener_catalogo_codigos_acc_default()

    codigos_no_operativos = {
        "OF",
        "OJT",
        "SIM",
        "CAM",
        "CIPE",
        "RT",
        "EN",
        "LA",
        "LC",
        "LN",
        "LF",
        "LL",
        "LM",
        "LX",
        "LE",
        "LD",
        "LU",
        "LR",
        "LP",
        "ACA",
        "ASA",
        "LG",
        "SUS",
        "TW",
        "CO",
        "RTA",
        "RTB",
        "PSI",
    }

    for codigo in codigos_no_operativos:
        definicion = catalogo[codigo]
        assert definicion.categoria_importacion == RosterCodeImportCategory.NO_OPERATIVO
        assert definicion.genera_asignacion is False
        assert definicion.entra_motor_tecnico is False
        assert definicion.elegible_swap_acc_actual is False


def test_catalogo_define_normalizables() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        obtener_catalogo_codigos_acc_default,
    )

    catalogo = obtener_catalogo_codigos_acc_default()

    assert catalogo["IN"].categoria_importacion == RosterCodeImportCategory.NORMALIZABLE
    assert catalogo["IN"].normaliza_a == "EN"

    assert catalogo["FC"].categoria_importacion == RosterCodeImportCategory.NORMALIZABLE
    assert catalogo["FC"].normaliza_a == ""

    assert catalogo["IN/C"].categoria_importacion == RosterCodeImportCategory.NORMALIZABLE
    assert catalogo["IN/C"].normaliza_a == "C"

    assert catalogo["REM"].categoria_importacion == RosterCodeImportCategory.NORMALIZABLE
    assert catalogo["REM"].normaliza_a == "RTA"

    assert catalogo["RET"].categoria_importacion == RosterCodeImportCategory.NORMALIZABLE
    assert catalogo["RET"].normaliza_a == "RTB"


def test_catalogo_define_ae_aec_fuera_de_alcance() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        obtener_catalogo_codigos_acc_default,
    )

    catalogo = obtener_catalogo_codigos_acc_default()

    for codigo in ["AE", "AEC"]:
        definicion = catalogo[codigo]
        assert definicion.categoria_importacion == RosterCodeImportCategory.FUERA_DE_ALCANCE
        assert definicion.genera_asignacion is False
        assert definicion.entra_motor_tecnico is False
        assert definicion.elegible_swap_acc_actual is False


def test_obtener_definicion_codigo_roster_normaliza_entrada() -> None:
    from src.roster_code_catalog import obtener_definicion_codigo_roster

    definicion = obtener_definicion_codigo_roster(" ld ")

    assert definicion is not None
    assert definicion.codigo == "LD"
    assert definicion.significado == "Licencia medica"


def test_obtener_definicion_codigo_roster_desconocido_devuelve_none() -> None:
    from src.roster_code_catalog import obtener_definicion_codigo_roster

    assert obtener_definicion_codigo_roster("XYZ") is None


def test_listar_codigos_elegibles_swap_acc_actual() -> None:
    from src.roster_code_catalog import listar_codigos_elegibles_swap_acc_actual

    assert listar_codigos_elegibles_swap_acc_actual() == ["A", "B", "C"]


def test_listar_codigos_por_categoria_importacion() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        listar_codigos_por_categoria_importacion,
    )

    assert listar_codigos_por_categoria_importacion(
        RosterCodeImportCategory.OPERATIVO_ACTIVO
    ) == ["A", "B", "C"]

    assert listar_codigos_por_categoria_importacion(
        RosterCodeImportCategory.FUERA_DE_ALCANCE
    ) == ["AE", "AEC"]


def test_catalogo_y_configuracion_importacion_acc_estan_alineados() -> None:
    from src.roster_code_catalog import (
        RosterCodeImportCategory,
        obtener_catalogo_codigos_acc_default,
    )
    from src.roster_import_service import obtener_config_acc_default

    catalogo = obtener_catalogo_codigos_acc_default()
    config = obtener_config_acc_default()

    codigos_operativos_activos = {
        codigo
        for codigo, definicion in catalogo.items()
        if definicion.categoria_importacion == RosterCodeImportCategory.OPERATIVO_ACTIVO
    }
    codigos_operativos_configurables = {
        codigo
        for codigo, definicion in catalogo.items()
        if definicion.categoria_importacion
        == RosterCodeImportCategory.OPERATIVO_CONFIGURABLE
    }
    codigos_no_operativos = {
        codigo
        for codigo, definicion in catalogo.items()
        if definicion.categoria_importacion == RosterCodeImportCategory.NO_OPERATIVO
    }
    codigos_fuera_de_alcance = {
        codigo
        for codigo, definicion in catalogo.items()
        if definicion.categoria_importacion == RosterCodeImportCategory.FUERA_DE_ALCANCE
    }
    normalizaciones = {
        codigo: definicion.normaliza_a
        for codigo, definicion in catalogo.items()
        if definicion.categoria_importacion == RosterCodeImportCategory.NORMALIZABLE
    }

    assert config.operativos_activos == codigos_operativos_activos
    assert config.operativos_configurables == codigos_operativos_configurables
    assert config.no_operativos == codigos_no_operativos
    assert config.fuera_de_alcance == codigos_fuera_de_alcance
    assert config.normalizaciones == normalizaciones
