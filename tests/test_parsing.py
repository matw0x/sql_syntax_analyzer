import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from parsing import ParserService
from common import ParsingError
from .utils import BaseTestCase, get_mock_settings

class TestParserService(BaseTestCase):
    def setUp(self):
        self.settings_patcher = patch('parsing.service.settings', get_mock_settings())
        self.mock_settings = self.settings_patcher.start()
        self.parser = ParserService()

    def tearDown(self):
        self.settings_patcher.stop()

    def test_basic_select_parsing(self):
        sql = "SELECT count(id) FROM users WHERE age > 18"
        parsed = self.parser.parse(sql)
        
        self.assertEqual(parsed.structure.command_type, "SelectStmt")
        self.assertIn("users", parsed.structure.tables)
        self.assertIn("count", parsed.structure.aggregates)

    def test_complex_query_structure(self):
        sql = """
            SELECT u.name, o.total 
            FROM public.users u 
            JOIN sales.orders o ON u.id = o.user_id
        """
        parsed = self.parser.parse(sql)
        tables = set(parsed.structure.tables)
        
        self.assertTrue({"public.users", "sales.orders"}.issubset(tables) 
                        or {"users", "orders"}.issubset(tables))

    def test_dangerous_commands_detection(self):
        dangerous_sqls = [
            ("TRUNCATE TABLE users", "TruncateStmt"),
            ("DROP TABLE orders", "DropStmt"),
        ]
        
        for sql, expected_type in dangerous_sqls:
            with self.subTest(sql=sql):
                parsed = self.parser.parse(sql)
                self.assertIn(expected_type, parsed.structure.dangerous_commands)

    def test_stress_invalid_syntax(self):
        invalid_queries = [
            "SELECT * FROM", 
            "DELETE FROM users WHERE",
            "SLECT * FROM users",
            "DELETE * FROM users",
            "Gibberish text 123"
        ]
        
        for sql in invalid_queries:
            with self.subTest(sql=sql):
                with self.assertRaises(ParsingError):
                    self.parser.parse(sql)

    def test_stress_deep_nesting(self):
        depth = 50
        sql = "SELECT * FROM t WHERE id IN (" * depth + "1" + ")" * depth
        
        try:
            parsed = self.parser.parse(sql)
            self.assertEqual(parsed.structure.command_type, "SelectStmt")
        except RecursionError:
            self.fail("Parser failed on deep recursion")