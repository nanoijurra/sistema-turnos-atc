from src.engine import validar_todo
from src.scenarios.v1_basico import crear_escenario
from src.scoring import es_roster_valido, calcular_score


def main():
    asignaciones = crear_escenario()

    resultados = validar_todo(asignaciones, "config_restrictivo.json")

    for r in sorted(resultados, key=lambda x: x.prioridad):
        print(f"[P{r.prioridad}] {r.regla}: {r.ok}")

        for v in r.violaciones:
            print(f"   - {v.codigo}: {v.mensaje}")

    print()
    print(f"Roster válido: {es_roster_valido(resultados)}")
    print(f"Score: {calcular_score(resultados)}")


if __name__ == "__main__":
    main()