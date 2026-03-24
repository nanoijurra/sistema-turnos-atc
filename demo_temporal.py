from src.simulator import crear_swap_request
from src.simulator import (
    mostrar_roster,
    explorar_swaps_entre_controladores,
    filtrar_swaps_validos,
    filtrar_swaps_utiles,
    generar_recomendacion_textual,
)

from src.scenarios.v3_controladores_mixto import crear_escenario as escenario_mixto
from src.scenarios.v4_controladores_beneficioso import crear_escenario as escenario_beneficioso
from src.scenarios.v5_controladores_beneficioso_mutuo import crear_escenario as escenario_beneficioso_mutuo


def ejecutar_demo(nombre: str, asignaciones: list) -> None:
    print("=" * 80)
    print(f"ESCENARIO: {nombre}")
    print("=" * 80)

    print("Roster original:")
    mostrar_roster(asignaciones)
    print("\nEjemplo de SwapRequest:")

    request = crear_swap_request(asignaciones, 0, 3, motivo="Intercambio personal")

    print(f"  ID           : {request.id}")
    print(f"  Controlador A: {request.controlador_a}")
    print(f"  Controlador B: {request.controlador_b}")
    print(f"  Índices      : {request.idx_a} <-> {request.idx_b}")
    print(f"  Estado       : {request.estado}")
    print(f"  Motivo       : {request.motivo}")
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