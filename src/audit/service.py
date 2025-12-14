import json
import time
from pathlib import Path
from common import ParsedQuery, ValidationResult

class AuditLogger:
    def __init__(self, log_file: str = "artifacts/audit.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, 
                    query: ParsedQuery, 
                    validation: ValidationResult, 
                    transformed_sql: str | None = None):
        
        record = {
            "timestamp": time.time(),
            "original_sql": query.raw_sql,
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "transformed_sql": transformed_sql,
            "statement_type": self._extract_stmt_type(query.ast)
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _extract_stmt_type(self, ast) -> str:
        if not ast:
            return "UNKNOWN"
        return type(ast[0].stmt).__name__