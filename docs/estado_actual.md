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

Ultimo checkpoint cerrado confirmado al redactar: **v115**, commit `e39e73f`,
tag `checkpoint-v115-conciliacion-funcional-documental`.
Rama y tag publicados segun salida del usuario. Arbol de trabajo limpio al cierre de v115. Esto no afirma limpieza permanente.

Trabajo actual: **v116 - reparacion de semantic lint**, pendiente de cierre Git.
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

La validacion local de v116 esta registrada. Quedan pendientes el cotejo final del
diff preparado y el cierre Git (commit, tag y push).

V114 reparo estructura y conservo numeraciones. V115 agrego contenido sustentado en
codigo y quedo cerrado en e39e73f. V116 modifica solo la herramienta de lint, sus
tests y documentacion de seguimiento; no modifica reglas funcionales ATC.
El lint de semantic_guard se repara en v116: recorrido completo, reglas acotadas,
errores visibles y salida CLI verificable. No acredita integridad documental
completa ni reglas ATC. Semantic diff mantiene sus limitaciones anteriores.

## Estado documental y siguientes pasos

- Se actualiza contexto, se concilia Turno y se incorporan objetos/terminos calendar-aware.
- Decision 54 y Contratos 26/27 completan contenido faltante sin sobreescribir 53/25.
- La contradiccion entrenamiento/Turno ACC queda resuelta documentalmente contra codigo.
- Referencias historicas a roster_service representan extraccion futura, no falta de versionado.
- contexto_resumen y estado_docs siguen desactualizados; generacion prevista en v117.
- README vacio y retiro material de contratos_resumen pendientes.
- v116: lint reparado y 27 regresiones aprobadas en el entorno de preparacion; suite local 489 passed, 1 skipped; cierre Git pendiente.
- v117: generacion de derivados; v118: cierre documental integral.
- v119: simulacion seleccionada prevista; revisar prioridad frente a deuda funcional detectada.
- Bases SQLite transitorias versionadas y requirements UTF-16: deuda separada.

## Recuperacion y mantenimiento

Al retomar, comprobar Git, leer este estado y consultar el mapa. Registrar la base de
cada evidencia; no promover pruebas sinteticas a resultado de suite completa.
El ultimo checkpoint cerrado identifica la base confirmada al redactar, no el hash
futuro del propio documento. Mantener seguimiento de hallazgos en checkpoints siguientes.
