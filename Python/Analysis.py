from Nodes import *

class Resolver(Visitor):
    def resolveS(self, statements : list[Stmt]):
        for stmt in statements:
            self.resolve(stmt)

    def resolve(self, expr : Stmt | Expr):
        expr.accept(self)

    def visitBinaryExpr(self, expr: BinaryExpr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitSubscriptExpr(self, expr: SubscriptExpr):
        self.resolve(expr.iterable)
        self.resolve(expr.subscript)
    
    def visitUnaryExpr(self, expr: UnaryExpr):
        self.resolve(expr.right)
    