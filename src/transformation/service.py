from pglast.printers import node_printer
from common.models import ParsedQuery, TransformedQuery
from common.errors import TransformationError
from ._mutators import TenantIDInjector

class TransformerService:

    def __init__(self, tenant_id: str):
        self._tenant_id = tenant_id

    def add_tenant_security(self, parsed_query: ParsedQuery) -> TransformedQuery:
        try:
            injector = TenantIDInjector(self._tenant_id)
            
            modified_ast = injector.visit(parsed_query.ast)
            
            new_sql_string = node_printer(modified_ast)
            
            return TransformedQuery(
                original_ast=parsed_query.ast,
                modified_ast=modified_ast,
                new_sql=new_sql_string
            )
            
        except Exception as e:
            raise TransformationError(f"Failed to transform AST: {e}")