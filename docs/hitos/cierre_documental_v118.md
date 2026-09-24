# Cierre documental v118

## Base y alcance

Base exportada: tag checkpoint-v117-generacion-documentos-derivados.
Commit confirmado por salida del usuario: 6db14e9. V117 cerrado y publicado.
V118 completa la etapa documental prevista por la auditoria v111; no certifica
cumplimiento de reglas ATC ni ausencia de toda contradiccion posible.

## Seguimiento del plan

| Etapa | Resultado registrado | Limite |
| --- | --- | --- |
| v111 | Auditoria contra v110 | Diagnostico historico, no estado actual |
| v112 | Registro activo desde v96 e indice v1-v95 | Anomalias historicas conservadas como evidencia |
| v113 | Estado vigente y mapa documental | Clasificar no valida contenido |
| v114 | Reparacion estructural de canonicos | No modifica comportamiento |
| v115 | Conciliacion funcional contra codigo | Deuda de reglas permanece abierta |
| v116 | Reparacion del lint y regresiones | Semantic diff mantiene limitaciones |
| v117 | Generador y control de sincronizacion | Fuentes manuales requieren revision |
| v118 | README, retiro del resumen obsoleto y revision final | Validacion Windows confirmada; cierre Git pendiente |

## Cambios y retiro

README incorpora preparacion local, comandos, limites y navegacion.
Se elimina docs/contratos_resumen.md y su entrada del mapa; docs/contratos.md
es la referencia vigente. La version retirada se conserva en el tag v117.
Para recuperarla sin imprimirla completa en la terminal:

```powershell
git archive --format=zip --output=../contratos_resumen_v117.zip checkpoint-v117-generacion-documentos-derivados docs/contratos_resumen.md
```

Las menciones en auditorias y checkpoints son historicas y se conservan.
La exclusion del nombre en semantic_guard y su fixture de regresion siguen
siendo comportamiento defensivo valido; no son enlaces a un archivo requerido.
No se cambia src/, tests/, tools/, configuracion, requirements ni bases SQLite.

Archivos del cambio: README.md, checkpoints.md, docs/estado_actual.md,
docs/mapa_documental.yml, docs/contexto_resumen.md, docs/estado_docs.md,
este informe y la eliminacion de docs/contratos_resumen.md.

## Validacion y evidencia

Controles ejecutados en preparacion:

- Inventario: 19 rutas declaradas, sin archivos documentales faltantes o sobrantes.
- Doce documentos Markdown vigentes: un titulo principal, fences cerrados,
  enlaces relativos y anclas comprobados sin errores.
- Checkpoints v96-v118 unicos y ordenados; bloques v96-v117 identicos a la base.
- Generador: 21 pruebas unittest aprobadas; dos derivados sincronizados.
- Semantic lint: 57 archivos analizados, 6 excluidos, cero infracciones, salida 0.
- Comparacion con ZIP base: siete archivos nuevos/modificados y una eliminacion;
  sin cambios fuera del alcance. Control de whitespace del diff sin errores.

Los documentos historicos se preservan; sus formatos y referencias anteriores
no se reinterpretan como documentacion vigente. Estos controles estructurales
no acreditan exactitud semantica completa ni pruebas operativas.

Suite de base v117: 510 passed, 1 skipped en 7.68 s.
Validacion v118 en Windows confirmada por el usuario:
- Suite completa: 510 passed, 1 skipped en 7.23 s.
- Generador: dos derivados sincronizados, salida 0.
- Semantic lint: 57 analizados, 6 excluidos, sin infracciones, salida 0.
- Git diff --check sin errores.
Cotejo final del diff preparado y cierre Git pendientes.

## Deuda que sigue abierta

- Continuidad entre meses: el agregado multimes procesa meses independientes.
- Descanso: defaults y comparadores distintos; min_horas no coincide con horas_minimas.
- Ventana configurada de 12 horas y cobertura no acreditada de 18 turnos/144 horas
  y maximo universal de jornadas mixtas: requieren decision y pruebas funcionales.
- Diagnostico y aptitud para revision no equivalen a aprobacion operativa.
- Imports con efectos SQLite, bases versionadas y requirements UTF-16.
- Semantic diff y validacion integral de significado no resueltos por lint.
- Preparacion de entorno documentada; instalacion limpia no ensayada aqui.

La simulacion v119 sigue siendo una propuesta. Antes de un uso decisorio debe
priorizarse la conciliacion de reglas y limites identificados. La etapa documental
puede cerrarse sin declarar resuelta esa deuda funcional.
