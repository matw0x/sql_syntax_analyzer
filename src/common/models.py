from dataclasses import dataclass, field
from pglast.ast import Node

@dataclass
class ParsedQuery:
    raw_sql: str
    ast: tuple[Node, ...]
    
@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)