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

### Motivo

Reducir acoplamiento y facilitar escalabilidad.

---

### Decision 2 - Engine sin logica de negocio

El engine no toma decisiones operativas (VIABLE / OBSERVAR / RECHAZAR).

### Motivo

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