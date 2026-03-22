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
print(f"  Clasificación: {resultado['clasificacion']}")

print("\nImpacto por controlador:")
antes = resultado["resumen_por_controlador_original"]
despues = resultado["resumen_por_controlador_nuevo"]

for controlador, datos_antes in antes.items():
    datos_despues = despues.get(
        controlador,
        {
            "valido": True,
            "score": 100,
            "violaciones": {"total": 0, "hard": 0, "soft": 0},
            "por_regla": {},
        },
    )

    print(f"\n{controlador}:")
    print(f"  Válido : {datos_antes['valido']} -> {datos_despues['valido']}")
    print(f"  Score  : {datos_antes['score']} -> {datos_despues['score']}")
    print(
        f"  Hard   : {datos_antes['violaciones']['hard']} -> "
        f"{datos_despues['violaciones']['hard']}"
    )
    print(
        f"  Total  : {datos_antes['violaciones']['total']} -> "
        f"{datos_despues['violaciones']['total']}"
    )

print("\nRecomendación textual:")
print(generar_recomendacion_textual(resultado))