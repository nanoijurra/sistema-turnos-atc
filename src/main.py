from src.engine import validar_todo
from src.scenarios.v1_basico import crear_escenario


def main():
    asignaciones = crear_escenario()

    resultados = validar_todo(asignaciones, "config_restrictivo.json")

    for r in sorted(resultados, key=lambda x: x["prioridad"]):
        print(f"[P{r['prioridad']}] {r['regla']}: {r['ok']}")

        for v in r["violaciones"]:
            print(f"   - {v['codigo']}: {v['mensaje']}")


if __name__ == "__main__":
    main()