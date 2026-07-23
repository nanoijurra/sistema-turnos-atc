# Estado de documentacion

## 1. Version conceptual del sistema

Estado:

```text
estable
en evolucion controlada
con camino calendar-aware paralelo en diagnostico
```

Ultima revision documental:

```text
checkpoint-v103-actualizacion-contexto-sistema-calendar-aware
```

Validacion actual:

```text
py -m pytest -q
440 passed
```

---

## 2. Estado de documentos principales

### decisiones.md

Estado:

```text
consistente
compatibilizado con calendar-aware
```

Ultima decision relevante:

```text
Decision 53 - Timeline diaria y diagnostico calendar-aware paralelo
```

---

### contratos.md

Estado:

```text
consistente
compatibilizado con calendar-aware
```

Ultimo contrato relevante:

```text
Contrato 25 - EntryPoint paralelo calendar-aware
```

---

### invariantes.md

Estado:

```text
consistente
incluye invariantes calendar-aware
```

Invariantes calendar-aware agregadas:

```text
CA-1 - LIBRE no equivale a NO_OPERATIVO_DOCUMENTADO
CA-2 - La timeline diaria no reemplaza asignaciones operativas
CA-3 - El diagnostico calendar-aware no reemplaza al engine
CA-4 - El entrypoint calendar-aware no decide swaps
CA-5 - El workflow formal no cambia
CA-6 - La integracion al motor general requiere decision explicita
```

---

### modelo_dominio.md

Estado:

```text
consistente
incluye timeline diaria importada
```

Conceptos incorporados:

```text
RosterDiaImportado
RosterDayStatus
OPERATIVO
LIBRE
NO_OPERATIVO_DOCUMENTADO
OPERATIVO_CONFIGURABLE_NO_ACTIVO
FUERA_DE_ALCANCE
DESCONOCIDO
```

---

### diccionario.md

Estado:

```text
consistente
incluye terminos calendar-aware
```

Terminos incorporados:

```text
calendar-aware
timeline diaria
dias_importados
RosterDiaImportado
RosterDayStatus
LIBRE
NO_OPERATIVO_DOCUMENTADO
diagnostico calendar-aware
entrypoint paralelo calendar-aware
ResultadoDiagnosticoCalendarAware
EXCESO_LIBRES_CONSECUTIVOS
```

---

### contexto_sistema.md

Estado:

```text
actualizado
compatibilizado con v96-v103
```

Incluye:

```text
arquitectura actual
estructura del proyecto
flujo operativo
capas del sistema
camino calendar-aware paralelo
estado actual
restricciones vigentes
```

---

### contexto_resumen.md

Estado:

```text
actualizado en v104
resumen breve del estado vigente
```

---

## 3. Decisiones recientes relevantes

Checkpoints recientes:

```text
v96 -> validadores calendar-aware sobre timeline
v97 -> diagnostico tecnico calendar-aware
v98 -> comparacion tradicional vs timeline
v99 -> smoke diagnostico sobre CSV real local
v100 -> entrypoint paralelo calendar-aware
v101 -> smoke entrypoint calendar-aware sobre CSV real local
v102 -> compatibilizacion documental calendar-aware
v103 -> actualizacion contexto_sistema calendar-aware
```

---

## 4. Estado arquitectonico resumido

Camino tradicional:

```text
swap_service
-> simulator
-> engine.py
-> validator.py
```

Camino calendar-aware paralelo:

```text
resultado_importacion / dias_importados
-> roster_calendar_aware_entrypoint.py
-> diagnostico timeline
-> ResultadoDiagnosticoCalendarAware
```

Ambos caminos conviven.

El camino calendar-aware no reemplaza al camino tradicional.

---

## 5. Terminos criticos

```text
clasificacion tecnica != decision operativa
decision operativa != estado del workflow
diagnostico calendar-aware != decision de swap
timeline diaria != Asignacion
LIBRE != NO_OPERATIVO_DOCUMENTADO
entrypoint calendar-aware != engine.py
validator.py tradicional sigue vigente
```

---

## 6. Deudas o pendientes documentales

Pendientes posibles:

```text
revisar contexto_resumen.md cuando cambie la arquitectura
revisar estado_docs.md despues de cada bloque documental grande
evaluar reporte operativo calendar-aware en checkpoint futuro
definir integracion al motor general solo mediante decision explicita futura
```

No hay deuda vigente que obligue a modificar codigo.

---

## 7. Checklist previo a tag

Antes de crear un tag:

```text
git status limpio antes de empezar
diff revisado
tests en verde
checkpoint agregado
commit realizado
tag creado
push realizado
working tree clean al cierre
```

---

## 8. Regla principal

La clasificacion tecnica, la decision operativa, el estado del workflow y el diagnostico calendar-aware representan planos distintos del sistema.

No deben confundirse ni colapsarse.

---
