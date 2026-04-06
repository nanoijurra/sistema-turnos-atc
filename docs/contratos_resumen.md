# Contratos resumen

## engine
- valida reglas
- no toma decisiones de negocio

## simulator.evaluar_swap
- simula swap
- no persiste
- devuelve clasificación:
  - BENEFICIOSO
  - ACEPTABLE
  - RECHAZABLE

## swap_service.evaluar_swap_request
- valida request
- valida ventana operativa
- usa evaluar_swap
- transforma clasificación en decisión:
  - BENEFICIOSO → APROBABLE
  - ACEPTABLE → OBSERVAR
  - RECHAZABLE → RECHAZAR
- persiste request evaluado

## swap_service.aplicar_swap_request
- solo aplica requests ACEPTADOS
- crea nueva versión de roster
- cancela requests obsoletos
- marca request como APLICADO

## reglas de consistencia
- simulator clasifica
- swap_service decide
- aplicar no reevalúa
- engine no decide negocio