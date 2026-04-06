# Cierre de ambiguedad semantica

## 1. Objetivo

Resolver la ambigüedad semántica crítica del sistema de swaps ATC, originada en la colisión entre:

- clasificación técnica
- decisión operativa
- estado del workflow

y establecer mecanismos de control para prevenir drift futuro.

---

## 2. Resultado alcanzado

Se consolidó una separación estricta entre tres planos del sistema.

### Evaluacion tecnica
- origen: `simulator`
- valores:
  - BENEFICIOSO
  - ACEPTABLE
  - RECHAZABLE

### Decision operativa
- origen: `swap_service`
- valores:
  - VIABLE
  - OBSERVAR
  - RECHAZAR

### Estado del workflow
- valores:
  - PENDIENTE
  - EVALUADO
  - APROBADO
  - RECHAZADO
  - CANCELADO
  - APLICADO

### Regla critica consolidada
- `simulator` clasifica
- `swap_service` decide
- el estado refleja el ciclo de vida del request
- aplicar no reevalúa

---

## 3. Correccion semantica aplicada

Se eliminó el uso ambiguo de:
- `APROBABLE`
- la confusión entre “aprobado” como decisión y como estado

Se definió:
- `VIABLE` = decisión operativa sugerida
- `APROBADO` = estado posterior a resolución

Se elimino ademas el uso generico e impreciso de terminologia ambigua en documentacion semantica, cuando generaba mezcla entre planos

---

## 4. Alineacion documental

Se actualizaron y alinearon:
- `modelo_dominio.md`
- `invariantes.md`
- `decisiones.md`
- `contratos.md`
- `contexto_sistema.md`

### Resultado
- coherencia arquitectónica alta
- coherencia semántica alta
- sin contradicciones activas
- sin ambigüedad entre planos

---

## 5. Nuevo subsistema de control: semantic_guard

Se incorporó un subsistema auxiliar para proteger coherencia futura.

### Semantic lint
Valida el estado actual del sistema y detecta:
- ambigüedad terminológica
- mezcla de planos
- reaparición de términos prohibidos

### Semantic diff
Valida drift entre versiones y detecta:
- pérdida de taxonomías
- cambios semánticos no controlados
- reintroducción de ambigüedad

---

## 6. Alcance de semantic_guard

Aplica sobre:
- documentación semántica dentro de `docs/`

Excluye:
- archivos de control de proceso, como `estado_docs.md`

---

## 7. Impacto arquitectonico

### Impacto positivo
- se elimina una ambigüedad estructural crítica
- se blinda la separación de responsabilidades
- se reduce riesgo de drift semántico
- se introduce validación automática de coherencia

### No impacto
- no se altera la lógica de negocio del sistema
- no se redefinen responsabilidades entre capas
- no se modifica el comportamiento esperado del flujo

---

## 8. Estado actual

- semantic lint: OK
- semantic diff: OK
- documentación alineada
- contratos estabilizados

---

## 9. Proximo paso

Retomar evolución arquitectónica sobre base semántica estable, priorizando:

1. cierre definitivo de frontera `simulator ↔ swap_service`
2. endurecimiento de contratos entre capas
3. consolidación de `roster_service`