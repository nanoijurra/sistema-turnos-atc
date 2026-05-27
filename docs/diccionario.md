
# Diccionario semantico del sistema

Este documento define conceptos y terminos relevantes para mantener coherencia semantica en el sistema de swaps ATC.

Su objetivo es evitar ambiguedades entre capas, responsabilidades, estados, clasificaciones y decisiones.

---

# Subsistemas y capas

- `engine` -> subsistema responsable de ejecutar validaciones de reglas configuradas. Es fuente de verdad tecnica para reglas. No decide operativamente.

- `scoring` -> subsistema responsable de calcular validez tecnica y score tecnico. Separa impacto hard y soft. No decide operativamente.

- `simulator` -> subsistema responsable de simular swaps, comparar escenario antes/despues y producir clasificacion tecnica. Clasifica tecnicamente, pero no decide operativamente.

- `swap_service` -> subsistema responsable del workflow formal de `SwapRequest`: crear, evaluar, resolver y aplicar. Es responsable de decision operativa, estados y persistencia del workflow.

- `roster_index` -> estructura derivada del roster vigente para acceso rapido. No evalua, no clasifica, no decide y no persiste.

- `candidate_generation` -> subsistema responsable de generar candidatos estructurales acotados. No evalua, no clasifica, no decide y no persiste.

- `technical_prefilter` -> subsistema de descarte tecnico local y conservador. No clasifica, no puntua, no decide y no persiste.

- `candidate_selection` -> subsistema de seleccion estructural top-N previa a la simulacion. Reduce universo de candidatos, pero no determina calidad tecnica. No llama `engine`, `scoring` ni `simulator`.

- `exploration_flow` -> flujo tecnico-operativo de exploracion. Combina generacion, prefiltrado, seleccion, simulacion, ranking tecnico y priorizacion historica. Puede evaluar via `simulator`, pero no decide ni persiste.

- `offer_reporting` -> subsistema de salida presentable para UI/reporting. Transforma resultados de exploracion en ofertas presentables. No evalua, no decide y no persiste.

- `offer_service` -> fachada liviana de consulta/oferta. Coordina `exploration_flow` y `offer_reporting`. No gestiona workflow formal de requests.

- `offer_to_request_service` -> frontera arquitectonica que convierte una `OfertaEvaluada` seleccionada en una `SwapRequest` formal. Crea request `PENDIENTE`, adjunta `offer_origin`, no evalua, no decide y no aplica.

- `offer_workflow_service` -> fachada/coordinador de alto nivel para flujos operativos de oferta. Puede generar oferta, seleccionar oferta, crear request formal y persistir explicitamente. No evalua, no decide y no aplica salvo que invoque una fachada especifica de evaluacion formal definida por contrato.

- `semantic_guard` -> subsistema auxiliar de vigilancia semantica del proyecto. Ayuda a detectar drift terminologico, usos ambiguos y violaciones de vocabulario arquitectonico.

---

# Entidades y objetos de dominio

- `SwapRequest` -> solicitud formal de intercambio de turnos. Es la unica entidad con workflow operativo formal.

- `OfertaEvaluada` -> resultado tecnico presentable y seleccionable generado a partir del flujo de exploracion. No es una solicitud formal.

- `OfferReport` -> reporte presentable de ofertas evaluadas. Es salida de reporting, no workflow operativo.

- `offer_origin` -> bloque de origen adjunto a una `SwapRequest` creada desde oferta. Conserva evidencia observada de la oferta seleccionada. No reemplaza evaluacion formal.

- `selection_metadata` -> datos sobre la seleccion de una oferta. Indica como, cuando o por quien se selecciono una oferta. No equivale a aprobacion ni resolucion.

- `selected_by` -> identificador de quien selecciona una oferta. No significa aprobador.

- `selection_reason` -> motivo de seleccion de una oferta. No significa motivo de resolucion operativa.

- `roster_version_id` -> identificador de version de roster sobre la cual se evalua o crea una request.

- `roster_hash` -> huella tecnica del contenido del roster. Sirve para detectar obsolescencia o inconsistencia entre oferta y roster vigente.

---

# Taxonomias

## Clasificacion tecnica

- `BENEFICIOSO` -> clasificacion tecnica producida por `simulator` cuando el swap mejora el escenario segun criterios tecnicos.

- `ACEPTABLE` -> clasificacion tecnica producida por `simulator` cuando el swap no mejora significativamente, pero resulta tecnicamente admisible.

- `RECHAZABLE` -> clasificacion tecnica producida por `simulator` cuando el swap resulta tecnicamente inconveniente o no admisible segun evaluacion tecnica.

## Decision operativa

- `VIABLE` -> decision operativa sugerida por `swap_service`.

- `OBSERVAR` -> decision operativa sugerida por `swap_service` cuando corresponde revision o cautela.

- `RECHAZAR` -> decision operativa sugerida por `swap_service` cuando el flujo formal determina rechazo operativo.

## Estados de SwapRequest

- `PENDIENTE` -> estado inicial de una `SwapRequest` creada pero aun no evaluada formalmente.

- `EVALUADO` -> estado de una `SwapRequest` luego de pasar por evaluacion formal.

- `APROBADO` -> estado de una `SwapRequest` resuelta favorablemente.

- `RECHAZADO` -> estado terminal de una `SwapRequest` resuelta desfavorablemente.

- `CANCELADO` -> estado terminal de una `SwapRequest` cancelada.

- `APLICADO` -> estado final de una `SwapRequest` cuyo swap fue aplicado al roster.

---

# Conceptos tecnicos y operativos

- `clasificacion_tecnica` -> resultado tecnico formal producido por `simulator`.

- `clasificacion_observada` -> clasificacion tecnica observada durante la generacion de una oferta y conservada en `offer_origin`. No reemplaza la clasificacion formal posterior.

- `decision_operativa` -> resultado operativo producido por `swap_service`. No debe confundirse con clasificacion tecnica.

- `decision_sugerida` -> decision operativa propuesta por `swap_service` luego de evaluar formalmente una `SwapRequest`.

- `estado_workflow` -> estado formal de una `SwapRequest`. No debe confundirse con clasificacion tecnica ni decision operativa.

- `evaluacion_formal` -> evaluacion de una `SwapRequest` realizada mediante `swap_service.evaluar_swap_request`.

- `evidencia_observada` -> informacion tecnica preservada desde la oferta original. Sirve para trazabilidad, no para reemplazar evaluacion formal.

- `snapshot` -> captura de contexto tecnico u operativo en un momento determinado.

- `obsolescencia` -> condicion en la que una oferta, request o evaluacion deja de corresponder al roster vigente o a la configuracion vigente.

- `divergencia` -> diferencia entre evidencia observada de una oferta y evaluacion formal posterior. No constituye error automatico.

- `ranking_tecnico` -> ordenamiento posterior a la evaluacion tecnica. Ocurre despues de `simulator`.

- `priorizacion_historica` -> reordenamiento soft posterior al ranking tecnico. No modifica clasificacion, score tecnico ni decision operativa.

---

# Verbos reservados

## Verbos del workflow formal

Estos verbos pertenecen al dominio de `SwapRequest` y `swap_service`:

- `crear`
- `evaluar`
- `resolver`
- `aprobar`
- `rechazar`
- `cancelar`
- `aplicar`

No deben usarse para describir workflow propio de ofertas.

## Verbos permitidos para ofertas

Estos verbos pueden usarse para ofertas:

- `generar`
- `presentar`
- `seleccionar`
- `descartar`
- `convertir_en_request`
- `crear_request_desde_oferta`

La oferta no se aprueba, no se rechaza, no se aplica y no se resuelve.

---

# Reglas de no confusion

- Una `OfertaEvaluada` no es una `SwapRequest`.

- `offer_origin` no es evaluacion formal.

- `clasificacion_observada` no es clasificacion formal.

- `selected_by` no es aprobador.

- `selection_reason` no es motivo de resolucion.

- `candidate_selection` no reemplaza a `simulator`.

- `priorizacion_historica` no modifica clasificacion tecnica.

- `decision_operativa` no es clasificacion tecnica.

- `estado_workflow` no es decision operativa.

- `APROBADO` no significa `BENEFICIOSO`.

- `BENEFICIOSO` no implica aprobacion automatica.

- `EVALUADO` no implica aprobado.

- `APLICADO` no implica reevaluacion.

---

# Fachadas

- `crear_request_desde_oferta_y_evaluar_formalmente` -> fachada de alto nivel que crea una `SwapRequest` formal desde una oferta seleccionada y luego invoca evaluacion formal mediante `swap_service.evaluar_swap_request`. No aprueba, no rechaza, no cancela y no aplica.

---

# Frases canonicas

- La oferta evaluada no constituye una solicitud operativa.

- La solicitud operativa nace exclusivamente como `SwapRequest` formal.

- `offer_origin` es evidencia observada, no evaluacion formal.

- La evaluacion formal de una request pertenece a `swap_service`.

- La fachada puede encadenar creacion y evaluacion formal, pero no puede resolver ni aplicar.

- La clasificacion tecnica no equivale a decision operativa.

- La decision operativa no equivale a estado del workflow.

- La request creada desde oferta nace `PENDIENTE`.

- La transicion valida de la fachada es `PENDIENTE -> EVALUADO`.

- La aplicacion del swap sigue siendo una operacion posterior, formal y separada.