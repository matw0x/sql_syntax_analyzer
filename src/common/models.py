from dataclasses import dataclass, field
from pglast.ast import Node

@dataclass(frozen=True)
class ParsedQuery:
    raw_sql: str
    ast: tuple[Node, ...]

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class TransformedQuery:
    original_ast: tuple[Node, ...]
    modified_ast: tuple[Node, ...]
    new_sql: str