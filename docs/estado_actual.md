# Estado actual del sistema ATC

## Tabla de contenido

- [Base y evidencia](#base-y-evidencia)
- [Capacidades y limites](#capacidades-y-limites)
- [Validacion](#validacion)
- [Estado documental](#estado-documental)
- [Trabajo en curso](#trabajo-en-curso)
- [Deuda y siguientes pasos](#deuda-y-siguientes-pasos)
- [Mantenimiento y recuperacion](#mantenimiento-y-recuperacion)

---

## Base y evidencia

Ultimo checkpoint cerrado: **v112**.

- Commit: `301cbe5`.
- Tag: `checkpoint-v112-saneamiento-checkpoints-indice-historico`.
- Cierre: push de rama y tag confirmado por salida Git del usuario.
- Arbol de trabajo limpio en la verificacion de cierre; no es una afirmacion permanente.
- Base funcional auditada: v110, commit `e345871`.
- v111 registro la auditoria; v112 saneo el historial. Ambos cambios fueron documentales.

Este documento es la referencia del estado vigente. No sustituye los contratos,
las decisiones ni la evidencia del codigo. La clasificacion y las dependencias
se declaran en [mapa_documental.yml](mapa_documental.yml).

Fuentes de esta revision:

- [Auditoria documental v110](hitos/auditoria_documental_v110.md).
- [Registro activo](../checkpoints.md).
- [Indice historico v1-v95](hitos/indice_checkpoints_v1_v95.md).
- Salidas Git aportadas por el usuario para el cierre de v112.

Las capacidades siguientes se apoyan en la auditoria de v110 y el historial;
esta revision documental no constituye una nueva inspeccion del codigo.

---

## Capacidades y limites

### Workflow formal tradicional

Cadena principal: `swap_service -> simulator -> engine.py -> validator.py`.

El flujo dispone de creacion, evaluacion, resolucion y aplicacion de solicitudes,
con persistencia de solicitudes e historial y versionado de rosters.
La aplicacion formal requiere una solicitud en estado `APROBADO`.

Se mantienen separados:

- clasificacion tecnica;
- decision operativa;
- estado del workflow.

### Diagnostico calendar-aware paralelo

Incluye importacion acotada de rosters, timeline diaria, validadores sobre dias
importados, diagnostico comparativo, entrypoint paralelo, reporte operativo y
diagnostico de carga multimes.

Hasta v110 se registraron importacion de CSV ACC CBA, normalizacion de codigos
`FC` e `IN/C`, pruebas multimes y un smoke de swap simulado sobre datos reales.

El diagnostico calendar-aware no reemplaza el motor tradicional, no decide
solicitudes ni aplica cambios al roster. La timeline distingue dias libres de
situaciones no operativas documentadas.

No se aplicaron swaps reales sobre los CSV ACC CBA en el alcance auditado.
La integracion del diagnostico calendar-aware al workflow formal requiere una
decision explicita y su validacion; no esta habilitada por este documento.

---

## Validacion

Ultima ejecucion de suite registrada: **463 passed**, sobre v110, confirmada por
el usuario. No se reejecuto pytest durante la auditoria ni para el saneamiento v112.
Ese resultado no acredita una ejecucion nueva ni cobertura operativa completa.

En v112 se verificaron:

- coincidencia del original local de checkpoints con el objeto preservado en v111;
- conservacion textual de v96-v111, salvo el encabezado normalizado de v97;
- 95 entradas en el indice historico;
- alcance documental del diff y ausencia de errores de whitespace;
- commit, tag, push y arbol de trabajo limpio al cierre.

`semantic_guard` tiene defectos pendientes. Su salida positiva no demuestra hoy
una revision completa ni integridad documental.

---

## Estado documental

La auditoria v111 detecto documentos desactualizados y declaraciones de cambios
que no coinciden con los commits. v112 resolvio el volumen y la organizacion del
historial; no reparo esas contradicciones.

- `contexto_sistema.md`: canonico, gravemente desactualizado y con Markdown defectuoso.
- `contexto_resumen.md`: derivado, detenido en el estado posterior a v103.
- `estado_docs.md`: control derivado desactualizado; contiene afirmaciones incorrectas.
- `contratos_resumen.md`: retirado como referencia vigente por decision de auditoria;
  su retiro material del repositorio sigue pendiente.
- v102: no incorporo las nuevas secciones declaradas en decisiones y contratos.
- v103: no modifico `contexto_sistema.md`, pese a declararlo en su checkpoint.

Se preservan las numeraciones reales existentes:

- Decision 53: Perfil operativo de persona.
- Contrato 25: Estado operativo general y habilitaciones.

No deben sobrescribirse para acomodar incorporaciones calendar-aware.

---

## Trabajo en curso

**v113 - clasificacion y estructura documental oficial**: documentos preparados y rutas verificadas; cierre Git pendiente.

Alcance:

- incorporar este estado vigente;
- incorporar el mapa documental con tipos, fuentes, dependencias y disparadores;
- registrar v113 en checkpoints.

Verificacion local: 17 rutas registradas, todas existentes.

No incluye reparacion de documentos canonicos, generadores, semantic_guard,
codigo funcional, datos reales ni modificaciones del workflow.
El mapa es declarativo: no implementa controles automaticos por si mismo.

---

## Deuda y siguientes pasos

Plan de referencia aprobado en v111, sujeto a revision explicita de alcance:

| Etapa | Objetivo | Estado |
| --- | --- | --- |
| v114 | Reparar documentos canonicos e indices | Pendiente |
| v115 | Completar documentacion funcional v105-v110 | Pendiente |
| v116 | Corregir y ampliar semantic_guard | Pendiente |
| v117 | Generar sistematicamente documentos derivados | Pendiente |
| v118 | Cerrar la reconciliacion documental integral | Pendiente |
| v119 | Simular un cambio de turno seleccionado | Previsto; alcance por precisar |

Deuda separada: bases SQLite transitorias versionadas en tests y
`requirements.txt` en UTF-16, segun auditoria. No se corrige dentro de v113.

---

## Mantenimiento y recuperacion

Actualizar este documento cuando cambien capacidades, limites, deuda, validacion
o el eje de trabajo. Cada resultado de tests debe indicar la base donde se obtuvo.
No copiar automaticamente afirmaciones de checkpoints sin cotejar su evidencia.

El ultimo checkpoint cerrado de este documento identifica la base confirmada al
redactarlo. En cada reanudacion prevalece la verificacion actual de Git; no intentar
incluir dentro de un commit el hash de ese mismo commit.

Para retomar trabajo: comprobar Git, leer este archivo y el mapa, y consultar
solo los documentos relevantes. Los historicos aportan antecedentes, no reemplazan
el estado vigente. La evidencia original anterior al saneamiento queda en el tag v111.

---
