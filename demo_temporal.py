from src.simulator import (
    mostrar_roster,
    explorar_swaps_entre_controladores,
    filtrar_swaps_validos,
    filtrar_swaps_utiles,
    generar_recomendacion_textual,
    crear_swap_request,
    evaluar_swap_request,
    resolver_swap_request,
    aplicar_swap_request,
    mostrar_historial_swap_request,
)

from src.scenarios.v3_controladores_mixto import crear_escenario as escenario_mixto
from src.scenarios.v4_controladores_beneficioso import crear_escenario as escenario_beneficioso
from src.scenarios.v5_controladores_beneficioso_mutuo import (
    crear_escenario as escenario_beneficioso_mutuo,
)
from src.engine import crear_roster_version_inicial
from src.request_store import limpiar_requests
from src.roster_store import limpiar_rosters


def ejecutar_demo(nombre: str, asignaciones: list) -> None:
    limpiar_requests()
    limpiar_rosters()

    roster_inicial = crear_roster_version_inicial(asignaciones)

    print("=" * 80)
    print(f"ESCENARIO: {nombre}")
    print("=" * 80)

    print(
        f"Roster vigente inicial: "
        f"v{roster_inicial.version_number} | id={roster_inicial.id} | "
        f"régimen={roster_inicial.regimen_horario}"
    )
    print()

    print("Roster original:")
    mostrar_roster(asignaciones)
    print()

    print("Ejemplo de SwapRequest:")
    request = crear_swap_request(asignaciones, 0, 3, motivo="Intercambio personal")

    print(f"  ID                : {request.id}")
    print(f"  Controlador A     : {request.controlador_a}")
    print(f"  Controlador B     : {request.controlador_b}")
    print(f"  Índices           : {request.idx_a} <-> {request.idx_b}")
    print(f"  Estado            : {request.estado}")
    print(f"  Fecha creación    : {request.fecha_creacion}")
    print(f"  Decisión sugerida : {request.decision_sugerida}")
    print(f"  Motivo            : {request.motivo}")
    print()
    print(mostrar_historial_swap_request(request))

    print("\nEvaluación del SwapRequest:")
    resultado_request = evaluar_swap_request(asignaciones, request)

    print(f"  Clasificación         : {resultado_request['clasificacion']}")
    print(f"  Decisión calculada    : {resultado_request['decision']}")
    print(f"  Decisión en request   : {request.decision_sugerida}")

    if "roster_version_id" in resultado_request:
        print(f"  Roster version id     : {resultado_request['roster_version_id']}")
    if "roster_version_number" in resultado_request:
        print(f"  Roster version number : {resultado_request['roster_version_number']}")

    print("\nResolviendo SwapRequest automáticamente...")

    if resultado_request["decision"] == "APROBABLE":
        request = resolver_swap_request(request, "ACEPTAR")
    elif resultado_request["decision"] == "RECHAZAR":
        request = resolver_swap_request(request, "RECHAZAR")
    else:
        print("  (queda en observación, no se resuelve automáticamente)")

    print(f"  Estado final         : {request.estado}")
    print(f"  Fecha resolución     : {request.fecha_resolucion}")
    print(f"  Decisión sugerida    : {request.decision_sugerida}")
    print()
    print(mostrar_historial_swap_request(request))
    print()

    if request.estado == "ACEPTADO":
        print("Aplicando SwapRequest al roster...")
        roster_aplicado = aplicar_swap_request(asignaciones, request)

        print(
            f"Nueva versión vigente: "
            f"v{roster_aplicado.version_number} | id={roster_aplicado.id} | "
            f"base_version_id={roster_aplicado.base_version_id}"
        )
        print()

        print("Roster actualizado:")
        mostrar_roster(roster_aplicado.asignaciones)
        print()
        print(mostrar_historial_swap_request(request))
        print()

    ranking = explorar_swaps_entre_controladores(asignaciones)
    swaps_validos = filtrar_swaps_validos(ranking)
    swaps_utiles = filtrar_swaps_utiles(ranking)

    print("Ranking automático de swaps entre controladores:")
    for i, resultado in enumerate(ranking, start=1):
        swap = resultado["swap"]

        print(f"\n#{i} Swap ({swap['idx_a']} <-> {swap['idx_b']})")
        print(f"  Válido nuevo : {resultado['valido_nuevo']}")
        print(f"  Score nuevo  : {resultado['score_nuevo']}")
        print(f"  Impacto      : {resultado['impacto']}")
        print(f"  Delta hard   : {resultado['delta_hard']}")
        print(f"  Delta total  : {resultado['delta_total_violaciones']}")
        print(f"  Clasificación: {resultado['clasificacion']}")

    print("\nSwaps válidos:")
    if not swaps_validos:
        print("  (ninguno)")
    else:
        for i, resultado in enumerate(swaps_validos, start=1):
            swap = resultado["swap"]

            print(f"\n#{i} Swap válido ({swap['idx_a']} <-> {swap['idx_b']})")
            print(f"  Impacto      : {resultado['impacto']}")
            print(f"  Clasificación: {resultado['clasificacion']}")

    print("\nSwaps útiles:")
    if not swaps_utiles:
        print("  (ninguno)")
    else:
        for i, resultado in enumerate(swaps_utiles, start=1):
            swap = resultado["swap"]

            print(f"\n#{i} Swap útil ({swap['idx_a']} <-> {swap['idx_b']})")
            print(f"  Impacto      : {resultado['impacto']}")
            print(f"  Clasificación: {resultado['clasificacion']}")
            print("  Recomendación textual:")
            print(f"    {generar_recomendacion_textual(resultado)}")

    print("\n")


ejecutar_demo("MIXTO", escenario_mixto())
ejecutar_demo("BENEFICIOSO", escenario_beneficioso())
ejecutar_demo("BENEFICIOSO MUTUO", escenario_beneficioso_mutuo())