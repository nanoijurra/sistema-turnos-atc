import ast
import re
from pathlib import PurePosixPath


class SemanticViolation:
    def __init__(self, rule_id: str, message: str, file: str, lineno: int) -> None:
        self.rule_id = rule_id
        self.message = message
        self.file = file
        self.lineno = lineno

    def __str__(self) -> str:
        return f"[{self.rule_id}] {self.file}:{self.lineno} -> {self.message}"


def rule_simulator_no_decision(tree: ast.AST, file: str) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []
    forbidden = ["VIABLE", "OBSERVAR", "RECHAZAR", "APROBADO"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for word in forbidden:
                if word in node.value:
                    violations.append(
                        SemanticViolation(
                            "S-01",
                            f"Simulator contiene término de decisión o workflow: {word}",
                            file,
                            getattr(node, "lineno", 0),
                        )
                    )
    return violations


def rule_engine_no_decision(tree: ast.AST, file: str) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []
    forbidden = ["VIABLE", "OBSERVAR", "RECHAZAR", "APROBADO"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for word in forbidden:
                if word in node.value:
                    violations.append(
                        SemanticViolation(
                            "S-02",
                            f"Engine contiene decisión operativa o estado: {word}",
                            file,
                            getattr(node, "lineno", 0),
                        )
                    )
    return violations


def rule_swap_service_no_classification_logic(
    tree: ast.AST, file: str
) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []
    forbidden_patterns = ["delta_score", "delta_hard", "delta_soft", "clasificar"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            for pattern in forbidden_patterns:
                if pattern in node.id:
                    violations.append(
                        SemanticViolation(
                            "S-03",
                            f"swap_service contiene lógica técnica sospechosa: {pattern}",
                            file,
                            getattr(node, "lineno", 0),
                        )
                    )
    return violations


# The declaration is evidence for S-05, not a productive audit event.
LEGACY_AUDIT_EVENT_NAMES = (
    "REQUEST_EVALUADO",
    "REQUEST_EVALUADO_SIN_TECNICA",
    "REQUEST_RESUELTO",
    "SWAP_APLICADO",
    "REQUEST_CANCELADO_POR_OBSOLESCENCIA",
    "Request creado:",
)


# S-04 intentionally recognizes explicit taxonomic assignments, not arbitrary prose.
_AMBIGUOUS_ASSIGNMENT = re.compile(
    r"\b(?:estado|clasificaci[oó]n|decisi[oó]n)"
    r"(?:[ \t]+(?:del[ \t]+)?(?:swap|request|roster|operativa|t[eé]cnica))*"
    r"[ \t]*(?::|=|\bes\b)[ \t]*[\"'`*]*"
    r"v[aá]lid[oa]\b",
    re.IGNORECASE,
)


def rule_no_ambiguous_valido(text: str, file: str) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _AMBIGUOUS_ASSIGNMENT.search(line):
            violations.append(
                SemanticViolation(
                    "S-04",
                    "Valido/valida usado como estado, clasificacion o decision sin taxonomia explicita",
                    file,
                    lineno,
                )
            )
    return violations


def _registry_constants(tree: ast.AST, file: str) -> set[int]:
    # Only the one literal registry in this module is exempt, never the whole file.
    parts = PurePosixPath(file.replace("\\", "/")).parts
    if tuple(parts[-3:]) != ("src", "semantic_guard", "lint_rules.py"):
        return set()
    if not isinstance(tree, ast.Module):
        return set()
    exempt: set[int] = set()
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name) or target.id != "LEGACY_AUDIT_EVENT_NAMES":
            continue
        if not isinstance(statement.value, ast.Tuple):
            continue
        # Do not exempt calls, interpolations, or executable event construction.
        if all(isinstance(item, ast.Constant) and isinstance(item.value, str)
               for item in statement.value.elts):
            exempt.update(id(item) for item in statement.value.elts)
    return exempt


def rule_no_legacy_audit_event_names(
    tree: ast.AST,
    file: str,
) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []
    exempt = _registry_constants(tree, file)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if id(node) in exempt:
            continue
        for event_name in LEGACY_AUDIT_EVENT_NAMES:
            # Match full event names, not prefixes of normalized identifiers.
            pattern = r"(?<!\w)" + re.escape(event_name)
            if event_name[-1].isalnum():
                pattern += r"(?!\w)"
            if re.search(pattern, node.value):
                violations.append(
                    SemanticViolation(
                        "S-05",
                        f"Nombre legacy de evento auditable detectado: {event_name}. Usar eventos normalizados v81.",
                        file,
                        getattr(node, "lineno", 0),
                    )
                )
    return violations
