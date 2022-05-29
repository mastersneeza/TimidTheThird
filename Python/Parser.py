from Error import ErrorReporter
from Nodes import *
from Token import Token

MAX_ARG_COUNT = 255

class ParseError(Exception): pass

class Parser:
    def __init__(self, tokens : list[Token]):
        self.tokens = tokens
        self.index = 0

    @property
    def current_tok(self) -> Token: return self.tokens[self.index]
    @property
    def next_tok(self) -> Token:
        if self.is_at_end: return self.tokens[-1]
        return self.tokens[self.index + 1]
    @property
    def previous_tok(self) -> Token: return self.tokens[self.index - 1]

    def error(self, token : Token, message : str):
        ErrorReporter.syntax_error(token, message)
        return ParseError()

    def consume(self, message : str, *types : tuple[int]):
        for type in types:
            if self.check(type):
                self.advance()
                return self.previous_tok
        raise self.error(self.current_tok, message)

    @property
    def is_at_end(self) -> bool: return self.current_tok.type == T_EOF

    def advance(self) -> Token:
        if not self.is_at_end: self.index += 1
        return self.previous_tok

    def check(self, type : int):
        if self.is_at_end: return False
        return self.current_tok.type == type        

    def match(self, *types : int):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def matcht(self, types : tuple[int]): # Match for a tuple
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def synchronize(self):
        self.advance()
        while not self.is_at_end:
            if self.previous_tok.type in (T_SEMIC, ): return

            tok_type = self.current_tok.type

            if tok_type in (T_LAMBDA, T_CONST, T_PRINT, T_IF, T_WHILE, T_DOLLAR, T_LCURL, T_ASSERT, T_FOR):
                return

            self.advance()

    def parse(self):
        try:
            statements = []
            while not self.is_at_end:
                stmt = self.declaration()
                if stmt == None:
                    break
                statements.append(stmt)

            if not ErrorReporter.HAD_ERROR and self.current_tok.type != T_EOF:
                self.error(self.current_tok, f"Failed to parse token '{self.current_tok.lexeme}'")

            return statements
        except ParseError:
            return None

    def declaration(self):
        try:
            if self.match(T_DOLLAR):
                return self.var_decl()
            return self.statement()
        except ParseError:
            self.synchronize()

    def var_decl(self):
        name : Token = self.consume("Expected an identifier (after '$')", T_IDENTIFIER)
        initializer : Expr = None
        if self.match(T_EQ):
            initializer = self.expr()
        
        e = VarDeclStmt(name, initializer)
        return e

    def statement(self):
        while self.match(T_SEMIC): pass # Ignore random semicolons or newlines
        if self.is_at_end or self.check(T_RCURL): # If end of file or end of block, ignore
            return None
        if self.match(T_WHILE): return self.while_stmt()
        if self.match(T_FOR): return self.for_stmt()
        if self.match(T_IF): return self.if_stmt()
        if self.match(T_PRINT): return self.print_stmt()
        if self.match(T_LCURL): return self.block()
        if self.match(T_ASSERT):
            kw = self.previous_tok
            condition = self.expr()
            message = self.expr()
            
            return AssertStmt(kw, condition, message)
        return self.expr_stmt()

    def for_stmt(self):
        return ForStmt()

    def while_stmt(self):
        condition = self.expr()
        body = self.statement()
        return WhileStmt(condition, body)

    def block(self):
        lcurl = self.previous_tok
        statements = []
        while not self.check(T_RCURL) and not self.is_at_end:
            stmt = self.declaration()
            if stmt == None:
                break
            statements.append(stmt)
        rcurl = self.consume("Expected a closing '}' (after '{' or previous statement)", T_RCURL)
        return Block(lcurl, statements, rcurl)

    def if_stmt(self):
        condition = self.expr()

        if_branch = self.statement()
        else_branch = None

        if self.match(T_ELSE):
            else_branch = self.statement()
        
        return IfStmt(condition, if_branch, else_branch)

    def print_stmt(self):
        value = self.expr()
        return PrintStmt(value)
    
    def expr_stmt(self):
        value = self.expr()
        return ExprStmt(value)

    # Expressions

    def expr(self):
        return self.ternary()
    
    def ternary(self):
        condition = self.assignment()

        if self.match(T_QMARK):
            if_branch = self.expr()

            self.consume("Expected a ':' (after if branch)", T_COLON)

            else_branch = self.expr()

            return TernaryExpr(condition, if_branch, else_branch)

        return condition

    def assignment(self):
        expr = self.lambda_expr()
        if (self.match(T_EQ)):
            value = self.assignment()

            if (isinstance(expr, VariableExpr)):
                return AssignExpr(expr.name, value)

            self.error(expr, "Invalid assignment target")
        return expr
    def lambda_expr(self):
        if self.match(T_LAMBDA):
            keyword : Token = self.previous_tok
            identifier : Token = self.consume("Expected an identifier (after 'lam' keyword)", T_IDENTIFIER)
            if self.is_at_end:
                raise self.error(self.current_tok, f"Expected a lambda expression body (after identifier '{self.previous_tok.lexeme}')")
            body = self.expr()
            return LambdaExpr(keyword, identifier, body)
        return self.or_expr()

    def or_expr(self): return self.bin_op(self.and_expr, (T_OR, ))
    def and_expr(self): return self.bin_op(self.equality, (T_AND, ))
    def equality(self): return self.bin_op(self.comparison, (T_EE, T_NE))
    def comparison(self): return self.bin_op(self.sum, (T_LT, T_LTE, T_GT, T_GTE))
    def sum(self): return self.bin_op(self.term, (T_PLUS, T_MINUS))
    def term(self): return self.bin_op(self.unary, (T_STAR, T_SLASH, T_PERCENT))

    def unary(self):
        if self.match(T_PLUS, T_MINUS, T_NOT):
            operator : Token = self.previous_tok
            if self.is_at_end:
                raise self.error(self.current_tok, f"Expected a unary operand (after unary operator '{self.previous_tok.lexeme}')")
            right : UnaryExpr = self.unary()
            return UnaryExpr(operator, right)
        return self.power()

    def power(self): return self.bin_op(self.factorial, (T_CARET, ), self.unary)

    def factorial(self):
        expr = self.call()

        if self.match(T_NOT):
            expr = FactorialExpr(expr)
        return expr

    def call(self):
        expr = self.atom()

        while True:
            if self.match(T_LPAR):
                expr = self.finish_call(expr)
            elif self.match(T_LSQR):
                expr = self.finish_subscript(expr)
            else:
                break

        return expr

    def atom(self):
        if self.match(T_IN):
            kw = self.previous_tok
            try:
                prompt = self.expr()
            except ParseError:
                prompt = None
            return InputExpr(prompt, kw)
        if self.match(T_INT, T_FLOAT, T_STRING, T_TRUE, T_FALSE, T_NULL): return LiteralExpr(self.previous_tok)
        if self.match(T_IDENTIFIER): return VariableExpr(self.previous_tok)
        if self.match(T_LPAR):
            lpar = self.previous_tok
            expr : Expr = self.expr() # Can be an expression or a dictionary key
            if self.match(T_COLON): # Dictionary literal
                keys = [expr]
                values = []

                values.append(self.expr())

                if self.match(T_COMMA):

                    while True:
                        keys.append(self.expr())
                        self.consume("Expected a ':' after dictionary key", T_COLON)
                        values.append(self.expr())

                        if self.check(T_COMMA) and self.next_tok.type == T_RPAR:
                            self.advance()
                            break

                        if not self.match(T_COMMA):
                            break
                    
                rpar = self.consume(f"Expected a ')' (after '{self.previous_tok.lexeme}')", T_RPAR) # Grouping
                return DictionaryExpr(lpar, rpar, keys, values)
            else:
                self.consume(f"Expected a ')' (after '{self.previous_tok.lexeme}')", T_RPAR) # Grouping
            return expr
        raise self.error(self.current_tok, "Expected an expression")

    def finish_subscript(self, atom : Expr):
        subscript = self.expr()

        self.consume("Expected a closing ']' after subscriptio", T_RSQR)
        return SubscriptExpr(atom, subscript)

    def finish_call(self, callee : Expr):
        arguments = []

        if not self.check(T_RPAR):
            while True:
                if len(arguments) > MAX_ARG_COUNT:
                    self.error(self.current_tok, f"Maximum argument count ({MAX_ARG_COUNT}) reached")
                
                arguments.append(self.expr())

                if self.check(T_COMMA) and self.next_tok.type == T_RPAR:
                    self.advance()
                    break

                if not self.match(T_COMMA):
                    break

        r_par = self.consume("Expected a closing ')' after function call", T_RPAR)
        return CallExpr(callee, r_par, arguments)

    def bin_op(self, left_rule : type, operators : tuple[int], right_rule : type = None) -> BinaryExpr | Expr:
        if right_rule == None: right_rule = left_rule
        left : Expr = left_rule()

        while self.matcht(operators):
            operator : Token = self.previous_tok
            if self.is_at_end:
                raise self.error(self.current_tok, f"Expected a right binary operand (after '{operator.lexeme}')")
            right : Expr = right_rule()
            left = BinaryExpr(left, operator, right)

        return left