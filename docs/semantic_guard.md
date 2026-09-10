# Semantic guard

## Tabla de contenido

- [Proposito y limites](#proposito-y-limites)
- [Alcance del lint](#alcance-del-lint)
- [Reglas](#reglas)
- [Excepciones acotadas](#excepciones-acotadas)
- [Uso](#uso)
- [Pruebas](#pruebas)
- [Semantic diff](#semantic-diff)
- [Mantenimiento](#mantenimiento)

---

## Proposito y limites

Revision v116 del lint semantico sobre base v115, commit e39e73f.
Detecta patrones conocidos en codigo y documentacion. No demuestra coherencia
semantica completa, cobertura normativa ATC, correccion de swaps ni vigencia de
cada documento. Tampoco reemplaza pytest, revision humana o control del diff Git.

La reparacion elimina el recorrido incompleto, acota la excepcion de declaraciones
y reemplaza la busqueda indiscriminada de valido por patrones taxonomicos explicitos.
Los codigos S-01 a S-05 y la API que devuelve lista de infracciones se conservan.

## Alcance del lint

- Archivos .py bajo src/, incluidos subdirectorios y semantic_guard.
- Archivos .md bajo docs/, incluidos estado_actual y contexto_resumen.
- Exclusiones Markdown: docs/hitos/**, docs/estado_docs.md y docs/contratos_resumen.md.
  Corresponden a historia cerrada, control derivado y resumen retirado como vigente.
  Los mismos nombres en otras subcarpetas no se excluyen por coincidencia parcial.
- No examina tests/, tools/, config/, YAML, README ni checkpoints de la raiz.
- No sigue directorios simbolicos; los reporta como alcance incompleto (S-00).
  Un archivo enlazado fuera de su directorio src o docs tambien produce S-00.

El recorrido usa os.walk con errores visibles y orden estable. Deben existir src
y docs, con archivos elegibles en ambos. Error de lectura, codificacion o sintaxis
Python no se convierte en exito y no impide analizar los demas archivos.
El reporte distingue archivos analizados de excluidos; un archivo que fallo al
analizar no se cuenta como analizado satisfactoriamente.

## Reglas

| Codigo | Control | Limite |
| --- | --- | --- |
| S-00 | Alcance ausente, vacio, inaccesible o archivo no analizado | Fallo del control, no infraccion de dominio |
| S-01 | Literales de decision/workflow en simulator.py | Heuristica sobre AST, no flujo de datos |
| S-02 | Literales de decision/workflow en engine.py | Heuristica sobre AST, no flujo de datos |
| S-03 | Nombres tecnicos sospechosos en swap_service.py | Patrones de nombres; no prueba de reclasificacion |
| S-04 | Valido/valida como valor de estado, clasificacion o decision | Patrones explicitos en una linea; no comprension general del texto |
| S-05 | Nombres antiguos de eventos en constantes de texto Python | No resuelve cadenas construidas dinamicamente |

S-01/02/03 se seleccionan por nombre exacto del archivo, no porque una carpeta o
archivo auxiliar contenga la palabra engine, simulator o swap_service.

S-04 reconoce etiquetas de estado, clasificacion o decision seguidas de dos puntos,
igual o el verbo es y un valor valido/valida, con o sin tildes y comillas simples.
Informa la linea real. No marca el verbo valida, identificadores como
valido_sin_hard ni frases tecnicamente calificadas fuera de esos patrones.
Un encabezado estructural Request valido por si solo tampoco es una asignacion
taxonomica. La regla examina tambien lineas en fences; no se excluyen ejemplos
por el solo hecho de usar Markdown de codigo.

## Excepciones acotadas

S-05 no marca los literales del tuple LEGACY_AUDIT_EVENT_NAMES declarado en el
nivel de modulo de src/semantic_guard/lint_rules.py. La excepcion se limita a
esa declaracion literal: no excluye el archivo ni llamadas o f-strings.
Un evento antiguo usado en otra asignacion del mismo modulo sigue produciendo
infraccion. El mismo nombre de variable fuera de ese modulo no tiene excepcion.

Los eventos se comparan por limites de identificador para evitar coincidencias
de prefijos. El evento largo REQUEST_EVALUADO_SIN_TECNICA se reporta una sola vez.
Esta es una comprobacion de constantes, no un analisis de referencias a variables.

## Uso

Desde la raiz del repositorio, en PowerShell:

```powershell
py -m src.semantic_guard.lint_runner
$LASTEXITCODE
```

Para indicar otra raiz:

```powershell
py -m src.semantic_guard.lint_runner --root C:\PROYECTO\sistema-turnos-atc
```

Salida: cantidad de archivos analizados/excluidos y detalles de infracciones.
Codigo de salida 0: sin infracciones en el alcance declarado.
Codigo de salida 1: infraccion o fallo S-00. Argumentos CLI invalidos: argparse
usa su codigo 2. Un error imprevisto no se transforma en una lista vacia.

API:

- run_semantic_lint(root="."): lista de SemanticViolation, compatible con uso previo.
- run_semantic_lint_report(root="."): SemanticLintReport con violations,
  analyzed_files y excluded_files.
- analyze_python_file y analyze_markdown_file: analisis directo de un archivo.

## Pruebas

El test de integridad existente usa la raiz obtenida desde su propio archivo.
Se agregan 27 regresiones compatibles con unittest y pytest. Cubren recorrido
completo, carpetas vacias, errores, alcance declarado, declaraciones versus uso,
limites de eventos, usos legitimos, infracciones S-01 a S-05 y salida CLI.
La prueba de enlaces simbolicos puede omitirse si el sistema no permite crearlos.

```powershell
py -m unittest discover -s tests -p test_semantic_guard_regressions.py -v
py -m pytest -q
```

La primera orden no requiere pytest ni carga conftest. La segunda verifica el
proyecto completo y debe ejecutarse localmente antes de cerrar v116.
Los smokes de CSV real pueden omitirse si faltan los archivos; registrar passed,
skipped y failed reales, sin sustituirlos por el resultado historico 463 passed.

## Semantic diff

Los modulos diff_runner, diff_rules y extractor se conservan sin modificaciones
en v116. Comparan taxonomias y terminos antiguos entre dos textos; no heredan las
reglas S-04/S-05 del lint. run_semantic_diff(old_path, new_path) permite rutas
explicitas. El entrypoint actual usa docs_old/contratos.md y docs/contratos.md,
y no implementa un codigo de salida no cero por infracciones.

No usar ese entrypoint como gate automatico sin preparar su base de comparacion y
corregir su salida en un alcance posterior. No se declara reparado todo semantic
diff por haber reparado el lint.

## Mantenimiento

Mantener las exclusiones explicitas y probadas. Cualquier nueva regla debe incluir
un caso que deba fallar y otro legitimo que deba pasar. Las excepciones no deben
ocultar usos productivos. Si cambia el inventario, cambian los conteos; no fijarlos
como criterio de exito. Mantener codigo, esta especificacion y seguimiento juntos.
