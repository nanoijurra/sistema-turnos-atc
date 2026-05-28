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

## 13.Contrato de priorizacion historica de swaps

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


