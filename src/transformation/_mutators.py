from pglast.ast import (
    Node, SelectStmt, A_Expr, A_Const, ColumnRef, BoolExpr
)
from pglast.visitors import VisitorMutator


class TenantIDInjector(VisitorMutator):
    def __init__(self, tenant_id: str):
        super().__init__()
        self.tenant_id = tenant_id

    def visit_SelectStmt(self, node: SelectStmt, *args):
        # Рекурсивный обход (обязательно)
        node = super().visit_SelectStmt(node, *args)

        # Создаем tenant_id = '...'
        new_clause = A_Expr(
            kind=A_Expr.Kind.AEXPR_OP,
            name=('=',),
            lexpr=ColumnRef(fields=('tenant_id',)),
            rexpr=A_Const(val=self.tenant_id)
        )

        existing = node.where_clause

        if existing is None:
            node.where_clause = new_clause
        else:
            # В 6.x enum лежит в BoolExpr.BoolExprType
            node.where_clause = BoolExpr(
                boolop=BoolExpr.BoolExprType.AND_EXPR,
                args=[existing, new_clause]
            )

        return node
