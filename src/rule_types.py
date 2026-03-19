from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Violation:
    codigo: str
    mensaje: str
    severidad: str
    penalizacion: int | float = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleResult:
    regla: str
    prioridad: int
    violaciones: list[Violation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violaciones) == 0