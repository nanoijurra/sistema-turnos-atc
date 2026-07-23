# Contexto resumen

Sistema de swaps ATC en Python.

Este documento resume el estado arquitectonico vigente.

Para detalles completos, ver:

```text
docs/contexto_sistema.md
docs/decisiones.md
docs/contratos.md
docs/invariantes.md
docs/modelo_dominio.md
docs/diccionario.md
checkpoints.md
```

---

## Estructura general

Camino tradicional del workflow formal:

```text
swap_service
-> simulator
-> engine.py
-> validator.py
```

Responsabilidades principales:

```text
engine -> validacion tecnica tradicional de reglas
validator.py -> reglas tecnicas tradicionales sobre asignaciones operativas
simulator -> evaluacion tecnica y clasificacion del swap
swap_service -> decision operativa, workflow y aplicacion
scoring -> score y validez agregada
models -> entidades del dominio
roster_store -> versionado/persistencia de rosters normalizados
request_store -> persistencia de SwapRequest e historial
```

---

## Camino calendar-aware paralelo

Adicionalmente, existe un camino diagnostico calendar-aware paralelo para rosters importados:

```text
resultado_importacion / dias_importados
-> roster_calendar_aware_entrypoint.py
-> diagnostico timeline
-> ResultadoDiagnosticoCalendarAware
```

Modulos principales:

```text
roster_import_service -> importacion y normalizacion de roster real
roster_day_timeline -> timeline diaria importada
roster_timeline_validator -> reglas calendar-aware sobre timeline
roster_timeline_diagnostics -> resumen y comparacion diagnostica
roster_calendar_aware_entrypoint -> entrypoint publico paralelo
```

Este camino:

```text
no reemplaza engine.py
no reemplaza validator.py
no decide swaps
no modifica SwapRequest
no aplica cambios de roster
no altera el workflow formal
```

---

## Flujo formal de swaps

El flujo formal vigente es:

```text
crear_swap_request
-> evaluar_swap_request
-> resolver_swap_request
-> aplicar_swap_request
```

Estados principales:

```text
PENDIENTE
EVALUADO
APROBADO
RECHAZADO
CANCELADO
APLICADO
```

La aplicacion solo puede ocurrir desde `APROBADO`.

La decision operativa y la clasificacion tecnica son planos distintos.

---

## Estado actual

Estado consolidado luego de v103:

```text
workflow formal consolidado
engine tradicional vigente
validator.py tradicional vigente
roster import real acotado disponible
timeline diaria importada disponible
validadores calendar-aware disponibles
diagnostico calendar-aware disponible
entrypoint calendar-aware paralelo disponible
documentacion principal compatibilizada
```

Validacion actual:

```text
py -m pytest -q
440 passed
```

---

## Resultado sobre CSV real local

Sobre el CSV real local acotado:

```text
data/imports/csv_ok.csv
```

La cadena calendar-aware validada es:

```text
CSV real local
-> importador
-> dias_importados
-> diagnostico calendar-aware
-> 0 hard
-> 1 soft
```

La unica observacion vigente sobre timeline es:

```text
EXCESO_LIBRES_CONSECUTIVOS
```

---

## Reglas de oro

```text
clasificacion tecnica != decision operativa
decision operativa != estado del workflow
diagnostico calendar-aware != decision de swap
timeline diaria != Asignacion
LIBRE != NO_OPERATIVO_DOCUMENTADO
entrypoint calendar-aware != engine tradicional
```

---

## Restricciones vigentes

No integrar ni reemplazar sin decision explicita:

```text
engine.py
validator.py
workflow formal
```

No subir CSV real local al repositorio.

Mantener cambios chicos, testeados y versionados por checkpoint.

---
