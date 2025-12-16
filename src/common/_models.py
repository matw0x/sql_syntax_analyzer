from dataclasses import dataclass, field
from pglast.ast import Node

@dataclass(frozen=True)
class QueryStructure:
    command_type: str
    tables: list[str]
    functions: list[str]
    aggregates: list[str]
    where_clauses: list[str]
    dangerous_commands: list[str]
    has_subqueries: bool = False

@dataclass(frozen=True)
class ParsedQuery:
    raw_sql: str
    ast: tuple[Node, ...]
    structure: QueryStructure

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class TransformedQuery:
    original_ast: tuple[Node, ...]
    modified_ast: tuple[Node, ...]
    new_sql: str