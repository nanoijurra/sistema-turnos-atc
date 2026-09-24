# Sistema de cambios de turnos ATC

## Tabla de contenido

- [Alcance](#alcance)
- [Preparacion local](#preparacion-local)
- [Validacion](#validacion)
- [Documentacion](#documentacion)
- [Mantenimiento](#mantenimiento)

---

## Alcance

Proyecto Python para importar rosters, explorar y simular cambios, y gestionar
solicitudes mediante evaluacion, resolucion y aplicacion sobre versiones de roster.
Incluye un diagnostico calendar-aware paralelo y reportes de meses independientes.

El diagnostico no aprueba cambios operativos. Persisten diferencias entre requisitos
operativos y reglas implementadas, incluida la continuidad entre meses. En v119 se unifica el descanso
predeterminado en 16 horas; esto no verifica por si solo las demas reglas. Consultar los limites en [estado actual](docs/estado_actual.md) antes
de interpretar resultados. La documentacion completada no habilita uso decisorio.

## Preparacion local

Entorno de referencia del usuario: Windows, PowerShell y Python 3.14.
Desde la raiz de una copia del repositorio:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

requirements.txt esta versionado en UTF-16. Si pip rechaza su codificacion,
crear una copia UTF-8 temporal para instalar sin modificar el archivo versionado:

```powershell
$requisitosATC = Join-Path $env:TEMP ("atc_requirements_" + [guid]::NewGuid().ToString("N") + ".txt")
try {
    $contenidoATC = [System.IO.File]::ReadAllText((Join-Path (Get-Location) 'requirements.txt'))
    [System.IO.File]::WriteAllText($requisitosATC, $contenidoATC, [System.Text.UTF8Encoding]::new($false))
    .\.venv\Scripts\python.exe -m pip install -r $requisitosATC
} finally {
    Remove-Item -LiteralPath $requisitosATC -ErrorAction SilentlyContinue
}
```

Esta secuencia prepara el entorno; no demuestra portabilidad a todas las versiones
ni una instalacion limpia verificada. Hay bases SQLite versionadas y algunos imports
inicializan tablas. Ejecutar pruebas y demos en una copia de trabajo destinada a
validacion, no sobre datos operativos. Estas deudas siguen abiertas.

## Validacion

Desde la raiz, usando el interprete del entorno preparado:

```powershell
.\.venv\Scripts\python.exe tools/generar_documentacion.py --check
.\.venv\Scripts\python.exe -m src.semantic_guard.lint_runner
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

Verificar el codigo de salida de cada comando antes de continuar. Un lint sin
infracciones solo acredita su alcance declarado. La suite puede omitir la prueba
de symlinks si Windows no permite crearlos. Resultados y base de cada ejecucion
se registran en estado_actual y checkpoints, sin duplicar cifras aqui.

## Documentacion

- [Estado actual y deuda funcional](docs/estado_actual.md): punto de entrada al retomar.
- [Contexto resumido](docs/contexto_resumen.md): derivado del estado actual.
- [Arquitectura](docs/contexto_sistema.md).
- [Contratos](docs/contratos.md), [decisiones](docs/decisiones.md) e [invariantes](docs/invariantes.md).
- [Modelo de dominio](docs/modelo_dominio.md) y [diccionario](docs/diccionario.md).
- [Mapa documental](docs/mapa_documental.yml) y [estado documental generado](docs/estado_docs.md).
- [Generacion documental](docs/generacion_documental.md) y [semantic guard](docs/semantic_guard.md).
- [Checkpoints activos](checkpoints.md) e [indice historico](docs/hitos/indice_checkpoints_v1_v95.md).
- [Cierre documental v118](docs/hitos/cierre_documental_v118.md): alcance, evidencia y pendientes.

## Mantenimiento

Editar las fuentes manuales; no editar contexto_resumen ni estado_docs directamente.
Despues de cambiar estado_actual o mapa_documental, ejecutar:

```powershell
.\.venv\Scripts\python.exe tools/generar_documentacion.py --write
.\.venv\Scripts\python.exe tools/generar_documentacion.py --check
```

Mantener las evidencias historicas. contratos_resumen fue retirado en v118;
los contratos vigentes se consultan en docs/contratos.md y su copia anterior es
recuperable en el tag checkpoint-v117-generacion-documentos-derivados.
