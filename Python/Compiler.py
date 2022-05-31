from Enum import iota
from Error import ErrorReporter
from Nodes import *
from Token import Token

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

import struct

### Value types ###
V_INT = iota(True)
V_FLOAT = iota()
V_STRING = iota()

class Value:
    def __init__(self, type : int = V_INT, bytes_ : bytes = None):
        self.type = type
        temp = list(bytes_)
        temp.insert(0, self.type)
        self.bytes_ = bytes(temp)

    @staticmethod
    def init_string_(string : str): # Old method
        chars = list(string)
        length = len(chars)

        strlen = struct.pack('<I', length) # Emit the bytes as an unsigned 32 bit integer

        str_bytes = []

        for byte in strlen:
            str_bytes.append(byte)
                
        for char in chars:
            str_bytes.append(ord(char)) # Convert each character into a byte
        return Value(V_STRING, str_bytes)

    @staticmethod
    def init_string(string : str):
        chars = list(string)

        str_bytes = []

        for char in chars:
            str_bytes.append(ord(char)) # Convert each character into a byte
        str_bytes.append(ord('\0'))
        return Value(V_STRING, str_bytes)

    def __repr__(self):
        byte_str = ""
        i = 0
        for byte in self.bytes_:
            byte_str += hex(byte)[2:].rjust(2, '0') + ' '

            if i >= 7:
                print("")
                i = 0
                continue
        return f"({self.type} | {byte_str})"

class Compiler(Visitor):
    def __init__(self, statements : list[Stmt]):
        self.statements = statements
        self.constants : list[Value] = []
        self.code : list[int] = []

        self.interned_strings : dict[str, int] = {}

        self.locals = []
        self.local_count = 0
        self.scope_depth = 0

        self.debug = False

    def visit(self, expr : Expr | Stmt): expr.accept(self)

    # Variable methods
    def begin_scope(self): self.scope_depth += 1
    def end_scope(self):
        self.scope_depth -= 1

        while self.local_count > 0 and self.locals[self.local_count - 1]["depth"] > self.scope_depth: # Pop all the locals at the end of the scope
            self.emit_byte(OP_POP)
            self.local_count -= 1

    def add_local(self, name : Token):
        local = {
            "name": name,
            "depth": -1 # -1 means not ready for use
        }
        self.locals.append(local)
        self.local_count += 1

    def resolve_local(self, name : Token):
        for i in range(self.local_count - 1, -1, -1):
            local = self.locals[i]
            if (local["name"].lexeme == name.lexeme):
                if local["depth"] == -1:
                    ErrorReporter.resolve_error(name, "Cannot read a variable in its own initializer")
                return i
        return -1

    def parse_variable(self, name : Token) -> int:
        self.declare_variable(name)
        if self.scope_depth > 0: return 0
        return self.identifier_constant(name)

    def mark_initialized(self):
        self.locals[self.local_count - 1]["depth"] = self.scope_depth

    def identifier_constant(self, name : Token) -> int: # Add name to the constant pool and return its index
        new, index = self.register_string(name.lexeme)
        if new:
            self.add_value(Value.init_string(name.lexeme))
        return index

    def define_variable(self, global_idx : int):
        if (self.scope_depth > 0):
            self.mark_initialized()
            return

        self.emit_byte(OP_DEFINE_GLOBAL)
        self.emit_const_w_count(self.constant_count)
        self.emit_1_or_3(global_idx)

    def declare_variable(self, name : Token):
        if (self.scope_depth == 0): return

        for i in range(self.local_count - 1, -1, -1):
            local = self.locals[i]

            # If the variable already exists and is in an outer scope we can declare the variable
            if local["depth"] != -1 and local["depth"] < self.scope_depth: break

            if name.lexeme == local["name"].lexeme:
                ErrorReporter.resolve_error(name, f"Variable '{name.lexeme}' has already been declared in this scope")

        self.add_local(name)

    def named_variable(self, name : Token, is_assign : bool = False):
        get_op, set_op = OP_GET_GLOBAL, OP_SET_GLOBAL

        arg = self.resolve_local(name)
 
        if arg != -1:
            get_op = OP_GET_LOCAL
            set_op = OP_SET_LOCAL
        else:
            arg = self.identifier_constant(name)
            get_op = OP_GET_GLOBAL
            set_op = OP_SET_GLOBAL
        
        if is_assign: self.emit_byte(set_op)
        else: self.emit_byte(get_op)
        self.emit_const_w_count(self.constant_count)
        self.emit_1_or_3(arg)

    def dump(self, bytecode : bytes):
        i = 0
        self.debug = True
        for byte in bytecode:
            print(hex(byte)[2:].rjust(2, '0'), end = ' ')

            if i >= 7:
                print("")
                i = 0
                continue
            i += 1
        print("\n")

    @property
    def constant_count(self): return len(self.constants)

    def add_value(self, value : Value):
        self.constants.append(value)
        #print([', '.join(''.join([chr(int(y)) for y in x.bytes_]) for x in self.constants)])
        return self.constant_count - 1 # Return the index of the appended value

    def make_bytecode(self):
        bytecode = []
        constants = []

        for constant in self.constants:
            constants.extend(constant.bytes_)

        for constant in constants:
            bytecode.append(constant)
        
        bytecode.extend(self.code)
        return bytecode

    def write(self, path : str):
        bytecode = self.make_bytecode()

        # TODO: write to file

        with open(path, "wb") as f:
           f.write(bytes(bytecode))

    def compile(self, path : str):
        self.emit_header()

        for stmt in self.statements: self.visit(stmt)

        self.emit_end()

        #self.dump(self.make_bytecode())
        #self.dump(self.code)

        if ErrorReporter.HAD_ERROR: return

        self.write(path)
        assert not self.debug, "Still in debug mode"

    def register_string(self, string : str):
        if string not in self.interned_strings.keys():
            self.interned_strings[string] = self.constant_count
            return (True, self.constant_count)
        return (False, self.interned_strings[string])

    def emit_1_or_3(self, number : int):
        if number < 256:
            self.emit_byte(number)
        else:
            self.emit_byte(number & 0xff) # Little endian
            self.emit_byte((number >> 8) & 0xff)
            self.emit_byte((number >> 16) & 0xff)

    def emit_byte(self, byte : int): self.code.append(byte)
    def emit_bytes(self, byte1 : int, byte2):
        self.emit_byte(byte1)
        self.emit_byte(byte2)

    def emit_empty_str(self):
        new, index = self.register_string("")
        if new:
            self.add_value(Value.init_string(""))
        self.emit_const_w_count(index)
        self.emit_1_or_3(index)

    def emit_constant(self, value : Value, with_instruction : bool = True):
        index = self.add_value(value)
        if with_instruction:
            self.emit_const_w_count(index)
            self.emit_1_or_3(index)

    def emit_const_w_count(self, count : int):
        self.emit_byte(OP_CONSTANT if count < 256 else OP_CONSTANT_LONG)

    def emit_header(self):
        self.emit_byte(HEADER0)
        self.emit_byte(HEADER1)

    def emit_jump(self, instruction : int):
        self.emit_byte(instruction)
        self.emit_bytes(0xFF, 0xFF)
        return len(self.code) - 2

    def emit_loop(self, stmt, loop_start):
        self.emit_byte(OP_LOOP)

        offset = len(self.code) - loop_start + 2
        if offset > 2**16 - 1:
            ErrorReporter.compile_error(stmt, "Loop body too large")

        self.emit_byte(offset & 0xff)
        self.emit_byte((offset >> 8) & 0xff)

    def patch_jump(self, expr, offset):
        jump = len(self.code) - offset - 2

        if jump > 2**16 - 1:
            ErrorReporter.compile_error(expr, "Too much code to jump")

        self.code[offset] = jump & 0xff # Little endian
        self.code[offset + 1] = (jump >> 8) & 0xff

    def emit_string(self, string : str, with_instruction = True):
        new, index = self.register_string(string)

        if new:

            val = Value.init_string(string)
            i = self.add_value(val)
            if i == index and with_instruction:
                self.emit_const_w_count(index)
                self.emit_1_or_3(index)
        else:
            if with_instruction:
                self.emit_const_w_count(index)
                self.emit_1_or_3(index)

    def emit_end(self): self.emit_byte(OP_RETURN)

    def emit_null(self): self.emit_byte(OP_NULL)

    def emit_pop(self): self.emit_byte(OP_POP)

    ### Statements ###

    def visitBlock(self, block: Block):
        previous_depth = self.scope_depth
        self.begin_scope()
        assert self.scope_depth == previous_depth + 1, "Error in creating new scope"
        for stmt in block.statements:
            self.visit(stmt)
        self.end_scope()

    def visitExprStmt(self, stmt: ExprStmt):
        self.visit(stmt.expr)
        self.emit_pop()

    def visitForStmt(self, stmt: ForStmt):
        if stmt.initializer != None:
            self.visit(stmt.initializer)

        loop_start = len(self.code)
        if stmt.condition != None: self.visit(stmt.condition)
        else: self.emit_byte(OP_TRUE)        

        exit_jump = self.emit_jump(OP_JUMP_IF_FLS)
        self.emit_pop()

        self.visit(stmt.body)

        if stmt.step != None:
            self.visit(stmt.step)

        self.emit_loop(stmt.body, loop_start)

        self.patch_jump(stmt, exit_jump)
        self.emit_pop()

    def visitIfStmt(self, stmt: IfStmt):
        self.visit(stmt.condition)

        then_jump = self.emit_jump(OP_JUMP_IF_FLS)
        self.emit_pop()

        self.visit(stmt.if_branch)

        else_jump = self.emit_jump(OP_JUMP)

        self.patch_jump(stmt.if_branch, then_jump)
        self.emit_pop()

        if stmt.else_branch != None:
            self.visit(stmt.else_branch)

        self.patch_jump(stmt.if_branch if stmt.else_branch == None else stmt.else_branch, else_jump)

    def visitPrintStmt(self, stmt: PrintStmt):
        if stmt.value == None: self.emit_empty_str()
        else: self.visit(stmt.value)
        self.emit_byte(OP_PRINT)

    def visitVarDeclStmt(self, stmt: VarDeclStmt):
        global_idx = self.parse_variable(stmt.name)
        if stmt.initializer == None:
            self.emit_null()
        else:
            self.visit(stmt.initializer)
        self.define_variable(global_idx)

    def visitWhileStmt(self, stmt: WhileStmt):
        loop_start = len(self.code)
        self.visit(stmt.condition)

        exit_jump = self.emit_jump(OP_JUMP_IF_FLS)
        self.emit_pop()

        self.begin_scope()

        self.visit(stmt.body)

        self.end_scope()

        self.emit_loop(stmt.body, loop_start)

        self.patch_jump(stmt, exit_jump)
        self.emit_pop()

    ### Expressions ###

    def visitAssignExpr(self, expr: AssignExpr):
        self.visit(expr.value)
        self.named_variable(expr.name, True)

    def visitBinaryExpr(self, expr: BinaryExpr):
        self.visit(expr.left)
        self.visit(expr.right)

        op = expr.operator.type

        if op == T_PLUS: self.emit_byte(OP_ADD)
        elif op == T_MINUS: self.emit_byte(OP_SUB)
        elif op == T_STAR: self.emit_byte(OP_MUL)
        elif op == T_SLASH: self.emit_byte(OP_DIV)
        elif op == T_PERCENT: self.emit_byte(OP_MOD)
        elif op == T_CARET: self.emit_byte(OP_POW)
        elif op == T_EE: self.emit_byte(OP_EQ)
        elif op == T_NE: self.emit_bytes(OP_EQ, OP_NOT)
        elif op == T_LT: self.emit_byte(OP_LT)
        elif op == T_LTE: self.emit_bytes(OP_GT, OP_NOT)
        elif op == T_GT: self.emit_byte(OP_GT)
        elif op == T_GTE: self.emit_bytes(OP_LT, OP_NOT)
        elif op == T_AND: self.emit_byte(OP_AND)
        elif op == T_OR: self.emit_byte(OP_OR)

    def visitFactorialExpr(self, expr: FactorialExpr):
        self.visit(expr.expr)
        self.emit_byte(OP_FACT)

    def visitInputExpr(self, expr: InputExpr):
        if expr.prompt != None:
            self.visit(expr.prompt)
        else:
            self.emit_empty_str()
        self.emit_byte(OP_GET_INPUT)

    def visitLiteralExpr(self, expr: LiteralExpr):
        value = expr.token.value
        expr_type = expr.token.type

        if expr_type == T_STRING:
            self.emit_string(expr.token.lexeme) 
        elif expr_type in (T_TRUE, T_FALSE): self.emit_byte(OP_TRUE if expr.token.type == T_TRUE else OP_FALSE)
        elif expr_type == T_NULL: self.emit_null()
        elif expr.token.type == T_FLOAT: self.emit_constant(Value(V_FLOAT, struct.pack('=d', value))) #Use native byte order for constants
        elif expr.token.type == T_INT:
            #If the number is a simple number like 1, we can emit an instruction specifically to emit it
            if value == 0: self.emit_byte(OP_0)
            elif value == 1: self.emit_byte(OP_1)
            elif value == 2: self.emit_byte(OP_2)
            else:
                # Add value to constant pool then add instruction
                self.emit_constant(Value(V_INT, struct.pack('=q', value)))

    def visitSubscriptExpr(self, expr: SubscriptExpr): # Like list indexing or dictionary key access
        self.visit(expr.iterable)
        self.visit(expr.subscript)
        self.emit_byte(OP_SUBSCRIPT)

    def visitTernaryExpr(self, expr: TernaryExpr): # Exactly like if statement
        self.visit(expr.condition)

        then_jump = self.emit_jump(OP_JUMP_IF_FLS)
        self.emit_pop()

        self.visit(expr.if_branch)

        else_jump = self.emit_jump(OP_JUMP)

        self.patch_jump(expr.if_branch, then_jump)
        self.emit_pop()

        if expr.else_branch != None:
            self.visit(expr.else_branch)

        self.patch_jump(expr.else_branch, else_jump)

    def visitUnaryExpr(self, expr: UnaryExpr):
        self.visit(expr.right)

        op = expr.operator.type

        if op == T_MINUS:
            if self.code[-1] == OP_1: # If the number is -1 we can emit a specific instruction for it
                self.code[-1] = OP_NEG1
                return
            self.emit_byte(OP_NEGATE)
        elif op == T_NOT: self.emit_byte(OP_NOT)
        elif op == T_PLUS: return

    def visitVariableExpr(self, expr: VariableExpr):
        self.named_variable(expr.name)