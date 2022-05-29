from Nodes import *

import struct

### Opcodes ###
OP_NOP = iota(True)
OP_CONSTANT = iota()
OP_CONSTANT_LONG = iota()
OP_NEG1 = iota()
OP_0 = iota()
OP_1 = iota()
OP_2 = iota()

OP_TRUE = iota()
OP_FALSE = iota()
OP_NULL = iota()

OP_PRINT = iota()
OP_POP = iota()
OP_NEGATE = iota()
OP_NOT = iota()
OP_FACT = iota()

OP_ADD = iota()
OP_SUB = iota()
OP_MUL = iota()
OP_DIV = iota()
OP_MOD = iota()
OP_POW = iota()
OP_EQ = iota()
OP_LT = iota()
OP_GT = iota()
OP_AND = iota()
OP_OR = iota()

OP_JUMP_IF_FLS = iota()
OP_JUMP = iota()
OP_LOOP = iota()

OP_DEFINE_GLOBAL = iota()
OP_GET_GLOBAL = iota()
OP_SET_GLOBAL = iota()
OP_GET_LOCAL = iota()
OP_SET_LOCAL = iota()

OP_GET_INPUT = iota()

OP_SUBSCRIPT = iota()

OP_RETURN = iota()

### Headers ###
HEADER0 = 0xFA

HEADER1 = 0xCC
STRING0 = 0xCC
STRING1 = 0xFA
INT = 0x99
FLOAT = 0x69

class Compiler(Visitor):
    def __init__(self, statements : list[Stmt]):
        self.stmts = statements
        self.bytecode = []
        self.constant_count = 0
        self.emit_header()
        self.locals = []
        self.local_count = 0
        self.scope_depth = 0

    def add_local(self, name : Token):
        local = {
            "name": name,
            "depth": self.scope_depth
        }
        self.locals.append(local)

    def begin_scope(self):
        self.scope_depth += 1

    def end_scope(self):
        self.scope_depth -= 1

    def emit_byte(self, byte):
        self.bytecode.append(byte)

    def emit_bytes(self, byte1, byte2):
        self.emit_byte(byte1)
        self.emit_byte(byte2)

    def emit_1_or_3_bytes(self, number : int):
        if number < 256:
            self.emit_byte(number)
        else:
            self.emit_byte(number & 0xff) # Little endian
            self.emit_byte((number >> 8) & 0xff)
            self.emit_byte((number >> 16) & 0xff)

    def emit_constant(self):
        self.constant_count += 1
        self.emit_constant_count(self.constant_count)

    def emit_constant_count(self, count : int):
        self.emit_byte(OP_CONSTANT if count < 256 else OP_CONSTANT_LONG)

    def emit_null(self):
        self.emit_byte(OP_NULL)

    def emit_string(self, string : str, with_instruction = True):
        if with_instruction:
            self.emit_constant()
        else:
            self.constant_count += 1
        self.emit_byte(STRING0) # Add a header to know we are adding a string
        
        chars = list(string)

        length = len(chars)

        strlen = struct.pack('<I', length) # Emit the bytes as an unsigned integer
        for byte in strlen:
            self.emit_byte(byte)
                
        for char in chars:
            self.emit_byte(ord(char)) # Convert each character into a byte

    def emit_identifier(self, identifier : str):
        self.emit_string(identifier, False) # Store the variable's name as a string
        global_index = self.constant_count - 1 # Get the index of the string in the constant pool
        return global_index

    def emit_variable(self, instruction : int, name : str):
        self.emit_byte(instruction)
        Compiler.resolve_local(self, name)
        global_index = self.emit_identifier(name) # Add the string to the constant pool without adding it to the stack
        self.emit_constant_count(global_index) # Tell the VM how to interpret the next bytes
        self.emit_1_or_3_bytes(global_index) # The index as bytes

    def emit_header(self):
        self.emit_bytes(HEADER0, HEADER1)

    def declare_variable(self, name : Token):
        if (self.scope_depth == 0): return
        self.add_local(name)

    def compile(self):
        for stmt in self.stmts:
            self.visit(stmt)
        self.emit_byte(OP_RETURN)
        return self.bytecode

    def visit(self, expr : Expr|Stmt):
        expr.accept(self)

    def visitPrintStmt(self, stmt: PrintStmt):
        self.visit(stmt.value)
        self.emit_byte(OP_PRINT)

    def visitIfStmt(self, stmt: IfStmt):
        self.visit(stmt.condition)
        self.visit(stmt.if_branch)
        if stmt.else_branch != None:
            self.visit(stmt.else_branch)

    def visitExprStmt(self, stmt: ExprStmt):
        self.visit(stmt.expr)
        self.emit_byte(OP_POP)

    def visitBlock(self, block: Block):
        self.begin_scope()
        for stmt in block.statements:
            self.visit(stmt)
        self.end_scope()
    
    def visitVarDeclStmt(self, stmt: VarDeclStmt):
        # Emit the initializer bytecode so its on top of the stack
        if stmt.initializer == None: # Interpret the initializer
            self.emit_null()
        else:
            self.visit(stmt.initializer)
        self.declare_variable(stmt.name)
        if (self.scope_depth > 0): return
        self.emit_variable(OP_DEFINE_GLOBAL, stmt.name.lexeme)

    def visitAssignExpr(self, expr: AssignExpr):
        self.visit(expr.value)
        self.emit_variable(OP_SET_GLOBAL, expr.name.lexeme)

    def visitTernaryExpr(self, expr: TernaryExpr):
        self.visit(expr.condition)
        self.visit(expr.if_branch)
        self.visit(expr.else_branch)

    def visitVariableExpr(self, expr: VariableExpr):
        self.emit_variable(OP_GET_GLOBAL, expr.name.lexeme)

    def visitLambdaExpr(self, expr: LambdaExpr):
        self.visit(expr.body)

    @staticmethod
    def resolve_local(compiler, name : Token) -> int:
        for i in range(compiler.local_count - 1, 0, -1):
            local = compiler.locals[i]
            if name.lexeme == local["name"].lexeme:
                return i
        return -1

    def visitLiteralExpr(self, expr: LiteralExpr):
        value = expr.token.value
        expr_type = expr.token.type

        if expr_type == T_STRING: # Format: (OP_CONSTANT | OP_CONSTANT_LONG) header (length of characters as four byte int) (list of characters as bytes) 
            # OP_CONSTANT STRING0 STRING1 length chars
            self.emit_string(expr.token.lexeme) 
        elif expr_type in (T_TRUE, T_FALSE): self.emit_byte(OP_TRUE if expr.token.type == T_TRUE else OP_FALSE)
        elif expr_type == T_NULL: self.emit_null()
        elif expr.token.type == T_FLOAT:
            self.emit_constant()
            self.emit_byte(0x69) # Float header
            self.bytecode.extend(struct.pack('<d', value))
        elif expr.token.type == T_INT:
            #If the number is a simple number like 1, we can emit an instruction specifically to emit it
            if value == 0: self.emit_byte(OP_0)
            elif value == 1: self.emit_byte(OP_1)
            elif value == 2: self.emit_byte(OP_2)
            else:
                self.emit_constant()
                self.emit_byte(0x99) # Int header
                self.bytecode.extend(struct.pack('<q', value))

    def visitInputExpr(self, expr: InputExpr):
        if expr.prompt != None:
            self.visit(expr.prompt)
        self.emit_byte(OP_GET_INPUT)

    def visitCallExpr(self, expr: CallExpr):
        self.visit(expr.callee)
        for arg in expr.args:
            self.visit(arg)

    def visitUnaryExpr(self, expr : UnaryExpr):
        self.visit(expr.right)

        op = expr.operator.type

        if op == T_MINUS:
            if self.bytecode[-1] == OP_1: # If the number is -1 we can emit a specific instruction for it
                self.bytecode[-1] = OP_NEG1
                return
            self.emit_byte(OP_NEGATE)
        elif op == T_NOT:
            self.emit_byte(OP_NOT)
        elif op == T_PLUS:
            return
        
    def visitBinaryExpr(self, expr : BinaryExpr):
        self.visit(expr.left)
        self.visit(expr.right)

        op = expr.operator.type

        if op == T_PLUS:
            self.emit_byte(OP_ADD)
        elif op == T_MINUS:
            self.emit_byte(OP_SUB)
        elif op == T_STAR:
            self.emit_byte(OP_MUL)
        elif op == T_SLASH:
            self.emit_byte(OP_DIV)
        elif op == T_PERCENT:
            self.emit_byte(OP_MOD)
        elif op == T_CARET:
            self.emit_byte(OP_POW)
        elif op == T_EE:
            self.emit_byte(OP_EQ)
        elif op == T_NE:
            self.emit_bytes(OP_EQ, OP_NOT)
        elif op == T_LT:
            self.emit_byte(OP_LT)
        elif op == T_LTE:
            self.emit_bytes(OP_GT, OP_NOT)
        elif op == T_GT:
            self.emit_byte(OP_GT)
        elif op == T_GTE:
            self.emit_bytes(OP_LT, OP_NOT)
        elif op == T_AND:
            self.emit_byte(OP_AND)
        elif op == T_OR:
            self.emit_byte(OP_OR)

    def visitFactorialExpr(self, expr: FactorialExpr):
        self.visit(expr.expr)
        self.emit_byte(OP_FACT)