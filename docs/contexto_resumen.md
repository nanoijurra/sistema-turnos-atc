Sistema de swaps ATC en Python.

Estructura:
- engine → validación y reglas
- swap_service → lógica de negocio (crear/evaluar/resolver/aplicar swaps)
- simulator → simulación y exploración
- scoring → score y validez
- models → entidades
- stores → persistencia en memoria

Flujo:
crear → evaluar → resolver → aplicar → nueva versión de roster

Estado actual:
refactor en curso (separación engine vs services)

Problemas actuales:
- decisiones incorrectas (VIABLE vs RECHAZAR)
- inconsistencias entre índices y controladores
- tests fallando tras refactor

Restricciones:
- no romper tests
- no meter lógica en engine
- mantener arquitectura desacoplada