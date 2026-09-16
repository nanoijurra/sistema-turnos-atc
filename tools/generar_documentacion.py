"""Reproducible derived Markdown. Restricted YAML profile; standard library only."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile

SECTIONS = ('Base confirmada', 'Capacidades verificadas', 'Limites y deuda funcional', 'Validacion')
OUTPUTS = ('docs/contexto_resumen.md', 'docs/estado_docs.md')
FIELDS = {'ruta', 'tipo', 'estado', 'fuentes', 'dependencias', 'revisar_cuando', 'modo_actual', 'ultima_revision', 'accion_pendiente'}

class DocumentationError(ValueError):
    pass

def normalize(text):
    return text.removeprefix('\ufeff').replace('\r\n', '\n').replace('\r', '\n')

def read(path):
    return normalize(path.read_text(encoding='utf-8-sig'))

def digest(text):
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()

def scalar(raw, line):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', raw):
            return raw
        raise DocumentationError(f'Mapa linea {line}: escalar YAML no soportado') from None

def parse_map(text):
    data, section, entry = {}, None, None
    for number, line in enumerate(normalize(text).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        top = re.fullmatch(r'([a-z][a-z0-9_]*):(?: (.+))?', line)
        if top:
            key, raw = top.groups()
            if key in data:
                raise DocumentationError(f'Clave duplicada: {key}')
            if raw is None:
                if key not in ('reglas', 'documentos'):
                    raise DocumentationError(f'Bloque no soportado: {key}')
                data[key], section = [], key
            else:
                data[key], section = scalar(raw, number), None
            entry = None
            continue
        if section == 'reglas' and line.startswith('  - '):
            value = scalar(line[4:], number)
            if not isinstance(value, str):
                raise DocumentationError('Regla debe ser texto')
            data[section].append(value)
            continue
        if section == 'documentos':
            first = re.fullmatch(r'  - ruta: (.+)', line)
            field = re.fullmatch(r'    ([a-z][a-z0-9_]*): (.+)', line)
            if first:
                entry = {'ruta': scalar(first[1], number)}
                data[section].append(entry)
                continue
            if field and entry is not None:
                key, raw = field.groups()
                if key in entry:
                    raise DocumentationError(f'Campo duplicado: {key}')
                entry[key] = scalar(raw, number)
                continue
        raise DocumentationError(f'Mapa linea {number}: sintaxis YAML no soportada')
    if type(data.get('version_esquema')) is not int or data['version_esquema'] != 1:
        raise DocumentationError('version_esquema debe ser 1')
    if not isinstance(data.get('reglas'), list) or not isinstance(data.get('documentos'), list) or not data['documentos']:
        raise DocumentationError('Mapa sin reglas/documentos validos')
    seen = set()
    for entry in data['documentos']:
        if set(entry) != FIELDS:
            raise DocumentationError('Campos documentales faltantes o no soportados')
        for key, value in entry.items():
            if key in ('fuentes', 'dependencias', 'revisar_cuando'):
                valid = isinstance(value, list) and all(isinstance(x, str) and x for x in value)
            else:
                valid = isinstance(value, str) and bool(value)
            if not valid:
                raise DocumentationError(f'Tipo invalido: {key}')
        if entry['ruta'] in seen:
            raise DocumentationError('Ruta documental duplicada')
        seen.add(entry['ruta'])
    return data

def safe_path(root, relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or '\\' in relative or ':' in relative or rel.as_posix() != relative:
        raise DocumentationError(f'Ruta no admitida: {relative}')
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise DocumentationError(f'Ruta fuera del repositorio: {relative}')
    return path

def sections(text):
    result, current, buffer, fence = {}, None, [], None
    for line in normalize(text).splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        if fence is None and line.startswith('## '):
            if current is not None:
                result[current] = '\n'.join(buffer).strip()
            current = line[3:].strip()
            if current in result:
                raise DocumentationError(f'Seccion duplicada: {current}')
            buffer = []
        elif current is not None:
            buffer.append(line)
    if fence:
        raise DocumentationError('Fence sin cerrar en estado_actual')
    if current is not None:
        result[current] = '\n'.join(buffer).strip()
    for title in SECTIONS:
        if not result.get(title):
            raise DocumentationError(f'Seccion requerida ausente o vacia: {title}')
    return result

def cell(value):
    return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ')

def build_outputs(root):
    state = read(safe_path(root, 'docs/estado_actual.md'))
    mapping_text = read(safe_path(root, 'docs/mapa_documental.yml'))
    entries = {e['ruta']: e for e in parse_map(mapping_text)['documentos']}
    for target, source in zip(OUTPUTS, ('docs/estado_actual.md', 'docs/mapa_documental.yml')):
        e = entries.get(target)
        if not e or e['tipo'] != 'derivado' or e['modo_actual'] != 'generado':
            raise DocumentationError(f'{target} debe declararse derivado generado')
        if e['fuentes'] != [source] or e['dependencias'] != [source]:
            raise DocumentationError(f'Fuentes/dependencias inesperadas: {target}')
        safe_path(root, target)
    for e in entries.values():
        for relative in [e['ruta'], *e['dependencias']]:
            path = safe_path(root, relative)
            if relative not in OUTPUTS and not path.is_file():
                raise DocumentationError(f'Ruta documental ausente: {relative}')
    blocks = sections(state)
    tool_hash = digest(read(Path(__file__)))
    def header(title, source, content):
        return (f'# {title}\n\nGenerado por `tools/generar_documentacion.py`. No editar manualmente.\n\n'
                f'Fuente: [{source}]({source}).\n\n'
                f'<!-- fuente-sha256: {digest(content)}; generador-sha256: {tool_hash} -->\n')
    summary = header('Contexto resumen', 'estado_actual.md', state)
    summary += '\nSeleccion de secciones completas; no certifica el contenido de la fuente.\n'
    for title in SECTIONS:
        summary += f'\n## {title}\n\n{blocks[title]}\n'
    status = header('Estado de documentacion', 'mapa_documental.yml', mapping_text)
    status += '\nLos estados se transcriben del mapa; generar esta tabla no certifica vigencia ni repara documentos.\n'
    status += f'\nDocumentos registrados: {len(entries)}.\n\n'
    status += '| Documento | Tipo | Estado | Modo | Ultima revision | Accion pendiente |\n| --- | --- | --- | --- | --- | --- |\n'
    for e in sorted(entries.values(), key=lambda e: e['ruta']):
        status += '| ' + ' | '.join(cell(e[k]) for k in ('ruta', 'tipo', 'estado', 'modo_actual', 'ultima_revision', 'accion_pendiente')) + ' |\n'
    status += '\nFuentes, dependencias y disparadores completos: consultar el mapa.\n'
    return dict(zip(OUTPUTS, (summary, status)))

def generate(root, *, check):
    root = root.resolve()
    outputs = build_outputs(root)  # Validate all sources before changing any output.
    stale = [rel for rel, content in outputs.items() if not safe_path(root, rel).exists() or read(safe_path(root, rel)) != content]
    if check:
        return stale
    for rel in stale:
        path = safe_path(root, rel)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(outputs[rel])
        try:
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    return stale

def main(argv=None):
    parser = argparse.ArgumentParser(description='Generar o verificar derivados documentales')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--write', action='store_true')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        stale = generate(args.root, check=args.check)
    except (OSError, UnicodeError, DocumentationError) as error:
        print(f'ERROR: {error}')
        return 2
    if args.check and stale:
        print('DESACTUALIZADOS: ' + ', '.join(stale))
        return 1
    print('Actualizados: ' + str(len(stale)) if args.write else 'OK: 2 derivados sincronizados')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
