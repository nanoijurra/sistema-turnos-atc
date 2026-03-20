from datetime import date

from src.scenarios.v3_swap_entre_controladores import crear_escenario
from src.simulator import (
    mostrar_roster,
    simular_swap_entre_controladores,
    generar_recomendacion_textual,
)

asignaciones = crear_escenario()

print("Roster original:")
mostrar_roster(asignaciones)
print()

resultado = simular_swap_entre_controladores(
    asignaciones=asignaciones,
    controlador_a="ATC_A",
    fecha_a=date(2026, 3, 3),
    controlador_b="ATC_B",
    fecha_b=date(2026, 3, 4),
)

print("Resultado del swap entre controladores:")
print(f"  Válido nuevo : {resultado['valido_nuevo']}")
print(f"  Score nuevo  : {resultado['score_nuevo']}")
print(f"  Delta hard   : {resultado['delta_hard']}")
print(f"  Delta total  : {resultado['delta_total_violaciones']}")

resultado["swap"] = {"idx_a": 2, "idx_b": 3}
resultado["impacto"] = 0  # temporal para reutilizar la explicación textual
print("\nRecomendación textual:")
print(generar_recomendacion_textual(resultado))
def test_simular_swap_entre_controladores_devuelve_estructura_valida():
    from datetime import date
    from src.scenarios.v3_swap_entre_controladores import crear_escenario
    from src.simulator import simular_swap_entre_controladores

    asignaciones = crear_escenario()

    resultado = simular_swap_entre_controladores(
        asignaciones=asignaciones,
        controlador_a="ATC_A",
        fecha_a=date(2026, 3, 3),
        controlador_b="ATC_B",
        fecha_b=date(2026, 3, 4),
    )

    assert "valido_nuevo" in resultado
    assert "score_nuevo" in resultado
    assert "delta_hard" in resultado
    assert "delta_total_violaciones" in resultado