from Runtime import *
from Value import Clock, TimidAnon
from Nodes import*
from Error import ErrorReporter

class Interpreter(Visitor): # TODO: organize REPL runtime
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        self.should_break = False
        self.should_continue = False

        self.globals.define("Clock", Clock())

    def interpret(self, statements : list[Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
        except (RuntimeError, TypeError) as e:
            ErrorReporter.runtime_error(e)

    def evaluate(self, expr : Expr, environment : Environment = None):
        previous = self.environment
        if environment != None:
            try:
                self.environment = environment
                result = expr.accept(self)
            finally:
                self.environment = previous
        else:
            result = expr.accept(self)
        return result

    def execute(self, stmt : Stmt): stmt.accept(self)

    def execute_block(self, statements : list[Stmt], environment : Environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visitBlock(self, block: Block):
        self.execute_block(block.statements, Environment(self.environment))

    def visitContinueStmt(self, stmt: ContinueStmt):
        self.should_continue = True

    def visitPrintStmt(self, stmt: PrintStmt):
        result = ""
        if stmt.value != None:
            result = self.evaluate(stmt.value)
        print(ToString(result))

    def visitExprStmt(self, stmt: ExprStmt): self.evaluate(stmt.expr)

    def visitForStmt(self, stmt: ForStmt):
        if stmt.initializer != None:
            self.execute(stmt.initializer)

        if stmt.condition == None:
            stmt.condition = LiteralExpr(Token(T_TRUE, "tru", None, Position(0, 0, 0, "", ""), Position(0, 0, 0, "", "")))
        
        while self.evaluate(stmt.condition):
            if self.should_break: break
            if self.should_continue:
                self.should_continue = False
                continue

            self.execute(stmt.body)

            if stmt.step != None:
                self.execute(stmt.step)

        self.should_break = False

    def visitForeverStmt(self, stmt: ForeverStmt):
        while True:
            if self.should_break: break
            self.execute(stmt.body)
            if self.should_continue:
                self.should_continue = False
                continue
        self.should_break = False
        self.should_continue = False

    def visitWhileStmt(self, stmt: WhileStmt):
        while self.evaluate(stmt.condition):
            if self.should_break: break
            if self.should_continue:
                self.should_continue = False
                continue
            self.execute(stmt.body)
        self.should_break = False
        self.should_continue = False

    def visitBreakStmt(self, stmt: BreakStmt):
        self.should_break = True

    def visitIfStmt(self, stmt: IfStmt):
        condition = self.evaluate(stmt.condition)

        if condition:
            self.execute(stmt.if_branch)
            return
        if stmt.else_branch != None:
            self.execute(stmt.else_branch)
        
    def visitVarDeclStmt(self, stmt: VarDeclStmt):
        value = None
        if (stmt.initializer != None):
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visitAssignExpr(self, expr: AssignExpr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visitLambdaExpr(self, expr: LambdaExpr):
        return TimidAnon(expr, self.environment.copy())

    def visitInputExpr(self, expr: InputExpr):
        prompt = ""
        if expr.prompt != None:
            prompt = self.evaluate(expr.prompt)

        return input(prompt)

    def visitAssertStmt(self, stmt: AssertStmt):
        condition = self.evaluate(stmt.condition)

        msg = "Assertion error"
        if stmt.error_msg != None:
            msg = self.evaluate(stmt.error_msg)

        if not (condition):
            raise RuntimeError(stmt.pos_start, stmt.pos_end, msg)
    
    def visitLiteralExpr(self, expr: LiteralExpr):
        type_ = expr.token.type
        if type_ in (T_INT, T_FLOAT):
            return expr.token.value
        elif type_ in (T_TRUE, T_FALSE):
            return expr.token.type == T_TRUE
        elif type_ == T_NULL:
            return None
        elif type_ == T_STRING:
            return expr.token.lexeme

    def visitBinaryExpr(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if IsNumeric(left):
            left = ToNumber(left)
        if IsNumeric(right):
            right = ToNumber(right)
        
        operator = expr.operator.type

        if operator == T_PLUS:
            if isinstance(left, str) or isinstance(right, str):
                left = ToString(left)
                right = ToString(right)

            return left + right
        elif operator == T_MINUS:
            return left - right
        elif operator == T_STAR:
            return left * right
        elif operator == T_SLASH:
            if right == 0:
                raise RuntimeError(expr.right.pos_start, expr.right.pos_end, "Division by zero")
            return left / right
        elif operator == T_PERCENT:
            if right == 0:
                raise RuntimeError(expr.right.pos_start, expr.right.pos_end, "Modulus by zero")
            return left % right
        elif operator == T_CARET:
            return left ** right
        elif operator == T_EE:
            return IsEqual(left, right)
        elif operator == T_NE:
            return not IsEqual(left, right)
        elif operator == T_LT:
            return left < right
        elif operator == T_LTE:
            return left <= right
        elif operator == T_GT:
            return left > right
        elif operator == T_GTE:
            return left >= right
        elif operator == T_AND:
            return left and right
        elif operator == T_OR:
            return left or right

    def visitDictionaryExpr(self, expr: DictionaryExpr):
        keys = [self.evaluate(key) for key in expr.keys]
        values = [self.evaluate(value) for value in expr.values]
        d = dict()

        for key in keys:
            d[key] = values[keys.index(key)]

        return d

    def visitFactorialExpr(self, expr: FactorialExpr):
        left = self.evaluate(expr.expr)
        if not IsNumeric(left):
            raise RuntimeError(expr.expr.pos_start, expr.expr.pos_end, "Expected integer to factorialize")

        if ToInt(left) < 0:
            raise RuntimeError(expr.expr.pos_start, expr.expr.pos_end, "Cannot factorialize negative number")

        result = 1
        for i in range(1, ToInt(left) + 1):
            result *= i
        return result        

    def visitUnaryExpr(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)

        operator = expr.operator.type

        if operator == T_MINUS:
            return -right
        elif operator == T_NOT:
            return not right
        elif operator == T_PLUS:
            return right

    def visitCallExpr(self, expr: CallExpr):
        callee = self.evaluate(expr.callee)

        args = []

        for arg in expr.args:
            args.append(self.evaluate(arg))

        if not isinstance(callee, TimidCallable):
            raise RuntimeError(expr.pos_start, expr.pos_end, f"Object of type {type(callee)} is not callable. (Functions and classes are)")

        function : TimidCallable = callee

        if len(args) != function.arity:
            raise RuntimeError(expr.paren.pos_start, expr.pos_end, f"Expected {function.arity} arguments but received {len(args)}")

        return function.call(self, args)

    def visitSubscriptExpr(self, expr: SubscriptExpr):
        iterable = self.evaluate(expr.iterable)

        if not isinstance(iterable, str):
            raise RuntimeError(expr.iterable.pos_start, expr.iterable.pos_end, "Expected an iterable type to subscript")

        index = self.evaluate(expr.subscript)

        if not isinstance(index, int):
            raise RuntimeError(expr.subscript.pos_start, expr.subscript.pos_end, "Expected an integral type as an index")

        if index >= len(iterable):
            raise RuntimeError(expr.subscript.pos_start, expr.subscript.pos_end, "Index is out of bounds")

        return iterable[index]

    def visitVariableExpr(self, expr: VariableExpr):
        return self.environment.get(expr.name)

    def visitTernaryExpr(self, expr: TernaryExpr):
        condition = self.evaluate(expr.condition)
        
        if condition:
            return self.evaluate(expr.if_branch)
        return self.evaluate(expr.else_branch)