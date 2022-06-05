from Error import ErrorReporter
from Nodes import *
from Token import Token

MAX_ARG_COUNT = 255
MAX_NEST_DEPTH = 40

class ParseError(Exception): pass

class Parser:
    def __init__(self, tokens : list[Token]):
        self.tokens = tokens
        self.index = 0
        self.nest_depth = 0

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
                return self.advance()
        raise self.error(self.current_tok, message)

    def check_nonterminal(self, nont : Expr|Stmt|None, message : str):
        if nont == None:
            raise self.error(self.current_tok, message + f" (after '{self.previous_tok.lexeme}')")

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
        self.nest_depth = 0
        self.advance()
        while not self.is_at_end:
            if self.previous_tok.type in (T_SEMIC, ): return

            tok_type = self.current_tok.type

            if tok_type in (T_LAMBDA, T_CONST, T_PRINT, T_IF, T_WHILE, T_DOLLAR, T_LCURL, T_ASSERT, T_FOR, T_FOREVER, T_GOTO):
                return

            self.advance()

    def parse(self):
        try:
            statements = []
            while not self.is_at_end:
                stmt = self.declaration()

                if stmt == None: # If there are trailing newlines then return the statements
                    break
                statements.append(stmt)

            if not ErrorReporter.HAD_ERROR and self.current_tok.type != T_EOF:
                self.error(self.current_tok, f"Failed to parse token '{self.current_tok.lexeme}'")

            return statements
        except ParseError:
            return None

    def declaration(self, nullable = False):
        try:
            while self.match(T_SEMIC): pass # Ignore random semicolons or newlines
            if self.is_at_end: # If end of file or end of block, ignore
                return None
            if self.match(T_DOLLAR):
                return self.var_decl(nullable)
            return self.statement(nullable)
        except ParseError:
            self.synchronize()

    def var_decl(self, nullable = False):
        name : Token = self.consume("Expected an identifier (after '$')", T_IDENTIFIER)
        initializer : Expr = None
        if self.match(T_EQ):
            initializer = self.expr(True)

            self.check_nonterminal(initializer, "Expected a variable initializer")
        
        return VarDeclStmt(name, initializer)

    def statement(self, nullable = False):
        while self.match(T_SEMIC): pass # Ignore random semicolons or newlines
        if self.is_at_end or self.check(T_RCURL): # If end of file or end of block, ignore
            return None
        if self.match(T_WHILE): return self.while_stmt(nullable)
        if self.match(T_FOREVER):
            kw = self.previous_tok
            body = self.statement(True)
            self.check_nonterminal(body, "Expected a 'forever' loop body")
            return ForeverStmt(kw, body)
        if self.match(T_FOR): return self.for_stmt(nullable)
        if self.match(T_IF): return self.if_stmt(nullable)
        if self.match(T_PRINT): return self.print_stmt(nullable)
        if self.match(T_LCURL): return self.block(nullable)
        if self.match(T_ASSERT):
            kw = self.previous_tok
            condition = self.expr(nullable)
            message = self.expr(True)
            
            return AssertStmt(kw, condition, message)
        if self.check(T_IDENTIFIER) and self.next_tok.type == T_COLON:
            name = self.advance()
            self.advance() # Consume colon

            return Label(name)
        if self.match(T_GOTO):
            label = self.consume("Expected a label", T_IDENTIFIER)
            return GotoStmt(label)
        if self.match(T_BREAK): return BreakStmt(self.previous_tok)
        if self.match(T_CONTINUE): return ContinueStmt(self.previous_tok)
        return self.expr_stmt(nullable)

    def for_stmt(self, nullable = False):
        kw = self.previous_tok
        if self.match(T_DOLLAR):
            initializer = self.var_decl(True)
        else:
            initializer = self.expr(True)
        self.consume("Expected a ',' or initializer statement after 'for' keyword", T_COMMA)
        condition = self.expr(True)
        self.consume("Expected a ',' after initializer or ','", T_COMMA)
        step = self.expr(True)
        body = self.statement(True)
        self.check_nonterminal(body, "Expected a 'for' loop body")
        return ForStmt(kw, body, initializer, condition, step)

    def while_stmt(self, nullable = False):
        self.nest_depth += 1
        if self.nest_depth >= MAX_NEST_DEPTH:
            raise self.error(self.current_tok, "Maximum block nesting depth reached")
        condition = self.expr(True)

        if condition == None:
            raise self.error(self.current_tok, f"Expected a 'while' loop condition (after '{self.previous_tok.lexeme}' token)")

        body = self.statement(True)

        if body == None:
            raise self.error(self.current_tok, f"Expected a 'while' loop body (after '{self.previous_tok.lexeme}')")
        self.nest_depth -= 1
        return WhileStmt(condition, body)

    def block(self, nullable = False):
        lcurl = self.previous_tok
        self.nest_depth += 1
        if self.nest_depth >= MAX_NEST_DEPTH:
            raise self.error(lcurl, "Maximum block nesting depth reached")

        statements = []
        while not self.check(T_RCURL) and not self.is_at_end:
            stmt = self.declaration(True)
            if stmt == None:
                break
            statements.append(stmt)
        rcurl = self.consume("Expected a closing '}' (after '{' or previous statement)", T_RCURL)
        self.nest_depth -= 1
        return Block(lcurl, statements, rcurl)

    def if_stmt(self, nullable = False):
        self.nest_depth += 1
        if self.nest_depth >= MAX_NEST_DEPTH:
            raise self.error(self.current_tok, "Maximum block nesting depth reached")
        condition = self.expr(True)

        if condition == None:
            raise self.error(self.current_tok, f"Expected an 'if' statement condition (after '{self.previous_tok.lexeme}')")

        if_branch = self.statement(True)

        self.check_nonterminal(if_branch, f"Expected an 'if' statement body")

        else_branch = None

        if self.match(T_ELSE):
            else_branch = self.statement(True)

            if else_branch == None:
                raise self.error(self.current_tok, f"Expected an 'else' clause body (after '{self.previous_tok.lexeme}')")

        self.nest_depth -= 1
        return IfStmt(condition, if_branch, else_branch)

    def print_stmt(self, nullable = False):
        kw = self.previous_tok
        value = self.expr(True) # There can be nothing to print
        return PrintStmt(kw, value)
    
    def expr_stmt(self, nullable = False):
        value = self.expr(True)
        self.check_nonterminal(value, "Expected a statement")
        return ExprStmt(value)

    # Expressions

    def expr(self, nullable = False):
        return self.assignment(nullable)

    def assignment(self, nullable = False):
        expr = self.ternary(nullable)
        if self.match(T_EQ, T_PLUS_ASSIGN, T_MINUS_ASSIGN, T_STAR_ASSIGN, T_SLASH_ASSIGN, T_PERCENT_ASSIGN, T_CARET_ASSIGN):
            operand = self.previous_tok
            invalid = False
            value = self.assignment(True)

            if (not isinstance(expr, VariableExpr)):
                self.error(expr, "Invalid assignment target")
                invalid = True

            if value == None:
                raise self.error(self.current_tok, f"Expected an assignment value (after '{self.previous_tok.lexeme}')")

            if not invalid:
                return AssignExpr(expr.name, value, operand)

        return expr

    def ternary(self, nullable = False):
        condition = self.lambda_expr(nullable)

        if self.match(T_QMARK):
            if_branch = self.expr(True)

            if if_branch == None:
                raise self.error(self.current_tok, f"Expected a ternary operator False branch (after '{self.previous_tok.lexeme}')")

            self.consume(f"Expected a ':' in ternary operator (after '{self.previous_tok.lexeme}')", T_COLON)

            else_branch = self.expr(True)

            if else_branch == None:
                raise self.error(self.current_tok, f"Expected a ternary operator True branch (after '{self.previous_tok.lexeme}')")

            return TernaryExpr(condition, if_branch, else_branch)
        return condition

    def lambda_expr(self, nullable = False):
        if self.match(T_LAMBDA):
            keyword : Token = self.previous_tok
            identifier : Token = self.consume("Expected an identifier (after 'lam' keyword)", T_IDENTIFIER)
            if self.is_at_end:
                raise self.error(self.current_tok, f"Expected a lambda expression body (after identifier '{self.previous_tok.lexeme}')")
            body = self.expr(nullable)
            return LambdaExpr(keyword, identifier, body)
        return self.or_expr(nullable)

    def or_expr(self, nullable = False):     return self.bin_op(self.and_expr, (T_OR, ), nullable = nullable)
    def and_expr(self, nullable = False):    return self.bin_op(self.equality, (T_AND, ), nullable = nullable)
    def equality(self, nullable = False):    return self.bin_op(self.comparison, (T_EE, T_NE), nullable = nullable)
    def comparison(self, nullable = False):  return self.bin_op(self.sum, (T_LT, T_LTE, T_GT, T_GTE), nullable = nullable)
    def sum(self, nullable = False):         return self.bin_op(self.term, (T_PLUS, T_MINUS), nullable = nullable)
    def term(self, nullable = False):        return self.bin_op(self.unary, (T_STAR, T_SLASH, T_PERCENT), nullable = nullable)

    def unary(self, nullable = False):
        if self.match(T_PLUS, T_MINUS, T_NOT):
            operator : Token = self.previous_tok
            right : UnaryExpr = self.unary(True)

            if right == None:
                raise self.error(self.current_tok, f"Expected a unary operand (after unary operator '{self.previous_tok.lexeme}')")
            return UnaryExpr(operator, right)
        return self.power(nullable)

    def power(self, nullable = False): return self.bin_op(self.factorial, (T_CARET, ), self.unary, nullable)

    def factorial(self, nullable = False):
        expr = self.call(nullable)

        while self.match(T_NOT): # There can be as many !s after the expression
            expr = FactorialExpr(expr)
        return expr

    def call(self, nullable = False):
        expr = self.atom(nullable)

        while True:
            if self.match(T_LPAR):
                expr = self.finish_call(expr)
            elif self.match(T_LSQR):
                expr = self.finish_subscript(expr)
            else:
                break

        return expr

    def atom(self, nullable = False):
        if self.match(T_IN):
            kw = self.previous_tok
            prompt = self.expr(True) # There may not be a prompt
            return InputExpr(prompt, kw)
        if self.match(T_INT, T_FLOAT, T_STRING, T_TRUE, T_FALSE, T_NULL): return LiteralExpr(self.previous_tok)
        if self.match(T_IDENTIFIER):
            if self.match(T_COLON):
                raise self.error(self.previous_tok, "Goto label in expression")
            return VariableExpr(self.previous_tok)
        if self.match(T_LPAR):
            self.nest_depth += 1
            if self.nest_depth >= MAX_NEST_DEPTH:
                raise self.error(self.current_tok, "Maximum parentheses nesting depth reached")
            lpar = self.previous_tok
            expr : Expr = self.expr() # Can be an expression or a dictionary key
            if self.match(T_COLON): # Dictionary literal
                keys = [expr]
                values = []

                value = self.expr(True)

                if value == None:
                    raise self.error(self.current_tok, f"Expected an initial dictionary value (after '{self.previous_tok.lexeme}')")
                values.append(value) # There must be a value

                if self.match(T_COMMA): # If there is comma we might have more entries
                    while True:
                        key = self.expr(True)
                        if key == None:
                            break
                        keys.append(key)

                        self.consume("Expected a ':' after dictionary key", T_COLON)

                        value = self.expr(True)

                        if value == None:
                            raise self.error(self.current_tok, f"Expected a dictionary value (after '{self.previous_tok.lexeme}')")
                        values.append(value)

                        if self.check(T_COMMA) and self.next_tok.type == T_RPAR: # Traling commas are allowed
                            self.advance() # Consume the trailing comma, and let the ')' be consumed by the consume function
                            break
                    
                rpar = self.consume(f"Expected a closing ')' for dictionary (after '{self.previous_tok.lexeme}')", T_RPAR) # Grouping
                self.nest_depth -= 1
                return DictionaryExpr(lpar, rpar, keys, values)
            else:
                self.consume(f"Expected a closing ')' for grouping (after '{self.previous_tok.lexeme}')", T_RPAR) # Grouping
                self.nest_depth -= 1
            return expr

        if not nullable:
            raise self.error(self.current_tok, "Expected an expression, a boolean, a string, a number, or 'nul'") # Default error message
        
        return None

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

    def bin_op(self, left_rule : type, operators : tuple[int], right_rule : type = None, nullable = False) -> BinaryExpr | Expr:
        if right_rule == None: right_rule = left_rule
        left : Expr = left_rule(nullable)

        while self.matcht(operators):
            operator : Token = self.previous_tok
            right : Expr = right_rule(True)

            if right == None:
                raise self.error(self.current_tok, f"Expected a right binary operand (after '{operator.lexeme}')")

            left = BinaryExpr(left, operator, right)

        return left