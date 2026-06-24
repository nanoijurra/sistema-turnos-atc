from __future__ import annotations

from datetime import date


def _dia(controlador, dia, estado, codigo=None):
    from src.roster_day_timeline import RosterDiaImportado

    return RosterDiaImportado(
        controlador=controlador,
        fecha=date(2026, 6, dia),
        estado=estado,
        raw_value=codigo or "",
        codigo=codigo,
        codigo_normalizado=codigo,
    )


def test_noches_con_cortes_calendario_no_generan_falso_positivo() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_max_c_consecutivos_timeline

    dias = [
        _dia("AICHINO MELINA", 2, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 4, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 5, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 8, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 10, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 11, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 13, RosterDayStatus.OPERATIVO, "C"),
        _dia("AICHINO MELINA", 14, RosterDayStatus.OPERATIVO, "C"),
    ]

    violaciones = validar_max_c_consecutivos_timeline(dias, max_dias=3)

    assert violaciones == []


def test_mas_de_tres_c_consecutivos_es_hard() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_max_c_consecutivos_timeline

    dias = [
        _dia("CONTROLADOR A", 1, RosterDayStatus.OPERATIVO, "C"),
        _dia("CONTROLADOR A", 2, RosterDayStatus.OPERATIVO, "C"),
        _dia("CONTROLADOR A", 3, RosterDayStatus.OPERATIVO, "C"),
        _dia("CONTROLADOR A", 4, RosterDayStatus.OPERATIVO, "C"),
    ]

    violaciones = validar_max_c_consecutivos_timeline(dias, max_dias=3)

    assert len(violaciones) == 1
    assert violaciones[0].codigo == "EXCESO_C_CONSECUTIVOS"
    assert violaciones[0].severidad == "hard"
    assert violaciones[0].metadata["cantidad_dias"] == 4


def test_mas_de_cinco_ab_consecutivos_es_hard() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_max_ab_consecutivos_timeline

    codigos = ["A", "B", "A", "B", "A", "B"]

    dias = [
        _dia("CONTROLADOR A", indice, RosterDayStatus.OPERATIVO, codigo)
        for indice, codigo in enumerate(codigos, start=1)
    ]

    violaciones = validar_max_ab_consecutivos_timeline(dias, max_dias=5)

    assert len(violaciones) == 1
    assert violaciones[0].codigo == "EXCESO_AB_CONSECUTIVOS"
    assert violaciones[0].severidad == "hard"
    assert violaciones[0].metadata["codigos"] == codigos


def test_corta_racha_ab_con_c_o_libre() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_max_ab_consecutivos_timeline

    dias = [
        _dia("CONTROLADOR A", 1, RosterDayStatus.OPERATIVO, "A"),
        _dia("CONTROLADOR A", 2, RosterDayStatus.OPERATIVO, "B"),
        _dia("CONTROLADOR A", 3, RosterDayStatus.OPERATIVO, "A"),
        _dia("CONTROLADOR A", 4, RosterDayStatus.OPERATIVO, "C"),
        _dia("CONTROLADOR A", 5, RosterDayStatus.OPERATIVO, "A"),
        _dia("CONTROLADOR A", 6, RosterDayStatus.OPERATIVO, "B"),
        _dia("CONTROLADOR A", 7, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR A", 8, RosterDayStatus.OPERATIVO, "A"),
        _dia("CONTROLADOR A", 9, RosterDayStatus.OPERATIVO, "B"),
    ]

    violaciones = validar_max_ab_consecutivos_timeline(dias, max_dias=5)

    assert violaciones == []


def test_mas_de_cinco_libres_consecutivos_es_soft() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_libres_consecutivos_timeline

    dias = [
        _dia("CONTROLADOR A", indice, RosterDayStatus.LIBRE)
        for indice in range(1, 7)
    ]

    violaciones = validar_libres_consecutivos_timeline(dias, max_dias=5)

    assert len(violaciones) == 1
    assert violaciones[0].codigo == "EXCESO_LIBRES_CONSECUTIVOS"
    assert violaciones[0].severidad == "soft"
    assert violaciones[0].metadata["cantidad_dias"] == 6


def test_no_operativo_documentado_no_cuenta_como_libre() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_libres_consecutivos_timeline

    dias = [
        _dia("CONTROLADOR A", 1, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR A", 2, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR A", 3, RosterDayStatus.LIBRE),
        _dia(
            "CONTROLADOR A",
            4,
            RosterDayStatus.NO_OPERATIVO_DOCUMENTADO,
            "LD",
        ),
        _dia("CONTROLADOR A", 5, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR A", 6, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR A", 7, RosterDayStatus.LIBRE),
    ]

    violaciones = validar_libres_consecutivos_timeline(dias, max_dias=5)

    assert violaciones == []


def test_descanso_insuficiente_entre_c_y_a_es_hard() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_descanso_minimo_timeline

    dias = [
        _dia("CONTROLADOR A", 1, RosterDayStatus.OPERATIVO, "C"),
        _dia("CONTROLADOR A", 2, RosterDayStatus.OPERATIVO, "A"),
    ]

    violaciones = validar_descanso_minimo_timeline(dias, horas_minimas=12)

    assert len(violaciones) == 1
    assert violaciones[0].codigo == "DESCANSO_INSUFICIENTE_TIMELINE"
    assert violaciones[0].severidad == "hard"
    assert violaciones[0].metadata["horas_descanso"] == 0


def test_descanso_suficiente_no_genera_falso_positivo() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_descanso_minimo_timeline

    dias = [
        _dia("DIAZ DAIANA", 3, RosterDayStatus.OPERATIVO, "C"),
        _dia("DIAZ DAIANA", 6, RosterDayStatus.OPERATIVO, "A"),
    ]

    violaciones = validar_descanso_minimo_timeline(dias, horas_minimas=12)

    assert violaciones == []


def test_validar_timeline_importada_agrega_por_controlador() -> None:
    from src.roster_day_timeline import RosterDayStatus
    from src.roster_timeline_validator import validar_timeline_importada

    dias = [
        _dia("CONTROLADOR A", 1, RosterDayStatus.OPERATIVO, "C"),
        _dia("CONTROLADOR A", 2, RosterDayStatus.OPERATIVO, "A"),
        _dia("CONTROLADOR B", 1, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR B", 2, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR B", 3, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR B", 4, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR B", 5, RosterDayStatus.LIBRE),
        _dia("CONTROLADOR B", 6, RosterDayStatus.LIBRE),
    ]

    violaciones = validar_timeline_importada(dias)

    codigos = {violacion.codigo for violacion in violaciones}

    assert codigos == {
        "DESCANSO_INSUFICIENTE_TIMELINE",
        "EXCESO_LIBRES_CONSECUTIVOS",
    }