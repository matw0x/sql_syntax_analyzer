import pglast
from pglast.parser import ParseError
from common import ParsingError, ParsedQuery
from ._analyzer import extract_structure

class ParserService:
    def parse(self, sql_string: str) -> ParsedQuery:
        try:
            ast = pglast.parse_sql(sql_string)
            structure = extract_structure(ast)
            
            return ParsedQuery(
                raw_sql=sql_string, 
                ast=ast,
                structure=structure
            )
            
        except ParseError as e:
            raise ParsingError(f"Failed to parse SQL: {e}")