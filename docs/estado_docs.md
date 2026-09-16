# Estado de documentacion

Generado por `tools/generar_documentacion.py`. No editar manualmente.

Fuente: [mapa_documental.yml](mapa_documental.yml).

<!-- fuente-sha256: bc688a0229d529e2dd5511a88332fe29ae3896a6107dc9c441a4103ff7a7b2c2; generador-sha256: a191210826215580dcff5d40a16452a81e5ec843d7e5ba66f4d9856ee503ca9e -->

Los estados se transcriben del mapa; generar esta tabla no certifica vigencia ni repara documentos.

Documentos registrados: 19.

| Documento | Tipo | Estado | Modo | Ultima revision | Accion pendiente |
| --- | --- | --- | --- | --- | --- |
| README.md | entrada | vacio_segun_auditoria | manual | v111: auditado, no reparado | Completar como entrada estable; no duplicar estado |
| checkpoints.md | historia_activa | revision_v117_cierre_pendiente | manual | v117: generacion sistematica, cierre Git pendiente | Registrar validacion y cierre v117; regenerar derivados al cambiar fuentes |
| docs/contexto_resumen.md | derivado | generado_desde_fuente_declarada | generado | v117: generacion sistematica, cierre Git pendiente | Regenerar ante cambios de fuente y ejecutar --check |
| docs/contexto_sistema.md | canonico | revisado_v115 | manual | v115: conciliacion documental contra base v114 | Mantener arquitectura y limites segun codigo; deuda funcional no resuelta por documentacion |
| docs/contratos.md | canonico | revisado_v115 | manual | v115: conciliacion documental contra base v114 | Mantener Contratos 26/27; no presentar diagnostico como aprobacion |
| docs/contratos_resumen.md | redundante_obsoleto | no_vigente_retiro_material_pendiente | manual | v111: retiro como vigente aprobado | Retirar materialmente en checkpoint documental posterior |
| docs/decisiones.md | canonico | revisado_v115 | manual | v115: conciliacion documental contra base v114 | Conservar Decision 54 descriptiva; resolver deuda funcional con decision explicita |
| docs/diccionario.md | canonico | revisado_v115 | manual | v115: conciliacion documental contra base v114 | Mantener terminos de reporte, multimes y normalizaciones conforme a codigo |
| docs/estado_actual.md | estado_vigente | revision_v117_cierre_pendiente | manual | v117: generacion sistematica, cierre Git pendiente | Registrar validacion y cierre v117; regenerar derivados al cambiar fuentes |
| docs/estado_docs.md | derivado | generado_desde_fuente_declarada | generado | v117: generacion sistematica, cierre Git pendiente | Regenerar ante cambios de fuente y ejecutar --check |
| docs/generacion_documental.md | tecnico | revision_v117_cierre_pendiente | manual | v117: creado | Mantener contrato del generador y registrar cierre |
| docs/hitos/auditoria_documental_v110.md | historico | cerrado | manual | v111: incorporado | Conservar como evidencia |
| docs/hitos/cierre_ambiguedad_semantica.md | historico | cerrado | manual | v111: clasificado historico | Conservar; sin actualizacion continua |
| docs/hitos/conciliacion_funcional_v115.md | historico | revision_v115_cerrada | manual | v115: creado | V115 cerrado; tratar deuda funcional mediante alcance explicito |
| docs/hitos/indice_checkpoints_v1_v95.md | indice_historico | incorporado_v112 | manual | v112: creado | Mantener limites probatorios; cotejo con Git confirmado en v112 |
| docs/invariantes.md | canonico | revisado_v115 | manual | v115: conciliacion documental contra base v114 | Mantener CA-7/8/9 y limites; conciliar reglas en checkpoint funcional |
| docs/mapa_documental.yml | registro_documental | revision_v117_cierre_pendiente | manual | v117: generacion sistematica, cierre Git pendiente | Registrar validacion y cierre v117; regenerar derivados al cambiar fuentes |
| docs/modelo_dominio.md | canonico | revisado_v115 | manual | v115: conciliacion documental contra base v114 | Entrenamiento conciliado para ACC; mantener distincion dataclass y frontera de importacion |
| docs/semantic_guard.md | tecnico | revisado_v116 | manual | v116 cerrado: suite local 489 passed, 1 skipped | Mantener especificacion y regresiones del lint; semantic diff no reparado en v116 |

Fuentes, dependencias y disparadores completos: consultar el mapa.
