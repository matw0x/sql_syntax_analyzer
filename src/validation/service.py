from src.common import ValidationResult, ParsedQuery
from config import settings
from .rules import StatementTypeRule, FunctionBlacklistRule, BaseRule

class ValidatorService:
    def __init__(self):
        self._rules: list[BaseRule] = [
            StatementTypeRule(settings.validation.forbidden_statements),
            FunctionBlacklistRule(settings.validation.forbidden_functions),
        ]
        self._enabled = settings.validation.enabled

    def validate(self, parsed_query: ParsedQuery) -> ValidationResult:
        if not self._enabled:
            return ValidationResult(is_valid=True)

        errors = []
        for rule in self._rules:
            error_message = rule.validate(parsed_query)
            if error_message:
                errors.append(error_message)
        
        if errors:
            return ValidationResult(is_valid=False, errors=tuple(errors))
        
        return ValidationResult(is_valid=True)