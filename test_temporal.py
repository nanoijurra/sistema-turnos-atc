from datetime import date

from src.scenarios.v2_fatiga import crear_escenario
from src.simulator import mostrar_roster, simular_swap_por_fecha

asignaciones = crear_escenario()

print("Roster original:")
mostrar_roster(asignaciones)
print()

resultado = simular_swap_por_fecha(
    asignaciones,
    fecha_a=date(2026, 3, 3),
    fecha_b=date(2026, 3, 4),
)

print("Valido:", resultado["valido"])
print("Score:", resultado["score"])

for r in resultado["resultados"]:
    print(f"[{r.regla}] {r.ok}")
    for v in r.violaciones:
        print("  ", v.codigo, v.mensaje)