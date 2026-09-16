import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools.generar_documentacion import (
    DocumentationError, OUTPUTS, SECTIONS, build_outputs, generate, main, parse_map,
)


def entry(path, source=None):
    return dict(ruta=path, tipo='derivado' if source else 'canonico', estado='pendiente',
                fuentes=[source] if source else [], dependencias=[source] if source else [],
                revisar_cuando=['Cambio de fuente'], modo_actual='generado' if source else 'manual',
                ultima_revision='v117', accion_pendiente='Revisar')


def serialize(entries):
    text = 'version_esquema: 1\nreglas:\n  - "No editar derivados"\ndocumentos:\n'
    for e in entries:
        for i, (k, v) in enumerate(e.items()):
            text += ('  - ' if i == 0 else '    ') + k + ': ' + json.dumps(v, ensure_ascii=False) + '\n'
    return text


class DocumentationGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        self.state = self.root / 'docs/estado_actual.md'
        self.mapping = self.root / 'docs/mapa_documental.yml'
        self.state.write_text('# Estado\n\n' + '\n'.join('## '+s+'\n\nContenido '+s+'\n' for s in SECTIONS))
        self.entries = [entry('docs/estado_actual.md'), entry('docs/mapa_documental.yml'),
                        entry(OUTPUTS[0], 'docs/estado_actual.md'), entry(OUTPUTS[1], 'docs/mapa_documental.yml')]
        self.save_map()

    def save_map(self):
        self.mapping.write_text(serialize(self.entries), encoding='utf-8')

    def test_check_missing_outputs_is_read_only(self):
        self.assertEqual(list(OUTPUTS), generate(self.root, check=True))
        self.assertFalse((self.root / OUTPUTS[0]).exists())
        self.assertFalse((self.root / OUTPUTS[1]).exists())

    def test_generate_is_deterministic_and_idempotent(self):
        self.assertEqual(list(OUTPUTS), generate(self.root, check=False))
        before = {p: ((self.root/p).read_bytes(), (self.root/p).stat().st_mtime_ns) for p in OUTPUTS}
        self.assertEqual([], generate(self.root, check=False))
        self.assertEqual([], generate(self.root, check=True))
        self.assertEqual(before, {p: ((self.root/p).read_bytes(), (self.root/p).stat().st_mtime_ns) for p in OUTPUTS})

    def test_source_change_marks_summary_stale(self):
        generate(self.root, check=False)
        self.state.write_text(self.state.read_text()+'\nNota nueva\n')
        self.assertEqual([OUTPUTS[0]], generate(self.root, check=True))

    def test_map_change_marks_control_stale(self):
        generate(self.root, check=False)
        self.entries[0]['estado'] = 'revisado'
        self.save_map()
        self.assertEqual([OUTPUTS[1]], generate(self.root, check=True))

    def test_manual_edit_is_detected_without_overwrite_in_check(self):
        generate(self.root, check=False)
        target = self.root/OUTPUTS[0]
        target.write_text('edicion manual\n')
        self.assertEqual([OUTPUTS[0]], generate(self.root, check=True))
        self.assertEqual('edicion manual\n', target.read_text())

    def test_lf_crlf_and_bom_are_equivalent(self):
        generate(self.root, check=False)
        for path in (self.state, self.mapping, *(self.root/p for p in OUTPUTS)):
            path.write_bytes(b'\xef\xbb\xbf'+path.read_text(encoding='utf-8-sig').replace('\n', '\r\n').encode('utf-8'))
        self.assertEqual([], generate(self.root, check=True))

    def test_complete_selected_sections_preserve_limits_and_test_provenance(self):
        self.state.write_text(self.state.read_text().replace('Contenido Validacion', '489 passed, 1 skipped; evidencia anterior, no nueva suite'))
        outputs = build_outputs(self.root)
        self.assertIn('489 passed, 1 skipped; evidencia anterior, no nueva suite', outputs[OUTPUTS[0]])
        self.assertIn('Contenido Limites y deuda funcional', outputs[OUTPUTS[0]])

    def test_missing_section_prevents_all_writes(self):
        self.state.write_text('# Incompleto\n')
        with self.assertRaises(DocumentationError):
            generate(self.root, check=False)
        self.assertFalse((self.root/OUTPUTS[1]).exists())

    def test_duplicate_section_is_rejected(self):
        self.state.write_text(self.state.read_text()+'\n## Validacion\nOtra\n')
        with self.assertRaises(DocumentationError):
            generate(self.root, check=False)

    def test_headings_inside_code_fences_do_not_replace_sections(self):
        self.state.write_text(self.state.read_text()+'\n```text\n## Validacion\nEjemplo\n```\n')
        self.assertIn('## Validacion\nEjemplo', build_outputs(self.root)[OUTPUTS[0]])

    def test_unclosed_fence_is_rejected(self):
        self.state.write_text(self.state.read_text()+'\n```text\n')
        with self.assertRaises(DocumentationError):
            build_outputs(self.root)

    def test_duplicate_paths_are_rejected(self):
        self.entries.append(self.entries[0].copy())
        self.save_map()
        with self.assertRaises(DocumentationError):
            build_outputs(self.root)

    def test_duplicate_root_key_is_rejected(self):
        with self.assertRaises(DocumentationError):
            parse_map(self.mapping.read_text()+'\nversion_esquema: 1\n')

    def test_unsupported_yaml_is_rejected(self):
        with self.assertRaises(DocumentationError):
            parse_map(self.mapping.read_text().replace('estado: "pendiente"', 'estado: |\n      multilinea', 1))

    def test_invalid_schema_field_type_is_rejected(self):
        self.entries[0]['dependencias'] = 'incorrecto'
        self.save_map()
        with self.assertRaises(DocumentationError):
            build_outputs(self.root)

    def test_missing_referenced_document_is_rejected(self):
        self.entries[0]['dependencias'] = ['docs/ausente.md']
        self.save_map()
        with self.assertRaises(DocumentationError):
            generate(self.root, check=False)

    def test_dependency_traversal_is_rejected(self):
        self.entries[0]['dependencias'] = ['../outside.md']
        self.save_map()
        with self.assertRaises(DocumentationError):
            build_outputs(self.root)

    def test_source_declarations_must_match_generator(self):
        self.entries[2]['fuentes'] = ['docs/contexto_sistema.md']
        self.save_map()
        with self.assertRaises(DocumentationError):
            build_outputs(self.root)

    def test_table_escapes_pipes_and_multiline_values(self):
        self.entries[0]['accion_pendiente'] = 'Uno | dos\ntres'
        self.save_map()
        self.assertIn('Uno &#124; dos tres', build_outputs(self.root)[OUTPUTS[1]])

    def test_repository_derivatives_are_current(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual([], generate(root, check=True))

    def test_cli_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, main(['--root', str(self.root), '--check']))
            self.assertEqual(0, main(['--root', str(self.root), '--write']))
            self.assertEqual(0, main(['--root', str(self.root), '--check']))
            self.mapping.unlink()
            self.assertEqual(2, main(['--root', str(self.root), '--check']))


if __name__ == '__main__':
    unittest.main()
