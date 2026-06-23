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

---

# Invariante 13 - La auditoria registra hechos y no gobierna el workflow

## TOC

- [13.1 Regla principal](#131-regla-principal)
- [13.2 La auditoria no cambia estados](#132-la-auditoria-no-cambia-estados)
- [13.3 La auditoria no decide](#133-la-auditoria-no-decide)
- [13.4 Actor registrado no equivale a permiso](#134-actor-registrado-no-equivale-a-permiso)
- [13.5 History no equivale a autorizacion](#135-history-no-equivale-a-autorizacion)
- [13.6 Motivos no equivalentes](#136-motivos-no-equivalentes)
- [13.7 Evento no reemplaza estado](#137-evento-no-reemplaza-estado)
- [13.8 Cancelacion por obsolescencia no equivale a rechazo](#138-cancelacion-por-obsolescencia-no-equivale-a-rechazo)
- [13.9 La auditoria no introduce nuevos estados](#139-la-auditoria-no-introduce-nuevos-estados)
- [13.10 Regla corta](#1310-regla-corta)

---

## 13.1 Regla principal

La auditoria estructurada registra hechos del workflow formal.

No gobierna el workflow.

---

## 13.2 La auditoria no cambia estados

La auditoria no puede cambiar el estado de una `SwapRequest`.

Los cambios de estado pertenecen al workflow formal de `swap_service`.

---

## 13.3 La auditoria no decide

La auditoria no puede:

```text
aprobar
rechazar
cancelar
aplicar
evaluar
resolver
```

La auditoria solo registra hechos ocurridos.

---

## 13.4 Actor registrado no equivale a permiso

Registrar un actor en un evento no implica que ese actor tenga permiso formal.

```text
actor registrado != actor autorizado
```

Los permisos, si se incorporan en el futuro, deben definirse en un contrato separado.

---

## 13.5 History no equivale a autorizacion

`history` conserva trazabilidad.

`history` no define permisos, autorizaciones ni roles.

---

## 13.6 Motivos no equivalentes

No deben mezclarse:

```text
motivo_creacion
motivo_evaluacion
motivo_resolucion
motivo_cancelacion
motivo_obsolescencia
motivo_aplicacion
```

Cada motivo pertenece al evento o etapa correspondiente.

---

## 13.7 Evento no reemplaza estado

La existencia de un evento auditable no reemplaza el estado formal de la request.

Ejemplo:

```text
REQUEST_APLICADA
```

no debe usarse como sustituto de:

```text
estado = APLICADO
```

El estado formal sigue siendo la fuente de verdad del workflow.

---

## 13.8 Cancelacion por obsolescencia no equivale a rechazo

Una cancelacion por obsolescencia de roster no equivale a rechazo operativo.

Debe quedar distinguida en motivo, history o evento auditable.

---

## 13.9 La auditoria no introduce nuevos estados

La auditoria estructurada no puede introducir estados nuevos de `SwapRequest`.

No agrega:

```text
PROPUESTO
ACEPTADO_POR_CONTRAPARTE
PENDIENTE_SUPERVISOR
OBSOLETO
```

Cualquier nuevo estado requiere decision arquitectonica separada.

---

## 13.10 Regla corta

La auditoria observa el workflow; no lo reemplaza.

---

# Invariante 14 - El importador normaliza datos reales, no evalua ni decide

## TOC

- [14.1 Regla principal](#141-regla-principal)
- [14.2 El importador no evalua swaps](#142-el-importador-no-evalua-swaps)
- [14.3 El importador no decide workflow](#143-el-importador-no-decide-workflow)
- [14.4 El importador no aplica](#144-el-importador-no-aplica)
- [14.5 Celda vacia es franco](#145-celda-vacia-es-franco)
- [14.6 A/B/C son turnos operativos](#146-abc-son-turnos-operativos)
- [14.7 Codigos no operativos no entran al motor en V1](#147-codigos-no-operativos-no-entran-al-motor-en-v1)
- [14.8 El importador no infiere puestos ni supervisores](#148-el-importador-no-infiere-puestos-ni-supervisores)
- [14.9 roster_store no parsea](#149-rosterstore-no-parsea)
- [14.10 RosterVersion se crea explicitamente](#1410-rosterversion-se-crea-explicitamente)
- [14.11 Regla corta](#1411-regla-corta)

---

## 14.1 Regla principal

El importador normaliza datos reales de roster.

No evalua swaps.

No decide workflow.

No aplica cambios operativos.

---

## 14.2 El importador no evalua swaps

El importador no puede llamar a:

```text
simulator
```

Tampoco puede clasificar tecnicamente swaps.

---

## 14.3 El importador no decide workflow

El importador no puede:

```text
aprobar
rechazar
cancelar
resolver
crear decision_sugerida
```

El workflow formal sigue perteneciendo a `swap_service`.

---

## 14.4 El importador no aplica

El importador no puede ejecutar swaps ni modificar requests existentes.

La aplicacion sigue perteneciendo a:

```text
swap_service.aplicar_swap_request
```

---

## 14.5 Celda vacia es franco

Una celda vacia representa franco.

No genera `Asignacion` operativa.

---

## 14.6 A/B/C son turnos operativos

Los codigos:

```text
A
B
C
```

representan turnos operativos y generan `Asignacion`.

---

## 14.7 Codigos no operativos no entran al motor en V1

Codigos como:

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

no deben generar `Asignacion` operativa en V1.

Deben quedar como eventos no operativos, warnings o informacion auxiliar de importacion.

---

## 14.8 El importador no infiere puestos ni supervisores

El importador no debe inferir:

```text
TMA
SUR
NORTE
SUPERVISOR
INSTRUCTOR
```

si esos datos no estan explicitamente presentes.

La posicion de una fila no debe usarse como regla general para determinar rol.

---

## 14.9 roster_store no parsea

`roster_store` no debe interpretar CSV, Excel ni matrices humanas.

Su responsabilidad es persistir y versionar rosters ya normalizados.

---

## 14.10 RosterVersion se crea explicitamente

Leer o parsear una matriz no debe crear una `RosterVersion` automaticamente de manera implicita.

La creacion de `RosterVersion` desde una importacion debe ser una accion explicita posterior a la validacion.

---

## 14.11 Regla corta

El importador prepara datos; el motor tecnico valida reglas; el workflow formal decide y ejecuta.

---

# Invariante 15 - El codigo del roster no alcanza para determinar elegibilidad

## TOC

- [15.1 Regla principal](#151-regla-principal)
- [15.2 A/B/C son necesarios pero no suficientes](#152-abc-son-necesarios-pero-no-suficientes)
- [15.3 Persona no operativa no participa](#153-persona-no-operativa-no-participa)
- [15.4 CMA vencido bloquea operatividad general](#154-cma-vencido-bloquea-operatividad-general)
- [15.5 Override administrativo negativo bloquea operatividad general](#155-override-administrativo-negativo-bloquea-operatividad-general)
- [15.6 Override administrativo requiere trazabilidad](#156-override-administrativo-requiere-trazabilidad)
- [15.7 Habilitacion TMA limita puesto, no operatividad general](#157-habilitacion-tma-limita-puesto-no-operatividad-general)
- [15.8 Sin puesto definido no se aplica filtro TMA en V1](#158-sin-puesto-definido-no-se-aplica-filtro-tma-en-v1)
- [15.9 Eventos no operativos no generan swaps](#159-eventos-no-operativos-no-generan-swaps)
- [15.10 La ausencia de OF no implica disponibilidad](#1510-la-ausencia-de-of-no-implica-disponibilidad)
- [15.11 El importador no decide elegibilidad compleja](#1511-el-importador-no-decide-elegibilidad-compleja)
- [15.12 Regla corta](#1512-regla-corta)

---

## 15.1 Regla principal

El codigo del roster no alcanza para determinar elegibilidad para swaps normales.

La elegibilidad depende del conjunto:

```text
persona
estado operativo general
asignacion/evento
configuracion de dependencia
puesto, si existe
```

---

## 15.2 A/B/C son necesarios pero no suficientes

Los codigos:

```text
A
B
C
```

representan turnos operativos activos para el contexto actual.

Pero no bastan por si solos para habilitar un swap.

La persona tambien debe estar operativa y pertenecer al universo operativo intercambiable.

---

## 15.3 Persona no operativa no participa

Si:

```text
estado_operativo_general = false
```

entonces la persona no participa en swaps operativos normales.

Esto aplica aunque tenga una asignacion `A`, `B` o `C`.

---

## 15.4 CMA vencido bloquea operatividad general

Regla conceptual:

```text
si fecha_vencimiento_cma <= fecha_actual
entonces estado_operativo_general = false
```

Un CMA / psicofisico vencido hace caer la operatividad general.

---

## 15.5 Override administrativo negativo bloquea operatividad general

Regla conceptual:

```text
si cma_override_operativo = false
entonces estado_operativo_general = false
```

Un override administrativo negativo bloquea la participacion de la persona en swaps operativos normales.

---

## 15.6 Override administrativo requiere trazabilidad

Todo override administrativo debe registrar:

```text
actor
motivo
fecha
```

No debe existir override administrativo valido sin trazabilidad minima.

---

## 15.7 Habilitacion TMA limita puesto, no operatividad general

No tener habilitacion TMA no vuelve necesariamente no operativa a la persona.

Limita su elegibilidad para puestos TMA si el puesto esta definido.

La persona puede seguir siendo elegible para otros puestos compatibles.

---

## 15.8 Sin puesto definido no se aplica filtro TMA en V1

Si el roster no define puestos, el sistema no debe inferirlos.

Regla V1:

```text
puesto no definido -> no aplicar filtro TMA
```

La compatibilidad por puesto queda reservada para V2.

---

## 15.9 Eventos no operativos no generan swaps

Eventos como:

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

no generan swaps normales.

Deben conservarse fuera de `Asignacion` operativa.

---

## 15.10 La ausencia de OF no implica disponibilidad

Que una persona no tenga `OF` en un dia determinado no implica automaticamente que este disponible para swaps.

La disponibilidad requiere perfil operativo y estado operativo general compatible.

---

## 15.11 El importador no decide elegibilidad compleja

El importador normaliza y separa datos.

No decide elegibilidad funcional compleja.

No evalua swaps.

No infiere puestos.

No infiere roles.

---

## 15.12 Regla corta

El evento del roster informa que hay asignado; no decide por si solo si puede intercambiarse.

---

# Invariante 16 - El catalogo oficial no implica activacion local

## TOC

- [16.1 Regla principal](#161-regla-principal)
- [16.2 Codigo conocido no equivale a codigo activo](#162-codigo-conocido-no-equivale-a-codigo-activo)
- [16.3 Solo codigos operativos activos generan Asignacion](#163-solo-codigos-operativos-activos-generan-asignacion)
- [16.4 Codigos no operativos quedan fuera de Asignacion](#164-codigos-no-operativos-quedan-fuera-de-asignacion)
- [16.5 Codigos legacy requieren normalizacion explicita](#165-codigos-legacy-requieren-normalizacion-explicita)
- [16.6 Codigos fuera de alcance no se aceptan silenciosamente](#166-codigos-fuera-de-alcance-no-se-aceptan-silenciosamente)
- [16.7 La configuracion no evalua swaps](#167-la-configuracion-no-evalua-swaps)
- [16.8 La configuracion no decide workflow](#168-la-configuracion-no-decide-workflow)
- [16.9 Importacion y reglas tecnicas permanecen separadas](#169-importacion-y-reglas-tecnicas-permanecen-separadas)
- [16.10 Regla corta](#1610-regla-corta)

---

## 16.1 Regla principal

Que un codigo exista en el PR o en el catalogo documental no significa que este activo para una dependencia determinada.

La activacion depende de configuracion.

---

## 16.2 Codigo conocido no equivale a codigo activo

Un codigo puede ser:

```text
conocido
oficial
legacy
fuera de alcance
desactivado
no operativo
```

sin ser operativo activo.

---

## 16.3 Solo codigos operativos activos generan Asignacion

En V1, solo los codigos clasificados como:

```text
OPERATIVO_ACTIVO
```

pueden generar `Asignacion` operativa.

Para el contexto actual ACC:

```text
A
B
C
```

---

## 16.4 Codigos no operativos quedan fuera de Asignacion

Codigos como:

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

no generan `Asignacion` operativa.

Deben conservarse como eventos no operativos o informacion auxiliar de importacion.

---

## 16.5 Codigos legacy requieren normalizacion explicita

Los codigos legacy no deben aceptarse silenciosamente.

Normalizaciones vigentes:

```text
IN -> EN
REM -> RTA
RET -> RTB
```

La normalizacion debe ser explicita y trazable.

---

## 16.6 Codigos fuera de alcance no se aceptan silenciosamente

Codigos oficiales pero fuera de alcance de una dependencia no deben aceptarse silenciosamente.

Para ACC actual:

```text
AE
AEC
```

quedan fuera de alcance.

En otra dependencia no H24 podrian ser validos si la configuracion los habilita.

---

## 16.7 La configuracion no evalua swaps

La configuracion de codigos no puede evaluar swaps.

No llama a:

```text
engine
scoring
simulator
```

---

## 16.8 La configuracion no decide workflow

La configuracion de codigos no puede:

```text
crear request
evaluar request
resolver request
aprobar request
rechazar request
cancelar request
aplicar request
```

El workflow formal sigue perteneciendo a `swap_service`.

---

## 16.9 Importacion y reglas tecnicas permanecen separadas

La configuracion de importacion no debe mezclarse con las reglas tecnicas del motor.

No son equivalentes:

```text
codigo desconocido
```

y:

```text
descanso minimo incumplido
```

---

## 16.10 Regla corta

Un codigo oficial puede existir sin estar activo para una dependencia.

---

# Invariante 17 - Persona operativa no equivale a rol institucional

## TOC

- [17.1 Regla principal](#171-regla-principal)
- [17.2 Rol institucional no define elegibilidad](#172-rol-institucional-no-define-elegibilidad)
- [17.3 Estado operativo general bloquea swaps](#173-estado-operativo-general-bloquea-swaps)
- [17.4 CMA vencido bloquea operatividad](#174-cma-vencido-bloquea-operatividad)
- [17.5 Override administrativo negativo bloquea operatividad](#175-override-administrativo-negativo-bloquea-operatividad)
- [17.6 Override requiere trazabilidad](#176-override-requiere-trazabilidad)
- [17.7 Habilitacion limita compatibilidad](#177-habilitacion-limita-compatibilidad)
- [17.8 Sin puesto definido no se aplica filtro TMA](#178-sin-puesto-definido-no-se-aplica-filtro-tma)
- [17.9 El importador no calcula perfil operativo](#179-el-importador-no-calcula-perfil-operativo)
- [17.10 Regla corta](#1710-regla-corta)

---

## 17.1 Regla principal

El rol institucional de una persona no equivale a su elegibilidad para swaps normales.

La elegibilidad depende del perfil operativo, estado operativo general, asignacion y contexto.

---

## 17.2 Rol institucional no define elegibilidad

No debe inferirse elegibilidad solo por rol.

Ejemplos:

```text
Supervisor en puesto operativo -> puede intercambiar como controlador.
Instructor en A/B/C -> elegible igual que controlador.
Adscripto -> administrativo, no participa en swaps normales.
Practicante -> OJT/SIM, no participa en swaps normales.
```

---

## 17.3 Estado operativo general bloquea swaps

Si:

```text
estado_operativo_general = false
```

entonces la persona no participa en swaps operativos normales.

Esto aplica aunque el roster tenga:

```text
A
B
C
```

---

## 17.4 CMA vencido bloquea operatividad

Regla conceptual:

```text
si fecha_vencimiento_cma <= fecha_actual
entonces estado_operativo_general = false
```

El CMA / psicofisico vencido bloquea la operatividad general.

---

## 17.5 Override administrativo negativo bloquea operatividad

Regla conceptual:

```text
si cma_override_operativo = false
entonces estado_operativo_general = false
```

Un override administrativo negativo bloquea la participacion en swaps normales.

---

## 17.6 Override requiere trazabilidad

Todo override administrativo debe tener:

```text
actor
motivo
fecha
```

No debe existir override administrativo valido sin trazabilidad minima.

---

## 17.7 Habilitacion limita compatibilidad

La falta de una habilitacion especifica no vuelve necesariamente no operativa a la persona completa.

Puede limitar compatibilidad por puesto.

Ejemplo:

```text
habilitado_tma = false
puesto = TMA
-> no compatible
```

---

## 17.8 Sin puesto definido no se aplica filtro TMA

Si el roster no define puestos, el sistema no debe inferirlos.

Regla V1:

```text
puesto no definido -> no aplicar filtro TMA
```

La compatibilidad por puesto queda reservada para V2.

---

## 17.9 El importador no calcula perfil operativo

El importador de roster no calcula:

```text
estado_operativo_general
CMA
override administrativo
habilitaciones
compatibilidad por puesto
```

El importador normaliza roster y separa asignaciones operativas de eventos no operativos.

---

## 17.10 Regla corta

El rol describe la funcion; el perfil operativo define si y donde puede operar.