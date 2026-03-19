from engine import validar_todo
from scenarios.v1_basico import crear_escenario

def main():
    asignaciones = crear_escenario()

    resultados = validar_todo(asignaciones, "config_restrictivo.json")

    for r in sorted(resultados, key=lambda x: x["prioridad"]):
        print(f"[P{r['prioridad']}] {r['regla']}: {r['ok']} - {r['mensaje']}")

if __name__ == "__main__":
    main()  