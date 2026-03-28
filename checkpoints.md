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

---

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