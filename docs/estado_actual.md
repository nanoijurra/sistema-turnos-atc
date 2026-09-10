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

Ultimo checkpoint cerrado confirmado al redactar: **v114**, commit `a9abc31`,
tag `checkpoint-v114-reparacion-estructural-documentos-canonicos`.
Rama y tag publicados segun salida del usuario. Sin cambios versionados al cierre;
quedaban tres TXT ajenos sin seguimiento. Esto no afirma limpieza permanente.

Trabajo actual: **v115 - conciliacion funcional documental**, pendiente de cierre Git.
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

Ultima suite completa registrada: **463 passed sobre v110**, reportada por el usuario.
En este entorno no hay pytest; no se declara una ejecucion nueva de la suite.
En v115 se inspeccionaron codigo y tests y se ejecutaron comprobaciones sinteticas
acotadas de normalizacion, frontera multimes y reporte, usando SQLite temporal.
Los CSV reales no se utilizaron ni se reejecutaron sus smokes.

V114 reparo estructura y conservo numeraciones. V115 agrega contenido sustentado en
codigo. Queda pendiente verificar e incorporar el paquete en el repositorio local.
semantic_guard sigue defectuoso y no acredita integridad documental completa.

## Estado documental y siguientes pasos

- Se actualiza contexto, se concilia Turno y se incorporan objetos/terminos calendar-aware.
- Decision 54 y Contratos 26/27 completan contenido faltante sin sobreescribir 53/25.
- La contradiccion entrenamiento/Turno ACC queda resuelta documentalmente contra codigo.
- Referencias historicas a roster_service representan extraccion futura, no falta de versionado.
- contexto_resumen y estado_docs siguen desactualizados; generacion prevista en v117.
- README vacio y retiro material de contratos_resumen pendientes.
- v116: corregir semantic_guard; v118: cierre documental integral.
- v119: simulacion seleccionada prevista; revisar prioridad frente a deuda funcional detectada.
- Bases SQLite transitorias versionadas y requirements UTF-16: deuda separada.

## Recuperacion y mantenimiento

Al retomar, comprobar Git, leer este estado y consultar el mapa. Registrar la base de
cada evidencia; no promover pruebas sinteticas a resultado de suite completa.
El ultimo checkpoint cerrado identifica la base confirmada al redactar, no el hash
futuro del propio documento. Mantener seguimiento de hallazgos en checkpoints siguientes.
