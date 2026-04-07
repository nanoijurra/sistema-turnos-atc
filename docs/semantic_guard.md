clear# Semantic guard

## Tabla de contenido

- [1. Proposito](#1-proposito)
- [2. Alcance](#2-alcance)
- [3. Objetivo del sistema](#3-objetivo-del-sistema)
- [4. Componentes](#4-componentes)
  - [4.1 Semantic lint](#41-semantic-lint)
  - [4.2 Semantic diff](#42-semantic-diff)
- [5. Estructura actual](#5-estructura-actual)
- [6. Reglas activas](#6-reglas-activas)
- [7. Uso operativo](#7-uso-operativo)
- [8. Alcance documental actual](#8-alcance-documental-actual)
- [9. Criterios de extension](#9-criterios-de-extension)
- [10. Restricciones](#10-restricciones)
- [11. Evolucion futura](#11-evolucion-futura)

---

## 1. Proposito

Definir el propósito, alcance y modo de uso del subsistema `semantic_guard`.

Este subsistema protege la coherencia semántica del sistema de swaps ATC mediante verificaciones automáticas sobre documentación y evolución de conceptos críticos.

---

## 2. Alcance

Este documento define:

- qué es `semantic_guard`
- qué controles realiza
- cómo se ejecuta
- qué alcance tiene hoy
- cómo debe evolucionar

No define:

- contratos funcionales del sistema principal
- reglas del dominio del swap
- implementación del flujo operativo principal

Ver también:

- [Ref: diccionario.md]
- [Ref: invariantes.md]
- [Ref: decisiones.md]
- [Ref: contratos.md]

---

## 3. Objetivo del sistema

`semantic_guard` existe para reducir drift semántico en el proyecto.

Su objetivo es detectar, antes de consolidar cambios:

- ambigüedades terminológicas
- mezcla indebida de planos conceptuales
- reaparición de términos legados
- pérdida de taxonomías críticas
- degradación de documentos rectores

Opera como capa de protección sobre:

- documentación
- evolución documental
- reglas semánticas mínimas del sistema

---

## 4. Componentes

### 4.1 Semantic lint

Verifica el estado actual del proyecto.

Responde a la pregunta:

**¿La semántica actual del sistema viola alguna regla conocida?**

Detecta, por ejemplo:

- uso de términos ambiguos en documentación
- violaciones activas de reglas semánticas
- contaminación semántica en archivos vigilados

#### Comando

bash
python -m src.semantic_guard.lint_runner

### 4.2  Semantic diff

Compara dos versiones de un documento para detectar drift semántico.

Responde a la pregunta:

¿Este cambio introdujo una degradacion conceptual respecto de la version anterior?

Detecta, por ejemplo:

pérdida de taxonomías
reaparición de términos prohibidos
cambios peligrosos en vocabulario rector
Comando
python -m src.semantic_guard.diff_runner

## 5. Estructura actual

La estructura actual del subsistema es:

src/
└── semantic_guard/
    ├── __init__.py
    ├── lint_rules.py
    ├── lint_runner.py
    ├── extractor.py
    ├── diff_rules.py
    └── diff_runner.py


## 6. Reglas activas

### Las reglas activas deben ser:

pocas
explícitas
justificadas por problemas reales
estables en el tiempo
Reglas de semantic lint

Incluyen, entre otras:

deteccion de ambiguedad terminologica en documentacion semantica
exclusión de archivos no semánticos o de control de proceso

Ejemplo:

estado_docs.md
Reglas de semantic diff

Incluyen, entre otras:

detección de pérdida de taxonomías críticas
detección de reaparición de términos legados
vigilancia de vocabulario estructural del sistema

### Regla de preservacion de taxonomia oficial

semantic_guard debe vigilar explicitamente la preservacion de la taxonomia oficial del sistema.

Incluye:

- clasificacion tecnica:
  - BENEFICIOSO
  - ACEPTABLE
  - RECHAZABLE

- decision operativa:
  - VIABLE
  - OBSERVAR
  - RECHAZAR

- estados del workflow:
  - PENDIENTE
  - EVALUADO
  - APROBADO
  - RECHAZADO
  - CANCELADO
  - APLICADO

Regla:

- no deben aparecer sinonimos o variantes para estos conceptos
- no deben mezclarse entre si los planos tecnico, operativo y de workflow
- no deben reintroducirse terminos eliminados como:
  - APROBABLE
  - ACEPTADO
  - reaparicion de terminologia ambigua

Motivo:

Estas taxonomias constituyen el lenguaje ubicuo del sistema y su alteracion implica drift semantico critico.

## 7. Uso operativo
### 7.1 Uso minimo recomendado

Antes de consolidar cambios en documentos rectores, ejecutar:

python -m src.semantic_guard.lint_runner
python -m src.semantic_guard.diff_runner
### 7.2 Cuando usar semantic lint

Usar semantic lint cuando:

se modifica documentación en docs/
se ajusta semántica del sistema
se reorganizan conceptos críticos
se quiere verificar el estado actual del corpus documental
7.3 Cuando usar semantic diff

Usar semantic diff cuando:

se reescribe un documento rector
se compara una versión previa contra una nueva
se revisa si un cambio introdujo drift conceptual

## 8. Alcance documental actual

Hoy semantic_guard vigila prioritariamente documentos semánticos en docs/.

Documentos objetivo
invariantes.md
modelo_dominio.md
decisiones.md
contratos.md
diccionario.md
Exclusiones

No todos los .md deben ser tratados como documentos semánticos.

Archivos de control de proceso o seguimiento operativo pueden excluirse explícitamente.

Ejemplo:

estado_docs.md
## 9. Criterios de extension

Toda nueva regla del sistema debe cumplir estas condiciones:

resolver una ambigüedad real ya observada
no introducir ruido innecesario
no duplicar otra regla existente
poder explicarse con claridad
no depender de interpretaciones frágiles
Regla de diseño

semantic_guard no debe crecer por entusiasmo, sino por necesidad real.

## 10. Restricciones

semantic_guard no debe:

redefinir semántica del sistema por sí mismo
convertirse en fuente de verdad del dominio
reemplazar la lectura crítica humana
introducir reglas arbitrarias sin justificación documental

Su rol es:

vigilar
alertar
proteger coherencia

No diseñar el sistema principal.

## 11. Evolucion futura

Posibles extensiones:

integración con pytest
integración con pre-commit
comparación automática contra ramas o snapshots
reglas semánticas sobre código
cobertura semántica de documentación
detección automática de referencias cruzadas rotas

Toda evolución debe preservar:

simplicidad
trazabilidad
bajo ruido
utilidad real