from pathlib import Path

from src.semantic_guard.diff_rules import (
    SemanticDiffViolation,
    rule_forbidden_legacy_terms,
    rule_missing_taxonomy,
    rule_partial_taxonomy_loss,
)
from src.semantic_guard.extractor import extract_semantic_tokens


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def run_semantic_diff(old_path: str, new_path: str) -> list[SemanticDiffViolation]:
    old_text = load_text(old_path)
    new_text = load_text(new_path)

    old_tokens = extract_semantic_tokens(old_text)
    new_tokens = extract_semantic_tokens(new_text)

    violations: list[SemanticDiffViolation] = []
    violations.extend(rule_missing_taxonomy(old_tokens, new_tokens))
    violations.extend(rule_partial_taxonomy_loss(old_tokens, new_tokens))
    violations.extend(rule_forbidden_legacy_terms(new_text))

    return violations


if __name__ == "__main__":
    old_path = "docs_old/contratos.md"
    new_path = "docs/contratos.md"

    violations = run_semantic_diff(old_path, new_path)

    if not violations:
        print("OK: semantic diff sin drift")
    else:
        print("Semantic diff violations found:\n")
        for violation in violations:
            print(violation)