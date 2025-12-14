from pglast.visitors import Visitor
from pglast.ast import RangeVar, FuncCall, String
from common import QueryStructure

class _StructureVisitor(Visitor):
    def __init__(self):
        self.tables = set()
        self.functions = set()
        self.command_type = "UNKNOWN"

    def visit(self, node):
        if self.command_type == "UNKNOWN" and hasattr(node, "stmt"):
             self.command_type = type(node.stmt).__name__
        super().visit(node)

    def visit_RangeVar(self, node: RangeVar):
        if node.relname:
            self.tables.add(node.relname)

    def visit_FuncCall(self, node: FuncCall):
        if node.funcname and isinstance(node.funcname[-1], String):
             self.functions.add(node.funcname[-1].sval.lower())

def extract_structure(ast: tuple) -> QueryStructure:
    visitor = _StructureVisitor()
    for stmt in ast:
        visitor(stmt)
    
    return QueryStructure(
        command_type=visitor.command_type,
        tables=list(visitor.tables),
        functions=list(visitor.functions)
    )