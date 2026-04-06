import ast
import os

from src.semantic_guard.lint_rules import (
    SemanticViolation,
    rule_engine_no_decision,
    rule_no_ambiguous_valido,
    rule_simulator_no_decision,
    rule_swap_service_no_classification_logic,
)


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def analyze_python_file(path: str) -> list[SemanticViolation]:
    content = load_text_file(path)
    tree = ast.parse(content)
    violations: list[SemanticViolation] = []

    normalized = path.replace("\\", "/").lower()

    if "simulator" in normalized:
        violations.extend(rule_simulator_no_decision(tree, path))

    if "engine" in normalized:
        violations.extend(rule_engine_no_decision(tree, path))

    if "swap_service" in normalized:
        violations.extend(rule_swap_service_no_classification_logic(tree, path))

    return violations


def analyze_markdown_file(path: str) -> list[SemanticViolation]:
    content = load_text_file(path)
    return rule_no_ambiguous_valido(content, path)

def run_semantic_lint():
    all_violations = []

    for root, dirs, files in os.walk("."):
        for file in files:
            full_path = os.path.join(root, file)

            normalized_path = os.path.abspath(full_path).replace("\\", "/").lower()

        if file.endswith(".py") and "/src/" in normalized_path:
                all_violations.extend(analyze_python_file(full_path))

        elif file.endswith(".md") and "/docs/" in normalized_path:
            if "estado_docs.md" in normalized_path:
                continue  # archivo de control, fuera de lint semántico

            all_violations.extend(analyze_markdown_file(full_path))

    return all_violations


if __name__ == "__main__":
    violations = run_semantic_lint()

    if not violations:
        print("OK: semantic lint sin violaciones")
    else:
        print("Semantic violations found:\n")
        for violation in violations:
            print(violation)