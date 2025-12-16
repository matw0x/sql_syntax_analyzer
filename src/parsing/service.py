import pglast
from pglast.parser import ParseError
from common import ParsingError, ParsedQuery
from config import settings
from ._analyzer import extract_structure

class ParserService:
    def __init__(self):
        self.known_aggregates = settings.parsing.known_aggregates

    def parse(self, sql_string: str) -> ParsedQuery:
        try:
            ast = pglast.parse_sql(sql_string)
            
            structure = extract_structure(ast, self.known_aggregates)
            
            return ParsedQuery(
                raw_sql=sql_string, 
                ast=ast,
                structure=structure
            )
            
        except ParseError as e:
            raise ParsingError(f"Failed to parse SQL: {e}")