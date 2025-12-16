import sys
import unittest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from audit import AuditLogger
from .utils import BaseTestCase

class TestAuditLogger(BaseTestCase):
    @patch("audit.service.open", new_callable=mock_open)
    @patch("audit.service.Path.mkdir")
    def test_log_structure(self, mock_mkdir, mock_file):
        logger = AuditLogger(log_file="dummy.jsonl")
        
        mock_query = MagicMock()
        mock_query.raw_sql = "SELECT 1"
        
        mock_query.structure.command_type = "SelectStmt"
        mock_query.structure.tables = ["t1"]
        mock_query.structure.functions = []
        mock_query.structure.aggregates = []
        mock_query.structure.where_clauses = []
        mock_query.structure.dangerous_commands = []
        mock_query.structure.has_subqueries = False
        
        mock_validation = MagicMock()
        mock_validation.is_valid = True
        
        transformed_sql = "SELECT 1 WHERE t=1"
        
        logger.log(mock_query, mock_validation, transformed_sql)
        
        handle = mock_file()
        self.assertTrue(handle.write.called)
        
        first_call = handle.write.call_args_list[0]
        json_str = first_call.args[0]
        
        try:
            log_entry = json.loads(json_str)
        except json.JSONDecodeError:
            self.fail(f"Logger wrote invalid JSON: {json_str}")

        self.assertEqual(log_entry["raw_sql"], "SELECT 1")
        self.assertEqual(log_entry["structure_analysis"]["tables"], ["t1"])
        self.assertIn("timestamp", log_entry)
        self.assertEqual(log_entry["structure_analysis"]["type"], "SelectStmt")