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
  - [6.1 Clasificacion tecnica](#61-clasificacion-tecnica)
  - [6.2 Decision sugerida](#62-decision-sugerida)
  - [6.3 Resolucion operativa](#63-resolucion-operativa)
  - [6.4 Aplicacion](#64-aplicacion)
  - [6.5 Motivos del workflow](#65-motivos-del-workflow)
- [7. Semantica de versiones](#7-semantica-de-versiones)
  - [7.1 Version vigente](#71-version-vigente)
  - [7.2 Version evaluable](#72-version-evaluable)
  - [7.3 Version aplicable](#73-version-aplicable)
  - [Regla unificada](#regla-unificada)
  - [Obsolescencia](#obsolescencia)
- [8. Identidad del objeto del swap](#8-identidad-del-objeto-del-swap)
  - [Semantica del intercambio](#semantica-del-intercambio)
- [9. Separacion conceptual](#9-separacion-conceptual)
  - [Evaluacion tecnica](#evaluacion-tecnica)
  - [Evaluacion formal](#evaluacion-formal)
  - [Resolucion operativa](#resolucion-operativa)
  - [Aplicacion](#aplicacion)
- [10. Reglas del dominio](#10-reglas-del-dominio)
- [11. Proposito del modelo](#11-proposito-del-modelo)
- [Nota de frontera con simulacion](#nota-de-frontera-con-simulacion)
- [Nota de estados, resolucion y aplicacion](#nota-de-estados-resolucion-y-aplicacion)
- [12. Frontera futura de roster real, perfil operativo y elegibilidad](#12-frontera-futura-de-roster-real-perfil-operativo-y-elegibilidad)
  - [12.1 Estado](#121-estado)
  - [12.2 Contexto](#122-contexto)
  - [12.3 Conceptos reconocidos](#123-conceptos-reconocidos)
  - [12.4 Modelo actual preservado](#124-modelo-actual-preservado)
  - [12.5 Elegibilidad funcional](#125-elegibilidad-funcional)
  - [12.6 Estado operativo general](#126-estado-operativo-general)
  - [12.7 Habilitaciones](#127-habilitaciones)
  - [12.8 Configuracion por dependencia](#128-configuracion-por-dependencia)
  - [12.9 Fronteras preservadas](#129-fronteras-preservadas)
  - [12.10 Decision de alcance](#1210-decision-de-alcance)
  - [12.11 Regla corta](#1211-regla-corta)
- [Timeline diaria importada](#timeline-diaria-importada)
  - [Descripcion](#descripcion)
  - [Entidad conceptual](#entidad-conceptual)
  - [Estados posibles](#estados-posibles)
  - [OPERATIVO](#operativo)
  - [LIBRE](#libre)
  - [NO_OPERATIVO_DOCUMENTADO](#no_operativo_documentado)
  - [OPERATIVO_CONFIGURABLE_NO_ACTIVO](#operativo_configurable_no_activo)
  - [FUERA_DE_ALCANCE](#fuera_de_alcance)
  - [DESCONOCIDO](#desconocido)
  - [Relacion con Asignacion](#relacion-con-asignacion)
  - [Relacion con diagnostico calendar-aware](#relacion-con-diagnostico-calendar-aware)
- [Objetos de reporte y carga calendar-aware](#objetos-de-reporte-y-carga-calendar-aware)
  - [ReporteOperativoCalendarAware](#reporteoperativocalendaraware)
  - [EntradaCargaRosterMes y DiagnosticoCargaRosterMes](#entradacargarostermes-y-diagnosticocargarostermes)
  - [DiagnosticoCargaMultiMesCalendarAware](#diagnosticocargamultimescalendaraware)

---

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

La auditoria se expresa mediante `history`, pero el `actor` registrado en un evento no define por si mismo permisos formales ni autorizacion operativa.

#### Componentes conceptuales

**A. Intencion**
- qué asignaciones se desean intercambiar
- a qué versión del roster pertenece

**B. Evaluacion tecnica**
- clasificación técnica del swap

**C. Evaluacion formal**
- `decision_sugerida` del sistema (VIABLE / OBSERVAR / RECHAZAR)
- motivo de evaluacion cuando corresponda

**D. Resolucion operativa**
- accion explicita posterior a la evaluacion formal
- destino de workflow: APROBADO / RECHAZADO / CANCELADO
- motivo_resolucion cuando corresponda

**E. Aplicacion**
- ejecucion del swap aprobado sobre roster versionado
- generacion de una nueva RosterVersion

**F. Workflow**
- estado del request
- historial de eventos
- actor registrado en eventos de trazabilidad

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

- PENDIENTE -> request creada pero aun no evaluada formalmente.
- EVALUADO -> request evaluada formalmente. Informa resultado y `decision_sugerida`, pero no aprueba, rechaza terminalmente, cancela ni aplica.
- APROBADO -> request resuelta favorablemente mediante accion explicita. No significa APLICADO.
- RECHAZADO -> request resuelta desfavorablemente mediante accion explicita.
- CANCELADO -> request cerrada sin aplicacion. Puede responder a cancelacion operativa u obsolescencia.
- APLICADO -> request aprobada cuyo swap fue ejecutado sobre una nueva version de roster.

#### Aclaracion de planos

El SwapRequest actúa como entidad agregadora de:

- evaluacion tecnica
- evaluacion formal con `decision_sugerida`
- resolucion operativa explicita
- aplicacion
- estado del workflow

Estos planos permanecen conceptualmente separados y no deben colapsarse.

En particular:

- `VIABLE` no significa `APROBADO`;
- `APROBADO` no significa `APLICADO`;
- cancelacion por obsolescencia no equivale a rechazo operativo.

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

Unidad operativa del roster que asigna un controlador a un turno operativo en una fecha específica dentro de una versión.

#### Naturaleza

Entidad de dominio base.

#### Componentes

* controlador
* fecha
* turno operativo

#### Identidad

Una Asignacion existe dentro de una RosterVersion.

Su identidad está dada por:

* la versión a la que pertenece
* su contenido operativo

El contenido operativo incluye, al menos:

* controlador
* fecha
* turno operativo

Y puede extenderse con otros atributos operativos relevantes si el roster los define explicitamente, por ejemplo:

* posición
* sector
* puesto
* rol operativo contextual

#### Propiedad clave

Una asignación no es una posición en una lista, sino una unidad operativa del sistema.

#### Frontera con eventos no operativos

No todo codigo de roster genera una Asignacion operativa.

Codigos no operativos, administrativos, de ausencia, capacitacion, comision, gestion, psicofisico o practica deben conservarse fuera de `Asignacion` operativa en V1.

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

Estos eventos pueden conservarse para trazabilidad de importacion, pero no participan como turnos operativos en `candidate_generation`, `engine`, `scoring` ni `simulator`.

---

### 4.4 Controlador

#### Definicion

Entidad que representa a un controlador de tránsito aéreo.

#### Rol

Participa en asignaciones dentro del roster.

---

### 4.5 Turno

#### Definicion

Tipo de turno operativo asignado en una fecha.

#### Ejemplos operativos actuales

Para el contexto actual ACC:

* A
* B
* C

#### Codigos operativos configurables

Existen codigos oficiales que podrian ser operativos si la configuracion de dependencia los habilita:

* D
* X

#### Frontera conceptual

No todo codigo de roster es un Turno operativo.

Codigos de licencia, ausencia, capacitacion, comision, gestion, psicofisico, practica o eventos administrativos no deben confundirse con `Turno` operativo en V1.

Ejemplos de codigos que no son Turno operativo en V1:

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
AE
AEC
REM
RET
```

Algunos codigos pueden normalizarse durante la importacion:

```text
IN -> EN
REM -> RTA
RET -> RTB
```


#### Representacion implementada y conciliacion v115

`src/models.py` define Turno como dataclass frozen con codigo, hora_inicio,
duracion_horas, categoria, es_nocturno y habilitado. No restringe por si sola
los codigos ni valida elegibilidad funcional.

El importador ACC crea asignaciones con el esquema de ocho horas A/B/C.
Entrenamiento no es un ejemplo de Turno operativo en esa ruta: OJT, SIM y EN
se conservan como eventos no operativos. El ejemplo contradictorio anterior se
retira de la definicion vigente y permanece recuperable en el tag v114.
D/X requieren tanto una configuracion adecuada como un esquema compatible;
marcarlos activos no agrega automaticamente esos turnos al esquema 8H.

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
  Cada asignacion operativa referencia un Turno; los eventos no operativos
  importados se representan separadamente.

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

### 6.2 Decision sugerida

Resultado operativo sugerido durante la evaluacion formal del request.

Valores:

- VIABLE
- OBSERVAR
- RECHAZAR

Puede diferir de la clasificación técnica.

No equivale a estado del workflow.

En particular:

- VIABLE no significa APROBADO.
- RECHAZAR no significa RECHAZADO terminal.

---

### 6.3 Resolucion operativa

Accion explicita posterior a la evaluacion formal.

Puede llevar una request EVALUADO a:

- APROBADO
- RECHAZADO
- CANCELADO

La resolucion no reevalua, no reclasifica y no aplica.

---

### 6.4 Aplicacion

Ejecucion de una request previamente APROBADO sobre roster versionado.

La aplicacion:

- ejecuta el intercambio real;
- crea una nueva RosterVersion;
- deja la request en estado APLICADO;
- no reevalua;
- no resuelve;
- no decide nuevamente.

---

### 6.5 Motivos del workflow

Los motivos deben conservar su significado segun la etapa del workflow.

- motivo de creacion -> explica por que nace una request.
- motivo de evaluacion -> explica restricciones o advertencias detectadas durante evaluacion formal.
- motivo_resolucion -> explica la accion explicita de resolver.
- motivo de obsolescencia -> explica cierre por cambio de version, sin convertirlo en rechazo operativo.

---

## 7. Semantica de versiones

### 7.1 Version vigente

Versión actual del roster utilizada por el sistema.

### 7.2 Version evaluable

Versión sobre la cual se evalúa un request.

### 7.3 Version aplicable

Versión sobre la cual puede ejecutarse un swap.

### Regla unificada

Un request es evaluable y aplicable dentro del flujo si su versión coincide con la versión vigente.

### Obsolescencia

Un request se vuelve obsoleto cuando su versión deja de ser vigente.

La obsolescencia puede provocar cancelacion del workflow, pero no equivale conceptualmente a rechazo operativo.

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

El sistema separa cuatro planos:

### Evaluacion tecnica

Describe el impacto del swap.

### Evaluacion formal

Describe el tratamiento sugerido del request y produce `decision_sugerida`.

### Resolucion operativa

Decide explicitamente el destino del request evaluado.

### Aplicacion

Describe el cambio real sobre el roster.

Ver separación operativa implementada en:  
[Ref: contratos.md #16]

y decisiones arquitectónicas en:  
[Ref: decisiones.md]

---

## 10. Reglas del dominio

- todo request pertenece a una única versión
- evaluar informa
- resolver decide explicitamente
- aplicar ejecuta
- no se evalúan requests sobre versiones no vigentes
- no se aplican swaps sobre versiones no vigentes
- solo una request APROBADO puede aplicarse
- APROBADO no significa APLICADO
- VIABLE no significa APROBADO
- toda aplicación genera una nueva versión
- la versión previa permanece inmutable
- los requests de versiones no vigentes se vuelven obsoletos
- cancelacion por obsolescencia no equivale a rechazo operativo

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

## Nota de estados, resolucion y aplicacion

- EVALUADO significa que la request fue evaluada formalmente.
- VIABLE es una `decision_sugerida`; no aprueba por si misma.
- APROBADO es un estado posterior a una resolucion operativa favorable y explicita.
- APROBADO no significa APLICADO.
- APLICADO significa que el swap aprobado fue ejecutado sobre roster versionado.
- CANCELADO por obsolescencia no significa RECHAZADO operativo.

---

## 12. Frontera futura de roster real, perfil operativo y elegibilidad

### 12.1 Estado

Conceptual / no implementado todavia.

Esta seccion describe conceptos de dominio identificados durante el analisis de roster real, codigos oficiales de listas de turno y elegibilidad funcional para swaps normales.

No implica cambios inmediatos en `models.py`.

No introduce entidades persistidas nuevas.

No modifica el workflow formal de `SwapRequest`.

---

### 12.2 Contexto

El sistema opera actualmente sobre asignaciones operativas normalizadas.

El workflow formal vigente se mantiene:

```text
PENDIENTE
-> EVALUADO
-> APROBADO / RECHAZADO / CANCELADO
-> APLICADO
```

La importacion de roster real incorpora una nueva frontera conceptual:

```text
matriz real
-> normalizacion
-> asignaciones operativas
-> eventos no operativos
-> roster versionado
```

A partir del analisis documental y operativo se identifica que la elegibilidad para swaps normales no depende solamente del codigo del roster.

---

### 12.3 Conceptos reconocidos

Se reconocen como conceptos de dominio futuros:

```text
catalogo oficial de codigos
configuracion por dependencia
codigo operativo activo
codigo operativo configurable
codigo no operativo
codigo legacy
codigo fuera de alcance
evento no operativo
perfil operativo para swaps
universo operativo intercambiable
estado operativo general
CMA / psicofisico
override administrativo CMA
habilitacion RADAR
habilitacion TMA
compatibilidad por puesto
elegibilidad funcional para swap
```

Estos conceptos se documentan para preservar semantica, pero no se implementan todavia como clases, enums, tablas ni servicios nuevos.

---

### 12.4 Modelo actual preservado

El modelo actual conserva como entidades principales:

```text
Controlador
Turno
Asignacion
RosterVersion
SwapRequest
```

La `Asignacion` representa un turno operativo interno.

Los eventos no operativos no deben confundirse con `Asignacion` operativa.

Ejemplos de eventos no operativos:

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

Estos eventos pueden conservarse para trazabilidad de importacion, pero no participan como turnos operativos en `candidate_generation`, `engine`, `scoring` ni `simulator`.

---

### 12.5 Elegibilidad funcional

La elegibilidad para swap normal se reconoce como una evaluacion funcional del conjunto:

```text
persona
estado operativo general
asignacion/evento
configuracion de dependencia
puesto, si existe
habilitaciones, si corresponde
```

Regla conceptual:

```text
El codigo del roster describe el evento; la elegibilidad para swap se determina por persona, aptitud, asignacion y contexto.
```

Para V1, el sistema mantiene la frontera simple:

```text
candidate_generation opera sobre asignaciones operativas normalizadas.
eventos no operativos quedan fuera de asignaciones swappeables.
si el puesto no esta definido, no se aplica filtro TMA.
```

---

### 12.6 Estado operativo general

El estado operativo general indica si una persona puede operar en terminos generales.

Reglas conceptuales futuras:

```text
si fecha_vencimiento_cma <= fecha_actual
entonces estado_operativo_general = false
```

y:

```text
si cma_override_operativo = false
entonces estado_operativo_general = false
```

Todo override administrativo CMA debe tener trazabilidad minima:

```text
actor
motivo
fecha
```

Estas reglas no se implementan todavia.

---

### 12.7 Habilitaciones

Se reconocen conceptualmente:

```text
RADAR
TMA
```

No se incorporan en esta etapa habilitaciones `SUR` ni `NORTE`.

La falta de habilitacion TMA no vuelve necesariamente no operativa a la persona.

Limita la compatibilidad con puestos TMA si el puesto esta definido.

Si el roster no define puestos, en V1 no se aplica filtro TMA.

---

### 12.8 Configuracion por dependencia

La configuracion por dependencia permite interpretar codigos de roster segun el contexto operativo.

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

El catalogo oficial de codigos no implica activacion local.

---

### 12.9 Fronteras preservadas

El importador:

```text
normaliza codigos
separa asignaciones operativas de eventos no operativos
emite warnings/errores
conserva trazabilidad de importacion
```

El importador no:

```text
evalua swaps
decide workflow
infiere puestos
infiere roles
calcula elegibilidad compleja
llama simulator
crea requests
resuelve requests
aplica requests
```

El `engine` sigue validando reglas tecnicas sobre asignaciones operativas ya normalizadas.

`technical_prefilter` queda reconocido como posible frontera futura para elegibilidad fina, pero no se implementa todavia.

---

### 12.10 Decision de alcance

No se agregan todavia al modelo implementado:

```text
PersonaProfile
EligibilityService
PerfilDependencia
EventoRoster formal
tabla de CMA
habilitaciones persistidas
compatibilidad por puesto
motor RAAC 67
```

Esta seccion solo fija el lenguaje de dominio para futuras decisiones.

---

### 12.11 Regla corta

El modelo actual se mantiene; la elegibilidad funcional queda documentada como frontera futura de dominio.

---

## Timeline diaria importada

### Descripcion

La timeline diaria importada representa cada dia calendario del roster mensual para cada controlador.

Su objetivo es conservar contexto calendario que no existe cuando solo se observan asignaciones operativas.

La timeline diaria permite diferenciar:

```text
turno operativo
dia libre
evento no operativo documentado
codigo configurable no activo
codigo fuera de alcance
codigo desconocido
```

---

### Entidad conceptual

La entidad conceptual es:

```text
RosterDiaImportado
```

Campos principales:

```text
controlador
fecha
estado
raw_value
codigo
codigo_normalizado
```

---

### Estados posibles

Los estados diarios son:

```text
OPERATIVO
LIBRE
NO_OPERATIVO_DOCUMENTADO
OPERATIVO_CONFIGURABLE_NO_ACTIVO
FUERA_DE_ALCANCE
DESCONOCIDO
```

---

### OPERATIVO

Representa una celda del roster que genera asignacion operativa.

En el contexto ACC actual, los codigos operativos activos son:

```text
A
B
C
```

---

### LIBRE

Representa una celda vacia del roster.

Equivale a dia sin asignacion.

Puede contar para warnings de libres consecutivos.

No equivale a licencia, capacitacion, psicofisico ni otro evento documentado.

---

### NO_OPERATIVO_DOCUMENTADO

Representa un codigo explicito del roster que no genera asignacion operativa.

Ejemplos:

```text
LA
LD
EN
PSI
RTA
RTB
OJT
SIM
CAM
```

Estos eventos se conservan por valor documental y auditable.

No entran al motor tecnico como turnos operativos.

No cuentan como dias libres.

---

### OPERATIVO_CONFIGURABLE_NO_ACTIVO

Representa un codigo operativo posible o configurable, pero no activo en la configuracion actual.

Ejemplos conceptuales:

```text
D
X
```

No debe tratarse como asignacion operativa activa mientras la configuracion no lo habilite.

---

### FUERA_DE_ALCANCE

Representa un codigo conocido pero fuera del alcance operativo actual.

Ejemplos conceptuales:

```text
AE
AEC
```

No implica que el codigo sea invalido globalmente.

Implica que no aplica al contexto ACC actual.

---

### DESCONOCIDO

Representa un valor no reconocido por el catalogo o la configuracion vigente.

Su tratamiento depende del modo de importacion y de la politica strict/permisiva.

---

### Relacion con Asignacion

`RosterDiaImportado` no reemplaza a `Asignacion`.

Los dias `OPERATIVO` pueden generar asignaciones operativas.

Los dias `LIBRE`, `NO_OPERATIVO_DOCUMENTADO`, `OPERATIVO_CONFIGURABLE_NO_ACTIVO`, `FUERA_DE_ALCANCE` y `DESCONOCIDO` no deben ser tratados automaticamente como asignaciones operativas.

---

### Relacion con diagnostico calendar-aware

La timeline diaria importada es la entrada principal para diagnosticos calendar-aware.

Permite validar reglas dependientes del calendario completo sin perder:

```text
dias libres
cortes calendario
eventos documentados
huecos reales entre turnos
```

---

---

## Objetos de reporte y carga calendar-aware

### ReporteOperativoCalendarAware

Dataclass frozen de `src/roster_calendar_aware_report.py`: mensaje, estado_general,
total_dias_importados, total_violaciones, total_hard, total_soft, valido_sin_hard,
codigos_principales, detalles y metadata. `to_dict()` expone datos serializables.
Sus estados generales no son estados de SwapRequest.

### EntradaCargaRosterMes y DiagnosticoCargaRosterMes

La entrada identifica anio, mes, ruta CSV y formato. El diagnostico conserva
fuente, disponibilidad, motivo de omision, conteos de importacion, posibilidad de
crear version, conteos calendar-aware y reporte opcional. No es una RosterVersion.

### DiagnosticoCargaMultiMesCalendarAware

Contiene una tupla de resultados mensuales y propiedades de agregacion. No es
una timeline unificada ni demuestra continuidad entre meses. El atributo
apto_para_revision_carga no representa aprobacion de un cambio de turno.
