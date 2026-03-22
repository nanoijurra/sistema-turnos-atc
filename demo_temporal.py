from src.scenarios.v3_swap_entre_controladores import crear_escenario
from src.simulator import (
    mostrar_roster,
    explorar_swaps_entre_controladores,
    filtrar_swaps_validos,
    filtrar_swaps_utiles,
    generar_recomendacion_textual,
)

asignaciones = crear_escenario()

print("Roster original:")
mostrar_roster(asignaciones)
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
for i, resultado in enumerate(swaps_validos, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap válido ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Impacto      : {resultado['impacto']}")
    print(f"  Clasificación: {resultado['clasificacion']}")

print("\nSwaps útiles:")
for i, resultado in enumerate(swaps_utiles, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap útil ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Impacto      : {resultado['impacto']}")
    print(f"  Clasificación: {resultado['clasificacion']}")
    print("  Recomendación textual:")
    print(f"    {generar_recomendacion_textual(resultado)}")