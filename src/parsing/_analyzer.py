from pglast.visitors import Visitor
from pglast.ast import String
from common import QueryStructure

class _StructureVisitor(Visitor):
    def __init__(self):
        self.tables = set()
        self.functions = set()
        self.command_type = "UNKNOWN"

    def visit(self, ancestors, node):
        if self.command_type == "UNKNOWN" and hasattr(node, "stmt"):
             self.command_type = type(node.stmt).__name__
        pass

    def visit_RangeVar(self, ancestors, node):
        if node.relname:
            self.tables.add(node.relname)

    def visit_FuncCall(self, ancestors, node):
        if node.funcname and isinstance(node.funcname[-1], String):
             self.functions.add(node.funcname[-1].sval.lower())

def extract_structure(ast: tuple) -> QueryStructure:
    visitor = _StructureVisitor()

    visitor(ast)
    
    return QueryStructure(
        command_type=visitor.command_type,
        tables=list(visitor.tables),
        functions=list(visitor.functions)
    )