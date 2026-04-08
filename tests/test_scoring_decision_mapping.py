from src.scoring import mapear_decision


def test_beneficioso_es_viable():
    assert mapear_decision("BENEFICIOSO") == "VIABLE"


def test_aceptable_es_observar():
    assert mapear_decision("ACEPTABLE") == "OBSERVAR"


def test_rechazable_es_rechazar():
    assert mapear_decision("RECHAZABLE") == "RECHAZAR"