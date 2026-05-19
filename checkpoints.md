# CHECKPOINTS DEL PROYECTO — SISTEMA SWAPS ATC

---

## checkpoint-v1-roster-versioning-stable
Fecha: 2026-03-25

### Estado general
Sistema funcional, consistente y con versionado de roster implementado.
Tests en verde y demo operativa.

### Qué quedó implementado

#### 1. Versionado de roster
- Entidad `RosterVersion` operativa
- Existe una única versión vigente
- Se generan nuevas versiones al aplicar swaps
- Se mantiene `base_version_id` para trazabilidad

#### 2. Engine consistente con versionado
- `crear_roster_version_inicial(...)`
- `crear_nueva_version_desde_roster_vigente(...)`
- `aplicar_swap_request(...)` ahora genera nueva versión en lugar de mutar lista

#### 3. SwapRequest alineado al modelo real
- `roster_version_id` asociado al momento de evaluación
- `roster_hash` para detección de cambios
- Invariantes de dominio activas:
  - no aplicar sin evaluar
  - no resolver sin evaluar
  - no aplicar si no está aceptado
  - no aplicar si el roster cambió

#### 4. Cancelación automática de obsolescencia
- Se implementa `cancelar_por_obsolescencia(...)` en el modelo
- Se implementa `cancelar_requests_obsoletos(...)` en engine
- Al generar nueva versión:
  - requests de la versión anterior (PENDIENTE/EVALUADO) → CANCELADO
- Se registra motivo y trazabilidad en history

#### 5. Stores funcionando correctamente
- `request_store` y `roster_store` consistentes con el flujo
- Persistencia en memoria estable
- Validación de único roster vigente

#### 6. Demo adaptada al nuevo flujo
- Se limpia estado antes de cada escenario
- Se crea roster inicial antes de evaluar
- Se muestra versión vigente
- Se adapta uso de `RosterVersion` en aplicación

#### 7. Tests
- 42 tests passing
- Cobertura de:
  - stores
  - engine
  - simulator
  - validator
  - invariantes de dominio
  - versionado y obsolescencia

---

### Decisiones de diseño importantes

- El engine es el orquestador (no lógica en store)
- El modelo contiene invariantes de negocio
- La obsolescencia se maneja por versionado (no por mutación)
- Cancelación automática separada de notificación al usuario
- `history` se mantiene simple (list[str]) por ahora

---

### Limitaciones actuales (conscientes)

- No existe estado explícito `EVALUADO` (se infiere por `decision_sugerida`)
- No hay capa de notificación al usuario
- Persistencia es en memoria (no DB)
- No hay control de concurrencia más allá de versión vigente

---

### Próximos pasos naturales

1. Formalizar estado `EVALUADO`
2. Mejorar ciclo de vida del SwapRequest
3. Evaluar requests solo contra roster vigente (pre-validación más explícita)
4. Evolucionar persistencia (si aplica)
5. Preparar capa de interacción (CLI / API / UI)

---

### Notas

Este checkpoint representa el paso de:
- sistema basado en listas
→ sistema con versionado, trazabilidad y control de obsolescencia

Es una base estable para seguir evolucionando el dominio sin romper consistencia.

------------------------------------------------------------------------------------------------------------------------

## checkpoint-v2-evaluated-state-formalized
Fecha: 2026-03-26

### Estado general
Se formaliza el estado `EVALUADO` dentro del ciclo de vida de `SwapRequest`.
Tests en verde y demo operativa.

### Qué quedó implementado

#### 1. Estado EVALUADO explícito
- `evaluar_swap_request(...)` ahora cambia `estado` de `PENDIENTE` a `EVALUADO`
- El request ya no queda ambiguo después de la evaluación

#### 2. Flujo de resolución alineado
- `resolver_swap_request(...)` ahora exige estado `EVALUADO`
- Requests ya terminales no pueden resolverse nuevamente
- Se mejora la consistencia semántica del ciclo de vida

#### 3. Flujo de aplicación alineado
- `aplicar_swap_request(...)` exige estado `ACEPTADO`
- Se elimina la lógica incorrecta que trataba `ACEPTADO` como estado no aplicable
- El flujo queda:
  - `PENDIENTE`
  - `EVALUADO`
  - `ACEPTADO / RECHAZADO / CANCELADO`
  - aplicación sobre request aceptado

#### 4. Tests y demo
- 42 tests passing
- La demo refleja correctamente:
  - requests observados → `EVALUADO`
  - requests rechazados → `RECHAZADO`
  - requests aprobados → `ACEPTADO` y luego aplicados

---

### Decisiones de diseño importantes

- `decision_sugerida` deja de ser la única señal de request evaluado
- el estado del request pasa a expresar mejor el momento del flujo
- resolver y aplicar quedan separados por contrato:
  - resolver requiere `EVALUADO`
  - aplicar requiere `ACEPTADO`

---

### Limitaciones actuales (conscientes)

- `APLICADO` todavía no se formaliza como estado explícito al final del flujo
- no existe todavía una capa de notificación al usuario
- persistencia sigue siendo en memoria

---

### Próximos pasos naturales

1. Formalizar estado `APLICADO`
2. Revisar si conviene separar mejor resolución manual vs automática
3. Mejorar consulta/listado de requests por estado
4. Evolucionar persistencia si el proyecto lo requiere

---

### Notas

Este checkpoint consolida el ciclo de vida del `SwapRequest` como máquina de estados más explícita y coherente.

----------------------------------------------------------------------------------------------------------------------------

## checkpoint-v3-applied-state-formalized
Fecha: 2026-03-28

### Estado general
Se formaliza el estado `APLICADO` en el ciclo de vida de `SwapRequest`.
Tests en verde y demo operativa.

### Qué quedó implementado

#### 1. Estado APLICADO explícito
- `aplicar_swap_request(...)` ahora marca el request como `APLICADO`
- El request deja de quedar ambiguamente en `ACEPTADO` después de ejecutarse

#### 2. Flujo del request más claro
- `PENDIENTE` → request creado
- `EVALUADO` → request evaluado
- `ACEPTADO / RECHAZADO / CANCELADO` → request resuelto
- `APLICADO` → request efectivamente ejecutado sobre el roster

#### 3. Guardas de estado más estrictas
- `resolver_swap_request(...)` exige estado `EVALUADO`
- `aplicar_swap_request(...)` exige estado `ACEPTADO`
- Se reduce la posibilidad de transiciones inconsistentes

#### 4. Auditoría y trazabilidad
- El historial refleja evaluación, resolución y aplicación
- La aplicación sigue generando nueva versión de roster
- Se mantiene el control de obsolescencia por `roster_version_id`

#### 5. Validación general
- 42 tests passing
- Demo operativa sin regresiones funcionales

---

### Decisiones de diseño importantes

- aceptación y aplicación quedan separadas como etapas distintas
- el estado del request refleja mejor la realidad operacional
- el sistema mantiene swap de turnos, no intercambio completo de asignaciones
- el modelo sigue evolucionando hacia una máquina de estados más explícita

---

### Limitaciones actuales (conscientes)

- persistencia sigue siendo en memoria
- la notificación al usuario todavía no existe como capa separada
- `history` sigue siendo `list[str]`, simple pero suficiente por ahora

---

### Próximos pasos naturales

1. Mejorar listados/consultas de requests por estado
2. Revisar si conviene separar mejor resolución manual vs automática
3. Evolucionar persistencia si el proyecto lo requiere
4. Evaluar una capa CLI/API más explícita

---

### Notas

Este checkpoint consolida la diferencia entre:
- request aceptado
- request efectivamente aplicado

Eso mejora consistencia de dominio y auditabilidad.

-------------------------------------------------------------------------------------------------------------------------------------------

## checkpoint-v4-request-store-sqlite
Fecha: 2026-03-30

### Estado general
Se migra `request_store` desde almacenamiento en memoria a persistencia real con SQLite.
Tests en verde y demo operativa.

### Qué quedó implementado

#### 1. Persistencia real de SwapRequest
- `request_store.py` ahora usa SQLite
- Los requests se almacenan en `data/swaps_atc.db`
- La tabla `swap_requests` se inicializa automáticamente si no existe

#### 2. Serialización / deserialización
- `SwapRequest` se serializa a columnas SQLite
- `history` se persiste como JSON
- `datetime` se guarda en formato ISO y se reconstruye correctamente

#### 3. Interfaz preservada
- Se mantienen las funciones existentes:
  - `guardar_request`
  - `listar_requests`
  - `limpiar_requests`
  - `listar_requests_por_estado`
  - `listar_requests_por_roster_version`
  - `listar_requests_activos`
  - `resumen_requests`
- Engine y simulator no necesitaron cambios de contrato

#### 4. Inicialización robusta
- La base se conecta mediante ruta robusta con `os.path`
- La tabla se crea automáticamente al importar el módulo (`init_db()`)

#### 5. Validación general
- 46 tests passing
- Demo operativa sin regresiones funcionales

---

### Decisiones de diseño importantes

- se eligió SQLite antes que API para consolidar persistencia primero
- se mantuvo compatibilidad con la interfaz del store
- la migración se hizo por sustitución interna, no por reescritura del sistema

---

### Limitaciones actuales (conscientes)

- solo `request_store` está persistido en SQLite
- `roster_store` sigue en memoria
- no hay todavía migraciones formales de esquema
- la auditoría sigue apoyándose en `history` como `list[str]`

---

### Próximos pasos naturales

1. Migrar `roster_store` a SQLite
2. Persistir `RosterVersion` y sus asignaciones
3. Evaluar consultas combinadas por request + versión
4. Recién después exponer una API mínima

---

### Notas

Este checkpoint convierte al sistema en una base persistente real, dejando atrás el almacenamiento efímero en memoria para `SwapRequest`.


-------------------------------------------------------------------------------------------------------------------------------------------

## checkpoint-v5-roster-store-sqlite
Fecha: 2026-03-30

### Estado general
Se migra `roster_store` desde almacenamiento en memoria a persistencia real con SQLite.
Tests en verde y demo operativa.

### Qué quedó implementado

#### 1. Persistencia real de RosterVersion
- `roster_store.py` ahora usa SQLite
- Los rosters se almacenan en `data/swaps_atc.db`
- La tabla `roster_versions` se inicializa automáticamente si no existe

#### 2. Persistencia de asignaciones
- Las `asignaciones` asociadas a cada `RosterVersion` se serializan como JSON
- Se reconstruyen correctamente `Asignacion`, `Turno` y `Controlador`

#### 3. Interfaz preservada
- Se mantienen las funciones existentes:
  - `guardar_roster`
  - `obtener_roster`
  - `listar_rosters`
  - `listar_rosters_vigentes`
  - `validar_unico_roster_vigente`
  - `obtener_roster_vigente`
  - `desactivar_roster_vigente_actual`
  - `limpiar_rosters`
- Engine y simulator no necesitaron cambios de contrato

#### 4. Persistencia completa del núcleo
- `request_store` ya persistía en SQLite
- Ahora también `roster_store` persiste en SQLite
- El sistema deja atrás definitivamente el almacenamiento efímero en memoria para sus stores principales

#### 5. Validación general
- 46 tests passing
- Demo operativa sin regresiones funcionales

---

### Decisiones de diseño importantes

- se eligió persistir `asignaciones` como JSON en esta etapa para mantener baja complejidad
- se mantuvo compatibilidad con la interfaz existente del store
- la migración se hizo por sustitución interna, no por rediseño del engine

---

### Limitaciones actuales (conscientes)

- no existen migraciones formales de esquema
- `history` sigue siendo `list[str]`
- las asignaciones todavía no están normalizadas en tablas relacionales separadas

---

### Próximos pasos naturales

1. Limpieza y consolidación de helpers SQLite comunes
2. Agregar consultas operativas más ricas sobre rosters/versiones
3. Evaluar normalización futura de asignaciones si el dominio lo necesita
4. Recién después considerar una API mínima (FastAPI)

---

### Notas

Este checkpoint consolida la persistencia SQLite del núcleo del sistema:
- requests
- rosters
- versionado
- trazabilidad

## checkpoint-v6-taxonomia-alineada
Fecha: 2026-04-05

### Estado general
Se alinea la implementación con la taxonomía arquitectónica consolidada.
Tests en verde y flujo consistente.

### Qué quedó implementado

#### 1. Separación semántica estabilizada
Queda consolidada la separación entre:

- clasificación técnica
- decisión operativa
- estado del workflow

Taxonomía vigente:

- clasificación:
  - `BENEFICIOSO`
  - `ACEPTABLE`
  - `RECHAZABLE`

- decisión:
  - `VIABLE`
  - `OBSERVAR`
  - `RECHAZAR`

- estado:
  - `PENDIENTE`
  - `EVALUADO`
  - `APROBADO`
  - `RECHAZADO`
  - `CANCELADO`
  - `APLICADO`

#### 2. swap_service alineado a decisión y workflow
- `evaluar_swap_request(...)` traduce clasificación técnica a decisión operativa usando:
  - `BENEFICIOSO` → `VIABLE`
  - `ACEPTABLE` → `OBSERVAR`
  - `RECHAZABLE` → `RECHAZAR`

- `resolver_swap_request(...)` usa estado `APROBADO` como estado de aprobación formal
- `aplicar_swap_request(...)` exige `APROBADO` y mantiene la regla:
  - aplicar no reevalúa

#### 3. simulator mantenido dentro de contrato
- `simulator` conserva responsabilidad de evaluación técnica
- no se introdujo decisión operativa dentro de simulator
- se preservó la frontera:
  - simulator clasifica
  - swap_service decide

#### 4. Consistencia global
- tests ajustados a la taxonomía nueva
- mensajes, assertions y flujo alineados con el vocabulario vigente
- desaparecen los términos anteriores que generaban ambigüedad:
  - `APROBABLE`
  - `ACEPTADO`

### Decisiones de diseño importantes

- la clasificación técnica no expresa decisión
- la decisión operativa no expresa estado
- el estado refleja únicamente el ciclo de vida del request
- la aprobación formal del request se representa con `APROBADO`
- la viabilidad operativa se expresa con `VIABLE`

### Limitaciones actuales (conscientes)

- `simulator.py` todavía expone wrappers operativos que delegan en `swap_service`
- persisten mezclas menores dentro de `simulator.py` entre evaluación, utilidades y presentación
- la semántica exacta del objeto swap debe seguir vigilada para evitar ambigüedad entre asignación y turno

### Próximos pasos naturales

1. revisar frontera pública de `simulator.py`
2. limpiar mezcla interna no contractual en simulator
3. seguir endureciendo consistencia entre workflow, stores y auditoría
4. continuar consolidación documental de contratos e invariantes

### Notas

Este checkpoint consolida la taxonomía central del sistema y reduce una ambigüedad crítica entre:

- clasificación técnica
- decisión operativa
- estado del request

A partir de este punto, la implementación queda alineada con la arquitectura semántica definida.

## checkpoint-v7-simulator-boundary-clean
Fecha: 2026-04-07

### Estado general
Se elimina completamente la exposición de funciones operativas desde `simulator.py`.
El sistema queda alineado con la frontera arquitectónica definida entre evaluación técnica y workflow operativo.

### Qué quedó implementado

#### 1. Frontera estricta simulator ↔ swap_service
- `simulator` deja de exponer:
  - crear_swap_request
  - evaluar_swap_request
  - resolver_swap_request
  - aplicar_swap_request
- `swap_service` se consolida como única puerta para el ciclo de vida del request

#### 2. Separación de responsabilidades efectiva
- `simulator`:
  - evaluación técnica
  - cálculo de deltas
  - clasificación
- `swap_service`:
  - validación operativa
  - decisión
  - gestión de estado
  - aplicación

#### 3. Refactor de consumidores
- tests actualizados para consumir `swap_service`
- demo adaptada al flujo correcto
- eliminación de accesos indirectos al workflow

#### 4. Validación general
- tests en verde
- sin regresiones funcionales
- contratos respetados

---

### Decisiones de diseño reforzadas

- Decision 28: frontera simulator ↔ swap_service consolidada
- Decision 29: simulator no expone funciones operativas (implementada completamente)

---

### Impacto

- se elimina ambigüedad en uso del sistema
- se evita bypass del flujo operativo
- se mejora mantenibilidad y escalabilidad
- se refuerza modelo mental del sistema

---

### Notas

Este checkpoint marca el cierre de la separación efectiva entre:

- evaluación técnica
- decisión operativa
- ejecución

Convirtiendo al sistema en una arquitectura correctamente estratificada.

---

## checkpoint-v8-swap-service-hardened
Fecha: 2026-04-07

---

### Estado general

Se consolida el modulo `swap_service` como nucleo operativo del sistema, endureciendo invariantes, alineando la semantica de implementacion y completando la cobertura de tests sobre el workflow.

---

### Que quedo implementado

#### 1. Hardening del workflow operativo

- validaciones explicitas en cada transicion de estado
- proteccion contra:
  - doble evaluacion
  - doble aplicacion
  - resolucion en estados invalidos
- control estricto de versionado:
  - el request solo opera sobre el roster vigente

---

#### 2. Refactor interno controlado (sin impacto en arquitectura)

- extraccion de validaciones duplicadas en helpers privados:
  - validacion de indices
  - validacion de controladores vs roster
- mejora de legibilidad y mantenibilidad
- eliminacion de duplicacion logica sin modificar contratos

---

#### 3. Alineacion semantica completa

- eliminacion de residuos de nomenclatura:
  - `ACEPTADO` → `APROBADO`
- eliminacion de clasificacion tecnica ficticia en rechazos operativos
- separacion clara entre:
  - clasificacion tecnica
  - decision operativa

---

#### 4. Normalizacion de eventos de historial

Se unifica el formato de eventos:

- `REQUEST_EVALUADO`
- `REQUEST_EVALUADO_SIN_TECNICA`
- `REQUEST_RESUELTO`
- `REQUEST_CANCELADO_POR_OBSOLESCENCIA`
- `SWAP_APLICADO`

Esto mejora:

- trazabilidad
- debugging
- consistencia semantica

---

#### 5. Testing reforzado

- realineacion completa de tests a la API publica (`swap_service`)
- incorporacion de tests de borde:
  - doble evaluacion
  - doble aplicacion
  - evaluacion de request cancelado
  - resolucion invalida
- incorporacion de tests directos sobre `swap_service`
- validacion explicita de mensajes de error

---

### Validacion general

- suite completa en verde
- sin regresiones
- comportamiento deterministico validado
- coherencia entre codigo, tests y documentacion

---

### Decisiones de diseno reforzadas

- Decision 30: swap_service como unica autoridad del workflow operativo
- Decision 31: invariantes operativos explicitos y obligatorios
- Decision 32: separacion estricta entre evaluacion tecnica y decision operativa (reforzada a nivel implementacion)

---

### Impacto

- se refuerza la robustez del sistema
- se reduce riesgo de estados inconsistentes
- se mejora trazabilidad operativa
- se elimina ambiguedad semantica
- se prepara la base para evolucion sin deuda tecnica

---

### Notas

Este checkpoint marca la consolidacion del flujo completo de un SwapRequest:

- creacion
- evaluacion
- resolucion
- aplicacion

Con garantias explicitas de:

- consistencia
- control de estado
- integridad operativa

El sistema queda preparado para escalar en complejidad sin comprometer estabilidad.

---

## checkpoint-v9-engine-scoring-baseline
Fecha: 2026-04-07

---

### Estado general

Se consolida el bloque de engine y scoring como base del criterio de decision del sistema.  
La clasificacion de swaps y su traduccion a decisiones operativas quedan formalizadas, testeadas y alineadas con el dominio.

---

### Que quedo implementado

#### 1. Scoring base estabilizado

- separacion clara entre validacion hard y penalizaciones soft
- funcion de score definida y acotada
- el score no interviene aun en la decision directa, pero queda disponible como señal

---

#### 2. Clasificacion de swaps formalizada

- implementacion explicita de `clasificar_swap`
- reglas definidas:
  - RECHAZABLE si invalida o empeora a algun controlador
  - BENEFICIOSO si mejora sin perjudicar a nadie
  - ACEPTABLE si no empeora y no mejora significativamente
- criterio basado en:
  - impacto global
  - impacto por controlador

---

#### 3. Mapping decision operativo consolidado

- extraccion de `mapear_decision` a `scoring.py`
- eliminacion de logica hardcodeada en `swap_service`
- relacion establecida:
  - BENEFICIOSO → VIABLE
  - ACEPTABLE → OBSERVAR
  - RECHAZABLE → RECHAZAR

---

#### 4. Testing del motor de decision

- tests unitarios para mapping de decision
- tests unitarios para clasificacion de swaps
- cobertura de casos clave:
  - invalido nuevo
  - empeora controlador
  - mejora global
  - no mejora ni empeora
- test conceptual adicional:
  - mejora global sin deterioro individual → BENEFICIOSO

---

### Decisiones de diseno reforzadas

- Decision 33: la clasificacion es responsabilidad del motor tecnico, no del workflow
- Decision 34: la decision operativa es una transformacion de la clasificacion
- Decision 35: el deterioro de cualquier controlador invalida el swap
- Decision 36: la mejora global es suficiente si no hay perjuicio individual

---

### Limitaciones actuales (conscientes)

- el score no se utiliza aun para ranking ni priorizacion
- no existe ponderacion diferencial entre controladores
- la mejora se mide de forma agregada, no cualitativa
- no hay umbrales ni sensibilidad configurable en clasificacion

---

### Proximos pasos naturales

- implementacion de ranking de swaps basado en clasificacion y score
- exposicion de resultados ordenados para consumo operativo
- evaluacion futura de refinamiento del scoring

---

### Notas

Este checkpoint marca el cierre del modelo de decision del sistema:

- evaluacion tecnica
- clasificacion
- decision operativa

El sistema ya no solo ejecuta swaps correctamente, sino que define de forma consistente cuales swaps son mejores.

Queda preparado para evolucionar hacia funcionalidades orientadas a valor (ranking, sugerencias, optimizacion).

---

## checkpoint-v10-ranking-swaps
Fecha: 2026-04-07

---

### Estado general

Se incorpora la primera feature operativa real del sistema: ranking de swaps.
El sistema ya no solo evalua y clasifica swaps correctamente, sino que puede ordenar candidatos y exponer los mejores resultados de forma util para consumo operativo.

---

### Que quedo implementado

#### 1. Ranking tecnico de swaps

- refuerzo del criterio de ordenamiento en `explorar_swaps`
- priorizacion por clasificacion:
  - BENEFICIOSO
  - ACEPTABLE
  - RECHAZABLE
- desempate por:
  - validez del roster resultante
  - delta hard
  - delta total de violaciones
  - impacto tecnico

---

#### 2. Formalizacion del criterio de ranking

- incorporacion de helper privado para prioridad de clasificacion
- eliminacion de dependencia exclusiva del campo `impacto` como orden principal
- alineacion del ranking con el criterio semantico ya consolidado en engine/scoring

---

#### 3. Mejora de recomendacion textual

- la recomendacion deja de limitarse a informar clasificacion
- ahora explica por que el swap es:
  - beneficioso
  - aceptable
  - rechazable
- mejora de utilidad para lectura operativa y debugging

---

#### 4. Feature `obtener_top_swaps`

- incorporacion de funcion para devolver los mejores swaps recomendados
- soporte para:
  - limitar cantidad de resultados
  - incluir o excluir swaps aceptables
  - devolver recomendacion textual incluida
- primer punto de salida operativa usable del sistema

---

#### 5. Testing del ranking

- tests unitarios de ranking:
  - BENEFICIOSO por encima de ACEPTABLE
  - ACEPTABLE por encima de RECHAZABLE
  - mejor delta por encima de peor delta dentro de misma clasificacion
- test de `obtener_top_swaps` con limite de resultados
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- Decision 37: el ranking tecnico debe respetar la clasificacion antes que el impacto bruto
- Decision 38: el ordenamiento de swaps pertenece a simulator como capa tecnica de exploracion
- Decision 39: la exposicion de top swaps puede construirse sobre el ranking tecnico sin mezclar workflow operativo

---

### Limitaciones actuales (conscientes)

- el ranking no utiliza aun score combinado configurable
- no existe priorizacion por controlador o criterio de equidad
- no hay reporte operativo consolidado en formato final
- `obtener_top_swaps` devuelve estructura tecnica, no una vista de producto terminada

---

### Proximos pasos naturales

- generar reporte operativo de swaps recomendados
- evaluar refinamiento del ranking con score combinado
- explorar criterios futuros de priorizacion por controlador

---

### Notas

Este checkpoint marca el pasaje desde una base de evaluacion y decision a una capacidad concreta de recomendacion.
El sistema ya puede producir una lista ordenada de swaps utiles, explicando por que un candidato queda mejor posicionado que otro.

Queda preparado para evolucionar hacia una capa de salida operativa mas cercana al uso real.

---

## checkpoint-v11-reporte-operativo

### Estado
COMPLETADO

---

### Capacidades incorporadas

- generacion de reporte operativo de swaps recomendados
- exposicion de top swaps en formato legible para humano
- integracion con ranking tecnico existente
- inclusion de clasificacion y explicacion textual por swap

---

### Comportamiento del sistema

- el sistema puede producir una lista ordenada de swaps recomendados
- cada swap incluye:
  - identificacion clara de controladores, fechas y turnos
  - clasificacion (beneficioso / aceptable / rechazable)
  - explicacion del impacto
- salida lista para uso operativo directo (sin necesidad de interpretar estructuras internas)

---

### Validacion

- tests de generacion de reporte en verde
- integracion correcta con `obtener_top_swaps`
- consistencia semantica mantenida con engine y ranking

---

### Impacto

- el sistema pasa de evaluacion tecnica a salida operativa usable
- se habilita uso real del sistema para analisis de swaps
- mejora significativa en interpretabilidad y comunicacion de resultados

---

### Notas

Este checkpoint marca la primera capacidad completa de recomendacion:

- evaluar
- clasificar
- ordenar
- explicar
- presentar

El sistema ya puede ser utilizado como herramienta de apoyo en la toma de decisiones operativas.

---

## checkpoint-v12-equidad-historica-minima
Fecha: 2026-04-07

---

### Estado general

Se incorpora la primera implementación completa de equidad histórica en el sistema, manteniendo la arquitectura intacta.

El sistema pasa de ser puramente técnico (evaluación y ranking) a incorporar una señal temporal mínima que permite comenzar a distribuir beneficios entre controladores.

---

### Que quedo implementado

#### 1. Capa de priorizacion historica (modulo separado)

- creacion de `historical_prioritization.py`
- implementacion de:
  - deteccion de controladores beneficiados
  - score de equidad historica
  - reordenamiento soft de swaps
- integracion sin contaminar:
  - engine
  - scoring tecnico
  - clasificacion
  - workflow

---

#### 2. Integracion opt-in en simulator

- nuevas funciones:
  - `explorar_swaps_con_priorizacion_historica`
  - `explorar_swaps_entre_controladores_con_priorizacion_historica`
- comportamiento:
  - ranking tecnico intacto
  - ajuste solo dentro de misma clasificacion
  - sin promocion de swaps rechazables

---

#### 3. Tracking minimo de beneficios

- creacion de `historical_tracking.py`
- implementacion de:
  - deteccion de beneficios por controlador
  - contador `beneficios_recientes`
- modelo simple:
  - sin persistencia
  - sin ventana temporal compleja
  - sin decaimiento

---

#### 4. Hook en flujo real de aplicacion

- integracion en `aplicar_swap_request`
- comportamiento:
  - actualiza historial solo si se provee
  - no modifica flujo existente
  - no introduce reevaluacion
- mantiene contrato:
  - aplicar no reevalua
  - no afecta decision operativa

---

#### 5. Hardening del reporte operativo

- tolerancia a:
  - controladores nulos
  - fechas faltantes
  - turnos incompletos
  - clasificaciones desconocidas
- mejora robustez de salida operativa

---

#### 6. Testing completo

- tests unitarios:
  - priorizacion historica
  - tracking de beneficios
- test de integracion:
  - hook en `aplicar_swap_request`
- validacion:
  - sin regresiones
  - comportamiento deterministico
  - suite en verde

---

### Decisiones de diseno reforzadas

- Decision 30: equidad historica como señal soft
- Decision 31: equidad fuera de simulator (no contaminar capa tecnica)
- Decision 32: tracking desacoplado del modelo tecnico
- Decision 33: integracion via hook en flujo operativo (aplicar)

---

### Limitaciones actuales (conscientes)

- historial no persistente (solo en memoria)
- modelo historico simplificado:
  - solo contador de beneficios
- no hay ventana temporal real (conceptual)
- no hay decaimiento temporal
- no hay priorizacion por carga estructural (solo swaps)

---

### Proximos pasos naturales

- persistencia del historial por controlador
- definicion de ventana temporal real (ej: ultimos 3 rosters)
- refinamiento del modelo de equidad:
  - incorporar carga operativa
  - no solo swaps
- integracion automatica del historial en flujo completo
- visualizacion de equidad en reportes

---

### Notas

Este checkpoint marca el inicio del comportamiento adaptativo del sistema.

El sistema deja de ser completamente estático (solo reglas y estado actual) y comienza a incorporar memoria mínima de decisiones pasadas.

Se mantiene:
- consistencia técnica
- separación de capas
- trazabilidad

Se habilita:
- evolución hacia un sistema justo en escenarios de alta escala (78 controladores)

---

## checkpoint-v13-equidad-historica-minima
Fecha: 2026-04-07

---

### Estado general

Se completa la primera implementación operativa de equidad histórica en el sistema.

El sistema incorpora:
- priorización histórica como señal soft
- tracking mínimo de beneficios
- integración en el flujo real de aplicación

Sin alterar la arquitectura ni los contratos existentes.

---

### Que quedo implementado

#### 1. Priorizacion historica desacoplada

- módulo nuevo: `historical_prioritization.py`
- funcionalidades:
  - detección de controladores beneficiados
  - cálculo de score de equidad
  - reordenamiento soft de swaps
- comportamiento:
  - no modifica clasificación técnica
  - no altera impacto ni validez
  - solo reordena dentro de la misma clasificación

---

#### 2. Integracion en simulator (opt-in)

- nuevas funciones:
  - `explorar_swaps_con_priorizacion_historica`
  - `explorar_swaps_entre_controladores_con_priorizacion_historica`
- mantiene:
  - ranking técnico original
- agrega:
  - ajuste por equidad como desempate

---

#### 3. Tracking minimo de beneficios

- módulo nuevo: `historical_tracking.py`
- lógica:
  - identifica controladores beneficiados
  - incrementa `beneficios_recientes`
- características:
  - modelo simple
  - sin persistencia
  - sin ventana temporal real
  - sin decaimiento

---

#### 4. Integracion en flujo operativo

- hook en `aplicar_swap_request`
- comportamiento:
  - actualización opcional del historial
  - sin impacto si no se provee historial
  - sin reevaluación técnica
- respeta invariantes:
  - aplicar no reevalua
  - no modifica decisión

---

#### 5. Testing

- tests unitarios:
  - priorización histórica
  - tracking de beneficios
- test de integración:
  - verificación de hook en `swap_service`
- validación:
  - comportamiento determinístico
  - suite completa en verde

---

### Decisiones de diseño reforzadas

- Decision 30: equidad histórica como señal soft
- Decision 31: separación estricta de capas
- Decision 32: tracking desacoplado
- Decision 33: integración vía hook en aplicación

---

### Limitaciones actuales (conscientes)

- historial no persistente
- modelo simplificado (solo beneficios)
- no hay ventana temporal real
- no hay decaimiento
- no se considera carga estructural (solo swaps)

---

### Proximos pasos naturales

- persistencia del historial por controlador
- definición de ventana temporal (ej: últimos 3 rosters)
- incorporación de decaimiento temporal
- integración automática del historial en todo el flujo
- ampliación del modelo de equidad (más allá de swaps)

---

### Notas

Este checkpoint marca la transición hacia un sistema con memoria operativa mínima.

Se mantiene la pureza técnica del sistema,
pero se habilita una primera forma de distribución de beneficios en escenarios de alta escala.

---

## checkpoint-v14-historical-store-sqlite
Fecha: 2026-04-07

---

### Estado general

Se incorpora persistencia SQLite para el historial minimo de equidad historica.

El sistema deja de depender exclusivamente de estructuras en memoria para registrar beneficios recientes por controlador y pasa a contar con una base persistente desacoplada del motor tecnico.

---

### Que quedo implementado

#### 1. Store historico dedicado

- creacion de `historical_store.py`
- responsabilidad exclusiva:
  - inicializacion de tabla
  - lectura de historial por controlador
  - lectura multiple
  - incremento de beneficios recientes

---

#### 2. Nueva tabla SQLite para equidad

- tabla nueva para historial minimo por controlador
- estructura implementada:
  - `controlador`
  - `beneficios_recientes`
- modelo simple y estable
- sin mezclar con `request_store` ni con `roster_store`

---

#### 3. Integracion con historical_tracking

- `historical_tracking.py` pasa a actualizar:
  - estructura en memoria
  - persistencia SQLite
- se mantiene compatibilidad con flujo anterior
- no se modifica semantica tecnica del tracking

---

#### 4. Integracion con flujo operativo

- `aplicar_swap_request` mantiene hook de tracking historico
- al aplicar swaps:
  - puede actualizar historial minimo persistente
- no introduce:
  - reevaluacion
  - cambios en clasificacion
  - cambios en decision operativa

---

#### 5. Testing

- tests nuevos para `historical_store`
- validacion de:
  - lectura neutra si no existe controlador
  - incremento persistente
  - acumulacion de beneficios
  - formato compatible para priorizacion
- suite completa en verde

---

### Decisiones de diseno reforzadas

- Decision 34: persistencia historica en store separado
- Decision 35: no mezclar historial de equidad con stores operativos existentes
- Decision 36: tracking persistente minimo antes de introducir ventanas temporales

---

### Limitaciones actuales (conscientes)

- historial persistido aun reducido a `beneficios_recientes`
- no hay ventana temporal real
- no hay decaimiento
- no hay lectura automatica aun desde priorizacion
- no se persisten otras señales de carga o rezago

---

### Proximos pasos naturales

- consumo automatico del historial persistido desde priorizacion
- definicion de ventana temporal real
- incorporacion de decaimiento temporal
- ampliacion del modelo historico mas alla de beneficios simples

---

### Notas

Este checkpoint marca el cierre de la primera capa persistente de equidad historica.

El sistema ya puede almacenar memoria minima por controlador a lo largo del tiempo, preparando el terreno para que esa memoria sea utilizada automaticamente en el ranking de swaps.

---

## checkpoint-v15-equidad-automatica-desde-sqlite
Fecha: 2026-04-07

---

### Estado general

Se completa la integracion automatica de equidad historica en el sistema mediante persistencia SQLite.

La priorizacion historica deja de depender de estructuras manuales en memoria y pasa a consumir historial persistido de forma transparente, manteniendo intacta la arquitectura y los contratos existentes.

---

### Que quedo implementado

#### 1. Persistencia SQLite para equidad historica

- creacion de `historical_store.py`
- tabla nueva para historial minimo por controlador
- operaciones implementadas:
  - inicializacion
  - lectura individual
  - lectura multiple
  - incremento de beneficios recientes

---

#### 2. Tracking historico persistente

- integracion de escritura persistente en `historical_tracking.py`
- cada beneficio detectado:
  - actualiza estructura en memoria
  - actualiza tambien almacenamiento SQLite
- se mantiene compatibilidad con modelo previo

---

#### 3. Consumo automatico del historial

- `historical_prioritization.py` ya no depende obligatoriamente de un dict manual
- si no se provee historial:
  - detecta controladores involucrados
  - lee automaticamente historial persistido desde SQLite
- si no hay datos:
  - comportamiento neutro
  - sin romper flujo

---

#### 4. Integracion real en flujo de priorizacion

- la equidad historica pasa a ser usable en condiciones reales
- el ranking puede incorporar memoria operativa sin armado manual externo
- se mantiene:
  - clasificacion tecnica
  - score tecnico
  - impacto tecnico
  - decision operativa

---

#### 5. Testing

- tests nuevos para store historico
- tests de persistencia e incremento acumulado
- test de consumo automatico desde SQLite en priorizacion
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- Decision 34: persistencia historica desacoplada del motor tecnico
- Decision 35: lectura automatica del historial como comportamiento por defecto
- Decision 36: equidad historica sigue siendo señal soft, nunca criterio dominante

---

### Limitaciones actuales (conscientes)

- historial aun simplificado a `beneficios_recientes`
- no hay ventana temporal real
- no hay decaimiento
- no hay normalizacion por carga estructural
- no se exponen aun señales de equidad en el reporte operativo

---

### Proximos pasos naturales

- exponer equidad historica en reporte operativo
- definir ventana temporal real (ej: ultimos 3 rosters)
- incorporar decaimiento temporal
- ampliar el modelo historico mas alla de beneficios simples

---

### Notas

Este checkpoint marca el pasaje desde una equidad historica experimental a una equidad historica integrada al flujo real.

El sistema ya no solo recuerda beneficios pasados:
tambien los utiliza automaticamente para priorizar alternativas tecnicamente validas en escenarios de mayor escala.

---

## checkpoint-v16-equidad-visible-en-salida
Fecha: 2026-04-07

---

### Estado general

Se incorpora una señal contextual mínima de equidad histórica en la salida textual de recomendaciones.

El sistema comienza a comunicar, de forma no técnica, cuándo la priorización fue influenciada por la distribución reciente de carga entre controladores.

---

### Que quedo implementado

#### 1. Exposicion controlada de equidad

- integración en `generar_recomendacion_textual`
- agregado de una línea contextual cuando aplica:
  - "Considerando distribucion reciente de carga."
- no se exponen:
  - scores
  - valores numericos
  - detalles internos

---

#### 2. Activacion condicional

- la señal solo aparece cuando:
  - `ajuste_equidad == "APLICADO"`
- comportamiento neutro en el resto de los casos
- no genera ruido en recomendaciones tecnicas puras

---

#### 3. Integracion con modelo existente

- reutiliza:
  - `historical_prioritization`
  - señal `ajuste_equidad`
- no modifica:
  - ranking
  - clasificacion
  - impacto tecnico

---

#### 4. Lenguaje operativo

- wording alineado a contexto ATC:
  - "distribucion reciente de carga"
- evita terminologia tecnica:
  - equidad
  - score
  - algoritmo

---

### Decisiones de diseno reforzadas

- Decision 37: explicar solo cuando es necesario (no sobrecargar)
- Decision 38: lenguaje operativo por encima del tecnico
- Decision 39: transparencia controlada en sistemas multi-actor

---

### Limitaciones actuales (conscientes)

- no se expone informacion cuantitativa
- no hay visibilidad de equidad a nivel agregado
- no existe vista administrativa de distribucion

---

### Proximos pasos naturales

- definir si la señal debe aparecer en el reporte completo
- evaluar exposicion para perfiles administrativos
- incorporar visualizacion agregada de equidad

---

### Notas

Este checkpoint marca la transicion desde una equidad historica interna a una equidad historica visible.

Se mantiene el equilibrio entre:
- transparencia
- simplicidad
- no interferir con el flujo mental del controlador

---

Perfecto. Cerramos ambos checkpoints de forma ordenada.

🧾 checkpoint-v17-limpieza-salida-operativa
---

## checkpoint-v17-limpieza-salida-operativa
Fecha: 2026-04-07

---

### Estado general

Se realiza una limpieza integral de las salidas textuales del sistema, mejorando la consistencia, legibilidad y alineación con un uso operativo real.

No se introducen cambios en la lógica del sistema ni en los contratos existentes.

---

### Que quedo implementado

#### 1. Limpieza de recomendacion textual

- simplificacion de mensajes
- eliminacion de redundancias
- unificacion de estilo (sin tildes)
- mejora de claridad operativa

---

#### 2. Consistencia de lenguaje

- alineacion de textos entre:
  - recomendacion
  - reporte
- mensajes mas cortos y directos
- mejor integracion con lenguaje operativo real

---

#### 3. Ajuste de mensajes de error y fallback

- mejora en:
  - swaps con datos incompletos
  - indices fuera de rango
  - clasificaciones desconocidas
- mensajes mas claros y uniformes

---

#### 4. Limpieza menor de formato

- eliminacion de lineas en blanco innecesarias
- mejora de estructura visual del codigo

---

### Decisiones de diseno reforzadas

- Decision 37: separacion entre logica tecnica y presentacion textual
- Decision 38: lenguaje operativo por encima de lenguaje tecnico en salida
- Decision 39: consistencia de mensajes como parte de la calidad del sistema

---

### Limitaciones actuales (conscientes)

- no existe aun una vista operativa diferenciada (compacta vs detallada)
- la recomendacion textual sigue siendo relativamente extensa

---

### Proximos pasos naturales

- crear vista operativa compacta
- evaluar cual salida es mas adecuada para uso real
- separar explicitamente vistas:
  - tecnica
  - operativa

---

### Notas

Este checkpoint no cambia comportamiento del sistema.

Su objetivo es mejorar la interpretabilidad y preparar la salida para uso real en entorno ATC.

---

## checkpoint-v18-resumen-operativo-swaps
Fecha: 2026-04-07

---

### Estado general

Se incorpora una nueva vista operativa compacta para la recomendacion de swaps.

El sistema ahora ofrece dos niveles de salida:
- reporte detallado
- resumen operativo

---

### Que quedo implementado

#### 1. Nueva funcion de resumen operativo

- creacion de:
  - `generar_resumen_operativo_swaps`
- ubicada en `simulator`
- no modifica logica existente

---

#### 2. Vista compacta orientada a operacion

- informacion clave por swap:
  - controladores
  - fecha y turno
  - clasificacion
  - recomendacion
- formato reducido y facil de leer

---

#### 3. Manejo robusto de datos incompletos

- tolerancia a:
  - indices invalidos
  - controladores faltantes
  - fechas o turnos incompletos

---

#### 4. Integracion con flujo existente

- reutiliza:
  - `obtener_top_swaps`
  - evaluacion tecnica existente
- no recalcula ni altera ranking

---

#### 5. Testing

- test dedicado para la nueva funcion
- validacion de salida no vacia
- consistencia con comportamiento esperado

---

### Decisiones de diseno reforzadas

- Decision 40: separacion explicita entre salida detallada y salida operativa
- Decision 41: presentacion como responsabilidad del simulator
- Decision 42: vistas multiples sin duplicar logica

---

### Limitaciones actuales (conscientes)

- ambas vistas conviven sin definicion de uso oficial
- no hay seleccion dinamica de formato segun contexto
- no hay interfaz externa (CLI/UI)

---

### Proximos pasos naturales

- definir salida operativa oficial
- incorporar selector de formato (modo detallado vs compacto)
- evaluar integracion con interfaz de usuario

---

### Notas

Este checkpoint marca el paso desde una salida orientada a desarrollo hacia una salida usable en operacion real.

Se mantiene la coherencia con la arquitectura y se evita introducir logica duplicada.

---

## checkpoint-v19-equidad-eventos-y-decaimiento
Fecha: 2026-04-07

---

### Estado general

Se evoluciona el modelo de equidad historica desde un contador simple hacia un esquema basado en eventos persistidos, con ventana temporal configurable y decaimiento calculado en lectura.

La equidad historica mantiene su rol de señal soft de priorizacion, pero ahora con una base temporal mas realista para escenarios de escala.

---

### Que quedo implementado

#### 1. Modelo historico basado en eventos

- incorporacion de `historical_equity_events` como nueva fuente de informacion historica
- cada beneficio valido aplicado genera un evento persistido
- los eventos guardan:
  - controlador
  - swap_request_id
  - fecha_evento
  - tipo_evento

---

#### 2. Evolucion de historical_store

- `historical_store.py` pasa a soportar:
  - registro de eventos
  - listado de eventos por controlador
  - lectura derivada de historial
- se mantiene compatibilidad con el contador legacy durante la transicion

---

#### 3. Ventana temporal configurable

- incorporacion de ventana temporal deslizante en lectura
- primer modelo:
  - `ventana_dias`
- los eventos fuera de ventana dejan de aportar al score historico

---

#### 4. Decaimiento calculado en lectura

- implementacion de decaimiento lineal
- los eventos mas recientes pesan mas
- los eventos cercanos al limite de ventana pesan menos
- el decaimiento no se persiste

---

#### 5. Evolucion de historical_tracking

- el tracking deja de depender solo del contador agregado
- ahora:
  - mantiene compatibilidad en memoria
  - conserva contador legacy
  - registra eventos historicos validos
- solo swaps aplicados generan eventos

---

#### 6. Evolucion de historical_prioritization

- la priorizacion historica puede leer historial derivado desde eventos
- si no se provee historial manual:
  - detecta controladores involucrados
  - consulta historial persistido
  - aplica ventana + decaimiento
- se mantiene:
  - misma clasificacion tecnica
  - mismo workflow
  - mismo criterio de señal soft

---

#### 7. Testing

- nuevos tests para:
  - registro de eventos
  - lectura de eventos
  - ventana temporal
  - decaimiento
  - consumo automatico desde SQLite
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- Decision 40: el historial historico evoluciona a modelo basado en eventos
- Decision 41: la ventana temporal se aplica en lectura, no en persistencia
- Decision 42: el decaimiento se calcula on-the-fly
- Decision 43: los eventos aplicados son la fuente valida de memoria historica

---

### Limitaciones actuales (conscientes)

- se mantiene compatibilidad legacy durante la transicion
- el modelo sigue enfocado en beneficios, no en carga estructural completa
- el decaimiento es lineal y fijo
- no existe aun una definicion avanzada de controlador castigado
- no hay agregados ni vistas administrativas sobre eventos

---

### Proximos pasos naturales

- retirar progresivamente el contador simplificado legacy
- definir si la ventana temporal debe pasar a configuracion externa
- evaluar si el modelo de equidad debe incorporar:
  - carga estructural
  - noches
  - secuencias desfavorables
- estudiar si el decaimiento lineal sigue siendo suficiente

---

### Notas

Este checkpoint marca el pasaje desde una equidad historica minima y agregada hacia una equidad historica con dimension temporal real.

El sistema ya no solo recuerda que hubo beneficios:
tambien distingue cuando ocurrieron y cuanto deben seguir pesando en la priorizacion actual.

---

## checkpoint-v20-double-apply-test
Fecha: 2026-04-20

---

### Estado general

Se incorpora un test explícito para validar el comportamiento de no idempotencia de `aplicar_swap_request`, asegurando que un `SwapRequest` no pueda ser aplicado más de una vez.

Este checkpoint fortalece la robustez del sistema frente a reintentos indebidos, sin modificar lógica existente.

---

### Que quedo implementado

#### 1. Test explicito de doble aplicacion

- se agrega test especifico para validar que un `SwapRequest` ya aplicado no pueda volver a aplicarse
- el flujo cubierto es:
  - crear request
  - evaluar
  - aprobar
  - aplicar correctamente
  - intentar aplicar nuevamente
- el segundo intento debe fallar con error

---

#### 2. Cobertura explicita de no idempotencia

- se hace explicito mediante test que `aplicar_swap_request` es una operacion no idempotente
- se valida que el estado `APLICADO` actua como guard terminal
- se protege contra regresiones futuras en el flujo de aplicacion

---

#### 3. Sin cambios de logica productiva

- no se modifico comportamiento de:
  - `engine`
  - `scoring`
  - `simulator`
  - `swap_service`
- no se alteraron contratos
- no se modifico persistencia ni versionado
- el refuerzo es exclusivamente via testing

---

#### 4. Testing

- se agrega cobertura explicita sobre:
  - doble aplicacion de `SwapRequest`
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- `aplicar_swap_request` no es idempotente
- un request en estado `APLICADO` es terminal y no puede reutilizarse
- los guards de estado deben ser respetados estrictamente
- la validacion de flujo se refuerza mediante tests, no mediante logica redundante

---

### Limitaciones actuales (conscientes)

- no se cubren aun otros estados terminales (`RECHAZADO`, `CANCELADO`) en tests explicitos
- no se valida persistencia completa campo por campo
- no se valida explicitamente la no reevaluacion

---

### Proximos pasos naturales

- agregar test de aplicar sobre `RECHAZADO`
- agregar test de aplicar sobre `CANCELADO`
- avanzar sobre persistencia completa (roundtrip)
- evaluar test explicito de no reevaluacion

---

### Notas

Este checkpoint transforma un comportamiento ya implementado en una garantia verificable.

La no idempotencia de `aplicar_swap_request` deja de ser una propiedad implícita y pasa a estar protegida por la suite de tests.

---

## checkpoint-v21-apply-guards
Fecha: 2026-04-20

---

### Estado general

Se amplía la cobertura de tests sobre los guards de `aplicar_swap_request`, incorporando validación explícita para el estado terminal `RECHAZADO`.

El objetivo es asegurar que el sistema no permita la aplicación de requests fuera del flujo operativo válido.

---

### Que quedo implementado

#### 1. Test explicito de aplicar sobre request rechazado

- se agrega test especifico para validar que un `SwapRequest` en estado `RECHAZADO` no pueda aplicarse
- el test fuerza el estado terminal y verifica que `aplicar_swap_request` bloquee la operacion
- se valida el comportamiento esperado sin depender de la evaluacion tecnica

---

#### 2. Refuerzo de guards por estado terminal

- se hace explicito que solo requests en estado `APROBADO` son elegibles para aplicacion
- cualquier otro estado (`RECHAZADO`, `PENDIENTE`, `EVALUADO`, etc.) queda implicitamente bloqueado
- el test asegura que esta restriccion no se degrade en el futuro

---

#### 3. Sin cambios de logica productiva

- no se modifico comportamiento de:
  - `engine`
  - `scoring`
  - `simulator`
  - `swap_service`
- no se alteraron contratos
- no se modifico persistencia ni versionado
- el refuerzo es exclusivamente via testing

---

#### 4. Testing

- se agrega cobertura explicita sobre:
  - aplicar `SwapRequest` en estado `RECHAZADO`
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- `RECHAZADO` es un estado terminal incompatible con aplicacion
- los guards de `aplicar_swap_request` deben ser estrictos y deterministas
- el flujo operativo define claramente que solo `APROBADO` habilita la aplicacion
- la proteccion se implementa via tests, no via complejidad adicional

---

### Limitaciones actuales (conscientes)

- no se cubre aun el estado `CANCELADO` en test explicito
- no se valida persistencia exhaustiva
- no se valida explicitamente la no reevaluacion en aplicar

---

### Proximos pasos naturales

- agregar test de aplicar sobre `CANCELADO`
- completar cobertura de estados terminales
- avanzar sobre test de persistencia completa
- evaluar test de no reevaluacion

---

### Notas

Este checkpoint continúa el endurecimiento del flujo de aplicación.

Se transforma una restricción implícita del sistema en una garantía explícita protegida por tests, reduciendo el riesgo de regresiones en el manejo de estados terminales.

---

## checkpoint-v22-blindaje-aplicar-tests-explicitos
Fecha: 2026-04-20

---

### Estado general

Se refuerza la cobertura de tests sobre el flujo de aplicacion de `SwapRequest`, sin modificar logica productiva ni arquitectura.

El objetivo de este checkpoint fue cerrar huecos puntuales detectados en la verificacion de implementacion: proteger con evidencia explicita los guards de `aplicar_swap_request` para estados terminales y reintentos de aplicacion.

---

### Que quedo implementado

#### 1. Test explicito de doble aplicacion

- se agrega test especifico para validar que un `SwapRequest` ya aplicado no pueda volver a aplicarse
- el flujo cubierto es:
  - crear request
  - evaluar
  - aprobar
  - aplicar correctamente
  - intentar aplicar de nuevo
- el segundo intento debe fallar con error

---

#### 2. Test explicito de aplicar sobre request rechazado

- se agrega test especifico para validar que un `SwapRequest` en estado `RECHAZADO` no pueda aplicarse
- el test fuerza un estado terminal rechazado y verifica que `aplicar_swap_request` lo bloquee
- esto hace explicita una proteccion que ya existia en la logica general de guards

---

#### 3. Test explicito de aplicar sobre request cancelado

- se agrega test especifico para validar que un `SwapRequest` en estado `CANCELADO` no pueda aplicarse
- el test verifica que `aplicar_swap_request` rechace el intento de aplicacion sobre un request ya cancelado
- queda cubierto otro estado terminal critico del workflow

---

#### 4. Sin cambios de logica productiva

- no se modifico comportamiento de:
  - `engine`
  - `scoring`
  - `simulator`
  - `swap_service`
- no se alteraron contratos
- no se movieron responsabilidades entre capas
- no se toco persistencia ni versionado

---

#### 5. Testing

- se amplifica la cobertura sobre guards de `aplicar_swap_request`
- quedan ahora cubiertos de forma explicita:
  - doble aplicacion
  - aplicar sobre `RECHAZADO`
  - aplicar sobre `CANCELADO`
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- `aplicar_swap_request` sigue siendo una operacion terminal y no idempotente
- solo requests en estado `APROBADO` pueden aplicarse
- `RECHAZADO`, `CANCELADO` y `APLICADO` son estados incompatibles con aplicacion
- aplicar no reevalua ni reclasifica
- el endurecimiento actual se hace via tests, no via rediseño

---

### Limitaciones actuales (conscientes)

- todavia no se agrego test explicito de roundtrip exhaustivo de persistencia campo por campo
- todavia no se agrego test explicito de no reevaluacion mediante aislamiento o verificacion negativa
- parte del blindaje sigue validado por inspeccion de codigo y cobertura indirecta, no siempre por test quirurgico dedicado

---

### Proximos pasos naturales

- agregar test de persistencia exhaustiva de `SwapRequest` en roundtrip completo
- evaluar test explicito de no reevaluacion en `aplicar_swap_request`
- revisar si conviene endurecer aun mas la cobertura de estados terminales en `resolver_swap_request`
- continuar limpieza incremental de cobertura sin tocar arquitectura

---

### Notas

Este checkpoint no cambia el sistema:
lo vuelve mas defendible.

La implementacion ya estaba correctamente blindada en logica.
Lo que se hizo aca fue transformar protecciones implicitas o generales en evidencia de test explicita, reduciendo riesgo de regresion futura en el workflow de aplicacion.

---

## checkpoint-v23-request-roundtrip-test
Fecha: 2026-04-20

---

### Estado general

Se incorpora un test exhaustivo de persistencia para `SwapRequest`, validando el comportamiento completo de serialización y deserialización (roundtrip) contra SQLite.

Este checkpoint cierra el último hueco relevante detectado en la verificación de implementación, garantizando que todos los campos críticos del modelo se preservan correctamente en almacenamiento.

---

### Que quedo implementado

#### 1. Test de roundtrip completo de SwapRequest

- se agrega test especifico para validar persistencia completa de un `SwapRequest`
- el flujo cubierto es:
  - creación manual del request con todos los campos relevantes
  - guardado en SQLite mediante `guardar_request`
  - recuperación mediante `obtener_request`
  - comparación campo por campo

---

#### 2. Cobertura exhaustiva de campos

El test valida explícitamente la preservación de:

- `id`
- `controlador_a`
- `controlador_b`
- `idx_a`
- `idx_b`
- `estado`
- `fecha_creacion`
- `fecha_resolucion`
- `decision_sugerida`
- `motivo`
- `history`
- `roster_hash`
- `roster_version_id`

---

#### 3. Validacion de serializacion y deserializacion

- se valida que:
  - fechas se serializan correctamente (ISO) y se reconstruyen sin pérdida
  - `history` se serializa como JSON y se recupera correctamente como lista
  - los campos opcionales y obligatorios mantienen coherencia semántica

---

#### 4. Sin cambios de logica productiva

- no se modifico comportamiento de:
  - `models`
  - `request_store`
  - `db`
- no se alteraron contratos
- no se modifico estructura de base de datos
- el refuerzo es exclusivamente via testing

---

#### 5. Testing

- se agrega test integral de persistencia completa
- se complementan los tests parciales existentes
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- `SwapRequest` es una entidad completamente persistible sin pérdida de información relevante
- la capa de persistencia debe ser determinista y reversible (roundtrip confiable)
- la integridad de datos no depende de uso parcial del modelo
- los campos críticos del dominio deben ser verificables en conjunto

---

### Limitaciones actuales (conscientes)

- no se valida aún comportamiento ante datos corruptos en base
- no se testea concurrencia o condiciones de carrera en persistencia
- no se cubren escenarios de migración de esquema

---

### Proximos pasos naturales

- evaluar test de no reevaluación explícita en `aplicar_swap_request`
- considerar tests de integridad ante errores de persistencia
- explorar validaciones defensivas adicionales en deserialización
- analizar necesidad de tests de concurrencia en el store

---

### Notas

Este checkpoint eleva la garantía de integridad de datos del sistema.

La persistencia deja de estar validada por fragmentos y pasa a estar protegida como unidad completa, reduciendo significativamente el riesgo de errores silenciosos en almacenamiento y recuperación.

---

Excelente. Con esto cerraste todos los invariantes críticos del sistema.

Estado real después de v24

Tenés cubierto explícitamente:

Guards de aplicación
✔ no evaluado → bloquea
✔ no aprobado → bloquea
✔ RECHAZADO → bloquea
✔ CANCELADO → bloquea
✔ doble aplicación → bloquea
Persistencia
✔ roundtrip completo garantizado
Flujo crítico
✔ aplicar no reevalúa (test explícito)
Arquitectura
✔ separación de capas intacta
✔ contratos respetados
✔ invariantes protegidos por tests

👉 Esto ya es nivel producción robusta, no prototipo.

Commit y tag
git add .
git commit -m "add explicit test ensuring aplicar does not reevaluate"
git tag checkpoint-v24-no-reevaluacion-test
Checkpoint v24 (listo para copiar/pegar)
## checkpoint-v24-no-reevaluacion-test
Fecha: 2026-04-20

---

### Estado general

Se incorpora un test explícito para validar que `aplicar_swap_request` no depende de evaluación técnica ni reingresa al flujo de evaluación.

Este checkpoint cierra el último invariante crítico del sistema a nivel de workflow operativo.

---

### Que quedo implementado

#### 1. Test explicito de no reevaluacion

- se agrega test especifico para validar que `aplicar_swap_request` no llama a `evaluar_swap_request`
- el test utiliza monkeypatch para reemplazar la función de evaluación por una versión que falla
- si el flujo de aplicar intentara reevaluar, el test falla inmediatamente

---

#### 2. Aislamiento completo de la fase de aplicación

- se valida que:
  - la evaluación ocurre exclusivamente en la fase de evaluación
  - la decisión ocurre en la fase de resolución
  - la aplicación no depende de lógica técnica adicional
- `aplicar_swap_request` actúa únicamente sobre estado ya decidido

---

#### 3. Sin cambios de logica productiva

- no se modifico comportamiento de:
  - `engine`
  - `scoring`
  - `simulator`
  - `swap_service`
- no se alteraron contratos
- no se modifico persistencia ni versionado
- el refuerzo es exclusivamente via testing

---

#### 4. Testing

- se agrega cobertura explícita sobre:
  - no reevaluación en aplicar
- validacion completa en verde

---

### Decisiones de diseno reforzadas

- `aplicar_swap_request` no reevalúa ni reclasifica
- la clasificación técnica es responsabilidad exclusiva del `simulator`
- la decisión operativa es responsabilidad exclusiva de `swap_service`
- la aplicación es una operación terminal que no altera evaluación previa
- se refuerza la separación estricta entre evaluación, decisión y aplicación

---

### Limitaciones actuales (conscientes)

- no se testea aún comportamiento ante corrupción de datos en persistencia
- no se cubren escenarios de concurrencia en aplicación
- no se validan condiciones de carrera sobre versiones de roster

---

### Proximos pasos naturales

- evaluar mecanismos de bloqueo de concurrencia en aplicación
- analizar consistencia bajo escenarios simultáneos
- explorar herramientas de observabilidad del sistema
- avanzar hacia escenarios de uso real o integración

---

### Notas

Este checkpoint cierra el núcleo lógico del sistema.

A partir de este punto, el sistema no solo está correctamente diseñado:
también está defendido contra regresiones en sus invariantes más críticos.

---

## checkpoint-v25-roster-index-candidate-generation-v1
Fecha: 2026-04-20

---

### Estado general

Se implementa una primera version minima y segura de exploracion acotada mediante dos nuevas piezas arquitectonicas:

- `roster_index`
- `candidate_generation`

El objetivo de este checkpoint es introducir una base escalable para generacion de candidatos plausibles, sin tocar la evaluacion tecnica ni el workflow operativo existente.

---

### Que quedo implementado

#### 1. Nuevo modulo `roster_index`

- se incorpora `src/roster_index.py`
- se implementa una estructura derivada `RosterIndex`
- se agrega `build_roster_index(asignaciones)`

El indice expone como minimo:

- `by_date`
- `by_date_turno`
- `by_controller`
- `future_window`

---

#### 2. `roster_index` como estructura derivada

- `roster_index` se construye desde asignaciones dadas
- no es fuente de verdad
- no persiste
- no evalua
- no decide
- no crea requests

Su funcion en esta v1 es acelerar acceso y recorte de universo elegible.

---

#### 3. Nuevo modulo `candidate_generation`

- se incorpora `src/candidate_generation.py`
- se implementa generacion acotada de candidatos
- se soportan casos minimos:
  - cambio dentro del mismo dia
  - cambio hacia dias futuros

Se implementan funciones de generacion sobre asignaciones candidatas plausibles para simulacion posterior.

---

#### 4. Filtros baratos aplicados

`candidate_generation` aplica solo filtros baratos, compatibles con su contrato:

- exclusion de la misma asignacion exacta
- exclusion del mismo controlador
- mismo dia para exploracion same-day
- fecha origen hacia adelante para exploracion future

No se agregan filtros caros ni evaluacion tecnica.

---

#### 5. Sin invasion de capas tecnicas

- no se toca `engine`
- no se toca `scoring`
- no se toca `swap_service`
- no se toca persistencia
- no se modifica `simulator.py` en esta v1

`candidate_generation` no:

- clasifica
- calcula score
- decide
- crea `SwapRequest`
- invoca evaluacion hard completa

---

#### 6. Testing

Se agregan tests nuevos para:

##### `tests/test_roster_index.py`
- construccion correcta de `by_date`
- construccion correcta de `by_date_turno`
- construccion correcta de `by_controller`
- construccion correcta de `future_window`
- no perdida de asignaciones
- no duplicacion de asignaciones

##### `tests/test_candidate_generation.py`
- candidatos same-day
- candidatos future
- exclusion de mismo controlador
- exclusion de fechas anteriores
- contrato de retorno como asignaciones
- ausencia de clasificacion o decision

Validacion:
- tests nuevos en verde
- suite completa en verde

---

### Decisiones de diseno reforzadas

- la generacion de candidatos debe estar separada de la evaluacion tecnica
- `roster_index` es solo una vista derivada del roster
- `candidate_generation` construye universo plausible, no universo total
- la exploracion acotada reemplaza conceptualmente a la exploracion global exhaustiva como direccion futura del sistema

---

### Limitaciones actuales (conscientes)

- esta v1 aun no integra el flujo acotado dentro de `simulator`
- no reemplaza todavia el brute force existente
- los filtros son intencionalmente baratos y conservadores
- aun no existe benchmark comparativo entre brute force y candidate generation acotado
- no se modela todavia una entidad explicita de necesidad o request context

---

### Proximos pasos naturales

- integrar un punto minimo en `simulator` para consumir `roster_index` + `candidate_generation`
- medir benchmark comparativo entre exploracion global y generacion acotada
- definir contrato de entrada para exploracion centrada en necesidad concreta
- evaluar refinamientos adicionales de filtros baratos sin invadir evaluacion tecnica

---

### Notas

Este checkpoint no cambia la evaluacion tecnica del sistema.

Introduce la primera base concreta para escalar la generacion de candidatos sin caer en exploracion global exhaustiva, preservando la arquitectura vigente y manteniendo intactas las responsabilidades de cada capa.

---

## checkpoint-v26-simulator-bounded-candidate-entrypoint
Fecha: 2026-04-20

---

### Estado general

Se incorpora una integracion minima y segura en `simulator.py` para habilitar exploracion acotada de candidatos usando:

- `roster_index`
- `candidate_generation`

El objetivo de este checkpoint es conectar la nueva generacion acotada con el simulador sin tocar el flujo brute force existente.

---

### Que quedo implementado

#### 1. Nueva funcion en `simulator.py`

- se agrega `explorar_candidatos_acotados(asignacion_origen, asignaciones, modo="auto")`
- la funcion:
  - construye `roster_index`
  - invoca `generate_candidates`
  - devuelve candidatos crudos

---

#### 2. Integracion minima y no invasiva

- no se reemplaza `explorar_swaps_entre_controladores`
- no se elimina el brute force existente
- no se altera la evaluacion tecnica vigente
- no se cambia clasificacion ni scoring

`simulator` actua solo como orquestador de la nueva exploracion acotada.

---

#### 3. Contrato preservado

La nueva funcion:

- no evalua
- no clasifica
- no decide
- no crea `SwapRequest`
- no persiste

Devuelve exclusivamente asignaciones candidatas plausibles para simulacion posterior.

---

#### 4. Testing

Se agregan tests nuevos en `tests/test_simulator_candidate_generation.py` para validar:

- que `explorar_candidatos_acotados` devuelve lista
- que `same_day` funciona
- que `future` funciona
- que no rompe el simulator existente
- que no devuelve `SwapRequest`
- que no clasifica ni decide
- que usa correctamente `candidate_generation`

Validacion:
- tests nuevos en verde
- suite completa en verde

---

### Decisiones de diseno reforzadas

- `simulator` puede orquestar exploracion acotada sin absorber responsabilidades de generacion
- `candidate_generation` sigue siendo la capa de construccion del universo plausible
- la exploracion acotada se integra como camino nuevo, no como reemplazo abrupto del brute force
- se mantiene separacion estricta entre:
  - generacion de candidatos
  - evaluacion tecnica
  - decision operativa

---

### Limitaciones actuales (conscientes)

- `explorar_candidatos_acotados` aun devuelve candidatos crudos y no evaluados
- no existe aun benchmark comparativo formal entre brute force y exploracion acotada
- no se reemplazo todavia ningun flujo operativo existente por el nuevo camino
- no se introdujo aun una entidad explicita de necesidad concreta o request context

---

### Proximos pasos naturales

- medir benchmark comparativo entre exploracion global y exploracion acotada
- definir si el simulador debe ofrecer una variante que evalue tecnicamente solo los candidatos acotados
- analizar integracion posterior con flujo centrado en request o necesidad concreta
- estudiar si la nueva exploracion acotada debe convertirse en camino preferente del sistema

---

### Notas

Este checkpoint completa la primera cadena funcional de exploracion acotada:

- indice derivado
- generacion acotada
- punto de entrada en simulator

Con esto, el sistema ya dispone de una base concreta para abandonar progresivamente la exploracion global exhaustiva sin romper la arquitectura vigente.

---

## checkpoint-v27-comparative-exploration-benchmark
Fecha: 2026-04-20

---

### Estado general

Se incorpora un benchmark comparativo seguro entre:

- exploracion global exhaustiva (brute force)
- exploracion acotada centrada en asignacion origen

El objetivo de este checkpoint es medir escalabilidad operativa sin tocar codigo productivo ni forzar ejecuciones fuera de rango temporal.

---

### Que quedo implementado

#### 1. Nuevo benchmark comparativo

- se agrega `tools/benchmark_comparativo_exploracion.py`
- compara:
  - `explorar_swaps_entre_controladores`
  - `explorar_candidatos_acotados`
- usa escenarios escalados para:
  - 80 controladores
  - 120 controladores
  - 180 controladores

---

#### 2. Estrategia segura de medicion

- el benchmark no fuerza ejecucion brute force cuando el universo excede el umbral definido
- en esos casos reporta `NO_EJEC`
- se mantiene:
  - cantidad de pares brutos estimados
  - medicion real del camino acotado
  - factor de reduccion del universo

Esto evita benchmarks inutilmente largos o fuera de rango operativo.

---

#### 3. Resultado comparativo principal

Resultados observados:

- 80 controladores:
  - brute total: 12640
  - acotado total: 158
  - reduccion: 80x
  - acotado ms: ~0.36

- 120 controladores:
  - brute total: 28560
  - acotado total: 238
  - reduccion: 120x
  - acotado ms: ~0.50

- 180 controladores:
  - brute total: 64440
  - acotado total: 358
  - reduccion: 180x
  - acotado ms: ~0.78

---

#### 4. Confirmacion de limite operativo del brute force

- el brute force global queda explicitamente fuera de rango operativo en escalas reales del dominio
- la exploracion acotada se mantiene en tiempos sub-milisegundo para las escalas medidas
- queda validada empiricamente la direccion arquitectonica adoptada

---

#### 5. Sin cambios de logica productiva

- no se toca:
  - `engine`
  - `scoring`
  - `swap_service`
  - `simulator.py`
  - `candidate_generation`
  - `roster_index`
  - persistencia
  - tests
- el benchmark vive exclusivamente en `tools/`

---

### Decisiones de diseno reforzadas

- la exploracion global exhaustiva no es un camino operativo viable para dotaciones reales ATC
- la exploracion acotada centrada en una asignacion origen reduce drasticamente el universo candidato
- la estrategia arquitectonica basada en `roster_index` + `candidate_generation` queda respaldada por evidencia de escala
- el brute force puede permanecer como referencia o herramienta auxiliar, no como camino preferente

---

### Limitaciones actuales (conscientes)

- la comparacion no busca equivalencia funcional exacta entre ambos caminos
- la exploracion acotada se mide desde una asignacion origen concreta
- el brute force en escalas altas no se ejecuta realmente en modo seguro
- aun no existe una variante integrada que evalue tecnicamente solo los candidatos acotados

---

### Proximos pasos naturales

- definir si la exploracion acotada pasa a ser camino preferente del sistema
- agregar una variante que simule tecnicamente solo los candidatos acotados
- medir pipeline completo:
  - generacion acotada
  - simulacion tecnica
  - ranking posterior
- decidir el rol residual del brute force en el sistema

---

### Notas

Este checkpoint no optimiza brute force:
demuestra que ya no hace falta insistir con el como camino principal.

La evidencia de escala respalda que el sistema debe evolucionar hacia generacion acotada de candidatos seguida de simulacion tecnica selectiva.

---

## checkpoint-v28-bounded-technical-evaluation-flow
Fecha: 2026-04-20

---

### Estado general

Se incorpora una nueva variante en `simulator.py` para evaluar tecnicamente solo los candidatos generados por exploracion acotada.

Con este checkpoint queda completa la primera cadena funcional de exploracion escalable del sistema:

- `roster_index`
- `candidate_generation`
- `explorar_candidatos_acotados`
- `explorar_y_evaluar_candidatos_acotados`

---

### Que quedo implementado

#### 1. Nueva funcion en `simulator.py`

- se agrega `explorar_y_evaluar_candidatos_acotados(asignacion_origen, asignaciones, modo="auto", config_file="config_equilibrado.json")`
- la funcion:
  - usa `explorar_candidatos_acotados(...)`
  - localiza indices en `asignaciones`
  - evalua tecnicamente cada candidato con `evaluar_swap(...)`
  - devuelve resultados tecnicos reales del simulator

---

#### 2. Evaluacion tecnica selectiva

- ya no se depende de exploracion global exhaustiva para obtener resultados tecnicos
- el flujo nuevo toma un subconjunto acotado de candidatos plausibles
- luego ejecuta evaluacion tecnica real solo sobre ese subconjunto

Esto convierte la exploracion acotada en un camino util y completo para simulacion tecnica.

---

#### 3. Contrato preservado

La nueva funcion:

- no crea `SwapRequest`
- no decide
- no persiste
- no invoca `swap_service`
- no altera scoring
- no altera clasificacion tecnica

`simulator` se mantiene como capa de evaluacion tecnica y orquestacion.

---

#### 4. Sin ruptura del flujo existente

- no se reemplaza `explorar_swaps_entre_controladores`
- no se elimina brute force
- no se modifica el flujo global existente
- el nuevo camino convive como variante integrada y separada

---

#### 5. Testing

Se agregan tests nuevos en `tests/test_simulator_bounded_evaluation.py` para validar:

- que la nueva funcion devuelve lista
- que `same_day` funciona
- que `future` funciona
- que los elementos devueltos contienen evaluacion tecnica real
- que no devuelve `SwapRequest`
- que no decide ni agrega decision operativa
- que no rompe el simulator existente
- que la clasificacion tecnica sigue siendo la vigente del sistema

Validacion:
- tests nuevos en verde
- suite completa en verde

---

### Decisiones de diseno reforzadas

- la generacion de candidatos sigue separada de la evaluacion tecnica
- `simulator` puede evaluar tecnicamente solo un subconjunto acotado sin absorber responsabilidades de generacion
- la estrategia escalable del sistema queda alineada con:
  - prefiltrado barato
  - simulacion tecnica selectiva
  - preservacion del contrato tecnico vigente

---

### Limitaciones actuales (conscientes)

- el flujo nuevo aun no esta integrado a ningun camino operativo preferente del sistema
- no reemplaza todavia el brute force global
- no existe aun un pipeline completo que conecte esta salida tecnica con ranking operativo final
- falta benchmark especifico del flujo acotado + evaluacion tecnica completa

---

### Proximos pasos naturales

- benchmark del flujo completo:
  - exploracion acotada
  - evaluacion tecnica selectiva
- definir si este camino pasa a ser preferente frente al brute force
- integrar el flujo acotado evaluado con ranking o consumo posterior
- decidir el rol residual del brute force en el sistema

---

### Notas

Este checkpoint marca el pasaje desde una exploracion acotada solo generativa hacia una exploracion acotada tecnicamente util.

El sistema ya no solo puede recortar el universo:
tambien puede evaluarlo tecnicamente de forma selectiva y escalable.

---

## checkpoint-v29-bounded-evaluated-flow-benchmark
Fecha: 2026-04-20

---

### Estado general

Se incorpora un benchmark especifico para medir el flujo completo acotado evaluado del sistema:

- generacion acotada de candidatos
- evaluacion tecnica selectiva

El objetivo de este checkpoint es validar si el nuevo camino escalable queda en rango operativo util una vez incluida la evaluacion tecnica real del simulator.

---

### Que quedo implementado

#### 1. Nuevo benchmark del flujo acotado evaluado

- se agrega `tools/benchmark_flujo_acotado_evaluado.py`
- el benchmark:
  - toma `asignaciones[0]` como `asignacion_origen`
  - ejecuta `explorar_y_evaluar_candidatos_acotados(...)`
  - mide tiempo total del flujo
  - reporta cantidad de candidatos evaluados
  - reporta conteo por clasificacion tecnica

---

#### 2. Escalas medidas

Se mide el flujo completo sobre escenarios escalados para:

- 80 controladores
- 120 controladores
- 180 controladores

---

#### 3. Resultados observados

Resultados obtenidos:

- 80 controladores
  - asignaciones: 160
  - flujo: ~12426 ms
  - evaluados: 158
  - BENEFICIOSO: 0
  - ACEPTABLE: 0
  - RECHAZABLE: 158

- 120 controladores
  - asignaciones: 240
  - flujo: ~28435 ms
  - evaluados: 238
  - BENEFICIOSO: 0
  - ACEPTABLE: 0
  - RECHAZABLE: 238

- 180 controladores
  - asignaciones: 360
  - flujo: ~63475 ms
  - evaluados: 358
  - BENEFICIOSO: 0
  - ACEPTABLE: 0
  - RECHAZABLE: 358

---

#### 4. Conclusiones tecnicas del benchmark

- la generacion acotada sigue reduciendo correctamente el universo candidato
- el cuello dominante del flujo completo ya no es la combinatoria global
- el cuello pasa a ser la evaluacion tecnica individual por candidato
- el sistema mejora radicalmente frente al brute force global, pero el flujo completo aun no queda en rango operativo comodo para escalas altas

---

#### 5. Sin cambios de logica productiva

- no se toca `src/`
- no se modifica:
  - `engine`
  - `scoring`
  - `swap_service`
  - `candidate_generation`
  - `roster_index`
  - `simulator.py`
- el benchmark vive exclusivamente en `tools/`

---

### Decisiones de diseno reforzadas

- la estrategia de exploracion acotada fue correcta y necesaria
- el problema combinatorio global queda resuelto conceptualmente
- el siguiente cuello del sistema ya no es la generacion del universo
- el siguiente cuello esta en el costo de evaluacion tecnica selectiva por candidato

---

### Limitaciones actuales (conscientes)

- el benchmark usa una `asignacion_origen` fija (`asignaciones[0]`)
- el escenario escalado puede no representar distribucion operativa real de casos utiles
- todos los candidatos resultaron `RECHAZABLE`, lo cual puede reflejar:
  - origen poco representativo
  - escenario artificialmente restrictivo
  - filtros baratos aun demasiado amplios
- no se perfila internamente en que subpasos exactos se consume el tiempo de evaluacion tecnica

---

### Proximos pasos naturales

- discutir en arquitectura el nuevo cuello de botella
- decidir si la proxima palanca es:
  - endurecer filtros baratos
  - introducir una prevalidacion tecnica ligera
  - optimizar el pipeline de evaluacion tecnica selectiva
- medir costo interno por candidato y por subpaso tecnico
- definir si el flujo acotado evaluado puede convertirse en camino operativo preferente tras una nueva iteracion

---

### Notas

Este checkpoint confirma que la arquitectura nueva resolvio el problema correcto:
la combinatoria.

El sistema ya no falla por explorar demasiado.
Ahora el problema esta en cuanto cuesta evaluar tecnicamente cada candidato que sobrevive al recorte inicial.

---

Contexto: sistema de swaps ATC en Python.

Estado actual:
- exploracion global exhaustiva descartada
- roster_index implementado
- candidate_generation implementado
- simulator ya tiene:
  - explorar_candidatos_acotados(...)
  - explorar_y_evaluar_candidatos_acotados(...)
- benchmark actual muestra:
  - universo ya reducido
  - pero costo aun alto en evaluacion tecnica completa
  - casi todos los candidatos terminan RECHAZABLE

Decision arquitectonica ya tomada:
Agregar una capa intermedia de prevalidacion tecnica ligera entre:
- candidate_generation
- simulator

---

Modo de trabajo:
IMPLEMENTACION CONTROLADA

---

Arquitectura vigente (NO TOCAR)

- engine = validacion de reglas y configuracion
- scoring = validez tecnica y score tecnico
- simulator = evaluacion tecnica y clasificacion
- swap_service = workflow operativo
- candidate_generation = generacion acotada de candidatos
- roster_index = estructura derivada del roster

---

Restricciones duras

NO tocar:
- engine
- scoring
- swap_service
- persistencia
- request_store
- roster_store
- modelos
- candidate_generation.py
- roster_index.py
- benchmarks existentes
- docs
- checkpoints

NO hacer:
- refactor
- cambios de arquitectura
- cambios semanticos
- cambios en clasificacion tecnica
- cambios en scoring tecnico
- cambios en contratos existentes
- optimizacion ciega de simulator
- paralelizacion
- caching masivo
- limpieza oportunista

NO introducir:
- decision operativa en simulator
- evaluacion tecnica completa en candidate_generation
- logica hard completa en prefilter
- score en prefilter
- clasificacion en prefilter
- persistencia en prefilter
- requests en prefilter

---

Objetivo funcional

Implementar una v1 minima y segura de una nueva capa:

- src/technical_prefilter.py

e integrarla de forma minima en simulator.py para crear un flujo:

candidate_generation
→ technical_prefilter
→ simulator

sin romper nada existente.

---

Contrato esperado de la nueva capa

## technical_prefilter
Debe:
- descartar solo inviabilidad tecnica obvia
- ser barata
- ser conservadora
- trabajar sobre:
  - asignacion_origen
  - candidatos
  - asignaciones del roster

No debe:
- clasificar
- puntuar
- decidir
- persistir
- crear SwapRequest
- reemplazar simulator

---

Diseno minimo esperado

## src/technical_prefilter.py

Implementar funciones minimas equivalentes a:

- is_candidate_technically_plausible(asignacion_origen, asignacion_candidata, asignaciones) -> bool
- filter_technically_plausible_candidates(asignacion_origen, candidatos, asignaciones) -> list

Mantener implementacion extremadamente conservadora en esta v1.

Chequeos admitidos en v1:
- excluir mismo controlador
- excluir misma asignacion exacta
- excluir intercambio trivial sin cambio real
- solo chequeos locales, baratos y obvios

NO meter en esta v1:
- descanso minimo completo
- secuencias completas
- noches consecutivas
- dotacion minima
- score
- clasificacion
- validez hard completa del roster

---

Integracion minima en simulator.py

Agregar una funcion nueva y separada.

Nombre sugerido:
- explorar_y_evaluar_candidatos_con_prefiltro(...)
o equivalente claro y consistente

Debe:
1. usar explorar_candidatos_acotados(...)
2. pasar por technical_prefilter
3. evaluar tecnicamente solo los sobrevivientes
4. devolver resultados tecnicos reales del simulator

No reemplazar:
- explorar_swaps_entre_controladores
- explorar_candidatos_acotados
- explorar_y_evaluar_candidatos_acotados

Solo agregar una nueva variante.

---

Tests a agregar

Crear:
- tests/test_technical_prefilter.py
- tests/test_simulator_prefiltered_bounded_evaluation.py

Validar como minimo:

## test_technical_prefilter.py
- devuelve lista
- excluye mismo controlador
- excluye misma asignacion exacta
- no clasifica
- no decide
- no devuelve requests
- mantiene candidatos plausibles simples

## test_simulator_prefiltered_bounded_evaluation.py
- la nueva funcion devuelve lista
- same_day funciona
- future funciona
- usa prefilter antes de evaluar
- no rompe simulator existente
- no crea requests
- no decide
- mantiene clasificacion tecnica real en la salida

Usar escenarios existentes del proyecto si sirven.
No crear fixtures complejos innecesarios.

---

Benchmark por etapas

Crear:
- tools/benchmark_flujo_acotado_prefiltrado.py

Debe reportar, para 80 / 120 / 180 controladores si es posible:

- controladores
- asignaciones
- generados
- prefiltrados
- simulados
- tiempo generacion
- tiempo prefiltrado
- tiempo simulacion
- tiempo total
- clasificacion final:
  - BENEFICIOSO
  - ACEPTABLE
  - RECHAZABLE

Si alguna escala tarda demasiado, permitir modo seguro o corte preventivo, pero no tocar codigo productivo.

---

Validacion final obligatoria

1. correr tests nuevos
2. correr pytest completo
3. correr el benchmark nuevo
4. reportar:
   - archivos creados o modificados
   - funciones agregadas
   - resumen corto del flujo
   - resultado de tests
   - salida del benchmark
   - por que no rompe arquitectura

---

Formato de entrega obligatorio

Quiero que trabajes asi:

1. inspecciona el codigo existente y detecta nombres reales reutilizables
2. implementa solo lo minimo necesario
3. agrega tests nuevos minimos
4. agrega benchmark nuevo
5. corre tests
6. corre benchmark
7. entrega resumen corto y preciso

NO hagas explicaciones largas.
NO propongas rediseños.
NO mejores otras areas.
NO toques mas de lo pedido.

Si dudas entre hacer mas o hacer menos:
hacer menos.

Regla principal:
instalar correctamente la nueva frontera arquitectonica con una v1 minima, segura y conservadora, sin romper nada.

---

## checkpoint-v30-technical-prefilter-v1
Fecha: 2026-04-20

---

### Estado general

Se implementa una primera version minima y conservadora de prevalidacion tecnica ligera entre:

- `candidate_generation`
- `simulator`

El objetivo es reducir candidatos de baja plausibilidad tecnica antes de ejecutar la evaluacion tecnica completa, sin romper contratos ni mover responsabilidades entre capas.

---

### Que quedo implementado

#### 1. Nuevo modulo `technical_prefilter`

- se agrega `src/technical_prefilter.py`
- se implementan:
  - `is_candidate_technically_plausible(...)`
  - `filter_technically_plausible_candidates(...)`

---

#### 2. Prefiltro tecnico ligero

La v1 descarta solo obviedades locales y conservadoras:

- mismo controlador
- misma asignacion exacta
- swap trivial sin cambio real

No clasifica, no puntua, no decide, no persiste, no crea requests y no reemplaza al simulator.

---

#### 3. Nueva variante en `simulator.py`

- se agrega `explorar_y_evaluar_candidatos_con_prefiltro(...)`
- el flujo nuevo es:

`candidate_generation -> technical_prefilter -> simulator`

La funcion nueva evalua tecnicamente solo los candidatos sobrevivientes al prefiltro.

---

#### 4. Testing

Se agregan tests nuevos:

- `tests/test_technical_prefilter.py`
- `tests/test_simulator_prefiltered_bounded_evaluation.py`

Validacion:
- tests nuevos en verde
- suite completa: `130 passed`

---

#### 5. Benchmark por etapas

Se agrega:

- `tools/benchmark_flujo_acotado_prefiltrado.py`

Resultados observados:

- 80 controladores:
  - generados: 158
  - simulados: 79
  - total: ~6375 ms

- 120 controladores:
  - generados: 238
  - simulados: 119
  - total: ~14007 ms

- 180 controladores:
  - generados: 358
  - simulados: 179
  - total: ~35271 ms

---

### Decisiones de diseno reforzadas

- `candidate_generation` sigue siendo estructural
- `technical_prefilter` filtra inviabilidad tecnica obvia y barata
- `simulator` sigue siendo fuente de verdad de evaluacion tecnica completa y clasificacion
- la nueva capa no reemplaza al simulator ni invade scoring

---

### Limitaciones actuales (conscientes)

- la reduccion inicial es significativa pero todavia no deja el flujo completo en tiempo ideal para 180 controladores
- todos los candidatos simulados siguen resultando `RECHAZABLE`
- no se incorporan todavia chequeos tecnicos mas ricos
- no se optimizo internamente `evaluar_swap`
- no se introdujo paralelizacion ni cache

---

### Proximos pasos naturales

- analizar si el benchmark usa una asignacion origen representativa
- medir otros origenes para validar calidad del universo candidato
- evaluar nuevos chequeos conservadores en `technical_prefilter`
- perfilar costo interno de `evaluar_swap`
- decidir si el flujo prefiltrado puede pasar a ser camino preferente tras una iteracion adicional

---

### Notas

Este checkpoint instala correctamente una nueva frontera arquitectonica.

El sistema ya no solo reduce el universo candidato por estructura:
tambien descarta inviabilidades tecnicas obvias antes de pagar el costo de simulacion completa.

---

## checkpoint-v31-prefiltered-origins-benchmark
Fecha: 2026-04-20

---

### Estado general

Se incorpora un benchmark diagnostico para medir el flujo prefiltrado sobre multiples asignaciones origen.

El objetivo es determinar si el patron observado de candidatos `RECHAZABLE` depende de una asignacion origen puntual o si se repite en diferentes puntos del escenario escalado.

---

### Que quedo implementado

#### 1. Nuevo benchmark de multiples origenes

- se agrega `tools/benchmark_origenes_prefiltrados.py`
- el benchmark mide el flujo:

`exploracion acotada -> technical_prefilter -> evaluacion tecnica`

sobre varios origenes representativos de cada escenario.

---

#### 2. Origenes evaluados

Para cada escala se toman origenes distribuidos en el roster escalado:

- primer elemento
- cuarto aproximado
- mitad
- tres cuartos aproximado
- ultimo elemento

Se evitan duplicados si coincidieran.

---

#### 3. Escalas medidas

Se mide el flujo sobre escenarios escalados para:

- 80 controladores
- 120 controladores
- 180 controladores

---

#### 4. Resultados observados

##### 80 controladores

- origenes principales con turno `C`:
  - generados: 158
  - prefiltrados/simulados: 79
  - resultado: 79 `RECHAZABLE`
- ultimo origen con turno `B`:
  - generados: 39
  - prefiltrados/simulados: 0

Resumen:
- promedio tiempo: ~5049 ms
- promedio simulados: ~63
- total `RECHAZABLE`: 316

---

##### 120 controladores

- origenes principales con turno `C`:
  - generados: 238
  - prefiltrados/simulados: 119
  - resultado: 119 `RECHAZABLE`
- ultimo origen con turno `B`:
  - generados: 59
  - prefiltrados/simulados: 0

Resumen:
- promedio tiempo: ~11429 ms
- promedio simulados: ~95
- total `RECHAZABLE`: 476

---

##### 180 controladores

- origenes principales con turno `C`:
  - generados: 358 o 178 segun origen
  - prefiltrados/simulados: 179 o 89
  - resultado: todos `RECHAZABLE`
- ultimo origen con turno `B`:
  - generados: 89
  - prefiltrados/simulados: 0

Resumen:
- promedio tiempo: ~19325 ms
- promedio simulados: ~107
- total `RECHAZABLE`: 536

---

#### 5. Conclusion tecnica del benchmark

El patron de candidatos `RECHAZABLE` no depende solamente de `asignaciones[0]`.

Se repite en multiples origenes representativos, lo que indica que el problema probablemente esta en:

- el escenario escalado artificialmente restrictivo
- candidatos estructuralmente plausibles pero tecnicamente pobres
- falta de un prefiltro tecnico mas especifico
- o una combinacion de los anteriores

---

### Decisiones de diseno reforzadas

- no conviene agregar mas logica al prefiltro sin diagnostico adicional
- la medicion de multiples origenes evita optimizar en base a un solo caso
- el siguiente paso debe identificar causas tecnicas concretas de rechazo
- el flujo prefiltrado permite medir comportamiento por origen sin tocar codigo productivo

---

### Limitaciones actuales (conscientes)

- el benchmark sigue usando escenarios escalados artificiales
- los origenes son representativos por posicion, no necesariamente por valor operativo real
- no identifica todavia que reglas hard dominan los rechazos
- no distingue aun entre problema de escenario y problema de candidato

---

### Proximos pasos naturales

- agregar benchmark diagnostico de motivos de rechazo
- identificar si los rechazos provienen de descanso, secuencia, noches, dotacion u otras reglas
- decidir si una v2 de `technical_prefilter` puede incorporar chequeos locales conservadores
- no modificar prefiltro todavia sin evidencia de reglas dominantes

---

### Notas

Este checkpoint confirma que el problema no es un origen aislado.

La exploracion prefiltrada se comporta consistentemente en varios puntos del escenario, por lo que la proxima decision debe basarse en reglas tecnicas dominantes y no en intuicion.

---

## checkpoint-v32-dominant-hard-rules-diagnostics
Fecha: 2026-04-20

---

### Estado general

Se incorpora un benchmark diagnostico para identificar las reglas hard dominantes responsables de los rechazos en el flujo prefiltrado.

El objetivo es dejar de tratar los resultados `RECHAZABLE` como una caja negra y determinar que invariantes tecnicas invalidan los swaps candidatos.

---

### Que quedo implementado

#### 1. Nuevo benchmark de reglas dominantes

- se agrega `tools/benchmark_reglas_dominantes_prefiltrado.py`
- el benchmark analiza el flujo:

`exploracion acotada -> technical_prefilter -> evaluacion tecnica`

y extrae informacion desde los resultados tecnicos del simulator.

---

#### 2. Analisis de estructuras tecnicas existentes

El benchmark inspecciona campos ya presentes en la salida tecnica:

- `resumen_por_regla_nuevo`
- `resumen_por_regla_original`
- `delta_hard`
- `resultado_swap`
- `valido_nuevo`

No se modifica codigo productivo.

---

#### 3. Escalas medidas

Se miden escenarios escalados para:

- 80 controladores
- 120 controladores
- 180 controladores

usando los mismos criterios de origenes representativos del benchmark anterior.

---

#### 4. Resultados observados

##### 80 controladores

- total simulados: 316
- total rechazables: 316
- reglas dominantes:
  - `Descanso minimo`: 316
  - `Secuencia`: 316

---

##### 120 controladores

- total simulados: 476
- total rechazables: 476
- reglas dominantes:
  - `Descanso minimo`: 476
  - `Secuencia`: 476

---

##### 180 controladores

- total simulados: 536
- total rechazables: 536
- reglas dominantes:
  - `Descanso minimo`: 536
  - `Secuencia`: 536

---

#### 5. Conclusion tecnica del benchmark

Los rechazos del flujo prefiltrado no son aleatorios ni difusos.

El patron dominante es consistente:

- todos los candidatos simulados terminan `RECHAZABLE`
- las reglas hard responsables son principalmente:
  - `Descanso minimo`
  - `Secuencia`

No aparecen como dominantes en esta medicion:

- noches consecutivas
- dotacion
- otros factores

---

### Decisiones de diseno reforzadas

- no corresponde optimizar a ciegas el simulator
- no corresponde agregar filtros al prefiltro sin evidencia
- la siguiente mejora debe estar dirigida especificamente a descanso minimo y secuencia
- el diagnostico confirma que el problema ya no es la combinatoria global sino la plausibilidad tecnica local

---

### Limitaciones actuales (conscientes)

- el benchmark sigue usando escenarios escalados artificiales
- los resultados dependen de la estructura actual de salida del simulator
- no distingue aun si descanso minimo y secuencia fallan por la misma causa local
- no define todavia que parte de esos chequeos puede entrar legalmente en `technical_prefilter`

---

### Proximos pasos naturales

- discutir en arquitectura la frontera permitida de `technical_prefilter` v2
- definir chequeos locales y conservadores para:
  - descanso minimo
  - secuencia inmediata
- decidir si el prefiltro puede leer parametros de configuracion
- evitar duplicar la validacion completa del engine
- medir impacto de una eventual v2 sobre:
  - cantidad de simulados
  - tiempo total
  - preservacion de candidatos tecnicamente validos

---

### Notas

Este checkpoint convierte el problema de performance en un problema semantico preciso.

Ya no se sabe solamente que los candidatos son rechazados:
ahora se sabe que la invalidacion dominante proviene de descanso minimo y secuencia.

---

## checkpoint-v33-technical-prefilter-descanso-local
Fecha: 2026-04-20

---

### Estado general

Se implementa `technical_prefilter v2.1` con un chequeo conservador de descanso minimo local inmediato.

El objetivo es detectar inviabilidad tecnica local evidente antes de enviar candidatos a evaluacion tecnica completa en `simulator`.

---

### Que quedo implementado

#### 1. Chequeo local de descanso minimo

Se agregan funciones auxiliares en `src/technical_prefilter.py` para:

- obtener horas minimas de descanso desde configuracion existente
- agrupar asignaciones por controlador
- ubicar posicion de una asignacion dentro del roster
- calcular descanso entre asignaciones vecinas
- detectar descanso local inmediato insuficiente

---

#### 2. Motivo diagnostico simple

Se agrega exposicion de motivo diagnostico:

- `DESCANSO_LOCAL`

El motivo se usa para benchmark y trazabilidad tecnica ligera.

No representa clasificacion tecnica ni decision operativa.

---

#### 3. Contrato conservador

El prefiltro:

- no demuestra validez
- no clasifica
- no puntua
- no decide
- no persiste
- no crea `SwapRequest`
- no reemplaza al simulator

Ante duda, deja pasar el candidato.

---

#### 4. Testing

Se amplian tests en `tests/test_technical_prefilter.py`.

Validacion:
- tests del prefiltro: `10 passed`
- suite completa: `142 passed`

---

#### 5. Benchmark actualizado

Se actualiza `tools/benchmark_flujo_acotado_prefiltrado.py` para reportar:

- generados
- descartados por `DESCANSO_LOCAL`
- prefiltrados
- simulados
- tiempos por etapa
- clasificacion final

Resultados observados:

- 80 controladores:
  - generados: 158
  - `DESCANSO_LOCAL`: 79
  - simulados: 79
  - total: ~6597 ms

- 120 controladores:
  - generados: 238
  - `DESCANSO_LOCAL`: 119
  - simulados: 119
  - total: ~14372 ms

- 180 controladores:
  - generados: 358
  - `DESCANSO_LOCAL`: 179
  - simulados: 179
  - total: ~32326 ms

---

### Decisiones de diseno reforzadas

- `technical_prefilter` puede descartar inviabilidad tecnica local evidente
- el descanso minimo local inmediato puede analizarse antes del simulator si se mantiene conservador
- la configuracion existente debe usarse para evitar hardcodear parametros
- el simulator sigue siendo la fuente de verdad de evaluacion tecnica completa

---

### Limitaciones actuales (conscientes)

- la v2.1 no redujo mas el universo simulado respecto de la v1 en el escenario medido
- los candidatos que sobreviven siguen terminando `RECHAZABLE`
- el cuello dominante restante probablemente este asociado a secuencia o a descanso no detectable localmente
- no se implemento secuencia local
- no se implemento cache, paralelizacion ni optimizacion de `evaluar_swap`

---

### Proximos pasos naturales

- analizar si conviene discutir `technical_prefilter v2.2` para secuencia local inmediata
- revisar si los candidatos sobrevivientes fallan por secuencia dominante
- evitar agregar mas logica sin evidencia adicional
- mantener la frontera estricta del prefiltro para no crear un mini-simulator

---

### Notas

Este checkpoint instala un chequeo conservador de descanso local y mejora la trazabilidad del prefiltro.

Aunque no reduce mas la cantidad de simulaciones en el escenario actual, permite distinguir descartes por descanso local y delimita mejor el problema restante.

---

## checkpoint-v33-technical-prefilter-descanso-local
Fecha: 2026-04-20

---

### Estado general

Se implementa `technical_prefilter v2.1` con un chequeo conservador de descanso minimo local inmediato.

El objetivo es detectar inviabilidad tecnica local evidente antes de enviar candidatos a evaluacion tecnica completa en `simulator`.

---

### Que quedo implementado

#### 1. Chequeo local de descanso minimo

Se agregan funciones auxiliares en `src/technical_prefilter.py` para:

- obtener horas minimas de descanso desde configuracion existente
- agrupar asignaciones por controlador
- ubicar posicion de una asignacion dentro del roster
- calcular descanso entre asignaciones vecinas
- detectar descanso local inmediato insuficiente

---

#### 2. Motivo diagnostico simple

Se agrega exposicion de motivo diagnostico:

- `DESCANSO_LOCAL`

El motivo se usa para benchmark y trazabilidad tecnica ligera.

No representa clasificacion tecnica ni decision operativa.

---

#### 3. Contrato conservador

El prefiltro:

- no demuestra validez
- no clasifica
- no puntua
- no decide
- no persiste
- no crea `SwapRequest`
- no reemplaza al simulator

Ante duda, deja pasar el candidato.

---

#### 4. Testing

Se amplian tests en `tests/test_technical_prefilter.py`.

Validacion:
- tests del prefiltro: `10 passed`
- suite completa: `142 passed`

---

#### 5. Benchmark actualizado

Se actualiza `tools/benchmark_flujo_acotado_prefiltrado.py` para reportar:

- generados
- descartados por `DESCANSO_LOCAL`
- prefiltrados
- simulados
- tiempos por etapa
- clasificacion final

Resultados observados:

- 80 controladores:
  - generados: 158
  - `DESCANSO_LOCAL`: 79
  - simulados: 79
  - total: ~6597 ms

- 120 controladores:
  - generados: 238
  - `DESCANSO_LOCAL`: 119
  - simulados: 119
  - total: ~14372 ms

- 180 controladores:
  - generados: 358
  - `DESCANSO_LOCAL`: 179
  - simulados: 179
  - total: ~32326 ms

---

### Decisiones de diseno reforzadas

- `technical_prefilter` puede descartar inviabilidad tecnica local evidente
- el descanso minimo local inmediato puede analizarse antes del simulator si se mantiene conservador
- la configuracion existente debe usarse para evitar hardcodear parametros
- el simulator sigue siendo la fuente de verdad de evaluacion tecnica completa

---

### Limitaciones actuales (conscientes)

- la v2.1 no redujo mas el universo simulado respecto de la v1 en el escenario medido
- los candidatos que sobreviven siguen terminando `RECHAZABLE`
- el cuello dominante restante probablemente este asociado a secuencia o a descanso no detectable localmente
- no se implemento secuencia local
- no se implemento cache, paralelizacion ni optimizacion de `evaluar_swap`

---

### Proximos pasos naturales

- analizar si conviene discutir `technical_prefilter v2.2` para secuencia local inmediata
- revisar si los candidatos sobrevivientes fallan por secuencia dominante
- evitar agregar mas logica sin evidencia adicional
- mantener la frontera estricta del prefiltro para no crear un mini-simulator

---

### Notas

Este checkpoint instala un chequeo conservador de descanso local y mejora la trazabilidad del prefiltro.

Aunque no reduce mas la cantidad de simulaciones en el escenario actual, permite distinguir descartes por descanso local y delimita mejor el problema restante.

---

## checkpoint-v34-technical-prefilter-secuencia-local
Fecha: 2026-04-20

---

### Estado general

Se implementa `technical_prefilter v2.2` con chequeo conservador de secuencia local inmediata.

El objetivo es detectar inviabilidad tecnica local evidente por secuencia antes de enviar candidatos a evaluacion tecnica completa en `simulator`.

---

### Que quedo implementado

#### 1. Chequeo local de secuencia inmediata

Se agregan funciones auxiliares en `src/technical_prefilter.py` para:

- obtener regla de configuracion existente
- evaluar secuencia local minima alrededor de asignaciones afectadas
- detectar secuencia local inmediata prohibida

---

#### 2. Motivo diagnostico simple

Se agrega exposicion de motivo diagnostico:

- `SECUENCIA_LOCAL`

El motivo se usa para benchmark y trazabilidad tecnica ligera.

No representa clasificacion tecnica ni decision operativa.

---

#### 3. Contrato conservador

El prefiltro:

- no demuestra validez
- no clasifica
- no puntua
- no decide
- no persiste
- no crea `SwapRequest`
- no reemplaza al simulator

Ante duda, deja pasar el candidato.

---

#### 4. Testing

Se amplian tests en `tests/test_technical_prefilter.py`.

Validacion:

- tests del prefiltro: `13 passed`
- suite completa: `145 passed`

---

#### 5. Benchmark actualizado

Se actualiza `tools/benchmark_flujo_acotado_prefiltrado.py` para reportar:

- generados
- descartados por `DESCANSO_LOCAL`
- descartados por `SECUENCIA_LOCAL`
- prefiltrados
- simulados
- tiempos por etapa
- clasificacion final

Resultados observados:

- 80 controladores:
  - generados: 158
  - `DESCANSO_LOCAL`: 79
  - `SECUENCIA_LOCAL`: 79
  - simulados: 79
  - total: ~6623 ms

- 120 controladores:
  - generados: 238
  - `DESCANSO_LOCAL`: 119
  - `SECUENCIA_LOCAL`: 119
  - simulados: 119
  - total: ~14409 ms

- 180 controladores:
  - generados: 358
  - `DESCANSO_LOCAL`: 179
  - `SECUENCIA_LOCAL`: 179
  - simulados: 179
  - total: ~32257 ms

---

### Decisiones de diseno reforzadas

- `technical_prefilter` puede detectar inviabilidad tecnica local evidente por secuencia inmediata
- la deteccion de secuencia local debe mantenerse conservadora y limitada
- la fuente de verdad de evaluacion completa sigue siendo `simulator`
- el prefiltro puede mejorar trazabilidad aunque no reduzca aun el universo simulado

---

### Limitaciones actuales (conscientes)

- `SECUENCIA_LOCAL` no redujo simulaciones adicionales respecto de `DESCANSO_LOCAL` en el escenario medido
- los motivos `DESCANSO_LOCAL` y `SECUENCIA_LOCAL` parecen solaparse sobre el mismo subconjunto
- los candidatos sobrevivientes siguen terminando `RECHAZABLE`
- no se implementaron reglas de noches, dotacion, score, cache ni paralelizacion
- no se optimizo internamente `evaluar_swap`

---

### Proximos pasos naturales

- diagnosticar por que los candidatos que sobreviven al prefiltro siguen siendo `RECHAZABLE`
- distinguir si el rechazo restante proviene de validacion global del roster base escalado o del swap candidato
- revisar si el benchmark escalado artificial introduce violaciones estructurales de base
- antes de agregar mas logica al prefiltro, comparar `valido_original` vs `valido_nuevo`

---

### Notas

Este checkpoint agrega trazabilidad semantica al prefiltro.

Aunque no mejora la cantidad de simulaciones en el escenario actual, confirma que descanso local y secuencia local detectan el mismo tipo de inviabilidad temprana sobre una parte del universo candidato.

---

## checkpoint-v35-prefiltered-flow-diagnostics
Fecha: 2026-04-20

---

### Estado general

Se incorporan benchmarks diagnosticos para interpretar correctamente el comportamiento del flujo prefiltrado cuando el roster base puede ser tecnicamente invalido.

El objetivo es distinguir si los resultados `RECHAZABLE` provienen de swaps realmente negativos o de escenarios escalados que ya comienzan contaminados.

---

### Problema detectado

Hasta este checkpoint, los benchmarks mostraban:

- 0 `BENEFICIOSO`
- 0 `ACEPTABLE`
- muchos `RECHAZABLE`

Sin embargo, no existia visibilidad sobre:

- si el roster original ya era invalido
- si el swap mejoraba o empeoraba
- si el swap mantenia invalidez previa
- si el escenario escalado estaba contaminado desde origen

---

### Que quedo implementado

#### 1. Benchmark de validez original vs nueva

Se agrega:

- `tools/benchmark_validez_original_vs_nuevo.py`

El benchmark usa el flujo:

`candidate_generation -> technical_prefilter -> simulator`

sin modificar logica de evaluacion.

---

#### 2. Instrumentacion de diagnostico

Se inspeccionan resultados reales devueltos por:

`explorar_y_evaluar_candidatos_con_prefiltro(...)`

Extrayendo:

- `valido_original`
- `valido_nuevo`
- `resumen_original`
- `resumen_nuevo`
- `delta_hard`
- `delta_soft`
- `delta_score`
- `clasificacion`

---

#### 3. Nuevas categorias de interpretacion

Se agregan categorias de diagnostico:

- `VV`
  - original valido -> nuevo valido
- `VI`
  - original valido -> nuevo invalido
- `IV`
  - original invalido -> nuevo valido
- `II`
  - original invalido -> nuevo invalido

Para `II` se agrega subclasificacion:

- `II_mejora`
- `II_igual`
- `II_empeora`

usando:

- mejora si `hard_nuevo < hard_original`
- igual si `hard_nuevo == hard_original`
- empeora si `hard_nuevo > hard_original`

---

### Resultados observados

Escenario medido:
- escala 80 controladores
- origenes representativos

Resultado dominante:

- `II = 79`
- `II_mejora = 79`
- `VV = 0`
- `VI = 0`
- `IV = 0`
- `BENEFICIOSO = 0`
- `ACEPTABLE = 0`
- `RECHAZABLE = 79`

---

### Interpretacion tecnica

El benchmark demuestra que:

- el roster original ya era invalido
- los swaps evaluados mejoran el roster
- pero no alcanzan a volverlo valido
- la clasificacion sigue siendo `RECHAZABLE`

Esto implica que:

- el escenario escalado esta contaminado o parte de una base ya invalida
- el sistema no esta necesariamente generando swaps malos
- la taxonomia actual exige validez final para salir de `RECHAZABLE`

---

### Decisiones de diseno reforzadas

- no corresponde agregar mas prefiltros por ahora
- no corresponde optimizar simulator a ciegas
- los benchmarks deben distinguir invalidez heredada de invalidez causada
- `RECHAZABLE` no siempre significa empeoramiento
- la interpretacion de benchmark debe considerar `valido_original`

---

### Limitaciones actuales (conscientes)

- el benchmark solo se ejecuto inicialmente sobre escala 80
- no se instrumentaron aun escalas 120/180 con diagnostico completo
- no se redefine taxonomia tecnica
- no se modifica clasificacion
- no se separa aun mejora parcial de validez final

---

### Proximos pasos naturales

- discutir en arquitectura como interpretar mejoras parciales sobre rosters invalidos
- decidir si el benchmark debe reportar:
  - mejora tecnica parcial
  - invalidez heredada
  - invalidez introducida
- estudiar si los escenarios escalados deben construirse desde base valida
- evitar seguir optimizando sobre benchmarks contaminados

---

### Notas

Este checkpoint cambia la interpretacion del flujo prefiltrado.

El problema ya no parece ser simplemente que los swaps sean malos.

La evidencia muestra que muchos swaps mejoran tecnicamente el roster, pero parten de escenarios ya invalidos y no logran recuperar validez completa.

---

## checkpoint-v36-diagnostic-transition-benchmark
Fecha: 2026-04-26

---

### Estado general

Se incorpora un benchmark de transiciones diagnosticas separado de la clasificacion tecnica.

El objetivo es interpretar correctamente resultados `RECHAZABLE` cuando el roster original ya es tecnicamente invalido.

---

### Que quedo implementado

#### 1. Nuevo benchmark de transiciones diagnosticas

Se agrega:

- `tools/benchmark_transiciones_diagnosticas.py`

El benchmark usa resultados tecnicos existentes del simulator y deriva una taxonomia diagnostica solo para reporting.

---

#### 2. Taxonomia diagnostica separada

Se reportan transiciones como:

- `VV_MEJORA`
- `VV_IGUAL`
- `VV_EMPEORA`
- `VI_DEGRADA`
- `IV_RECUPERA`
- `II_MEJORA`
- `II_IGUAL`
- `II_EMPEORA`

Esta taxonomia no cambia:

- clasificacion tecnica
- ranking
- decision operativa
- scoring
- contratos

---

#### 3. Resultados observados

##### 80 controladores

- evaluados: 79
- clasificacion tecnica: `RECHAZABLE=79`
- diagnostico: `II_MEJORA=79`

##### 120 controladores

- evaluados: 119
- clasificacion tecnica: `RECHAZABLE=119`
- diagnostico: `II_MEJORA=119`

##### 180 controladores

- evaluados: 179
- clasificacion tecnica: `RECHAZABLE=179`
- diagnostico: `II_MEJORA=179`

---

### Interpretacion tecnica

Los resultados muestran que los swaps evaluados:

- parten de un roster original invalido
- terminan en un roster nuevo que sigue invalido
- reducen violaciones hard
- por lo tanto son mejoras parciales sobre invalidez heredada

La clasificacion tecnica permanece correctamente como `RECHAZABLE`, porque no se recupera validez completa.

---

### Decisiones de diseno reforzadas

- `RECHAZABLE` no debe reinterpretarse como empeoramiento automatico
- la clasificacion tecnica no se modifica
- las transiciones diagnosticas pertenecen al reporting/benchmark
- la mejora parcial sobre roster invalido debe medirse aparte de la clasificacion tecnica

---

### Limitaciones actuales (conscientes)

- el benchmark sigue siendo diagnostico, no productivo
- no se persiste la taxonomia diagnostica
- no se integra aun a reportes operativos
- no corrige la contaminacion del escenario escalado
- no modifica el generador de escenarios

---

### Proximos pasos naturales

- definir si futuros benchmarks deben exigir roster base valido
- crear escenarios escalados tecnicamente validos
- reportar siempre clasificacion tecnica junto con transicion diagnostica
- evitar optimizar sobre escenarios contaminados sin separar invalidez heredada

---

### Notas

Este checkpoint estabiliza la interpretacion de benchmarks.

A partir de ahora, un resultado `RECHAZABLE` puede distinguirse diagnosticamente como degradacion, invalidez heredada o mejora parcial, sin alterar la taxonomia tecnica del sistema.

---

## checkpoint-v37-benchmark-safe-roster-mode
Fecha: 2026-04-26

---

### Estado general

Se incorpora el concepto de modo de benchmark para distinguir escenarios normales, escenarios de recuperacion y escenarios contaminados artificialmente.

El objetivo es evitar interpretar benchmarks sobre rosters base invalidos como si fueran mediciones normales del sistema.

---

### Que quedo implementado

#### 1. Nuevo helper de safety para benchmarks

Se agrega:

- `tools/benchmark_safety.py`

Este modulo permite evaluar el estado base del roster antes de ejecutar benchmarks.

Reporta:

- modo de benchmark
- `valido_original`
- `hard_original`
- `soft_original`
- `score_original`

---

#### 2. Modos de benchmark

Se incorporan modos conceptuales:

- `NORMAL`
  - exige roster base sin violaciones hard
  - si `hard_original > 0`, aborta

- `RECUPERACION`
  - permite roster base invalido
  - etiqueta explicitamente el escenario como recuperacion

- `STRESS_CONTAMINADO`
  - permite escenarios artificiales contaminados
  - debe declararlo explicitamente

---

#### 3. Integracion en benchmark de transiciones diagnosticas

Se actualiza:

- `tools/benchmark_transiciones_diagnosticas.py`

El benchmark ahora corre en modo:

- `RECUPERACION`

y reporta safety por escala antes de interpretar resultados.

---

#### 4. Validacion de escenario contaminado

Resultados observados:

- 80 controladores:
  - `valido_original=False`
  - `hard_original=160`
  - `soft_original=0`
  - `score_original=100`

- 120 controladores:
  - `valido_original=False`
  - `hard_original=240`
  - `soft_original=0`
  - `score_original=100`

- 180 controladores:
  - `valido_original=False`
  - `hard_original=360`
  - `soft_original=0`
  - `score_original=100`

Esto confirma que el escenario escalado actual no es benchmark-safe para modo `NORMAL`.

---

#### 5. Prueba de modo NORMAL

Se valida que el modo `NORMAL` aborta correctamente cuando el roster base es invalido.

Mensaje esperado:

`Benchmark NORMAL abortado: roster base invalido (...)`

---

### Decisiones de diseno reforzadas

- los benchmarks normales deben partir de roster base valido
- los benchmarks sobre rosters invalidos deben declararse como recuperacion o stress contaminado
- la taxonomia tecnica no se modifica
- la taxonomia diagnostica sigue siendo reporting
- la interpretacion del benchmark depende del modo declarado

---

### Limitaciones actuales (conscientes)

- todavia no existe builder escalado que garantice `hard_original=0`
- los benchmarks actuales siguen usando escenarios escalados contaminados
- el modo `RECUPERACION` permite interpretar mejoras parciales, pero no representa operacion normal
- no se corrige aun el generador de escenarios

---

### Proximos pasos naturales

- crear o ajustar builder de escenarios benchmark-safe
- exigir modo `NORMAL` para benchmarks de performance operativa
- mantener modo `RECUPERACION` para pruebas de reparacion sobre rosters invalidos
- comparar resultados entre:
  - benchmark normal
  - benchmark recuperacion
  - benchmark stress contaminado

---

### Notas

Este checkpoint separa definitivamente dos conceptos:

- funcionamiento normal del sistema sobre roster valido
- recuperacion parcial sobre escenarios invalidos

A partir de ahora, ningun benchmark deberia interpretarse sin declarar su modo y estado base del roster.

---

## checkpoint-v38-benchmark-safe-builder-v1
Fecha: 2026-04-26

---

### Estado general

Se incorpora un builder benchmark-safe inicial dentro de `tools/`.

El objetivo es generar escenarios sinteticos tecnicamente validos para benchmarks de modo `NORMAL`, evitando partir de rosters contaminados.

---

### Que quedo implementado

#### 1. Nuevo builder benchmark-safe

Se agrega:

- `tools/benchmark_safe_builder.py`

El builder genera escenarios sinteticos de baja densidad para distintas cantidades de controladores.

---

#### 2. Validacion tecnica del escenario base

El builder valida el roster generado usando la validacion tecnica existente del sistema.

Reporta metadata:

- `modo`
- `valido_original`
- `hard_original`
- `soft_original`
- `score_original`
- `benchmark_safe`

---

#### 3. Modo NORMAL

En modo `NORMAL`, el builder exige:

- `hard_original = 0`

Si el roster base no cumple, debe abortar.

---

#### 4. Escalas verificadas

Se probo el builder para:

- 80 controladores
- 120 controladores
- 180 controladores

Resultados:

- `benchmark_safe=True`
- `valido_original=True`
- `hard_original=0`
- `soft_original=0`
- `score_original=100`

en las tres escalas.

---

### Decisiones de diseno reforzadas

- los benchmarks normales deben partir de escenarios hard-clean
- la certificacion de validez la hace el engine/scoring existente
- el builder vive en `tools/`, no en `src/`
- el escenario generado no pretende ser un roster operativo completo
- la validez del benchmark se separa de la calidad operativa del escenario

---

### Limitaciones actuales (conscientes)

- el builder genera escenarios de baja densidad
- no representa aun una lista operativa real completa
- no garantiza dotaciones operativas por turno
- no modela secuencias reales de trabajo
- sirve como base tecnica limpia para benchmarks, no como generador de rosters reales

---

### Proximos pasos naturales

- usar este builder como fuente para benchmarks `NORMAL`
- comparar resultados entre:
  - escenario contaminado en modo `RECUPERACION`
  - escenario benchmark-safe en modo `NORMAL`
- decidir si se necesita un builder operativo mas denso
- medir candidate_generation y prefilter sobre base no contaminada

---

### Notas

Este checkpoint corrige el problema de interpretacion de benchmarks contaminados.

A partir de ahora, el sistema puede distinguir entre benchmarks de recuperacion sobre rosters invalidos y benchmarks normales sobre rosters hard-clean.

---

## checkpoint-v39-normal-vs-recovery-benchmark
Fecha: 2026-04-28

---

### Estado general

Se incorpora un benchmark comparativo entre escenario `NORMAL` benchmark-safe y escenario `RECUPERACION` contaminado.

El objetivo es validar la diferencia entre medir sobre un roster base tecnicamente limpio y medir sobre un roster base invalido.

---

### Que quedo implementado

#### 1. Nuevo benchmark comparativo

Se agrega:

- `tools/benchmark_normal_vs_recuperacion.py`

El benchmark compara:

- escenario `NORMAL benchmark-safe`
- escenario `RECUPERACION contaminado`

sin modificar logica productiva.

---

#### 2. Escenario NORMAL benchmark-safe

Resultado observado:

- `benchmark_safe=True`
- `valido_original=True`
- `hard_original=0`
- `soft_original=0`
- `score_original=100`
- evaluados: 0

Interpretacion:

- el builder benchmark-safe v1 genera una base tecnicamente limpia
- pero la base es demasiado simple o de baja densidad para producir candidatos evaluables

---

#### 3. Escenario RECUPERACION contaminado

Resultado observado:

- `benchmark_safe=False`
- `valido_original=False`
- `hard_original=160`
- `soft_original=0`
- `score_original=100`
- evaluados: 79
- clasificacion tecnica: `RECHAZABLE=79`
- transicion diagnostica: `II_MEJORA=79`

Interpretacion:

- el escenario contaminado genera actividad
- pero mide recuperacion parcial sobre invalidez heredada
- no representa benchmark normal de operacion

---

### Decisiones de diseno reforzadas

- benchmark `NORMAL` exige roster base hard-clean
- benchmark `RECUPERACION` debe declarar invalidez heredada
- `RECHAZABLE + II_MEJORA` no significa swap negativo
- un escenario benchmark-safe tambien debe tener densidad suficiente para generar intercambios utiles

---

### Limitaciones actuales (conscientes)

- el builder benchmark-safe v1 es tecnicamente valido pero operativamente pobre
- no genera candidatos evaluables en el benchmark comparativo
- el escenario contaminado sigue siendo util para pruebas de recuperacion, no para performance normal
- falta un builder benchmark-safe v2 con mayor densidad operativa

---

### Proximos pasos naturales

- diseñar builder benchmark-safe v2
- generar rosters base validos con mas de una asignacion por controlador
- mantener `hard_original=0`
- asegurar que existan candidatos evaluables
- comparar performance normal sobre escenario valido y suficientemente denso

---

### Notas

Este checkpoint demuestra que no alcanza con que un escenario sea tecnicamente valido.

Para benchmarks operativos, el escenario debe ser tambien suficientemente denso como para producir oportunidades reales de swap.

---

## checkpoint-v40-benchmark-safe-builder-v2
Fecha: 2026-04-28

---

### Estado general

Se incorpora `benchmark_safe_builder v2` en `tools/` para generar escenarios `NORMAL_DENSO`.

El objetivo es disponer de escenarios tecnicamente validos y suficientemente densos para benchmarks de performance operativa, evitando medir sobre rosters contaminados o demasiado pobres.

---

### Que quedo implementado

#### 1. Nuevo builder denso benchmark-safe

Se agrega:

- `tools/benchmark_safe_builder_v2.py`

El builder genera escenarios sinteticos en modo:

- `NORMAL_DENSO`

---

#### 2. Escenarios tecnicamente validos

El builder valida los escenarios usando la logica existente del sistema.

Resultados obtenidos:

- `benchmark_safe=True`
- `valido_original=True`
- `hard_original=0`
- `soft_original=0`
- `score_original=100`

para las escalas medidas.

---

#### 3. Escenarios utiles para benchmark

A diferencia del builder v1, el builder v2 genera escenarios con densidad suficiente para producir candidatos.

Metadata reportada:

- `modo`
- `benchmark_safe`
- `benchmark_useful`
- `controladores`
- `asignaciones`
- `hard_original`
- `soft_original`
- `score_original`
- `valido_original`
- `candidate_count`
- `simulable_count`
- `origenes_con_candidatos`
- `densidad_promedio`

---

#### 4. Escalas verificadas

Resultados observados:

- 80 controladores:
  - asignaciones: 240
  - hard: 0
  - soft: 0
  - score: 100
  - candidates: 6910
  - simulables: 2370
  - origenes con candidatos: 30
  - densidad: 3.0

- 120 controladores:
  - asignaciones: 360
  - hard: 0
  - soft: 0
  - score: 100
  - candidates: 10710
  - simulables: 3570
  - origenes con candidatos: 30
  - densidad: 3.0

- 180 controladores:
  - asignaciones: 540
  - hard: 0
  - soft: 0
  - score: 100
  - candidates: 16110
  - simulables: 5370
  - origenes con candidatos: 30
  - densidad: 3.0

---

### Decisiones de diseno reforzadas

- los benchmarks `NORMAL` deben partir de rosters hard-clean
- los escenarios benchmark-safe tambien deben ser utiles, no solo validos
- el builder sigue viviendo en `tools/`, no en `src/`
- el engine/scoring existente certifica validez
- el builder no reemplaza un generador real de roster operativo

---

### Limitaciones actuales (conscientes)

- el builder sigue siendo sintetico
- no representa aun un roster operativo real completo
- no modela dotaciones reales por sector
- no modela reglas humanas de armado de lista
- no se integro aun a benchmarks de performance completos

---

### Proximos pasos naturales

- usar `NORMAL_DENSO` en benchmarks comparativos
- medir flujo acotado + prefiltro + simulator sobre base valida
- comparar resultados contra modo `RECUPERACION`
- evaluar si aparecen transiciones `VV_*` en lugar de `II_*`
- despues, recien despues, analizar performance real

---

### Notas

Este checkpoint corrige la limitacion principal del builder v1.

El sistema ya puede generar escenarios de benchmark que son al mismo tiempo validos y con actividad suficiente para medir swaps.

---

## checkpoint-v41-tools-bootstrap-path
Fecha: 2026-04-28

---

### Estado general

Se normaliza el manejo de path en los scripts dentro de `tools/`.

El objetivo es permitir que los benchmarks y utilidades puedan ejecutarse tanto como modulo como script directo desde la raiz del proyecto.

---

### Problema detectado

Algunos scripts fallaban al ejecutarse con:

`python tools/nombre_script.py`

porque Python tomaba `tools/` como raiz de importacion y no encontraba el paquete `src`.

En cambio, funcionaban usando:

`python -m tools.nombre_script`

---

### Que quedo implementado

#### 1. Nuevo helper de bootstrap

Se agrega:

- `tools/bootstrap_path.py`

con funcion:

- `ensure_project_root_on_path()`

La funcion agrega la raiz del proyecto a `sys.path` si no esta presente.

---

#### 2. Normalizacion de imports en tools

Se actualizan scripts de `tools/` que importan `src.*` para ejecutar el bootstrap antes de esos imports.

Patron utilizado:

()```python
(try:
    from tools.bootstrap_path import ensure_project_root_on_path
except ModuleNotFoundError:
    from bootstrap_path import ensure_project_root_on_path

ensure_project_root_on_path() )

---

## checkpoint-v43-candidate-selection-v1
Fecha: 2026-04-28

---

### Estado general

Se implementa `candidate_selection v1` como nueva capa entre:

- `technical_prefilter`
- `simulator`

El objetivo es reducir la cantidad de candidatos enviados a evaluacion tecnica completa, sin tocar el simulator ni modificar la semantica tecnica del sistema.

---

### Que quedo implementado

#### 1. Nuevo modulo `candidate_selection`

Se agrega:

- `src/candidate_selection.py`

con funcion principal:

`seleccionar_candidatos(asignacion_origen, candidatos, asignaciones, top_n=50)`

---

#### 2. Responsabilidad de la nueva capa

`candidate_selection` toma candidatos ya generados y prefiltrados, los ordena con criterios estructurales baratos y devuelve un subconjunto acotado.

No:

- llama a `engine`
- llama a `scoring`
- llama a `simulator`
- clasifica
- decide
- persiste
- crea `SwapRequest`
- modifica candidatos

---

#### 3. Criterios de ordenamiento v1

La seleccion es deterministica y usa criterios baratos:

1. misma fecha que la asignacion origen primero
2. menor distancia en dias
3. turno distinto antes que mismo turno
4. nombre de controlador como desempate
5. fecha y codigo de turno como desempate final

---

#### 4. Testing

Se agrega:

- `tests/test_candidate_selection.py`

Casos cubiertos:

- devuelve lista
- si candidatos <= `top_n`, devuelve todos
- si candidatos > `top_n`, recorta
- prioriza mismo dia
- prioriza menor distancia temporal
- resultado deterministico
- no devuelve `SwapRequest`
- no clasifica
- no decide
- no modifica candidatos

Validacion:

- tests nuevos: `10 passed`
- suite completa: `155 passed`

---

#### 5. Benchmark NORMAL_DENSO con seleccion

Se agrega:

- `tools/benchmark_normal_denso_selection.py`

El benchmark mide:

`candidate_generation -> technical_prefilter -> candidate_selection -> simulator`

sobre escenarios `NORMAL_DENSO`.

---

### Resultados observados

Con `top_n=50` y 3 origenes por escala:

#### 80 controladores

- generados: 711
- prefiltrados: 237
- seleccionados: 150
- simulados: 150
- clasificacion final: `ACEPTABLE=150`
- transicion diagnostica: `VV_IGUAL=150`

#### 120 controladores

- generados: 1071
- prefiltrados: 357
- seleccionados: 150
- simulados: 150
- clasificacion final: `ACEPTABLE=150`
- transicion diagnostica: `VV_IGUAL=150`

#### 180 controladores

- generados: 1611
- prefiltrados: 537
- seleccionados: 150
- simulados: 150
- clasificacion final: `ACEPTABLE=150`
- transicion diagnostica: `VV_IGUAL=150`

---

### Comparacion contra baseline

Cantidad de simulados por origen:

- 80 controladores:
  - antes: 79
  - ahora: 50

- 120 controladores:
  - antes: 119
  - ahora: 50

- 180 controladores:
  - antes: 179
  - ahora: 50

---

### Decisiones de diseno reforzadas

- no es necesario simular todos los candidatos prefiltrados para una primera oferta
- la reduccion de volumen puede hacerse antes del simulator
- `candidate_selection` no reemplaza scoring tecnico ni clasificacion
- el simulator sigue siendo la fuente de verdad tecnica
- la seleccion es estructural y barata, no tecnica

---

### Limitaciones actuales (conscientes)

- `top_n=50` es una decision inicial y configurable
- los criterios son simples y no incorporan preferencias reales del usuario
- no hay aun diversidad avanzada por controlador
- no se mide todavia calidad de candidatos descartados
- no se optimizo internamente `evaluar_swap`

---

### Proximos pasos naturales

- medir tiempos comparativos antes/despues con `candidate_selection`
- evaluar valores alternativos de `top_n`
- estudiar diversidad por controlador o turno
- integrar esta capa como camino preferente solo cuando el contrato operativo lo apruebe
- mantener disponible el flujo sin seleccion para diagnostico completo

---

### Notas

Este checkpoint introduce una palanca estructural importante de performance.

El sistema reduce la carga sobre `simulator` sin alterar la evaluacion tecnica ni la taxonomia del dominio.

---

## checkpoint-v44-candidate-selection-comparative-benchmark
Fecha: 2026-04-28

---

### Estado general

Se incorpora un benchmark comparativo para medir el impacto de `candidate_selection` sobre el flujo `NORMAL_DENSO`.

El objetivo es comparar el costo de evaluar todos los candidatos prefiltrados contra evaluar solo un subconjunto `top_n`.

---

### Que quedo implementado

#### 1. Nuevo benchmark comparativo

Se agrega:

- `tools/benchmark_selection_comparativo.py`

El benchmark compara:

- flujo sin seleccion
- flujo con `candidate_selection`

sobre escenario `NORMAL_DENSO`.

---

#### 2. Flujo medido

Sin seleccion:

`candidate_generation -> technical_prefilter -> simulator`

Con seleccion:

`candidate_generation -> technical_prefilter -> candidate_selection -> simulator`

---

#### 3. Configuracion del benchmark

- `top_n = 50`
- `origenes_por_escala = 3`
- escalas:
  - 80 controladores
  - 120 controladores
  - 180 controladores

---

### Resultados observados

#### 80 controladores

- sin seleccion:
  - evaluados: 237
  - tiempo: ~16766 ms

- con seleccion:
  - evaluados: 150
  - tiempo: ~10607 ms

- ahorro:
  - ~6159 ms
  - ~36.7%

---

#### 120 controladores

- sin seleccion:
  - evaluados: 357
  - tiempo: ~36220 ms

- con seleccion:
  - evaluados: 150
  - tiempo: ~15236 ms

- ahorro:
  - ~20984 ms
  - ~57.9%

---

#### 180 controladores

- sin seleccion:
  - evaluados: 537
  - tiempo: ~81631 ms

- con seleccion:
  - evaluados: 150
  - tiempo: ~22774 ms

- ahorro:
  - ~58857 ms
  - ~72.1%

---

### Resultado funcional

Con seleccion, el resultado tecnico se mantiene coherente:

- clasificacion tecnica:
  - `ACEPTABLE=150` en cada escala

- transicion diagnostica:
  - `VV_IGUAL=150` en cada escala

Esto confirma que `candidate_selection` reduce carga sin alterar la semantica tecnica.

---

### Decisiones de diseno reforzadas

- no es necesario enviar todos los candidatos prefiltrados al simulator en la primera pasada
- la seleccion estructural top-N es una palanca efectiva de performance
- `candidate_selection` puede reducir costo sin tocar engine, scoring ni simulator
- el simulator sigue siendo fuente de verdad tecnica
- la seleccion no clasifica, no decide y no puntua tecnicamente

---

### Limitaciones actuales (conscientes)

- `top_n=50` es un valor inicial
- no se mide aun calidad relativa de candidatos descartados
- no hay diversidad avanzada por controlador
- no se incorporan preferencias explicitas del usuario
- todos los resultados observados son `ACEPTABLE + VV_IGUAL`, por lo que falta generar escenarios con mayor variedad tecnica

---

### Proximos pasos naturales

- evaluar distintos valores de `top_n`
- medir trade-off entre costo y cobertura
- agregar diversidad simple por controlador si se justifica
- decidir si `candidate_selection` pasa a ser camino preferente
- mantener flujo sin seleccion para diagnostico completo

---

### Notas

Este checkpoint confirma que la estrategia de seleccion previa a simulacion reduce sustancialmente el costo del flujo `NORMAL_DENSO`, especialmente a mayor escala.

---

## checkpoint-v45-exploration-modes-metadata
Fecha: 2026-05-06

---

### Estado general

Se formalizaron los modos oficiales de exploracion y el contrato minimo de metadata para integrar `candidate_selection` como camino preferente de oferta rapida sin alterar los contratos tecnicos existentes.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Modos oficiales de exploracion

Se agrego el archivo:

 `src/exploration_modes.py`

Con los modos oficiales:

 `OFERTA_RAPIDA`
 `DIAGNOSTICO_COMPLETO`
 `EXHAUSTIVO`

#### 2. Metadata obligatoria por ejecucion

Se agrego la dataclass:

 `ExplorationMetadata`

Campos incluidos:

 `modo_exploracion`
 `candidatos_generados`
 `candidatos_prefiltrados`
 `candidatos_seleccionados`
 `candidatos_evaluados`
 `top_n`
 `criterio_seleccion`
 `tiempos_por_etapa`

#### 3. Builders de metadata

Se agregaron funciones para construir metadata segun modo:

 `construir_metadata_oferta_rapida`
 `construir_metadata_diagnostico_completo`
 `construir_metadata_exhaustivo`

#### 4. Criterio de seleccion documentado en codigo

Se agrego la constante:

 `CRITERIO_SELECCION_CANDIDATE_SELECTION_V1`

El criterio queda explicitado como estructural y barato, sin evaluacion tecnica.

#### 5. Mensaje seguro para UI/reporting

Se agrego la constante:

 `MENSAJE_REPORTING_OFERTA_RAPIDA`

Texto:

```text
Mostrando mejores candidatos evaluados segun filtros actuales.

```

---


## checkpoint-v46-oferta-rapida-topn-benchmark
Fecha: 2026-05-06

---

### Estado general

Se agrego un benchmark comparativo para medir `OFERTA_RAPIDA` contra `DIAGNOSTICO_COMPLETO` usando una matriz de valores `top_n`.

El bloque no modifica el comportamiento tecnico del sistema. Solo agrega una herramienta de medicion en `tools/`.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Benchmark top-N de oferta rapida

Se agrego el archivo:

- `tools/benchmark_oferta_rapida_topn.py`

El benchmark compara dos modos oficiales:

- `DIAGNOSTICO_COMPLETO`
- `OFERTA_RAPIDA`

---

#### 2. Matriz de top_n

Se mide `OFERTA_RAPIDA` con los siguientes valores:

- `top_n=20`
- `top_n=40`
- `top_n=50`
- `top_n=80`
- `top_n=100`

---

#### 3. Flujo medido

`DIAGNOSTICO_COMPLETO` mide el flujo:

    candidate_generation -> technical_prefilter -> simulator

`OFERTA_RAPIDA` mide el flujo:

    candidate_generation -> technical_prefilter -> candidate_selection -> simulator

---

#### 4. Metadata por ejecucion

El benchmark reporta metadata compatible con `ExplorationMetadata`.

Campos reportados:

- `modo_exploracion`
- `candidatos_generados`
- `candidatos_prefiltrados`
- `candidatos_seleccionados`
- `candidatos_evaluados`
- `top_n`
- `criterio_seleccion`
- `tiempos_por_etapa`

---

#### 5. Comparacion contra diagnostico completo

Para cada escala se calcula:

- tiempo total
- candidatos evaluados
- candidatos seleccionados
- ahorro en milisegundos
- ahorro porcentual
- clasificacion tecnica
- transicion diagnostica
- diversidad de controladores

---

#### 6. Compatibilidad con contratos reales existentes

El benchmark se adapto a los contratos reales del codigo actual:

- `generate_candidates(asignacion_origen, roster_index, mode)`
- `filter_technically_plausible_candidates(..., config_file)`
- `evaluar_swap(asignaciones, idx_a, idx_b, config_file)`

Esto mantiene el benchmark alineado con los modulos existentes sin modificar `src/`.

---

### Resultados observados

Suite completa:

    162 passed

Resultados principales del benchmark:

- `DIAGNOSTICO_COMPLETO` evalua todos los candidatos prefiltrados.
- `OFERTA_RAPIDA` evalua solo los candidatos seleccionados por `candidate_selection`.
- `top_n=50` mantiene el patron esperado del checkpoint anterior.
- La clasificacion tecnica observada se mantiene como `ACEPTABLE`.
- La transicion diagnostica observada se mantiene como `VV_IGUAL`.

Lectura operativa:

- `top_n=20` ofrece el mayor ahorro, pero puede ser demasiado restrictivo para oferta real.
- `top_n=40` aparece como opcion razonable para una oferta mas liviana.
- `top_n=50` queda sostenido como default inicial operativo.
- `top_n=80` y `top_n=100` se acercan mas al diagnostico completo y pierden parte de la ventaja de costo.

---

### Decisiones de diseno reforzadas

- `candidate_selection` reduce universo antes de simular.
- `candidate_selection` no clasifica.
- `candidate_selection` no puntua tecnicamente.
- `candidate_selection` no decide.
- `candidate_selection` no persiste.
- `candidate_selection` no llama `engine`, `scoring` ni `simulator`.
- `simulator` sigue siendo la fuente de verdad tecnica.
- El ranking tecnico debe ocurrir despues de la simulacion.
- `DIAGNOSTICO_COMPLETO` se conserva como camino de auditoria, diagnostico y benchmark.
- `OFERTA_RAPIDA` queda validado como camino operativo preferente medible.

---

### Limitaciones actuales (conscientes)

- El benchmark todavia es una herramienta en `tools/`, no un flujo operativo integrado.
- No se integro `OFERTA_RAPIDA` en `swap_service`.
- No se agrego cache.
- No se agrego paralelizacion.
- No se optimizo internamente `simulator`.
- No se implemento seleccion basada en score tecnico.
- No se implemento candidate_selection inteligente avanzada.
- No se elimino el modo completo.

---

### Proximos pasos naturales

- Crear un flujo de exploracion/oferta que use explicitamente `ModoExploracion`.
- Mantener `DIAGNOSTICO_COMPLETO` disponible para auditoria.
- Integrar metadata de exploracion en una salida estructurada.
- Preparar una funcion operativa de oferta rapida sin tocar aun `swap_service`.
- Definir luego si esa funcion sera consumida por reporting, UI o servicio operativo.
- Mantener `top_n=50` como default inicial operativo, salvo nueva evidencia.

---

### Notas

Este checkpoint aporta evidencia empirica para sostener `OFERTA_RAPIDA` como camino preferente.

No modifica contratos tecnicos ni cambia decisiones operativas.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `technical_prefilter` ni `candidate_selection`.

---

## checkpoint-v47-exploration-flow-oferta-rapida
Fecha: 2026-05-06

---

### Estado general

Se agrego un flujo estructurado de exploracion para soportar `OFERTA_RAPIDA` como camino operativo preferente y `DIAGNOSTICO_COMPLETO` como camino alternativo de auditoria, diagnostico y benchmark.

El bloque no integra todavia `swap_service` ni modifica decisiones operativas. Solo crea una capa de flujo tecnico-operativo para explorar candidatos, evaluar swaps y devolver resultados con metadata.

La suite de tests quedo en verde.

---

### Que quedo implementado

#### 1. Nuevo modulo de flujo de exploracion

Se agrego el archivo:

- `src/exploration_flow.py`

Este modulo concentra el flujo:

    candidate_generation -> technical_prefilter -> candidate_selection -> simulator -> ranking tecnico

para el modo `OFERTA_RAPIDA`.

Tambien concentra el flujo:

    candidate_generation -> technical_prefilter -> simulator -> ranking tecnico

para el modo `DIAGNOSTICO_COMPLETO`.

---

#### 2. Resultado estructurado del flujo

Se agrego la dataclass:

- `ExplorationFlowResult`

Campos principales:

- `modo_exploracion`
- `evaluaciones`
- `metadata`

Tambien se agrego la propiedad:

- `cantidad_evaluaciones`

---

#### 3. Default operativo de oferta rapida

Se agrego la constante:

- `DEFAULT_TOP_N_OFERTA_RAPIDA = 50`

Esto deja `top_n=50` como default inicial operativo, sin convertirlo en una constante rigida interna del algoritmo.

---

#### 4. Flujo OFERTA_RAPIDA

Se agrego la funcion:

- `explorar_oferta_rapida`

Responsabilidades:

- construir `roster_index`
- generar candidatos con `candidate_generation`
- aplicar `technical_prefilter`
- aplicar `candidate_selection`
- evaluar candidatos seleccionados con `simulator`
- ordenar resultados por ranking tecnico
- devolver evaluaciones y metadata

Este flujo usa `candidate_selection` antes de simular.

---

#### 5. Flujo DIAGNOSTICO_COMPLETO

Se agrego la funcion:

- `explorar_diagnostico_completo`

Responsabilidades:

- construir `roster_index`
- generar candidatos con `candidate_generation`
- aplicar `technical_prefilter`
- evaluar todos los candidatos prefiltrados con `simulator`
- ordenar resultados por ranking tecnico
- devolver evaluaciones y metadata

Este flujo no usa `candidate_selection`.

---

#### 6. Funcion publica de seleccion de modo

Se agrego la funcion:

- `explorar_candidatos_para_oferta`

Modos soportados:

- `OFERTA_RAPIDA`
- `DIAGNOSTICO_COMPLETO`

El modo default es:

- `OFERTA_RAPIDA`

El modo `EXHAUSTIVO` no se integra todavia al flujo operativo.

---

#### 7. Ranking tecnico posterior a simulator

Se agrego ordenamiento tecnico interno posterior a la simulacion.

Criterio aplicado:

- `BENEFICIOSO`
- `ACEPTABLE`
- `RECHAZABLE`
- mejor `delta_score`
- menor `delta_hard`
- menor `delta_soft`

Este ranking ocurre despues de `simulator`, por lo que no cambia el contrato de `candidate_selection`.

---

#### 8. Metadata por ejecucion

El flujo devuelve metadata compatible con `ExplorationMetadata`.

Campos incluidos:

- `modo_exploracion`
- `candidatos_generados`
- `candidatos_prefiltrados`
- `candidatos_seleccionados`
- `candidatos_evaluados`
- `top_n`
- `criterio_seleccion`
- `tiempos_por_etapa`

Tiempos registrados:

- `roster_index_ms`
- `candidate_generation_ms`
- `technical_prefilter_ms`
- `candidate_selection_ms` en `OFERTA_RAPIDA`
- `simulator_ms`
- `technical_ranking_ms`
- `total_ms`

---

#### 9. Tests especificos

Se agrego el archivo:

- `tests/test_exploration_flow.py`

Cobertura agregada:

- `OFERTA_RAPIDA` usa `candidate_selection` antes de simular.
- `OFERTA_RAPIDA` respeta `top_n`.
- `OFERTA_RAPIDA` usa `top_n=50` como default.
- `DIAGNOSTICO_COMPLETO` no usa `candidate_selection`.
- El flujo operativo default es `OFERTA_RAPIDA`.
- El flujo permite `DIAGNOSTICO_COMPLETO`.
- El flujo rechaza modos no soportados.
- `OFERTA_RAPIDA` rechaza `top_n` invalido.
- El ranking tecnico ocurre despues de `simulator`.

---

### Resultados observados

Tests especificos:

    tests/test_exploration_flow.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- `candidate_selection` queda integrado solo como reduccion de universo previa a simulacion.
- `candidate_selection` no clasifica.
- `candidate_selection` no puntua tecnicamente.
- `candidate_selection` no decide.
- `candidate_selection` no persiste.
- `candidate_selection` no llama `engine`, `scoring` ni `simulator`.
- `simulator` sigue siendo la fuente de verdad tecnica.
- El ranking tecnico ocurre despues de `simulator`.
- `OFERTA_RAPIDA` queda como camino default del flujo de oferta.
- `DIAGNOSTICO_COMPLETO` se mantiene como camino alternativo para auditoria, diagnostico y benchmark.
- `EXHAUSTIVO` queda fuera del flujo operativo por ahora.
- `swap_service` no se modifica en este checkpoint.

---

### Limitaciones actuales (conscientes)

- El flujo todavia no esta integrado a `swap_service`.
- El flujo todavia no persiste resultados.
- El flujo todavia no aplica priorizacion historica.
- El flujo todavia no genera reporte final para UI.
- No se agrego cache.
- No se agrego paralelizacion.
- No se optimizo internamente `simulator`.
- No se agrego seleccion inteligente avanzada.
- No se elimino `DIAGNOSTICO_COMPLETO`.

---

### Proximos pasos naturales

- Integrar priorizacion historica despues del ranking tecnico.
- Mantener separada la clasificacion tecnica de la priorizacion historica.
- Agregar tests para verificar que la priorizacion historica no cambia clasificacion, validez ni impacto tecnico.
- Preparar salida de oferta con texto seguro para UI/reporting.
- Evaluar luego si el flujo debe ser consumido por `swap_service` o por una capa intermedia de reporting/oferta.

---

### Notas

Este checkpoint crea la primera capa operativa concreta para `OFERTA_RAPIDA`, sin romper los contratos tecnicos existentes.

No modifica `engine`, `scoring`, `simulator`, `swap_service`, `technical_prefilter`, `candidate_generation` ni `candidate_selection`.

---

## checkpoint-v48-historical-prioritization-flow
Fecha: 2026-05-06

---

### Estado general

Se integro la priorizacion historica dentro del flujo de exploracion de `OFERTA_RAPIDA`.

La priorizacion historica se aplica despues del ranking tecnico y solo si el flujo recibe historial de controladores.

El bloque no modifica `swap_service`, no persiste resultados y no cambia decisiones operativas.

La suite de tests quedo en verde.

---

### Que quedo implementado

#### 1. Priorizacion historica en exploration_flow

Se modifico el archivo:

- `src/exploration_flow.py`

Se agrego integracion con:

- `priorizar_por_equidad_historica`

La priorizacion se aplica dentro de `OFERTA_RAPIDA`, despues de:

    candidate_generation -> technical_prefilter -> candidate_selection -> simulator -> ranking tecnico

---

#### 2. Helper interno de priorizacion

Se agrego el helper interno:

- `_aplicar_priorizacion_historica`

Comportamiento:

- si `historial_controladores` es `None`, no prioriza
- si recibe historial, llama a `priorizar_por_equidad_historica`
- devuelve las evaluaciones finales
- devuelve un flag booleano indicando si se aplico priorizacion historica

---

#### 3. Parametro historial_controladores

Se agrego el parametro opcional:

- `historial_controladores`

En las funciones:

- `explorar_oferta_rapida`
- `explorar_candidatos_para_oferta`

El parametro permite aplicar priorizacion historica sin acoplar el flujo a persistencia ni a stores.

---

#### 4. Metadata extendida

Se agrego en la metadata el campo:

- `priorizacion_historica_aplicada`

Valores esperados:

- `True` cuando `OFERTA_RAPIDA` recibe historial y aplica priorizacion
- `False` cuando no recibe historial
- `False` en `DIAGNOSTICO_COMPLETO`

Tambien se agrega el tiempo de etapa:

- `historical_prioritization_ms`

---

#### 5. DIAGNOSTICO_COMPLETO sin priorizacion historica

Se dejo explicito que `DIAGNOSTICO_COMPLETO` no aplica priorizacion historica.

Esto mantiene al modo completo como herramienta de auditoria, diagnostico y benchmark tecnico.

---

#### 6. Tests especificos agregados

Se modifico el archivo:

- `tests/test_exploration_flow.py`

Cobertura agregada:

- `OFERTA_RAPIDA` aplica priorizacion historica despues del ranking tecnico.
- `OFERTA_RAPIDA` sin historial no aplica priorizacion historica.
- `DIAGNOSTICO_COMPLETO` no aplica priorizacion historica.
- `explorar_candidatos_para_oferta` pasa el historial a `OFERTA_RAPIDA`.
- La priorizacion historica puede reordenar evaluaciones.
- La priorizacion historica no modifica campos tecnicos de las evaluaciones.

---

### Resultados observados

Tests especificos:

    tests/test_exploration_flow.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- La priorizacion historica ocurre despues del ranking tecnico.
- La priorizacion historica no modifica clasificacion tecnica.
- La priorizacion historica no modifica validez tecnica.
- La priorizacion historica no modifica impacto tecnico.
- La priorizacion historica no modifica deltas tecnicos.
- `candidate_selection` sigue reduciendo universo antes de simular.
- `candidate_selection` no clasifica.
- `candidate_selection` no puntua tecnicamente.
- `candidate_selection` no decide.
- `simulator` sigue siendo la fuente de verdad tecnica.
- `DIAGNOSTICO_COMPLETO` se mantiene sin priorizacion historica.
- `swap_service` no se modifica en este checkpoint.

---

### Limitaciones actuales (conscientes)

- El flujo todavia no esta integrado a `swap_service`.
- El flujo no persiste resultados.
- El flujo no actualiza historial.
- El flujo no decide aprobacion ni rechazo.
- El flujo no genera todavia una salida final de UI/reporting.
- No se agrego cache.
- No se agrego paralelizacion.
- No se optimizo internamente `simulator`.
- No se agrego seleccion inteligente avanzada.
- No se elimino `DIAGNOSTICO_COMPLETO`.

---

### Proximos pasos naturales

- Crear una salida de oferta para UI/reporting.
- Incluir mensaje seguro: "Mostrando mejores candidatos evaluados segun filtros actuales."
- Separar claramente evaluacion tecnica, ranking tecnico y priorizacion historica.
- Agregar metadata visible para cantidad de candidatos generados, prefiltrados, seleccionados y evaluados.
- Evaluar luego si el flujo debe ser consumido por una capa intermedia de oferta o por `swap_service`.

---

### Notas

Este checkpoint integra equidad historica como priorizacion posterior a la evaluacion tecnica.

No cambia la clasificacion tecnica, no cambia el scoring base, no cambia la decision operativa y no modifica la aplicacion de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `technical_prefilter`, `candidate_generation` ni `candidate_selection`.

---

## checkpoint-v49-offer-reporting-output
Fecha: 2026-05-06

---

### Estado general

Se agrego una salida estructurada de oferta orientada a UI/reporting.

El bloque toma el resultado de `exploration_flow` y lo transforma en una estructura presentable, con mensaje seguro, ofertas enumeradas y metadata visible.

No modifica el flujo tecnico, no cambia clasificacion, no decide aprobacion/rechazo y no persiste resultados.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Nuevo modulo de reporting de oferta

Se agrego el archivo:

- `src/offer_reporting.py`

Este modulo convierte un `ExplorationFlowResult` en una salida orientada a presentacion.

---

#### 2. Estructura OfertaEvaluada

Se agrego la dataclass:

- `OfertaEvaluada`

Campos principales:

- `posicion`
- `clasificacion`
- `delta_score`
- `delta_hard`
- `delta_soft`
- `idx_a`
- `idx_b`
- `evaluacion`

La estructura conserva la evaluacion tecnica original sin modificarla.

---

#### 3. Estructura OfferReport

Se agrego la dataclass:

- `OfferReport`

Campos principales:

- `mensaje`
- `modo_exploracion`
- `ofertas`
- `metadata`

Tambien se agrego:

- propiedad `cantidad_ofertas`
- metodo `to_dict()`

---

#### 4. Funcion publica de reporte

Se agrego la funcion:

- `generar_reporte_oferta`

Responsabilidades:

- recibir un `ExplorationFlowResult`
- aplicar un limite opcional de resultados
- enumerar ofertas desde posicion `1`
- preservar el orden recibido desde `exploration_flow`
- generar metadata visible para UI/reporting
- devolver un `OfferReport`

---

#### 5. Mensaje seguro para UI/reporting

El reporte usa el mensaje seguro definido previamente:

    Mostrando mejores candidatos evaluados segun filtros actuales.

Este mensaje evita afirmar que se muestran todos los swaps posibles.

---

#### 6. Metadata visible

El reporte expone solo metadata prevista para presentacion:

- `modo_exploracion`
- `candidatos_generados`
- `candidatos_prefiltrados`
- `candidatos_seleccionados`
- `candidatos_evaluados`
- `top_n`
- `criterio_seleccion`
- `priorizacion_historica_aplicada`
- `tiempos_por_etapa`

No expone campos internos no previstos.

---

#### 7. Tests especificos

Se agrego el archivo:

- `tests/test_offer_reporting.py`

Cobertura agregada:

- el reporte incluye mensaje seguro
- el reporte no dice "todos los swaps posibles"
- el reporte conserva modo y cantidad
- el reporte enumera posiciones
- el reporte preserva el orden recibido desde el flujo
- el reporte no modifica evaluacion tecnica
- el reporte incluye metadata visible
- el reporte no expone metadata interna no visible
- el reporte respeta limite
- el reporte rechaza limite invalido
- `to_dict()` devuelve estructura serializable
- el reporte tolera evaluaciones incompletas

---

### Resultados observados

Suite completa:

    186 passed

---

### Decisiones de diseno reforzadas

- La salida de oferta queda separada del flujo tecnico.
- `offer_reporting` no decide aprobacion ni rechazo.
- `offer_reporting` no persiste resultados.
- `offer_reporting` no modifica clasificacion tecnica.
- `offer_reporting` no modifica ranking tecnico.
- `offer_reporting` no modifica priorizacion historica.
- `offer_reporting` preserva el orden recibido desde `exploration_flow`.
- El mensaje visible no promete mostrar todos los swaps posibles.
- La metadata visible queda controlada y explicita.
- `swap_service` no se modifica en este checkpoint.

---

### Limitaciones actuales (conscientes)

- Todavia no hay UI real.
- Todavia no hay API.
- Todavia no se integra `offer_reporting` con `swap_service`.
- Todavia no se persisten reportes.
- Todavia no se actualiza historial.
- Todavia no se decide aprobacion/rechazo.
- Todavia no hay formato final de exportacion.
- Todavia no hay integracion con base de datos.

---

### Proximos pasos naturales

- Crear una funcion de alto nivel que combine `exploration_flow` + `offer_reporting`.
- Mantener esa funcion fuera de `swap_service` inicialmente.
- Agregar tests de integracion liviana entre flujo y reporte.
- Evaluar luego si esa capa sera consumida por UI, API o por una capa operativa intermedia.
- Mantener `swap_service` sin cambios hasta definir contrato de consumo.

---

### Notas

Este checkpoint crea la primera salida presentable de ofertas evaluadas.

No cambia el comportamiento tecnico del sistema.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `technical_prefilter`, `candidate_generation`, `candidate_selection` ni `exploration_flow`.

---

## checkpoint-v50-offer-service-facade
Fecha: 2026-05-06

---

### Estado general

Se agrego una fachada liviana de servicio para generar ofertas evaluadas a partir de una asignacion origen.

El bloque combina `exploration_flow` y `offer_reporting` sin modificar `swap_service`.

No decide aprobacion ni rechazo, no persiste resultados y no modifica el comportamiento tecnico del sistema.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Nuevo modulo offer_service

Se agrego el archivo:

- `src/offer_service.py`

Este modulo actua como fachada liviana entre:

- `exploration_flow`
- `offer_reporting`

---

#### 2. Funcion generar_oferta_para_asignacion

Se agrego la funcion:

- `generar_oferta_para_asignacion`

Responsabilidades:

- recibir una asignacion origen
- recibir el roster completo
- recibir `config_file`
- delegar exploracion a `explorar_candidatos_para_oferta`
- delegar salida presentable a `generar_reporte_oferta`
- devolver un `OfferReport`

---

#### 3. Parametros soportados

La funcion soporta:

- `asignacion_origen`
- `asignaciones`
- `config_file`
- `modo_exploracion`
- `top_n`
- `historial_controladores`
- `limite`

Defaults operativos:

- `modo_exploracion = OFERTA_RAPIDA`
- `top_n = 50`
- `historial_controladores = None`
- `limite = None`

---

#### 4. Modos soportados por delegacion

La fachada permite usar los modos ya definidos en `exploration_flow`:

- `OFERTA_RAPIDA`
- `DIAGNOSTICO_COMPLETO`

El modo `EXHAUSTIVO` sigue sin integrarse al flujo operativo.

---

#### 5. Separacion de responsabilidades

`offer_service` no implementa logica tecnica propia.

Solo coordina:

    exploration_flow -> offer_reporting

No clasifica, no puntua tecnicamente, no decide y no persiste.

---

#### 6. Tests especificos

Se agrego el archivo:

- `tests/test_offer_service.py`

Cobertura agregada:

- combina flujo y reporte
- usa defaults operativos
- permite `DIAGNOSTICO_COMPLETO`
- no decide ni persiste
- respeta limite de reporte
- propaga error de limite invalido
- propaga error de modo no soportado

---

### Resultados observados

Suite completa:

    193 passed

---

### Decisiones de diseno reforzadas

- `offer_service` queda separado de `swap_service`.
- `offer_service` no gestiona workflow de requests.
- `offer_service` no aprueba ni rechaza swaps.
- `offer_service` no persiste resultados.
- `offer_service` no modifica historial.
- `offer_service` no modifica clasificacion tecnica.
- `offer_service` no modifica scoring.
- `offer_service` no modifica ranking tecnico.
- `offer_service` no modifica priorizacion historica.
- `swap_service` se mantiene sin cambios.

---

### Limitaciones actuales (conscientes)

- Todavia no se integra `offer_service` con UI o API.
- Todavia no se integra `offer_service` con `swap_service`.
- Todavia no se persisten reportes de oferta.
- Todavia no se actualiza historial desde este flujo.
- Todavia no hay seleccion interactiva de una oferta por parte del usuario.
- Todavia no se crean `SwapRequest` desde ofertas.
- Todavia no hay control de permisos ni auditoria de uso.

---

### Proximos pasos naturales

- Definir contrato para convertir una oferta seleccionada en `SwapRequest`.
- Mantener esa conversion separada de la generacion de ofertas.
- Agregar tests para asegurar que generar ofertas no crea requests.
- Evaluar si la conversion oferta -> request debe vivir en `swap_service` o en una capa intermedia.
- Mantener `offer_service` como fachada de consulta/oferta, no como workflow de aprobacion.

---

### Notas

Este checkpoint crea una fachada operativa liviana para consultar ofertas evaluadas.

No modifica el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `technical_prefilter`, `candidate_generation`, `candidate_selection`, `exploration_flow` ni `offer_reporting`.

---

## checkpoint-v51-offer-request-conversion
Fecha: 2026-05-06

---

### Estado general

Se agrego un contrato para convertir una oferta seleccionada en una solicitud formal de swap.

El bloque crea una capa intermedia entre la salida de oferta y el workflow formal de requests, sin integrar todavia `swap_service`.

No evalua, no decide, no persiste, no aprueba, no rechaza y no aplica swaps.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Nuevo modulo offer_request

Se agrego el archivo:

- `src/offer_request.py`

Este modulo define el contrato para convertir una `OfertaEvaluada` seleccionada en un request formal.

---

#### 2. Contexto de origen de oferta

Se agrego la dataclass:

- `OfferRequestContext`

Campos principales:

- `modo_exploracion`
- `top_n`
- `criterio_seleccion`
- `priorizacion_historica_aplicada`
- `metadata_origen`

Este contexto conserva la trazabilidad de como se genero la oferta.

---

#### 3. Construccion de contexto

Se agrego la funcion:

- `construir_contexto_offer_request`

Responsabilidad:

- recibir metadata de oferta
- construir un `OfferRequestContext`
- preservar la metadata original

---

#### 4. Conversion oferta -> request

Se agrego la funcion:

- `crear_swap_request_desde_oferta`

Responsabilidades:

- validar que la oferta tenga `idx_a`
- validar que la oferta tenga `idx_b`
- crear un request con esos indices
- adjuntar contexto de origen
- adjuntar metadata de oferta
- adjuntar resumen tecnico de la oferta

Campos de trazabilidad adjuntados al request:

- `offer_context`
- `offer_metadata`
- `offer_clasificacion`
- `offer_delta_score`
- `offer_delta_hard`
- `offer_delta_soft`

---

#### 5. Fabrica desacoplada de request

Se agrego una funcion local:

- `crear_swap_request`

Esta funcion actua como wrapper para crear requests sin acoplar `offer_request` a `simulator`.

Esto evita depender de exports que no pertenecen al contrato actual de `simulator`.

---

#### 6. Validacion de indices

Se agrego validacion explicita para ofertas incompletas:

- rechaza oferta sin `idx_a`
- rechaza oferta sin `idx_b`

---

#### 7. Tests especificos

Se agrego el archivo:

- `tests/test_offer_request.py`

Cobertura agregada:

- construye contexto desde metadata
- crea request usando indices de la oferta
- agrega contexto de origen
- preserva metadata de origen
- preserva resumen tecnico de la oferta
- no evalua
- no decide
- no persiste
- rechaza oferta sin `idx_a`
- rechaza oferta sin `idx_b`

---

### Resultados observados

Tests especificos:

    tests/test_offer_request.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- La conversion de oferta a request queda separada de la generacion de ofertas.
- La conversion no pertenece al flujo tecnico de simulacion.
- La conversion no pertenece todavia a `swap_service`.
- `offer_request` no evalua tecnicamente.
- `offer_request` no decide.
- `offer_request` no persiste.
- `offer_request` no aplica swaps.
- `offer_request` no modifica estados.
- `offer_request` conserva trazabilidad de origen.
- `simulator` no se usa como fabrica directa de requests en este checkpoint.

---

### Limitaciones actuales (conscientes)

- La conversion todavia no esta integrada con `swap_service`.
- El request creado todavia no se persiste.
- El request creado todavia no entra al workflow formal.
- No se evalua nuevamente la solicitud.
- No se aprueba ni rechaza.
- No se aplica swap.
- No se actualiza historial.
- No se implementa seleccion interactiva real desde UI.
- No hay auditoria persistida de la oferta elegida.

---

### Proximos pasos naturales

- Definir si la conversion oferta -> request debe integrarse a `swap_service` o permanecer en una capa intermedia.
- Agregar tests para asegurar que una oferta convertida conserva indices y contexto al entrar al workflow.
- Evaluar si la metadata de oferta debe persistirse en el modelo formal de `SwapRequest`.
- Definir si `SwapRequest` debe incorporar campos oficiales de origen de oferta en vez de atributos dinamicos.
- Mantener separado el acto de generar ofertas del acto de crear una solicitud formal.

---

### Notas

Este checkpoint crea el contrato inicial para convertir una oferta seleccionada en request.

No cambia el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `technical_prefilter`, `candidate_generation`, `candidate_selection`, `exploration_flow`, `offer_reporting` ni `offer_service`.

---

## checkpoint-v52-offer-to-request-service
Fecha: 2026-05-06

---

### Estado general

Se implemento la frontera formal `offer_to_request_service.py` para convertir una `OfertaEvaluada` seleccionada en una `SwapRequest` formal.

La conversion respeta el workflow oficial: la request nace en estado `PENDIENTE` y debe ser evaluada luego por `swap_service.evaluar_swap_request`.

El bloque no crea un workflow paralelo de ofertas, no evalua, no decide, no aprueba, no rechaza, no aplica swaps y no persiste por fuera del workflow existente.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Campo oficial offer_origin en SwapRequest

Se modifico el archivo:

- `src/models.py`

Se agrego el campo opcional:

- `offer_origin`

Objetivo:

- centralizar la trazabilidad de origen de una oferta seleccionada
- evitar campos sueltos como `offer_clasificacion`, `offer_delta_score`, etc.
- mantener separada la evidencia observada de la evaluacion formal del request

---

#### 2. Nuevo modulo offer_to_request_service

Se agrego el archivo:

- `src/offer_to_request_service.py`

Responsabilidad:

- convertir una `OfertaEvaluada` seleccionada en una `SwapRequest` formal
- delegar la creacion formal del request a `swap_service.crear_swap_request`
- adjuntar `offer_origin`
- agregar history event `CREADO_DESDE_OFERTA`
- devolver una request formal en estado `PENDIENTE`

---

#### 3. Funcion crear_request_formal_desde_oferta

Se agrego la funcion:

- `crear_request_formal_desde_oferta`

Responsabilidades:

- recibir una `OfertaEvaluada`
- recibir `asignaciones`
- recibir metadata de oferta
- validar `idx_a`
- validar `idx_b`
- validar indices contra roster
- validar `roster_version_id_origen` contra version vigente si esta disponible
- validar `roster_hash_origen` contra hash vigente si esta disponible
- obtener controladores desde el roster
- crear una `SwapRequest` formal mediante `swap_service.crear_swap_request`
- adjuntar `offer_origin`
- agregar evento de history `CREADO_DESDE_OFERTA`

---

#### 4. Validacion de obsolescencia por version/hash

Se agregaron validaciones para rechazar conversiones si la oferta fue generada sobre un roster distinto.

Validaciones soportadas:

- `roster_version_id_origen`
- `roster_version_id`
- `roster_hash_origen`
- `roster_hash`

Si la version o hash de origen no coincide con el vigente informado, se rechaza la conversion y se exige regenerar ofertas.

---

#### 5. Estructura offer_origin

El bloque `offer_origin` contiene datos explicitamente marcados como origen, observados o snapshot.

Campos incluidos:

- `created_from_offer`
- `source_type`
- `modo_exploracion`
- `top_n`
- `criterio_seleccion`
- `priorizacion_historica_aplicada`
- `candidatos_generados`
- `candidatos_prefiltrados`
- `candidatos_seleccionados`
- `candidatos_evaluados`
- `offer_rank_observado`
- `clasificacion_observada`
- `delta_score_observado`
- `delta_hard_observado`
- `delta_soft_observado`
- `roster_version_id_origen`
- `roster_hash_origen`
- `config_file_origen`
- `created_from_offer_at`

---

#### 6. Evento de history

Se agrego el evento:

- `CREADO_DESDE_OFERTA`

Este evento queda en `request.history` y deja trazabilidad de que la solicitud formal nacio desde una oferta evaluada.

---

#### 7. Tests especificos

Se agrego el archivo:

- `tests/test_offer_to_request_service.py`

Cobertura agregada:

- crea request formal desde oferta en estado `PENDIENTE`
- adjunta `offer_origin`
- usa nombres observados/origen/snapshot
- agrega history event `CREADO_DESDE_OFERTA`
- no setea decision
- no nace `EVALUADO`
- no llama evaluacion formal
- no llama resolucion
- no llama aplicar
- rechaza oferta sin `idx_a`
- rechaza oferta sin `idx_b`
- rechaza version de roster distinta
- rechaza hash inconsistente
- preserva `clasificacion_observada` sin convertirla en clasificacion formal
- permite que el request creado sea evaluado formalmente despues por `swap_service.evaluar_swap_request`

---

### Resultados observados

Tests especificos:

    tests/test_offer_to_request_service.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- La oferta evaluada no es una solicitud operativa.
- La solicitud operativa nace exclusivamente como `SwapRequest`.
- `offer_to_request_service` no crea un workflow paralelo.
- `offer_to_request_service` no evalua tecnicamente.
- `offer_to_request_service` no clasifica tecnicamente.
- `offer_to_request_service` no decide.
- `offer_to_request_service` no aprueba.
- `offer_to_request_service` no rechaza.
- `offer_to_request_service` no aplica swaps.
- `offer_to_request_service` no rankea.
- `offer_to_request_service` no modifica roster.
- `offer_to_request_service` no genera candidatos.
- `offer_to_request_service` no hace reporting UI.
- La evaluacion formal sigue ocurriendo en `swap_service.evaluar_swap_request`.
- La request creada desde oferta nace siempre `PENDIENTE`.
- La clasificacion de la oferta queda como `clasificacion_observada`, no como clasificacion formal del request.

---

### Limitaciones actuales (conscientes)

- `offer_origin` todavia no se persiste en SQLite.
- No se agrego columna `offer_origin_json`.
- No se creo tabla normalizada de origen de oferta.
- No se integra todavia la seleccion real desde UI.
- No se actualiza historial de beneficios desde esta conversion.
- No se reutiliza la evaluacion de oferta como evaluacion formal.
- No se crea request en estado `EVALUADO`.
- No se aprueba automaticamente una oferta `BENEFICIOSO`.
- No se implementa bloqueo temporal multiusuario.
- No se implementa concurrencia avanzada.
- No se implementan notificaciones ni analytics.

---

### Proximos pasos naturales

- Definir si `offer_origin` debe persistirse en SQLite como JSON.
- Implementar persistencia minima de `offer_origin` si se decide avanzar.
- Agregar tests para serializar y deserializar requests con origen de oferta.
- Mantener `offer_origin` como evidencia observada, no como evaluacion formal.
- Evaluar luego la integracion UI/API para seleccionar una oferta y crear request.
- Mantener separado el acto de generar ofertas del acto de crear una solicitud formal.

---

### Notas

Este checkpoint implementa la frontera formal entre una oferta evaluada y una solicitud operativa.

No cambia el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service` ni `aplicar_swap_request`.

---

## checkpoint-v53-persist-offer-origin
Fecha: 2026-05-06

---

### Estado general

Se implemento la persistencia minima de `offer_origin` en SQLite.

El bloque permite guardar y recuperar la trazabilidad de origen de una oferta seleccionada dentro de `SwapRequest`, sin crear una tabla nueva y sin modificar el workflow formal de swaps.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Persistencia JSON de offer_origin

Se modifico el archivo:

- `src/request_store.py`

Se agrego soporte para serializar y deserializar:

- `SwapRequest.offer_origin`

El campo se persiste como JSON en la tabla existente:

- `swap_requests`

---

#### 2. Nueva columna offer_origin

Se agrego la columna:

- `offer_origin TEXT`

en la tabla:

- `swap_requests`

La columna almacena el bloque `offer_origin` completo como JSON.

---

#### 3. Migracion segura para bases existentes

Se agregaron helpers internos:

- `_column_exists`
- `_ensure_offer_origin_column`

Comportamiento:

- si la tabla no existe, se crea con la columna `offer_origin`
- si la tabla ya existe sin `offer_origin`, se agrega mediante `ALTER TABLE`
- si la columna ya existe, no hace nada

Esto mantiene compatibilidad con bases SQLite locales existentes.

---

#### 4. Serializacion de request

Se actualizo:

- `serialize_request`

Ahora incluye:

- `json.dumps(request.offer_origin)` si existe
- `None` si no existe

---

#### 5. Deserializacion de request

Se actualizo:

- `deserialize_request`

Ahora reconstruye:

- `offer_origin` como `dict` cuando existe
- `None` cuando no existe

Tambien mantiene compatibilidad defensiva con filas antiguas que no tengan la columna.

---

#### 6. Tests especificos

Se modifico el archivo:

- `tests/test_request_store.py`

Cobertura agregada:

- guarda y recupera request con `offer_origin`
- preserva el bloque completo de origen de oferta
- request sin `offer_origin` vuelve con `offer_origin is None`
- `init_db` asegura que exista la columna `offer_origin`

---

### Resultados observados

Tests focalizados:

    tests/test_request_store.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- `offer_origin` queda persistido como evidencia observada de origen.
- `offer_origin` no reemplaza la evaluacion formal del request.
- `offer_origin` no cambia el estado del request.
- `offer_origin` no contiene decision operativa formal.
- `offer_origin` no aprueba ni rechaza.
- `offer_origin` no aplica swaps.
- La persistencia se mantiene minima y compatible con SQLite.
- No se crea tabla normalizada nueva.
- No se modifica `swap_service`.
- No se modifica el workflow formal.

---

### Limitaciones actuales (conscientes)

- `offer_origin` se persiste como JSON, no como tabla normalizada.
- No hay indices SQL sobre campos internos de `offer_origin`.
- No se implementa busqueda por origen de oferta.
- No se implementa reporting historico por origen de oferta.
- No se implementa auditoria avanzada.
- No se implementa versionado interno del schema de `offer_origin`.
- No se agrega validacion profunda del contenido JSON al recuperar.
- No se implementa limpieza/migracion avanzada de datos viejos.

---

### Proximos pasos naturales

- Agregar tests integrados que cubran el flujo completo:
  `offer_service -> offer_to_request_service -> request_store`.
- Verificar que una oferta seleccionada pueda crear una `SwapRequest` formal, persistirse y recuperarse con `offer_origin`.
- Mantener la evaluacion formal posterior en `swap_service.evaluar_swap_request`.
- Evaluar despues si se necesita reporting historico sobre requests creados desde oferta.
- Mantener `offer_origin` como evidencia observada, no como decision operativa.

---

### Notas

Este checkpoint persiste la trazabilidad de origen de oferta sin cambiar el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `offer_request` ni `offer_to_request_service`.

---

## checkpoint-v54-offer-to-request-integration
Fecha: 2026-05-06

---

### Estado general

Se agrego cobertura de integracion liviana para validar el flujo entre una oferta evaluada seleccionada, la conversion formal a `SwapRequest` y la persistencia en `request_store`.

El bloque no modifica comportamiento productivo. Solo agrega tests de integracion.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Test de integracion oferta -> request -> store

Se agrego el archivo:

- `tests/test_offer_to_request_integration.py`

Este test valida el flujo:

    OfertaEvaluada
    -> offer_to_request_service.crear_request_formal_desde_oferta
    -> request_store.guardar_request
    -> request_store.obtener_request

---

#### 2. Persistencia y recuperacion de offer_origin

Se valida que una request creada desde oferta pueda:

- persistirse
- recuperarse
- conservar `offer_origin`
- conservar `history`
- conservar `roster_version_id`
- conservar indices
- conservar controladores
- seguir en estado `PENDIENTE`

---

#### 3. Separacion entre evidencia observada y evaluacion formal

Se valida que la request recuperada:

- no queda evaluada
- no tiene `decision_sugerida`
- no tiene clasificacion formal
- conserva `clasificacion_observada` solo dentro de `offer_origin`

Esto refuerza que la oferta es evidencia preliminar y no reemplaza la evaluacion formal.

---

#### 4. Validacion de obsolescencia

Se agrego cobertura para rechazar conversiones cuando:

- cambia `roster_version_id`
- cambia `roster_hash`

Esto obliga a regenerar ofertas si el roster vigente ya no coincide con el origen de la oferta.

---

#### 5. Uso del roster vigente real

Se valida que la creacion formal use el roster vigente existente y que la request resultante quede asociada a esa version.

---

### Resultados observados

Tests focalizados:

    tests/test_offer_to_request_integration.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- Una oferta evaluada no es una solicitud operativa.
- Una request formal creada desde oferta nace `PENDIENTE`.
- `offer_origin` es evidencia observada, no evaluacion formal.
- La evaluacion formal sigue perteneciendo a `swap_service.evaluar_swap_request`.
- La conversion rechaza ofertas obsoletas por version/hash.
- `request_store` preserva la trazabilidad de origen.
- No se crea workflow paralelo de ofertas.
- No se modifica `swap_service`.

---

### Limitaciones actuales (conscientes)

- Todavia no hay seleccion real desde UI.
- Todavia no hay endpoint/API.
- Todavia no hay permisos.
- Todavia no hay auditoria avanzada.
- Todavia no hay reporting historico sobre requests creados desde oferta.
- Todavia no se reutiliza la evaluacion de oferta como evaluacion formal.
- Todavia no hay bloqueo temporal multiusuario.
- Todavia no hay concurrencia avanzada.

---

### Proximos pasos naturales

- Agregar una funcion de alto nivel para seleccionar una oferta desde un `OfferReport` y crear una request formal.
- Mantener esa funcion separada de `swap_service`.
- Agregar validacion de posicion/rango de oferta seleccionada.
- Devolver request formal lista para evaluacion.
- Mantener `swap_service` como dueño de evaluar, resolver y aplicar.

---

### Notas

Este checkpoint agrega evidencia de integracion entre oferta evaluada, request formal y persistencia.

No cambia el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `offer_request`, `offer_to_request_service` ni `aplicar_swap_request`.

---
## checkpoint-v55-offer-report-selection
Fecha: 2026-05-06

---

### Estado general

Se agrego soporte para seleccionar una oferta visible desde un `OfferReport` y convertirla en una `SwapRequest` formal.

El bloque completa la frontera entre reporte de ofertas y creacion formal de solicitud, sin evaluar, decidir, persistir ni modificar el workflow formal de swaps.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Seleccion de oferta por posicion

Se modifico el archivo:

- `src/offer_to_request_service.py`

Se agrego la funcion:

- `obtener_oferta_por_posicion`

Responsabilidades:

- recibir un `OfferReport`
- recibir una posicion visible de oferta
- validar que la posicion sea mayor que cero
- buscar la `OfertaEvaluada` correspondiente
- rechazar posiciones inexistentes

---

#### 2. Conversion desde reporte de oferta

Se agrego la funcion:

- `crear_request_formal_desde_reporte_oferta`

Responsabilidades:

- recibir un `OfferReport`
- recibir `posicion_oferta`
- obtener la oferta seleccionada
- delegar conversion a `crear_request_formal_desde_oferta`
- usar la metadata del reporte como origen
- devolver una `SwapRequest` formal

---

#### 3. Reutilizacion del contrato existente

La nueva funcion reutiliza:

- `crear_request_formal_desde_oferta`

Por lo tanto mantiene las mismas garantias:

- request nace `PENDIENTE`
- adjunta `offer_origin`
- registra evento `CREADO_DESDE_OFERTA`
- valida version/hash si se informan
- no evalua
- no decide
- no aplica
- no persiste

---

#### 4. Tests especificos

Se agrego el archivo:

- `tests/test_offer_report_selection.py`

Cobertura agregada:

- obtiene oferta correcta por posicion
- rechaza posicion cero
- rechaza posicion inexistente
- crea request formal usando la oferta seleccionada
- adjunta `offer_origin` usando metadata del reporte
- no evalua
- no decide
- no persiste
- propaga error de version obsoleta
- propaga error de hash obsoleto

---

### Resultados observados

Tests focalizados:

    tests/test_offer_report_selection.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- La posicion de oferta es una seleccion de UI/reporting, no un estado de workflow.
- `OfferReport` sigue siendo salida presentable, no solicitud operativa.
- La solicitud operativa nace recien al crear `SwapRequest`.
- La conversion usa metadata del reporte como origen.
- `offer_origin` conserva evidencia observada.
- La clasificacion de la oferta sigue siendo `clasificacion_observada`.
- La evaluacion formal sigue perteneciendo a `swap_service.evaluar_swap_request`.
- `offer_to_request_service` no crea workflow paralelo.
- `offer_to_request_service` no persiste.

---

### Limitaciones actuales (conscientes)

- Todavia no hay UI real.
- Todavia no hay API.
- Todavia no hay control de permisos.
- Todavia no hay auditoria avanzada.
- Todavia no hay seleccion interactiva persistida.
- Todavia no hay bloqueo temporal multiusuario.
- Todavia no se integra con un endpoint o comando operativo.
- Todavia no se registra quien selecciono la oferta.
- Todavia no se guarda motivo del usuario al seleccionar la oferta.

---

### Proximos pasos naturales

- Agregar una fachada de alto nivel para generar reporte y crear request desde posicion seleccionada.
- O bien detener esta linea y volver a arquitectura para decidir si ya corresponde integrar con UI/API.
- Definir si la seleccion desde reporte debe aceptar `usuario`, `motivo_usuario` o `observacion`.
- Evaluar si conviene persistir inmediatamente el request creado desde seleccion o dejar persistencia explicita.
- Mantener separadas oferta, seleccion, request formal y evaluacion formal.

---

### Notas

Este checkpoint conecta la seleccion visible de una oferta con la creacion formal de una `SwapRequest`.

No cambia el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `offer_request`, `request_store` ni `aplicar_swap_request`.

---


## checkpoint-v56-offer-workflow-selection-facade
Fecha: 2026-05-06

---

### Estado general

Se agrego una fachada de alto nivel para generar ofertas y crear una `SwapRequest` formal desde una oferta seleccionada.

El bloque combina `offer_service` y `offer_to_request_service`, pero no crea un workflow paralelo: la request resultante nace `PENDIENTE` y debe continuar por el workflow formal de `swap_service`.

No evalua, no decide, no persiste, no aprueba, no rechaza y no aplica swaps.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Nuevo modulo offer_workflow_service

Se agrego el archivo:

- `src/offer_workflow_service.py`

Este modulo actua como fachada de alto nivel para coordinar:

    offer_service -> offer_to_request_service

---

#### 2. Resultado estructurado de seleccion

Se agrego la dataclass:

- `OfferSelectionResult`

Campos principales:

- `reporte`
- `request`

Propiedades agregadas:

- `request_id`
- `cantidad_ofertas`

---

#### 3. Funcion generar_oferta_y_crear_request

Se agrego la funcion:

- `generar_oferta_y_crear_request`

Responsabilidades:

- generar un `OfferReport` desde una asignacion origen
- seleccionar una oferta visible por posicion
- crear una `SwapRequest` formal desde esa oferta
- devolver reporte y request juntos

---

#### 4. Parametros soportados

La funcion soporta:

- `asignacion_origen`
- `asignaciones`
- `config_file`
- `posicion_oferta`
- `modo_exploracion`
- `top_n`
- `historial_controladores`
- `limite_reporte`
- `roster_version_id_vigente`
- `roster_hash_vigente`

Defaults operativos:

- `modo_exploracion = OFERTA_RAPIDA`
- `top_n = 50`
- `historial_controladores = None`
- `limite_reporte = None`

---

#### 5. Separacion de responsabilidades

`offer_workflow_service` solo coordina.

No implementa logica tecnica propia.

No clasifica, no puntua, no evalua formalmente, no decide, no persiste y no aplica.

---

#### 6. Tests especificos

Se agrego el archivo:

- `tests/test_offer_workflow_service.py`

Cobertura agregada:

- combina correctamente `offer_service` y `offer_to_request_service`
- pasa parametros de generacion de oferta
- pasa parametros de seleccion/conversion a request
- usa defaults operativos
- no evalua
- no decide
- no persiste
- propaga error de posicion invalida
- propaga error de roster obsoleto

---

### Resultados observados

Tests focalizados:

    tests/test_offer_workflow_service.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- `offer_workflow_service` es fachada de coordinacion, no workflow formal.
- La oferta evaluada sigue sin ser una solicitud operativa.
- La solicitud operativa nace como `SwapRequest`.
- La request creada desde oferta nace `PENDIENTE`.
- La evaluacion formal sigue perteneciendo a `swap_service.evaluar_swap_request`.
- La resolucion sigue perteneciendo a `swap_service.resolver_swap_request`.
- La aplicacion sigue perteneciendo a `swap_service.aplicar_swap_request`.
- `offer_workflow_service` no persiste.
- `offer_workflow_service` no decide.
- `offer_workflow_service` no crea un flujo paralelo de aprobacion.

---

### Limitaciones actuales (conscientes)

- Todavia no hay UI real.
- Todavia no hay API.
- Todavia no hay permisos.
- Todavia no hay auditoria de usuario seleccionante.
- Todavia no se persiste automaticamente la request creada.
- Todavia no se evalua formalmente en esta fachada.
- Todavia no se integra con endpoints o comandos operativos.
- Todavia no hay bloqueo temporal multiusuario.
- Todavia no hay concurrencia avanzada.

---

### Proximos pasos naturales

- Definir si la request creada por esta fachada debe persistirse automaticamente o si la persistencia debe seguir siendo explicita.
- Agregar metadata opcional de usuario/motivo de seleccion.
- Evaluar si corresponde crear una funcion de aplicacion operativa completa:
  generar oferta -> seleccionar -> crear request -> persistir -> evaluar formalmente
  manteniendo cada responsabilidad separada.
- Volver a arquitectura antes de integrar persistencia automatica o evaluacion formal automatica.

---

### Notas

Este checkpoint conecta la generacion de ofertas con la seleccion de una oferta y la creacion de una request formal.

No cambia el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `offer_to_request_service`, `request_store` ni `aplicar_swap_request`.

---

## checkpoint-v57-offer-selection-metadata
Fecha: 2026-05-06

---

### Estado general

Se agrego metadata opcional de seleccion de usuario dentro de `offer_origin`.

El bloque permite registrar quien selecciono una oferta, el motivo de seleccion y una nota operativa, sin modificar el workflow formal de swaps.

No evalua, no decide, no persiste automaticamente, no aprueba, no rechaza y no aplica swaps.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Metadata opcional de seleccion

Se agregaron campos opcionales dentro de `offer_origin`:

- `selected_by`
- `selection_reason`
- `selection_note`

Estos campos permiten trazabilidad operativa de la seleccion visible de una oferta.

---

#### 2. Propagacion desde crear_request_formal_desde_oferta

Se modifico el archivo:

- `src/offer_to_request_service.py`

Se actualizo la funcion:

- `crear_request_formal_desde_oferta`

Ahora acepta:

- `selected_by`
- `selection_reason`
- `selection_note`

Y los incorpora dentro de `offer_origin`.

---

#### 3. Propagacion desde crear_request_formal_desde_reporte_oferta

Se actualizo la funcion:

- `crear_request_formal_desde_reporte_oferta`

Ahora propaga:

- `selected_by`
- `selection_reason`
- `selection_note`

hacia `crear_request_formal_desde_oferta`.

---

#### 4. Propagacion desde offer_workflow_service

Se modifico el archivo:

- `src/offer_workflow_service.py`

Se actualizo la funcion:

- `generar_oferta_y_crear_request`

Ahora acepta y propaga:

- `selected_by`
- `selection_reason`
- `selection_note`

hacia `crear_request_formal_desde_reporte_oferta`.

---

#### 5. History enriquecido

El evento:

- `CREADO_DESDE_OFERTA`

ahora incluye `selected_by` cuando esta disponible.

Esto permite identificar en el historial quien selecciono la oferta sin convertir esa seleccion en decision operativa formal.

---

#### 6. Tests especificos

Se agrego el archivo:

- `tests/test_offer_selection_metadata.py`

Cobertura agregada:

- request creada desde oferta adjunta metadata de seleccion
- request creada sin metadata deja campos en `None`
- request creada desde reporte propaga metadata de seleccion
- metadata de seleccion no evalua, no decide y no persiste

Tambien se actualizo:

- `tests/test_offer_workflow_service.py`

Cobertura agregada:

- `generar_oferta_y_crear_request` propaga metadata de seleccion

---

### Resultados observados

Tests focalizados:

    tests/test_offer_selection_metadata.py tests/test_offer_workflow_service.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- La seleccion de una oferta no es una decision operativa.
- `selected_by` identifica quien selecciono la oferta, no quien aprobo el swap.
- `selection_reason` es motivo de seleccion, no motivo de aprobacion/rechazo.
- `selection_note` es observacion operativa, no resolucion formal.
- La request creada sigue naciendo `PENDIENTE`.
- La evaluacion formal sigue perteneciendo a `swap_service.evaluar_swap_request`.
- La decision formal sigue perteneciendo a `swap_service.resolver_swap_request`.
- `offer_origin` sigue siendo evidencia observada y trazabilidad de origen.
- No se crea workflow paralelo.

---

### Limitaciones actuales (conscientes)

- No hay validacion de identidad de usuario.
- No hay permisos.
- No hay auditoria avanzada.
- No se persiste automaticamente la request.
- No se evalua automaticamente la request.
- No se notifica a terceros.
- No hay UI real.
- No hay API.
- No hay bloqueo temporal multiusuario.
- No hay concurrencia avanzada.

---

### Proximos pasos naturales

- Definir si corresponde una funcion de alto nivel que cree y persista la request seleccionada.
- Evaluar si esa funcion debe vivir en `offer_workflow_service` o en una capa de aplicacion superior.
- Mantener la persistencia como paso explicito salvo decision arquitectonica contraria.
- Agregar tests de persistencia de `selected_by`, `selection_reason` y `selection_note` dentro de `offer_origin`.
- Evaluar luego integracion con UI/API.

---

### Notas

Este checkpoint agrega trazabilidad de seleccion sin cambiar el workflow formal.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `request_store` ni `aplicar_swap_request`.

---

## checkpoint-v58-offer-selection-metadata-persistence
Fecha: 2026-05-06

---

### Estado general

Se agrego cobertura de persistencia para la metadata de seleccion incluida dentro de `offer_origin`.

El bloque valida que los campos de seleccion de usuario sobreviven al guardado y recuperacion desde SQLite, aprovechando la persistencia JSON de `offer_origin` ya implementada previamente.

No se modifico codigo productivo. Solo se agregaron tests.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Tests de persistencia de metadata de seleccion

Se agrego el archivo:

- `tests/test_offer_selection_metadata_persistence.py`

Este archivo valida que una request creada desde oferta puede persistirse y recuperarse conservando dentro de `offer_origin` los campos:

- `selected_by`
- `selection_reason`
- `selection_note`

---

#### 2. Persistencia de selected_by

Se valida que el campo:

- `selected_by`

se guarda y recupera correctamente dentro de `offer_origin`.

Ejemplo cubierto:

- `SUP_ACC_CBA`

---

#### 3. Persistencia de selection_reason

Se valida que el campo:

- `selection_reason`

se guarda y recupera correctamente dentro de `offer_origin`.

Este campo representa motivo de seleccion de oferta, no motivo de aprobacion o rechazo.

---

#### 4. Persistencia de selection_note

Se valida que el campo:

- `selection_note`

se guarda y recupera correctamente dentro de `offer_origin`.

Este campo representa una nota operativa de seleccion, no una resolucion formal.

---

#### 5. Campos None preservados

Se valida que si la request se crea sin metadata de seleccion:

- `selected_by`
- `selection_reason`
- `selection_note`

se conservan como `None` dentro de `offer_origin` al persistir y recuperar.

---

#### 6. Separacion con decision formal

Se valida que la metadata de seleccion persistida:

- no reemplaza decision formal
- no setea `decision_sugerida`
- no crea `decision_operativa`
- no crea `aprobado_por`
- no crea `rechazado_por`
- no cambia el estado `PENDIENTE`

---

### Resultados observados

Tests focalizados:

    tests/test_offer_selection_metadata_persistence.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- `selected_by` identifica quien selecciono una oferta, no quien aprobo un swap.
- `selection_reason` es motivo de seleccion, no decision operativa.
- `selection_note` es una observacion de seleccion, no resolucion formal.
- `offer_origin` sigue siendo evidencia observada.
- La request creada desde oferta sigue naciendo `PENDIENTE`.
- La evaluacion formal sigue perteneciendo a `swap_service.evaluar_swap_request`.
- La decision formal sigue perteneciendo a `swap_service.resolver_swap_request`.
- La persistencia de `offer_origin` no altera el workflow formal.
- No se crea workflow paralelo.

---

### Limitaciones actuales (conscientes)

- No hay validacion de identidad de usuario.
- No hay permisos.
- No hay auditoria avanzada.
- No se persiste automaticamente la request desde la fachada de seleccion.
- No se evalua automaticamente la request.
- No hay UI real.
- No hay API.
- No hay bloqueo temporal multiusuario.
- No hay concurrencia avanzada.
- No hay busqueda por campos internos de `offer_origin`.

---

### Proximos pasos naturales

- Agregar persistencia explicita de una request creada desde oferta.
- Mantener la persistencia separada de la generacion de ofertas.
- Mantener la persistencia separada de la evaluacion formal.
- Validar que persistir una request desde oferta no evalua, no decide y no aplica.
- Evaluar luego si una fachada superior debe combinar:
  - generar oferta
  - seleccionar oferta
  - crear request
  - persistir request

---

### Notas

Este checkpoint agrega cobertura de persistencia de metadata de seleccion dentro de `offer_origin`.

No cambia comportamiento productivo.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `offer_to_request_service`, `offer_workflow_service`, `request_store` ni `aplicar_swap_request`.

---

## checkpoint-v59-explicit-offer-request-persistence
Fecha: 2026-05-06

---

### Estado general

Se agrego persistencia explicita para una `SwapRequest` creada desde oferta.

El bloque permite guardar una request creada desde `offer_workflow_service` o `offer_to_request_service`, manteniendo separadas las responsabilidades de generar oferta, seleccionar oferta, crear request formal, persistir request y evaluar formalmente.

No evalua, no decide, no aprueba, no rechaza y no aplica swaps.

La suite completa quedo en verde.

---

### Que quedo implementado

#### 1. Persistencia explicita desde offer_workflow_service

Se modifico el archivo:

- `src/offer_workflow_service.py`

Se agrego la funcion:

- `persistir_request_creado_desde_oferta`

Responsabilidad:

- recibir una `SwapRequest` creada desde oferta
- validar que este en estado `PENDIENTE`
- validar que no tenga `decision_sugerida`
- validar que tenga `offer_origin`
- delegar persistencia a `request_store.guardar_request`
- devolver la request persistida

---

#### 2. Validaciones previas a persistir

La funcion rechaza:

- requests que no esten en estado `PENDIENTE`
- requests que ya tengan `decision_sugerida`
- requests sin `offer_origin`

Esto evita persistir como request desde oferta algo que ya pertenece a otra etapa del workflow formal.

---

#### 3. Persistencia sin workflow paralelo

La funcion solo persiste.

No llama:

- `evaluar_swap_request`
- `resolver_swap_request`
- `aplicar_swap_request`

No modifica:

- estado
- decision
- roster
- evaluacion formal
- clasificacion formal

---

#### 4. Tests unitarios

Se agrego el archivo:

- `tests/test_offer_workflow_persistence.py`

Cobertura agregada:

- delega en `request_store.guardar_request`
- requiere estado `PENDIENTE`
- rechaza request con `decision_sugerida`
- requiere `offer_origin`
- no evalua
- no resuelve
- no aplica

---

#### 5. Test de integracion con SQLite

Se agrego el archivo:

- `tests/test_offer_workflow_persistence_integration.py`

Cobertura agregada:

- crea request formal desde oferta
- agrega metadata de seleccion
- persiste explicitamente la request
- recupera la request desde `request_store`
- conserva `offer_origin`
- conserva `selected_by`
- conserva `selection_reason`
- conserva `selection_note`
- conserva estado `PENDIENTE`
- conserva `decision_sugerida is None`

---

### Resultados observados

Tests focalizados:

    tests/test_offer_workflow_persistence.py tests/test_offer_workflow_persistence_integration.py passed

Suite completa:

    passed

---

### Decisiones de diseno reforzadas

- Persistir una request desde oferta es un paso explicito.
- Generar oferta no persiste.
- Seleccionar oferta no persiste automaticamente.
- Crear request formal desde oferta no evalua.
- Persistir request desde oferta no evalua.
- Persistir request desde oferta no decide.
- Persistir request desde oferta no aprueba ni rechaza.
- Persistir request desde oferta no aplica swaps.
- La request persistida sigue entrando al workflow formal como `PENDIENTE`.
- La evaluacion formal sigue perteneciendo a `swap_service.evaluar_swap_request`.
- `offer_origin` sigue siendo evidencia observada y trazabilidad, no decision formal.

---

### Limitaciones actuales (conscientes)

- Todavia no hay funcion que combine automaticamente:
  - generar oferta
  - seleccionar oferta
  - crear request
  - persistir request
  - evaluar formalmente

- Todavia no se evalua automaticamente despues de persistir.
- Todavia no hay API.
- Todavia no hay UI real.
- Todavia no hay permisos.
- Todavia no hay auditoria avanzada de usuario.
- Todavia no hay bloqueo temporal multiusuario.
- Todavia no hay concurrencia avanzada.
- Todavia no hay notificaciones.

---

### Proximos pasos naturales

- Definir si corresponde una fachada superior para:
  - generar oferta
  - seleccionar oferta
  - crear request
  - persistir request

- Mantener la evaluacion formal como paso separado.
- Agregar test que valide el flujo completo hasta request persistida desde una sola funcion si se decide avanzar.
- Evaluar si se necesita registrar un evento de history adicional al momento de persistir explicitamente.
- Volver a arquitectura antes de automatizar evaluacion formal o decisiones.

---

### Notas

Este checkpoint agrega persistencia explicita de request creada desde oferta sin cambiar el workflow formal de swaps.

No toca `engine`, `scoring`, `simulator`, `swap_service`, `candidate_generation`, `technical_prefilter`, `candidate_selection`, `exploration_flow`, `offer_reporting`, `offer_service`, `offer_to_request_service`, `request_store` ni `aplicar_swap_request`.

---