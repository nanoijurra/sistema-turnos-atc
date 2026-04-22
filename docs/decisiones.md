# Decisiones de arquitectura

## Tabla de contenido

- [Arquitectura general](#arquitectura-general)
- [Modelo de dominio](#modelo-de-dominio)
- [Evaluacion tecnica](#evaluacion-tecnica)
- [Decision operativa](#decision-operativa)
- [Versionado y consistencia](#versionado-y-consistencia)
- [Estrategia de evolucion](#estrategia-de-evolucion)

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

### Mapeo normal hacia decision operativa

- BENEFICIOSO → VIABLE
- ACEPTABLE → OBSERVAR
- RECHAZABLE → RECHAZAR

### Aclaracion

Este mapeo expresa el tratamiento operativo normal derivado de la evaluación técnica, pero puede ser desplazado por restricciones operativas del flujo, como la ventana operativa.

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
- swap_service → decisión operativa, estados y orquestación del flujo
- (futuro) roster_service → versionado, vigencia y obsolescencia de roster

### Definicion

- engine responde si existen violaciones según reglas configuradas
- scoring responde si el roster es válido y cuál es su score
- simulator responde cómo impacta técnicamente un swap
- swap_service responde qué decisión operativa corresponde sobre un SwapRequest
- aplicar_swap_request no reevalúa ni reclasifica

### Motivo

Evitar duplicación de lógica, preservar contratos y permitir escalabilidad sin acoplamiento.

### Consecuencia

Queda prohibido:
- que engine tome decisiones de negocio
- que simulator modifique requests o persista
- que swap_service reclasifique swaps
- que aplicar_swap_request vuelva a evaluar un swap

Ver implementación contractual en:
[Ref: contratos.md #16]

---

### Decision 12 - Fuente unica de verdad por responsabilidad

Cada pregunta crítica del sistema debe tener un único módulo responsable.

### Asignacion

- validez técnica por reglas → engine / scoring
- clasificación técnica del swap → simulator
- decisión operativa del request → swap_service
- aplicación real y versionado → swap_service (temporalmente), luego roster_service

### Motivo

Reducir ambigüedad y evitar inconsistencias entre capas.

---

### Decision 13 - Ventana operativa como regla de negocio



La validación de ventana operativa pertenece a swap_service y no a simulator ni engine.

### Motivo

La ventana operativa no forma parte de la calidad técnica del roster, sino de la admisibilidad operativa del trámite de swap.

### Consecuencia

Si falla la ventana operativa:
- la decisión operativa es RECHAZAR
- se registra motivo: SWAP_FUERA_DE_VENTANA_OPERATIVA
- la clasificación técnica no se modifica ni se falsifica

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

La decisión operativa del request queda separada de la clasificación técnica.

### Definicion

- clasificacion_tecnica = resultado técnico del swap
- decision_operativa = acción o tratamiento del request dentro del flujo del sistema

### Valores de decision operativa

- VIABLE
- OBSERVAR
- RECHAZAR

### Origen

- swap_service

### Motivo

Preservar trazabilidad y permitir representar casos donde un swap sea técnicamente aceptable o beneficioso pero operativamente inadmisible.

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
- decisión operativa
- motivo operativo, cuando corresponda

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

### Decision 28 Frontera definitiva entre simulator y swap_service

Decisión:
Se consolida la frontera definitiva entre `simulator` y `swap_service`.

Definición:
- `simulator` produce evaluación técnica de escenarios hipotéticos de swap
- `swap_service` produce tratamiento operativo del request dentro del flujo del sistema

Responsabilidad de `simulator`:
- comparar escenario original y escenario resultante
- calcular deltas técnicos
- clasificar técnicamente el swap
- explorar alternativas de swap

Responsabilidad de `swap_service`:
- validar condiciones estructurales y operativas del request
- consumir evaluación técnica de `simulator`
- producir decisión operativa
- gestionar estado, persistencia e historial del request

Regla:
`simulator` no produce decisión operativa ni estado de workflow.
`swap_service` no reclasifica técnicamente ni reinterpreta el resultado técnico como nueva clasificación.

Motivo:
Blindar la separación entre evaluación técnica y ciclo de vida operativo del request.

### Decision 29 Frontera publica de simulator

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