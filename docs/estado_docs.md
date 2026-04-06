Estado de documentación
1. Versión conceptual del sistema
estado: estable / en evolución / refactor activo
última revisión arquitectónica: (fecha o tag)
2. Estado de documentos

decisiones.md:

última sección: 26
estado: consistente / requiere revisión

contratos.md:

última sección: 16
estado: consistente / en ajuste

invariantes.md:

versión reorganizada: ✔
estado: consistente

modelo_dominio.md:

versión reorganizada: ✔
estado: consistente

contexto_sistema.md:

estado: base estable
3. Decisiones recientes relevantes
definición formal del swap:
→ intercambio de turno/actividad entre asignaciones
frontera pública de simulator:
→ solo evaluación técnica
clasificación técnica:
→ permanece en simulator, sin lógica operativa
separación de presentación:
→ fuera del núcleo de simulator (deuda pendiente)
comparación técnica:
→ evitar dependencia de RosterVersion ficticio (deuda)
4. Deudas arquitectónicas identificadas
wrappers operativos en simulator (transitorio)
generar_recomendacion_textual en simulator (sacar a futuro)
impacto_por_controlador acoplado a RosterVersion
5. Términos críticos (semántica fija)
clasificación técnica ≠ decisión operativa
request válido = versión vigente
swap = intercambio de turno entre asignaciones
asignación = unidad operativa (no índice)
engine = única fuente de reglas
simulator = evaluación técnica
swap_service = decisión y workflow
6. Checklist previo a tag

### Antes de crear un tag:

Tests en verde

Auditoría de coherencia documental realizada

No hay contradicciones entre:

decisiones.md
contratos.md
invariantes.md
modelo_dominio.md

Decisiones nuevas reflejadas en todos los documentos relevantes

### importante
La clasificación técnica, la decisión operativa y el estado del workflow representan planos distintos del sistema y no deben confundirse ni colapsarse.

# Reglas de oro 

Si dos términos:
suenan parecido
viven en capas distintas
y pueden leerse como sinónimos
👉 uno de los dos está mal elegido

Concepto	                    Valores	                      Responsable
clasificación técnica	BENEFICIOSO / ACEPTABLE / RECHAZABLE	simulator
decisión operativa	VIABLE / OBSERVAR / RECHAZAR	          swap_service
estado	PENDIENTE / EVALUADO / APROBADO / ...	                 workflow