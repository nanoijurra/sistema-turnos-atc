from src.scenarios.v2_fatiga import crear_escenario
from src.simulator import (
    mostrar_roster,
    explorar_swaps,
    generar_pares_swap,
    filtrar_swaps_validos,
)

asignaciones = crear_escenario()

print("Roster original:")
mostrar_roster(asignaciones)
print()

pares = generar_pares_swap(asignaciones)
ranking = explorar_swaps(asignaciones, pares)
swaps_validos = filtrar_swaps_validos(ranking)

print("Ranking automático de swaps:")
for i, resultado in enumerate(ranking, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Válido nuevo : {resultado['valido_nuevo']}")
    print(f"  Score nuevo  : {resultado['score_nuevo']}")
    print(f"  Delta score  : {resultado['delta_score']}")
    print(f"  Mejora       : {resultado['mejora']}")

print("\nSwaps válidos:")
for i, resultado in enumerate(swaps_validos, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap válido ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Score nuevo : {resultado['score_nuevo']}")
    print(f"  Delta score : {resultado['delta_score']}")