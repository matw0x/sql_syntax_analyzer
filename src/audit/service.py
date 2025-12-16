import json
from datetime import datetime
from pathlib import Path
from common import ParsedQuery, ValidationResult

class AuditLogger:
    def __init__(self, log_file: str = "artifacts/audit.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, query: ParsedQuery, validation: ValidationResult, transformed_sql: str | None = None):
        structure = query.structure

        record = {
            "timestamp": datetime.now().isoformat(),
            "raw_sql": query.raw_sql,
            "structure_analysis": {
                "type": structure.command_type,
                "tables": structure.tables,
                "functions": structure.functions,
                "aggregates": structure.aggregates,
                "where_conditions": structure.where_clauses, 
                "dangerous_markers": structure.dangerous_commands,
                "has_subqueries": structure.has_subqueries
            },
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, indent=4))
            f.write("\n" + "-"*50 + "\n")

    def _extract_stmt_type(self, ast) -> str:
        if not ast:
            return "UNKNOWN"
        return type(ast[0].stmt).__name__