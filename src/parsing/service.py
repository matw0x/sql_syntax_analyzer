import pglast
from pglast.parser import ParseError
from common.errors import ParsingError
from common.models import ParsedQuery

class ParserService:
    def parse(self, sql_string: str) -> ParsedQuery:
        try:
            ast = pglast.parse_sql(sql_string)
            return ParsedQuery(raw_sql=sql_string, ast=ast)
        except ParseError as e:
            raise ParsingError(f"Failed to parse SQL: {e}")