from src.scenarios.v2_fatiga import crear_escenario as crear_escenario_fatiga
from src.scenarios.v2_noches import crear_escenario as crear_escenario_noches
from src.validator import validar_descanso_minimo, validar_noches_consecutivas


def test_validar_descanso_minimo_detecta_violacion():
    asignaciones = crear_escenario_fatiga()

    violaciones = validar_descanso_minimo(asignaciones, horas_minimas=16)

    assert len(violaciones) == 1
    assert violaciones[0].codigo == "DESCANSO_INSUFICIENTE"
    assert violaciones[0].severidad == "hard"


def test_validar_noches_consecutivas_detecta_exceso():
    asignaciones = crear_escenario_noches()

    violaciones = validar_noches_consecutivas(asignaciones, max_noches=3)

    assert len(violaciones) == 1
    assert violaciones[0].codigo == "EXCESO_NOCHES_CONSECUTIVAS"
    assert violaciones[0].severidad == "hard"