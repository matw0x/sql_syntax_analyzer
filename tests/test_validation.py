import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from validation import ValidatorService
from .utils import BaseTestCase, get_mock_settings

class TestValidatorService(BaseTestCase):
    def test_validation_disabled(self):
        mock_conf = get_mock_settings(val_enabled=False)
        with patch('validation.service.settings', mock_conf):
            validator = ValidatorService()
            mock_query = MagicMock()
            mock_query.structure.functions = ["pg_sleep"]
            
            result = validator.validate(mock_query)
            self.assertTrue(result.is_valid)

    def test_forbidden_statements(self):
        mock_conf = get_mock_settings(forbidden_stmts=["DropStmt"])
        with patch('validation.service.settings', mock_conf):
            validator = ValidatorService()
            
            mock_stmt = MagicMock()
            mock_stmt.stmt.__class__.__name__ = "DropStmt"
            
            mock_query = MagicMock()
            mock_query.ast = [mock_stmt]
            
            result = validator.validate(mock_query)
            self.assertFalse(result.is_valid)
            self.assertIn("Forbidden statement", result.errors[0])

    def test_forbidden_functions(self):
        mock_conf = get_mock_settings(forbidden_funcs=["crosstab"])
        with patch('validation.service.settings', mock_conf):
            validator = ValidatorService()
            
            mock_query = MagicMock()
            mock_query.structure.functions = ["crosstab", "count"]
            
            result = validator.validate(mock_query)
            self.assertFalse(result.is_valid)
            self.assertIn("crosstab", result.errors[0])