from datetime import datetime
from dataclasses import replace
from src.engine import crear_roster_version_inicial
from src.swap_service import (
    crear_swap_request,
    evaluar_swap_request,
    )
from src.roster_store import limpiar_rosters
from src.request_store import limpiar_requests
from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario


def setup_function():
    limpiar_rosters()
    limpiar_requests()


def test_swap_rechazado_por_ventana_operativa():
    asignaciones_originales = crear_escenario()
    ahora = datetime.now()

    asignaciones = [
        replace(a, fecha=ahora.date())
        for a in asignaciones_originales
    ]

    crear_roster_version_inicial(asignaciones)

    req = crear_swap_request("ATC_A", "ATC_B", 0, 3)

    resultado = evaluar_swap_request(
        asignaciones,
        req,
        evaluar_swap_fn=lambda **kwargs: {"clasificacion": "BENEFICIOSO"},
    )

    assert resultado["decision"] == "RECHAZAR"
    assert resultado["clasificacion"] is None
    assert resultado["motivo"] == "SWAP_FUERA_DE_VENTANA_OPERATIVA"