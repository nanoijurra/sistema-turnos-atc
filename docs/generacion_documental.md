# Generacion documental

## Fuentes y salidas

| Salida | Fuente de contenido | Transformacion |
| --- | --- | --- |
| docs/contexto_resumen.md | docs/estado_actual.md | Secciones completas de base, capacidades, limites y validacion |
| docs/estado_docs.md | docs/mapa_documental.yml | Tabla ordenada de tipo, estado, modo, revision y accion pendiente |

El generador no resume mediante interpretacion, no inventa resultados ni modifica
canonicos. Los derivados se regeneran; no se editan a mano. Las fuentes manuales
siguen necesitando revision humana. Una tabla generada no certifica su contenido.

## Comandos

Desde cualquier directorio, indicar la ruta al script. La raiz por defecto se
obtiene desde su ubicacion dentro del proyecto, no desde el directorio de trabajo.

```powershell
py tools/generar_documentacion.py --write
py tools/generar_documentacion.py --check
$LASTEXITCODE
```

--write valida ambas fuentes antes de escribir y reemplaza cada salida mediante
un archivo temporal. No hay transaccion conjunta entre dos archivos: si un fallo
de disco interrumpe el segundo reemplazo, corregir el fallo y volver a generar.
Una salida ya sincronizada no se reescribe ni cambia su fecha de modificacion.

--check no escribe, no crea salidas ni carpetas. Retorna:

- 0: las dos salidas coinciden con fuentes y generador.
- 1: alguna salida falta o esta desactualizada.
- 2: fuente ausente/invalida, esquema no soportado o error de lectura/escritura.

Los modos --check y --write son obligatorios y mutuamente excluyentes.
--root permite indicar otra raiz. No se permite escapar de ella mediante rutas
documentales, dependencias o enlaces simbolicos a archivos externos.

## Perfil del mapa YAML

No se agregan dependencias a requirements.txt. El lector acepta exclusivamente
el perfil YAML ya utilizado en este mapa; no pretende interpretar YAML general.

- Raiz: claves sin sangria, escalares de una linea y bloques reglas/documentos.
- reglas: lista de cadenas con dos espacios y guion.
- documentos: entradas iniciadas por ruta; campos con cuatro espacios.
- Valores: literales JSON (cadenas con comillas dobles, listas en linea, booleanos,
  numeros) o identificadores simples como v117 en campos de cabecera.
- Cada documento requiere ruta, tipo, estado, fuentes, dependencias, revisar_cuando,
  modo_actual, ultima_revision y accion_pendiente.
- No admite anchors, aliases, bloques multilinea, listas anidadas en bloque ni
  comentarios al final de valores. Rechaza sintaxis no soportada con error explicito.

El esquema exige rutas unicas, tipos correctos y dependencias existentes. Las dos
salidas pueden faltar para permitir su primera generacion. El mapa debe declararlas
como tipo derivado, modo generado y con sus fuentes/dependencias exactas.

## Reproducibilidad

Cada salida incluye huella SHA256 del texto de su fuente y del generador.
No hay fecha de ejecucion automatica ni rutas absolutas dentro del contenido.
UTF-8 con/sin BOM y LF/CRLF se normalizan para evitar diferencias entre Windows y
Linux. Cualquier otra alteracion de fuente, generador o salida exige regeneracion.
Los enlaces relativos del resumen siguen funcionando porque permanece en docs/.

Se preservan integramente las secciones seleccionadas, incluyendo limites y
procedencia de tests. Se rechazan secciones duplicadas, vacias o ausentes y fences
sin cerrar. Los titulos dentro de fences no se interpretan como secciones.

## Verificacion y cierre

```powershell
py -m unittest discover -s tests -p test_generar_documentacion.py -v
py -m pytest -q
py -m src.semantic_guard.lint_runner
py tools/generar_documentacion.py --check
```

El test de integridad de derivados se incluye en la suite: una fuente manual
modificada sin regenerar provoca un fallo. Al registrar resultados nuevos de la
suite en estado_actual, ejecutar --write y --check antes de preparar el commit.
No hace falta repetir la suite completa si solo se transcribe ese resultado;
si cambia codigo o comportamiento, corresponde verificar nuevamente.

El lint y este generador son controles complementarios. El generador no demuestra
cumplimiento normativo, no resuelve deuda funcional ni corrige semantic diff.
