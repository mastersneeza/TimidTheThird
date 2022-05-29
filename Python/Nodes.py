from Token import *

### Expressions ###

class Expr:
    def __init__(self, pos_start : Position, pos_end : Position):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def accept(self, visitor): pass

class SubscriptExpr(Expr):
    def __init__(self, iterable : Expr, subscript : Expr):
        self.iterable = iterable
        self.subscript = subscript
        super().__init__(self.iterable.pos_start, self.subscript.pos_end)
    def accept(self, visitor):
        return visitor.visitSubscriptExpr(self)

class AssignExpr(Expr):
    def __init__(self, name : Token, value : Expr):
        self.name = name
        self.value = value
        super().__init__(name.pos_start, value.pos_end)
    def accept(self, visitor):
        return visitor.visitAssignExpr(self)
    def __repr__(self) -> str:
        return f"({self.name.lexeme} = {self.value})"

class BinaryExpr(Expr):
    def __init__(self, left : Expr, operator : Token, right : Expr):
        self.left = left
        self.operator = operator
        self.right = right
        super().__init__(self.left.pos_start, self.right.pos_end)

    def accept(self, visitor): return visitor.visitBinaryExpr(self)
    def __repr__(self): return f"({self.left} {self.operator.lexeme} {self.right})"

class CallExpr(Expr):
    def __init__(self, callee : Expr, paren : Token, args : list[Expr]):
        self.callee = callee
        self.paren = paren
        self.args = args
        super().__init__(callee.pos_start, paren.pos_end)
    
    def accept(self, visitor): return visitor.visitCallExpr(self)
    def __repr__(self): return f"({self.callee}({self.args}))" 

class DictionaryExpr(Expr):
    def __init__(self, lpar : Token, rpar : Token, keys : list[Expr], values : list[Expr]):
        self.keys = keys
        self.values = values
        super().__init__(lpar.pos_start, rpar.pos_end)
    def accept(self, visitor): return visitor.visitDictionaryExpr(self)

class FactorialExpr(Expr):
    def __init__(self, expr : Expr):
        self.expr = expr
        super().__init__(expr.pos_start, expr.pos_end)

    def accept(self, visitor): return visitor.visitFactorialExpr(self)
    def __repr__(self) -> str: return f"({self.expr}!)"

class InputExpr(Expr): # User input
    def __init__(self, prompt : Expr, kw : Token):
        self.prompt = prompt
        super().__init__(kw.pos_start, kw.pos_end if prompt == None else prompt.pos_end)

    def accept(self, visitor): return visitor.visitInputExpr(self)
    def __repr__(self) -> str: return f"(input {self.prompt})"

class LambdaExpr(Expr):
    def __init__(self, keyword : Token, identifier : Token, body : Expr):
        self.keyword = keyword
        self.identifier = identifier
        self.body = body
        super().__init__(keyword.pos_start, body.pos_end)

    def accept(self, visitor): return visitor.visitLambdaExpr(self)
    def __repr__(self): return f"(lam {self.identifier.lexeme} {self.body})"

class LiteralExpr(Expr):
    def __init__(self, token : Token):
        self.token = token
        super().__init__(token.pos_start, token.pos_end)

    def accept(self, visitor): return visitor.visitLiteralExpr(self)
    def __repr__(self): return f"{self.token.lexeme}"

class TernaryExpr(Expr):
    def __init__(self, condition : Expr, if_branch : Expr, else_branch : Expr):
        self.condition = condition
        self.if_branch = if_branch
        self.else_branch = else_branch
        super().__init__(self.condition.pos_start, self.else_branch.pos_end)
    def accept(self, visitor):
        return visitor.visitTernaryExpr(self)
    def __repr__(self) -> str:
        return f"({self.condition} ? {self.if_branch} : {self.else_branch})"

class UnaryExpr(Expr):
    def __init__(self, operator : Token, right : Expr):
        self.operator = operator
        self.right = right
        super().__init__(self.operator.pos_start, self.right.pos_end)

    def accept(self, visitor): return visitor.visitUnaryExpr(self)
    def __repr__(self): return f"({self.operator.lexeme} {self.right})"

class VariableExpr(Expr):
    def __init__(self, name : Token):
        self.name = name
        super().__init__(self.name.pos_start, self.name.pos_end)

    def accept(self, visitor): return visitor.visitVariableExpr(self)
    def __repr__(self): return f"{self.name.lexeme}"

### Statements ###

class Stmt:
    def __init__(self, pos_start : Position, pos_end : Position):
        self.pos_start = pos_start
        self.pos_end = pos_end
    def accept(self, visitor): pass

class AssertStmt(Stmt):
    def __init__(self, keyword : Token, condition : Expr, error_msg : Expr):
        self.keyword = keyword
        self.condition = condition
        self.error_msg = error_msg

        super().__init__(self.keyword.pos_start, self.error_msg.pos_end)

    def accept(self, visitor): return visitor.visitAssertStmt(self)

class Block(Stmt):
    def __init__(self, lcurl : Token, statements : list[Stmt], rcurl : Token):
        self.statements = statements
        super().__init__(lcurl.pos_start, rcurl.pos_end)

    def accept(self, visitor): return visitor.visitBlock(self)
    def __repr__(self) -> str:
        str_stmts = [str(stmt) for stmt in self.statements]
        string = '\n'.join(str_stmts)
        return f"{{{string}}}"

class ExprStmt(Stmt):
    def __init__(self, expr : Expr):
        self.expr = expr
        super().__init__(expr.pos_start, expr.pos_end)

    def accept(self, visitor): visitor.visitExprStmt(self)
    def __repr__(self): return f"(expr {self.expr})"

class ForStmt(Stmt):
    def __init__(self, body : Stmt, name : Token, condition : Expr = None, step : Expr = None):
        self.body = body
        self.name = name
        self.condition = condition
        self.step = step

        super().__init__(self.name.pos_start, self.body.pos_end)
    def accept(self, visitor): visitor.visitForStmt(self)

class IfStmt(Stmt):
    def __init__(self, condition : Expr, if_branch : Stmt, else_branch : Stmt = None):
        self.condition = condition
        self.if_branch = if_branch
        self.else_branch = else_branch
        super().__init__(condition.pos_start, if_branch.pos_end if else_branch == None else else_branch.pos_end)
    def accept(self, visitor): visitor.visitIfStmt(self)
    def __repr__(self): return f"(if {self.condition} do {self.if_branch} else {self.else_branch})"

class PrintStmt(Stmt):
    def __init__(self, value : Expr):
        self.value = value
        super().__init__(value.pos_start, value.pos_end)

    def accept(self, visitor): visitor.visitPrintStmt(self)
    def __repr__(self): return f"(print {self.value})"

class WhileStmt(Stmt):
    def __init__(self, condition : Expr, body : Stmt):
        self.condition = condition
        self.body = body
        super().__init__(self.condition.pos_start, self.body.pos_end)

    def accept(self, visitor): visitor.visitWhileStmt(self)
    def __repr__(self): return f"(while {self.condition} do {self.body})"

class VarDeclStmt(Stmt):
    def __init__(self, name : Token, initializer : Expr):
        self.name = name
        self.initializer = initializer
        super().__init__(name.pos_start, initializer.pos_end if initializer != None else name.pos_end)

    def accept(self, visitor): visitor.visitVarDeclStmt(self)
    def __repr__(self): return f"(var {self.name.lexeme} = {self.initializer})"

### Visitor ###
class Visitor:
    def visitSubscriptExpr(self, expr : SubscriptExpr): pass
    def visitAssignExpr(self, expr : AssignExpr): pass
    def visitBinaryExpr(self, expr : BinaryExpr): pass
    def visitCallExpr(self, expr : CallExpr): pass
    def visitDictionaryExpr(self, expr : DictionaryExpr): pass
    def visitFactorialExpr(self, expr : FactorialExpr): pass
    def visitInputExpr(self, expr : InputExpr): pass
    def visitLambdaExpr(self, expr : LambdaExpr): pass
    def visitLiteralExpr(self, expr : LiteralExpr): pass
    def visitTernaryExpr(self, expr : TernaryExpr): pass
    def visitUnaryExpr(self, expr : UnaryExpr): pass
    def visitVariableExpr(self, expr : VariableExpr): pass
    
    def visitAssertStmt(self, stmt : AssertStmt): pass
    def visitBlock(self, block : Block): pass
    def visitExprStmt(self, stmt : ExprStmt): pass
    def visitForStmt(self, stmt : ForStmt): pass
    def visitIfStmt(self, stmt : IfStmt): pass
    def visitPrintStmt(self, stmt : PrintStmt): pass
    def visitVarDeclStmt(self, stmt : VarDeclStmt): pass
    def visitWhileStmt(self, stmt : WhileStmt): pass
