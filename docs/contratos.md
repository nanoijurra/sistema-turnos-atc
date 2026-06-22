# Contratos del sistema

## Tabla de contenido

- [1. Proposito](#1-proposito)
- [2. Alcance](#2-alcance)
- [3. Referencias](#3-referencias)
- [4. Definiciones](#4-definiciones)
- [5. Estructura principal](#5-estructura-principal)
  - [5.1 Capas del sistema](#51-capas-del-sistema)
- [6. Contratos funcionales](#6-contratos-funcionales)
  - [6.1 validar_todo](#61-validar_todo)
  - [6.2 evaluar_swap](#62-evaluar_swap)
  - [6.3 evaluar_swap_request](#63-evaluar_swap_request)
  - [6.3.1 resolver_swap_request](#631-resolver_swap_request)
  - [6.4 aplicar_swap_request](#64-aplicar_swap_request)
  - [6.5 Contrato de clasificacion y decision](#65-contrato-de-clasificacion-y-decision)
- [7. Responsabilidades](#7-responsabilidades)
  - [7.1 Contrato definitivo de src.engine](#71-contrato-definitivo-de-srcengine)
  - [7.2 Contrato definitivo de src.simulator](#72-contrato-definitivo-de-srcsimulator)
  - [7.3 Contrato definitivo de src.swap_service](#73-contrato-definitivo-de-srcswap_service)
  - [7.4 Contrato de ventana operativa](#74-contrato-de-ventana-operativa)
  - [7.5 Contrato de dependencia entre modulos](#75-contrato-de-dependencia-entre-modulos)
- [8. Flujo](#8-flujo)
  - [8.1 Contrato definitivo de evaluacion y decision](#81-contrato-definitivo-de-evaluacion-y-decision)
- [9. Notas](#9-notas)
  - [9.1 Nota de evolucion](#91-nota-de-evolucion)
  - [9.2 Aclaracion sobre indices estructurales](#92-aclaracion-sobre-indices-estructurales)
  - [9.3 Aclaracion sobre mapeo normal](#93-aclaracion-sobre-mapeo-normal)
  - [9.4 Diferencia entre obsolescencia y cancelacion](#94-diferencia-entre-obsolescencia-y-cancelacion)
- [10. Reglas criticas](#10-reglas-criticas)
  - [10.1 Reglas de consistencia](#101-reglas-de-consistencia)
  - [10.2 Contrato minimo de salida de evaluar_swap](#102-contrato-minimo-de-salida-de-evaluar_swap)
  - [10.3 Contrato de mapeo clasificacion tecnica a decision operativa](#103-contrato-de-mapeo-clasificacion-tecnica-a-decision-operativa)
  - [10.4 Regla de separacion de planos](#104-regla-de-separacion-de-planos)
  - [10.5 Regla critica de frontera](#105-regla-critica-de-frontera)
- [11. Trazabilidad](#11-trazabilidad)
  - [11.1 Contrato de estados de SwapRequest](#111-contrato-de-estados-de-swaprequest)
  - [11.2 Contratos de consistencia de datos](#112-contratos-de-consistencia-de-datos)
  - [11.3 Contratos de frontera de simulator](#113-contratos-de-frontera-de-simulator)
  - [11.4 Contrato consolidado entre simulator y swap_service](#114-contrato-consolidado-entre-simulator-y-swap_service)
- [12. Contrato de frontera publica de simulator](#12-contrato-de-frontera-publica-de-simulator)
- [13. Contrato de priorizacion historica de swaps](#13-contrato-de-priorizacion-historica-de-swaps)
- [14. Contrato de equidad historica avanzada](#14-contrato-de-equidad-historica-avanzada)
- [15. Contrato de flujo de oferta con equidad historica](#15-contrato-de-flujo-de-oferta-con-equidad-historica)
- [16. Contrato de candidate_generation](#16-contrato-de-candidate_generation)
- [17. Contrato de roster_index](#17-contrato-de-roster_index)
- [Contrato 18 - Fachada para crear request desde oferta y evaluar formalmente](#contrato-18---fachada-para-crear-request-desde-oferta-y-evaluar-formalmente)
- [Contrato 19 - Resolucion operativa posterior de SwapRequest evaluada](#contrato-19---resolucion-operativa-posterior-de-swaprequest-evaluada)
- [Contrato 20 - Aplicacion de SwapRequest aprobada](#contrato-20---aplicacion-de-swaprequest-aprobada)

---

## 1. Proposito

Definir contratos explícitos entre módulos para garantizar consistencia, evitar ambigüedades y estabilizar el sistema durante refactors.

---

## 2. Alcance

Este documento define:
- contratos entre módulos
- responsabilidades por capa
- flujo de evaluación, decisión y aplicación

No define:
- implementación concreta
- reglas del dominio (ver invariantes.md)
- modelo conceptual (ver modelo_dominio.md)

---

## 3. Referencias

- [Ref: decisiones.md #11]
- [Ref: decisiones.md #17]
- [Ref: decisiones.md #25]
- [Ref: invariantes.md]
- [Ref: modelo_dominio.md]

---

## 4. Definiciones

- **clasificación técnica** → resultado técnico del swap (simulator)
- **decision_sugerida** → tratamiento operativo sugerido durante la evaluacion formal del request (swap_service)
- **resolucion operativa** → accion explicita posterior que lleva una request evaluada a APROBADO, RECHAZADO o CANCELADO
- **aplicacion** → ejecucion de una request APROBADO sobre roster versionado
- **estado** → etapa del workflow del request

---

## 5. Estructura principal

### 5.1 Capas del sistema

#### src.engine

Responsabilidad:
- validación de reglas
- ejecución de reglas configuradas
- utilidades técnicas

No debe:
- tomar decisiones de negocio (VIABLE / OBSERVAR / RECHAZAR)
- modificar estado de SwapRequest
- aplicar swaps

#### src.swap_service

Responsabilidad:
- flujo completo del swap:
  - crear
  - evaluar
  - resolver
  - aplicar
- decision_sugerida durante evaluacion formal
- resolucion operativa explicita
- aplicacion de requests aprobadas
- persistencia de requests
- trazabilidad del workflow

No debe:
- duplicar lógica de validación del engine
- ejecutar reglas directamente fuera de validar_todo
- convertir automaticamente decision_sugerida en estado terminal
- aplicar requests no aprobadas

#### src.simulator

Responsabilidad:
- simular swaps
- comparar estado antes/después
- calcular impacto

No debe:
- persistir cambios
- modificar requests
- crear versiones de roster

#### src.scoring

Responsabilidad:
- calcular validez agregada del roster a partir de resultados del engine
- calcular score basado en violaciones soft

No debe:
- ejecutar reglas
- redefinir semántica de validaciones

---

## 6. Contratos funcionales

### 6.1 validar_todo

**Firma:** `validar_todo(asignaciones, config_file) -> list[RuleResult]`

Debe:
- ejecutar reglas configuradas
- agrupar por controlador
- devolver lista ordenada por prioridad

No debe:
- modificar datos
- tomar decisiones de negocio

### 6.2 evaluar_swap

**Firma:** `evaluar_swap(asignaciones, idx_a, idx_b, config_file) -> dict`
**Modulo:** `src.simulator`

#### Proposito

Simular un intercambio de turnos sobre un conjunto de asignaciones y devolver una evaluación técnica completa del estado antes y después, sin persistir cambios.

#### Responsabilidad

Es la fuente única de verdad de la clasificación técnica del swap.

#### Debe hacer

- construir un escenario "antes" con las asignaciones originales
- construir un escenario "después" aplicando el intercambio entre `idx_a` e `idx_b`
- validar técnicamente ambos escenarios usando engine
- calcular validez y score de ambos escenarios usando scoring
- resumir violaciones por regla
- calcular diferencias entre ambos estados
- clasificar el swap

#### Clasificacion permitida

- BENEFICIOSO
- ACEPTABLE
- RECHAZABLE

#### Criterio de clasificacion

La clasificación se basa exclusivamente en:
- validez hard antes/después
- score antes/después
- variación de hard violations
- variación de soft violations

No puede incorporar:
- ventana operativa
- estados del request
- criterios manuales de aprobación
- workflow de negocio

#### No debe hacer

- no persiste
- no modifica `SwapRequest`
- no crea versiones de roster
- no cambia estados
- no registra history
- no toma decisiones operativas
- no aplica el swap real

#### Entrada esperada

- `asignaciones`: colección de asignaciones del roster evaluado
- `idx_a`: índice de la asignación origen
- `idx_b`: índice de la asignación destino
- `config_file`: configuración de reglas

#### Validaciones propias permitidas

Puede validar únicamente:
- existencia de índices
- posibilidad técnica de construir la simulación

No debe validar:
- ventana operativa
- estado del request
- vigencia de `roster_version_id`
- reglas de workflow

#### Salida minima obligatoria

Debe devolver una estructura estable con al menos:

- `idx_a`
- `idx_b`
- `antes`
  - `valido`
  - `score`
  - `resumen_por_regla`
- `despues`
  - `valido`
  - `score`
  - `resumen_por_regla`
- `delta_score`
- `delta_hard`
- `delta_soft`
- `clasificacion`

#### Regla critica

La `clasificacion_tecnica` devuelta por `evaluar_swap` es definitiva a nivel técnico y no puede ser recalculada, reemplazada ni falsificada por `swap_service`.

### 6.3 evaluar_swap_request

**Firma:** `evaluar_swap_request(request_id, ...) -> dict`  
**Modulo:** `src.swap_service`

#### Proposito

Evaluar un `SwapRequest` dentro del flujo de negocio, consumir la clasificacion tecnica formal, producir una `decision_sugerida`, actualizar su estado a `EVALUADO` y persistir el resultado.

#### Responsabilidad

Es la fuente única de verdad de la evaluacion formal del request y de la `decision_sugerida`.

No es fuente de verdad de aprobacion, rechazo terminal, cancelacion ni aplicacion.

#### Debe hacer

- cargar el `SwapRequest`
- validar consistencia estructural del request
- validar que el request esté en estado evaluable
- validar que el request pertenezca a una `roster_version_id` válida
- validar que el request esté asociado a la versión vigente del sistema
- validar ventana operativa
- si corresponde, invocar `simulator.evaluar_swap(...)`
- mapear clasificación técnica a `decision_sugerida`
- actualizar estado a `EVALUADO`
- persistir request
- registrar history

#### Mapeo obligatorio clasificacion a decision

- BENEFICIOSO → VIABLE
- ACEPTABLE → OBSERVAR
- RECHAZABLE → RECHAZAR

#### Excepcion operativa obligatoria

Si falla una restricción operativa, como ventana operativa:
- la decisión operativa debe ser `RECHAZAR`
- el motivo debe registrarse explícitamente
- la clasificación técnica no debe ser reemplazada por una clasificación operativa ficticia

El sistema puede:
- no producir clasificación técnica si la evaluación técnica no se ejecuta
- o conservarla separadamente si existe

En ningún caso una restricción operativa redefine la naturaleza de la clasificación técnica.

#### Validaciones estructurales esperadas

Debe validar:
- que el request exista
- que el estado actual permita evaluación
- que `idx_a` e `idx_b` sean coherentes con el roster
- que `controlador_a` y `controlador_b` correspondan con las asignaciones referidas
- que exista `roster_version_id`
- que el request pertenezca a la versión correcta
- que no esté obsoleto respecto de la versión vigente

#### Validaciones operativas propias

Debe validar:
- ventana operativa
- otras precondiciones de negocio no técnicas del roster

#### No debe hacer

- no ejecuta reglas directamente por fuera de engine/simulator
- no recalcula score
- no reclasifica el swap
- no aplica el swap
- no crea nueva versión
- no cancela requests obsoletos
- no aprueba
- no rechaza terminalmente
- no cancela por resolucion operativa
- no convierte `decision_sugerida` en estado terminal
- no resuelve aceptación/rechazo final fuera del flujo definido

#### Estado resultante

Si la evaluación se completa:
- el request queda en estado `EVALUADO`

#### Persistencia obligatoria

Debe persistir al menos:
- clasificación técnica, si existe
- `decision_sugerida`
- motivo de evaluacion, si aplica
- estado actualizado a `EVALUADO`
- history

#### Regla critica

`swap_service` consume la clasificación técnica producida por `simulator` y solo agrega interpretación operativa; no puede reemplazar ni recalcular la clasificación.

👉 Fuente de verdad de decisión

#### Aclaración sobre clasificación técnica ausente

Si la evaluación técnica no se ejecuta por una restricción operativa:

- la clasificación técnica puede ser nula
- debe persistirse explícitamente como ausente
- no debe inferirse ni reemplazarse por lógica operativa

### 6.3.1 resolver_swap_request

**Firma:** `resolver_swap_request(request, accion, motivo_resolucion=None, actor=None) -> SwapRequest`
**Modulo:** `src.swap_service`

#### Proposito

Resolver operativamente una `SwapRequest` ya evaluada.

La resolucion transforma una evaluacion formal en una decision explicita de workflow, sin aplicar el swap.

#### Responsabilidad

Es la compuerta formal entre:

```text
EVALUADO
-> APROBADO / RECHAZADO / CANCELADO
```

---

### 6.4 aplicar_swap_request

**Firma:** `aplicar_swap_request(request_id, ...) -> RosterVersion`  
**Modulo:** `src.swap_service`

#### Proposito

Aplicar efectivamente un swap previamente APROBADO sobre la versión de roster correspondiente.

#### Debe hacer

- cargar el `SwapRequest`
- validar que el request esté en estado `APROBADO`
- validar que la `roster_version_id` del request siga siendo aplicable según el contrato vigente
- aplicar el intercambio real
- crear una nueva versión de roster
- cancelar requests obsoletos
- marcar el request como `APLICADO`
- persistir cambios
- registrar history

#### No debe hacer

- no reevalúa el swap
- no recalcula score
- no reclasifica
- no remapea decisión
- no reinterpreta reglas técnicas

#### Regla critica

`aplicar_swap_request` ejecuta una `SwapRequest` ya resuelta explicitamente como `APROBADO`; no evalua, no resuelve y no decide nuevamente.

👉 Fuente de verdad de aplicación

### 6.5 Contrato de clasificacion y decision

#### Clasificacion tecnica

- origen: simulator
- propósito: describir el impacto técnico del swap sobre el roster
- valores:
  - BENEFICIOSO
  - ACEPTABLE
  - RECHAZABLE

La clasificación técnica:
- no incorpora ventana operativa
- no incorpora estado del request
- no incorpora decisiones de workflow
- no incorpora motivos operativos

#### Decision operativa

- origen: swap_service
- propósito: determinar qué tratamiento corresponde al request dentro del flujo del sistema
- valores:
  - VIABLE
  - OBSERVAR
  - RECHAZAR

La decisión operativa sugerida:
- puede derivarse normalmente de la clasificación técnica
- puede verse afectada por restricciones operativas
- debe registrarse separadamente de la clasificación técnica
- no equivale a estado del workflow
- no aprueba, rechaza terminalmente, cancela ni aplica por si misma

---

## 7. Responsabilidades

### 7.1 Contrato definitivo de src.engine

#### Responsabilidad exclusiva

- ejecutar reglas configuradas
- producir RuleResult
- agrupar validaciones por controlador
- exponer resultados técnicos reutilizables

#### Prohibiciones

- no decide negocio
- no modifica requests
- no persiste
- no aplica swaps
- no conoce estados de workflow

#### Fuente de verdad

Toda regla hard/soft configurable debe ejecutarse exclusivamente desde engine.

Consecuencia:
Ninguna otra capa debe duplicar lógica de validación basada en reglas.

#### Regla adicional

La semántica de todos los parámetros configurables (ej: min_horas) pertenece exclusivamente al engine.

Ningún otro módulo puede reinterpretar dichos parámetros.

### 7.2 Contrato definitivo de src.simulator

#### Responsabilidad exclusiva

- construir escenario antes/después
- invocar engine
- invocar scoring
- calcular deltas
- clasificar técnicamente el swap

#### Prohibiciones

- no persiste
- no modifica SwapRequest
- no crea versiones
- no valida ventana operativa
- no toma decisiones operativas

#### Fuente de verdad

simulator es la única fuente válida de:
- delta_score
- delta_hard
- delta_soft
- clasificacion

### 7.3 Contrato definitivo de src.swap_service

#### Responsabilidad exclusiva

- crear request
- validar request estructuralmente
- validar precondiciones operativas
- invocar simulator
- mapear clasificación a decisión
- persistir cambios de estado
- resolver request
- aplicar request APROBADO

#### Prohibiciones

- no ejecuta reglas por fuera de engine
- no recalcula score
- no reclasifica swaps
- no reevalúa al aplicar

#### Fuente de verdad

swap_service es la única fuente válida de:
- decision_operativa
- transición de estado
- history del request
- aplicación del request

### 7.4 Contrato de ventana operativa

#### Responsable

- swap_service

#### Naturaleza

La ventana operativa es una validación de negocio, no una validación técnica del roster.

#### Regla

Si falla ventana operativa:
- la decisión operativa debe ser RECHAZAR
- se registra motivo: SWAP_FUERA_DE_VENTANA_OPERATIVA
- la clasificación técnica no debe ser modificada ni falsificada

El sistema puede:
- no ejecutar evaluación técnica
- o conservar la clasificación técnica separadamente si existe

#### Prohibicion

engine y simulator no deben implementar lógica de ventana operativa.

### 7.5 Contrato de dependencia entre modulos

Dependencias permitidas:
- simulator → engine, scoring
- swap_service → simulator, stores, models
- swap_service → engine solo de forma indirecta a través de simulator, salvo validaciones estructurales no basadas en reglas

Dependencias prohibidas:
- engine → swap_service
- simulator → swap_service
- scoring → swap_service
- engine → stores de requests

---

## 8. Flujo

### 8.1 Contrato definitivo de evaluacion y decision

#### 8.1.1 Principio general

El flujo del sistema se divide en cuatro niveles:

1. evaluacion tecnica
2. evaluacion formal con `decision_sugerida`
3. resolucion operativa explicita
4. aplicacion persistente

Cada nivel tiene un responsable y no debe absorber responsabilidades del nivel siguiente.

#### 8.1.2 Evaluacion tecnica

##### Responsable
- engine
- scoring
- simulator

##### Alcance

La evaluación técnica determina:
- violaciones hard y soft
- validez del roster
- score
- impacto comparativo antes/después del swap
- clasificación del swap

##### Regla

La clasificación técnica es responsabilidad exclusiva de simulator.

swap_service no puede:
- recalcular score
- reinterpretar deltas técnicos
- reclasificar un swap

#### 8.1.3 Evaluacion formal y decision_sugerida

##### Responsable
- swap_service

##### Alcance

La evaluacion formal determina:
- `decision_sugerida` VIABLE / OBSERVAR / RECHAZAR
- estado `EVALUADO`
- persistencia e historial de evaluacion

##### Regla

La `decision_sugerida` surge de:
- clasificación técnica recibida desde simulator
- validaciones operativas propias de swap_service

No determina por si misma:
- APROBADO
- RECHAZADO
- CANCELADO
- APLICADO

#### 8.1.3 bis Resolucion operativa explicita

##### Responsable
- swap_service

##### Alcance

La resolucion operativa decide explicitamente si una request `EVALUADO` pasa a:
- APROBADO
- RECHAZADO
- CANCELADO

##### Regla

La resolucion operativa no reevalua, no reclasifica y no aplica.

#### 8.1.4 Aplicacion persistente

##### Responsable
- swap_service
- (futuro) roster_service

##### Alcance

La aplicación real determina:
- intercambio efectivo
- creación de nueva versión
- cancelación de requests obsoletos
- actualización final del request

##### Regla

aplicar_swap_request no reevalúa, no reclasifica y no decide nuevamente.

---

## 9. Notas

### 9.1 Nota de evolucion

Actualmente swap_service realiza la aplicación y versionado.

En la arquitectura objetivo:
- swap_service autoriza la aplicación dentro del flujo del request
- roster_service materializa el cambio sobre el roster versionado

Esta separación permite desacoplar el workflow del request de la evolución del roster.

### 9.2 Aclaracion sobre indices estructurales

Los índices (`idx_a`, `idx_b`) representan una referencia estructural dentro de la versión del roster.

Sin embargo, a nivel de dominio, el objeto real del swap son asignaciones dentro de una versión.

Los índices no deben considerarse identidad conceptual del objeto intercambiado.

### 9.3 Aclaracion sobre mapeo normal

Este mapeo representa la traducción operativa normal de la evaluación técnica.

Excepción:
Las restricciones operativas del flujo pueden forzar una decisión operativa más restrictiva sin alterar la clasificación técnica del swap.

Consecuencia:
No debe interpretarse que clasificación técnica y decisión operativa son equivalentes.

### 9.4 Diferencia entre obsolescencia y cancelación

- obsolescencia → condición del dominio (pierde vigencia)
- CANCELADO → estado del workflow que refleja dicha condición

Todo request obsoleto debe transicionar a estado CANCELADO.

---

## 10. Reglas criticas

### 10.1 Reglas de consistencia

1. simulator clasifica, no decide
2. evaluar_swap_request informa, no resuelve
3. resolver_swap_request decide explicitamente, no aplica
4. aplicar_swap_request ejecuta, no reevalúa
5. engine no decide negocio
6. validez del roster ≠ aprobación automática
7. `VIABLE` no equivale a `APROBADO`
8. `APROBADO` no equivale a `APLICADO`
9. ventana operativa puede rechazar swaps válidos técnicamente
10. flujo favorable:
    PENDIENTE → EVALUADO → APROBADO → APLICADO

### 10.2 Contrato minimo de salida de evaluar_swap

evaluar_swap(...) debe devolver una estructura estable con estos campos mínimos:

- idx_a
- idx_b
- antes:
  - valido
  - score
  - resumen_por_regla
- despues:
  - valido
  - score
  - resumen_por_regla
- delta_score
- delta_hard
- delta_soft
- clasificacion

Regla:
swap_service consume esta salida sin reinterpretar la clasificación.

### 10.3 Contrato de mapeo clasificacion tecnica a decision operativa

Mapeo normal:
- BENEFICIOSO → VIABLE
- ACEPTABLE → OBSERVAR
- RECHAZABLE → RECHAZAR

### 10.4 Regla de separacion de planos

El sistema preserva tres planos distintos:

#### Evaluacion tecnica
Responsable: `simulator`  
Valores: BENEFICIOSO / ACEPTABLE / RECHAZABLE

#### Decision operativa
Responsable: `swap_service`  
Valores: VIABLE / OBSERVAR / RECHAZAR

#### Estado del workflow
Responsable: workflow del `SwapRequest`  
Valores: PENDIENTE / EVALUADO / APROBADO / RECHAZADO / CANCELADO / APLICADO

Estos tres planos nunca deben colapsarse entre sí.

### 10.5 Regla critica de frontera

- `simulator` clasifica.
- `evaluar_swap_request` informa.
- `resolver_swap_request` decide explicitamente.
- `aplicar_swap_request` ejecuta.
- El estado refleja la evolución del request dentro del workflow.

---

## 11. Trazabilidad

### 11.1 Contrato de estados de SwapRequest

Estados:
- PENDIENTE
- EVALUADO
- APROBADO
- RECHAZADO
- CANCELADO
- APLICADO

Transiciones válidas:
- PENDIENTE → EVALUADO
- EVALUADO → APROBADO
- EVALUADO → RECHAZADO
- EVALUADO → CANCELADO
- APROBADO → APLICADO

Estados terminales:
- RECHAZADO
- CANCELADO
- APLICADO

### 11.2 Contratos de consistencia de datos

#### Request valido

Debe referir:
- controladores correctos
- índices válidos
- roster_version_id vigente

#### Aplicacion valida

No se puede aplicar sobre versión distinta a la evaluada

#### Historia

Todo cambio relevante debe registrarse en history.

El `actor` registrado en history identifica quien ejecuto o disparo una accion, pero no define por si mismo permisos formales ni autorizacion operativa.

### 11.3 Contratos de frontera de simulator

#### 11.3.1 Frontera publica objetivo

simulator expone como frontera pública objetivo únicamente capacidades técnicas de simulación y evaluación comparativa.

Incluye:
- simulación de swaps
- evaluación antes/después
- cálculo de deltas
- clasificación técnica
- exploración técnica de alternativas

No incluye:
- workflow del request
- creación, resolución o aplicación de requests
- presentación textual
- lógica operativa

La exposición de funciones operativas desde simulator se considera transitoria y no contractual a nivel de arquitectura objetivo.

#### 11.3.2 Contrato semantico del swap

El swap del dominio se define como una operación sobre dos asignaciones de una misma versión, consistente en intercambiar el turno o actividad asignado entre ellas.

Consecuencia:
- las asignaciones siguen siendo el objeto del intercambio a nivel de dominio
- el cambio efectivo recae sobre el turno o actividad
- la identidad base de las asignaciones no se reemplaza

#### 11.3.3 Contrato de clasificacion tecnica

La clasificación permanece en simulator y es exclusivamente técnica.

clasificar_swap(...) solo puede derivarse de:
- validez técnica
- scoring
- deltas hard/soft
- impacto técnico por controlador

No puede derivarse de:
- ventana operativa
- estado del request
- criterios de aprobación
- motivos operativos

#### 11.3.4 Contrato de presentacion

La generación de texto explicativo o recomendación textual no forma parte del contrato objetivo de simulator.

Ese tipo de salida pertenece a una capa de presentación, reporting o interfaz.

#### 11.3.5 Contrato de comparacion tecnica neutral

Los cálculos comparativos internos de simulator deben apoyarse en estructuras técnicas neutrales de comparación.

El uso de `RosterVersion` ficticios dentro de simulación no forma parte del contrato objetivo y debe considerarse una solución transitoria.

### 11.4 Contrato consolidado entre simulator y swap_service

#### Proposito

Definir la frontera exacta entre evaluación técnica del swap y tratamiento operativo del request.

Esta sección operacionaliza las decisiones arquitectónicas de separación entre evaluación técnica, decisión operativa y workflow definidas en [Ref: decisiones.md #17]

#### 11.4.1 Responsabilidad de simulator

simulator es responsable exclusivamente de la evaluación técnica de escenarios hipotéticos de swap.

Debe producir:
- comparación técnica entre estado original y estado resultante
- clasificación técnica del swap
- deltas técnicos relevantes
- información estructurada de impacto técnico

No debe producir:
- decisión operativa
- estados de workflow
- resolución del request
- aplicación del swap
- validaciones operativas del flujo

#### 11.4.2 Salida conceptual de simulator

La salida de simulator debe representar únicamente resultados técnicos.

Debe poder incluir, al menos:
- clasificación técnica
- validez técnica antes y después
- score antes y después
- deltas hard/soft
- impacto técnico por controlador
- referencias estructurales del swap evaluado

No debe incluir:
- VIABLE / OBSERVAR / RECHAZAR
- APROBADO / RECHAZADO / CANCELADO / APLICADO
- motivos operativos
- decisiones del workflow

#### 11.4.3 Taxonomia tecnica de simulator

La clasificación técnica del swap usa exclusivamente estos valores:
- BENEFICIOSO
- ACEPTABLE
- RECHAZABLE

Esta clasificación responde a la pregunta:
¿Qué efecto técnico produce este swap sobre el roster?

#### 11.4.4 Responsabilidad de swap_service

swap_service es responsable del tratamiento operativo del `SwapRequest`.

Debe:
- validar precondiciones estructurales y operativas del request
- consumir la evaluación técnica producida por simulator
- producir una decisión operativa
- actualizar el estado del workflow según corresponda
- persistir el request y su history

No debe:
- recalcular clasificación técnica
- reinterpretar deltas técnicos como nueva clasificación
- ejecutar evaluación técnica por lógica propia fuera del contrato definido

#### 11.4.5 Taxonomia operativa de swap_service

La decisión operativa usa exclusivamente estos valores:
- VIABLE
- OBSERVAR
- RECHAZAR

Esta decisión responde a la pregunta:
¿Qué tratamiento operativo corresponde darle a este request?

La decisión operativa:
- puede derivarse normalmente de la clasificación técnica
- puede endurecerse por restricciones operativas
- no modifica la naturaleza de la clasificación técnica

#### 11.4.6 Mapeo normal entre clasificacion tecnica y decision operativa

Mapeo normal:
- BENEFICIOSO → VIABLE
- ACEPTABLE → OBSERVAR
- RECHAZABLE → RECHAZAR

Aclaración:
Este mapeo expresa la traducción operativa normal de la evaluación técnica.

Las restricciones operativas pueden forzar una decisión más restrictiva sin alterar la clasificación técnica.

#### 11.4.7 Estado del workflow

El estado del `SwapRequest` pertenece al plano del workflow y no al plano técnico ni al plano de decisión operativa.

Estados:
- PENDIENTE
- EVALUADO
- APROBADO
- RECHAZADO
- CANCELADO
- APLICADO

El estado responde a la pregunta:
¿En qué punto del ciclo de vida se encuentra el request?

Responsable:
- workflow del `SwapRequest`, materializado por swap_service

Regla:
El estado APROBADO representa una resolucion operativa favorable y explicita dentro del workflow.

No representa aplicacion del swap.

## 12. Contrato de frontera publica de simulator

### Proposito
Definir la superficie publica valida de `simulator` y evitar mezcla con responsabilidades operativas.



### Frontera valida de simulator

`simulator` expone unicamente capacidades tecnicas.

Puede exponer:
- evaluacion tecnica de swaps
- comparacion de escenarios
- clasificacion tecnica
- calculo de impacto
- exploracion de alternativas



### Prohibicion de exposicion operativa

`simulator` no debe exponer funciones relacionadas con:
- creacion de SwapRequest
- evaluacion de SwapRequest
- resolucion de SwapRequest
- aplicacion de SwapRequest
- gestion de estado
- workflow operativo



### Regla de delegacion

La existencia de delegacion interna hacia `swap_service` no habilita la exposicion publica de funciones operativas desde `simulator`.



### Puerta operativa unica

Todas las operaciones del ciclo de vida del request deben exponerse exclusivamente desde `swap_service`.



### Regla de consistencia

La superficie publica del modulo debe reflejar exclusivamente sus responsabilidades.

En consecuencia:
- `simulator` publica evaluacion tecnica
- `swap_service` publica operacion y workflow

Ambas superficies no deben solaparse.

---

## 13. Contrato de priorizacion historica de swaps

### Proposito

Aplicar un criterio de equidad historica sobre un conjunto de swaps ya evaluados tecnicamente, ajustando su orden relativo sin modificar su significado tecnico.


### Ubicacion

Este modulo se ubica:

- despues de `simulator`
- antes del consumo del ranking por UI o flujo operativo

No forma parte de:
- engine
- scoring
- simulator
- swap_service


### Entrada

- lista de evaluaciones tecnicas de swaps
- informacion historica por controlador dentro de la ventana definida


### Salida

- misma lista de evaluaciones
- orden ajustado por equidad historica

Puede agregar:
- score_equidad
- metadata explicativa

No puede modificar:
- clasificacion
- impacto
- score tecnico
- validez


### Garantias

- no altera evaluacion tecnica
- no introduce decision operativa
- no modifica workflow
- comportamiento deterministico


### Regla de actuacion

Puede:
- reordenar swaps validos o aceptables
- desempatar swaps tecnicamente similares

No puede:
- promover swaps rechazables
- redefinir clasificacion tecnica
- eliminar swaps por criterio historico

### Regla de peso

La equidad historica es una señal soft subordinada a la calidad tecnica del swap.

### Regla critica

La equidad historica modifica prioridad, no significado.

---

## 14. Contrato de equidad historica avanzada

### Proposito

Definir el modelo contractual de equidad historica sin alterar evaluacion tecnica, clasificacion ni decision operativa.


### Fuente de datos valida

La equidad historica solo puede construirse a partir de eventos derivados de swaps con estado `APLICADO`.

No son fuente valida:

- evaluaciones tecnicas
- decisiones operativas favorables
- requests rechazados
- requests cancelados
- requests aprobados no aplicados
- sugerencias del sistema


### Modelo historico

La informacion historica se representa mediante eventos por controlador, con capacidad minima para expresar:

- controlador
- timestamp
- roster_version_id
- request_id
- tipo de impacto
- peso o magnitud


### Ventana temporal

La lectura historica se realiza sobre una ventana temporal configurable.

La ventana:
- no pertenece a engine
- no pertenece a scoring tecnico
- no modifica simulator
- se aplica en la capa de priorizacion historica


### Decaimiento

El decaimiento de los eventos historicos se calcula en lectura.

No debe persistirse como valor fijo en el store.


### Señal derivada

La condicion de controlador castigado se deriva a partir del historial reciente y no se persiste como estado propio del sistema.


### Prohibicion

La equidad historica no puede reaccionar a:

- propuestas no materializadas
- rechazos sociales
- bloqueos grupales
- oportunidades no concretadas

La equidad historica solo observa efectos operativos reales.

---


## 15. Contrato de flujo de oferta con equidad historica

### Regla

La priorizacion historica puede modificar el orden del listado de candidatos elegibles ofrecido por el sistema.

No puede modificar ni recalcularse a partir de:

- la eleccion final del usuario dentro del listado
- rechazos de otros usuarios
- solicitudes no concretadas
- regulacion social o grupal

### Trazabilidad

Las elecciones humanas y los rechazos pueden registrarse para auditoria, pero no constituyen insumo valido para la señal de equidad historica.

### Fuente historica valida

Solo los swaps con estado `APLICADO` generan eventos historicos validos para calculo de equidad.


---

## 16. Contrato de candidate_generation

### 16.1 Proposito

Definir la responsabilidad de generación acotada de swaps candidatos antes de la simulación técnica.

La capa `candidate_generation` existe para reducir el universo de búsqueda y entregar a `simulator` solo candidatos plausibles para una necesidad concreta.

---

### 16.2 Ubicacion en el flujo

El flujo correcto del sistema queda:

- request o asignacion origen
- candidate_generation
- simulator
- ranking tecnico
- priorizacion historica (si aplica)
- oferta al usuario

---

### 16.3 Responsabilidad exclusiva

`candidate_generation` es responsable de:

- tomar una asignacion origen o necesidad concreta del usuario
- construir un universo elegible acotado
- aplicar filtros previos baratos
- devolver candidatos estructuralmente plausibles para simulacion

---

### 16.4 Entrada

La entrada de `candidate_generation` debe poder incluir:

- asignacion origen
- roster actual
- criterios de búsqueda del usuario
- restricciones estructurales baratas
- configuración operativa mínima si corresponde

---

### 16.5 Salida

La salida de `candidate_generation` debe ser una colección acotada de candidatos para simulación.

La salida puede expresarse como:

- pares de índices
- referencias estructurales equivalentes

Siempre que no redefina la identidad conceptual del swap.

---

### 16.6 Filtros permitidos

`candidate_generation` puede aplicar únicamente filtros baratos y previos a la simulación.

Ejemplos:

- excluir misma asignacion
- excluir mismo controlador si no corresponde
- restringir por fecha o rango de fechas
- restringir por tipo de turno o compatibilidad declarada
- excluir candidatos estructuralmente incompatibles
- limitar el universo por criterios operativos simples y baratos

---

### 16.7 Prohibiciones

`candidate_generation` no debe:

- ejecutar evaluacion tecnica completa
- usar engine para clasificar candidatos
- calcular score tecnico final
- clasificar swaps
- decidir operativamente
- persistir
- reemplazar simulator
- reemplazar swap_service

---

### 16.8 Regla de frontera

La capa `candidate_generation` reduce universo de búsqueda.

La capa `simulator` evalúa técnicamente.

La capa `swap_service` decide operativamente.

Estas responsabilidades no deben mezclarse.

---

### 16.9 Regla critica

La generación de candidatos modifica cobertura, no significado.

Reducir el universo elegible no implica evaluar, clasificar ni decidir.

---

## 17. Contrato de roster_index

### 17.1 Proposito

Definir una estructura derivada del roster vigente que permita acceso rápido a subconjuntos operativos relevantes.

`roster_index` existe para reducir el costo de búsqueda dentro del roster y permitir generación eficiente de candidatos.

---

### 17.2 Naturaleza

`roster_index` es una estructura derivada y reconstruible.

No representa una nueva fuente de verdad.

La fuente de verdad sigue siendo:

- RosterVersion vigente

---

### 17.3 Responsabilidad exclusiva

`roster_index` es responsable de:

- indexar asignaciones del roster vigente
- permitir acceso rápido por criterios estructurales
- reducir exploración lineal completa
- asistir a candidate_generation

---

### 17.4 Fuente de datos

`roster_index` se construye exclusivamente desde:

- roster vigente
- asignaciones persistidas

No puede incorporar información externa.

---

### 17.5 Relacion con versionado

Cada versión vigente del roster debe tener un índice consistente asociado.

Cuando cambia la versión:

- el índice anterior deja de ser vigente
- debe reconstruirse un nuevo índice

---

### 17.6 Consultas permitidas

El índice puede responder consultas como:

- asignaciones por fecha
- asignaciones por turno
- asignaciones por controlador
- asignaciones por fecha y turno
- subconjuntos por rango temporal
- agrupaciones operativas simples

---

### 17.7 Restricciones

`roster_index` no debe:

- evaluar reglas
- clasificar swaps
- calcular score
- decidir workflow
- persistir requests
- reemplazar simulator
- reemplazar candidate_generation

---

### 17.8 Regla critica

`roster_index` acelera acceso.

No redefine significado.

No modifica semántica del roster.

---

### 17.9 Regla de consistencia

El índice debe representar exactamente la misma realidad que la versión vigente del roster.

No puede existir divergencia entre:

- roster vigente
- índice vigente

---

### 17.10 Estructura conceptual recomendada

`roster_index` puede organizarse mediante múltiples vistas estructurales derivadas.

Se recomienda incluir:

- by_date
- by_date_turno
- by_controller
- future_window

Estas estructuras permiten navegación rápida sin recorrer el roster completo.

---

#### by_date

Agrupa asignaciones por fecha.

Permite:

- consultas operativas por día
- subconjuntos diarios

---

#### by_date_turno

Agrupa asignaciones por fecha y turno.

Permite:

- obtener universo compatible por día y turno
- acelerar generación de candidatos

---

#### by_controller

Agrupa asignaciones por controlador.

Permite:

- navegación histórica individual
- filtros rápidos por persona

---

#### future_window

Agrupa asignaciones futuras desde una fecha dada.

Permite:

- reducir universo temporal
- evitar exploración retrospectiva
- escalar búsqueda multi-fecha

---

#### Regla

Estas estructuras son derivadas.

No reemplazan la fuente de verdad del roster.

---

### 17.11 Uso de roster_index por candidate_generation

`candidate_generation` debe utilizar `roster_index` como fuente estructural principal para construir el universo elegible de candidatos.

No debe recorrer el roster completo como estrategia base.

---

#### Caso de mismo dia

Si la necesidad del usuario se limita al mismo dia, `candidate_generation` debe consultar prioritariamente:

- by_date
- by_date_turno

Esto permite construir rapidamente el subconjunto de candidatos del dia y turno buscado.

---

#### Caso de otro dia

Si la necesidad del usuario se extiende a dias futuros, `candidate_generation` debe consultar prioritariamente:

- future_window

Esto permite reducir el universo a asignaciones futuras relevantes sin explorar retrospectivamente todo el roster.

---

#### Regla de composicion

`candidate_generation` puede combinar subconjuntos obtenidos desde `roster_index` con filtros baratos adicionales, pero no debe ejecutar evaluacion tecnica completa en esta etapa.

---

#### Regla critica

`roster_index` reduce acceso.
`candidate_generation` reduce universo.
`simulator` evalua tecnicamente.

Estas funciones no deben mezclarse.

---

# Contrato 18 - Fachada para crear request desde oferta y evaluar formalmente

## TOC

- [18.1 Proposito](#181-proposito)
- [18.2 Contexto](#182-contexto)
- [18.3 Flujo contractual](#183-flujo-contractual)
- [18.4 Responsabilidades permitidas](#184-responsabilidades-permitidas)
- [18.5 Responsabilidades prohibidas](#185-responsabilidades-prohibidas)
- [18.6 Estado inicial obligatorio](#186-estado-inicial-obligatorio)
- [18.7 Evaluacion formal](#187-evaluacion-formal)
- [18.8 Separacion entre evidencia observada y evaluacion formal](#188-separacion-entre-evidencia-observada-y-evaluacion-formal)
- [18.9 Resultado esperado](#189-resultado-esperado)
- [18.10 Divergencia entre oferta y evaluacion formal](#1810-divergencia-entre-oferta-y-evaluacion-formal)
- [18.11 Beneficio esperado](#1811-beneficio-esperado)
- [18.12 Relacion con otros contratos](#1812-relacion-con-otros-contratos)
- [18.13 Regla corta](#1813-regla-corta)

---

## 18.1 Proposito

Definir el contrato arquitectonico de la fachada de alto nivel encargada de crear una `SwapRequest` formal desde una oferta evaluada seleccionada y ejecutar inmediatamente su evaluacion formal mediante `swap_service`.

La fachada propuesta se denomina conceptualmente:

```text
crear_request_desde_oferta_y_evaluar_formalmente
```

---

## 18.2 Contexto

El sistema ya permite:

```text
OfertaEvaluada
-> seleccion de oferta
-> SwapRequest formal PENDIENTE
-> offer_origin como evidencia observada
-> persistencia explicita
```

La evaluacion tecnica observada durante la generacion de la oferta queda preservada en `offer_origin`, pero no constituye evaluacion formal del request.

La evaluacion formal sigue perteneciendo a:

```text
swap_service.evaluar_swap_request
```

---

## 18.3 Flujo contractual

La fachada debe coordinar el siguiente flujo:

```text
OfertaEvaluada seleccionada
-> crear SwapRequest formal PENDIENTE
-> preservar offer_origin
-> persistir request creada desde oferta
-> evaluar formalmente mediante swap_service.evaluar_swap_request
-> persistir resultado formal evaluado
-> devolver SwapRequest EVALUADO o resultado equivalente
```

---

## 18.4 Responsabilidades permitidas

La fachada puede:

1. Recibir una oferta evaluada seleccionada.
2. Delegar la creacion formal de la request desde oferta.
3. Garantizar que la request nace en estado `PENDIENTE`.
4. Preservar `offer_origin` como evidencia observada.
5. Persistir explicitamente la request creada desde oferta, si el flujo actual lo requiere.
6. Invocar `swap_service.evaluar_swap_request`.
7. Persistir el resultado formal de la evaluacion.
8. Devolver una `SwapRequest` en estado `EVALUADO` o un resultado estructurado equivalente.
9. Registrar trazabilidad del paso oferta -> request -> evaluacion formal.
10. Comparar, si corresponde, la evidencia observada de `offer_origin` contra la evaluacion formal posterior.

---

## 18.5 Responsabilidades prohibidas

La fachada no puede:

- llamar directamente a `engine`;
- llamar directamente a `scoring`;
- llamar directamente a `simulator`;
- clasificar tecnicamente por cuenta propia;
- decidir `VIABLE`, `OBSERVAR` o `RECHAZAR` por fuera de `swap_service`;
- aprobar requests;
- rechazar requests como resolucion operativa;
- cancelar requests;
- aplicar swaps;
- modificar roster;
- reemplazar la evaluacion formal usando datos de `offer_origin`;
- crear estados propios de oferta;
- crear un workflow paralelo de ofertas.

---

## 18.6 Estado inicial obligatorio

Toda `SwapRequest` creada desde una oferta debe nacer primero en estado:

```text
PENDIENTE
```

Aunque la fachada evalue inmediatamente despues, la transicion valida es:

```text
PENDIENTE -> EVALUADO
```

No se permite que una request creada desde oferta nazca directamente como:

```text
EVALUADO
```

---

## 18.7 Evaluacion formal

La evaluacion formal debe realizarse exclusivamente mediante:

```text
swap_service.evaluar_swap_request
```

La fachada puede invocar esa funcion, pero no puede reemplazarla ni simular su resultado.

---

## 18.8 Separacion entre evidencia observada y evaluacion formal

La informacion contenida en `offer_origin` representa evidencia tecnica observada durante la generacion de la oferta.

Por lo tanto:

```text
clasificacion_observada != clasificacion_formal
delta_score_observado != delta_score_formal
delta_hard_observado != delta_hard_formal
delta_soft_observado != delta_soft_formal
```

Estos valores pueden coincidir, pero no son semanticamente equivalentes.

---

## 18.9 Resultado esperado

El resultado exitoso de la fachada es una request formal evaluada, pero no resuelta:

```text
estado = EVALUADO
decision_sugerida = definida por swap_service
```

El resultado de esta fachada no debe ser:

```text
APROBADO
RECHAZADO
CANCELADO
APLICADO
```

---

## 18.10 Divergencia entre oferta y evaluacion formal

Si la clasificacion formal difiere de la clasificacion observada en `offer_origin`, la divergencia debe conservarse como informacion de trazabilidad o advertencia operativa.

Ejemplo:

```text
offer_origin.clasificacion_observada = BENEFICIOSO
evaluacion_formal.clasificacion = ACEPTABLE
```

Esto no implica error automatico. Indica que la evaluacion formal vigente no coincide con la evidencia observada al momento de generar la oferta.

---

## 18.11 Beneficio esperado

El beneficio principal de esta fachada es operativo, no de performance.

La fachada mejora:

- consistencia del flujo;
- reduccion de friccion para futura UI/API;
- menor riesgo de requests creadas desde oferta sin evaluacion formal;
- trazabilidad uniforme;
- comparacion clara entre evidencia observada y evaluacion formal.

No se espera una mejora significativa en benchmarks de exploracion, porque la reduccion fuerte de costo ocurre previamente en:

```text
candidate_generation
-> technical_prefilter
-> candidate_selection
-> exploration_flow
-> simulator
```

---

## 18.12 Relacion con otros contratos

Este contrato no modifica:

- responsabilidad de `engine`;
- responsabilidad de `scoring`;
- responsabilidad de `simulator`;
- responsabilidad de `candidate_selection`;
- responsabilidad de `swap_service.aplicar_swap_request`;
- taxonomia de clasificacion tecnica;
- taxonomia de decision operativa;
- estados formales de `SwapRequest`.

---

## 18.13 Regla corta

La fachada puede crear y evaluar formalmente una request desde oferta, pero no puede resolverla ni aplicarla.

---

# Contrato 19 - Resolucion operativa posterior de SwapRequest evaluada

## TOC

- [19.1 Proposito](#191-proposito)
- [19.2 Contexto](#192-contexto)
- [19.3 Flujo contractual](#193-flujo-contractual)
- [19.4 Estado de entrada](#194-estado-de-entrada)
- [19.5 Estados de salida](#195-estados-de-salida)
- [19.6 Responsabilidades permitidas](#196-responsabilidades-permitidas)
- [19.7 Responsabilidades prohibidas](#197-responsabilidades-prohibidas)
- [19.8 Tratamiento de decision_sugerida](#198-tratamiento-de-decisionsugerida)
- [19.9 Tratamiento de OBSERVAR](#199-tratamiento-de-observar)
- [19.10 Tratamiento de offer_origin](#1910-tratamiento-de-offerorigin)
- [19.11 Relacion con aplicacion](#1911-relacion-con-aplicacion)
- [19.12 Modelo V1 sin workflow bilateral](#1912-modelo-v1-sin-workflow-bilateral)
- [19.13 Regla corta](#1913-regla-corta)

---

## 19.1 Proposito

Definir el contrato arquitectonico de la resolucion operativa posterior de una `SwapRequest` que ya fue evaluada formalmente.

La resolucion operativa es la etapa que decide si una request evaluada pasa a:

```text
APROBADO
RECHAZADO
CANCELADO
```

---

## 19.2 Contexto

Una request creada desde oferta o creada manualmente puede pasar por evaluacion formal mediante:

```text
swap_service.evaluar_swap_request
```

Luego de esa evaluacion, la request queda en estado:

```text
EVALUADO
```

La evaluacion formal puede producir una `decision_sugerida`, pero esa decision no equivale a resolucion terminal.

---

## 19.3 Flujo contractual

El flujo contractual de resolucion es:

```text
SwapRequest EVALUADO
-> accion explicita de resolucion
-> APROBADO / RECHAZADO / CANCELADO
```

La aplicacion queda fuera de este contrato:

```text
APROBADO
-> aplicar_swap_request
-> APLICADO
```

---

## 19.4 Estado de entrada

La resolucion operativa solo puede operar sobre una request en estado:

```text
EVALUADO
```

No debe resolver requests en estados:

```text
PENDIENTE
APROBADO
RECHAZADO
CANCELADO
APLICADO
```

---

## 19.5 Estados de salida

La resolucion operativa puede llevar la request a uno de estos estados:

```text
APROBADO
RECHAZADO
CANCELADO
```

No puede llevar directamente a:

```text
APLICADO
```

---

## 19.6 Responsabilidades permitidas

La resolucion operativa puede:

1. Recibir una `SwapRequest` en estado `EVALUADO`.
2. Considerar `decision_sugerida`.
3. Considerar clasificacion tecnica formal.
4. Considerar advertencias o divergencias.
5. Registrar actor de resolucion.
6. Registrar fecha/hora de resolucion.
7. Registrar accion de resolucion.
8. Registrar motivo de resolucion.
9. Registrar history formal.
10. Cambiar el estado a `APROBADO`, `RECHAZADO` o `CANCELADO`.

---

## 19.7 Responsabilidades prohibidas

La resolucion operativa no puede:

- reevaluar la request;
- llamar directamente a `engine`;
- llamar directamente a `scoring`;
- llamar directamente a `simulator`;
- modificar `offer_origin`;
- modificar la clasificacion tecnica formal;
- modificar la evaluacion formal;
- aplicar el swap;
- modificar roster;
- crear workflow paralelo;
- convertir automaticamente una decision sugerida en estado terminal.

---

## 19.8 Tratamiento de decision_sugerida

La `decision_sugerida` orienta la resolucion, pero no la reemplaza.

Por lo tanto:

```text
VIABLE != APROBADO
OBSERVAR != APROBADO
RECHAZAR != RECHAZADO
```

La resolucion debe ser una accion explicita.

---

## 19.9 Tratamiento de OBSERVAR

Si la `decision_sugerida` es:

```text
OBSERVAR
```

la resolucion debe requerir especial trazabilidad.

En V1, esto significa que la accion de resolver debe conservar motivo explicito.

En una version futura, `OBSERVAR` podria requerir rol supervisor o validacion adicional, pero eso no forma parte de este contrato.

---

## 19.10 Tratamiento de offer_origin

Si la request proviene de una oferta, el bloque `offer_origin` debe permanecer como evidencia observada.

La resolucion no debe pisar ni reinterpretar:

```text
clasificacion_observada
delta_score_observado
delta_hard_observado
delta_soft_observado
```

La resolucion puede consultar esa informacion como trazabilidad, pero no debe convertirla en decision terminal.

---

## 19.11 Relacion con aplicacion

La resolucion no aplica el swap.

La aplicacion sigue siendo una operacion posterior, separada y formal:

```text
swap_service.aplicar_swap_request
```

La unica transicion valida hacia aplicacion es:

```text
APROBADO
-> APLICADO
```

segun el contrato vigente de aplicacion.

---

## 19.12 Modelo V1 sin workflow bilateral

Para V1 no se incorpora workflow bilateral formal.

No se agregan estados como:

```text
PROPUESTO
ACEPTADO_POR_CONTRAPARTE
RECHAZADO_POR_CONTRAPARTE
PENDIENTE_SUPERVISOR
```

La contraparte no se modela todavia como estado propio, porque el sistema ya protege restricciones hard y consistencia tecnica mediante evaluacion formal.

La aceptacion bilateral, contrapropuestas y bloqueos multiusuario quedan reservados para una etapa posterior.

---

## 19.13 Regla corta

Una request evaluada puede ser resuelta explicitamente, pero no puede resolverse automaticamente ni aplicarse dentro de la misma etapa.

---

# Contrato 20 - Aplicacion de SwapRequest aprobada

## TOC

- [20.1 Proposito](#201-proposito)
- [20.2 Contexto](#202-contexto)
- [20.3 Flujo contractual](#203-flujo-contractual)
- [20.4 Estado de entrada](#204-estado-de-entrada)
- [20.5 Estados de entrada prohibidos](#205-estados-de-entrada-prohibidos)
- [20.6 Estado de salida](#206-estado-de-salida)
- [20.7 Responsabilidades permitidas](#207-responsabilidades-permitidas)
- [20.8 Responsabilidades prohibidas](#208-responsabilidades-prohibidas)
- [20.9 Versionado de roster](#209-versionado-de-roster)
- [20.10 Cancelacion de obsoletos](#2010-cancelacion-de-obsoletos)
- [20.11 Relacion con oferta evaluada](#2011-relacion-con-oferta-evaluada)
- [20.12 Relacion con evaluacion y resolucion](#2012-relacion-con-evaluacion-y-resolucion)
- [20.13 Regla corta](#2013-regla-corta)

---

## 20.1 Proposito

Definir el contrato arquitectonico de aplicacion de una `SwapRequest` aprobada.

La aplicacion es la etapa que ejecuta el swap sobre el roster y crea una nueva version de roster.

---

## 20.2 Contexto

El workflow formal de una `SwapRequest` separa:

```text
evaluacion formal
-> resolucion operativa
-> aplicacion
```

Una request solo puede aplicarse luego de haber sido resuelta explicitamente como:

```text
APROBADO
```

---

## 20.3 Flujo contractual

El flujo contractual de aplicacion es:

```text
SwapRequest APROBADO
-> aplicar_swap_request
-> ejecutar intercambio sobre roster
-> crear nueva version de roster
-> marcar request APLICADO
```

---

## 20.4 Estado de entrada

La aplicacion solo puede operar sobre una request en estado:

```text
APROBADO
```

---

## 20.5 Estados de entrada prohibidos

La aplicacion no puede operar sobre requests en estado:

```text
PENDIENTE
EVALUADO
RECHAZADO
CANCELADO
APLICADO
```

---

## 20.6 Estado de salida

El estado esperado luego de una aplicacion exitosa es:

```text
APLICADO
```

---

## 20.7 Responsabilidades permitidas

`aplicar_swap_request` puede:

1. Recibir una `SwapRequest` en estado `APROBADO`.
2. Validar que la request pertenece al roster vigente.
3. Ejecutar el intercambio de asignaciones.
4. Crear una nueva version de roster.
5. Marcar la request como `APLICADO`.
6. Registrar history formal de aplicacion.
7. Persistir el estado `APLICADO`.
8. Cancelar requests obsoletos si corresponde al contrato vigente.
9. Registrar history de cancelacion por obsolescencia en requests afectadas.
10. Preservar trazabilidad entre version anterior y nueva version.

---

## 20.8 Responsabilidades prohibidas

`aplicar_swap_request` no puede:

- reevaluar la request;
- resolver la request;
- aprobar;
- rechazar;
- cancelar por decision operativa humana;
- modificar `decision_sugerida`;
- modificar `offer_origin`;
- modificar clasificacion tecnica formal;
- reemplazar evaluacion formal;
- llamar directamente a `engine`;
- llamar directamente a `scoring`;
- llamar directamente a `simulator`;
- crear workflow paralelo;
- aplicar una request dos veces;
- aplicar una request que no este `APROBADO`.

---

## 20.9 Versionado de roster

La aplicacion debe crear una nueva version de roster.

La nueva version representa el roster luego de ejecutar el intercambio aprobado.

La version anterior deja de ser vigente.

La request aplicada debe quedar asociada a la trazabilidad de la version sobre la cual fue evaluada y a la version resultante cuando el modelo lo permita.

---

## 20.10 Cancelacion de obsoletos

Cuando una aplicacion crea una nueva version de roster, otras requests asociadas a la version anterior pueden quedar obsoletas.

La cancelacion de obsoletos debe respetar:

- no cancelar requests ya `APLICADO`;
- no alterar historicos terminales salvo contrato explicito;
- distinguir cancelacion por obsolescencia de cancelacion operativa;
- no tratar obsolescencia como rechazo operativo;
- registrar motivo claro;
- registrar history;
- no reevaluar las requests canceladas;
- no aplicar requests canceladas.

Estados candidatos a cancelacion por obsolescencia:

```text
PENDIENTE
EVALUADO
APROBADO
```

Estados no candidatos a modificacion por obsolescencia:

```text
RECHAZADO
CANCELADO
APLICADO
```

---

## 20.11 Relacion con oferta evaluada

Si la request aplicada proviene de una oferta, `offer_origin` debe permanecer inmutable.

La aplicacion no debe modificar:

```text
clasificacion_observada
delta_score_observado
delta_hard_observado
delta_soft_observado
selection_metadata
```

La oferta no se aplica. Se aplica la `SwapRequest` formal aprobada.

---

## 20.12 Relacion con evaluacion y resolucion

La aplicacion no reemplaza evaluacion formal ni resolucion operativa.

Por lo tanto:

```text
aplicar != evaluar
aplicar != resolver
aplicar != aprobar
```

La aplicacion presupone que la request ya fue evaluada y aprobada por el flujo correspondiente.

---

## 20.13 Regla corta

Solo se aplica una `SwapRequest` aprobada; aplicar ejecuta sobre roster y no decide.

---

# Contrato 21 - Auditoria estructurada minima del workflow formal

## TOC

- [21.1 Proposito](#211-proposito)
- [21.2 Contexto](#212-contexto)
- [21.3 Principio contractual](#213-principio-contractual)
- [21.4 Eventos auditables minimos](#214-eventos-auditables-minimos)
- [21.5 Campos base de evento auditable](#215-campos-base-de-evento-auditable)
- [21.6 Responsabilidades permitidas](#216-responsabilidades-permitidas)
- [21.7 Responsabilidades prohibidas](#217-responsabilidades-prohibidas)
- [21.8 Actor registrado no equivale a permiso](#218-actor-registrado-no-equivale-a-permiso)
- [21.9 Motivos diferenciados](#219-motivos-diferenciados)
- [21.10 Relacion con history](#2110-relacion-con-history)
- [21.11 Relacion con workflow formal](#2111-relacion-con-workflow-formal)
- [21.12 Regla corta](#2112-regla-corta)

---

## 21.1 Proposito

Definir el contrato arquitectonico de auditoria estructurada minima para el workflow formal de `SwapRequest`.

La auditoria estructurada registra hechos relevantes del workflow de manera consistente y trazable.

---

## 21.2 Contexto

El workflow formal vigente es:

```text
PENDIENTE
-> evaluar_swap_request
-> EVALUADO
-> resolver_swap_request
-> APROBADO / RECHAZADO / CANCELADO
-> aplicar_swap_request
-> APLICADO
```

Cada etapa produce hechos relevantes que deben poder auditarse sin modificar la semantica del workflow.

---

## 21.3 Principio contractual

La auditoria estructurada no gobierna el workflow.

La auditoria estructurada registra hechos ocurridos dentro del workflow.

```text
El workflow cambia estados.
La auditoria registra hechos del workflow.
```

---

## 21.4 Eventos auditables minimos

Los eventos auditables minimos son:

```text
REQUEST_CREADA
REQUEST_CREADA_DESDE_OFERTA
REQUEST_EVALUADA
REQUEST_RESUELTA
REQUEST_APLICADA
REQUEST_CANCELADA_POR_OBSOLESCENCIA
```

El evento `REQUEST_RESUELTA` debe poder representar el resultado:

```text
APROBADO
RECHAZADO
CANCELADO
```

El evento `REQUEST_CANCELADA_POR_OBSOLESCENCIA` debe mantenerse separado para no confundir obsolescencia tecnica/versionado con resolucion operativa.

---

## 21.5 Campos base de evento auditable

Un evento auditable puede contener:

```text
event_type
timestamp
actor
actor_type
request_id
estado_anterior
estado_nuevo
motivo
source
roster_version_id
roster_hash
metadata
```

La obligatoriedad de cada campo puede variar segun el tipo de evento.

La implementacion futura debe definir validaciones especificas por evento.

---

## 21.6 Responsabilidades permitidas

La auditoria estructurada puede:

1. Registrar eventos del workflow.
2. Registrar actor informado.
3. Registrar tipo de actor informado.
4. Registrar timestamp.
5. Registrar estado anterior y estado nuevo.
6. Registrar motivo asociado.
7. Registrar version/hash de roster si corresponde.
8. Registrar metadata auxiliar.
9. Diferenciar eventos humanos de eventos automaticos del sistema.
10. Diferenciar cancelacion operativa de cancelacion por obsolescencia.

---

## 21.7 Responsabilidades prohibidas

La auditoria estructurada no puede:

- cambiar estados;
- decidir;
- aprobar;
- rechazar;
- cancelar;
- aplicar;
- reevaluar;
- modificar `decision_sugerida`;
- modificar `offer_origin`;
- modificar clasificacion tecnica;
- definir permisos;
- validar autorizacion;
- crear workflow paralelo;
- introducir nuevos estados;
- reemplazar `swap_service`.

---

## 21.8 Actor registrado no equivale a permiso

El campo `actor` representa quien o que fue registrado como ejecutor u origen del evento.

No representa por si mismo autorizacion formal.

La auditoria puede registrar:

```text
actor = usuario_123
actor_type = USER
```

o:

```text
actor = sistema
actor_type = SYSTEM
```

Pero no debe inferir permisos.

La autorizacion formal, si se implementa en el futuro, debe definirse en un contrato separado.

---

## 21.9 Motivos diferenciados

Los motivos deben mantenerse semanticamente separados.

No son equivalentes:

```text
motivo_creacion
motivo_evaluacion
motivo_resolucion
motivo_cancelacion
motivo_obsolescencia
motivo_aplicacion
```

La auditoria estructurada debe permitir distinguir el motivo asociado al evento correspondiente.

---

## 21.10 Relacion con history

`history` puede seguir existiendo como trazabilidad historica del request.

La auditoria estructurada puede implementarse inicialmente sobre `history` si eso respeta el contrato de eventos.

No se exige en esta etapa una nueva tabla ni un refactor de persistencia.

---

## 21.11 Relacion con workflow formal

La auditoria debe acompañar las transiciones del workflow, no reemplazarlas.

Ejemplos:

```text
evaluar_swap_request
-> registra REQUEST_EVALUADA

resolver_swap_request
-> registra REQUEST_RESUELTA

aplicar_swap_request
-> registra REQUEST_APLICADA
```

Pero la existencia de un evento no debe ser usada como sustituto del estado formal.

---

## 21.12 Regla corta

La auditoria conserva hechos; no decide transiciones.

---

# Contrato 22 - Importacion y normalizacion de roster real acotado

## TOC

- [22.1 Proposito](#221-proposito)
- [22.2 Contexto](#222-contexto)
- [22.3 Entrada soportada V1](#223-entrada-soportada-v1)
- [22.4 Interpretacion de codigos](#224-interpretacion-de-codigos)
- [22.5 Salida contractual](#225-salida-contractual)
- [22.6 Responsabilidades permitidas](#226-responsabilidades-permitidas)
- [22.7 Responsabilidades prohibidas](#227-responsabilidades-prohibidas)
- [22.8 Validaciones estructurales](#228-validaciones-estructurales)
- [22.9 Eventos no operativos](#229-eventos-no-operativos)
- [22.10 Contexto intermensual](#2210-contexto-intermensual)
- [22.11 Relacion con roster_store](#2211-relacion-con-rosterstore)
- [22.12 Relacion con engine y workflow](#2212-relacion-con-engine-y-workflow)
- [22.13 Regla corta](#2213-regla-corta)

---

## 22.1 Proposito

Definir el contrato arquitectonico de importacion y normalizacion de roster real acotado.

La importacion convierte una matriz mensual simple en datos internos confiables para el sistema de swaps ATC.

---

## 22.2 Contexto

El sistema opera internamente con asignaciones y versiones de roster.

Para usar datos reales, se requiere una frontera de importacion que transforme una matriz humana en:

```text
asignaciones operativas internas
eventos no operativos registrados
reporte de importacion
metadata de importacion
```

sin alterar el workflow formal de `SwapRequest`.

---

## 22.3 Entrada soportada V1

La entrada soportada en V1 es:

```text
CSV o matriz tabular simple
```

Estructura esperada:

```text
controlador,01,02,03,...,30/31
CONTROLADOR A,A,B,,C,...,LA
CONTROLADOR B,,C,A,,...,PSI
```

Reglas:

- primera columna: controlador;
- columnas siguientes: dias del mes;
- una celda por controlador/dia;
- celda vacia = franco;
- `A`, `B`, `C` = turnos operativos;
- otros codigos conocidos = eventos no operativos;
- codigos desconocidos = error o warning segun politica.

---

## 22.4 Interpretacion de codigos

La interpretacion contractual es:

```text
A -> Asignacion operativa
B -> Asignacion operativa
C -> Asignacion operativa
celda vacia -> franco, no genera Asignacion
codigo no operativo conocido -> evento no operativo de importacion
codigo desconocido -> error o warning segun politica
```

El importador no debe interpretar codigos no operativos como turnos operativos.

---

## 22.5 Salida contractual

La salida conceptual debe ser:

```text
RosterImportResult
```

Contenido recomendado:

```text
asignaciones_operativas
eventos_no_operativos
warnings
errors
metadata
roster_version
```

`roster_version` puede ser `None` si la operacion solo parsea y valida sin persistir.

---

## 22.6 Responsabilidades permitidas

El importador puede:

1. Recibir una matriz o CSV simple.
2. Normalizar nombres de controladores.
3. Normalizar dias.
4. Normalizar codigos.
5. Identificar celdas vacias como francos.
6. Convertir `A`, `B`, `C` en asignaciones operativas.
7. Registrar codigos no operativos conocidos como eventos de importacion.
8. Detectar codigos desconocidos.
9. Generar warnings.
10. Generar errores bloqueantes.
11. Producir reporte de importacion.
12. Coordinar la creacion explicita de una `RosterVersion` inicial si no hay errores bloqueantes.

---

## 22.7 Responsabilidades prohibidas

El importador no puede:

- evaluar swaps;
- clasificar tecnicamente;
- decidir workflow;
- crear requests;
- resolver requests;
- aplicar requests;
- modificar requests existentes;
- llamar a `simulator`;
- reemplazar `engine`;
- inferir puestos no presentes;
- inferir supervisores;
- crear roles;
- crear permisos;
- crear locks;
- crear workflow bilateral;
- interpretar Excel generico con formato visual complejo;
- depender de colores, formulas o celdas combinadas.

---

## 22.8 Validaciones estructurales

Errores bloqueantes recomendados:

```text
controlador vacio
controlador duplicado
dia invalido
dia fuera de mes
codigo operativo desconocido
celda ambigua no parseable
fecha imposible
mes/anio invalido
```

Warnings recomendados:

```text
codigo no operativo conocido
codigo desconocido en modo permisivo
falta contexto previo
nombre normalizado
controlador sin turnos operativos
turnos no operativos ignorados por motor tecnico
puestos no definidos
supervisores no definidos
```

---

## 22.9 Eventos no operativos

Los codigos no operativos conocidos deben quedar fuera del motor tecnico en V1.

Ejemplos:

```text
LA
PSI
RTA
RTB
REM
RET
SIM
TW
```

Estos codigos pueden registrarse como eventos de importacion o elementos auxiliares del reporte.

No deben generar `Asignacion` operativa.

---

## 22.10 Contexto intermensual

El importador puede recibir contexto previo opcional:

```text
asignaciones_contexto_previas
```

Ese contexto puede servir para validaciones intermensuales.

No forma parte del roster mensual principal importado.

En V1 no se exige contexto posterior del mes siguiente.

Si falta contexto previo, el importador puede emitir warning.

---

## 22.11 Relacion con roster_store

`roster_store` persiste y versiona rosters.

`roster_store` no parsea CSV ni matrices humanas.

La creacion de una `RosterVersion` desde una importacion debe ser una accion explicita, posterior a parseo y validacion.

---

## 22.12 Relacion con engine y workflow

La importacion no reemplaza al `engine`.

La importacion prepara datos.

La validacion tecnica de reglas sigue perteneciendo a `engine`.

La evaluacion de swaps sigue perteneciendo al flujo formal existente.

La importacion no modifica el workflow:

```text
PENDIENTE
-> EVALUADO
-> APROBADO / RECHAZADO / CANCELADO
-> APLICADO
```

---

## 22.13 Regla corta

Importar roster convierte datos reales en asignaciones internas; no evalua, no decide y no aplica.

---

# Contrato 23 - Frontera de elegibilidad funcional para swaps normales

## TOC

- [23.1 Proposito](#231-proposito)
- [23.2 Contexto](#232-contexto)
- [23.3 Principio contractual](#233-principio-contractual)
- [23.4 Condiciones conceptuales de elegibilidad](#234-condiciones-conceptuales-de-elegibilidad)
- [23.5 Persona operativa general](#235-persona-operativa-general)
- [23.6 CMA / psicofisico](#236-cma--psicofisico)
- [23.7 Override administrativo](#237-override-administrativo)
- [23.8 Habilitaciones RADAR y TMA](#238-habilitaciones-radar-y-tma)
- [23.9 Codigos operativos y no operativos](#239-codigos-operativos-y-no-operativos)
- [23.10 Eventos no operativos](#2310-eventos-no-operativos)
- [23.11 Puestos no definidos](#2311-puestos-no-definidos)
- [23.12 Responsabilidades permitidas del importador](#2312-responsabilidades-permitidas-del-importador)
- [23.13 Responsabilidades prohibidas del importador](#2313-responsabilidades-prohibidas-del-importador)
- [23.14 Relacion con candidate_generation](#2314-relacion-con-candidategeneration)
- [23.15 Relacion futura con technical_prefilter](#2315-relacion-futura-con-technicalprefilter)
- [23.16 Regla corta](#2316-regla-corta)

---

## 23.1 Proposito

Definir la frontera conceptual de elegibilidad funcional para swaps normales.

El contrato evita confundir codigo de roster con elegibilidad automatica.

---

## 23.2 Contexto

El sistema importa rosters reales y genera asignaciones operativas internas.

Sin embargo, una asignacion operativa solo puede participar en un swap normal si la persona y el contexto permiten esa participacion.

La elegibilidad funcional depende de:

```text
persona
estado operativo general
codigo/evento de roster
configuracion de dependencia
puesto afectado, si existe
```

---

## 23.3 Principio contractual

El codigo del roster no alcanza para determinar elegibilidad.

La elegibilidad para swap es una evaluacion funcional del conjunto:

```text
persona + asignacion + contexto
```

---

## 23.4 Condiciones conceptuales de elegibilidad

Para que una asignacion pueda participar en un swap normal, conceptualmente deben cumplirse:

```text
persona pertenece al universo operativo intercambiable
estado_operativo_general = true
codigo del dia corresponde a asignacion operativa swappeable
codigo operativo activo por configuracion
puesto compatible si el puesto esta definido
```

---

## 23.5 Persona operativa general

Una persona con:

```text
estado_operativo_general = false
```

no participa en swaps operativos normales.

Esto bloquea cualquier asignacion operativa, incluso si el roster muestra `A`, `B` o `C`.

---

## 23.6 CMA / psicofisico

El CMA / psicofisico afecta el estado operativo general.

Regla conceptual:

```text
si fecha_vencimiento_cma <= fecha_actual
entonces estado_operativo_general = false
```

Esta regla queda documentada como dominio futuro.

No se implementa en este contrato.

---

## 23.7 Override administrativo

El override administrativo puede afectar la aptitud operativa.

Regla conceptual:

```text
si cma_override_operativo = false
entonces estado_operativo_general = false
```

Todo override administrativo debe tener:

```text
actor
motivo
fecha
```

Sin esos datos, el override no debe considerarse trazable.

---

## 23.8 Habilitaciones RADAR y TMA

Las habilitaciones reconocidas conceptualmente en esta etapa son:

```text
RADAR
TMA
```

La falta de habilitacion TMA no vuelve necesariamente no operativa a la persona.

Limita su compatibilidad con puestos TMA si el puesto esta definido.

Si el puesto no esta definido, la compatibilidad TMA queda fuera de V1.

---

## 23.9 Codigos operativos y no operativos

Codigos operativos activos para el contexto actual:

```text
A
B
C
```

Codigos operativos configurables futuros:

```text
D
X
```

Normalizaciones vigentes:

```text
IN -> EN
REM -> RTA
RET -> RTB
```

Codigos como `AE` y `AEC` corresponden a contextos de dependencias no H24 y quedan fuera del alcance operativo actual ACC.

Su aplicacion futura debe depender de configuracion por dependencia.

---

## 23.10 Eventos no operativos

Los eventos no operativos deben conservarse fuera de `Asignacion` operativa.

Ejemplos:

```text
LA
PSI
RTA
RTB
OJT
SIM
CAM
CIPE
EN
CO
TW
OF
```

Estos eventos pueden conservarse para trazabilidad, pero no generan swaps normales.

---

## 23.11 Puestos no definidos

Si el roster no define puestos, el sistema no debe inferirlos.

Regla V1:

```text
puesto no definido -> no aplicar filtro TMA
```

La elegibilidad por puesto queda reservada para V2.

---

## 23.12 Responsabilidades permitidas del importador

El importador puede:

```text
normalizar codigos
normalizar nombres
separar asignaciones operativas
registrar eventos no operativos
emitir warnings
emitir errores
preservar trazabilidad de eventos no operativos
```

---

## 23.13 Responsabilidades prohibidas del importador

El importador no puede:

```text
decidir elegibilidad funcional compleja
evaluar swaps
llamar simulator
llamar engine para reglas profundas
inferir puestos
inferir roles
inferir supervisores
inferir disponibilidad operativa por ausencia de OF
aplicar reglas de habilitacion TMA
crear requests
resolver requests
aplicar requests
```

---

## 23.14 Relacion con candidate_generation

`candidate_generation` solo debe generar candidatos desde asignaciones operativas swappeables.

No debe generar candidatos sobre eventos no operativos.

---

## 23.15 Relacion futura con technical_prefilter

`technical_prefilter` se reconoce como posible frontera futura para evaluar:

```text
estado operativo general
habilitaciones
compatibilidad por puesto
configuracion por dependencia
restricciones funcionales previas al simulator
```

Esta logica no se implementa todavia.

---

## 23.16 Regla corta

Solo una persona operativa, con asignacion operativa y contexto compatible, puede participar en swaps normales.

---

# Contrato 24 - Interpretacion configurable de codigos de roster

## TOC

- [24.1 Proposito](#241-proposito)
- [24.2 Contexto](#242-contexto)
- [24.3 Principio contractual](#243-principio-contractual)
- [24.4 Catalogo oficial](#244-catalogo-oficial)
- [24.5 Configuracion de dependencia](#245-configuracion-de-dependencia)
- [24.6 Categorias de codigos](#246-categorias-de-codigos)
- [24.7 Configuracion conceptual ACC](#247-configuracion-conceptual-acc)
- [24.8 Normalizaciones](#248-normalizaciones)
- [24.9 Codigos fuera de alcance](#249-codigos-fuera-de-alcance)
- [24.10 Politica de errores y warnings](#2410-politica-de-errores-y-warnings)
- [24.11 Responsabilidades permitidas](#2411-responsabilidades-permitidas)
- [24.12 Responsabilidades prohibidas](#2412-responsabilidades-prohibidas)
- [24.13 Relacion con engine](#2413-relacion-con-engine)
- [24.14 Relacion con elegibilidad](#2414-relacion-con-elegibilidad)
- [24.15 Regla corta](#2415-regla-corta)

---

## 24.1 Proposito

Definir el contrato conceptual para interpretar codigos de roster mediante configuracion por dependencia.

---

## 24.2 Contexto

El PR-GOPE-044 define codigos oficiales o documentales para listas de turno.

Sin embargo, la aplicabilidad de esos codigos depende del tipo de dependencia, regimen operativo y configuracion local.

Por eso, el sistema debe distinguir entre:

```text
codigo conocido
codigo aplicable
codigo activo
codigo operativo
codigo no operativo
codigo legacy
codigo fuera de alcance
```

---

## 24.3 Principio contractual

El catalogo oficial no implica activacion local.

Un codigo puede existir documentalmente y, aun asi, estar desactivado o fuera de alcance para una dependencia determinada.

---

## 24.4 Catalogo oficial

El catalogo oficial representa codigos conocidos o documentados.

Ejemplos:

```text
A
B
C
D
X
AE
AEC
LA
PSI
RTA
RTB
OJT
SIM
CAM
CIPE
EN
IN
CO
TW
OF
REM
RET
```

Este catalogo no decide por si solo si el codigo genera una `Asignacion` operativa.

---

## 24.5 Configuracion de dependencia

La configuracion de dependencia define como interpretar codigos en un contexto operativo determinado.

Debe poder expresar:

```text
tipo de dependencia
regimen operativo
codigos operativos activos
codigos operativos configurables
codigos no operativos
codigos legacy
codigos fuera de alcance
normalizaciones
politica strict
```

---

## 24.6 Categorias de codigos

Las categorias conceptuales son:

```text
OPERATIVO_ACTIVO
OPERATIVO_CONFIGURABLE
NO_OPERATIVO
NORMALIZABLE
LEGACY
FUERA_DE_ALCANCE
DESCONOCIDO
```

Solo los codigos `OPERATIVO_ACTIVO` deben generar `Asignacion` operativa en V1.

Los codigos `NO_OPERATIVO` deben conservarse como eventos no operativos o datos auxiliares de importacion.

---

## 24.7 Configuracion conceptual ACC

Para el contexto actual ACC:

```text
OPERATIVO_ACTIVO:
  A
  B
  C

OPERATIVO_CONFIGURABLE:
  D
  X

NO_OPERATIVO:
  LA
  PSI
  RTA
  RTB
  OJT
  SIM
  CAM
  CIPE
  EN
  CO
  TW
  OF

NORMALIZABLE:
  IN -> EN
  REM -> RTA
  RET -> RTB

FUERA_DE_ALCANCE:
  AE
  AEC
```

Esta configuracion es conceptual y documental.

No implica implementacion inmediata.

---

## 24.8 Normalizaciones

Las normalizaciones vigentes son:

```text
IN -> EN
REM -> RTA
RET -> RTB
```

Una normalizacion debe registrar o emitir warning de importacion si corresponde.

La normalizacion no debe ocurrir silenciosamente si afecta trazabilidad.

---

## 24.9 Codigos fuera de alcance

Un codigo fuera de alcance no es necesariamente invalido en todo el sistema.

Ejemplo:

```text
AE
AEC
```

Estos codigos quedan fuera de alcance para ACC actual, pero podrian aplicar a dependencias no H24 si la configuracion correspondiente los habilita.

---

## 24.10 Politica de errores y warnings

Errores bloqueantes recomendados:

```text
codigo desconocido sin normalizacion
codigo fuera de alcance en strict=True
codigo operativo configurable no activo usado como operativo
codigo ambiguo
codigo incompatible con tipo de dependencia
```

Warnings recomendados:

```text
codigo legacy normalizado
codigo normalizado
codigo no operativo conocido
codigo configurable desactivado, si la politica lo permite
```

La politica exacta debe depender de la configuracion de importacion.

---

## 24.11 Responsabilidades permitidas

La configuracion de codigos puede ser usada para:

```text
normalizar codigos
clasificar codigos
validar codigos de entrada
emitir warnings
emitir errores
determinar si un codigo genera Asignacion operativa
determinar si un codigo queda como evento no operativo
```

---

## 24.12 Responsabilidades prohibidas

La configuracion de codigos no puede:

```text
evaluar swaps
decidir workflow
aprobar requests
rechazar requests
cancelar requests
aplicar requests
calcular permisos
inferir roles
inferir puestos
reemplazar reglas tecnicas del engine
```

---

## 24.13 Relacion con engine

El `engine` valida reglas tecnicas.

La configuracion de codigos prepara datos antes de que lleguen al motor tecnico.

No deben mezclarse:

```text
validacion de codigo de roster
```

con:

```text
validacion tecnica de descanso, secuencias o noches
```

---

## 24.14 Relacion con elegibilidad

La configuracion de codigos es una condicion previa para elegibilidad funcional.

Pero no define elegibilidad completa.

Ejemplo:

```text
codigo = A
categoria = OPERATIVO_ACTIVO
```

no alcanza si:

```text
estado_operativo_general = false
```

o si el puesto definido exige una habilitacion que la persona no tiene.

---

## 24.15 Regla corta

El catalogo dice que codigos existen; la configuracion dice que codigos aplican.