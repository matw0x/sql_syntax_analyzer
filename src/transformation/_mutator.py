from pglast.visitors import Visitor
from pglast.ast import A_Expr, A_Const, ColumnRef, BoolExpr, String, Integer
from pglast.enums import A_Expr_Kind, BoolExprType

class TenantInjector(Visitor):
    def __init__(self, tenant_column: str, tenant_value: str | int):
        self.tenant_column = tenant_column
        self.tenant_value = tenant_value
        self.modified = False

    def visit_SelectStmt(self, ancestors, node):
        if isinstance(self.tenant_value, int):
            val_node = Integer(ival=self.tenant_value)
            const_node = A_Const(isnull=False, val=val_node)
        else:
            val_node = String(sval=str(self.tenant_value))
            const_node = A_Const(isnull=False, val=val_node)

        tenant_condition = A_Expr(
            kind=A_Expr_Kind.AEXPR_OP,
            name=[String(sval='=')],
            lexpr=ColumnRef(fields=[String(sval=self.tenant_column)]),
            rexpr=const_node,
            location=-1
        )

        if node.whereClause is None:
            new_where = tenant_condition
        else:
            new_where = BoolExpr(
                boolop=BoolExprType.AND_EXPR,
                args=[node.whereClause, tenant_condition],
                location=-1
            )

        node.whereClause = new_where
        self.modified = True
        return node