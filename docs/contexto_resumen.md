# Contexto resumen

Generado por `tools/generar_documentacion.py`. No editar manualmente.

Fuente: [estado_actual.md](estado_actual.md).

<!-- fuente-sha256: 7920d59a50530e524e62236852a0ba31d82e2b8ce8e0c6ce93be5db961521bea; generador-sha256: a191210826215580dcff5d40a16452a81e5ec843d7e5ba66f4d9856ee503ca9e -->

Seleccion de secciones completas; no certifica el contenido de la fuente.

## Base confirmada

Ultimo checkpoint cerrado confirmado al redactar: **v117**, commit `6db14e9`,
tag `checkpoint-v117-generacion-documentos-derivados`.
Rama y tag publicados segun salida del usuario. Arbol de trabajo limpio al cierre de v117. Esto no afirma limpieza permanente.

Trabajo actual: **v118 - cierre documental integral**, pendiente de cierre Git.
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

Ultima suite completa confirmada por el usuario, sobre v117 en Windows:
**510 passed, 1 skipped en 7.68 s**. Derivados sincronizados y lint con
57 archivos analizados, 6 excluidos, sin infracciones; ambos con salida 0.
El skip de symlinks fue identificado en v116 por permisos del sistema operativo;
la salida agregada de v117 informa una omision sin repetir su motivo.

V117 quedo cerrado y publicado en 6db14e9 con arbol limpio segun salida del usuario.
La evidencia de v116 (489 passed, 1 skipped) y v110 (463 passed) es historica.
Validacion v118 en Windows confirmada por el usuario:
- Suite completa: 510 passed, 1 skipped en 7.23 s.
- Generador: dos derivados sincronizados, salida 0.
- Semantic lint: 57 archivos analizados, 6 excluidos, sin infracciones, salida 0.
- Git diff --check sin errores.
Cierre Git pendiente. No se atribuye la suite de v117 a una ejecucion nueva.

V114 reparo estructura y conservo numeraciones. V115 agrego contenido sustentado en
codigo y quedo cerrado en e39e73f. V116 modifica solo la herramienta de lint, sus
tests y documentacion de seguimiento; no modifica reglas funcionales ATC.
El lint de semantic_guard se repara en v116: recorrido completo, reglas acotadas,
errores visibles y salida CLI verificable. No acredita integridad documental
completa ni reglas ATC. Semantic diff mantiene sus limitaciones anteriores.
