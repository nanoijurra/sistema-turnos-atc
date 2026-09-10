# Conciliacion funcional documental v115

## Base y alcance

Base exportada desde tag checkpoint-v114-reparacion-estructural-documentos-canonicos,
commit a9abc31 confirmado por el usuario. El ZIP no contiene metadatos Git completos.
Revision de codigo y tests para documentar capacidades v105-v110 y conciliar Turno.
No se modifica src/, tests/, config/, tools/, bases ni CSV reales.

## Matriz de evidencia

| Capacidad | Codigo | Tests existentes revisados |
| --- | --- | --- |
| EntryPoint paralelo | src/roster_calendar_aware_entrypoint.py | tests/test_roster_calendar_aware_entrypoint.py |
| Reporte y limite de detalles | src/roster_calendar_aware_report.py | tests/test_roster_calendar_aware_report.py |
| Agregado por mes y CSV ACC CBA | src/roster_calendar_aware_multimonth.py | tests/test_roster_calendar_aware_multimonth.py |
| FC e IN/C | src/roster_import_service.py y src/roster_code_catalog.py | tests/test_roster_import_service.py y tests/test_roster_code_catalog.py |
| Smoke de reporte real | src/roster_calendar_aware_report.py | tests/test_smoke_reporte_operativo_calendar_aware_csv_real.py |
| Smoke multimes real | src/roster_calendar_aware_multimonth.py | tests/test_smoke_multimes_acc_cba_reales.py |
| Swap simulado real | src/simulator.py | tests/test_smoke_swap_simulado_acc_cba_real.py |
| Turno y frontera ACC | src/models.py y src/roster_import_service.py | tests de importacion y catalogo |
| Versionado implementado | src/swap_service.py, src/engine.py y src/roster_store.py | Inspeccion directa; sin nueva suite |

Los tests reales contienen expectativas ligadas a CSV locales. Su presencia en el
repositorio no demuestra ejecucion en este entorno ni garantiza esos resultados
sobre archivos distintos. El smoke de swap usa el simulador tradicional y no
crea solicitudes ni aplica cambios reales.

## Comprobaciones ejecutadas

Sin pytest instalado. Se realizaron llamadas directas con datos sinteticos y una
base SQLite temporal, reasignando DB_PATH en memoria antes de importar servicios.
Los imports inicializan tablas en dependencias. Un primer intento sin directorio
data fallo al abrir SQLite; se repitio con aislamiento temporal, sin editar codigo.

1. FC -> LIBRE; IN/C -> C; OJT/SIM quedan fuera de asignaciones: comprobado.
2. C el 30 de junio y A el 1 de julio, mismo controlador:
   - Fachada multimes: 0 HARD y apto_para_revision_carga=True.
   - Timeline concatenada entregada al entrypoint: 1 HARD por descanso de 0 horas.
3. Reporte del diagnostico anterior: total_hard=1 y un detalle con limite=1.

Son comprobaciones acotadas; no sustituyen la suite completa. Ultima suite
historica reportada por usuario: 463 passed sobre v110. No se reejecutaron los
smokes con CSV reales ni se instalaron dependencias para ampliar pruebas.

## Hallazgos que requieren decision funcional

- Multimes no concatena dias y puede omitir infracciones entre meses.
- Descanso timeline default 12 con <=; tradicional default 12 con <.
- config_equilibrado usa min_horas, pero validar_descanso_minimo acepta horas_minimas.
  engine.ejecutar_regla filtra claves no reconocidas: el valor declarado no se pasa.
  Actualmente coincide numericamente con el default, lo que oculta la discrepancia.
- La ventana operativa configurada por defecto es 12 horas antes del turno. No debe
  confundirse con descanso entre jornadas ni afirmarse una ventana 24-36 implementada.
- Los maximos timeline de A/B y C separados no equivalen a cinco jornadas mixtas.
- No se observan controles mensuales 18 turnos/144 horas en este camino diagnostico.
- La configuracion ACC y el esquema 8H deben ser compatibles; activar D/X en un set
  no crea automaticamente esos turnos en el esquema que utiliza el importador.
- Ausencia de versionado de negocio en las funciones diagnosticas no equivale a
  ausencia absoluta de escrituras SQLite al cargar dependencias.

Estos hallazgos describen implementacion. No certifican conformidad normativa ni
cambian los requisitos operativos. Deben tratarse en un checkpoint funcional
explicito antes de presentar el sistema como verificador operacional completo.

## Conciliacion realizada

Se retira del modelo vigente el ejemplo entrenamiento como Turno operativo ACC;
la evidencia previa queda preservada en v114. La dataclass sigue siendo general.
Se reemplaza el contexto desactualizado por arquitectura observada y limites.
Se documentan Decision 54, Contratos 26/27, CA-7/8/9 y objetos/terminos de reporte.
Se mantienen numeraciones anteriores. No se reescribe el historial de checkpoints.

## Pendientes de proceso

Cotejo local final del paquete, commit/tag/push v115. semantic_guard pendiente v116;
derivados manuales desactualizados pendientes v117. El README vacio y retiro material
de contratos_resumen siguen en deuda; no se amplian silenciosamente en este cambio.
