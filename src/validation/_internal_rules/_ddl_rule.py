from pglast.ast import (
    Node, DropStmt, TruncateStmt, CreateStmt, 
    AlterTableStmt
)
from validation.rules import BaseRule

FORBIDDEN_DDL_NODES = (
    DropStmt, 
    TruncateStmt, 
    CreateStmt, 
    AlterTableStmt
)

class DDLRule(BaseRule):
    
    def validate(self, ast: tuple[Node, ...]) -> str | None:
        for stmt in ast:
            actual_statement = stmt.stmt 
            if isinstance(actual_statement, FORBIDDEN_DDL_NODES):
                return f"Forbidden DDL operation found: {type(actual_statement).__name__}"
        
        return None