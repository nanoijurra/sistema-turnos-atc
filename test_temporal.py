from src.scenarios.v2_fatiga import crear_escenario
from src.validator import validar_descanso_minimo

asignaciones = crear_escenario()
violaciones = validar_descanso_minimo(asignaciones, horas_minimas=16)

for v in violaciones:
    print(v.codigo, v.mensaje, v.severidad)