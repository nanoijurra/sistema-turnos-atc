from pathlib import Path

from src.semantic_guard.lint_runner import run_semantic_lint


def test_semantic_integrity() -> None:
    violations = run_semantic_lint(Path(__file__).resolve().parents[1])
    assert not violations, "\n".join(str(v) for v in violations)