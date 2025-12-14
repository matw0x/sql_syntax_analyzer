from pglast.printers import node_printer
from common import ParsedQuery, TransformedQuery, TransformationError
from config import settings
from ._mutator import TenantInjector

class TransformerService:
    def __init__(self, current_tenant_id: str):
        self.tenant_id = current_tenant_id
        self.config = settings.transformation

    def transform(self, query: ParsedQuery) -> TransformedQuery:
        if not self.config.enabled:
            return TransformedQuery(
                original_ast=query.ast,
                modified_ast=query.ast,
                new_sql=query.raw_sql
            )

        try:
            injector = TenantInjector(
                tenant_column=self.config.tenant_column,
                tenant_value=self.tenant_id
            )

            new_ast_list = []
            for stmt in query.ast:
                new_ast_list.append(injector(stmt))
            
            new_ast = tuple(new_ast_list)

            if injector.modified:
                new_sql = node_printer(new_ast)
            else:
                new_sql = query.raw_sql

            return TransformedQuery(
                original_ast=query.ast,
                modified_ast=new_ast,
                new_sql=new_sql
            )

        except Exception as e:
            raise TransformationError(f"Transformation failed: {e}")