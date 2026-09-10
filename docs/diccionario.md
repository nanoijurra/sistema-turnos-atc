# Diccionario semantico del sistema

## Tabla de contenido

- [Subsistemas y capas](#subsistemas-y-capas)
- [Entidades y objetos de dominio](#entidades-y-objetos-de-dominio)
- [Taxonomias](#taxonomias)
  - [Clasificacion tecnica](#clasificacion-tecnica)
  - [Decision operativa](#decision-operativa)
  - [Estados de SwapRequest](#estados-de-swaprequest)
- [Conceptos tecnicos y operativos](#conceptos-tecnicos-y-operativos)
- [Verbos reservados](#verbos-reservados)
  - [Verbos del workflow formal](#verbos-del-workflow-formal)
  - [Verbos permitidos para ofertas](#verbos-permitidos-para-ofertas)
- [Reglas de no confusion](#reglas-de-no-confusion)
- [Fachadas](#fachadas)
- [Frases canonicas](#frases-canonicas)
- [Diccionario - conceptos de roster real, codigos y elegibilidad](#diccionario---conceptos-de-roster-real-codigos-y-elegibilidad)
  - [Catalogo oficial de codigos](#catalogo-oficial-de-codigos)
  - [Codigo de roster](#codigo-de-roster)
  - [Codigo operativo activo](#codigo-operativo-activo)
  - [Codigo operativo configurable](#codigo-operativo-configurable)
  - [Codigo no operativo](#codigo-no-operativo)
  - [Codigo normalizable](#codigo-normalizable)
  - [Codigo legacy](#codigo-legacy)
  - [Codigo fuera de alcance](#codigo-fuera-de-alcance)
  - [Normalizacion de codigo](#normalizacion-de-codigo)
  - [Configuracion por dependencia](#configuracion-por-dependencia)
  - [Perfil de dependencia](#perfil-de-dependencia)
  - [Reglas de importacion](#reglas-de-importacion)
  - [Asignacion operativa](#asignacion-operativa)
  - [Asignacion operativa swappeable](#asignacion-operativa-swappeable)
  - [Evento no operativo](#evento-no-operativo)
  - [Roster importado normalizado](#roster-importado-normalizado)
  - [Roster operativo tecnico](#roster-operativo-tecnico)
  - [RosterImportResult](#rosterimportresult)
  - [Rol institucional](#rol-institucional)
  - [Perfil operativo para swaps](#perfil-operativo-para-swaps)
  - [Universo operativo intercambiable](#universo-operativo-intercambiable)
  - [Estado operativo general](#estado-operativo-general)
  - [CMA / psicofisico](#cma--psicofisico)
  - [Override administrativo CMA](#override-administrativo-cma)
  - [Habilitacion RADAR](#habilitacion-radar)
  - [Habilitacion TMA](#habilitacion-tma)
  - [Compatibilidad por puesto](#compatibilidad-por-puesto)
  - [Puesto no definido](#puesto-no-definido)
  - [Elegibilidad funcional para swap](#elegibilidad-funcional-para-swap)
  - [Elegibilidad por codigo](#elegibilidad-por-codigo)
  - [Elegibilidad por persona](#elegibilidad-por-persona)
  - [Elegibilidad por puesto](#elegibilidad-por-puesto)
  - [candidate_generation](#candidate_generation)
  - [technical_prefilter](#technical_prefilter)
- [Terminos calendar-aware](#terminos-calendar-aware)
  - [calendar-aware](#calendar-aware)
  - [timeline diaria](#timeline-diaria)
  - [dias_importados](#dias_importados)
  - [RosterDiaImportado](#rosterdiaimportado)
  - [RosterDayStatus](#rosterdaystatus)
  - [LIBRE](#libre)
  - [NO_OPERATIVO_DOCUMENTADO](#no_operativo_documentado)
  - [diagnostico calendar-aware](#diagnostico-calendar-aware)
  - [entrypoint paralelo calendar-aware](#entrypoint-paralelo-calendar-aware)
  - [ResultadoDiagnosticoCalendarAware](#resultadodiagnosticocalendaraware)
  - [EXCESO_LIBRES_CONSECUTIVOS](#exceso_libres_consecutivos)

---

Este documento define conceptos y terminos relevantes para mantener coherencia semantica en el sistema de swaps ATC.

Su objetivo es evitar ambiguedades entre capas, responsabilidades, estados, clasificaciones y decisiones.

---

## Subsistemas y capas

- `engine` -> subsistema responsable de ejecutar validaciones de reglas configuradas. Es fuente de verdad tecnica para reglas. No decide operativamente.

- `scoring` -> subsistema responsable de calcular validez tecnica y score tecnico. Separa impacto hard y soft. No decide operativamente.

- `simulator` -> subsistema responsable de simular swaps, comparar escenario antes/despues y producir clasificacion tecnica. Clasifica tecnicamente, pero no decide operativamente.

- `swap_service` -> subsistema responsable del workflow formal de `SwapRequest`: crear, evaluar, resolver y aplicar. Es responsable de decision operativa, estados, persistencia y trazabilidad del workflow. Evalua para informar, resuelve para decidir explicitamente y aplica para ejecutar el cambio sobre roster.

- `roster_index` -> estructura derivada del roster vigente para acceso rapido. No evalua, no clasifica, no decide y no persiste.

- `candidate_generation` -> subsistema responsable de generar candidatos estructurales acotados. No evalua, no clasifica, no decide y no persiste.

- `technical_prefilter` -> subsistema de descarte tecnico local y conservador. No clasifica, no puntua, no decide y no persiste.

- `candidate_selection` -> subsistema de seleccion estructural top-N previa a la simulacion. Reduce universo de candidatos, pero no determina calidad tecnica. No llama `engine`, `scoring` ni `simulator`.

- `exploration_flow` -> flujo tecnico-operativo de exploracion. Combina generacion, prefiltrado, seleccion, simulacion, ranking tecnico y priorizacion historica. Puede evaluar via `simulator`, pero no decide ni persiste.

- `offer_reporting` -> subsistema de salida presentable para UI/reporting. Transforma resultados de exploracion en ofertas presentables. No evalua, no decide y no persiste.

- `offer_service` -> fachada liviana de consulta/oferta. Coordina `exploration_flow` y `offer_reporting`. No gestiona workflow formal de requests.

- `offer_to_request_service` -> frontera arquitectonica que convierte una `OfertaEvaluada` seleccionada en una `SwapRequest` formal. Crea request `PENDIENTE`, adjunta `offer_origin`, no evalua, no decide y no aplica.

- `offer_workflow_service` -> fachada/coordinador de alto nivel para flujos operativos de oferta. Puede generar oferta, seleccionar oferta, crear request formal y persistir explicitamente. No evalua, no decide y no aplica salvo que invoque una fachada especifica de evaluacion formal definida por contrato.

- `semantic_guard` -> subsistema auxiliar de vigilancia semantica del proyecto. Ayuda a detectar drift terminologico, usos ambiguos y violaciones de vocabulario arquitectonico.

---

## Entidades y objetos de dominio

- `SwapRequest` -> solicitud formal de intercambio de turnos. Es la unica entidad con workflow operativo formal.

- `OfertaEvaluada` -> resultado tecnico presentable y seleccionable generado a partir del flujo de exploracion. No es una solicitud formal.

- `OfferReport` -> reporte presentable de ofertas evaluadas. Es salida de reporting, no workflow operativo.

- `offer_origin` -> bloque de origen adjunto a una `SwapRequest` creada desde oferta. Conserva evidencia observada de la oferta seleccionada. No reemplaza evaluacion formal.

- `selection_metadata` -> datos sobre la seleccion de una oferta. Indica como, cuando o por quien se selecciono una oferta. No equivale a aprobacion ni resolucion.

- `selected_by` -> identificador de quien selecciona una oferta. No significa aprobador.

- `selection_reason` -> motivo de seleccion de una oferta. No significa motivo de resolucion operativa.

- `motivo_creacion` -> razon o contexto por el cual se crea una `SwapRequest`. No equivale a motivo de resolucion.

- `motivo_resolucion` -> razon registrada al resolver explicitamente una `SwapRequest`. Pertenece a la accion de resolver y no debe confundirse con motivo de creacion, seleccion de oferta u obsolescencia tecnica.

- `history` -> registro cronologico de eventos relevantes del workflow de una `SwapRequest`. Sirve para trazabilidad, no para definir permisos formales.

- `actor` -> identificador registrado en un evento de `history` para indicar quien ejecuto o disparo una accion. No equivale por si mismo a autorizacion, rol formal ni control de permisos.

- `roster_version_id` -> identificador de version de roster sobre la cual se evalua o crea una request.

- `roster_hash` -> huella tecnica del contenido del roster. Sirve para detectar obsolescencia o inconsistencia entre oferta y roster vigente.

---

## Taxonomias

### Clasificacion tecnica

- `BENEFICIOSO` -> clasificacion tecnica producida por `simulator` cuando el swap mejora el escenario segun criterios tecnicos.

- `ACEPTABLE` -> clasificacion tecnica producida por `simulator` cuando el swap no mejora significativamente, pero resulta tecnicamente admisible.

- `RECHAZABLE` -> clasificacion tecnica producida por `simulator` cuando el swap resulta tecnicamente inconveniente o no admisible segun evaluacion tecnica.

### Decision operativa

- `VIABLE` -> decision operativa sugerida por `swap_service` luego de evaluar formalmente una `SwapRequest`. Indica que puede avanzar a resolucion favorable si un actor la resuelve explicitamente. No significa `APROBADO`.

- `OBSERVAR` -> decision operativa sugerida por `swap_service` cuando corresponde revision o cautela antes de resolver explicitamente.

- `RECHAZAR` -> decision operativa sugerida por `swap_service` cuando la evaluacion formal indica rechazo operativo recomendado. No significa `RECHAZADO` terminal hasta que exista resolucion explicita.

### Estados de SwapRequest

- `PENDIENTE` -> estado inicial de una `SwapRequest` creada pero aun no evaluada formalmente.

- `EVALUADO` -> estado de una `SwapRequest` luego de pasar por evaluacion formal. Informa resultado tecnico-operativo, pero no aprueba, rechaza, cancela ni aplica.

- `APROBADO` -> estado de una `SwapRequest` resuelta favorablemente mediante accion explicita. No significa `APLICADO`.

- `RECHAZADO` -> estado terminal de una `SwapRequest` resuelta desfavorablemente mediante accion explicita.

- `CANCELADO` -> estado terminal de una `SwapRequest` cancelada. Puede responder a decision operativa, obsolescencia o imposibilidad de continuar el flujo. Cancelacion por obsolescencia no equivale a rechazo operativo.

- `APLICADO` -> estado final de una `SwapRequest` aprobada cuyo swap fue ejecutado sobre una nueva version de roster.

---

## Conceptos tecnicos y operativos

- `clasificacion_tecnica` -> resultado tecnico formal producido por `simulator`.

- `clasificacion_observada` -> clasificacion tecnica observada durante la generacion de una oferta y conservada en `offer_origin`. No reemplaza la clasificacion formal posterior.

- `decision_operativa` -> resultado operativo producido por `swap_service`. No debe confundirse con clasificacion tecnica.

- `decision_sugerida` -> decision operativa propuesta por `swap_service` luego de evaluar formalmente una `SwapRequest`.

- `estado_workflow` -> estado formal de una `SwapRequest`. No debe confundirse con clasificacion tecnica ni decision operativa.

- `evaluacion_formal` -> evaluacion de una `SwapRequest` realizada mediante `swap_service.evaluar_swap_request`. Informa resultado tecnico-operativo y deja la request en estado `EVALUADO`; no resuelve ni aplica.

- `resolucion_operativa` -> accion explicita posterior a la evaluacion formal. Decide si una `SwapRequest` pasa a `APROBADO`, `RECHAZADO` o `CANCELADO`. No reevalua y no aplica.

- `aplicacion_formal` -> accion posterior a una resolucion favorable. Ejecuta el swap aprobado sobre roster y deja la request en estado `APLICADO`.

- `evidencia_observada` -> informacion tecnica preservada desde la oferta original. Sirve para trazabilidad, no para reemplazar evaluacion formal.

- `snapshot` -> captura de contexto tecnico u operativo en un momento determinado.

- `obsolescencia` -> condicion en la que una oferta, request o evaluacion deja de corresponder al roster vigente o a la configuracion vigente.

- `divergencia` -> diferencia entre evidencia observada de una oferta y evaluacion formal posterior. No constituye error automatico.

- `ranking_tecnico` -> ordenamiento posterior a la evaluacion tecnica. Ocurre despues de `simulator`.

- `priorizacion_historica` -> reordenamiento soft posterior al ranking tecnico. No modifica clasificacion, score tecnico ni decision operativa.

---

## Verbos reservados

### Verbos del workflow formal

Estos verbos pertenecen al dominio de `SwapRequest` y `swap_service`:

- `crear` -> generar una `SwapRequest` formal.
- `evaluar` -> informar resultado tecnico-operativo de una `SwapRequest`. No decide y no aplica.
- `resolver` -> decidir explicitamente el destino operativo de una `SwapRequest` evaluada.
- `aprobar` -> resolver favorablemente una `SwapRequest`. No aplica el swap.
- `rechazar` -> resolver desfavorablemente una `SwapRequest`.
- `cancelar` -> cerrar una `SwapRequest` sin aplicarla. Si la causa es obsolescencia, no equivale a rechazo operativo.
- `aplicar` -> ejecutar un swap aprobado sobre una nueva version de roster.

No deben usarse para describir workflow propio de ofertas.

### Verbos permitidos para ofertas

Estos verbos pueden usarse para ofertas:

- `generar`
- `presentar`
- `seleccionar`
- `descartar`
- `convertir_en_request`
- `crear_request_desde_oferta`

La oferta no se aprueba, no se rechaza, no se aplica y no se resuelve.

---

## Reglas de no confusion

- Una `OfertaEvaluada` no es una `SwapRequest`.

- `offer_origin` no es evaluacion formal.

- `clasificacion_observada` no es clasificacion formal.

- `selected_by` no es aprobador.

- `selection_reason` no es motivo de resolucion.

- `motivo_creacion` no es `motivo_resolucion`.

- `actor` registrado en `history` no equivale a permisos formales.

- `candidate_selection` no reemplaza a `simulator`.

- `priorizacion_historica` no modifica clasificacion tecnica.

- `decision_operativa` no es clasificacion tecnica.

- `decision_sugerida` no es estado del workflow.

- `estado_workflow` no es decision operativa.

- `VIABLE` no significa `APROBADO`.

- `RECHAZAR` como decision sugerida no significa `RECHAZADO` terminal.

- `APROBADO` no significa `BENEFICIOSO`.

- `APROBADO` no significa `APLICADO`.

- `BENEFICIOSO` no implica aprobacion automatica.

- `EVALUADO` no implica aprobado.

- `APLICADO` no implica reevaluacion.

- Cancelacion por obsolescencia no equivale a rechazo operativo.

---

## Fachadas

- `crear_request_desde_oferta_y_evaluar_formalmente` -> fachada de alto nivel que crea una `SwapRequest` formal desde una oferta seleccionada y luego invoca evaluacion formal mediante `swap_service.evaluar_swap_request`. No aprueba, no rechaza, no cancela y no aplica.

---

## Frases canonicas

- La oferta evaluada no constituye una solicitud operativa.

- La solicitud operativa nace exclusivamente como `SwapRequest` formal.

- `offer_origin` es evidencia observada, no evaluacion formal.

- La evaluacion formal de una request pertenece a `swap_service`.

- Evaluar informa.

- Resolver decide explicitamente.

- Aplicar ejecuta.

- La fachada puede encadenar creacion y evaluacion formal, pero no puede resolver ni aplicar.

- La clasificacion tecnica no equivale a decision operativa.

- La decision operativa no equivale a estado del workflow.

- `VIABLE` no equivale a `APROBADO`.

- `APROBADO` no equivale a `APLICADO`.

- La request creada desde oferta nace `PENDIENTE`.

- La transicion valida de la fachada es `PENDIENTE -> EVALUADO`.

- La resolucion explicita posterior puede llevar a `APROBADO`, `RECHAZADO` o `CANCELADO`.

- La aplicacion del swap sigue siendo una operacion posterior, formal y separada.

- Cancelar por obsolescencia cierra el flujo sin convertir la request en rechazo operativo.

---

## Diccionario - conceptos de roster real, codigos y elegibilidad

---

### Catalogo oficial de codigos

Conjunto documental de codigos conocidos o definidos por normativa/procedimiento.

El catalogo oficial indica que un codigo existe o es conocido.

No implica que ese codigo este activo para una dependencia determinada.

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

Regla asociada:

```text
El catalogo oficial no implica activacion local.
```

---

### Codigo de roster

Valor que aparece en una celda de la lista de turno para una persona y un dia determinado.

Puede representar:

```text
turno operativo
evento no operativo
licencia
ausencia
capacitacion
comision
gestion
psicofisico
codigo legacy
codigo fuera de alcance
```

El codigo de roster describe el evento planificado.

No determina por si solo la elegibilidad para swap.

---

### Codigo operativo activo

Codigo que, para una dependencia determinada, genera una `Asignacion` operativa.

Para el contexto actual ACC:

```text
A
B
C
```

Solo los codigos operativos activos generan asignaciones operativas en V1.

---

### Codigo operativo configurable

Codigo oficial que podria generar una `Asignacion` operativa si la configuracion de dependencia lo habilita.

Ejemplos:

```text
D
X
```

Para el contexto actual ACC, `D` y `X` son codigos conocidos, pero no se consideran activos por defecto.

---

### Codigo no operativo

Codigo que representa un evento que no genera asignacion operativa swappeable.

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

Los codigos no operativos deben conservarse para trazabilidad, pero no participan en `candidate_generation`, `engine`, `scoring` ni `simulator` como turnos operativos.

---

### Codigo normalizable

Codigo aceptado como entrada, pero convertido a un codigo normalizado vigente.

Normalizaciones documentadas:

```text
IN -> EN
REM -> RTA
RET -> RTB
```

La normalizacion pertenece a la capa de importacion/configuracion.

No pertenece al `engine`, `simulator` ni al workflow formal de `SwapRequest`.

---

### Codigo legacy

Codigo conocido por uso historico o esquema anterior, pero no estandar vigente.

Ejemplos:

```text
REM
RET
```

En el contexto actual, estos codigos no se usan como codigos finales.

Se normalizan si existe regla explicita:

```text
REM -> RTA
RET -> RTB
```

La normalizacion de codigos legacy no debe ser silenciosa si afecta trazabilidad.

---

### Codigo fuera de alcance

Codigo oficial o conocido que no aplica a una dependencia determinada.

Para el contexto actual ACC:

```text
AE
AEC
```

`AE` y `AEC` no son invalidos globalmente.

Pueden aplicar a dependencias no H24 si la configuracion de dependencia los habilita.

---

### Normalizacion de codigo

Proceso por el cual el importador transforma un codigo de entrada en un codigo estandar vigente.

Ejemplos:

```text
IN -> EN
REM -> RTA
RET -> RTB
```

La normalizacion debe ser explicita y trazable.

Puede generar warning de importacion.

---

### Configuracion por dependencia

Configuracion que define como interpretar codigos de roster segun el contexto operativo de una dependencia.

Puede definir:

```text
codigos operativos activos
codigos operativos configurables
codigos no operativos
codigos legacy
codigos fuera de alcance
normalizaciones
politica strict
reglas de importacion
```

No evalua swaps.

No decide workflow.

No reemplaza al `engine`.

---

### Perfil de dependencia

Descripcion conceptual del tipo de dependencia y su regimen operativo.

Ejemplos conceptuales:

```text
tipo_dependencia = ACC
regimen_operativo = H24
```

o:

```text
tipo_dependencia = TWR
regimen_operativo = NO_H24
```

El perfil de dependencia ayuda a seleccionar o modificar la configuracion aplicable.

No debe hardcodearse una dependencia especifica como caso especial del sistema.

---

### Reglas de importacion

Reglas usadas por el importador para interpretar una matriz o CSV de roster.

Ejemplos:

```text
strict
normalizar_codigos
permitir_legacy
rechazar_fuera_de_alcance
clasificar_no_operativos
```

No deben mezclarse con reglas tecnicas del `engine`.

No son equivalentes:

```text
codigo desconocido
```

y:

```text
descanso minimo incumplido
```

---

### Asignacion operativa

Representacion interna de un turno operativo asignado a una persona en una fecha determinada.

En V1, se genera desde codigos operativos activos.

Para el contexto actual ACC:

```text
A
B
C
```

Las asignaciones operativas son la entrada relevante para reglas tecnicas, simulacion y generacion de candidatos.

---

### Asignacion operativa swappeable

Asignacion operativa que puede ser considerada para un swap normal.

No alcanza con que el codigo sea operativo.

Tambien deben cumplirse condiciones de elegibilidad funcional, por ejemplo:

```text
persona operativa general
pertenencia al universo operativo intercambiable
codigo operativo activo
puesto compatible si el puesto esta definido
```

---

### Evento no operativo

Evento de roster que no genera `Asignacion` operativa.

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

Debe conservarse fuera de `Asignacion` para trazabilidad, importacion y analisis.

No participa en swaps normales.

---

### Roster importado normalizado

Resultado conceptual de importar una matriz real de roster y normalizar sus datos.

Puede contener:

```text
asignaciones operativas
eventos no operativos
warnings
errors
metadata
```

No equivale necesariamente al input tecnico puro del `engine`.

Puede conservar mas informacion que la que el motor tecnico consume.

---

### Roster operativo tecnico

Vista o subconjunto del roster usado por `engine`, `scoring`, `simulator` y `candidate_generation`.

Contiene asignaciones operativas evaluables.

No incluye eventos no operativos como turnos swappeables.

---

### RosterImportResult

Resultado conceptual de una importacion de roster.

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

### Rol institucional

Funcion o posicion institucional de una persona.

Ejemplos:

```text
Jefe de Dependencia
Representante ANS / Coordinador
Instructor
Supervisor
Controlador
Practicante
Adscripto
```

El rol institucional no equivale automaticamente a elegibilidad para swap.

Ejemplos:

```text
Supervisor en puesto operativo -> puede intercambiar como controlador.
Instructor en A/B/C -> elegible igual que controlador.
Adscripto -> administrativo, no participa en swaps normales.
Practicante -> aparece como OJT/SIM, no participa en swaps normales.
```

---

### Perfil operativo para swaps

Concepto funcional que indica si una persona puede formar parte del universo operativo intercambiable.

No es lo mismo que rol institucional.

Ejemplo:

```text
Instructor = rol institucional
Instructor en A/B/C = potencialmente elegible
Instructor en OJT/SIM/RTA/RTB/EN = no elegible
```

---

### Universo operativo intercambiable

Conjunto de personas que pueden participar en swaps operativos normales si cumplen las condiciones del dia y contexto.

No debe inferirse solamente desde el codigo del roster.

Depende de:

```text
perfil de persona
estado operativo general
configuracion de dependencia
```

---

### Estado operativo general

Indica si una persona puede operar en terminos generales.

Si:

```text
estado_operativo_general = false
```

entonces la persona no participa en swaps operativos normales, aunque tenga una asignacion `A`, `B` o `C`.

El estado operativo general puede caer por:

```text
CMA / psicofisico vencido
override administrativo negativo
```

---

### CMA / psicofisico

Condicion de aptitud psicofisica asociada a una persona.

Regla conceptual:

```text
si fecha_vencimiento_cma <= fecha_actual
entonces estado_operativo_general = false
```

CMA vencido implica persona no operativa para swaps normales.

---

### Override administrativo CMA

Decision administrativa registrada que puede afectar la aptitud operativa asociada al CMA / psicofisico.

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

No debe existir override administrativo valido sin trazabilidad minima.

El override administrativo no representa permiso de sistema.

---

### Habilitacion RADAR

Habilitacion operativa que indica que la persona puede operar en contexto radar, segun corresponda a la dependencia.

Se reconoce conceptualmente como parte del perfil operativo futuro.

No se implementa en esta etapa.

---

### Habilitacion TMA

Habilitacion operativa que indica si la persona puede operar puestos TMA.

No tener habilitacion TMA no vuelve necesariamente no operativa a la persona.

Limita su compatibilidad con puestos TMA si el puesto esta definido.

Si el roster no define puestos, en V1 no se aplica filtro TMA.

---

### Compatibilidad por puesto

Evaluacion de si una persona puede cubrir un puesto especifico segun sus habilitaciones.

Ejemplo:

```text
habilitado_tma = false
puesto = TMA
-> no compatible
```

Si el puesto no esta definido, la compatibilidad por puesto queda fuera de V1.

---

### Puesto no definido

Situacion en la que el roster importado no informa puesto operativo especifico.

Regla V1:

```text
puesto no definido -> no aplicar filtro TMA
```

El sistema no debe inferir puestos no presentes en la entrada.

---

### Elegibilidad funcional para swap

Evaluacion conceptual que determina si una asignacion puede participar en un swap normal.

Depende de:

```text
persona
estado operativo general
asignacion/evento
configuracion de dependencia
puesto, si existe
habilitaciones, si corresponde
```

Regla corta:

```text
El codigo del roster describe el evento; la elegibilidad para swap se determina por persona, aptitud, asignacion y contexto.
```

---

### Elegibilidad por codigo

Condicion basada en la clasificacion del codigo de roster.

Ejemplo:

```text
A/B/C -> codigos operativos activos
LA/PSI/RTA/RTB/etc. -> no operativos
```

La elegibilidad por codigo es necesaria pero no suficiente.

---

### Elegibilidad por persona

Condicion basada en el estado y perfil operativo de la persona.

Ejemplos:

```text
estado_operativo_general = false -> no elegible
adscripto administrativo -> no elegible para swaps normales
practicante OJT/SIM -> no elegible para swaps normales
```

---

### Elegibilidad por puesto

Condicion basada en la compatibilidad entre persona y puesto.

Ejemplo:

```text
sin habilitacion TMA -> no elegible para puesto TMA
```

En V1, si el puesto no esta definido, no se aplica filtro TMA.

---

### candidate_generation

Capa que genera candidatos estructurales para swaps.

Debe operar solo sobre asignaciones operativas swappeables.

No debe generar candidatos sobre eventos no operativos.

No evalua, no clasifica, no decide y no persiste workflow.

---

### technical_prefilter

Frontera futura posible para aplicar reglas finas de elegibilidad antes de la simulacion tecnica.

Podria evaluar:

```text
estado operativo general
habilitaciones
compatibilidad por puesto
configuracion de dependencia
restricciones funcionales previas al simulator
```

No reemplaza al `simulator`.

No decide workflow.

No persiste requests.

No se implementa todavia como parte de esta documentacion.

---

## Terminos calendar-aware

### calendar-aware

Enfoque de validacion o diagnostico que considera el calendario completo del roster importado.

No analiza solamente asignaciones operativas, sino tambien dias libres, eventos no operativos documentados y cortes reales entre fechas.

---

### timeline diaria

Representacion diaria del roster importado por controlador.

Contiene un registro por cada controlador y fecha del periodo importado.

Permite conservar contexto calendario completo.

---

### dias_importados

Coleccion de dias diarios importados generada por el importador de roster.

Es la entrada principal del diagnostico calendar-aware.

---

### RosterDiaImportado

Registro diario importado para un controlador en una fecha determinada.

Contiene:

```text
controlador
fecha
estado
raw_value
codigo
codigo_normalizado
```

---

### RosterDayStatus

Categoria del dia importado.

Valores principales:

```text
OPERATIVO
LIBRE
NO_OPERATIVO_DOCUMENTADO
OPERATIVO_CONFIGURABLE_NO_ACTIVO
FUERA_DE_ALCANCE
DESCONOCIDO
```

---

### LIBRE

Dia sin asignacion, representado por celda vacia del roster.

Cuenta como dia libre para diagnosticos de rachas libres.

No equivale a licencia ni a evento no operativo documentado.

---

### NO_OPERATIVO_DOCUMENTADO

Dia con codigo explicito de roster que no genera asignacion operativa.

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

No cuenta como dia libre.

No entra al motor tecnico como turno operativo.

Conserva valor documental y auditable.

---

### diagnostico calendar-aware

Resultado de evaluar una timeline diaria importada con reglas que consideran calendario completo.

Informa violaciones hard, soft, codigos y severidades.

No decide swaps.

No modifica workflow.

---

### entrypoint paralelo calendar-aware

Frontera publica para consumir diagnostico calendar-aware sin acoplarse a modulos internos.

Modulo:

```text
src/roster_calendar_aware_entrypoint.py
```

Funciones:

```text
diagnosticar_dias_importados_calendar_aware
diagnosticar_importacion_calendar_aware
```

---

### ResultadoDiagnosticoCalendarAware

Resultado publico devuelto por el entrypoint calendar-aware.

Campos:

```text
total_dias_importados
total_violaciones
total_hard
total_soft
valido_sin_hard
por_codigo
por_severidad
violaciones
```

---

### EXCESO_LIBRES_CONSECUTIVOS

Codigo de violacion soft usado cuando una timeline contiene mas de 5 dias consecutivos con estado `LIBRE`.

Los dias `NO_OPERATIVO_DOCUMENTADO` no cuentan como `LIBRE`.

---
