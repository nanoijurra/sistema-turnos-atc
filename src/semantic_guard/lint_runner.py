import argparse
import ast
import os
from dataclasses import dataclass, field
from pathlib import Path

from src.semantic_guard.lint_rules import (
    SemanticViolation,
    rule_engine_no_decision,
    rule_no_ambiguous_valido,
    rule_no_legacy_audit_event_names,
    rule_simulator_no_decision,
    rule_swap_service_no_classification_logic,
)


@dataclass
class SemanticLintReport:
    violations: list[SemanticViolation] = field(default_factory=list)
    analyzed_files: list[str] = field(default_factory=list)
    excluded_files: list[str] = field(default_factory=list)


# Closed history and retired/control documents are not current semantic contracts.
EXCLUDED_MARKDOWN_FILES = frozenset({"estado_docs.md", "contratos_resumen.md"})


def load_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def analyze_python_file(path: str) -> list[SemanticViolation]:
    tree = ast.parse(load_text_file(path), filename=path)
    violations: list[SemanticViolation] = []
    filename = Path(path.replace("\\", "/")).name.lower()
    if filename == "simulator.py":
        violations.extend(rule_simulator_no_decision(tree, path))
    if filename == "engine.py":
        violations.extend(rule_engine_no_decision(tree, path))
    if filename == "swap_service.py":
        violations.extend(rule_swap_service_no_classification_logic(tree, path))
    violations.extend(rule_no_legacy_audit_event_names(tree, path))
    return violations


def analyze_markdown_file(path: str) -> list[SemanticViolation]:
    return rule_no_ambiguous_valido(load_text_file(path), path)


def run_semantic_lint_report(root: str | Path = ".") -> SemanticLintReport:
    root = Path(root).resolve()
    report = SemanticLintReport()
    for folder, extension in (("src", ".py"), ("docs", ".md")):
        directory = root / folder
        count = 0
        if not directory.is_dir():
            report.violations.append(SemanticViolation(
                "S-00", "Directorio requerido ausente", str(directory), 0))
            continue
        candidates: list[Path] = []

        def record_walk_error(error: OSError) -> None:
            report.violations.append(SemanticViolation(
                "S-00", f"No se pudo recorrer el directorio: {error}",
                str(error.filename or directory), 0))

        for current, dirs, files in os.walk(directory, onerror=record_walk_error, followlinks=False):
            dirs.sort()
            for dirname in list(dirs):
                linked = Path(current) / dirname
                if linked.is_symlink():
                    dirs.remove(dirname)
                    report.violations.append(SemanticViolation(
                        "S-00", "Directorio enlazado no recorrido", str(linked), 0))
            candidates.extend(Path(current) / filename for filename in sorted(files))
        for path in candidates:
            if path.suffix.lower() != extension:
                continue
            relative = path.relative_to(directory)
            if extension == ".md" and (
                relative.parts[0] == "hitos"
                or relative.as_posix() in EXCLUDED_MARKDOWN_FILES
            ):
                report.excluded_files.append(str(path))
                continue
            if not path.resolve().is_relative_to(directory.resolve()):
                report.violations.append(SemanticViolation(
                    "S-00", "Archivo enlazado fuera del alcance", str(path), 0))
                continue
            count += 1
            try:
                analyzer = analyze_python_file if extension == ".py" else analyze_markdown_file
                report.violations.extend(analyzer(str(path)))
                report.analyzed_files.append(str(path))
            except (OSError, UnicodeError, SyntaxError) as error:
                report.violations.append(SemanticViolation(
                    "S-00", f"Archivo no analizado: {error}", str(path),
                    getattr(error, "lineno", 0) or 0))
        if count == 0:
            report.violations.append(SemanticViolation(
                "S-00", f"Sin archivos {extension} elegibles para analizar", str(directory), 0))
    return report


def run_semantic_lint(root: str | Path = ".") -> list[SemanticViolation]:
    # Preserve the original public list-returning API.
    return run_semantic_lint_report(root).violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Semantic lint del sistema ATC")
    parser.add_argument("--root", default=".", help="Raiz del repositorio")
    args = parser.parse_args(argv)
    report = run_semantic_lint_report(args.root)
    print(f"Archivos analizados: {len(report.analyzed_files)}; excluidos: {len(report.excluded_files)}")
    if report.violations:
        for violation in report.violations:
            print(violation)
        return 1
    print("OK: semantic lint sin violaciones en el alcance declarado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
