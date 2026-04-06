# Modelo de dominio

## Tabla de contenido

- [1. Objetivo](#1-objetivo)
- [2. Alcance](#2-alcance)
- [3. Entidades principales](#3-entidades-principales)
- [4. Definicion de entidades](#4-definicion-de-entidades)
  - [4.1 SwapRequest](#41-swaprequest)
  - [4.2 RosterVersion](#42-rosterversion)
  - [4.3 Asignacion](#43-asignacion)
  - [4.4 Controlador](#44-controlador)
  - [4.5 Turno](#45-turno)
- [5. Relaciones entre entidades](#5-relaciones-entre-entidades)
- [6. Conceptos clave del dominio](#6-conceptos-clave-del-dominio)
- [7. Semantica de versiones](#7-semantica-de-versiones)
- [8. Identidad del objeto del swap](#8-identidad-del-objeto-del-swap)
- [9. Separacion conceptual](#9-separacion-conceptual)
- [10. Reglas del dominio](#10-reglas-del-dominio)
- [11. Proposito del modelo](#11-proposito-del-modelo)
- [Nota de frontera con simulacion](#nota-de-frontera-con-simulacion)

---

## 1. Objetivo

Definir las entidades principales del sistema de swaps ATC, su significado conceptual, sus relaciones y las reglas del dominio que deben preservarse independientemente de la implementación.

Este documento describe qué son las cosas del sistema, no cómo se implementan ni qué módulo las gestiona.

---

## 2. Alcance

Este modelo cubre:

- entidades del dominio
- relaciones entre entidades
- identidad conceptual
- estados del dominio
- reglas del negocio ligadas a las entidades

No cubre:

- implementación
- contratos entre módulos
- lógica de servicios
- detalles técnicos

---

## 3. Entidades principales

El dominio está compuesto por las siguientes entidades:

- SwapRequest
- RosterVersion
- Asignacion
- Controlador
- Turno

---

## 4. Definicion de entidades

### 4.1 SwapRequest

#### Definicion

Entidad que representa una intención de intercambio de turnos entre dos asignaciones, su evaluación técnica, su tratamiento operativo y su resultado dentro del flujo del sistema.

#### Naturaleza

Entidad de proceso auditable.

#### Componentes conceptuales

**A. Intencion**
- qué asignaciones se desean intercambiar
- a qué versión del roster pertenece

**B. Evaluacion tecnica**
- clasificación técnica del swap

**C. Decision operativa**
- decisión del sistema (VIABLE / OBSERVAR / RECHAZAR)
- motivo operativo cuando corresponda

**D. Workflow**
- estado del request
- historial de eventos

#### Identidad

Un SwapRequest es único por:

- su identificador
- la versión de roster a la que pertenece

#### Restricciones conceptuales

- pertenece a una única RosterVersion
- refiere exactamente dos asignaciones dentro de esa versión
- no puede existir fuera del contexto de una versión

#### Propiedad de simetria

Un SwapRequest refiere dos asignaciones sin jerarquía entre ellas.

El intercambio es simétrico: ambas asignaciones son equivalentes como objeto del swap.

Las nociones de “origen” y “destino” son únicamente técnicas y no forman parte del modelo de dominio.

#### Propiedad de inmutabilidad de evaluacion

Una vez evaluado un SwapRequest:

- su clasificación técnica no debe cambiar
- representa el resultado técnico sobre la versión en la que fue evaluado

Si cambia la versión del roster:

- el request no se reevalúa automáticamente
- el request pasa a ser obsoleto

#### Estados del dominio

- PENDIENTE
- EVALUADO
- APROBADO
- RECHAZADO
- CANCELADO
- APLICADO

#### Aclaración de planos

El SwapRequest actúa como entidad agregadora de:

- evaluación técnica
- decisión operativa
- estado del workflow

Estos planos permanecen conceptualmente separados y no deben colapsarse.

---

### 4.2 RosterVersion

#### Definicion

Snapshot completo e inmutable del roster en un momento del sistema.

#### Naturaleza

Entidad de estado versionado.

#### Propiedades

- representa un estado consistente del roster
- es inmutable a nivel conceptual
- puede ser vigente o histórica
- puede ser origen de otras versiones

#### Identidad

Una RosterVersion es única por su identificador.

#### Relacion temporal

Las versiones forman una secuencia de evolución del roster.

#### Propiedad temporal

Las versiones forman una línea de tiempo única del sistema.

Cada nueva versión:

- deriva de una versión anterior
- representa un nuevo estado consistente
- reemplaza a la versión vigente anterior

No existen bifurcaciones en la línea de versiones dentro del flujo operativo normal.

#### Rol en el sistema

- fuente de verdad operativa
- base para evaluación de swaps
- contexto de aplicación de cambios

---

### 4.3 Asignacion

#### Definicion

Unidad operativa del roster que asigna un controlador a un turno en una fecha específica dentro de una versión.

#### Naturaleza

Entidad de dominio base.

#### Componentes

- controlador
- fecha
- turno

#### Identidad

Una Asignacion existe dentro de una RosterVersion.

Su identidad está dada por:

- la versión a la que pertenece
- su contenido operativo

El contenido operativo incluye, al menos:

- controlador
- fecha
- turno

Y puede extenderse con otros atributos operativos relevantes (ej: posición, sector, rol).

#### Propiedad clave

Una asignación no es una posición en una lista, sino una unidad operativa del sistema.

---

### 4.4 Controlador

#### Definicion

Entidad que representa a un controlador de tránsito aéreo.

#### Rol

Participa en asignaciones dentro del roster.

---

### 4.5 Turno

#### Definicion

Tipo de actividad asignada en una fecha.

#### Ejemplos

- turno mañana
- turno tarde
- turno noche
- entrenamiento

---

## 5. Relaciones entre entidades

- SwapRequest ↔ RosterVersion  
  Un SwapRequest pertenece a una única RosterVersion.

- RosterVersion ↔ Asignacion  
  Una RosterVersion contiene un conjunto de Asignacion.

- SwapRequest ↔ Asignacion  
  Un SwapRequest refiere exactamente dos asignaciones dentro de la misma versión.

- Asignacion ↔ Controlador  
  Cada asignación corresponde a un controlador.

- Asignacion ↔ Turno  
  Cada asignación define un turno o actividad.

---

## 6. Conceptos clave del dominio

### 6.1 Clasificacion tecnica

Resultado de evaluar el impacto del swap sobre el roster.

Valores:

- BENEFICIOSO
- ACEPTABLE
- RECHAZABLE

No incluye:

- restricciones operativas
- estados del request

---

### 6.2 Decision operativa

Resultado del tratamiento del request dentro del sistema.

Valores:

- VIABLE
- OBSERVAR
- RECHAZAR

Puede diferir de la clasificación técnica.

---

### 6.3 Motivo operativo

Explica por qué una decisión operativa se aparta del resultado técnico.

Ejemplo:

- fuera de ventana operativa

---

## 7. Semantica de versiones

### 7.1 Version vigente

Versión actual del roster utilizada por el sistema.

### 7.2 Version evaluable

Versión sobre la cual se evalúa un request.

### 7.3 Version aplicable

Versión sobre la cual puede ejecutarse un swap.

### Regla unificada

Un request está habilitado dentro del flujo si su versión coincide con la versión vigente.

### Obsolescencia

Un request se vuelve obsoleto cuando su versión deja de ser vigente.

---

## 8. Identidad del objeto del swap

El objeto real del intercambio son las asignaciones.

No son:

- índices
- posiciones
- identificadores técnicos

Son:

- unidades operativas dentro de una versión

### Semantica del intercambio

El swap del dominio opera sobre dos asignaciones de una misma versión.

La operación consiste en intercambiar el turno o actividad asignado entre ellas.

Consecuencia:

- las asignaciones siguen siendo las unidades del dominio involucradas
- el cambio efectivo recae sobre el contenido de turno o actividad
- la identidad base de cada asignación se preserva

---

## 9. Separacion conceptual

El sistema separa tres planos:

### Evaluacion tecnica

Describe el impacto del swap.

### Decision operativa

Describe el tratamiento del request.

### Aplicacion

Describe el cambio real sobre el roster.

Ver separación operativa implementada en:  
[Ref: contratos.md #16]

y decisiones arquitectónicas en:  
[Ref: decisiones.md]

---

## 10. Reglas del dominio

- todo request pertenece a una única versión
- no se evalúan requests sobre versiones no vigentes
- no se aplican swaps sobre versiones no vigentes
- toda aplicación genera una nueva versión
- la versión previa permanece inmutable
- los requests de versiones no vigentes se vuelven obsoletos

---

## 11. Proposito del modelo

Este modelo asegura:

- consistencia conceptual
- claridad semántica
- trazabilidad
- independencia de implementación
- base sólida para evolución del sistema

---

## Nota de frontera con simulacion

La simulación del swap pertenece al plano de evaluación técnica y no implica por sí misma:

- workflow del request
- decisión operativa
- presentación textual
- versionado formal del roster

La simulación compara escenarios hipotéticos; la gestión de versiones pertenece al plano de estado real del sistema.

---

## IMPORTANTE

APROBADO = estado posterior a decisión operativa favorable