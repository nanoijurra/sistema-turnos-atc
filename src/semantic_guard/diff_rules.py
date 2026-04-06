class SemanticDiffViolation:
    def __init__(self, rule_id: str, message: str) -> None:
        self.rule_id = rule_id
        self.message = message

    def __str__(self) -> str:
        return f"[{self.rule_id}] {self.message}"


def rule_missing_taxonomy(
    old_tokens: dict[str, set[str]], new_tokens: dict[str, set[str]]
) -> list[SemanticDiffViolation]:
    violations: list[SemanticDiffViolation] = []

    for category in old_tokens:
        if old_tokens[category] and not new_tokens[category]:
            violations.append(
                SemanticDiffViolation(
                    "D-01",
                    f"Se eliminó completamente la taxonomía de '{category}'",
                )
            )

    return violations


def rule_partial_taxonomy_loss(
    old_tokens: dict[str, set[str]], new_tokens: dict[str, set[str]]
) -> list[SemanticDiffViolation]:
    violations: list[SemanticDiffViolation] = []

    for category in old_tokens:
        lost = old_tokens[category] - new_tokens[category]
        if lost:
            violations.append(
                SemanticDiffViolation(
                    "D-02",
                    f"Se perdieron términos en '{category}': {sorted(lost)}",
                )
            )

    return violations


def rule_forbidden_legacy_terms(new_text: str) -> list[SemanticDiffViolation]:
    violations: list[SemanticDiffViolation] = []
    forbidden_terms = ["APROBABLE", "ACEPTADO"]

    for term in forbidden_terms:
        if term in new_text:
            violations.append(
                SemanticDiffViolation(
                    "D-03",
                    f"Reapareció término legado prohibido: {term}",
                )
            )

    return violations