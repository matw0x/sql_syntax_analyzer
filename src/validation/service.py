from common.models import ValidationResult, ParsedQuery
from .rules import BaseRule

from ._internal_rules._ddl_rule import DDLRule

class ValidatorService:
    
    def __init__(self):
        self._rules: list[BaseRule] = [
            DDLRule(),
            # BlacklistRule(config.get_blacklist()),
        ]

    def validate(self, parsed_query: ParsedQuery) -> ValidationResult:
        errors = []
        
        for rule in self._rules:
            error_message = rule.validate(parsed_query.ast)
            if error_message:
                errors.append(error_message)
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        
        return ValidationResult(is_valid=True)