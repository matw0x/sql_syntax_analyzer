import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from transformation import TransformerService
from parsing import ParserService
from .utils import BaseTestCase, get_mock_settings

class TestTransformerService(BaseTestCase):
    def setUp(self):
        self.tenant_id = "corp_123"
        self.mock_conf = get_mock_settings(
            trans_enabled=True,
            tenant_enabled=True,
            target_col="org_id"
        )
        self.patcher = patch('transformation.service.settings', self.mock_conf)
        self.patcher.start()
        
        with patch('parsing.service.settings', self.mock_conf):
            self.parser = ParserService()
            
        self.transformer = TransformerService(current_tenant_id=self.tenant_id)

    def tearDown(self):
        self.patcher.stop()

    def test_transformation_skipped_if_disabled(self):
        self.mock_conf.transformation.enabled = False
        transformer = TransformerService(self.tenant_id)
        
        sql = "SELECT * FROM users"
        parsed = self.parser.parse(sql)
        result = transformer.transform(parsed)
        
        self.assertEqual(result.new_sql, sql)

    def test_inject_where_simple(self):
        sql = "SELECT name FROM users"
        parsed = self.parser.parse(sql)
        result = self.transformer.transform(parsed)
        
        self.assertIn("WHERE", result.new_sql)
        self.assertIn(f"org_id = '{self.tenant_id}'", result.new_sql)

    def test_inject_where_append(self):
        sql = "SELECT name FROM users WHERE active = true"
        parsed = self.parser.parse(sql)
        result = self.transformer.transform(parsed)
        
        self.assertIn("active = TRUE", result.new_sql) 
        self.assertIn("AND", result.new_sql)
        self.assertIn(f"org_id = '{self.tenant_id}'", result.new_sql)

    def test_skip_non_select_statements(self):
        sql = "INSERT INTO users (name) VALUES ('Alice')"
        parsed = self.parser.parse(sql)
        result = self.transformer.transform(parsed)
        
        self.assertEqual(result.new_sql, sql)