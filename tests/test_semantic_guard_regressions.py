"""Regression checks usable with both unittest and pytest, without business DB imports."""
import ast
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.semantic_guard.lint_rules import (
    rule_no_ambiguous_valido,
    rule_no_legacy_audit_event_names,
)
from src.semantic_guard.lint_runner import (
    analyze_python_file, main, run_semantic_lint, run_semantic_lint_report,
)


class SemanticGuardRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('src/base.py', 'x = 1\n')
        self.write('docs/base.md', '# Documento\nEl motor valida reglas.\n')

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def test_every_source_file_and_nested_directory_is_analyzed(self):
        self.write('src/a.py', 'event = "SWAP_APLICADO"\n')
        self.write('src/z.py', 'event = "REQUEST_RESUELTO"\n')
        self.write('src/nested/m.py', 'event = "REQUEST_EVALUADO"\n')
        report = run_semantic_lint_report(self.root)
        violations = [v for v in report.violations if v.rule_id == 'S-05']
        self.assertEqual({'a.py', 'z.py', 'm.py'}, {Path(v.file).name for v in violations})
        self.assertEqual(5, len(report.analyzed_files))

    def test_every_markdown_file_is_analyzed(self):
        self.write('docs/a.md', 'Estado: valido\n')
        self.write('docs/z.md', 'Clasificacion: válida\n')
        self.assertEqual(2, len(run_semantic_lint(self.root)))

    def test_empty_subdirectories_do_not_reuse_previous_file(self):
        (self.root / 'src/empty').mkdir()
        (self.root / 'docs/empty').mkdir()
        report = run_semantic_lint_report(self.root)
        self.assertEqual([], report.violations)
        self.assertEqual(2, len(report.analyzed_files))

    def test_missing_required_directory_is_not_success(self):
        self.assertTrue(all(v.rule_id == 'S-00' for v in run_semantic_lint(self.root / 'missing')))
        self.assertEqual(2, len(run_semantic_lint(self.root / 'missing')))

    def test_existing_but_empty_scope_is_not_success(self):
        (self.root / 'src/base.py').unlink()
        self.assertTrue(any(v.rule_id == 'S-00' for v in run_semantic_lint(self.root)))

    def test_only_explicit_historical_and_retired_docs_are_excluded(self):
        for name in ('docs/hitos/event.md', 'docs/estado_docs.md', 'docs/contratos_resumen.md'):
            self.write(name, 'Estado: valido\n')
        self.write('docs/nested/estado_docs.md', 'Estado: valido\n')
        report = run_semantic_lint_report(self.root)
        self.assertEqual(3, len(report.excluded_files))
        self.assertEqual(1, len(report.violations))
        self.assertIn('nested', report.violations[0].file)

    def test_state_and_current_summary_are_not_excluded(self):
        self.write('docs/estado_actual.md', 'Estado: valido\n')
        self.write('docs/contexto_resumen.md', 'Decision: valido\n')
        self.assertEqual(2, len(run_semantic_lint(self.root)))

    def test_invalid_python_is_reported_and_other_files_continue(self):
        self.write('src/a.py', 'def broken(:\n')
        self.write('src/z.py', 'event = "SWAP_APLICADO"\n')
        ids = {v.rule_id for v in run_semantic_lint(self.root)}
        self.assertEqual({'S-00', 'S-05'}, ids)

    def test_invalid_encoding_is_reported(self):
        (self.root / 'docs/base.md').write_bytes(b'\xff\xfe\x00')
        self.assertEqual('S-00', run_semantic_lint(self.root)[0].rule_id)

    def test_bom_is_supported(self):
        self.write('src/bom.py', '\ufeffevent = "SWAP_APLICADO"\n')
        self.assertEqual('S-05', run_semantic_lint(self.root)[0].rule_id)

    def test_component_rule_is_selected_by_exact_filename(self):
        self.write('src/engine_helper.py', 'decision = "APROBADO"\n')
        self.assertEqual([], run_semantic_lint(self.root))
        self.write('src/engine.py', 'decision = "APROBADO"\n')
        self.assertEqual('S-02', run_semantic_lint(self.root)[0].rule_id)

    def test_simulator_and_swap_service_rules_remain_enabled(self):
        self.write('src/simulator.py', 'decision = "VIABLE"\n')
        self.write('src/swap_service.py', 'delta_score = 4\n')
        self.assertEqual({'S-01', 'S-03'}, {v.rule_id for v in run_semantic_lint(self.root)})

    def test_registry_declaration_does_not_hide_productive_use_in_same_file(self):
        path = self.write('src/semantic_guard/lint_rules.py',
                          'LEGACY_AUDIT_EVENT_NAMES = ("SWAP_APLICADO",)\nevent = "SWAP_APLICADO"\n')
        violations = analyze_python_file(str(path))
        self.assertEqual(1, len(violations))
        self.assertEqual(2, violations[0].lineno)

    def test_same_registry_name_in_other_module_is_not_exempt(self):
        tree = ast.parse('LEGACY_AUDIT_EVENT_NAMES = ("SWAP_APLICADO",)')
        self.assertEqual(1, len(rule_no_legacy_audit_event_names(tree, 'src/other.py')))

    def test_registry_exception_does_not_cover_calls(self):
        tree = ast.parse('LEGACY_AUDIT_EVENT_NAMES = log("SWAP_APLICADO")')
        self.assertEqual(1, len(rule_no_legacy_audit_event_names(tree, 'src/semantic_guard/lint_rules.py')))

    def test_windows_path_registry_is_recognized(self):
        tree = ast.parse('LEGACY_AUDIT_EVENT_NAMES = ("SWAP_APLICADO",)')
        self.assertEqual([], rule_no_legacy_audit_event_names(tree, r'C:\repo\src\semantic_guard\lint_rules.py'))

    def test_normalized_events_and_identifier_prefixes_are_not_legacy(self):
        tree = ast.parse('x = "REQUEST_EVALUADA REQUEST_RESUELTA REQUEST_APLICADA XSWAP_APLICADO SWAP_APLICADO_EXTRA"')
        self.assertEqual([], rule_no_legacy_audit_event_names(tree, 'src/events.py'))

    def test_long_legacy_event_is_reported_once(self):
        tree = ast.parse('x = "REQUEST_EVALUADO_SIN_TECNICA"')
        violations = rule_no_legacy_audit_event_names(tree, 'src/events.py')
        self.assertEqual(1, len(violations))
        self.assertIn('REQUEST_EVALUADO_SIN_TECNICA', violations[0].message)

    def test_legacy_event_inside_fstring_is_detected(self):
        tree = ast.parse('x = f"SWAP_APLICADO: {request_id}"')
        self.assertEqual(1, len(rule_no_legacy_audit_event_names(tree, 'src/events.py')))

    def test_ambiguous_taxonomic_assignments_report_actual_lines(self):
        text = '# Ejemplo\nEstado: válido\nclasificacion tecnica = "valida"\nDecision operativa es valido\n'
        self.assertEqual([2, 3, 4], [v.lineno for v in rule_no_ambiguous_valido(text, 'docs/x.md')])

    def test_legitimate_technical_uses_and_verbs_are_allowed(self):
        text = ('El motor valida reglas.\nUn swap tecnicamente válido puede ser rechazado.\n'
                'valido_sin_hard\nEstado: valido_sin_hard\nClasificacion: ACEPTABLE\n'
                'Version valida por identidad.\n#### Request valido\n')
        self.assertEqual([], rule_no_ambiguous_valido(text, 'docs/x.md'))

    def test_directory_traversal_error_is_not_silent_success(self):
        import os
        real_walk = os.walk

        def broken_walk(top, **kwargs):
            kwargs['onerror'](PermissionError(13, 'denied', str(top / 'locked')))
            yield from real_walk(top, **kwargs)

        with patch('src.semantic_guard.lint_runner.os.walk', side_effect=broken_walk):
            report = run_semantic_lint_report(self.root)
        self.assertEqual(2, len(report.violations))
        self.assertTrue(all(v.rule_id == 'S-00' for v in report.violations))

    def test_symlink_directory_is_reported_instead_of_skipped_silently(self):
        link = self.root / 'src/linked'
        try:
            link.symlink_to(self.root / 'docs', target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('OS does not permit creating symlinks')
        self.assertTrue(any(v.rule_id == 'S-00' for v in run_semantic_lint(self.root)))

    def test_public_list_api_is_preserved(self):
        self.assertIsInstance(run_semantic_lint(self.root), list)

    def test_cli_success_and_violation_return_codes(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, main(['--root', str(self.root)]))
        self.assertIn('Archivos analizados: 2', output.getvalue())
        self.write('src/base.py', 'event = "SWAP_APLICADO"')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, main(['--root', str(self.root)]))

    def test_cli_process_returns_nonzero_for_incomplete_scope(self):
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, '-m', 'src.semantic_guard.lint_runner',
                                 '--root', str(self.root / 'absent')],
                                cwd=repo, capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn('S-00', result.stdout)

    def test_cli_process_returns_zero_for_clean_scope(self):
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, '-m', 'src.semantic_guard.lint_runner',
                                 '--root', str(self.root)], cwd=repo, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
