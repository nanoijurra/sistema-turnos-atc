from datetime import date

from src.scenarios.v2_fatiga import crear_escenario
from src.simulator import mostrar_roster, evaluar_swap

asignaciones = crear_escenario()

print("Roster original:")
mostrar_roster(asignaciones)
print()

resultado = evaluar_swap(asignaciones, 2, 3)

print("ANTES:")
print("  Valido:", resultado["valido_original"])
print("  Score :", resultado["score_original"])

print("\nDESPUÉS:")
print("  Valido:", resultado["valido_nuevo"])
print("  Score :", resultado["score_nuevo"])

print("\nDELTA:")
print("  Delta score:", resultado["delta_score"])
print("  Mejora:", resultado["mejora"])
print("  Empeora:", resultado["empeora"])
print("  Igual:", resultado["igual"])