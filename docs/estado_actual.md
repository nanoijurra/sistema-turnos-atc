# Estado actual del sistema ATC

## Tabla de contenido

- [Base confirmada](#base-confirmada)
- [Capacidades verificadas](#capacidades-verificadas)
- [Limites y deuda funcional](#limites-y-deuda-funcional)
- [Validacion](#validacion)
- [Estado documental y siguientes pasos](#estado-documental-y-siguientes-pasos)
- [Recuperacion y mantenimiento](#recuperacion-y-mantenimiento)

---

## Base confirmada

Ultimo checkpoint cerrado confirmado al redactar: **v118**, commit `8a6a6b7`,
tag `checkpoint-v118-cierre-documental-integral`.
Rama y tag publicados segun salida del usuario. Arbol de trabajo limpio al cierre de v118. Esto no afirma limpieza permanente.

Trabajo actual: **v119 - correccion del descanso minimo**, pendiente de cierre Git.
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
- V119 corrige descanso: default y perfiles incluidos 16 horas, comparacion <.
  Engine y prefiltro comparten horas_minimas y alias min_horas, con validacion.
- Timeline no lee perfiles JSON; umbrales explicitos externos siguen siendo posibles.
- No se migran ni reevalúan solicitudes persistidas evaluadas con reglas anteriores.
- Ventana operativa default configurada: 12 horas antes del turno; distinta del descanso.
- No se acredita cobertura de 18 turnos, 144 horas ni maximo universal de jornadas mixtas
  mediante el diagnostico timeline inspeccionado.
- Los requisitos operativos deben conciliarse con estas reglas antes de uso decisorio.
- Cargar modulos puede inicializar tablas SQLite; no prometer cero acceso a DB.

Los limites que permanecen requieren un alcance
funcional posterior explicito; no desaparecen por completar documentacion.

## Validacion

Base v118 en Windows confirmada por el usuario: 510 passed, 1 skipped en 7.23 s.
V118 cerrado y publicado en 8a6a6b7. Resultado historico, no ejecucion de v119.
Preparacion v119 en Python 3.12/Linux: 532 passed, 5 skipped; las cinco omisiones
requieren CSV reales locales no incluidos en el ZIP. Incluye 26 casos nuevos de
descanso y parametros. Validacion v119 en Windows confirmada por el usuario:
- Suite completa: 536 passed, 1 skipped en 7.47 s.
- Unica omision: prueba de symlinks por permisos del sistema operativo.
- Generador: dos derivados sincronizados, salida 0.
- Semantic lint: 58 analizados, 6 excluidos, sin infracciones, salida 0.
- Git diff --check sin errores.
Cotejo final del diff preparado y cierre Git pendientes.
No se acredita uso operacional ni cobertura de todas las reglas ATC.

## Estado documental y siguientes pasos

- Se actualiza contexto, se concilia Turno y se incorporan objetos/terminos calendar-aware.
- Decision 54 y Contratos 26/27 completan contenido faltante sin sobreescribir 53/25.
- La contradiccion entrenamiento/Turno ACC queda resuelta documentalmente contra codigo.
- Referencias historicas a roster_service representan extraccion futura, no falta de versionado.
- contexto_resumen y estado_docs se generan desde estado_actual y mapa_documental
  mediante tools/generar_documentacion.py; --check detecta desactualizacion.
- README completado; contratos_resumen retirado del arbol y del mapa en v118.
- v116 cerrado: lint reparado, suite local 489 passed, 1 skipped por symlinks en Windows.
- v117 cerrado: generador y comprobacion validados en Windows.
- v118 cerrado: etapa documental completada y deuda funcional explicita.
- v119: correccion del descanso priorizada; simulacion seleccionada postergada.
- Bases SQLite transitorias versionadas y requirements UTF-16: deuda separada.

## Recuperacion y mantenimiento

Al retomar, comprobar Git, leer este estado y consultar el mapa. Registrar la base de
cada evidencia; no promover pruebas sinteticas a resultado de suite completa.
El ultimo checkpoint cerrado identifica la base confirmada al redactar, no el hash
futuro del propio documento. Mantener seguimiento de hallazgos en checkpoints siguientes.

Despues de editar este estado o el mapa, ejecutar el generador con --write y
--check. Instrucciones: [generacion_documental.md](generacion_documental.md).
