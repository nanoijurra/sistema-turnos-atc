from src.scenarios.v2_fatiga import crear_escenario
from src.simulator import (
    mostrar_roster,
    explorar_swaps,
    generar_pares_swap,
    filtrar_swaps_validos,
    filtrar_swaps_utiles,
)

asignaciones = crear_escenario()

print("Roster original:")
mostrar_roster(asignaciones)
print()

pares = generar_pares_swap(asignaciones)
ranking = explorar_swaps(asignaciones, pares)
swaps_validos = filtrar_swaps_validos(ranking)
swaps_utiles = filtrar_swaps_utiles(ranking)

print("Ranking automático de swaps:")
for i, resultado in enumerate(ranking, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Válido nuevo         : {resultado['valido_nuevo']}")
    print(f"  Score nuevo          : {resultado['score_nuevo']}")
    print(f"  Impacto              : {resultado['impacto']}")
    print(f"  Delta score          : {resultado['delta_score']}")
    print(f"  Hard antes           : {resultado['resumen_original']['hard']}")
    print(f"  Hard después         : {resultado['resumen_nuevo']['hard']}")
    print(f"  Total antes          : {resultado['resumen_original']['total']}")
    print(f"  Total después        : {resultado['resumen_nuevo']['total']}")
    print(f"  Delta hard           : {resultado['delta_hard']}")
    print(f"  Delta total          : {resultado['delta_total_violaciones']}")
    print(f"  Mejora               : {resultado['mejora']}")
    print(f"  Empeora              : {resultado['empeora']}")
    print(f"  Igual                : {resultado['igual']}")

print("\nSwaps válidos:")
for i, resultado in enumerate(swaps_validos, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap válido ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Impacto       : {resultado['impacto']}")
    print(f"  Hard después  : {resultado['resumen_nuevo']['hard']}")
    print(f"  Total después : {resultado['resumen_nuevo']['total']}")
    print(f"  Delta hard    : {resultado['delta_hard']}")
    print(f"  Delta total   : {resultado['delta_total_violaciones']}")

print("\nSwaps útiles:")
for i, resultado in enumerate(swaps_utiles, start=1):
    swap = resultado["swap"]

    print(f"\n#{i} Swap útil ({swap['idx_a']} <-> {swap['idx_b']})")
    print(f"  Impacto       : {resultado['impacto']}")
    print(f"  Hard después  : {resultado['resumen_nuevo']['hard']}")
    print(f"  Total después : {resultado['resumen_nuevo']['total']}")
    print(f"  Delta hard    : {resultado['delta_hard']}")
    print(f"  Delta total   : {resultado['delta_total_violaciones']}")
    print("  Impacto por regla:")

    for regla, datos_antes in resultado["resumen_por_regla_original"].items():
        datos_despues = resultado["resumen_por_regla_nuevo"].get(
            regla,
            {"total": 0, "hard": 0, "soft": 0},
        )

        print(
            f"    - {regla}: "
            f"hard {datos_antes['hard']} -> {datos_despues['hard']}, "
            f"total {datos_antes['total']} -> {datos_despues['total']}"
        )