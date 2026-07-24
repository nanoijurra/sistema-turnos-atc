# Auditoria documental integral contra v110

Fecha: 2026-07-24

Estado: auditoria cerrada para planificacion

Base auditada:

```text
commit: e3458710680c4badcde11ee734e8bb5dce090591
tag: checkpoint-v110-smoke-swap-simulado-acc-cba-real
rama: main
suite confirmada por el usuario: 463 passed
```

---

## 1. Objetivo

Auditar la documentacion versionada del sistema de swaps ATC contra el contenido real del repositorio en v110.

La auditoria busca:

- identificar documentos vigentes, historicos, derivados, redundantes u obsoletos;
- detectar contradicciones entre codigo, documentos, checkpoints y commits;
- definir una estructura documental sostenible;
- establecer controles sistematicos para evitar nueva desactualizacion;
- preparar una base documental solida antes de retomar implementacion funcional.

Esta auditoria no modifica comportamiento productivo.

---

## 2. Alcance revisado

Se revisaron:

```text
README.md
checkpoints.md
docs/
src/
tests/
tools/
config/
requirements.txt
.gitignore
```

Tambien se contrastaron los commits:

```text
61ca950 - checkpoint-v102-compatibilizacion-documental-calendar-aware
5b4c682 - checkpoint-v103-actualizacion-contexto-sistema-calendar-aware
```

---

## 3. Estado real confirmado

El repositorio auditado corresponde a v110.

Estado funcional confirmado:

```text
main sincronizado con origin/main
working tree limpio antes de iniciar v111
suite local confirmada: 463 passed
camino tradicional vigente
camino calendar-aware paralelo y diagnostico
sin aplicacion real de swaps sobre los CSV ACC CBA
```

La auditoria no reejecuto la suite porque el entorno de revision no disponia de pytest.

El resultado de 463 tests corresponde a la ejecucion local confirmada por el usuario sobre el repositorio real.

---

## 4. Hallazgos sobre checkpoints

### 4.1 Tamano y estructura

`checkpoints.md` contiene aproximadamente:

```text
19409 lineas
mas de 440 KB
```

El archivo mezcla:

- historia cerrada;
- estado vigente;
- resultados de tests antiguos;
- proximos pasos ya superados;
- decisiones y restricciones de distintos momentos;
- bloques duplicados o fuera de orden.

Esta acumulacion dificulta el uso del archivo como contexto para Codex y Work.

### 4.2 Duplicaciones y desorden

Se confirmo:

```text
checkpoint v33 duplicado
checkpoint v46 ubicado despues de v110
```

### 4.3 Huecos documentales

No se identificaron bloques propios para:

```text
v42
v83
v84
```

La ausencia de un bloque no autoriza a reconstruir o inventar contenido.

Los huecos deben quedar registrados como tales hasta que exista evidencia recuperable en Git.

### 4.4 Divergencia entre checkpoint y commit en v102

El checkpoint v102 declara incorporaciones en:

```text
docs/decisiones.md
docs/contratos.md
docs/invariantes.md
docs/modelo_dominio.md
docs/diccionario.md
```

El commit real `61ca950` modifico solamente:

```text
checkpoints.md
docs/diccionario.md
docs/invariantes.md
docs/modelo_dominio.md
```

No modifico:

```text
docs/decisiones.md
docs/contratos.md
```

Por lo tanto, no quedaron implementados:

```text
Decision 53 - Timeline diaria y diagnostico calendar-aware paralelo
Contrato 25 - EntryPoint paralelo calendar-aware
```

Las numeraciones reales existentes se preservan:

```text
Decision 53 - Perfil operativo de persona
Contrato 25 - Estado operativo general y habilitaciones
```

Si luego de la revision conceptual corresponden nuevas incorporaciones calendar-aware, deberan usar numeros nuevos y no reemplazar los existentes.

### 4.5 Divergencia entre checkpoint y commit en v103

El checkpoint v103 declara la actualizacion completa de:

```text
docs/contexto_sistema.md
```

El commit real `5b4c682` modifico solamente:

```text
checkpoints.md
```

`docs/contexto_sistema.md` no fue modificado.

Por lo tanto, v103 registro como realizado un cambio que no ingreso al commit.

---

## 5. Hallazgos por documento

### 5.1 README.md

Estado:

```text
vacio
```

Debe convertirse en el punto de entrada estable al repositorio.

No debe duplicar el estado operativo completo.

Debe orientar hacia:

- proposito del proyecto;
- forma de ejecutar tests;
- mapa documental;
- estado actual;
- documentos canonicos.

### 5.2 docs/contexto_sistema.md

Estado:

```text
canonico
gravemente desactualizado
estructura Markdown incompleta
```

Todavia afirma:

```text
refactor en curso
tests fallando
estado actual inestable
aproximadamente 50 tests
roster_service futuro
```

Estas afirmaciones no representan v110.

Tambien contiene un bloque Markdown sin cerrar.

### 5.3 docs/contexto_resumen.md

Estado:

```text
derivado
desactualizado
```

Quedo detenido en:

```text
estado posterior a v103
440 passed
```

No contiene la evolucion v105-v110.

No debe seguir dependiendo de actualizacion manual independiente.

### 5.4 docs/estado_docs.md

Estado:

```text
control documental
desactualizado
contiene afirmaciones incorrectas
```

Quedo detenido en v104 y reproduce como realizadas las actualizaciones incompletas de v102 y v103.

Debe simplificarse y convertirse en una salida sistematica derivada de un registro documental.

### 5.5 docs/contratos_resumen.md

Estado:

```text
redundante
obsoleto
semanticamente peligroso
```

Contiene terminos legados:

```text
APROBABLE
ACEPTADOS
```

Duplica parcialmente `docs/contratos.md` y ya demostro que puede quedar desalineado.

Decision aprobada:

```text
retirarlo como documento vigente
```

La ejecucion material de esa decision queda para un checkpoint posterior.

### 5.6 docs/decisiones.md

Estado:

```text
canonico
contenido acumulativo
indice incompleto
```

El indice llega hasta Decision 48, mientras el documento llega hasta Decision 53.

No contiene la decision calendar-aware declarada por v102.

Debe conservarse y normalizarse sin renumerar decisiones existentes.

### 5.7 docs/contratos.md

Estado:

```text
canonico
contenido acumulativo
indice incompleto
```

El indice llega hasta Contrato 20, mientras el documento llega hasta Contrato 25.

No contiene el contrato calendar-aware declarado por v102.

Debe conservarse y normalizarse sin renumerar contratos existentes.

### 5.8 docs/invariantes.md

Estado:

```text
canonico
incluye invariantes calendar-aware
indice incompleto
```

El indice llega hasta Invariante 12, mientras el documento contiene invariantes posteriores y la serie CA-1 a CA-6.

Debe conservarse y normalizarse.

### 5.9 docs/modelo_dominio.md

Estado:

```text
canonico
contenido vigente parcial
estructura inconsistente
```

Se confirmo:

```text
numeracion duplicada de 4.5 Turno
orden alterado entre Controlador y Turno
segundo titulo principal para Timeline diaria importada
indice que no representa toda la estructura
```

Debe conservarse y repararse sin cambiar semantica por efecto lateral.

### 5.10 docs/diccionario.md

Estado:

```text
canonico
incluye terminos calendar-aware hasta v102
estructura acumulativa
```

Utiliza varios titulos principales como si reuniera documentos concatenados.

No incorpora terminos relevantes de v105-v110.

Debe conservarse, normalizarse y actualizarse con terminos efectivamente vigentes.

### 5.11 docs/semantic_guard.md

Estado:

```text
documento tecnico
formato defectuoso
descripcion parcialmente desalineada
```

Comienza con:

```text
clear# Semantic guard
```

Tambien presenta jerarquia Markdown irregular y ejemplos sin bloques correctamente formateados.

Debe corregirse junto con la implementacion real de `semantic_guard`, no de manera aislada.

### 5.12 docs/hitos/cierre_ambiguedad_semantica.md

Estado:

```text
historico
cerrado
util
```

Debe conservarse como evidencia historica.

No representa por si mismo el estado actual del sistema y no requiere actualizacion continua.

---

## 6. Cobertura documental faltante de v105-v110

No se encontraron en la documentacion vigente referencias suficientes a:

```text
ReporteOperativoCalendarAware
generar_reporte_operativo_calendar_aware
DiagnosticoCargaMultiMesCalendarAware
diagnosticar_carga_multimes_calendar_aware
importar_roster_acc_cba_desde_csv
FORMATO_CSV_ACC_CBA
FC
IN/C
```

Actualmente, el detalle de esas incorporaciones depende casi exclusivamente de `checkpoints.md`.

La deuda debe resolverse en un checkpoint documental especifico.

---

## 7. Hallazgos sobre semantic_guard

### 7.1 Recorrido incompleto

La indentacion de `run_semantic_lint()` deja el analisis de archivos fuera del bucle interno.

Como consecuencia, el resultado:

```text
OK: semantic lint sin violaciones
```

no demuestra que todos los archivos hayan sido revisados.

### 7.2 Autodeteccion de terminos prohibidos

Al simular el recorrido completo, el guard detecta los terminos legados contenidos en su propia lista de prohibiciones.

La herramienta necesita diferenciar:

- uso productivo de un termino legado;
- declaracion del termino dentro de una regla de vigilancia.

### 7.3 Regla valido/valido demasiado amplia

La regla actual considera ambiguo cualquier uso de:

```text
valido
válido
```

Un recorrido completo marca documentos canonicos aunque el termino aparezca en un contexto tecnicamente preciso.

La regla debe refinarse antes de convertirse en control obligatorio.

### 7.4 Conclusion

`semantic_guard` es conceptualmente util, pero no puede considerarse hoy una prueba suficiente de integridad documental.

Su reparacion y ampliacion quedan para un checkpoint posterior y controlado.

---

## 8. Otros hallazgos de higiene del repositorio

El repositorio versiona archivos SQLite transitorios:

```text
tests/_manual_test.db
tests/_manual_test.db-journal
tests/_test_swaps_atc.db
tests/_test_swaps_atc.db-journal
```

`.gitignore` ignora bases dentro de `data/`, pero no estos archivos dentro de `tests/`.

Tambien se confirmo:

```text
requirements.txt codificado como UTF-16
```

Estos puntos no forman parte de la correccion documental inmediata.

Deben registrarse como deuda de higiene y resolverse en checkpoints separados, sin mezclarlos silenciosamente con cambios de documentacion.

---

## 9. Clasificacion documental aprobada

| Documento | Tipo | Decision |
| --- | --- | --- |
| `README.md` | entrada estable | completar |
| `checkpoints.md` | historia activa | reducir y rotar |
| `docs/contexto_sistema.md` | canonico | conservar y actualizar |
| `docs/contexto_resumen.md` | derivado | conservar y generar sistematicamente |
| `docs/estado_docs.md` | derivado de control | simplificar y generar |
| `docs/contratos.md` | canonico | conservar y normalizar |
| `docs/contratos_resumen.md` | redundante obsoleto | retirar como vigente |
| `docs/decisiones.md` | canonico | conservar y normalizar |
| `docs/invariantes.md` | canonico | conservar y normalizar |
| `docs/modelo_dominio.md` | canonico | conservar y reparar |
| `docs/diccionario.md` | canonico | conservar y actualizar |
| `docs/semantic_guard.md` | tecnico | conservar y corregir |
| `docs/hitos/*` | historico | conservar sin actualizacion continua |

---

## 10. Arquitectura documental objetivo

### 10.1 Documentos canonicos manuales

```text
docs/contexto_sistema.md
docs/decisiones.md
docs/contratos.md
docs/invariantes.md
docs/modelo_dominio.md
docs/diccionario.md
```

Estos documentos requieren revision humana.

No deben ser reescritos automaticamente en su contenido conceptual.

### 10.2 Fuente unica de estado vigente

Se adopta:

```text
docs/estado_actual.md
```

Como unica fuente para:

- checkpoint vigente;
- arquitectura implementada;
- capacidades confirmadas;
- limites actuales;
- deuda abierta;
- proximo eje aprobado.

No debe contener historia extensa.

### 10.3 Documentos derivados

Se consideran derivados:

```text
docs/contexto_resumen.md
docs/estado_docs.md
indices y tablas de navegacion
```

Deben generarse o verificarse sistematicamente desde fuentes declaradas.

### 10.4 Registro documental

Se planifica crear:

```text
docs/mapa_documental.yml
```

El registro debera declarar para cada documento:

- tipo;
- estado;
- fuente;
- dependencias;
- evento que obliga a revisarlo;
- si es manual o generado;
- ultimo checkpoint de revision.

---

## 11. Estrategia para checkpoints historicos

Decisiones aprobadas:

```text
Git conserva la historia integra anterior
checkpoints.md activo conservara el tramo desde v96
docs/hitos contendra un indice historico conciso de v1-v95
no se duplicara el archivo historico completo dentro de docs
```

La version integra previa al saneamiento queda preservada en:

```text
tag checkpoint-v110-smoke-swap-simulado-acc-cba-real
```

Comando de recuperacion:

```text
git show checkpoint-v110-smoke-swap-simulado-acc-cba-real:checkpoints.md
```

La ejecucion de esta estrategia queda para v112.

---

## 12. Estrategia de validacion futura

La validacion documental debera comprobar:

- un unico titulo principal por documento;
- bloques Markdown correctamente cerrados;
- indices actualizados;
- checkpoints unicos y ordenados;
- referencias a archivos existentes;
- terminos legados fuera de documentos historicos;
- documentos derivados actualizados;
- correspondencia entre archivos declarados en el checkpoint y `git diff`;
- ausencia de cambios reales no declarados en el checkpoint;
- separacion entre documentos vigentes e historicos.

El cierre futuro debera combinar:

```text
suite de tests
semantic_guard corregido
validacion estructural documental
concordancia checkpoint/diff
git status limpio
```

---

## 13. Plan controlado aprobado

```text
v111 - auditoria documental integral contra v110
v112 - saneamiento de checkpoints e indice historico
v113 - clasificacion y estructura documental oficial
v114 - reparacion de documentos canonicos
v115 - actualizacion funcional documental v105-v110
v116 - correccion y ampliacion de semantic_guard
v117 - generacion sistematica de documentos derivados
v118 - cierre integral de documentacion
v119 - simulacion de cambio de turno seleccionado
```

Los nombres y alcances posteriores pueden ajustarse mediante diagnostico controlado.

No deben ampliarse silenciosamente dentro de un checkpoint ya iniciado.

---

## 14. Restricciones de v111

v111 no modifica:

```text
src/
tests/
tools/
config/
requirements.txt
.gitignore
documentos canonicos existentes
comportamiento productivo
base de datos
CSV reales
```

v111 no:

- corrige todavia `semantic_guard`;
- retira todavia `contratos_resumen.md`;
- mueve todavia checkpoints;
- inventa contenido para v42, v83 o v84;
- incorpora todavia Decision 54 ni Contrato 26;
- actualiza todavia documentos derivados.

---

## 15. Resultado de la auditoria

La auditoria confirma que el codigo de v110 dispone de una base funcional y testeada, pero la documentacion no constituye todavia una fuente unica, actual y verificable.

El problema principal no es la falta de documentos.

El problema es:

```text
duplicacion
acumulacion historica
fuentes de verdad no declaradas
actualizacion manual independiente
falta de concordancia automatica entre checkpoint y diff
```

La estrategia aprobada permite sanear el corpus sin alterar la funcionalidad del sistema y establecer una continuidad documental verificable antes de retomar implementacion operativa.
