from __future__ import annotations

from datetime import date


def test_importador_registra_timeline_diaria_completa() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01", "02", "03", "04", "05"],
        ["CONTROLADOR A", "A", "", "LD", "C", ""],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    assert not result.errors
    assert len(result.asignaciones_operativas) == 2
    assert len(result.eventos_no_operativos) == 1
    assert len(result.dias_importados) == 5

    estados = [dia.estado for dia in result.dias_importados]
    assert estados == [
        RosterDayStatus.OPERATIVO,
        RosterDayStatus.LIBRE,
        RosterDayStatus.NO_OPERATIVO_DOCUMENTADO,
        RosterDayStatus.OPERATIVO,
        RosterDayStatus.LIBRE,
    ]

    assert result.dias_importados[0].codigo_normalizado == "A"
    assert result.dias_importados[1].codigo_normalizado is None
    assert result.dias_importados[2].codigo_normalizado == "LD"
    assert result.dias_importados[3].codigo_normalizado == "C"
    assert result.dias_importados[4].codigo_normalizado is None


def test_libre_y_no_operativo_documentado_no_son_lo_mismo() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_import_service import importar_roster_desde_matriz

    matriz = [
        ["controlador", "01", "02", "03"],
        ["CONTROLADOR A", "", "LD", ""],
    ]

    result = importar_roster_desde_matriz(matriz, anio=2026, mes=6)

    libres = [
        dia
        for dia in result.dias_importados
        if dia.estado == RosterDayStatus.LIBRE
    ]
    no_operativos = [
        dia
        for dia in result.dias_importados
        if dia.estado == RosterDayStatus.NO_OPERATIVO_DOCUMENTADO
    ]

    assert [dia.fecha for dia in libres] == [
        date(2026, 6, 1),
        date(2026, 6, 3),
    ]
    assert [dia.fecha for dia in no_operativos] == [date(2026, 6, 2)]
    assert no_operativos[0].codigo_normalizado == "LD"


def test_agrupar_timeline_por_controlador_ordena_por_fecha() -> None:
    from src.roster_day_timeline import (
        RosterDayStatus,
        RosterDiaImportado,
        agrupar_timeline_por_controlador,
    )

    dias = [
        RosterDiaImportado(
            controlador="B",
            fecha=date(2026, 6, 2),
            estado=RosterDayStatus.LIBRE,
            raw_value="",
        ),
        RosterDiaImportado(
            controlador="A",
            fecha=date(2026, 6, 2),
            estado=RosterDayStatus.OPERATIVO,
            raw_value="B",
            codigo="B",
            codigo_normalizado="B",
        ),
        RosterDiaImportado(
            controlador="A",
            fecha=date(2026, 6, 1),
            estado=RosterDayStatus.OPERATIVO,
            raw_value="A",
            codigo="A",
            codigo_normalizado="A",
        ),
    ]

    grupos = agrupar_timeline_por_controlador(dias)

    assert list(grupos) == ["B", "A"]
    assert [dia.fecha for dia in grupos["A"]] == [
        date(2026, 6, 1),
        date(2026, 6, 2),
    ]


def test_contar_rachas_libres_solo_cuenta_celdas_vacias() -> None:
    from src.roster_day_timeline import (
        RosterDayStatus,
        RosterDiaImportado,
        obtener_rachas_libres_mayores_a,
    )

    dias = [
        RosterDiaImportado("A", date(2026, 6, 1), RosterDayStatus.LIBRE, ""),
        RosterDiaImportado("A", date(2026, 6, 2), RosterDayStatus.LIBRE, ""),
        RosterDiaImportado(
            "A",
            date(2026, 6, 3),
            RosterDayStatus.NO_OPERATIVO_DOCUMENTADO,
            "LD",
            codigo="LD",
            codigo_normalizado="LD",
        ),
        RosterDiaImportado("A", date(2026, 6, 4), RosterDayStatus.LIBRE, ""),
        RosterDiaImportado("A", date(2026, 6, 5), RosterDayStatus.LIBRE, ""),
    ]

    rachas = obtener_rachas_libres_mayores_a(dias, max_dias=1)

    assert len(rachas) == 2
    assert [[dia.fecha.day for dia in racha] for racha in rachas] == [
        [1, 2],
        [4, 5],
    ]


def test_rachas_c_respetan_cortes_de_calendario() -> None:
    from src.roster_day_timeline import (
        RosterDayStatus,
        RosterDiaImportado,
        obtener_rachas_c_mayores_a,
    )

    dias = [
        RosterDiaImportado(
            "A",
            date(2026, 6, 1),
            RosterDayStatus.OPERATIVO,
            "C",
            codigo="C",
            codigo_normalizado="C",
        ),
        RosterDiaImportado(
            "A",
            date(2026, 6, 2),
            RosterDayStatus.OPERATIVO,
            "C",
            codigo="C",
            codigo_normalizado="C",
        ),
        RosterDiaImportado("A", date(2026, 6, 3), RosterDayStatus.LIBRE, ""),
        RosterDiaImportado(
            "A",
            date(2026, 6, 4),
            RosterDayStatus.OPERATIVO,
            "C",
            codigo="C",
            codigo_normalizado="C",
        ),
        RosterDiaImportado(
            "A",
            date(2026, 6, 5),
            RosterDayStatus.OPERATIVO,
            "C",
            codigo="C",
            codigo_normalizado="C",
        ),
    ]

    rachas = obtener_rachas_c_mayores_a(dias, max_dias=3)

    assert rachas == []


def test_rachas_ab_detectan_mas_de_cinco_dias_consecutivos() -> None:
    from src.roster_day_timeline import (
        RosterDayStatus,
        RosterDiaImportado,
        obtener_rachas_ab_mayores_a,
    )

    codigos = ["A", "B", "A", "B", "A", "B"]

    dias = [
        RosterDiaImportado(
            "A",
            date(2026, 6, indice),
            RosterDayStatus.OPERATIVO,
            codigo,
            codigo=codigo,
            codigo_normalizado=codigo,
        )
        for indice, codigo in enumerate(codigos, start=1)
    ]

    rachas = obtener_rachas_ab_mayores_a(dias, max_dias=5)

    assert len(rachas) == 1
    assert [dia.codigo_normalizado for dia in rachas[0]] == codigos