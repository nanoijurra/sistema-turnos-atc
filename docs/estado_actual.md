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

Ultimo checkpoint cerrado confirmado al redactar: **v113**.

- Commit: `3229bb3`.
- Tag: `checkpoint-v113-clasificacion-estructura-documental`.
- Cierre: push de rama y tag confirmado por salida Git del usuario.
- Arbol de trabajo limpio en la verificacion de cierre; no es una afirmacion permanente.
- Base funcional auditada: v110, commit `e345871`.
- v111 registro la auditoria; v112 saneo el historial; v113 incorporo estado y mapa.
  Los tres cambios fueron documentales.

Este documento es la referencia del estado vigente. No sustituye los contratos,
las decisiones ni la evidencia del codigo. La clasificacion y las dependencias
se declaran en [mapa_documental.yml](mapa_documental.yml).

Fuentes de esta revision:

- [Auditoria documental v110](hitos/auditoria_documental_v110.md).
- [Registro activo](../checkpoints.md).
- [Indice historico v1-v95](hitos/indice_checkpoints_v1_v95.md).
- Salidas Git aportadas por el usuario para los cierres v112 y v113.
- Preparacion estructural v114 y verificacion local del usuario durante su incorporacion.

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
el usuario. No se reejecuto pytest durante los cambios documentales v111-v114.
Ese resultado no acredita una ejecucion nueva ni cobertura operativa completa.

En v112 se verificaron:

- coincidencia del original local de checkpoints con el objeto preservado en v111;
- conservacion textual de v96-v111, salvo el encabezado normalizado de v97;
- 95 entradas en el indice historico;
- alcance documental del diff y ausencia de errores de whitespace;
- commit, tag, push y arbol de trabajo limpio al cierre.

En la preparacion v114 se comprobaron un H1 por documento, fences cerrados,
jerarquia sin saltos, destinos de indices y conservacion del texto de las reglas.
La copia aislada de los seis documentos paso git diff --check. El usuario los
incorporo localmente; queda pendiente la verificacion final del conjunto de nueve
archivos y su cierre Git. No se audito nuevamente el codigo funcional.

`semantic_guard` tiene defectos pendientes. Su salida positiva no demuestra hoy
una revision completa ni integridad documental.

---

## Estado documental

La auditoria v111 detecto documentos desactualizados y declaraciones de cambios
que no coinciden con los commits. v112 resolvio el volumen y la organizacion del
historial; no reparo esas contradicciones.

- `contexto_sistema.md`: estructura reparada en v114; contenido antiguo conservado
  y advertido como desactualizado. Actualizacion funcional pendiente.
- `contratos.md`, `decisiones.md`, `invariantes.md` y `diccionario.md`: estructura
  e indices reparados; esto no acredita actualizacion funcional completa.
- `modelo_dominio.md`: Controlador/Turno reordenados y titulo 4.5 duplicado resuelto
  estructuralmente. La definicion anterior que incluye entrenamiento se conserva
  identificada; su contradiccion con la frontera operativa sigue pendiente.
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

**v114 - reparacion estructural de documentos canonicos**, en curso; cierre Git pendiente.

Alcance total: seis documentos canonicos y tres archivos de seguimiento.

- Reparar titulos, jerarquias, indices y el fence del contexto.
- Conservar numeraciones de decisiones, contratos e invariantes.
- Preservar texto de reglas y definiciones, con notas explicitas sobre contradicciones.
- Actualizar este estado y el mapa, y agregar el registro v114 en checkpoints.

La definicion de Turno y la vigencia de referencias a roster_service requieren
conciliacion conceptual posterior. No se habilitan nuevos turnos ni elegibilidades.
No se reparan generadores o semantic_guard ni se modifica codigo o datos reales.
El mapa sigue siendo declarativo; sus 17 rutas fueron verificadas en v113.

---

## Deuda y siguientes pasos

Plan de referencia aprobado en v111, sujeto a revision explicita de alcance:

| Etapa | Objetivo | Estado |
| --- | --- | --- |
| v114 | Reparar estructura e indices de documentos canonicos | En curso; cierre Git pendiente |
| v115 | Actualizar contenido funcional y conciliar contradicciones identificadas | Pendiente |
| v116 | Corregir y ampliar semantic_guard | Pendiente |
| v117 | Generar sistematicamente documentos derivados | Pendiente |
| v118 | Cerrar la reconciliacion documental integral | Pendiente |
| v119 | Simular un cambio de turno seleccionado | Previsto; alcance por precisar |

Deuda separada: bases SQLite transitorias versionadas en tests y
`requirements.txt` en UTF-16, segun auditoria. No se corrige dentro de v114.

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
