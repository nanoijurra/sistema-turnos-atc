# Invariantes del sistema

## Tabla de contenido

- [1. Objetivo](#1-objetivo)
- [2. Invariantes de capas](#2-invariantes-de-capas)
- [3. Invariantes de flujo y versionado](#3-invariantes-de-flujo-y-versionado)
- [4. Invariantes de decision y evaluacion](#4-invariantes-de-decision-y-evaluacion)
- [5. Invariantes de reglas y validacion](#5-invariantes-de-reglas-y-validacion)
- [6. Invariantes de estados y trazabilidad](#6-invariantes-de-estados-y-trazabilidad)
- [7. Invariantes del dominio del swap](#7-invariantes-del-dominio-del-swap)
- [8. Invariantes criticos](#8-invariantes-criticos)
- [9. Proposito arquitectonico](#9-proposito-arquitectonico)

---

## 1. Objetivo

Definir las reglas fundamentales que el sistema de swaps ATC debe preservar siempre, independientemente de la implementación.

Los invariantes representan verdades del sistema que no pueden violarse sin romper su consistencia conceptual.

---

## 2. Invariantes de capas

### I-1 Engine no decide negocio

El módulo engine:

- no toma decisiones operativas (VIABLE / OBSERVAR / RECHAZAR)
- no modifica estados de SwapRequest

Su responsabilidad es exclusivamente técnica (validación de reglas).

---

### I-2 Simulator no decide ni persiste

El módulo simulator:

- puede clasificar swaps
- no puede decidir
- no puede persistir
- no puede modificar requests
- no puede crear versiones de roster

---

### I-3 SwapService no reclasifica

El módulo swap_service:

- no puede recalcular ni reinterpretar la clasificación técnica
- debe consumir la clasificación producida por simulator

---

### I-4 Aplicar no reevalua

La aplicación de un swap:

- no reevalúa
- no reclasifica
- no redefine decisiones

Ejecuta una decisión previamente tomada.

---

## 3. Invariantes de flujo y versionado

### I-5 Todo request pertenece a una version

Todo SwapRequest debe estar ligado a una única `roster_version_id`.

---

### I-6 Evaluacion sobre la version propia y vigente

Un request debe evaluarse usando exactamente la versión de roster a la que pertenece, siempre que dicha versión sea la versión vigente del sistema.

---

### I-7 No aplicar sobre version distinta

Un request no puede aplicarse sobre una versión distinta de la evaluada.

---

### I-8 Aplicar genera nueva version

Toda aplicación válida de un swap debe generar una nueva versión de roster.

---

### I-9 Version vigente unica

Debe existir una única versión vigente del roster en cada momento.

---

### I-10 Obsolescencia por cambio de version

Todo request no terminal asociado a una versión que deja de ser vigente:

- pasa a ser obsoleto
- deja de ser aplicable dentro del flujo normal

---

### I-11 Request evaluable y aplicable dentro del flujo solo en version vigente

Un SwapRequest solo puede ser evaluado y aplicado si su `roster_version_id` coincide con la versión vigente.

---

### I-12 Toda modificacion pasa por versionado

Ningún cambio real del roster puede ocurrir fuera del flujo que:

- crea una nueva versión
- actualiza la vigencia del sistema

---

## 4. Invariantes de decision y evaluacion

### I-13 Clasificacion tecnica ≠ decision operativa

- clasificación técnica = evaluación técnica del impacto del swap
- decisión operativa = tratamiento del request dentro del flujo

Nunca deben confundirse ni colapsarse en un único concepto.

---

### I-14 Mapeo no identitario

Existe un mapeo normal entre clasificación técnica y decisión operativa, pero no son equivalentes.

Las restricciones operativas pueden endurecer la decisión sin alterar la clasificación técnica.

---

### I-15 Restricciones operativas pueden rechazar swaps validos

Un swap técnicamente válido puede ser rechazado por condiciones operativas.

---

### I-16 Restricciones operativas no falsifican evaluacion tecnica

Ninguna restricción operativa puede transformar una causa de rechazo operativo en una falsa clasificación técnica del swap.

---

## 5. Invariantes de reglas y validacion

### I-17 Fuente unica de reglas

Todas las reglas hard/soft deben ejecutarse exclusivamente en engine.

---

### I-18 Interpretacion unica de configuracion

La semántica de todos los parámetros configurables pertenece exclusivamente al engine.

Ningún otro módulo puede reinterpretarlos.

---

### I-19 Hard no degradable

Una regla hard nunca puede reinterpretarse como soft.

---

### I-20 Soft no determina decision operativa favorable

Las reglas soft no pueden, por sí solas, determinar una decisión operativa favorable.

---

### I-21 Simulacion sobre base consistente

Toda simulación debe partir de un roster consistente y definido.

---

## 6. Invariantes de estados y trazabilidad

### I-22 Transiciones validas

Un SwapRequest solo puede seguir transiciones válidas del flujo definido.

---

### I-23 Estados terminales son finales

Los estados:

- RECHAZADO
- CANCELADO
- APLICADO

no pueden reingresar al flujo.

---

### I-24 Trazabilidad obligatoria

Todo cambio relevante en un request debe registrarse en history.

---

### I-25 Trazabilidad de asignaciones

El sistema nunca debe perder la relación entre:

- asignación
- controlador
- fecha

aunque se apliquen swaps.

---

## 7. Invariantes del dominio del swap

### I-26 El objeto del swap son asignaciones

Todo swap debe entenderse como una operación sobre dos asignaciones dentro de una misma versión.

Los índices:

- pueden usarse como referencia estructural
- no definen la identidad del objeto del dominio

---

## 8. Invariantes criticos

Estos invariantes son considerados fundamentales:

- engine valida, no decide
- simulator clasifica, no decide ni persiste
- swap_service decide, no clasifica
- aplicar no reevalúa
- todo request pertenece a una única versión
- no aplicar sobre versión distinta
- toda aplicación crea nueva versión
- clasificación ≠ decisión
- restricciones operativas no alteran clasificación técnica
- fuente única de reglas
- estados terminales no reingresan
- roster vigente único

Ver formalización de responsabilidades y fronteras en:  
[Ref: contratos.md #16]

---

## 9. Proposito arquitectonico

Estos invariantes permiten:

- evitar duplicación de lógica
- preservar consistencia entre módulos
- mantener separación de responsabilidades
- asegurar trazabilidad
- soportar evolución del sistema sin degradar diseño