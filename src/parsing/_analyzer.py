from pglast.visitors import Visitor
from pglast.stream import RawStream
from pglast.ast import String
from common import QueryStructure

class _StructureVisitor(Visitor):
    def __init__(self, known_aggregates: set[str]):
        self.tables = set()
        self.functions = set()
        self.aggregates = set()
        self.where_clauses = []       
        self.dangerous_commands = []  
        self.has_subqueries = False
        self.command_type = "UNKNOWN"
        self.known_aggregates = known_aggregates

    def visit(self, ancestors, node):
        if self.command_type == "UNKNOWN" and hasattr(node, "stmt"):
             self.command_type = type(node.stmt).__name__

        if hasattr(node, "whereClause") and node.whereClause:
            try:
                condition_sql = "WHERE " + RawStream()(node.whereClause)
                self.where_clauses.append(condition_sql)
            except: pass
        
        # just HAVING example
        if hasattr(node, "havingClause") and node.havingClause:
            try:
                condition_sql = "HAVING " + RawStream()(node.havingClause)
                self.where_clauses.append(condition_sql)
            except: pass

        if type(node).__name__ in ("PrepareStmt", "ExecuteStmt"):
            self.dangerous_commands.append(type(node).__name__)

        pass

    def visit_RangeVar(self, ancestors, node):
        if node.relname:
            self.tables.add(node.relname)

    def visit_FuncCall(self, ancestors, node):
        if node.funcname and isinstance(node.funcname[-1], String):
             func_name = node.funcname[-1].sval.lower()
             if func_name in self.known_aggregates:
                 self.aggregates.add(func_name)
             else:
                 self.functions.add(func_name)

    def visit_SubLink(self, ancestors, node):
        self.has_subqueries = True
        pass

    def visit_RangeSubselect(self, ancestors, node):
        self.has_subqueries = True
        pass

    def visit_TruncateStmt(self, ancestors, node):
        self.dangerous_commands.append("TruncateStmt")

    def visit_DropStmt(self, ancestors, node):
        self.dangerous_commands.append("DropStmt")
        
        if node.objects:
            for obj in node.objects:
                if isinstance(obj, (list, tuple)):
                    parts = [p.sval for p in obj if isinstance(p, String)]
                    if parts:
                        self.tables.add(".".join(parts))
                elif isinstance(obj, String):
                     self.tables.add(obj.sval)

def extract_structure(ast: tuple, known_aggregates: list[str]) -> QueryStructure:
    visitor = _StructureVisitor(set(known_aggregates))
    visitor(ast)
    
    return QueryStructure(
        command_type=visitor.command_type,
        tables=list(visitor.tables),
        functions=list(visitor.functions),
        aggregates=list(visitor.aggregates),
        has_subqueries=visitor.has_subqueries,
        where_clauses=list(visitor.where_clauses),
        dangerous_commands=list(visitor.dangerous_commands)
    )