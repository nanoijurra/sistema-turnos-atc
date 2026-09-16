# Contexto resumen

Generado por `tools/generar_documentacion.py`. No editar manualmente.

Fuente: [estado_actual.md](estado_actual.md).

<!-- fuente-sha256: 95fb31171ecff896a032085baad109870916face31a8cbd36cd6aede7d37434f; generador-sha256: a191210826215580dcff5d40a16452a81e5ec843d7e5ba66f4d9856ee503ca9e -->

Seleccion de secciones completas; no certifica el contenido de la fuente.

## Base confirmada

Ultimo checkpoint cerrado confirmado al redactar: **v116**, commit `d082c50`,
tag `checkpoint-v116-reparacion-semantic-lint`.
Rama y tag publicados segun salida del usuario. Arbol de trabajo limpio al cierre de v116. Esto no afirma limpieza permanente.

Trabajo actual: **v117 - generacion sistematica de derivados**, pendiente de cierre Git.
Base funcional: codigo exportado desde v114; v111-v114 fueron cambios documentales.
El estado es referencia de seguimiento; contratos, decisiones e invariantes definen
sus planos. El [mapa](mapa_documental.yml) declara fuentes y responsabilidades.

## Capacidades verificadas

- Workflow formal crear/evaluar/resolver/aplicar, con persistencia y versiones.
- Importacion ACC acotada, timeline diaria y diagnostico calendar-aware paralelo.
- Reporte operativo serializable y resumen multimes de meses independientes.
- Adaptador CSV ACC CBA, FC -> LIBRE e IN/C -> C.
- Smoke versionado de swap simulado sobre CSV real; no aplicacion operacional real.

Arquitectura detallada: [contexto_sistema.md](contexto_sistema.md).
Evidencia: [conciliacion funcional v115](hitos/conciliacion_funcional_v115.md).

## Limites y deuda funcional

- El calendario paralelo no reemplaza al motor tradicional ni decide solicitudes.
- Multimes no verifica automaticamente continuidad entre meses. Caso sintetico
  C/30-jun -> A/1-jul: agregado mensual 0 HARD, timeline concatenada 1 HARD.
- VALIDO_SIN_HARD y apto_para_revision_carga no equivalen a aprobacion operativa.
- Descanso timeline default 12 con <=; tradicional default 12 con <.
- min_horas en config_equilibrado se filtra por no coincidir con horas_minimas.
- Ventana operativa default configurada: 12 horas antes del turno; distinta del descanso.
- No se acredita cobertura de 18 turnos, 144 horas ni maximo universal de jornadas mixtas
  mediante el diagnostico timeline inspeccionado.
- Los requisitos operativos deben conciliarse con estas reglas antes de uso decisorio.
- Cargar modulos puede inicializar tablas SQLite; no prometer cero acceso a DB.

Estos limites se documentan sin modificar codigo ni parametros. Requieren un alcance
funcional posterior explicito; no desaparecen por completar documentacion.

## Validacion

Ultima ejecucion de la suite completa, sobre los cambios locales de v116:
**489 passed, 1 skipped en 7.17 s**, confirmada por el usuario en Windows.

- Regresiones nuevas locales: 26 passed, 1 skipped en 0.51 s.
- Omision: test_symlink_directory_is_reported_instead_of_skipped_silently.
- Motivo informado: OS does not permit creating symlinks.
- Ese caso paso en el entorno de preparacion: 27 regresiones unittest aprobadas
  en Python 3.12. No se presenta como comprobado en Windows.
- Lint local: 56 archivos analizados, 6 excluidos, cero infracciones, salida 0.

El resultado historico de v110 fue 463 passed. En v115 se realizaron inspeccion
y comprobaciones sinteticas aisladas, sin pytest en el entorno de preparacion.
La ejecucion local nueva no debe confundirse con aquella evidencia historica.

V116 quedo cerrado y publicado en d082c50. Su validacion local queda como evidencia
de esa base. En preparacion v117: 21 pruebas unittest del generador aprobadas; --check confirma
los dos derivados sincronizados y lint con 57 analizados, 6 excluidos, sin infracciones.
Validacion v117 en Windows confirmada por el usuario: 510 passed, 1 skipped en 7.68 s.
Generador --check y semantic lint con salida 0. Git diff --check sin errores.
Cotejo final del diff y cierre Git pendientes.

V114 reparo estructura y conservo numeraciones. V115 agrego contenido sustentado en
codigo y quedo cerrado en e39e73f. V116 modifica solo la herramienta de lint, sus
tests y documentacion de seguimiento; no modifica reglas funcionales ATC.
El lint de semantic_guard se repara en v116: recorrido completo, reglas acotadas,
errores visibles y salida CLI verificable. No acredita integridad documental
completa ni reglas ATC. Semantic diff mantiene sus limitaciones anteriores.
