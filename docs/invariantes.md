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
- [Invariante 10 - Fachada de creacion y evaluacion formal desde oferta](#invariante-10---fachada-de-creacion-y-evaluacion-formal-desde-oferta)
- [Invariante 11 - Decision sugerida no equivale a resolucion operativa](#invariante-11---decision-sugerida-no-equivale-a-resolucion-operativa)
- [Invariante 12 - Aplicar ejecuta, no evalua ni resuelve](#invariante-12---aplicar-ejecuta-no-evalua-ni-resuelve)

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
- puede mapear la evaluación formal a una decision_sugerida operativa sin alterar la clasificación técnica

---

### I-4 Aplicar no reevalua

La aplicación de un swap:

- no reevalúa
- no reclasifica
- no redefine decisiones
- no resuelve

Ejecuta una decisión favorable previamente tomada y explicitamente aprobada.

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

### I-16 bis Evaluar informa, resolver decide

La evaluacion formal de una `SwapRequest` informa resultado tecnico-operativo.

No puede por si misma:

- aprobar;
- rechazar terminalmente;
- cancelar;
- aplicar.

La resolucion operativa debe ser una accion explicita posterior.

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

El `actor` registrado en `history` identifica quien ejecuto o disparo una accion, pero no define por si mismo permisos formales ni autorizacion operativa.

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
- evaluar informa
- resolver decide explicitamente
- aplicar ejecuta
- aplicar no reevalúa
- aplicar solo puede ejecutarse sobre `APROBADO`
- `VIABLE` no equivale a `APROBADO`
- `APROBADO` no equivale a `APLICADO`
- todo request pertenece a una única versión
- no aplicar sobre versión distinta
- toda aplicación crea nueva versión
- clasificación ≠ decisión
- restricciones operativas no alteran clasificación técnica
- fuente única de reglas
- estados terminales no reingresan
- cancelacion por obsolescencia no equivale a rechazo operativo
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

---

# Invariante 10 - Fachada de creacion y evaluacion formal desde oferta

## TOC

- [10.1 Regla principal](#101-regla-principal)
- [10.2 La request nace PENDIENTE](#102-la-request-nace-pendiente)
- [10.3 La evaluacion formal pertenece a swap_service](#103-la-evaluacion-formal-pertenece-a-swap_service)
- [10.4 offer_origin es evidencia observada](#104-offer_origin-es-evidencia-observada)
- [10.5 La fachada no decide](#105-la-fachada-no-decide)
- [10.6 La fachada no resuelve](#106-la-fachada-no-resuelve)
- [10.7 La fachada no aplica](#107-la-fachada-no-aplica)
- [10.8 La fachada no evalua por cuenta propia](#108-la-fachada-no-evalua-por-cuenta-propia)
- [10.9 La divergencia no es error automatico](#109-la-divergencia-no-es-error-automatico)
- [10.10 La mejora de performance no es objetivo de la fachada](#1010-la-mejora-de-performance-no-es-objetivo-de-la-fachada)
- [10.11 Regla corta](#1011-regla-corta)

---

## 10.1 Regla principal

La fachada `crear_request_desde_oferta_y_evaluar_formalmente` no crea un workflow paralelo de ofertas.

La unica entidad con workflow operativo formal sigue siendo:

```text
SwapRequest
```

La oferta evaluada sigue siendo solamente:

```text
resultado tecnico presentable y seleccionable
```

---

## 10.2 La request nace PENDIENTE

Toda `SwapRequest` creada desde una oferta debe nacer primero en estado:

```text
PENDIENTE
```

Aunque la fachada ejecute inmediatamente la evaluacion formal, la request no puede nacer directamente como `EVALUADO`.

La transicion valida es:

```text
PENDIENTE -> EVALUADO
```

---

## 10.3 La evaluacion formal pertenece a swap_service

La evaluacion formal de una request creada desde oferta debe realizarse mediante:

```text
swap_service.evaluar_swap_request
```

Ninguna fachada puede reemplazar esa evaluacion usando directamente informacion de `offer_origin`.

---

## 10.4 offer_origin es evidencia observada

`offer_origin` conserva informacion observada durante la generacion de la oferta.

Esa informacion no reemplaza:

- clasificacion formal;
- decision operativa;
- estado del workflow;
- motivo de resolucion;
- resultado formal de evaluacion;
- aprobacion;
- aplicacion.

---

## 10.5 La fachada no decide

La fachada no puede decidir por cuenta propia:

```text
VIABLE
OBSERVAR
RECHAZAR
```

Si existe `decision_sugerida`, debe provenir del flujo formal de `swap_service`.

---

## 10.6 La fachada no resuelve

La fachada no puede llevar una request a:

```text
APROBADO
RECHAZADO
CANCELADO
APLICADO
```

Para este contrato, la fachada solo puede llegar hasta:

```text
EVALUADO
```

---

## 10.7 La fachada no aplica

La fachada no puede invocar ni reemplazar:

```text
swap_service.aplicar_swap_request
```

La aplicacion sigue siendo una operacion formal posterior y separada.

---

## 10.8 La fachada no evalua por cuenta propia

La fachada no puede llamar directamente a:

```text
engine
scoring
simulator
```

Tampoco puede reconstruir clasificacion tecnica por fuera de `swap_service.evaluar_swap_request`.

---

## 10.9 La divergencia no es error automatico

Una diferencia entre la clasificacion observada de la oferta y la clasificacion formal posterior no constituye automaticamente un error.

Debe tratarse como:

```text
trazabilidad
advertencia operativa
evidencia de cambio de contexto
```

No debe tratarse automaticamente como violacion de contrato.

---

## 10.10 La mejora de performance no es objetivo de la fachada

La fachada no existe para mejorar benchmarks de exploracion.

La optimizacion de exploracion pertenece a:

```text
candidate_generation
technical_prefilter
candidate_selection
exploration_flow
```

La fachada existe para mejorar:

- consistencia operativa;
- trazabilidad;
- facilidad de integracion futura;
- reduccion de requests creadas desde oferta que queden sin evaluacion formal.

---

## 10.11 Regla corta

La fachada puede encadenar creacion y evaluacion formal, pero no puede convertir evidencia observada en decision operativa ni en aprobacion.

---

# Invariante 11 - Decision sugerida no equivale a resolucion operativa

## TOC

- [11.1 Regla principal](#111-regla-principal)
- [11.2 EVALUADO no significa APROBADO](#112-evaluado-no-significa-aprobado)
- [11.3 VIABLE no significa APROBADO](#113-viable-no-significa-aprobado)
- [11.4 RECHAZAR no significa RECHAZADO](#114-rechazar-no-significa-rechazado)
- [11.5 La resolucion debe ser explicita](#115-la-resolucion-debe-ser-explicita)
- [11.6 La resolucion no aplica](#116-la-resolucion-no-aplica)
- [11.7 La resolucion no reevalua](#117-la-resolucion-no-reevalua)
- [11.8 offer_origin no se modifica](#118-offerorigin-no-se-modifica)
- [11.9 No hay workflow bilateral en V1](#119-no-hay-workflow-bilateral-en-v1)
- [11.10 Regla corta](#1110-regla-corta)

---

## 11.1 Regla principal

La `decision_sugerida` producida durante la evaluacion formal no equivale a resolucion operativa.

La resolucion debe ser una accion explicita posterior sobre una `SwapRequest` en estado `EVALUADO`.

---

## 11.2 EVALUADO no significa APROBADO

Una request en estado:

```text
EVALUADO
```

no esta aprobada.

Debe existir una accion formal posterior para pasar a:

```text
APROBADO
```

---

## 11.3 VIABLE no significa APROBADO

Una `decision_sugerida` igual a:

```text
VIABLE
```

no convierte automaticamente la request en:

```text
APROBADO
```

`VIABLE` orienta, pero no resuelve.

---

## 11.4 RECHAZAR no significa RECHAZADO

Una `decision_sugerida` igual a:

```text
RECHAZAR
```

no convierte automaticamente la request en:

```text
RECHAZADO
```

El rechazo terminal debe ser una resolucion formal con trazabilidad.

---

## 11.5 La resolucion debe ser explicita

La transicion desde:

```text
EVALUADO
```

hacia:

```text
APROBADO
RECHAZADO
CANCELADO
```

requiere una accion explicita de resolucion.

No se permite resolucion automatica en V1.

---

## 11.6 La resolucion no aplica

La resolucion operativa no puede llevar directamente a:

```text
APLICADO
```

La aplicacion sigue siendo una etapa posterior y separada.

---

## 11.7 La resolucion no reevalua

La resolucion operativa no debe reevaluar la request.

No debe llamar directamente a:

```text
engine
scoring
simulator
```

La evaluacion formal ya fue realizada previamente mediante `swap_service.evaluar_swap_request`.

---

## 11.8 offer_origin no se modifica

Si la request proviene de una oferta, `offer_origin` debe permanecer como evidencia observada.

La resolucion no puede modificar:

```text
clasificacion_observada
delta_score_observado
delta_hard_observado
delta_soft_observado
```

---

## 11.9 No hay workflow bilateral en V1

En V1 no se agregan estados formales de aceptacion bilateral.

No se incorporan estados como:

```text
PROPUESTO
ACEPTADO_POR_CONTRAPARTE
RECHAZADO_POR_CONTRAPARTE
PENDIENTE_SUPERVISOR
```

La contraparte no se modela todavia como workflow propio.

---

## 11.10 Regla corta

La evaluacion formal informa; la resolucion operativa decide; la aplicacion ejecuta.

---

# Invariante 12 - Aplicar ejecuta, no evalua ni resuelve

## TOC

- [12.1 Regla principal](#121-regla-principal)
- [12.2 Solo APROBADO puede aplicar](#122-solo-aprobado-puede-aplicar)
- [12.3 Estados prohibidos para aplicar](#123-estados-prohibidos-para-aplicar)
- [12.4 Aplicar no reevalua](#124-aplicar-no-reevalua)
- [12.5 Aplicar no resuelve](#125-aplicar-no-resuelve)
- [12.6 Aplicar no modifica offer_origin](#126-aplicar-no-modifica-offerorigin)
- [12.7 Aplicar no modifica decision_sugerida](#127-aplicar-no-modifica-decisionsugerida)
- [12.8 Aplicar crea nueva version de roster](#128-aplicar-crea-nueva-version-de-roster)
- [12.9 Aplicar no se repite](#129-aplicar-no-se-repite)
- [12.10 Cancelacion de obsoletos](#1210-cancelacion-de-obsoletos)
- [12.11 Regla corta](#1211-regla-corta)

---

## 12.1 Regla principal

La aplicacion ejecuta un swap aprobado sobre el roster.

La aplicacion no evalua, no resuelve y no decide.

---

## 12.2 Solo APROBADO puede aplicar

La aplicacion solo puede ejecutarse sobre una `SwapRequest` en estado:

```text
APROBADO
```

---

## 12.3 Estados prohibidos para aplicar

No se puede aplicar una request en estado:

```text
PENDIENTE
EVALUADO
RECHAZADO
CANCELADO
APLICADO
```

---

## 12.4 Aplicar no reevalua

La aplicacion no puede reevaluar la request.

No puede llamar directamente a:

```text
engine
scoring
simulator
```

Tampoco puede reemplazar ni recalcular la evaluacion formal previa.

---

## 12.5 Aplicar no resuelve

La aplicacion no puede aprobar, rechazar ni cancelar por decision operativa.

La request debe llegar a aplicacion ya resuelta como:

```text
APROBADO
```

---

## 12.6 Aplicar no modifica offer_origin

Si la request proviene de una oferta, `offer_origin` debe permanecer como evidencia observada.

La aplicacion no puede modificar:

```text
clasificacion_observada
delta_score_observado
delta_hard_observado
delta_soft_observado
selection_metadata
```

---

## 12.7 Aplicar no modifica decision_sugerida

La aplicacion no puede modificar `decision_sugerida`.

`decision_sugerida` pertenece al resultado de evaluacion formal.

---

## 12.8 Aplicar crea nueva version de roster

La aplicacion exitosa debe crear una nueva version de roster.

La nueva version representa el roster luego del swap aplicado.

---

## 12.9 Aplicar no se repite

Una request en estado:

```text
APLICADO
```

no puede aplicarse nuevamente.

La aplicacion debe ser idempotente desde el punto de vista de proteccion del workflow: ante un segundo intento, debe rechazar la operacion.

---

## 12.10 Cancelacion de obsoletos

Si la aplicacion genera una nueva version de roster, las requests asociadas a versiones anteriores pueden quedar obsoletas.

La cancelacion por obsolescencia debe:

- registrar motivo;
- registrar history;
- no tocar requests ya `APLICADO`;
- no reevaluar;
- no aplicar;
- diferenciarse de una cancelacion operativa normal;
- no tratarse como rechazo operativo.

---

## 12.11 Regla corta

Aplicar solo ejecuta una request aprobada y crea una nueva version de roster.