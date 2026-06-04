import ast


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


def rule_no_ambiguous_valido(text: str, file: str) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []

    if "válido" in text.lower() or "valido" in text.lower():
        violations.append(
            SemanticViolation(
                "S-04",
                "Uso potencialmente ambiguo de 'válido/valido' en documentación",
                file,
                0,
            )
        )

    return violations

def rule_no_legacy_audit_event_names(
    tree: ast.AST,
    file: str,
) -> list[SemanticViolation]:
    violations: list[SemanticViolation] = []

    forbidden_events = [
        "REQUEST_EVALUADO",
        "REQUEST_EVALUADO_SIN_TECNICA",
        "REQUEST_RESUELTO",
        "SWAP_APLICADO",
        "REQUEST_CANCELADO_POR_OBSOLESCENCIA",
        "Request creado:",
    ]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue

        if not isinstance(node.value, str):
            continue

        for event_name in forbidden_events:
            if event_name in node.value:
                violations.append(
                    SemanticViolation(
                        "S-05",
                        (
                            "Nombre legacy de evento auditable detectado: "
                            f"{event_name}. Usar eventos normalizados v81."
                        ),
                        file,
                        getattr(node, "lineno", 0),
                    )
                )

    return violations