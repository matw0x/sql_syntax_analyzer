import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from parsing import ParserService
from validation import ValidatorService
from transformation import TransformerService


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = ParserService()

    def test_extracts_tables_and_functions(self):
        parsed = self.parser.parse("SELECT sum(amount) FROM payments")

        self.assertEqual(parsed.structure.command_type, "SelectStmt")
        self.assertIn("payments", parsed.structure.tables)
        self.assertIn("sum", parsed.structure.functions)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.parser = ParserService()
        self.validator = ValidatorService()

    def test_blocks_forbidden_statement(self):
        parsed = self.parser.parse("DROP TABLE users")
        result = self.validator.validate(parsed)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Forbidden statement" in msg for msg in result.errors))

    def test_blocks_blacklisted_function(self):
        parsed = self.parser.parse("SELECT pg_sleep(1)")
        result = self.validator.validate(parsed)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("pg_sleep" in msg for msg in result.errors))


class TransformationTests(unittest.TestCase):
    def setUp(self):
        self.parser = ParserService()
        self.transformer = TransformerService(current_tenant_id="client_corp_1")

    def test_injects_tenant_filter_when_missing(self):
        parsed = self.parser.parse("SELECT * FROM orders")
        transformed = self.transformer.transform(parsed)

        self.assertNotEqual(transformed.new_sql, parsed.raw_sql)
        self.assertIn("tenant_id", transformed.new_sql)
        self.assertIn("client_corp_1", transformed.new_sql)
        self.assertIsNotNone(transformed.modified_ast[0].stmt.whereClause)

    def test_merges_with_existing_where_clause(self):
        parsed = self.parser.parse("SELECT * FROM orders WHERE status = 'ok'")
        transformed = self.transformer.transform(parsed)
        sql = transformed.new_sql

        self.assertIn("status", sql)
        self.assertIn("tenant_id", sql)
        self.assertIn("AND", sql)


if __name__ == "__main__":
    unittest.main()
