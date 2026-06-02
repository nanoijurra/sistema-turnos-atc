# Decisiones de arquitectura

## Tabla de contenido

- [Arquitectura general](#arquitectura-general)
- [Modelo de dominio](#modelo-de-dominio)
- [Evaluacion tecnica](#evaluacion-tecnica)
- [Decision operativa](#decision-operativa)
- [Versionado y consistencia](#versionado-y-consistencia)
- [Estrategia de evolucion](#estrategia-de-evolucion)
- [Decision 45 - Fachada para crear request desde oferta y evaluar formalmente](#decision-45---fachada-para-crear-request-desde-oferta-y-evaluar-formalmente)
- [Decision 46 - La evaluacion formal desde oferta no implica resolucion automatica](#decision-46---la-evaluacion-formal-desde-oferta-no-implica-resolucion-automatica)
- [Decision 47 - Resolucion operativa posterior explicita](#decision-47---resolucion-operativa-posterior-explicita)
- [Decision 48 - Aplicacion explicita solo desde APROBADO](#decision-48---aplicacion-explicita-solo-desde-aprobado)

---

## Arquitectura general

### Decision 1 - Separacion de capas

El sistema se separa en capas claras:

- engine → validación y reglas
- swap_service → lógica de negocio de swaps
- simulator → exploración
- (futuro) roster_service → versionado

#### Motivo

Reducir acoplamiento y facilitar escalabilidad.

---

### Decision 2 - Engine sin logica de negocio

El engine no toma decisiones operativas (VIABLE / OBSERVAR / RECHAZAR).

#### Motivo

Evitar que se convierta en una "god class".

---

### Decision 3 - SwapRequest como entidad central

### Decision

SwapRequest representa todo el ciclo:
- creación
- evaluación
- resolución
- aplicación

### Motivo

Trazabilidad completa y auditabilidad.

---

### Decision 4 - Evaluacion basada en clasificacion tecnica

### Clasificacion tecnica

- BENEFICIOSO
- ACEPTABLE
- RECHAZABLE

### Mapeo normal hacia decision_sugerida

- BENEFICIOSO → VIABLE
- ACEPTABLE → OBSERVAR
- RECHAZABLE → RECHAZAR

### Aclaracion

Este mapeo expresa el tratamiento operativo sugerido derivado de la evaluación técnica, pero puede ser desplazado por restricciones operativas del flujo, como la ventana operativa.

La `decision_sugerida` no equivale a resolucion operativa ni a estado terminal del workflow.

### Motivo

Separar análisis técnico de decisión operativa sin perder la posibilidad de rechazo por condiciones de negocio.

---

### Decision 5 - Validacion por controlador



Las reglas se ejecutan por controlador (no global directo).

### Motivo

Modelo realista de fatiga y restricciones ATC.

---

### Decision 6 - Versionado de roster

Cada cambio genera una nueva versión.

### Motivo

- auditabilidad
- rollback
- consistencia histórica

---

### Decision 7 - Requests ligados a version

### Decision

Un SwapRequest pertenece a una versión específica del roster.

### Motivo

Evitar aplicar swaps sobre estados inconsistentes.

---

### Decision 8 - Cancelacion de requests obsoletos


Al cambiar la versión vigente del roster:

- los requests no terminales asociados a la versión anterior pasan a ser obsoletos
- dichos requests deben transicionar a estado CANCELADO

### Motivo

Distinguir entre:
- obsolescencia como condición del dominio
- cancelación como estado del workflow

---

### Decision 9 - Tests como contrato

Los tests existentes definen comportamiento esperado.

### Motivo

Evitar regresiones durante refactor.

---

### Decision 10 - Refactor incremental



Separar capas sin cambiar comportamiento observable.

### Motivo

Reducir riesgo.

---

### Decision 11 - Separacion definitiva entre evaluacion tecnica, decision operativa y aplicacion

Se consolida la separación estricta entre capas con esta distribución final:

- engine → validación técnica de reglas
- scoring → validez y score
- simulator → simulación y clasificación técnica del swap
- swap_service → evaluacion formal, decision_sugerida, resolucion operativa, estados y aplicacion del flujo
- (futuro) roster_service → versionado, vigencia y obsolescencia de roster

### Definicion

- engine responde si existen violaciones según reglas configuradas
- scoring responde si el roster es válido y cuál es su score
- simulator responde cómo impacta técnicamente un swap
- evaluar_swap_request informa resultado formal y decision_sugerida
- resolver_swap_request decide explicitamente el destino operativo del SwapRequest
- aplicar_swap_request ejecuta una request aprobada; no reevalúa ni reclasifica

### Motivo

Evitar duplicación de lógica, preservar contratos y permitir escalabilidad sin acoplamiento.

### Consecuencia

Queda prohibido:
- que engine tome decisiones de negocio
- que simulator modifique requests o persista
- que swap_service reclasifique swaps
- que evaluar_swap_request resuelva o aplique
- que resolver_swap_request reevalúe o aplique
- que aplicar_swap_request vuelva a evaluar o resolver un swap

Ver implementación contractual en:
[Ref: contratos.md #16]

---

### Decision 12 - Fuente unica de verdad por responsabilidad

Cada pregunta crítica del sistema debe tener un único módulo responsable.

### Asignacion

- validez técnica por reglas → engine / scoring
- clasificación técnica del swap → simulator
- evaluacion formal y decision_sugerida → swap_service.evaluar_swap_request
- resolucion operativa explicita → swap_service.resolver_swap_request
- aplicación real y versionado → swap_service.aplicar_swap_request (temporalmente), luego roster_service

### Motivo

Reducir ambigüedad y evitar inconsistencias entre capas.

---

### Decision 13 - Ventana operativa como regla de negocio



La validación de ventana operativa pertenece a swap_service y no a simulator ni engine.

### Motivo

La ventana operativa no forma parte de la calidad técnica del roster, sino de la admisibilidad operativa del trámite de swap.

### Consecuencia

Si falla la ventana operativa:
- la decision_sugerida es RECHAZAR
- se registra motivo de evaluacion: SWAP_FUERA_DE_VENTANA_OPERATIVA
- la clasificación técnica no se modifica ni se falsifica
- no se genera por si mismo un estado terminal RECHAZADO

### Opcionalmente

- la clasificación técnica puede no calcularse
- o puede conservarse separadamente si existe

### Regla

Las restricciones operativas nunca redefinen la clasificación técnica.

---

### Decision 14 - Dependencia permitida entre capas

swap_service puede depender de simulator como colaborador técnico de evaluación.

### Regla

- swap_service orquesta
- simulator evalúa
- engine valida

### No se permite

- simulator llamando a swap_service
- engine llamando a swap_service
- swap_service duplicando la clasificación del simulator

### Motivo

Mantener dependencia unidireccional y evitar ciclos de lógica.

---

### Decision 15 - Refactor guiado por contratos antes que por movimiento de codigo

### Decision

Antes de seguir moviendo lógica entre módulos, se congelan contratos de entrada/salida y responsabilidades.

### Prioridad

1. fijar contrato de salida de simulator
2. fijar contrato de mapeo en swap_service
3. eliminar duplicación de validación fuera de engine
4. estabilizar tests
5. luego extraer roster_service

### Motivo

Reducir regresiones y evitar degradación de diseño durante el refactor.

---

### Decision 16 - La clasificacion se define como clasificacion tecnica del swap

### Decision

La clasificación del sistema se redefine explícitamente como clasificación técnica del swap.

### Definicion

La clasificación técnica expresa exclusivamente el impacto comparativo del swap sobre el roster evaluado, sin incorporar restricciones operativas, estados del workflow ni decisiones de negocio.

### Valores

- BENEFICIOSO
- ACEPTABLE
- RECHAZABLE

### Origen

- simulator

### Motivo

Eliminar la ambigüedad entre evaluación técnica y tratamiento operativo del request.

### Consecuencia

swap_service no puede fabricar ni reemplazar clasificación técnica por motivos operativos.

---

### Decision 17 - Separacion explicita entre clasificacion tecnica y decision operativa

### Decision

La decision_sugerida del request queda separada de la clasificación técnica, de la resolucion operativa y del estado del workflow.

### Definicion

- clasificacion_tecnica = resultado técnico del swap
- decision_sugerida = tratamiento operativo sugerido durante la evaluacion formal
- resolucion_operativa = accion explicita posterior que lleva el request a APROBADO, RECHAZADO o CANCELADO
- estado_workflow = punto del ciclo de vida del request

### Valores de decision_sugerida

- VIABLE
- OBSERVAR
- RECHAZAR

### Origen

- swap_service.evaluar_swap_request

### Motivo

Preservar trazabilidad y permitir representar casos donde un swap sea técnicamente aceptable o beneficioso pero operativamente inadmisible, sin convertir automaticamente la sugerencia en estado terminal.

---

### Decision 18 - Restricciones operativas no alteran la clasificacion tecnica

### Decision

Las restricciones operativas, incluyendo ventana operativa, no modifican la clasificación técnica del swap.

### Consecuencia

Si una restricción operativa impide continuar el request:
- la decisión operativa puede ser RECHAZAR
- el motivo debe registrarse explícitamente
- la clasificación técnica permanece separada cuando exista

### Motivo

Evitar mezclar causas técnicas con causas operativas.

---

### Decision 19 - El request debe poder distinguir evaluacion tecnica de rechazo operativo

El modelo del request debe permitir distinguir explícitamente:

- clasificación técnica
- decision_sugerida
- motivo de evaluacion, cuando corresponda
- resolucion operativa explicita
- motivo_resolucion, cuando corresponda
- cancelacion por obsolescencia, cuando corresponda

### Motivo

Mejorar auditabilidad, trazabilidad y consistencia conceptual del flujo.

---

### Decision 20 - Definicion de version vigente, evaluable y aplicable

Se distinguen explícitamente tres conceptos:

- versión vigente: estado actual del sistema
- versión evaluable: versión sobre la cual se evalúa un request
- versión aplicable: versión sobre la cual puede ejecutarse un swap

### Regla

Un SwapRequest es evaluable y aplicable dentro del flujo si y solo si su `roster_version_id` coincide con la versión vigente.

### Consecuencia

- no se evalúan requests sobre versiones no vigentes
- no se aplican swaps sobre versiones no vigentes
- los requests no terminales asociados a versiones no vigentes se consideran obsoletos

### Motivo

Eliminar ambigüedad en el manejo de versiones y garantizar consistencia operativa.

---

### Decision 21 - Fuente unica de verdad de reglas y configuracion

La semántica de todas las reglas hard/soft y sus parámetros configurables pertenece exclusivamente al subsistema de validación (engine + config).

### Consecuencia

- ningún otro módulo puede reinterpretar parámetros como min_horas
- simulator y swap_service deben consumir resultados del engine sin reinterpretarlos

### Motivo

Evitar divergencia de comportamiento entre capas y garantizar consistencia técnica.

---

### Decision 22 - El objeto del swap son asignaciones, no indices

El objeto real de un swap son dos asignaciones dentro de una versión de roster.

### Aclaracion

- los índices pueden utilizarse como referencia estructural
- pero no definen la identidad del objeto del dominio

### Consecuencia

SwapRequest debe entenderse como una operación sobre asignaciones, no sobre posiciones.

### Motivo

Evitar ambigüedad en la identidad del dato y mejorar consistencia del modelo.

---

### Decision 23 - Frontera publica objetivo de simulator

La frontera pública objetivo de `simulator` se limita a capacidades técnicas de simulación y evaluación comparativa de swaps.

### Incluye

- simulación de escenarios
- evaluación técnica antes/después
- cálculo de deltas
- clasificación técnica
- exploración y ranking técnico de swaps

### No incluye como diseño objetivo

- creación de requests
- evaluación de requests
- resolución de requests
- aplicación de requests
- presentación textual de resultados
- workflow operativo

### Motivo

Preservar la separación entre evaluación técnica y ciclo de vida operativo del request.

---

### Decision 24 - Semantica del swap en el dominio

El swap del dominio se define como una operación sobre dos asignaciones de una misma versión, consistente en intercambiar el turno o actividad asignado entre ellas.

### Consecuencia

- el objeto del swap sigue siendo un par de asignaciones
- la transformación efectiva del dominio recae sobre el turno o actividad asignado
- la identidad base de las asignaciones se preserva

### Motivo

Eliminar la ambigüedad entre “swap de asignaciones completas” y “swap de contenido de turno”, alineando arquitectura y semántica del dominio.

---

### Decision 25 - Clasificacion tecnica como responsabilidad estable de simulator

La clasificación del swap permanece en `simulator` como responsabilidad técnica pura.

### Condicion

`clasificar_swap(...)` solo puede usar criterios técnicos, incluyendo:
- validez del escenario
- score
- deltas hard/soft
- impacto técnico por controlador

### Prohibicion

No puede incorporar:
- ventana operativa
- estados del request
- decisiones de aprobación
- workflow
- motivos operativos

### Motivo

Blindar la clasificación técnica frente a deriva hacia criterios de negocio.

---

### Decision 26 - Presentacion textual fuera del nucleo de simulator

La generación de explicaciones o recomendaciones textuales no pertenece al diseño objetivo de `simulator`.

### Definicion

La presentación textual se considera responsabilidad de una capa de salida, reporting o interfaz, no del subsistema técnico de simulación.

### Aclaracion

La existencia temporal de funciones de recomendación textual dentro de `simulator` se considera deuda de frontera y no diseño objetivo.

### Motivo

Evitar mezcla entre evaluación técnica y presentación.

---

### Decision 27 - Comparacion tecnica desacoplada de versionado formal

Los cálculos comparativos técnicos dentro de `simulator`, incluyendo impacto por controlador, deben depender de una estructura técnica neutral de comparación y no de `RosterVersion` ficticios.

### Consecuencia

El uso de versiones dummy para cálculos comparativos se considera transitorio y no forma parte de la arquitectura objetivo.

### Motivo

`RosterVersion` pertenece al plano de versionado real del sistema, mientras que la simulación necesita comparar escenarios hipotéticos sin forzar dependencia con la abstracción de versionado formal.

---

### Decision 28 - Frontera definitiva entre simulator y swap_service

Decisión:
Se consolida la frontera definitiva entre `simulator` y `swap_service`.

Definición:
- `simulator` produce evaluación técnica de escenarios hipotéticos de swap
- `evaluar_swap_request` produce evaluacion formal y decision_sugerida
- `resolver_swap_request` produce resolucion operativa explicita
- `aplicar_swap_request` produce aplicacion sobre roster

Responsabilidad de `simulator`:
- comparar escenario original y escenario resultante
- calcular deltas técnicos
- clasificar técnicamente el swap
- explorar alternativas de swap

Responsabilidad de `swap_service`:
- validar condiciones estructurales y operativas del request
- consumir evaluación técnica de `simulator`
- producir decision_sugerida durante evaluacion formal
- resolver explicitamente requests evaluadas
- aplicar requests aprobadas
- gestionar estado, persistencia e historial del request

Regla:
`simulator` no produce decision_sugerida, resolucion operativa ni estado de workflow.
`swap_service` no reclasifica técnicamente ni reinterpreta el resultado técnico como nueva clasificación.
`evaluar_swap_request` informa.
`resolver_swap_request` decide explicitamente.
`aplicar_swap_request` ejecuta.

Motivo:
Blindar la separación entre evaluación técnica y ciclo de vida operativo del request.

### Decision 29 - Frontera publica de simulator

Decisión:
Se restringe la superficie publica de `simulator` a capacidades tecnicas exclusivamente.

Regla:
`simulator` no debe exponer funciones operativas del ciclo de vida de `SwapRequest`, aun cuando deleguen en `swap_service`.

Prohibido exponer:
- crear request
- evaluar request
- resolver request
- aplicar request
- gestion de estado
- workflow

Consecuencia:
`swap_service` es la unica puerta publica valida para operaciones de request y workflow.

Motivo:
Eliminar ambiguedad de uso y alinear la API publica con la arquitectura definida en la Decision 28.

---

### Decision 30 - Incorporacion de equidad historica como señal de priorizacion

### Decision

Se incorpora un criterio de equidad historica como señal soft de priorizacion en el sistema de swaps, sin afectar la evaluacion tecnica ni la decision operativa base.

### Definicion

La equidad historica representa el balance reciente de beneficios y perjuicios recibidos por cada controlador a partir de swaps aplicados.

Un controlador se considera relativamente “castigado” cuando su saldo historico reciente es desfavorable respecto a otros.

### Modelo adoptado

#### Se adopta un modelo de ventana historica deslizante basada en:

ultimos 3 rosters (recomendado)
o equivalente temporal acotado

#### Dentro de esa ventana se calcula:

impacto neto por controlador
mejoras vs deterioros recibidos

### Naturaleza de la señal

#### La equidad historica:

es una señal soft
no es restriccion hard
no invalida swaps
no redefine clasificacion tecnica
no sustituye decision operativa

### Ubicacion en la arquitectura

#### La equidad historica:

no pertenece a engine
no pertenece a scoring tecnico base
no modifica simulator en su contrato tecnico

#### Se aplica como criterio adicional en:

ranking de swaps
priorizacion de alternativas
desempate entre swaps tecnicamente equivalentes

### Regla de integracion

#### La equidad historica solo puede actuar sobre:

ordenamiento entre swaps validos o aceptables
priorizacion de swaps tecnicamente correctos

#### No puede actuar sobre:

validez tecnica
clasificacion tecnica
decision operativa base
aplicacion del swap
Modelo de datos conceptual

### Se requiere una estructura historica minima basada en eventos de swaps aplicados:

controlador involucrado
impacto recibido (mejora / neutro / deterioro)
referencia a roster_version
timestamp

Esta informacion permite calcular saldo historico dentro de la ventana definida.

### Riesgos controlados
memoria infinita → se limita por ventana
sesgo acumulado → se acota a historia reciente
injusticia inversa → peso bajo en ranking
complejidad → modelo simple y auditable

### Motivo

#### Incorporar justicia operativa sin comprometer:

consistencia tecnica
separacion de capas
contratos existentes

Permitiendo mejorar la distribucion de beneficios en escenarios reales de uso ATC.

---

### Decision 31 - Integracion de equidad historica fuera de simulator

#### Decision

La equidad historica se integra como una etapa de priorizacion posterior a la evaluacion tecnica de `simulator`.

---

#### Regla

`simulator` mantiene su contrato tecnico y produce unicamente:

- evaluacion tecnica
- clasificacion tecnica
- impacto tecnico
- metricas comparativas

La equidad historica no modifica esa salida.

---

#### Forma de integracion

La equidad historica actua sobre:

- ranking de alternativas
- priorizacion entre swaps tecnicamente aceptables
- desempate entre swaps equivalentes

No actua sobre:

- validez tecnica
- clasificacion tecnica
- decision operativa base
- aplicacion del swap

---


#### Modelo adoptado

Se utiliza un ajuste suave de ranking con peso bajo, subordinado siempre a la calidad tecnica del swap.

---

#### Motivo

Incorporar equidad historica sin contaminar el contrato tecnico de `simulator` ni alterar la separacion de capas del sistema.

---

### Decision 32 - Equidad historica basada en eventos aplicados

#### Decision

La equidad historica del sistema se calcula exclusivamente a partir de efectos realmente materializados en la operacion.

#### Regla

Solo los swaps con estado `APLICADO` generan eventos historicos utilizables para calculo de equidad.

No generan señal historica:

- swaps sugeridos
- swaps explorados
- swaps evaluados
- swaps con decision operativa favorable
- requests rechazados
- requests cancelados
- requests aprobados pero no aplicados

#### Motivo

Evitar que el sistema reaccione a propuestas no concretadas, bloqueos sociales, rechazos grupales o circunstancias ajenas al efecto operativo real del swap.

---

### Decision 33 - Ventana temporal configurable para equidad historica

#### Decision

La equidad historica avanzada se basa en una ventana temporal configurable, definida por tiempo y no por cantidad de rosters.

#### Modelo adoptado

Se recomienda una ventana inicial de 60 dias.

#### Regla

- el store conserva eventos historicos
- la ventana se aplica en lectura
- la configuracion de ventana pertenece a la capa de priorizacion historica

#### Motivo

Permitir un modelo estable, explicable y desacoplado del ritmo de publicacion de rosters.

---

### Decision 34 - Modelo historico basado en eventos

#### Decision

La equidad historica evoluciona desde un contador simplificado hacia un modelo basado en eventos historicos por controlador.

#### Cada evento historico debe permitir representar, como minimo:

- controlador involucrado
- timestamp
- roster_version_id
- request_id
- tipo de impacto:
  - mejora
  - neutro
  - deterioro
- magnitud o peso del impacto

#### Motivo

Permitir derivar recencia, frecuencia, saldo e historial operativo sin depender de acumuladores opacos.

---

### Decision 35 - Decaimiento calculado en lectura

#### Decision

El decaimiento de beneficios historicos no se persiste. Se calcula en lectura sobre eventos dentro de la ventana vigente.

#### Modelo inicial recomendado

Decaimiento por tramos temporales, simple y auditable.

Ejemplo conceptual:
- tramo reciente: peso alto
- tramo intermedio: peso medio
- tramo lejano: peso bajo
- fuera de ventana: no computa

#### Motivo

Mantener trazabilidad, evitar reescritura del historico y permitir ajustar la formula sin migraciones de datos.

---

### Decision 36 - Controlador castigado como señal derivada

#### Decision

La condicion de controlador relativamente castigado no se persiste como estado explicito. Se deriva a partir del historial reciente.

#### Señales validas

- saldo historico ponderado desfavorable
- baja frecuencia de mejoras recientes
- antiguedad desde la ultima mejora

#### Regla

La condicion de castigado es una señal relativa de priorizacion, no una categoria fija del sistema.

#### Motivo

Evitar rigidez semantica, sesgos persistentes y estados historicos artificiales.

---

### Decision 37 - La equidad historica no reacciona a rechazo social ni a propuestas no materializadas

#### Decision

La equidad historica no debe verse afectada por propuestas de swap que no llegan a materializarse, aun cuando hayan sido tecnicamente correctas o operativamente favorables.

#### Incluye

El sistema no debe compensar ni penalizar por:

- rechazo social del grupo
- falta de aceptacion entre personas
- swaps viables no aprobados
- swaps aprobados que no llegan a aplicarse
- preferencias informales o regulacion social externa al sistema

#### Regla critica

La equidad historica solo observa efectos operativos reales, no intenciones, propuestas ni oportunidades frustradas.

#### Motivo

Evitar que el sistema incorpore sesgos sociales externos y reaccione a dinamicas no controladas por la logica operativa formal.

---

### Decision 38 - La equidad historica ordena ofertas pero no aprende de elecciones ni rechazos

#### Decision

La equidad historica puede intervenir exclusivamente en el orden de presentacion de candidatos elegibles ofrecidos por el sistema.

#### Alcance permitido

La señal de equidad historica puede utilizarse para:

- priorizar candidatos en el listado ofrecido
- desempatar alternativas tecnicamente equivalentes
- ordenar elegibles dentro de una ventana historica definida

#### Prohibicion

La equidad historica no debe recalcularse ni ajustarse a partir de:

- la eleccion final realizada por el usuario sobre el listado ofrecido
- rechazos de otros usuarios
- solicitudes no concretadas
- oportunidades frustradas
- dinamicas sociales o regulatorias del grupo

#### Regla critica

La equidad historica influye en la oferta del sistema, pero no aprende del comportamiento humano posterior sobre esa oferta.

#### Motivo

Evitar sesgos reactivos, incomodidad operativa y sobrecompensacion artificial de controladores por causas no materializadas en la realidad operativa.

---


#### Regla

La priorizacion historica puede actuar sobre el orden del listado de candidatos elegibles ofrecido por el sistema.

No puede actuar sobre:

- la eleccion final del usuario dentro de ese listado
- rechazos de otros usuarios
- solicitudes no concretadas
- dinamicas sociales del grupo

#### Trazabilidad

Estos eventos pueden registrarse para auditoria y seguimiento operativo, pero no constituyen insumo valido para recalculo de equidad historica.

#### Garantia

La equidad historica modifica el orden de oferta inicial, pero no reacciona al comportamiento humano posterior sobre esa oferta.

---

### Decision 39 - Flujo de oferta con equidad historica no reactiva

#### Decision

La equidad historica puede intervenir en el orden del listado de candidatos elegibles ofrecido por el sistema, pero no puede reaccionar al comportamiento humano posterior sobre esa oferta.

#### Flujo

1. el usuario selecciona una asignacion origen y una alternativa deseada
2. el sistema calcula candidatos elegibles segun reglas tecnicas y operativas
3. el sistema ordena el listado usando:
   - correccion tecnica
   - prioridad historica soft
4. el usuario elige libremente un candidato del listado
5. la aceptacion o rechazo posterior se registra, pero no alimenta la equidad historica
6. solo un swap con estado `APLICADO` genera evento historico valido

#### Regla critica

La equidad historica influye en la oferta del sistema, pero no aprende de elecciones humanas, rechazos ni oportunidades frustradas.

#### Motivo

Evitar sobrecompensacion reactiva, incomodidad operativa y sesgos derivados de dinamicas sociales externas a la logica formal del sistema.

---

### Decision 40 - Exploracion acotada centrada en request

#### Decision

La exploracion de swaps deja de ser global y exhaustiva, y pasa a ser acotada y centrada en una necesidad concreta del usuario.

#### Modelo adoptado

El flujo correcto del sistema pasa a ser:

- request o asignacion origen
- generacion de candidatos elegibles
- simulacion tecnica
- ranking
- oferta al usuario

#### Regla

No se explora el universo completo de swaps del roster.

Se explora solo un conjunto acotado de candidatos plausibles, definido por filtros baratos y relevantes para la necesidad concreta.

#### Motivo

Garantizar escalabilidad operativa sin alterar la evaluacion tecnica ni los contratos actuales.

---

### Decision 41 - Candidate generation como capa separada

#### Decision

La generacion de swaps candidatos se define como una responsabilidad separada de la evaluacion tecnica.

#### Responsabilidad

La capa de candidate generation:

- construye un universo elegible acotado
- aplica filtros estructurales baratos
- entrega candidatos para simulacion

#### Prohibiciones

No debe:

- clasificar swaps
- ejecutar evaluacion tecnica completa
- decidir operativamente
- persistir
- reemplazar simulator

#### Motivo

Separar reduccion del universo de busqueda respecto de la evaluacion tecnica del swap.

---

### Decision 42 - Contrato de candidate_generation

#### Decision

Se define `candidate_generation` como una capa separada responsable de generar un universo acotado de swaps candidatos antes de la simulacion tecnica.

#### Responsabilidad

`candidate_generation`:

- parte de una necesidad concreta
- aplica filtros baratos
- devuelve candidatos plausibles para evaluar

#### No responsabilidad

`candidate_generation` no:

- clasifica
- decide
- persiste
- calcula score tecnico final
- reemplaza simulator

#### Motivo

Separar generacion del universo elegible respecto de la evaluacion tecnica del swap, garantizando escalabilidad sin romper capas ni contratos actuales.

---

### Decision 43 - Introduccion de roster_index

#### Decision

Se incorpora el concepto de `roster_index` como estructura derivada del roster vigente.

#### Objetivo

Permitir acceso eficiente a subconjuntos operativos del roster sin recorrer toda la colección de asignaciones.

#### Responsabilidad

`roster_index`:

- indexa asignaciones
- acelera búsquedas
- sirve a candidate_generation

#### No responsabilidad

`roster_index` no:

- evalúa
- clasifica
- decide
- persiste requests
- reemplaza roster_version

#### Motivo

Escalar generación de candidatos sin modificar contratos técnicos existentes.

---

### Decision 44 - candidate_generation consume roster_index

#### Decision

La capa `candidate_generation` debe construir el universo elegible de swaps a partir de `roster_index`, y no mediante recorridos globales completos del roster.

#### Regla

- para escenarios de mismo dia, debe apoyarse en indices por fecha y fecha+turno
- para escenarios de otro dia, debe apoyarse en indices temporales futuros
- la generacion de candidatos sigue siendo una etapa previa y barata respecto de la simulacion tecnica

#### Motivo

Reducir drásticamente el espacio de búsqueda sin alterar la evaluación técnica ni introducir lógica de decisión en la generación de candidatos.

---

# Decision 45 - Fachada para crear request desde oferta y evaluar formalmente

## TOC

- [45.1 Estado](#451-estado)
- [45.2 Contexto](#452-contexto)
- [45.3 Decision](#453-decision)
- [45.4 Alcance permitido](#454-alcance-permitido)
- [45.5 Restricciones](#455-restricciones)
- [45.6 Justificacion](#456-justificacion)
- [45.7 Consecuencia](#457-consecuencia)
- [45.8 Decision negativa explicita](#458-decision-negativa-explicita)
- [45.9 Regla corta](#459-regla-corta)

---

## 45.1 Estado

Aceptada.

---

## 45.2 Contexto

El sistema ya permite generar ofertas evaluadas, presentarlas al usuario, seleccionar una oferta y convertirla en una `SwapRequest` formal en estado `PENDIENTE`.

La oferta evaluada conserva informacion tecnica observada en `offer_origin`, pero esa informacion no constituye evaluacion formal del request.

La evaluacion formal sigue siendo responsabilidad de:

```text
swap_service.evaluar_swap_request
```

La linea oferta -> request formal quedo consolidada con la siguiente separacion:

```text
OfertaEvaluada
-> seleccion de oferta
-> SwapRequest formal PENDIENTE
-> offer_origin como evidencia observada
-> persistencia explicita
-> evaluacion formal posterior por swap_service
```

---

## 45.3 Decision

Se acepta incorporar una fachada de alto nivel denominada conceptualmente:

```text
crear_request_desde_oferta_y_evaluar_formalmente
```

Esta fachada coordina en una sola operacion de alto nivel el flujo:

```text
OfertaEvaluada seleccionada
-> SwapRequest formal PENDIENTE
-> evaluacion formal mediante swap_service.evaluar_swap_request
-> SwapRequest EVALUADO
```

---

## 45.4 Alcance permitido

La fachada puede:

- recibir una oferta seleccionada;
- crear una `SwapRequest` formal en estado `PENDIENTE`;
- adjuntar `offer_origin` como evidencia observada;
- persistir explicitamente la request si corresponde al flujo;
- invocar `swap_service.evaluar_swap_request`;
- persistir el resultado formal evaluado;
- devolver la request evaluada o un resultado estructurado equivalente;
- registrar trazabilidad de la evaluacion formal posterior;
- permitir comparar evidencia observada contra evaluacion formal.

---

## 45.5 Restricciones

La fachada no puede:

- aprobar requests;
- rechazar requests por decision operativa humana;
- cancelar requests;
- aplicar swaps;
- modificar roster;
- llamar directamente a `engine`;
- llamar directamente a `scoring`;
- llamar directamente a `simulator`;
- clasificar tecnicamente por cuenta propia;
- decidir `VIABLE`, `OBSERVAR` o `RECHAZAR` por fuera de `swap_service`;
- reutilizar `clasificacion_observada` como clasificacion formal;
- crear un workflow paralelo de ofertas.

---

## 45.6 Justificacion

La fachada no se incorpora como optimizacion de benchmark.

La mejora esperada es operativa:

- reduce friccion para una futura UI/API;
- evita que queden requests creadas desde oferta sin evaluacion formal;
- concentra la trazabilidad del paso oferta -> request -> evaluacion formal;
- permite comparar la evidencia observada de `offer_origin` con la evaluacion formal posterior;
- mantiene a `swap_service` como responsable de la evaluacion formal y la decision_sugerida.

---

## 45.7 Consecuencia

La request creada desde oferta sigue naciendo primero en estado:

```text
PENDIENTE
```

Si la fachada evalua inmediatamente, la transicion correcta es:

```text
PENDIENTE -> EVALUADO
```

La evaluacion formal debe quedar registrada como evento propio del workflow formal.

La informacion de `offer_origin` permanece como snapshot historico observado y no debe ser pisada por la evaluacion formal.

---

## 45.8 Decision negativa explicita

No se acepta que una request creada desde oferta nazca directamente como:

```text
EVALUADO
```

No se acepta que una clasificacion observada en oferta reemplace la evaluacion formal.

No se acepta que la fachada apruebe, rechace, cancele o aplique swaps.

---

## 45.9 Regla corta

La fachada automatiza el encadenamiento operativo de crear y evaluar formalmente, pero no automatiza la resolucion ni la aplicacion.

---

# Decision 46 - La evaluacion formal desde oferta no implica resolucion automatica

## Estado

Aceptada.

## Contexto

Luego de implementar `crear_request_desde_oferta_y_evaluar_formalmente`, el sistema puede crear una `SwapRequest` formal desde una oferta seleccionada y evaluarla mediante `swap_service.evaluar_swap_request`.

El resultado esperado de esa fachada es una request en estado `EVALUADO`.

## Decision

La evaluacion formal de una request creada desde oferta no implica resolucion automatica.

Una request `EVALUADO` no debe pasar automaticamente a:

```text
APROBADO
RECHAZADO
CANCELADO
APLICADO
```

## Justificacion

La evaluacion formal produce informacion tecnica y decision sugerida, pero la resolucion operativa pertenece a una etapa posterior del workflow.

La decision `VIABLE`, `OBSERVAR` o `RECHAZAR` no equivale por si misma a una resolucion final.

## Regla corta

```text
EVALUADO no significa APROBADO.
VIABLE no significa APROBADO.
RECHAZAR como decision sugerida no significa RECHAZADO terminal.
```

---

# Decision 47 - Resolucion operativa posterior explicita

## TOC

- [47.1 Estado](#471-estado)
- [47.2 Contexto](#472-contexto)
- [47.3 Decision](#473-decision)
- [47.4 Modelo elegido para V1](#474-modelo-elegido-para-v1)
- [47.5 Alcance permitido](#475-alcance-permitido)
- [47.6 Restricciones](#476-restricciones)
- [47.7 Justificacion](#477-justificacion)
- [47.8 Consecuencias](#478-consecuencias)
- [47.9 Decision negativa explicita](#479-decision-negativa-explicita)
- [47.10 Regla corta](#4710-regla-corta)

---

## 47.1 Estado

Aceptada.

---

## 47.2 Contexto

El sistema ya permite crear una `SwapRequest` formal desde una oferta evaluada seleccionada y luego evaluarla formalmente mediante `swap_service.evaluar_swap_request`.

El flujo consolidado es:

```text
OfertaEvaluada
-> seleccion de oferta
-> SwapRequest formal PENDIENTE
-> offer_origin como evidencia observada
-> persistencia explicita
-> evaluacion formal por swap_service
-> SwapRequest EVALUADO
```

La evaluacion formal puede producir una `decision_sugerida`:

```text
VIABLE
OBSERVAR
RECHAZAR
```

Pero esa decision sugerida no constituye una resolucion operativa terminal.

---

## 47.3 Decision

La resolucion operativa posterior a una `SwapRequest` en estado `EVALUADO` debe ser explicita.

Una request evaluada puede pasar a:

```text
APROBADO
RECHAZADO
CANCELADO
```

solo mediante una accion formal de resolucion.

La resolucion no debe ser automatica por el solo hecho de existir una `decision_sugerida`.

---

## 47.4 Modelo elegido para V1

Para V1 se adopta el modelo simple:

```text
CTA selecciona oferta
-> sistema crea SwapRequest
-> sistema evalua formalmente
-> actor autorizado resuelve explicitamente
-> si corresponde, luego se aplica
```

No se incorpora todavia un workflow formal de aceptacion bilateral.

La contraparte no se modela como estado propio en V1, porque el sistema ya protege las restricciones hard mediante evaluacion tecnica y formal.

La aceptacion bilateral, contrapropuestas y bloqueos multiusuario quedan fuera de esta decision y podran tratarse en una etapa posterior.

---

## 47.5 Alcance permitido

La resolucion operativa puede:

- consumir una `SwapRequest` en estado `EVALUADO`;
- considerar la `decision_sugerida`;
- considerar la clasificacion tecnica formal;
- considerar advertencias o divergencias;
- registrar actor de resolucion;
- registrar fecha/hora de resolucion;
- registrar accion de resolucion;
- registrar motivo_resolucion;
- pasar la request a `APROBADO`, `RECHAZADO` o `CANCELADO`.

---

## 47.6 Restricciones

La resolucion operativa no puede:

- modificar `offer_origin`;
- modificar la clasificacion tecnica formal;
- modificar la evaluacion formal;
- aplicar el swap;
- modificar roster;
- reevaluar la request;
- convertir automaticamente `VIABLE` en `APROBADO`;
- convertir automaticamente `RECHAZAR` en `RECHAZADO`;
- convertir automaticamente `BENEFICIOSO` en `APROBADO`.

---

## 47.7 Justificacion

La evaluacion formal informa, pero no decide terminalmente.

La `decision_sugerida` orienta al actor operativo, pero no reemplaza la resolucion formal.

El `actor` registrado en history identifica quien ejecuto o disparo la accion, pero no define por si mismo permisos formales ni autorizacion operativa.

Este diseño mantiene separadas cuatro etapas:

```text
evaluacion tecnica
-> decision sugerida
-> resolucion operativa
-> aplicacion al roster
```

La separacion evita automatizar decisiones operativas antes de definir roles, supervision, consentimiento bilateral, excepciones y trazabilidad institucional.

---

## 47.8 Consecuencias

Una `SwapRequest` en estado `EVALUADO` queda lista para resolucion, pero no esta aprobada automaticamente.

El sistema puede asistir la resolucion mostrando:

- clasificacion tecnica formal;
- decision_sugerida;
- impacto tecnico;
- divergencias contra `offer_origin`;
- advertencias;
- historial de eventos.

Pero la transicion a `APROBADO`, `RECHAZADO` o `CANCELADO` requiere accion explicita.

---

## 47.9 Decision negativa explicita

No se implementa por ahora:

```text
VIABLE -> APROBADO automatico
RECHAZAR -> RECHAZADO automatico
BENEFICIOSO -> APROBADO automatico
EVALUADO -> APLICADO automatico
```

No se agregan en V1 estados nuevos como:

```text
PROPUESTO
ACEPTADO_POR_CONTRAPARTE
RECHAZADO_POR_CONTRAPARTE
PENDIENTE_SUPERVISOR
```

No se implementa todavia workflow bilateral formal.

---

## 47.10 Regla corta

La evaluacion formal informa; la resolucion operativa decide; la aplicacion ejecuta.

---

# Decision 48 - Aplicacion explicita solo desde APROBADO

## TOC

- [48.1 Estado](#481-estado)
- [48.2 Contexto](#482-contexto)
- [48.3 Decision](#483-decision)
- [48.4 Alcance permitido](#484-alcance-permitido)
- [48.5 Restricciones](#485-restricciones)
- [48.6 Cancelacion de requests obsoletos](#486-cancelacion-de-requests-obsoletos)
- [48.7 Justificacion](#487-justificacion)
- [48.8 Consecuencias](#488-consecuencias)
- [48.9 Decision negativa explicita](#489-decision-negativa-explicita)
- [48.10 Regla corta](#4810-regla-corta)

---

## 48.1 Estado

Aceptada.

---

## 48.2 Contexto

El workflow formal consolidado de `SwapRequest` es:

```text
PENDIENTE
-> evaluar_swap_request
-> EVALUADO
-> resolver_swap_request
-> APROBADO / RECHAZADO / CANCELADO
-> aplicar_swap_request
-> APLICADO
```

La regla central vigente es:

```text
Evaluar informa.
Resolver decide explicitamente.
Aplicar ejecuta.
```

Luego de la resolucion operativa explicita, una request puede quedar en estado `APROBADO`.

La aplicacion es la etapa posterior encargada de ejecutar el swap sobre el roster y crear una nueva version.

---

## 48.3 Decision

La aplicacion de una `SwapRequest` debe ser una accion explicita y solo puede ejecutarse sobre una request en estado:

```text
APROBADO
```

La aplicacion debe realizarse mediante:

```text
swap_service.aplicar_swap_request
```

La aplicacion no debe ocurrir automaticamente como consecuencia de evaluar o resolver.

---

## 48.4 Alcance permitido

La aplicacion puede:

- recibir una `SwapRequest` en estado `APROBADO`;
- validar que la request corresponde al roster vigente;
- ejecutar el intercambio de asignaciones;
- crear una nueva version de roster;
- marcar la request como `APLICADO`;
- registrar history formal de aplicacion;
- persistir el estado `APLICADO`;
- cancelar requests obsoletos si corresponde al contrato vigente;
- registrar motivo especifico de cancelacion por obsolescencia cuando corresponda.

---

## 48.5 Restricciones

La aplicacion no puede:

- operar sobre requests en estado `PENDIENTE`;
- operar sobre requests en estado `EVALUADO`;
- operar sobre requests en estado `RECHAZADO`;
- operar sobre requests en estado `CANCELADO`;
- operar nuevamente sobre requests en estado `APLICADO`;
- reevaluar la request;
- resolver la request;
- modificar `decision_sugerida`;
- modificar `offer_origin`;
- reemplazar la evaluacion formal;
- llamar directamente a `engine`;
- llamar directamente a `scoring`;
- llamar directamente a `simulator`;
- crear workflow paralelo;
- aprobar automaticamente;
- rechazar automaticamente;
- modificar clasificacion tecnica formal.

---

## 48.6 Cancelacion de requests obsoletos

Al crear una nueva version de roster, algunas requests asociadas a la version anterior pueden quedar obsoletas.

La aplicacion puede cancelar requests obsoletas cuando corresponda, pero debe hacerlo con restricciones claras:

- solo deben cancelarse requests no terminales o no aplicadas que dependan de la version anterior;
- no deben modificarse requests ya `APLICADO`;
- no deben modificarse historicos terminales salvo contrato explicito;
- debe registrarse un motivo de cancelacion por obsolescencia;
- debe quedar history que permita distinguir cancelacion operativa de cancelacion por obsolescencia;
- no debe tratarse la obsolescencia como rechazo operativo.

Estados candidatos a cancelacion por obsolescencia:

```text
PENDIENTE
EVALUADO
APROBADO
```

Estados que no deberian modificarse por obsolescencia:

```text
RECHAZADO
CANCELADO
APLICADO
```

---

## 48.7 Justificacion

La aplicacion es la unica etapa que ejecuta consecuencias estructurales sobre el roster.

Por eso debe mantenerse separada de:

- evaluacion formal;
- decision sugerida;
- resolucion operativa;
- oferta evaluada;
- reporting;
- candidate_selection;
- simulator.

La separacion evita que una request tecnicamente viable o aprobada produzca cambios de roster sin una accion explicita de aplicacion.

---

## 48.8 Consecuencias

Una request `APROBADO` queda lista para aplicacion, pero no se aplica automaticamente.

La aplicacion debe ser una operacion formal, trazable y separada.

La aplicacion crea una nueva version de roster y puede provocar obsolescencia de requests vinculadas a versiones anteriores.

---

## 48.9 Decision negativa explicita

No se implementa:

```text
EVALUADO -> APLICADO automatico
VIABLE -> APLICADO automatico
BENEFICIOSO -> APLICADO automatico
APROBADO -> APLICADO automatico
```

No se implementa una fachada:

```text
evaluar_resolver_aplicar
```

ni:

```text
aprobar_y_aplicar
```

La aplicacion sigue siendo una compuerta propia.

---

## 48.10 Regla corta

La aplicacion solo ejecuta requests aprobadas y lo hace sobre una nueva version de roster.

---

# Decision 49 - Auditoria estructurada minima del workflow formal

## TOC

- [49.1 Estado](#491-estado)
- [49.2 Contexto](#492-contexto)
- [49.3 Decision](#493-decision)
- [49.4 Alcance permitido](#494-alcance-permitido)
- [49.5 Restricciones](#495-restricciones)
- [49.6 Diferencia entre history y audit trail](#496-diferencia-entre-history-y-audit-trail)
- [49.7 Eventos minimos](#497-eventos-minimos)
- [49.8 Campos minimos sugeridos](#498-campos-minimos-sugeridos)
- [49.9 Justificacion](#499-justificacion)
- [49.10 Consecuencias](#4910-consecuencias)
- [49.11 Decision negativa explicita](#4911-decision-negativa-explicita)
- [49.12 Regla corta](#4912-regla-corta)

---

## 49.1 Estado

Aceptada.

---

## 49.2 Contexto

El workflow formal de `SwapRequest` quedo consolidado como:

```text
PENDIENTE
-> evaluar_swap_request
-> EVALUADO
-> resolver_swap_request
-> APROBADO / RECHAZADO / CANCELADO
-> aplicar_swap_request
-> APLICADO
```

La regla central vigente es:

```text
Evaluar informa.
Resolver decide explicitamente.
Aplicar ejecuta.
```

Tambien quedaron separadas las responsabilidades:

- `simulator` clasifica tecnicamente;
- `swap_service.evaluar_swap_request` informa y produce `decision_sugerida`;
- `swap_service.resolver_swap_request` decide explicitamente el destino operativo;
- `swap_service.aplicar_swap_request` ejecuta una request aprobada sobre roster.

El sistema ya conserva `history`, pero se necesita definir un contrato semantico mas claro para eventos auditables del workflow.

---

## 49.3 Decision

Se adopta como proximo eje arquitectonico la auditoria estructurada minima del workflow formal.

La auditoria estructurada debe registrar hechos relevantes del workflow sin modificar estados, decisiones ni transiciones.

La auditoria no gobierna el workflow.

La auditoria observa y registra lo ocurrido.

---

## 49.4 Alcance permitido

La auditoria estructurada puede definir:

- tipos de eventos del workflow;
- timestamp de cada evento;
- actor registrado;
- tipo de actor;
- estado anterior;
- estado nuevo;
- motivo asociado;
- request afectada;
- version de roster asociada;
- metadata auxiliar;
- origen del evento;
- diferencia entre eventos operativos y eventos automaticos del sistema.

---

## 49.5 Restricciones

La auditoria estructurada no puede:

- crear nuevos estados de `SwapRequest`;
- modificar taxonomias;
- aprobar;
- rechazar;
- cancelar;
- aplicar;
- reevaluar;
- definir permisos;
- definir roles autorizantes;
- reemplazar `history`;
- reemplazar persistencia de requests;
- introducir UI;
- introducir API;
- introducir workflow bilateral;
- introducir locks o concurrencia;
- cambiar comportamiento productivo.

---

## 49.6 Diferencia entre history y audit trail

`history` representa trazabilidad existente del request.

Puede ser usado para conservar informacion legible o historica asociada a eventos.

`audit trail` representa un contrato estructurado de eventos auditables.

La auditoria estructurada no elimina `history`.

En V1, `audit trail` puede implementarse sobre `history` si el modelo actual lo permite, siempre que respete nombres, tipos de eventos y campos definidos.

---

## 49.7 Eventos minimos

Eventos minimos recomendados:

```text
REQUEST_CREADA
REQUEST_CREADA_DESDE_OFERTA
REQUEST_EVALUADA
REQUEST_RESUELTA
REQUEST_APLICADA
REQUEST_CANCELADA_POR_OBSOLESCENCIA
```

Para `REQUEST_RESUELTA`, el resultado debe indicar:

```text
APROBADO
RECHAZADO
CANCELADO
```

La cancelacion por obsolescencia se mantiene como evento diferenciado porque no equivale a rechazo operativo ni a cancelacion operativa comun.

---

## 49.8 Campos minimos sugeridos

Campos minimos sugeridos para eventos auditables:

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

No todos los campos son obligatorios para todos los eventos.

La implementacion futura debe definir cuales son requeridos por tipo de evento.

---

## 49.9 Justificacion

El workflow formal ya esta consolidado.

Antes de avanzar hacia roles, permisos, UI, API, locks o workflow bilateral, conviene definir una base de auditoria estructurada.

Esto permite:

- distinguir evaluacion, resolucion y aplicacion;
- distinguir cancelacion operativa de cancelacion por obsolescencia;
- conservar actor y motivo sin confundirlos con permisos;
- preparar integraciones futuras sin contaminar el core;
- mejorar trazabilidad institucional.

---

## 49.10 Consecuencias

El workflow no cambia.

Los estados no cambian.

Las taxonomias no cambian.

La auditoria estructurada queda definida como capa conceptual auxiliar de trazabilidad.

Cualquier implementacion futura debe respetar que:

```text
El workflow cambia estados.
La auditoria registra hechos del workflow.
```

---

## 49.11 Decision negativa explicita

No se implementa en esta decision:

```text
roles
permisos
supervisor
UI
API
workflow bilateral
locks
nuevas tablas
nuevos estados
automatismos
```

No se convierte `actor` en permiso formal.

No se convierte `history` en autorizacion.

No se modifica comportamiento productivo.

---

## 49.12 Regla corta

El workflow cambia estados; la auditoria registra hechos del workflow.