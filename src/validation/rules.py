from abc import ABC, abstractmethod
from common import ParsedQuery

class BaseRule(ABC):
    @abstractmethod
    def validate(self, query: ParsedQuery) -> str | None:
        pass

class StatementTypeRule(BaseRule):
    def __init__(self, forbidden_types: list[str]):
        self.forbidden_types = set(forbidden_types)

    def validate(self, query: ParsedQuery) -> str | None:
        for stmt in query.ast:
            stmt_type = type(stmt.stmt).__name__
            if stmt_type in self.forbidden_types:
                return f"Forbidden statement detected: {stmt_type}"
        return None

class FunctionBlacklistRule(BaseRule):    
    def __init__(self, forbidden_functions: list[str]):
        self.forbidden_functions = set(f.lower() for f in forbidden_functions)

    def validate(self, query: ParsedQuery) -> str | None:
        found = set(query.structure.functions).intersection(self.forbidden_functions)
        if found:
            return f"Forbidden functions detected: {', '.join(found)}"
        return None