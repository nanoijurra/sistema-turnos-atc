# Contexto del sistema

## Tabla de contenido

- [Proposito y base](#proposito-y-base)
- [Arquitectura implementada](#arquitectura-implementada)
- [Flujo formal](#flujo-formal)
- [Importacion y Turno](#importacion-y-turno)
- [Diagnostico y reporte](#diagnostico-y-reporte)
- [Alcance multimes y reglas](#alcance-multimes-y-reglas)
- [Evidencia y limites de validacion](#evidencia-y-limites-de-validacion)
- [Continuidad del trabajo](#continuidad-del-trabajo)

---

## Proposito y base

Sistema Python de evaluacion y gestion formal de cambios de turno ATC.
Revision v115 contrastada con el codigo del archivo exportado desde v114,
commit `a9abc31`. El cierre Git y la evidencia de tests se consultan en
[estado_actual.md](estado_actual.md); este documento describe arquitectura y limites.
No reemplaza decisiones, contratos, invariantes ni el modelo de dominio.

## Arquitectura implementada

| Componente | Responsabilidad actual |
| --- | --- |
| `src/engine.py` | Ejecucion de reglas configuradas y funciones de creacion de versiones; conserva responsabilidades adicionales a la validacion |
| `src/validator.py` | Reglas tradicionales sobre asignaciones |
| `src/scoring.py` | Agregacion tecnica y utilidades de mapeo |
| `src/simulator.py` | Simular y comparar; producir clasificacion tecnica |
| `src/swap_service.py` | Workflow formal, resolucion y aplicacion; coordina versiones y obsolescencia |
| `src/roster_store.py` | Persistencia SQLite y consulta de versiones |
| `src/request_store.py` | Persistencia de solicitudes e historial |
| `src/roster_import_service.py` | Importacion, normalizacion y creacion explicita de version si se solicita |
| `src/roster_day_timeline.py` | Representacion de dias, agrupacion y rachas |
| `src/roster_timeline_validator.py` | Reglas calendar-aware sobre dias recibidos |
| `src/roster_timeline_diagnostics.py` | Resumen y comparacion diagnostica |
| `src/roster_calendar_aware_entrypoint.py` | Entrada publica del diagnostico paralelo |
| `src/roster_calendar_aware_report.py` | Reporte diagnostico serializable |
| `src/roster_calendar_aware_multimonth.py` | Adaptador CSV ACC CBA y resumen de diagnosticos mensuales independientes |

No existe `src/roster_service.py` en la base revisada. Su extraccion aparece como
objetivo historico; no es un requisito para usar las funciones de versionado ya
implementadas en engine y coordinadas desde swap_service.

## Flujo formal

`crear_swap_request -> evaluar_swap_request -> resolver_swap_request -> aplicar_swap_request`.
La evaluacion produce informacion tecnica y decision sugerida. La resolucion
explicita cambia el estado; la aplicacion exige `APROBADO`, version vigente y
coherencia de indices/controladores. Crea una nueva version, cancela solicitudes
obsoletas y registra la aplicacion. No reevalua tecnicamente durante la aplicacion.

La exploracion y las fachadas de oferta se mantienen separadas de la resolucion.
La clasificacion tecnica, la decision sugerida y el estado del workflow no son
intercambiables. El diagnostico calendar-aware tampoco sustituye esos planos.

## Importacion y Turno

El importador ACC usa `crear_esquema_8h()`: A 06:30, B 14:30 y C 22:30, ocho horas
cada uno. La configuracion ACC activa A/B/C; D/X son configurables no activos.
El catalogo reconoce otros codigos, pero reconocer un codigo no lo activa.

`Turno` es una dataclass con codigo, inicio, duracion, categoria y banderas.
No valida por si sola una lista de codigos. La frontera operacional de la
importacion ACC proviene de su configuracion y del esquema de ocho horas.
`OJT`, `SIM`, `EN` y otros eventos no operativos no generan `Asignacion` operativa.

| Entrada | Normalizacion ACC | Resultado |
| --- | --- | --- |
| Vacia | Vacia | Dia LIBRE, sin asignacion |
| FC | Vacia | Dia LIBRE, con trazabilidad de normalizacion |
| IN/C | C | Dia OPERATIVO y asignacion C |
| IN | EN | Evento no operativo |
| REM / RET | RTA / RTB | Eventos no operativos |

El adaptador `importar_roster_acc_cba_desde_csv` esta definido en
`src/roster_calendar_aware_multimonth.py`, no en roster_import_service.

## Diagnostico y reporte

El entrypoint recibe una importacion con `dias_importados` o un iterable de dias.
El reporte expone dias, totales HARD/SOFT, codigos principales, detalles y metadata.
`limite_detalles` recorta solo detalles, sin alterar totales. Los codigos se ordenan
por cantidad descendente y luego por codigo. `to_dict()` permite serializacion.

`VALIDO_SIN_HARD` significa ausencia de HARD en el diagnostico ejecutado; no implica
importacion sin errores, aprobacion de solicitud ni cobertura de todas las reglas.
El reporte no crea versiones, requests ni aplica cambios. Sin embargo, la carga de
modulos dependientes puede inicializar tablas SQLite: no se garantiza ausencia
absoluta de acceso a DB por el solo hecho de importar los modulos.

## Alcance multimes y reglas

`diagnosticar_carga_multimes_calendar_aware` procesa cada entrada por separado y
agrega resultados. No concatena timelines ni verifica automaticamente el cruce
entre meses. El entrypoint sobre dias puede recibir una concatenacion construida
por el llamador; ese encadenamiento no lo realiza la fachada multimes.

`apto_para_revision_carga` exige entradas presentes, sin errores de importacion ni
HARD mensuales y al menos un mes. Puede seguir omitiendo una infraccion de frontera.
Los meses faltantes se omiten por defecto; con `omitir_faltantes=False` se lanza
`FileNotFoundError`. Los formatos soportados son CSV_SIMPLE y CSV_ACC_CBA.

El timeline usa por defecto maximo 5 A/B consecutivos, 3 C consecutivos, aviso SOFT
por mas de 5 libres, y descanso insuficiente cuando es menor o igual a 12 horas.
No equivale a un control universal de cinco jornadas operativas mixtas, ni incluye
por si mismo maximos mensuales de 18 turnos o 144 horas.

El validador tradicional usa por defecto 12 horas pero compara con `<`, no `<=`.
`config_equilibrado.json` declara `min_horas`, mientras la funcion acepta
`horas_minimas`: engine filtra el nombre no reconocido y utiliza el default.
El entrypoint calendar-aware no recibe ni propaga parametros de reglas.
Estos son limites del codigo observado, no una validacion de normativa operativa.
Conciliar el requisito operativo de descanso, los umbrales y su configuracion
requiere un cambio funcional explicito posterior.

## Evidencia y limites de validacion

Los tests v106, v109 y v110 dependen de CSV locales y pueden quedar omitidos si
faltan. v110 busca un par para smoke, llama a `simulator.evaluar_swap`, comprueba
la copia simulada y la conservacion de asignaciones originales. No es una
aprobacion ni una aplicacion real de swap.

Las verificaciones v115 y su alcance se registran en
[hitos/conciliacion_funcional_v115.md](hitos/conciliacion_funcional_v115.md).
No se modifica codigo ni se declara una ejecucion nueva de la suite completa.

## Continuidad del trabajo

Consultar el estado y el mapa documental antes de retomar. La deuda de
semantic_guard y la generacion de derivados mantienen sus etapas propias.
No subir CSV reales locales ni mezclar una correccion de reglas con un cierre
exclusivamente documental.
