from src.semantic_guard.lint_runner import run_semantic_lint


def test_semantic_integrity() -> None:
    violations = run_semantic_lint()
    assert not violations, "\n".join(str(v) for v in violations)