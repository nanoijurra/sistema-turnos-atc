# CHECKPOINTS DEL PROYECTO - SISTEMA SWAPS ATC

Registro activo desde v96. Preparacion de v112; v112 aun no cerrado.

Indice anterior: [v1-v95](docs/hitos/indice_checkpoints_v1_v95.md).
Historia integra previa: tag `checkpoint-v111-auditoria-documental-integral-v110`.
Los bloques conservan sus afirmaciones historicas; las divergencias documentales
v102/v103 se describen en v111 y en `docs/hitos/auditoria_documental_v110.md`.

---

## checkpoint-v96-reglas-calendar-aware-timeline

Fecha: 2026-06-23

---

### Estado general

Se implementaron validadores calendar-aware sobre la timeline diaria importada.

El objetivo fue validar reglas operativas reales usando `dias_importados`, sin depender solamente de `asignaciones_operativas`.

Esta version no reemplaza todavia el motor general ni modifica el workflow formal.

---

### Problema corregido conceptualmente

Antes de v96, el validador tradicional analizaba solo asignaciones operativas A/B/C.

Eso generaba falsos positivos porque no veia:

* dias libres
* huecos calendario
* no operativos documentados
* cortes reales entre turnos

El diagnostico previo habia mostrado:

```text
32 hard
5 Secuencia
27 Noches consecutivas
```

Luego se confirmo que esas violaciones eran falsos positivos por perdida de contexto calendario.

---

### Regla conceptual aplicada

Las nuevas validaciones trabajan sobre una timeline completa por controlador:

```text
OPERATIVO
LIBRE
NO_OPERATIVO_DOCUMENTADO
OPERATIVO_CONFIGURABLE_NO_ACTIVO
FUERA_DE_ALCANCE
DESCONOCIDO
```

Esto permite distinguir correctamente:

```text
LIBRE = celda vacia / sin asignacion
NO_OPERATIVO_DOCUMENTADO = codigo explicito como LA, LD, EN, PSI, RTA, RTB, etc.
```

---

### Archivos agregados

Se agrego:

* `src/roster_timeline_validator.py`
* `tests/test_roster_timeline_validator.py`

---

### Reglas implementadas sobre timeline

Se agregaron validadores para:

```text
hard: no mas de 5 dias consecutivos A/B
hard: no mas de 3 dias consecutivos C
hard: descanso mayor a 12 h entre turnos operativos consecutivos reales
soft: warning por mas de 5 dias libres consecutivos
```

---

### Funciones agregadas

En `src/roster_timeline_validator.py`:

```text
validar_max_ab_consecutivos_timeline
validar_max_c_consecutivos_timeline
validar_libres_consecutivos_timeline
validar_descanso_minimo_timeline
validar_timeline_controlador
validar_timeline_importada
```

---

### Severidades consolidadas

#### Hard

```text
EXCESO_AB_CONSECUTIVOS
EXCESO_C_CONSECUTIVOS
DESCANSO_INSUFICIENTE_TIMELINE
```

#### Soft

```text
EXCESO_LIBRES_CONSECUTIVOS
```

---

### Validaciones principales

#### Noches consecutivas

Ahora las noches C solo cuentan como consecutivas si ocurren en fechas calendario consecutivas.

Ejemplo que ya no genera falso positivo:

```text
C 02/06
C 04/06
C 05/06
C 08/06
```

Las fechas con cortes calendario reinician la racha.

#### A/B consecutivos

Se valida como hard si hay mas de 5 dias consecutivos con turnos A/B.

Ejemplo:

```text
A
B
A
B
A
B
```

Resultado:

```text
EXCESO_AB_CONSECUTIVOS
```

#### Dias libres

Se valida como soft si hay mas de 5 dias consecutivos con estado:

```text
LIBRE
```

No cuenta como libre:

```text
NO_OPERATIVO_DOCUMENTADO
```

Por lo tanto, codigos como `LD`, `LA`, `EN`, `PSI`, `RTA`, `RTB`, etc. cortan o separan la racha libre, pero no se cuentan como dias libres.

---

### Smoke sobre CSV real

Se ejecuto validacion sobre el CSV real acotado:

```text
Dias importados: 450
Asignaciones operativas: 213
Eventos no operativos: 28
Violaciones timeline: 1
```

Resultado por codigo:

```text
EXCESO_LIBRES_CONSECUTIVOS: 1
```

Resultado por severidad:

```text
soft: 1
```

Detalle:

```text
SOFT | EXCESO_LIBRES_CONSECUTIVOS |
Mas de 5 dias libres consecutivos para CARREVEDO SARAI:
6 dias entre 2026-06-02 y 2026-06-07.
```

---

### Resultado interpretado

El resultado esperado se cumplio:

```text
0 hard
1 soft
```

Esto confirma que las 32 hard previas no eran problemas reales del CSV, sino falsos positivos del validador anterior.

La unica observacion vigente corresponde a una racha libre mayor a 5 dias, correctamente clasificada como warning/soft.

---

### Restricciones respetadas

No se modifico:

* `validator.py`
* `engine.py`
* simulator
* scoring
* swap_service
* workflow formal
* roster_store
* request_store
* catalogo documental
* reglas tecnicas actuales del motor tradicional

No se conecto todavia la timeline al engine general.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v96 deja disponible un validador calendar-aware separado del motor actual.

La cadena validada queda:

```text
CSV real
-> importador
-> dias_importados
-> validar_timeline_importada
-> 0 hard
-> 1 soft por libres consecutivos
```

---

### Proximo paso sugerido

El proximo paso natural sera decidir integracion controlada:

```text
v97 - conectar validacion calendar-aware al diagnostico tecnico
```

Opciones posibles:

```text
1. Mantener validator.py tradicional para fixtures antiguos y agregar diagnostico timeline aparte.
2. Integrar reglas timeline al engine mediante nuevo entrypoint.
3. Reemplazar progresivamente reglas antiguas por reglas calendar-aware.
```

La opcion mas segura es la 1 o la 2, no reemplazar directamente.

---

## checkpoint-v97-diagnostico-tecnico-calendar-aware

Se agrego un modulo de diagnostico calendar-aware separado del workflow formal.

Archivos agregados:

```text
src/roster_timeline_diagnostics.py
tests/test_roster_timeline_diagnostics.py
```

---

## checkpoint-v98-comparacion-diagnostico-validadores

Fecha: 2026-06-26

---

### Estado general

Se agrego una comparacion controlada entre el diagnostico tradicional y el diagnostico calendar-aware basado en timeline.

El objetivo fue dejar evidencia tecnica comparable entre ambos enfoques, sin modificar todavia el motor general ni reemplazar el validador tradicional.

Esta version mantiene el diagnostico como una capa separada del workflow formal.

---

### Problema abordado

Hasta v96 ya se habia confirmado que el validador tradicional podia generar falsos positivos sobre rosters importados porque analiza solo asignaciones operativas A/B/C.

Ese enfoque no ve correctamente:

* dias libres
* huecos calendario
* no operativos documentados
* cortes reales entre turnos

El diagnostico calendar-aware, en cambio, trabaja sobre `dias_importados`, por lo que puede evaluar las reglas operativas usando la timeline diaria completa.

v98 no cambia reglas ni decisiones del sistema.

v98 solo agrega una estructura de comparacion para observar diferencias entre:

```text
validador tradicional
diagnostico timeline calendar-aware
```

---

### Alcance implementado

Se agrego una comparacion diagnostica que permite recibir:

```text
resumen tradicional ya calculado
diagnostico timeline ya calculado
```

Y devuelve una comparacion con:

```text
total_tradicional
hard_tradicional
soft_tradicional
total_timeline
hard_timeline
soft_timeline
diferencia_total
diferencia_hard
timeline_valido_sin_hard
requiere_revision_calendar_aware
```

---

### Archivos modificados

Se modificaron:

* `src/roster_timeline_diagnostics.py`
* `tests/test_roster_timeline_diagnostics.py`

---

### Clases agregadas

En `src/roster_timeline_diagnostics.py` se agrego:

```text
ComparacionDiagnosticoValidadores
```

---

### Funciones agregadas

En `src/roster_timeline_diagnostics.py` se agrego:

```text
comparar_diagnostico_tradicional_vs_timeline
```

---

### Comportamiento agregado

La nueva comparacion permite:

```text
- aceptar un resumen tradicional como dict u objeto con atributos
- aceptar un diagnostico timeline como objeto con atributos
- normalizar valores numericos total / hard / soft
- calcular diferencia total entre ambos diagnosticos
- calcular diferencia hard entre ambos diagnosticos
- marcar si corresponde revision calendar-aware
```

La marca:

```text
requiere_revision_calendar_aware
```

queda en `True` cuando:

```text
hard_tradicional > hard_timeline
y
timeline_valido_sin_hard == True
```

Esto permite identificar escenarios donde el validador tradicional informa mas hard que el diagnostico calendar-aware.

---

### Ejemplo conceptual cubierto

Caso representativo:

```text
tradicional:
total = 32
hard = 32
soft = 0

timeline:
total = 1
hard = 0
soft = 1
valido_sin_hard = True
```

Resultado esperado:

```text
diferencia_total = 31
diferencia_hard = 32
requiere_revision_calendar_aware = True
```

Este caso representa el escenario ya diagnosticado en versiones anteriores: muchas violaciones hard del validador tradicional pueden corresponder a falsos positivos por perdida de contexto calendario.

---

### Tests agregados

Se agregaron tests para validar:

```text
comparacion con diferencia hard entre tradicional y timeline
comparacion sin diferencia hard entre tradicional y timeline
```

Tambien se mantuvieron verdes los tests previos de diagnostico timeline:

```text
resumen vacio sin violaciones
conteo por codigo y severidad
diagnostico timeline sin violaciones
diagnostico timeline con soft por libres
diagnostico desde resultado de importacion
error controlado si falta dias_importados
```

---

### Validaciones ejecutadas

Se ejecuto test focalizado:

```text
python -m pytest tests/test_roster_timeline_diagnostics.py -q
```

Resultado:

```text
8 passed
```

Se ejecuto suite completa:

```text
python -m pytest -q
```

Resultado:

```text
434 passed
```

---

### Restricciones respetadas

No se modifico:

* `validator.py`
* `engine.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* roster_store
* request_store
* catalogo documental
* reglas tecnicas actuales del motor tradicional

No se conecto todavia la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v98 deja disponible una comparacion diagnostica entre validacion tradicional y validacion calendar-aware.

La cadena conceptual disponible queda:

```text
resumen tradicional
+
diagnostico timeline
-> comparar_diagnostico_tradicional_vs_timeline
-> diferencia_total
-> diferencia_hard
-> requiere_revision_calendar_aware
```

Esto permite documentar tecnicamente diferencias entre ambos enfoques antes de decidir cualquier integracion al motor general.

---

### Proximo paso sugerido

El proximo paso natural seria definir una integracion controlada sin reemplazo abrupto:

```text
v99 - entrypoint calendar-aware para diagnostico operativo o engine separado
```

Opciones posibles:

```text
1. Mantener el diagnostico separado y agregar smoke sobre CSV real.
2. Crear un entrypoint calendar-aware paralelo al engine tradicional.
3. Integrar timeline al engine solo para rosters importados con dias_importados.
4. Reemplazar progresivamente reglas tradicionales despues de mas evidencia.
```

La opcion mas segura sigue siendo avanzar con entrypoint paralelo o smoke diagnostico, sin reemplazar directamente `validator.py`.

---

---

## checkpoint-v99-smoke-diagnostico-csv-real

Fecha: 2026-06-26

---

### Estado general

Se agrego un smoke diagnostico sobre el CSV real local importado.

El objetivo fue ejecutar la cadena calendar-aware completa sobre el archivo real acotado `data/imports/csv_ok.csv`, usando la funcionalidad ya incorporada en v96, v97 y v98.

Esta version no agrega reglas nuevas.

Esta version no modifica el motor general ni el workflow formal.

---

### Problema abordado

Hasta v98 ya existian:

```text
validadores calendar-aware sobre timeline
diagnostico tecnico sobre dias_importados
comparacion diagnostica entre tradicional y timeline
```

Pero faltaba una validacion reproducible sobre el CSV real local que confirmara la cadena completa:

```text
CSV real
-> importacion strict=True
-> dias_importados
-> diagnostico timeline
-> comparacion contra resumen tradicional conocido
```

v99 agrega ese smoke controlado.

---

### Alcance implementado

Se agrego un test smoke local que:

```text
- verifica si existe data/imports/csv_ok.csv
- si no existe, omite el test con pytest.skip
- importa el CSV real con anio=2026 y mes=6
- genera diagnostico timeline desde resultado de importacion
- compara contra el resumen tradicional conocido
- valida los totales esperados del roster real acotado
```

El CSV real no se sube al repositorio.

El directorio `data/imports/` sigue ignorado por Git.

---

### Archivos agregados

Se agrego:

```text
tests/test_smoke_diagnostico_csv_real.py
```

---

### Archivos modificados

Se modifico:

```text
checkpoints.md
```

---

### Cadena validada

La cadena validada por el smoke queda:

```text
data/imports/csv_ok.csv
-> importar_roster_desde_csv(anio=2026, mes=6, strict=True)
-> resultado_importacion.dias_importados
-> generar_diagnostico_desde_importacion
-> comparar_diagnostico_tradicional_vs_timeline
```

---

### Resultado esperado de importacion

El smoke confirma:

```text
dias_importados = 450
asignaciones_operativas = 213
eventos_no_operativos = 28
```

---

### Resultado esperado timeline

El diagnostico timeline confirma:

```text
total_dias_importados = 450
total_violaciones = 1
total_hard = 0
total_soft = 1
valido_sin_hard = True
```

Resultado por codigo:

```text
EXCESO_LIBRES_CONSECUTIVOS = 1
```

---

### Comparacion contra resumen tradicional conocido

Se usa como referencia diagnostica el resumen tradicional ya observado:

```text
tradicional:
total = 32
hard = 32
soft = 0
```

Se compara contra:

```text
timeline:
total = 1
hard = 0
soft = 1
valido_sin_hard = True
```

Resultado esperado de comparacion:

```text
diferencia_total = 31
diferencia_hard = 32
requiere_revision_calendar_aware = True
```

---

### Interpretacion

El smoke confirma que, sobre el CSV real local:

```text
la validacion tradicional conocida informa 32 hard
la validacion calendar-aware informa 0 hard y 1 soft
```

Esto refuerza la conclusion previa:

```text
las hard tradicionales eran falsos positivos por perdida de contexto calendario
```

La unica observacion vigente sobre timeline es soft:

```text
EXCESO_LIBRES_CONSECUTIVOS
```

---

### Validaciones ejecutadas

Se ejecuto test smoke focalizado:

```text
python -m pytest tests/test_smoke_diagnostico_csv_real.py -q
```

Resultado:

```text
1 passed
```

Se ejecuto suite completa:

```text
python -m pytest -q
```

Resultado:

```text
435 passed
```

---

### Restricciones respetadas

No se modifico:

* `validator.py`
* `engine.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* roster_store
* request_store
* catalogo documental
* reglas tecnicas actuales del motor tradicional

No se conecto todavia la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

No se subio el CSV real al repositorio.

---

### Estado final

v99 deja un smoke reproducible para validar el diagnostico calendar-aware sobre el CSV real local.

La cadena consolidada queda:

```text
CSV real local
-> importador
-> dias_importados
-> diagnostico timeline
-> comparacion tradicional vs timeline
-> 0 hard timeline
-> 1 soft timeline
```

---

### Proximo paso sugerido

El proximo paso natural seria crear un entrypoint paralelo calendar-aware, sin reemplazar el engine tradicional:

```text
v100 - entrypoint paralelo calendar-aware
```

Objetivo sugerido:

```text
- crear una funcion publica de diagnostico operativo calendar-aware
- recibir resultado de importacion o dias_importados
- devolver resumen usable por capas superiores
- no tocar engine.py
- no tocar validator.py
- no cambiar workflow formal
```

La opcion segura sigue siendo mantener ambos caminos:

```text
engine tradicional
diagnostico calendar-aware paralelo
```

Antes de integrar o reemplazar, conviene seguir acumulando evidencia tecnica y mantener compatibilidad con fixtures anteriores.

---

---

## checkpoint-v100-entrypoint-paralelo-calendar-aware

Fecha: 2026-06-26

---

### Estado general

Se agrego un entrypoint paralelo calendar-aware para diagnosticar rosters importados usando la timeline diaria.

El objetivo fue crear una puerta de entrada publica, estable y separada del motor tradicional.

Esta version no reemplaza `engine.py`.

Esta version no modifica `validator.py`.

Esta version no altera el workflow formal.

---

### Problema abordado

Hasta v99 ya existian:

```text
validadores calendar-aware sobre timeline
diagnostico tecnico sobre dias_importados
comparacion tradicional vs timeline
smoke sobre CSV real local
```

Pero para que capas superiores pudieran usar esa informacion, todavia habia que conocer modulos internos como:

```text
roster_timeline_validator
roster_timeline_diagnostics
dias_importados
```

v100 agrega un entrypoint paralelo y explicito para consumir ese diagnostico sin acoplarse a los detalles internos.

---

### Alcance implementado

Se agrego una funcion publica para diagnosticar directamente dias importados:

```text
diagnosticar_dias_importados_calendar_aware
```

Se agrego una funcion publica para diagnosticar directamente un resultado de importacion:

```text
diagnosticar_importacion_calendar_aware
```

Ambas devuelven un resultado estable:

```text
ResultadoDiagnosticoCalendarAware
```

---

### Archivos agregados

Se agregaron:

```text
src/roster_calendar_aware_entrypoint.py
tests/test_roster_calendar_aware_entrypoint.py
```

---

### Archivos modificados

Se modifico:

```text
checkpoints.md
```

---

### Clases agregadas

En `src/roster_calendar_aware_entrypoint.py` se agrego:

```text
ResultadoDiagnosticoCalendarAware
```

---

### Funciones agregadas

En `src/roster_calendar_aware_entrypoint.py` se agregaron:

```text
diagnosticar_dias_importados_calendar_aware
diagnosticar_importacion_calendar_aware
```

---

### Resultado devuelto por el entrypoint

El resultado calendar-aware expone:

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

### Cadena disponible

Para dias importados:

```text
dias_importados
-> diagnosticar_dias_importados_calendar_aware
-> ResultadoDiagnosticoCalendarAware
```

Para resultado de importacion:

```text
resultado_importacion
-> diagnosticar_importacion_calendar_aware
-> ResultadoDiagnosticoCalendarAware
```

Internamente, el entrypoint reutiliza el diagnostico ya existente:

```text
generar_diagnostico_timeline_importada
generar_diagnostico_desde_importacion
```

---

### Interpretacion conceptual

v100 crea un camino paralelo:

```text
CAMINO TRADICIONAL
swap_service
-> engine.py
-> validator.py tradicional
-> resultado tecnico tradicional
```

```text
CAMINO CALENDAR-AWARE PARALELO
resultado_importacion / dias_importados
-> roster_calendar_aware_entrypoint.py
-> diagnostico timeline
-> ResultadoDiagnosticoCalendarAware
```

El camino tradicional sigue igual.

El camino calendar-aware queda disponible para diagnostico operativo y futuras capas superiores.

---

### Tests agregados

Se agregaron tests para validar:

```text
diagnostico calendar-aware sin violaciones
diagnostico calendar-aware con soft por libres consecutivos
diagnostico desde resultado de importacion con dias_importados
error controlado si el resultado de importacion no contiene dias_importados
```

---

### Validaciones ejecutadas

Se ejecuto test focalizado del nuevo entrypoint:

```text
python -m pytest tests/test_roster_calendar_aware_entrypoint.py -q
```

Resultado:

```text
4 passed
```

Se ejecutaron tests relacionados:

```text
python -m pytest tests/test_roster_timeline_diagnostics.py -q
python -m pytest tests/test_smoke_diagnostico_csv_real.py -q
```

Resultado:

```text
8 passed
1 passed
```

Se ejecuto suite completa:

```text
python -m pytest -q
```

Resultado:

```text
439 passed
```

---

### Restricciones respetadas

No se modifico:

* `validator.py`
* `engine.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* roster_store
* request_store
* catalogo documental
* reglas tecnicas actuales del motor tradicional

No se conecto todavia la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

No se modifico el CSV real.

---

### Estado final

v100 deja disponible un entrypoint paralelo calendar-aware estable y reusable.

El sistema ahora cuenta con dos caminos claramente separados:

```text
engine tradicional
diagnostico calendar-aware paralelo
```

Esto permite que futuras capas superiores consulten el diagnostico calendar-aware sin alterar el comportamiento actual del motor ni del workflow formal.

---

### Proximo paso sugerido

El proximo paso natural seria agregar un smoke o test de uso del entrypoint sobre el CSV real local:

```text
v101 - smoke entrypoint calendar-aware sobre CSV real
```

Objetivo sugerido:

```text
- importar data/imports/csv_ok.csv
- llamar diagnosticar_importacion_calendar_aware
- confirmar 0 hard y 1 soft
- confirmar por_codigo EXCESO_LIBRES_CONSECUTIVOS
- no tocar engine.py
- no tocar validator.py
- no cambiar workflow formal
```

La integracion con el motor general deberia seguir postergada hasta tener mas evidencia y una decision explicita.

---

---

## checkpoint-v101-smoke-entrypoint-calendar-aware-csv-real

Fecha: 2026-06-26

---

### Estado general

Se agrego un smoke sobre el CSV real local usando el entrypoint paralelo calendar-aware creado en v100.

El objetivo fue validar que la nueva puerta de entrada publica funcione correctamente sobre el roster real acotado `data/imports/csv_ok.csv`.

Esta version no agrega logica nueva.

Esta version no modifica el motor general ni el workflow formal.

---

### Problema abordado

Hasta v100 ya existia un entrypoint paralelo calendar-aware:

```text
diagnosticar_importacion_calendar_aware
diagnosticar_dias_importados_calendar_aware
```

Pero faltaba confirmar que ese entrypoint funcionara directamente sobre el CSV real local.

v101 agrega ese smoke controlado.

---

### Alcance implementado

Se agrego un test smoke local que:

```text
- verifica si existe data/imports/csv_ok.csv
- si no existe, omite el test con pytest.skip
- importa el CSV real con anio=2026 y mes=6
- llama diagnosticar_importacion_calendar_aware
- valida el resultado calendar-aware esperado
```

El CSV real no se sube al repositorio.

El directorio `data/imports/` sigue ignorado por Git.

---

### Archivos agregados

Se agrego:

```text
tests/test_smoke_entrypoint_calendar_aware_csv_real.py
```

---

### Archivos modificados

Se modifico:

```text
checkpoints.md
```

---

### Cadena validada

La cadena validada por el smoke queda:

```text
data/imports/csv_ok.csv
-> importar_roster_desde_csv(anio=2026, mes=6, strict=True)
-> diagnosticar_importacion_calendar_aware
-> ResultadoDiagnosticoCalendarAware
```

---

### Resultado esperado calendar-aware

El smoke confirma:

```text
total_dias_importados = 450
total_violaciones = 1
total_hard = 0
total_soft = 1
valido_sin_hard = True
```

Resultado por codigo:

```text
EXCESO_LIBRES_CONSECUTIVOS = 1
```

Resultado por severidad:

```text
SOFT = 1
```

---

### Interpretacion

El smoke confirma que el entrypoint paralelo calendar-aware puede diagnosticar el CSV real local sin pasar por el engine tradicional.

El resultado sigue siendo consistente con el diagnostico previo:

```text
0 hard
1 soft
```

La unica observacion vigente sobre timeline corresponde a:

```text
EXCESO_LIBRES_CONSECUTIVOS
```

---

### Validaciones ejecutadas

Se ejecuto test smoke focalizado:

```text
python -m pytest tests/test_smoke_entrypoint_calendar_aware_csv_real.py -q
```

Resultado:

```text
1 passed
```

Se ejecutaron tests relacionados:

```text
python -m pytest tests/test_roster_calendar_aware_entrypoint.py -q
python -m pytest tests/test_smoke_diagnostico_csv_real.py -q
```

Resultado:

```text
4 passed
1 passed
```

Se ejecuto suite completa:

```text
python -m pytest -q
```

Resultado:

```text
440 passed
```

---

### Restricciones respetadas

No se modifico:

* `validator.py`
* `engine.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* roster_store
* request_store
* catalogo documental
* reglas tecnicas actuales del motor tradicional

No se conecto todavia la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

No se modifico el CSV real.

No se subio el CSV real al repositorio.

---

### Estado final

v101 deja validado que el entrypoint paralelo calendar-aware funciona sobre el CSV real local.

La cadena consolidada queda:

```text
CSV real local
-> importador
-> diagnosticar_importacion_calendar_aware
-> ResultadoDiagnosticoCalendarAware
-> 0 hard
-> 1 soft
```

Esto confirma que capas superiores podrian consumir el diagnostico calendar-aware sin alterar el engine tradicional ni el workflow formal.

---

### Proximo paso sugerido

El proximo paso natural seria construir una salida resumida mas legible para capas superiores:

```text
v102 - reporte operativo calendar-aware
```

Objetivo sugerido:

```text
- transformar ResultadoDiagnosticoCalendarAware en un reporte simple
- exponer estado general, hard, soft y codigos principales
- mantener la salida como diagnostico
- no tocar engine.py
- no tocar validator.py
- no cambiar workflow formal
```

La integracion con el motor general deberia seguir postergada hasta tener una decision explicita.

---
---

## checkpoint-v102-compatibilizacion-documental-calendar-aware

Fecha: 2026-06-26

---

### Estado general

Se compatibilizo la documentacion principal con la arquitectura calendar-aware incorporada entre v96 y v101.

El objetivo fue documentar la timeline diaria importada, el diagnostico calendar-aware y el entrypoint paralelo, sin modificar codigo ni tests.

Esta version es exclusivamente documental.

---

### Problema abordado

La documentacion principal ya contenia decisiones y contratos sobre:

```text
engine tradicional
workflow formal de SwapRequest
importacion de roster real acotado
codigos de roster
elegibilidad funcional
```

Pero no reflejaba todavia los conceptos agregados entre v96 y v101:

```text
dias_importados
timeline diaria importada
LIBRE
NO_OPERATIVO_DOCUMENTADO
diagnostico calendar-aware
entrypoint paralelo calendar-aware
ResultadoDiagnosticoCalendarAware
```

v102 agrega esa capa documental sin reescribir la arquitectura historica.

---

### Alcance implementado

Se agregaron secciones documentales al final de los documentos principales.

La estrategia fue append-only:

```text
agregar bloques nuevos
no reordenar documentos
no reescribir decisiones anteriores
no cambiar contratos previos
no alterar contenido historico
```

---

### Archivos modificados

Se modificaron:

```text
docs/decisiones.md
docs/contratos.md
docs/invariantes.md
docs/modelo_dominio.md
docs/diccionario.md
checkpoints.md
```

---

### Decision documental agregada

En `docs/decisiones.md` se agrego:

```text
Decision 53 - Timeline diaria y diagnostico calendar-aware paralelo
```

La decision documenta:

```text
- la timeline diaria importada como representacion complementaria
- la diferencia entre LIBRE y NO_OPERATIVO_DOCUMENTADO
- la validacion calendar-aware sobre dias_importados
- el diagnostico calendar-aware como camino paralelo
- el entrypoint publico calendar-aware
- la convivencia entre engine tradicional y camino calendar-aware
- la restriccion de no reemplazar engine.py ni validator.py
```

---

### Contrato documental agregado

En `docs/contratos.md` se agrego:

```text
Contrato 25 - EntryPoint paralelo calendar-aware
```

El contrato documenta:

```text
- modulo responsable: src/roster_calendar_aware_entrypoint.py
- funciones publicas:
  - diagnosticar_dias_importados_calendar_aware
  - diagnosticar_importacion_calendar_aware
- resultado publico:
  - ResultadoDiagnosticoCalendarAware
- responsabilidades permitidas
- responsabilidades prohibidas
- relacion con engine y validator
- relacion con workflow formal
- relacion con importacion de roster
```

---

### Invariantes agregadas

En `docs/invariantes.md` se agregaron invariantes calendar-aware:

```text
CA-1 - LIBRE no equivale a NO_OPERATIVO_DOCUMENTADO
CA-2 - La timeline diaria no reemplaza asignaciones operativas
CA-3 - El diagnostico calendar-aware no reemplaza al engine
CA-4 - El entrypoint calendar-aware no decide swaps
CA-5 - El workflow formal no cambia
CA-6 - La integracion al motor general requiere decision explicita
```

---

### Modelo de dominio agregado

En `docs/modelo_dominio.md` se agrego la seccion:

```text
Timeline diaria importada
```

La seccion documenta:

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

Tambien documenta la relacion con `Asignacion` y con el diagnostico calendar-aware.

---

### Diccionario agregado

En `docs/diccionario.md` se agrego:

```text
Terminos calendar-aware
```

Se documentaron definiciones para:

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

### Restricciones respetadas

No se modifico:

* `src/`
* `tests/`
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* reglas tecnicas actuales
* CSV real local

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Validaciones ejecutadas

Se ejecuto la suite completa desde VS Code:

```text
python -m pytest -q
```

Resultado:

```text
440 passed
```

Nota:

```text
En una terminal PowerShell externa, python resolvio al alias de Microsoft Store.
La suite fue ejecutada correctamente desde VS Code, donde el entorno Python del proyecto esta disponible.
```

---

### Estado final

v102 deja compatibilizada la documentacion principal con la arquitectura calendar-aware actual.

La documentacion ahora refleja que el sistema tiene dos caminos diferenciados:

```text
camino tradicional:
swap_service
-> simulator
-> engine.py
-> validator.py

camino calendar-aware paralelo:
resultado_importacion / dias_importados
-> roster_calendar_aware_entrypoint.py
-> diagnostico timeline
-> ResultadoDiagnosticoCalendarAware
```

Ambos caminos conviven.

El camino calendar-aware sigue siendo diagnostico y paralelo.

La integracion al motor general queda postergada hasta decision explicita futura.

---

### Proximo paso sugerido

El proximo paso natural seria revisar si `docs/contexto_sistema.md` debe actualizarse con un resumen breve de los nuevos modulos.

Posible checkpoint:

```text
v103 - actualizacion de contexto_sistema calendar-aware
```

Objetivo sugerido:

```text
- agregar roster_day_timeline.py
- agregar roster_timeline_validator.py
- agregar roster_timeline_diagnostics.py
- agregar roster_calendar_aware_entrypoint.py
- documentar que son diagnosticos paralelos
- no tocar codigo
- no tocar tests
```

---
---

## checkpoint-v103-actualizacion-contexto-sistema-calendar-aware

Fecha: 2026-06-26

---

### Estado general

Se actualizo `docs/contexto_sistema.md` para reflejar la arquitectura actual del sistema luego de la incorporacion del camino calendar-aware paralelo.

El objetivo fue que el documento de contexto general mencione los modulos nuevos, el estado actual del sistema y la separacion entre el camino tradicional y el camino calendar-aware.

Esta version es exclusivamente documental.

---

### Problema abordado

`docs/contexto_sistema.md` habia quedado desactualizado respecto de los checkpoints recientes.

El documento todavia describia un estado anterior del proyecto y no reflejaba adecuadamente:

```text
roster_day_timeline.py
roster_timeline_validator.py
roster_timeline_diagnostics.py
roster_calendar_aware_entrypoint.py
dias_importados
timeline diaria importada
diagnostico calendar-aware
entrypoint paralelo calendar-aware
```

Ademas, el archivo tenia un problema estructural de Markdown: la seccion de estructura del proyecto abria un bloque `text` que dejaba parte del contenido posterior dentro del mismo bloque.

v103 corrige el documento completo para dejarlo consistente y legible.

---

### Alcance implementado

Se reemplazo completo el contenido de:

```text
docs/contexto_sistema.md
```

La actualizacion mantiene el objetivo original del documento:

```text
describir el contexto operativo, arquitectonico y de estado del sistema
```

Pero ahora incorpora el estado vigente del proyecto luego de v96-v102.

---

### Archivos modificados

Se modificaron:

```text
docs/contexto_sistema.md
checkpoints.md
```

---

### Contenido actualizado

El nuevo contexto del sistema documenta:

```text
- proposito
- alcance
- dominio del problema
- arquitectura actual
- estructura del proyecto
- flujo operativo
- capas del sistema
- camino calendar-aware paralelo
- estado actual
- reglas de negocio
- principios de diseno
- evolucion planificada
- restricciones
- forma de trabajo
```

---

### Arquitectura actual documentada

Se documento el camino tradicional:

```text
swap_service
-> simulator
-> engine.py
-> validator.py
```

Tambien se documento el camino calendar-aware paralelo:

```text
resultado_importacion / dias_importados
-> roster_calendar_aware_entrypoint.py
-> diagnostico timeline
-> ResultadoDiagnosticoCalendarAware
```

---

### Modulos nuevos incorporados al contexto

Se agregaron al contexto general:

```text
src/roster_import_service.py
src/roster_code_catalog.py
src/roster_day_timeline.py
src/roster_timeline_validator.py
src/roster_timeline_diagnostics.py
src/roster_calendar_aware_entrypoint.py
```

---

### Capas documentadas

Se actualizaron las responsabilidades de:

```text
src.engine
src.validator
src.scoring
src.simulator
src.swap_service
src.roster_import_service
src.roster_day_timeline
src.roster_timeline_validator
src.roster_timeline_diagnostics
src.roster_calendar_aware_entrypoint
```

---

### Restricciones reafirmadas

Se dejo documentado que el camino calendar-aware:

```text
- no reemplaza engine.py
- no reemplaza validator.py
- no modifica SwapRequest
- no decide swaps
- no aplica swaps
- no modifica workflow formal
- no crea RosterVersion
```

---

### Estado actual incorporado

Se documento el estado consolidado:

```text
engine tradicional vigente
validator.py tradicional vigente
workflow formal de SwapRequest consolidado
roster_store versiona rosters normalizados
request_store persiste requests e historial
roster_import_service importa CSV/matriz real acotada
timeline diaria importada disponible
validadores calendar-aware disponibles
diagnostico calendar-aware disponible
entrypoint calendar-aware paralelo disponible
```

Tambien se documentaron los checkpoints recientes:

```text
v96 -> validadores calendar-aware sobre timeline
v97 -> diagnostico tecnico calendar-aware
v98 -> comparacion tradicional vs timeline
v99 -> smoke diagnostico sobre CSV real local
v100 -> entrypoint paralelo calendar-aware
v101 -> smoke entrypoint calendar-aware sobre CSV real local
v102 -> compatibilizacion documental calendar-aware
```

---

### Resultado real documentado

Se incorporo el resultado validado sobre CSV real local:

```text
CSV real local
-> importador
-> dias_importados
-> diagnostico calendar-aware
-> 0 hard
-> 1 soft
```

La unica observacion vigente sobre timeline:

```text
EXCESO_LIBRES_CONSECUTIVOS
```

---

### Validaciones ejecutadas

Se ejecuto suite completa con launcher de Windows:

```text
py -m pytest -q
```

Resultado:

```text
440 passed
```

Nota:

```text
En este entorno, python -m pytest -q no resuelve correctamente por alias de Microsoft Store.
Para este repo se usa py -m pytest -q.
```

---

### Restricciones respetadas

No se modifico:

* `src/`
* `tests/`
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* reglas tecnicas actuales
* CSV real local

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v103 deja actualizado el documento global de contexto del sistema.

La documentacion principal queda mejor alineada con la arquitectura vigente:

```text
decisiones.md -> decisiones calendar-aware documentadas
contratos.md -> contrato del entrypoint calendar-aware documentado
invariantes.md -> invariantes calendar-aware documentadas
modelo_dominio.md -> timeline diaria documentada
diccionario.md -> terminos calendar-aware documentados
contexto_sistema.md -> contexto general actualizado
```

---

### Proximo paso sugerido

El proximo paso natural seria revisar documentos resumen secundarios:

```text
v104 - actualizacion de contexto_resumen y estado_docs
```

Objetivo sugerido:

```text
- actualizar docs/contexto_resumen.md
- actualizar docs/estado_docs.md
- reflejar v96-v103
- no tocar codigo
- no tocar tests
```

---

## checkpoint-v104-actualizacion-contexto-resumen-y-estado-docs

Fecha: 2026-06-26

---

### Estado general

Se actualizaron los documentos resumen secundarios para reflejar el estado vigente del sistema luego de v96-v103.

El objetivo fue alinear `docs/contexto_resumen.md` y `docs/estado_docs.md` con la arquitectura actual, especialmente con el camino calendar-aware paralelo.

Esta version es exclusivamente documental.

---

### Problema abordado

Los documentos secundarios todavia describian un estado anterior del proyecto.

`docs/contexto_resumen.md` mencionaba:

```text
refactor en curso
tests fallando tras refactor
decisiones incorrectas VIABLE vs RECHAZAR
inconsistencias entre indices y controladores
```

Ese contenido ya no representaba el estado actual del repo.

`docs/estado_docs.md` tambien conservaba referencias antiguas, como:

```text
ultima seccion: 26
ultima seccion: 16
engine = unica fuente de reglas
estado: en ajuste
```

Luego de v96-v103, la documentacion principal ya habia sido compatibilizada con:

```text
dias_importados
timeline diaria importada
diagnostico calendar-aware
entrypoint paralelo calendar-aware
ResultadoDiagnosticoCalendarAware
```

v104 actualiza los documentos resumen para que no contradigan ese estado consolidado.

---

### Alcance implementado

Se reemplazo completo el contenido de:

```text
docs/contexto_resumen.md
docs/estado_docs.md
```

La actualizacion mantiene los documentos como resumen, no como fuente principal de detalle.

Para detalle completo se siguen usando:

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

### Archivos modificados

Se modificaron:

```text
docs/contexto_resumen.md
docs/estado_docs.md
checkpoints.md
```

---

### Actualizacion de contexto_resumen.md

`docs/contexto_resumen.md` ahora resume:

```text
- estructura general del sistema
- camino tradicional del workflow formal
- responsabilidades principales por modulo
- camino calendar-aware paralelo
- flujo formal de swaps
- estado actual consolidado
- resultado sobre CSV real local
- reglas de oro
- restricciones vigentes
```

Tambien documenta explicitamente que el camino calendar-aware:

```text
no reemplaza engine.py
no reemplaza validator.py
no decide swaps
no modifica SwapRequest
no aplica cambios de roster
no altera el workflow formal
```

---

### Actualizacion de estado_docs.md

`docs/estado_docs.md` ahora refleja el estado de los documentos principales:

```text
decisiones.md -> consistente y compatibilizado con calendar-aware
contratos.md -> consistente y compatibilizado con calendar-aware
invariantes.md -> incluye invariantes calendar-aware
modelo_dominio.md -> incluye timeline diaria importada
diccionario.md -> incluye terminos calendar-aware
contexto_sistema.md -> actualizado y compatibilizado con v96-v103
contexto_resumen.md -> actualizado en v104
```

Tambien incorpora los checkpoints recientes:

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

### Estado arquitectonico reflejado

Se documento nuevamente la convivencia de dos caminos.

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

### Terminos criticos reafirmados

Se reafirmaron las diferencias conceptuales:

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

### Validaciones ejecutadas

Se ejecuto suite completa desde Codex usando `uv` con `PYTHONPATH=.`:

```text
uv run pytest -q
```

Resultado:

```text
440 passed
```

Nota operativa:

```text
En VS Code del usuario, la validacion equivalente se ejecuta con py -m pytest -q.
En el shell de Codex, py no esta disponible, por lo que se uso uv run pytest -q con PYTHONPATH=.
```

---

### Restricciones respetadas

No se modifico:

* `src/`
* `tests/`
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* reglas tecnicas actuales
* CSV real local

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v104 deja actualizados los documentos resumen secundarios.

La documentacion secundaria ya no describe un estado viejo con refactor inestable ni tests fallando.

Ahora refleja el estado consolidado:

```text
workflow formal vigente
engine tradicional vigente
validator.py tradicional vigente
camino calendar-aware paralelo disponible
documentacion principal compatibilizada
suite completa verde
```

---

### Proximo paso sugerido

El proximo paso natural seria decidir si corresponde construir una salida mas legible del diagnostico calendar-aware:

```text
v105 - reporte operativo calendar-aware
```

Objetivo sugerido:

```text
- transformar ResultadoDiagnosticoCalendarAware en un reporte simple
- exponer estado general, hard, soft y codigos principales
- mantener la salida como diagnostico
- no tocar engine.py
- no tocar validator.py
- no cambiar workflow formal
```

Tambien es valido pausar implementacion y revisar manualmente la documentacion antes de avanzar.

---

## checkpoint-v105-reporte-operativo-calendar-aware

Fecha: 2026-06-26

---

### Estado general

Se agrego un reporte operativo calendar-aware para presentar de forma estable el resultado del diagnostico paralelo.

El objetivo fue transformar `ResultadoDiagnosticoCalendarAware` en una salida mas legible para capas superiores, manteniendo su caracter estrictamente diagnostico.

Esta version no integra el camino calendar-aware al engine general.

Esta version no modifica el workflow formal.

---

### Problema abordado

Hasta v104 ya existia un entrypoint calendar-aware paralelo:

```text
diagnosticar_dias_importados_calendar_aware
diagnosticar_importacion_calendar_aware
ResultadoDiagnosticoCalendarAware
```

Ese resultado era estable, pero todavia no existia una capa especifica para presentarlo como reporte operativo simple.

v105 agrega esa capa sin cambiar la semantica del diagnostico.

---

### Alcance implementado

Se agrego un modulo nuevo:

```text
src/roster_calendar_aware_report.py
```

El modulo permite:

```text
- recibir ResultadoDiagnosticoCalendarAware
- calcular estado_general
- exponer totales hard / soft / total
- ordenar codigos principales
- exponer detalles de violaciones
- serializar el reporte con to_dict
- generar reporte desde resultado de importacion usando el entrypoint existente
```

---

### Archivos agregados

Se agregaron:

```text
src/roster_calendar_aware_report.py
tests/test_roster_calendar_aware_report.py
```

---

### Archivos modificados

Se modifico:

```text
checkpoints.md
```

---

### Clases agregadas

En `src/roster_calendar_aware_report.py` se agregaron:

```text
ResumenCodigoCalendarAware
DetalleViolacionCalendarAware
ReporteOperativoCalendarAware
```

---

### Funciones agregadas

En `src/roster_calendar_aware_report.py` se agregaron:

```text
generar_reporte_operativo_calendar_aware
generar_reporte_operativo_importacion_calendar_aware
```

---

### Constantes agregadas

Se agregaron:

```text
MENSAJE_REPORTE_CALENDAR_AWARE
ESTADO_VALIDO_SIN_HARD
ESTADO_INVALIDO_CON_HARD
```

---

### Resultado del reporte

El reporte operativo calendar-aware expone:

```text
mensaje
estado_general
total_dias_importados
total_violaciones
total_hard
total_soft
valido_sin_hard
codigos_principales
detalles
metadata
```

Estados generales:

```text
VALIDO_SIN_HARD
INVALIDO_CON_HARD
```

---

### Comportamiento implementado

El reporte:

```text
- mantiene el diagnostico como fuente
- no recalcula reglas
- no llama al engine tradicional
- no llama a validator.py
- no decide swaps
- no modifica estados de SwapRequest
- no persiste cambios
```

Tambien permite limitar detalles visibles mediante:

```text
limite_detalles
```

Si `limite_detalles` es menor o igual a cero, falla de forma controlada.

---

### Tests agregados

Se agregaron tests para validar:

```text
reporte sin hard
reporte con hard
ordenamiento de codigos por cantidad y codigo
limite de detalles
error controlado con limite_detalles invalido
serializacion to_dict
reporte desde resultado de importacion usando entrypoint
```

---

### Validaciones ejecutadas

Se ejecuto test focalizado:

```text
uv run pytest tests/test_roster_calendar_aware_report.py -q
```

Resultado:

```text
7 passed
```

Se ejecutaron tests relacionados:

```text
uv run pytest tests/test_roster_calendar_aware_entrypoint.py tests/test_smoke_entrypoint_calendar_aware_csv_real.py -q
```

Resultado:

```text
5 passed
```

Se ejecuto suite completa:

```text
uv run pytest -q
```

Resultado:

```text
447 passed
```

Nota operativa:

```text
En el shell de Codex se uso uv con PYTHONPATH=.
En VS Code del usuario, el comando equivalente habitual es py -m pytest -q.
```

---

### Restricciones respetadas

No se modifico:

* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* reglas tecnicas actuales
* CSV real local

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v105 deja disponible una salida operativa simple para el diagnostico calendar-aware.

La cadena queda:

```text
ResultadoDiagnosticoCalendarAware
-> generar_reporte_operativo_calendar_aware
-> ReporteOperativoCalendarAware
```

Y tambien:

```text
resultado_importacion
-> generar_reporte_operativo_importacion_calendar_aware
-> ReporteOperativoCalendarAware
```

El reporte es presentable y serializable, pero sigue siendo diagnostico.

No decide swaps ni altera el comportamiento formal del sistema.

---

### Proximo paso sugerido

El proximo paso natural seria validar el reporte operativo calendar-aware sobre el CSV real local:

```text
v106 - smoke reporte operativo calendar-aware sobre CSV real
```

Objetivo sugerido:

```text
- importar data/imports/csv_ok.csv
- generar ReporteOperativoCalendarAware
- confirmar estado_general VALIDO_SIN_HARD
- confirmar 0 hard y 1 soft
- confirmar EXCESO_LIBRES_CONSECUTIVOS
- no tocar engine.py
- no tocar validator.py
- no cambiar workflow formal
```

---

## checkpoint-v106-smoke-reporte-operativo-calendar-aware-csv-real

Fecha: 2026-06-26

---

### Estado general

Se agrego un smoke sobre el CSV real local usando el reporte operativo calendar-aware incorporado en v105.

El objetivo fue validar que `ReporteOperativoCalendarAware` funcione correctamente sobre el roster real acotado `data/imports/csv_ok.csv`.

Esta version no agrega logica de negocio nueva.

Esta version no modifica el motor general ni el workflow formal.

---

### Problema abordado

Hasta v105 ya existia una capa de reporte:

```text
ResultadoDiagnosticoCalendarAware
-> generar_reporte_operativo_calendar_aware
-> ReporteOperativoCalendarAware
```

Pero faltaba confirmar ese reporte sobre el CSV real local.

v106 agrega ese smoke controlado.

---

### Alcance implementado

Se agrego un test smoke local que:

```text
- verifica si existe data/imports/csv_ok.csv
- si no existe, omite el test con pytest.skip
- importa el CSV real con anio=2026 y mes=6
- llama generar_reporte_operativo_importacion_calendar_aware
- valida el reporte operativo calendar-aware esperado
- valida la serializacion basica con to_dict
```

El CSV real no se sube al repositorio.

El directorio `data/imports/` sigue ignorado por Git.

---

### Archivos agregados

Se agrego:

```text
tests/test_smoke_reporte_operativo_calendar_aware_csv_real.py
```

---

### Archivos modificados

Se modifico:

```text
checkpoints.md
```

---

### Cadena validada

La cadena validada por el smoke queda:

```text
data/imports/csv_ok.csv
-> importar_roster_desde_csv(anio=2026, mes=6, strict=True)
-> generar_reporte_operativo_importacion_calendar_aware
-> ReporteOperativoCalendarAware
```

---

### Resultado esperado del reporte

El smoke confirma:

```text
mensaje = Reporte operativo calendar-aware
estado_general = VALIDO_SIN_HARD
total_dias_importados = 450
total_violaciones = 1
total_hard = 0
total_soft = 1
valido_sin_hard = True
```

Codigo principal:

```text
EXCESO_LIBRES_CONSECUTIVOS = 1
```

Detalle validado:

```text
codigo = EXCESO_LIBRES_CONSECUTIVOS
severidad = SOFT
cantidad_dias = 6
```

---

### Interpretacion

El smoke confirma que el reporte operativo calendar-aware puede presentar el diagnostico del CSV real local sin pasar por el engine tradicional.

El resultado sigue siendo consistente con los checkpoints previos:

```text
0 hard
1 soft
```

La unica observacion vigente sobre timeline corresponde a:

```text
EXCESO_LIBRES_CONSECUTIVOS
```

---

### Validaciones ejecutadas

Se ejecuto test smoke focalizado:

```text
uv run pytest tests/test_smoke_reporte_operativo_calendar_aware_csv_real.py -q
```

Resultado:

```text
1 passed
```

Se ejecutaron tests relacionados:

```text
uv run pytest tests/test_roster_calendar_aware_report.py tests/test_roster_calendar_aware_entrypoint.py tests/test_smoke_entrypoint_calendar_aware_csv_real.py -q
```

Resultado:

```text
12 passed
```

Se ejecuto suite completa:

```text
uv run pytest -q
```

Resultado:

```text
448 passed
```

Nota operativa:

```text
En el shell de Codex se uso uv con PYTHONPATH=.
En VS Code del usuario, el comando equivalente habitual es py -m pytest -q.
```

---

### Restricciones respetadas

No se modifico:

* `src/`
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* reglas tecnicas actuales
* CSV real local

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

No se subio el CSV real al repositorio.

---

### Estado final

v106 deja validado el reporte operativo calendar-aware sobre el CSV real local.

La cadena consolidada queda:

```text
CSV real local
-> importador
-> generar_reporte_operativo_importacion_calendar_aware
-> ReporteOperativoCalendarAware
-> VALIDO_SIN_HARD
-> 0 hard
-> 1 soft
```

El reporte sigue siendo diagnostico.

No decide swaps ni altera el comportamiento formal del sistema.

---

### Proximo paso sugerido

El proximo paso natural seria pausar la implementacion y preparar un plan controlado para carga de rosters mensuales:

```text
v107 - diagnostico de carga multi-mes junio julio agosto
```

Objetivo sugerido:

```text
- revisar formato de las listas de junio, julio y agosto
- validar si corresponden a CSV/matriz ya soportada
- diagnosticar importacion sin persistir en base de datos
- generar reporte calendar-aware por mes
- no modificar la base de datos todavia
- no tocar engine.py
- no tocar validator.py
- no cambiar workflow formal
```

La carga real a base de datos deberia hacerse en un paso posterior y explicito, solo despues de validar importacion y diagnostico por mes.

---

## checkpoint-v107-diagnostico-carga-multimes-junio-julio-agosto

Fecha: 2026-07-23

---

### Estado general

Se agrego una capa de diagnostico multi-mes calendar-aware para preparar la carga controlada de rosters mensuales.

El objetivo fue poder analizar listas de junio, julio y agosto en memoria, sin persistir datos y sin modificar el workflow formal.

Esta version no carga datos en la base.

Esta version no crea `RosterVersion`.

Esta version no modifica el motor general.

---

### Problema abordado

El proyecto ya cuenta con:

```text
importador de roster real
dias_importados
entrypoint calendar-aware
reporte operativo calendar-aware
smokes sobre CSV real local
```

Pero antes de alimentar una base de datos con listas mensuales reales, hace falta un paso intermedio seguro:

```text
diagnosticar varios meses
comparar resultados
detectar faltantes
detectar errores de importacion
detectar hard calendar-aware
confirmar aptitud para revision de carga
```

v107 agrega ese paso sin persistencia.

---

### Alcance implementado

Se agrego un modulo nuevo:

```text
src/roster_calendar_aware_multimonth.py
```

El modulo permite:

```text
- recibir una lista de entradas mensuales
- importar cada CSV en memoria
- generar reporte operativo calendar-aware por mes
- resumir errores de importacion
- resumir hard y soft calendar-aware
- omitir archivos faltantes de forma controlada
- fallar si un archivo faltante es requerido
- indicar aptitud para revision de carga
```

---

### Archivos agregados

Se agregaron:

```text
src/roster_calendar_aware_multimonth.py
tests/test_roster_calendar_aware_multimonth.py
```

---

### Archivos modificados

Se modifico:

```text
checkpoints.md
```

---

### Clases agregadas

En `src/roster_calendar_aware_multimonth.py` se agregaron:

```text
EntradaCargaRosterMes
DiagnosticoCargaRosterMes
DiagnosticoCargaMultiMesCalendarAware
```

---

### Funcion agregada

En `src/roster_calendar_aware_multimonth.py` se agrego:

```text
diagnosticar_carga_multimes_calendar_aware
```

---

### Contrato conceptual

Cada entrada mensual se define con:

```text
anio
mes
csv_path
```

El diagnostico por mes expone:

```text
anio
mes
fuente
disponible
omitido_motivo
total_controladores
total_dias_importados
total_asignaciones_operativas
total_eventos_no_operativos
total_warnings_importacion
total_errors_importacion
puede_crear_roster_version
estado_general_calendar_aware
total_violaciones_calendar_aware
total_hard_calendar_aware
total_soft_calendar_aware
por_codigo_calendar_aware
por_severidad_calendar_aware
reporte
apto_para_revision_carga
```

El diagnostico multi-mes expone:

```text
total_meses
meses_disponibles
meses_omitidos
meses_con_errors_importacion
meses_con_hard_calendar_aware
total_hard_calendar_aware
total_soft_calendar_aware
apto_para_revision_carga
meses
```

---

### Regla de aptitud para revision de carga

Un mes queda apto para revision de carga si:

```text
esta disponible
no tiene errores de importacion
no tiene hard calendar-aware
```

El diagnostico multi-mes queda apto para revision de carga si:

```text
hay al menos un mes
no hay meses omitidos
no hay meses con errores de importacion
no hay meses con hard calendar-aware
```

Esta aptitud no implica carga automatica.

Solo habilita una revision posterior.

---

### Comportamiento ante archivos faltantes

Por defecto, si un CSV no existe:

```text
disponible = False
omitido_motivo = CSV_NO_DISPONIBLE
```

Si `omitir_faltantes=False`, el diagnostico falla con:

```text
FileNotFoundError
```

---

### Tests agregados

Se agregaron tests para validar:

```text
diagnostico multi-mes con meses disponibles
omision controlada de archivos faltantes
fallo si un faltante es requerido
deteccion de errores de importacion
deteccion de hard calendar-aware
no persistencia de RosterVersion
serializacion to_dict
```

---

### Validaciones ejecutadas

Se ejecuto test focalizado:

```text
uv run pytest tests/test_roster_calendar_aware_multimonth.py -q
```

Resultado:

```text
7 passed
```

Se ejecutaron tests relacionados:

```text
uv run pytest tests/test_roster_calendar_aware_report.py tests/test_roster_calendar_aware_entrypoint.py tests/test_smoke_reporte_operativo_calendar_aware_csv_real.py -q
```

Resultado:

```text
12 passed
```

Se ejecuto suite completa:

```text
uv run pytest -q
```

Resultado:

```text
455 passed
```

Nota operativa:

```text
En el shell de Codex se uso uv con PYTHONPATH=.
En VS Code del usuario, el comando equivalente habitual es py -m pytest -q.
```

---

### Restricciones respetadas

No se modifico:

* base de datos
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* reglas tecnicas actuales
* CSV real local

No se creo `RosterVersion`.

No se persistieron rosters.

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v107 deja disponible un diagnostico multi-mes para preparar una eventual carga controlada de junio, julio y agosto.

La cadena queda:

```text
EntradaCargaRosterMes[]
-> diagnosticar_carga_multimes_calendar_aware
-> importacion en memoria por mes
-> reporte calendar-aware por mes
-> DiagnosticoCargaMultiMesCalendarAware
```

El resultado es diagnostico.

No carga datos en base.

No decide swaps.

No altera el comportamiento formal del sistema.

---

### Proximo paso sugerido

El proximo paso natural seria usar esta capa con los archivos reales de junio, julio y agosto:

```text
v108 - smoke diagnostico multi-mes con archivos reales locales
```

Objetivo sugerido:

```text
- ubicar los archivos reales de junio, julio y agosto
- construir entradas mensuales
- ejecutar diagnosticar_carga_multimes_calendar_aware
- revisar resultados por mes
- no persistir en base de datos
- no crear RosterVersion
- no tocar engine.py
- no tocar validator.py
```

La carga real a base de datos debe seguir postergada hasta revisar el reporte multi-mes real.

---

## checkpoint-v108-normalizacion-codigos-fc-in-c

Fecha: 2026-07-23

---

### Estado general

Se agrego normalizacion explicita para codigos reales detectados en los rosters finales de junio, julio y agosto.

El objetivo fue resolver los ultimos codigos desconocidos antes de cualquier carga a base de datos.

Esta version no carga datos en la base.

Esta version no crea `RosterVersion`.

Esta version no modifica el motor general ni el workflow formal.

---

### Problema abordado

Durante el diagnostico de integridad de los CSV reales corregidos se detectaron dos codigos especiales:

```text
FC
IN/C
```

Interpretacion operativa confirmada:

```text
FC = fecha cumpleanos
FC se toma como dia libre

IN/C = ingles virtual + turno noche C
Para el roster operativo importa la C
```

Antes de v108, esos codigos podian quedar como desconocidos.

---

### Alcance implementado

Se agregaron normalizaciones al catalogo y al importador:

```text
FC -> celda libre
IN/C -> C
```

La normalizacion de `FC` conserva el valor original como `raw_value`, pero registra el dia como:

```text
LIBRE
```

La normalizacion de `IN/C` conserva el valor original como `raw_value`, pero registra el dia como:

```text
OPERATIVO
codigo_normalizado = C
```

---

### Archivos modificados

Se modificaron:

```text
src/roster_import_service.py
src/roster_code_catalog.py
tests/test_roster_import_service.py
tests/test_roster_code_catalog.py
checkpoints.md
```

---

### Comportamiento agregado

Para `FC`:

```text
- no genera asignacion operativa
- no genera evento no operativo
- no genera error
- registra dia importado como LIBRE
- genera warning CODIGO_NORMALIZADO
```

Para `IN/C`:

```text
- genera asignacion operativa C
- entra al motor tecnico como C
- participa de validacion calendar-aware como noche C
- no genera evento no operativo
- no genera error
- genera warning CODIGO_NORMALIZADO
```

---

### Catalogo actualizado

Se agregaron definiciones documentales para:

```text
FC
IN/C
```

`FC` queda como codigo local normalizable a libre.

`IN/C` queda como codigo local compuesto normalizable a `C`.

El catalogo y la configuracion del importador quedan alineados.

---

### Tests agregados

Se agregaron tests para validar:

```text
FC se normaliza a libre
FC no genera asignacion ni evento
IN/C se normaliza a C
IN/C genera asignacion operativa C
catalogo contiene FC e IN/C
catalogo e importador quedan alineados
```

---

### Diagnostico sobre archivos reales corregidos

Se ejecuto diagnostico en memoria sobre:

```text
C:\Users\nanoi\Documents\ACC CBA\junio.csv
C:\Users\nanoi\Documents\ACC CBA\julio.csv
C:\Users\nanoi\Documents\ACC CBA\agosto.csv
```

Los archivos actuales ya estan:

```text
sin DNI
sin columna FUNCION
con separador coma
```

Resultado:

```text
junio:
controladores = 74
dias_importados = 2220
asignaciones_operativas = 909
eventos_no_operativos = 334
errors_importacion = 0
hard_calendar_aware = 0
soft_calendar_aware = 1

julio:
controladores = 74
dias_importados = 2294
asignaciones_operativas = 910
eventos_no_operativos = 442
errors_importacion = 0
hard_calendar_aware = 0
soft_calendar_aware = 11

agosto:
controladores = 73
dias_importados = 2263
asignaciones_operativas = 930
eventos_no_operativos = 339
errors_importacion = 0
hard_calendar_aware = 0
soft_calendar_aware = 5
```

---

### Validaciones ejecutadas

Se ejecuto test focalizado de catalogo e importador:

```text
uv run pytest tests/test_roster_code_catalog.py tests/test_roster_import_service.py -q
```

Resultado:

```text
46 passed
```

Se ejecuto suite completa:

```text
uv run pytest -q
```

Resultado:

```text
457 passed
```

Nota operativa:

```text
En el shell de Codex se uso uv con PYTHONPATH=.
En VS Code del usuario, el comando equivalente habitual es py -m pytest -q.
```

---

### Restricciones respetadas

No se modifico:

* base de datos
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* CSV reales locales

No se creo `RosterVersion`.

No se persistieron rosters.

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v108 deja resueltos los codigos reales `FC` e `IN/C`.

Los tres CSV finales quedan diagnosticados con:

```text
0 errores de importacion
0 hard calendar-aware
```

La carga a base de datos sigue postergada hasta decision explicita posterior.

---

### Proximo paso sugerido

El proximo paso natural seria convertir este diagnostico manual en un smoke reproducible usando la capa multi-mes:

```text
v109 - smoke multi-mes con archivos reales finales
```

Objetivo sugerido:

```text
- usar los tres CSV reales finales
- ejecutar diagnosticar_carga_multimes_calendar_aware
- validar 0 errores de importacion
- validar 0 hard calendar-aware
- registrar soft por mes
- no persistir en base de datos
- no crear RosterVersion
```

---
## checkpoint-v109-smoke-multimes-acc-cba-reales-finales

Fecha: 2026-07-23

---

### Estado general

Se agrego un smoke reproducible para diagnosticar los tres CSV reales finales de ACC CBA.

El objetivo fue validar en conjunto junio, julio y agosto usando la capa multi-mes calendar-aware agregada en v107 y las normalizaciones reales agregadas en v108.

Esta version no carga datos en base.

Esta version no crea `RosterVersion`.

Esta version no modifica el motor general ni el workflow formal.

---

### Problema abordado

Hasta v108 ya estaban resueltos:

```text
FC -> libre
IN/C -> C
```

Tambien se habia confirmado manualmente que los tres CSV finales estaban:

```text
sin DNI
sin columna FUNCION
con separador coma
```

Faltaba convertir ese diagnostico manual en un smoke reproducible.

---

### Alcance implementado

Se agrego soporte explicito para formato:

```text
CSV_ACC_CBA
```

Ese formato permite leer archivos reales con estructura:

```text
APELLIDO NOMBRE,1,2,3,...
CONTROLADOR,A,B,,LA,...
```

Tambien soporta el caso de junio con fila inicial de titulo y dias en la segunda fila:

```text
APELLIDO NOMBRE,,,,...
,1,2,3,...
CONTROLADOR,A,B,,LA,...
```

---

### Archivos agregados

Se agrego:

```text
tests/test_smoke_multimes_acc_cba_reales.py
```

---

### Archivos modificados

Se modificaron:

```text
src/roster_calendar_aware_multimonth.py
tests/test_roster_calendar_aware_multimonth.py
checkpoints.md
```

---

### Constantes agregadas

En `src/roster_calendar_aware_multimonth.py` se agregaron:

```text
FORMATO_CSV_SIMPLE
FORMATO_CSV_ACC_CBA
```

---

### Comportamiento agregado

`EntradaCargaRosterMes` ahora permite indicar:

```text
formato
```

Por defecto:

```text
CSV_SIMPLE
```

Para los archivos finales ACC CBA:

```text
CSV_ACC_CBA
```

El formato `CSV_ACC_CBA`:

```text
- detecta separador coma o punto y coma
- soporta codificacion utf-8-sig, cp1252 o latin-1
- detecta la fila de dias
- toma la columna anterior al primer dia como controlador
- transforma internamente la matriz al contrato del importador base
```

---

### Smoke real agregado

Se agrego un smoke local sobre:

```text
C:\Users\nanoi\Documents\ACC CBA\junio.csv
C:\Users\nanoi\Documents\ACC CBA\julio.csv
C:\Users\nanoi\Documents\ACC CBA\agosto.csv
```

Si los archivos no existen en otra maquina, el test se omite con `pytest.skip`.

---

### Resultado esperado del smoke real

El smoke valida:

```text
total_meses = 3
meses_disponibles = 3
meses_omitidos = 0
meses_con_errors_importacion = 0
meses_con_hard_calendar_aware = 0
total_hard_calendar_aware = 0
total_soft_calendar_aware = 17
apto_para_revision_carga = True
```

Detalle por mes:

```text
junio:
controladores = 74
dias_importados = 2220
asignaciones_operativas = 909
eventos_no_operativos = 334
errors_importacion = 0
hard_calendar_aware = 0
soft_calendar_aware = 1

julio:
controladores = 74
dias_importados = 2294
asignaciones_operativas = 910
eventos_no_operativos = 442
errors_importacion = 0
hard_calendar_aware = 0
soft_calendar_aware = 11

agosto:
controladores = 73
dias_importados = 2263
asignaciones_operativas = 930
eventos_no_operativos = 339
errors_importacion = 0
hard_calendar_aware = 0
soft_calendar_aware = 5
```

---

### Tests agregados

Se agregaron tests para validar:

```text
CSV_ACC_CBA directo con APELLIDO NOMBRE y dias
CSV_ACC_CBA con fila de titulo y dias en segunda fila
rechazo de formato no soportado
smoke real con junio, julio y agosto finales
```

---

### Validaciones ejecutadas

Se ejecutaron tests focalizados:

```text
uv run pytest tests/test_roster_calendar_aware_multimonth.py tests/test_smoke_multimes_acc_cba_reales.py -q
```

Resultado:

```text
11 passed
```

Se ejecuto suite completa:

```text
uv run pytest -q
```

Resultado:

```text
461 passed
```

Nota operativa:

```text
En el shell de Codex se uso uv con PYTHONPATH=.
En VS Code del usuario, el comando equivalente habitual es py -m pytest -q.
```

---

### Restricciones respetadas

No se modifico:

* base de datos
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* CSV reales locales

No se creo `RosterVersion`.

No se persistieron rosters.

No se conecto la timeline al engine general.

No se reemplazo el validador tradicional.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v109 deja validado el diagnostico multi-mes con los archivos reales finales.

La cadena consolidada queda:

```text
CSV reales ACC CBA
-> FORMATO_CSV_ACC_CBA
-> diagnosticar_carga_multimes_calendar_aware
-> 0 errores de importacion
-> 0 hard calendar-aware
-> apto_para_revision_carga = True
```

El resultado sigue siendo diagnostico.

No carga datos en base.

No decide swaps.

No altera el comportamiento formal del sistema.

---

### Proximo paso sugerido

El proximo paso natural seria hacer una prueba controlada de cambio de turno en modo simulacion:

```text
v110 - prueba simulada de cambio de turno sobre roster importado
```

Objetivo sugerido:

```text
- elegir un mes y dos asignaciones concretas
- importar el roster en memoria
- crear RosterVersion solo en memoria o store controlado de test
- simular cambio de turno
- evaluar resultado tecnico
- no aplicar cambio real
- no tocar DB productiva
```

La aplicacion real de un cambio debe seguir siendo un paso posterior y explicito.

---

## checkpoint-v110-smoke-swap-simulado-acc-cba-real

Fecha: 2026-07-23

---

### Estado general

Se agrego una primera prueba controlada de cambio de turno sobre un roster real ACC CBA importado.

El objetivo fue validar que el sistema puede importar un CSV real final y ejecutar una simulacion tecnica de swap sin aplicar cambios reales.

Esta version no carga datos en base.

Esta version no crea `SwapRequest`.

Esta version no crea `RosterVersion`.

Esta version no aplica cambios de roster.

---

### Problema abordado

Hasta v109 ya estaba validado el diagnostico multi-mes sobre los CSV reales finales de junio, julio y agosto.

Faltaba confirmar un paso operativo siguiente, pero en modo seguro:

```text
CSV real final
-> importacion ACC CBA
-> asignaciones_operativas
-> simulacion tecnica de swap
-> roster simulado
-> roster original intacto
```

v110 agrega esa prueba sin activar el workflow formal ni persistir cambios.

---

### Alcance implementado

Se expuso una funcion publica para importar un CSV ACC CBA real:

```text
importar_roster_acc_cba_desde_csv
```

La funcion reutiliza el adaptador ACC CBA agregado en v109 y devuelve un `RosterImportResult`.

Tambien se agrego un smoke sobre el CSV real local de junio:

```text
C:\Users\nanoi\Documents\ACC CBA\junio.csv
```

El smoke:

```text
- importa junio 2026 con strict=True
- obtiene asignaciones_operativas
- busca un par de asignaciones de distintos controladores y distinto turno
- ejecuta evaluar_swap
- verifica que existe roster simulado
- verifica que el roster original no se modifica
- verifica que no aparece decision_sugerida
```

---

### Archivos agregados

Se agrego:

```text
tests/test_smoke_swap_simulado_acc_cba_real.py
```

---

### Archivos modificados

Se modificaron:

```text
src/roster_calendar_aware_multimonth.py
tests/test_roster_calendar_aware_multimonth.py
checkpoints.md
```

---

### Funcion publica agregada

En `src/roster_calendar_aware_multimonth.py` se agrego:

```text
importar_roster_acc_cba_desde_csv
```

Contrato basico:

```text
csv_path
anio
mes
strict=True
```

Resultado:

```text
RosterImportResult
```

Esta funcion no diagnostica multiples meses.

Esta funcion solo importa un CSV ACC CBA real y devuelve el resultado de importacion.

---

### Smoke de simulacion agregado

Se agrego un smoke que ejecuta:

```text
resultado_importacion = importar_roster_acc_cba_desde_csv(junio.csv, anio=2026, mes=6)
asignaciones = resultado_importacion.asignaciones_operativas
evaluacion = evaluar_swap(asignaciones, idx_a, idx_b)
```

El par `idx_a`, `idx_b` se elige de forma deterministica buscando:

```text
controladores distintos
turnos distintos
```

Esto garantiza que el intercambio simulado represente un cambio real de turno.

---

### Resultado validado

El smoke confirma:

```text
errors_importacion = 0
asignaciones_operativas = 909
```

Tambien confirma que la evaluacion tecnica devuelve una clasificacion conocida:

```text
BENEFICIOSO
ACEPTABLE
RECHAZABLE
```

Y que la salida no contiene:

```text
decision_sugerida
```

Esto mantiene la separacion entre:

```text
simulacion tecnica
decision operativa formal
```

---

### Garantia de no aplicacion

El smoke verifica que:

```text
roster_simulado is not asignaciones
```

Y que las asignaciones originales usadas para el intercambio quedan iguales despues de la evaluacion:

```text
asignaciones[idx_a] == asignacion_a_original
asignaciones[idx_b] == asignacion_b_original
```

Esto confirma que v110 simula el cambio pero no altera el roster importado original.

---

### Tests agregados

Se agregaron tests para validar:

```text
importar_roster_acc_cba_desde_csv con CSV ACC CBA chico
smoke de swap simulado sobre junio real ACC CBA
```

---

### Validaciones ejecutadas

Se ejecutaron tests relacionados:

```text
uv run pytest tests/test_roster_calendar_aware_multimonth.py tests/test_smoke_multimes_acc_cba_reales.py tests/test_smoke_swap_simulado_acc_cba_real.py -q
```

Resultado:

```text
13 passed
```

Se ejecuto suite completa:

```text
uv run pytest -q
```

Resultado:

```text
463 passed
```

---

### Restricciones respetadas

No se modifico:

* base de datos
* CSV reales locales
* `engine.py`
* `validator.py`
* `scoring.py`
* `simulator.py`
* `swap_service.py`
* workflow formal
* request_store
* roster_store

No se creo `SwapRequest`.

No se creo `RosterVersion`.

No se persistio request.

No se aplico cambio de turno real.

No se incorporo UI.

No se incorporo API.

---

### Estado final

v110 confirma que el sistema ya puede ejecutar una prueba tecnica de cambio de turno sobre un roster real importado.

La cadena validada queda:

```text
junio.csv real final
-> importar_roster_acc_cba_desde_csv
-> asignaciones_operativas
-> evaluar_swap
-> roster simulado
-> roster original intacto
```

El resultado sigue siendo simulacion tecnica.

No equivale a aprobacion.

No equivale a aplicacion.

No modifica datos reales.

---

### Proximo paso sugerido

El proximo paso natural seria una prueba controlada con un cambio elegido por el usuario:

```text
v111 - simulacion de cambio de turno seleccionado
```

Objetivo sugerido:

```text
- elegir mes
- elegir controlador A, fecha A y turno A
- elegir controlador B, fecha B y turno B
- importar roster real en memoria
- ejecutar evaluar_swap
- entregar reporte breve de resultado
- no crear SwapRequest
- no aplicar cambios
- no tocar DB
```

La aplicacion formal debe seguir postergada hasta una decision explicita.

---

## checkpoint-v111-auditoria-documental-integral-v110

Fecha: 2026-07-24

---

### Estado general

Se completo una auditoria documental integral contra el repositorio real en v110.

El objetivo fue identificar inconsistencias, duplicaciones, documentos desactualizados y fallas del proceso de mantenimiento documental antes de retomar implementacion funcional.

Esta version registra diagnostico y estrategia.

No corrige todavia los documentos auditados.

No modifica comportamiento productivo.

---

### Base auditada

```text
commit: e3458710680c4badcde11ee734e8bb5dce090591
tag: checkpoint-v110-smoke-swap-simulado-acc-cba-real
rama: main
suite confirmada: 463 passed
```

La auditoria se realizo contra un `git archive` exacto de v110.

---

### Archivo agregado

Se agrego:

```text
docs/hitos/auditoria_documental_v110.md
```

El documento contiene:

```text
- alcance auditado
- estado real confirmado
- inconsistencias entre checkpoints y commits
- evaluacion de cada documento
- cobertura faltante de v105-v110
- diagnostico de semantic_guard
- clasificacion documental aprobada
- arquitectura documental objetivo
- estrategia para checkpoints historicos
- estrategia de validacion futura
- plan controlado v112-v119
```

---

### Hallazgos principales registrados

Se confirmo:

```text
- README.md vacio
- contexto_sistema.md gravemente desactualizado
- contexto_resumen.md detenido en v103 y 440 tests
- estado_docs.md detenido en v104
- contratos_resumen.md redundante y con terminos legados
- indices incompletos en decisiones, contratos e invariantes
- estructura inconsistente en modelo_dominio.md
- estructura acumulativa en diccionario.md
- semantic_guard.md con formato defectuoso
- falta de documentacion canonica para v105-v110
```

Tambien se confirmo en `checkpoints.md`:

```text
- checkpoint v33 duplicado
- checkpoint v46 ubicado despues de v110
- ausencia de bloques propios identificables para v42, v83 y v84
```

Los huecos historicos no se reconstruyen sin evidencia.

---

### Divergencias confirmadas entre checkpoints y commits

#### v102

El checkpoint v102 declaro modificaciones en `docs/decisiones.md` y `docs/contratos.md`.

El commit real `61ca950` no modifico esos archivos.

Por lo tanto, no quedaron incorporados:

```text
Decision 53 - Timeline diaria y diagnostico calendar-aware paralelo
Contrato 25 - EntryPoint paralelo calendar-aware
```

Las numeraciones existentes se preservan:

```text
Decision 53 - Perfil operativo de persona
Contrato 25 - Estado operativo general y habilitaciones
```

#### v103

El checkpoint v103 declaro una actualizacion completa de:

```text
docs/contexto_sistema.md
```

El commit real `5b4c682` modifico solamente:

```text
checkpoints.md
```

La actualizacion declarada no ingreso al repositorio.

---

### Diagnostico de semantic_guard

Se confirmo que `run_semantic_lint()` tiene un problema de indentacion que impide considerar su resultado actual como prueba suficiente de integridad documental.

Tambien se detecto:

```text
- autodeteccion de terminos prohibidos en la propia lista de reglas
- regla valido/valido demasiado amplia
- recorrido documental incompleto
```

La reparacion queda fuera de v111.

---

### Decisiones documentales aprobadas

Se aprobaron estas decisiones:

```text
1. retirar docs/contratos_resumen.md como documento vigente
2. usar Git para conservar la historia integra de checkpoints antiguos
3. mantener posteriormente checkpoints.md activo desde v96
4. crear docs/estado_actual.md como unica fuente del estado vigente
```

La ejecucion material de estas decisiones queda para checkpoints posteriores.

---

### Estrategia documental aprobada

Se distinguen:

```text
documentos canonicos manuales
estado vigente unico
documentos derivados
documentos historicos
registro documental estructurado
```

Se planifica incorporar:

```text
docs/estado_actual.md
docs/mapa_documental.yml
```

Los documentos derivados deberan generarse o verificarse sistematicamente.

---

### Plan controlado

```text
v112 - saneamiento de checkpoints e indice historico
v113 - clasificacion y estructura documental oficial
v114 - reparacion de documentos canonicos
v115 - actualizacion funcional documental v105-v110
v116 - correccion y ampliacion de semantic_guard
v117 - generacion sistematica de documentos derivados
v118 - cierre integral de documentacion
v119 - simulacion de cambio de turno seleccionado
```

Los alcances posteriores pueden ajustarse mediante diagnostico controlado.

No deben ampliarse silenciosamente dentro de un checkpoint iniciado.

---

### Validaciones ejecutadas

Suite completa:

```text
py -m pytest -q
463 passed in 6.71s
```

Semantic lint actual:

```text
py -m src.semantic_guard.lint_runner
OK: semantic lint sin violaciones
```

El resultado del semantic lint se registra como salida ejecutada, pero no como prueba documental suficiente debido a las limitaciones diagnosticadas.

Validacion de formato del documento nuevo:

```text
git diff --cached --check
sin observaciones
```

---

### Restricciones respetadas

No se modifico:

```text
src/
tests/
tools/
config/
requirements.txt
.gitignore
documentos canonicos existentes
base de datos
CSV reales
comportamiento productivo
```

No se:

```text
- corrigio semantic_guard
- retiro contratos_resumen.md
- movieron checkpoints historicos
- inventaron contenidos para v42, v83 o v84
- incorporaron nuevas decisiones o contratos
- actualizaron documentos derivados
```

El bloque v111 se agrega al final sin reordenar todavia el bloque v46 desplazado.

Ese saneamiento pertenece a v112.

---

### Estado final

v111 deja persistida una auditoria verificable contra el repositorio real en v110.

La documentacion todavia no fue saneada.

Queda establecido un plan controlado para construir una base documental:

```text
actual
no redundante
trazable
verificable
mantenible
```

---

### Proximo paso sugerido

```text
v112 - saneamiento de checkpoints e indice historico
```

Objetivo:

```text
- preservar historia integra mediante Git
- dejar checkpoints.md activo desde v96
- crear indice historico conciso para v1-v95
- registrar duplicaciones, huecos y bloque fuera de orden
- no modificar src/
- no cambiar comportamiento productivo
```

---
## checkpoint-v112-saneamiento-checkpoints-indice-historico

Fecha: 2026-09-10

### Objetivo

Reducir el registro activo sin perder trazabilidad historica.

### Cambios

- Se conserva el detalle de v96-v111.
- Se normaliza exclusivamente el encabezado de v97.
- Se agrega docs/hitos/indice_checkpoints_v1_v95.md.
- El indice contiene 95 entradas y registra las anomalias.
- Este bloque incorpora v112 al registro activo.

### Preservacion historica

El original completo queda preservado en:
checkpoint-v111-auditoria-documental-integral-v110.

Se verifico coincidencia del archivo original con el objeto Git:
f90375ee4720eb687b280680880fad20844251b0.

La preparacion verifico conservacion textual de los 16 bloques
v96-v111, salvo el encabezado de v97.

### Anomalias registradas

- v33: dos bloques textualmente identicos.
- v46: bloque fuera de orden; comparte commit con v45.
- v42/v83/v84: sin bloque propio ni evidencia suficiente en las
  busquedas aportadas para reconstruir checkpoints independientes.
- v84: mencionado como antecedente por v85.
- v85: bloque asociado a cd2fc15, sin tag propio identificado.
- Las divergencias v102/v103 permanecen documentadas en v111.

### Validacion y limites

Verificacion local previa a este bloque:
4392 lineas activas, 137 lineas de indice,
16 checkpoints activos y 95 entradas historicas.

git diff --check sin errores de whitespace.
No se reejecuto pytest: cambio exclusivamente documental.
Ultima ejecucion registrada sobre v110: 463 passed.

No se modifica codigo, comportamiento funcional ni datos operativos.
El commit y el tag de v112 quedan pendientes del control final.

### Proximo paso

v113 - clasificacion y estructura documental oficial.

---

## checkpoint-v113-clasificacion-estructura-documental

Fecha: 2026-09-10

### Alcance realizado

- Se incorpora docs/estado_actual.md como referencia del estado vigente.
- Se incorpora docs/mapa_documental.yml con 17 documentos clasificados.
- Se declaran fuentes, dependencias, disparadores y acciones pendientes.
- Se actualiza la nota del indice historico sobre el cotejo confirmado en v112.
- Se distinguen documentos auditados, reparaciones pendientes y trabajo previsto.

### Validacion

- YAML parseado durante la preparacion; 17 rutas unicas.
- Verificacion local del usuario: 17 rutas existentes, 0 faltantes.
- El mapa es declarativo; no implementa validacion automatica.
- No se reejecuto pytest. Ultimo resultado registrado: 463 passed sobre v110.
- Revision final del diff y cierre Git pendientes al redactar este bloque.

### Limites

No se reparan todavia documentos canonicos ni semantic_guard.
No se implementan generadores ni se modifica codigo funcional.
No se alteran datos operativos ni el workflow formal.

### Proximo paso

v114 - reparacion de documentos canonicos.
Definir alcance concreto contra la auditoria antes de editar.

---
