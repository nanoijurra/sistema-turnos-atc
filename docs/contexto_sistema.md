# Contexto del sistema

## Tabla de contenido

- [Proposito](#proposito)
- [Alcance](#alcance)
- [Dominio del problema](#dominio-del-problema)
- [Arquitectura actual](#arquitectura-actual)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Flujo operativo](#flujo-operativo)
- [Capas del sistema](#capas-del-sistema)
- [Estado actual](#estado-actual)
- [Reglas de negocio](#reglas-de-negocio)
- [Principios de diseño](#principios-de-diseno)
- [Evolucion planificada](#evolucion-planificada)
- [Restricciones](#restricciones)
- [Forma de trabajo](#forma-de-trabajo)

---

## Proposito

Describir el contexto operativo, arquitectónico y de estado del sistema de swaps ATC.

Este documento provee una visión global del sistema en su estado actual.

---

## Alcance

Define:

- contexto del sistema
- arquitectura actual
- estructura del proyecto
- flujo operativo
- estado del sistema
- lineamientos de evolución

No define:

- modelo de dominio (ver modelo_dominio.md)
- invariantes (ver invariantes.md)
- contratos entre módulos (ver contratos.md)
- decisiones arquitectónicas (ver decisiones.md)

---

## Dominio del problema

Sistema basado en operaciones reales ATC donde:

- cada controlador tiene asignaciones por fecha
- los swaps impactan restricciones operativas
- existen reglas hard (inviolables) y soft (penalización)

El sistema debe comportarse como un entorno real, no como una simple permuta.

---

## Arquitectura actual

El sistema está organizado en capas con responsabilidades diferenciadas:

- engine → validación técnica de reglas
- simulator → evaluación técnica y clasificación del swap
- swap_service → decisión operativa, workflow y aplicación
- scoring → cálculo de validez agregada y score a partir de resultados técnicos
- (futuro) roster_service → versionado y consistencia

---

## Estructura del proyecto

```text
src/
├── engine.py
├── swap_service.py
├── simulator.py
├── scoring.py
├── models.py
├── rule_types.py
├── validator.py
│
├── roster_store.py
├── request_store.py
│
├── scenarios/
│   ├── v3_controladores_mixto.py
│   ├── v4_controladores_beneficioso.py
│   ├── v5_controladores_beneficioso_mutuo.py
│
└── config/
    └── config_equilibrado.json

tests/
├── test_simulator.py
├── test_operacion.py
├── test_request_store.py
├── test_roster_store.py
├── test_scoring.py
├── test_versioning.py


## Flujo operativo

El flujo de un swap se compone de:

1. crear_swap_request
2. evaluar_swap_request
   - validación de ventana operativa
   - simulación técnica del swap (simulator)
   - clasificación técnica
   - decisión operativa
3. resolver_swap_request
4. aplicar_swap_request
   - creación de nueva versión de roster
   - cancelación de requests obsoletos

Referencia formal:
[Ref: contratos.md #8]

Capas del sistema
src.engine

Responsabilidad:

validación global (validar_todo)
ejecución de reglas
utilidades técnicas

No debe:

tomar decisiones de negocio
participar del flujo de swap
src.swap_service

Responsabilidad:

orquestación del flujo de swap
decisiones operativas
persistencia del request

Incluye:

crear_swap_request
evaluar_swap_request
resolver_swap_request
aplicar_swap_request
src.simulator

Responsabilidad:

simulación de swaps
evaluación técnica comparativa
cálculo de impacto

No debe:

persistir
modificar requests
tomar decisiones operativas
src.scoring

Responsabilidad:

validación del roster
cálculo de score
src.models

Define entidades del dominio:

SwapRequest
RosterVersion
Asignacion
Controlador
Turno
src.rule_types

Define estructuras técnicas:

RuleResult
Violation
Estado actual
Refactor en curso

Separación de capas en progreso:

✔ swap_service implementado
✔ engine parcialmente desacoplado
❌ contratos aún inestables
Problemas identificados
inconsistencias entre índices y controladores
decisiones incorrectas (RECHAZAR vs VIABLE)
desalineación en parámetros dinámicos (min_horas)
errores derivados de refactor incompleto
tests fallando en evaluación de swap
Estado de testing
cobertura amplia (~50+ tests)
estado actual: inestable
prioridad: estabilización
Reglas de negocio
Hard
invalidan el roster
bloquean aprobación
Soft
penalizan score
permiten comparación entre alternativas
Principios de diseño
preservar integridad operativa
no violar reglas hard
minimizar penalización soft
mantener consistencia del modelo
Evolucion planificada
Proximo paso

Introducir:

src.roster_service

Responsabilidades futuras:

versionado de roster
gestión de versiones
manejo de obsolescencia
Restricciones
no romper tests existentes
no introducir hacks
mantener separación de capas
evitar acoplamiento entre engine y servicios
Forma de trabajo

El sistema se desarrolla en tres contextos separados:

arquitectura
implementación
testing/debug

Cada contexto tiene responsabilidades definidas y no debe mezclar concerns.

---


