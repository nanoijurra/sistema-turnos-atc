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
- **decisión operativa** → tratamiento del request (swap_service)
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
- decisiones operativas
- persistencia de requests

No debe:
- duplicar lógica de validación del engine
- ejecutar reglas directamente fuera de validar_todo

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

Evaluar un `SwapRequest` dentro del flujo de negocio, asignar clasificación técnica y decisión operativa, actualizar su estado y persistir el resultado.

#### Responsabilidad

Es la fuente única de verdad de la decisión operativa del request.

#### Debe hacer

- cargar el `SwapRequest`
- validar consistencia estructural del request
- validar que el request esté en estado evaluable
- validar que el request pertenezca a una `roster_version_id` válida
- validar que el request esté asociado a la versión vigente del sistema
- validar ventana operativa
- si corresponde, invocar `simulator.evaluar_swap(...)`
- mapear clasificación técnica a decisión operativa
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
- no resuelve aceptación/rechazo final fuera del flujo definido

#### Estado resultante

Si la evaluación se completa:
- el request queda en estado `EVALUADO`

#### Persistencia obligatoria

Debe persistir al menos:
- clasificación técnica
- decisión operativa
- motivo, si aplica
- estado actualizado
- history

#### Regla critica

`swap_service` consume la clasificación técnica producida por `simulator` y solo agrega interpretación operativa; no puede reemplazar ni recalcular la clasificación.

👉 Fuente de verdad de decisión

#### Aclaración sobre clasificación técnica ausente

Si la evaluación técnica no se ejecuta por una restricción operativa:

- la clasificación técnica puede ser nula
- debe persistirse explícitamente como ausente
- no debe inferirse ni reemplazarse por lógica operativa

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

`aplicar_swap_request` ejecuta una decisión ya tomada; no realiza una nueva evaluación.

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

La decisión operativa:
- puede derivarse normalmente de la clasificación técnica
- puede verse afectada por restricciones operativas
- debe registrarse separadamente de la clasificación técnica

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

El flujo del sistema se divide en tres niveles:

1. evaluación técnica
2. decisión operativa
3. aplicación persistente

Cada nivel tiene un único responsable.

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

#### 8.1.3 Decision operativa

##### Responsable
- swap_service

##### Alcance

La decisión operativa determina:
- si el request queda VIABLE / OBSERVAR / RECHAZAR
- estado del request
- persistencia e historial

##### Regla

La decisión operativa surge de:
- clasificación técnica recibida desde simulator
- validaciones operativas propias de swap_service

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
2. swap_service decide, no clasifica
3. aplicar no reevalúa
4. engine no decide negocio
5. validez del roster ≠ aprobación automática
6. ventana operativa puede rechazar swaps válidos técnicamente
7. flujo favorable:
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

`simulator` clasifica.  
`swap_service` decide.  
La aplicación no reevalúa.  
El estado refleja la evolución del request dentro del workflow.

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

Todo cambio relevante debe registrarse en history

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
El estado APROBADO representa la materialización en el workflow de una decisión operativa favorable.

## 12. Contrato de frontera publica de simulator

### Proposito
Definir la superficie publica valida de `simulator` y evitar mezcla con responsabilidades operativas.

---

### Frontera valida de simulator

`simulator` expone unicamente capacidades tecnicas.

Puede exponer:
- evaluacion tecnica de swaps
- comparacion de escenarios
- clasificacion tecnica
- calculo de impacto
- exploracion de alternativas

---

### Prohibicion de exposicion operativa

`simulator` no debe exponer funciones relacionadas con:
- creacion de SwapRequest
- evaluacion de SwapRequest
- resolucion de SwapRequest
- aplicacion de SwapRequest
- gestion de estado
- workflow operativo

---

### Regla de delegacion

La existencia de delegacion interna hacia `swap_service` no habilita la exposicion publica de funciones operativas desde `simulator`.

---

### Puerta operativa unica

Todas las operaciones del ciclo de vida del request deben exponerse exclusivamente desde `swap_service`.

---

### Regla de consistencia

La superficie publica del modulo debe reflejar exclusivamente sus responsabilidades.

En consecuencia:
- `simulator` publica evaluacion tecnica
- `swap_service` publica operacion y workflow

Ambas superficies no deben solaparse.