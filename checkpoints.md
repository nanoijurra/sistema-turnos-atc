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