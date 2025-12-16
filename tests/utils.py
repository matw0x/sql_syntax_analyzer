import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

def get_mock_settings(
    parsing_aggregates=None,
    val_enabled=True,
    forbidden_stmts=None,
    forbidden_funcs=None,
    trans_enabled=True,
    tenant_enabled=True,
    target_col="tenant_id"
):
    mock = MagicMock()
    mock.parsing.known_aggregates = parsing_aggregates or ["count", "sum", "avg"]
    mock.validation.enabled = val_enabled
    mock.validation.forbidden_statements = forbidden_stmts or ["DropStmt", "TruncateStmt"]
    mock.validation.forbidden_functions = forbidden_funcs or ["pg_sleep"]
    mock.transformation.enabled = trans_enabled
    mock.transformation.allowed_statements = ["SelectStmt"]
    mock.transformation.rules.tenant_injection.enabled = tenant_enabled
    mock.transformation.rules.tenant_injection.target_column = target_col
    return mock

class BaseTestCase(unittest.TestCase):
    pass