import pglast.ast
from pglast.stream import RawStream
from common import ParsedQuery, TransformedQuery, TransformationError
from config import settings
from ._mutator import TenantInjector

class TransformerService:
    def __init__(self, current_tenant_id: str):
        self.tenant_id = current_tenant_id
        self.config = settings.transformation
        
        self._allowed_types = []
        for name in self.config.allowed_statements:
            if hasattr(pglast.ast, name):
                self._allowed_types.append(getattr(pglast.ast, name))
        self._allowed_types = tuple(self._allowed_types)

    def transform(self, query: ParsedQuery) -> TransformedQuery:
        if not self.config.enabled:
            return self._skip(query)

        try:
            for stmt in query.ast:
                if not isinstance(stmt.stmt, self._allowed_types):
                    return self._skip(query)
            
            current_ast = query.ast
            was_modified = False

            tenant_rule = self.config.rules.tenant_injection
            
            if tenant_rule.enabled:
                injector = TenantInjector(
                    tenant_column=tenant_rule.target_column,
                    tenant_value=self.tenant_id
                )

                current_ast = injector(current_ast)
                if injector.modified:
                    was_modified = True

            if was_modified:
                new_sql = RawStream()(current_ast)
            else:
                new_sql = query.raw_sql

            return TransformedQuery(
                original_ast=query.ast,
                modified_ast=current_ast,
                new_sql=new_sql
            )

        except Exception as e:
            raise TransformationError(f"Transformation failed: {e}")

    def _skip(self, query: ParsedQuery) -> TransformedQuery:
        return TransformedQuery(
            original_ast=query.ast,
            modified_ast=query.ast,
            new_sql=query.raw_sql
        )