from Enum import iota
from Error import ErrorReporter
from Nodes import *
from Token import Token
from Globals import COMPILER_DEBUG
from Opcodes import *

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

class Chunk:
    def __init__(self):
        self.code : list[int] = []
        self.constants : list[Value] = []

    @property
    def code_length(self): return len(self.code)

    @property
    def constant_count(self): return len(self.constants)

    @property
    def as_bytes(self):
        bytecode = []
        constants = []

        for constant in self.constants:
            constants.extend(constant.bytes_)

        for constant in constants:
            bytecode.append(constant)
        
        bytecode.extend(self.code)
        return bytecode

    def emit_byte(self, byte : int):
        self.code.append(byte)

    def emit_bytes(self, *bytes : tuple[int]):
        for byte in bytes: self.emit_byte(byte)

    def emit_1_or_3(self, index : int):
        if index < 256: self.emit_byte(index)
        else: self.emit_bytes(index & 0xff, (index >> 8) & 0xff, (index >> 16) & 0xff)

    def emit_constant(self, value : Value, with_instruction : bool = True):
        index = self.add_value(value)
        if with_instruction:
            self.emit_const_w_count(index)
            self.emit_1_or_3(index)

    def emit_const_w_count(self, count : int): self.emit_byte(OP_CONSTANT if count < 256 else OP_CONSTANT_LONG)

    def emit_header(self): self.emit_bytes(HEADER0, HEADER1)

    def emit_jump(self, instruction : int):
        self.emit_byte(instruction)
        self.emit_bytes(0xFF, 0xFF)
        return self.code_length - 2 # Return position of jump instruction in code

    def emit_loop(self, stmt : Stmt, loop_start):
        self.emit_byte(OP_LOOP)
        loop_distance = self.code_length - loop_start + 2 # Jump to the start of the loop, taking into account the two bytes used

        if loop_distance > 2**16 - 1:
            ErrorReporter.compile_error(stmt, "Loop body too large")
        
        self.emit_bytes(loop_distance & 0xff, (loop_distance >> 8) & 0xff)

    def emit_end(self): self.emit_byte(OP_RETURN)

    def emit_null(self): self.emit_byte(OP_NULL)

    def emit_pop(self): self.emit_byte(OP_POP)

    def patch_jump(self, expr : Stmt | Expr, jump_idx):
        jump_distance = len(self.code) - jump_idx - 2 # Get jump size

        if jump_distance > 2**16 - 1:
            ErrorReporter.compile_error(expr, "Too much code to jump")

        self.code[jump_idx] = jump_distance & 0xff # Little endian
        self.code[jump_idx + 1] = (jump_distance >> 8) & 0xff

    def add_value(self, value : Value):
        self.constants.append(value)
        return self.constant_count - 1 # Return the index of the appended value

    def dump(self, bytecode : bytes):
        i = 0
        for byte in bytecode:
            clog(hex(byte)[2:].rjust(2, '0'), end = ' ')

            if i >= 7:
                clog()
                i = 0
                continue
            i += 1
        clog("\n")

def clog(message, end = '\n'): # Prints only if debug is enabled
    if COMPILER_DEBUG:
        print(message, end = end)
    
class Compiler(Visitor):
    def __init__(self, statements : list[Stmt]):
        self.statements = statements
        self._chunk = Chunk()

        self.interned_strings : dict[str, int] = {}

        self.locals = []
        self.local_count = 0
        self.scope_depth = 0

        self.break_position = -1
        self.continue_position = -1

        self.inner_loop_start = -1
        self.inner_loop_end = -1
        self.breaking = False
        self.continuing = False

        self.continue_type = OP_LOOP # Because continue in for loops can jump either forwards or backwards, but typically it jumps back to the top

    @property
    def chunk(self): return self._chunk

    def visit(self, expr : Expr | Stmt): expr.accept(self)

    # Variable methods
    def begin_scope(self): self.scope_depth += 1
    def end_scope(self):
        self.scope_depth -= 1

        while self.local_count > 0 and self.locals[self.local_count - 1]["depth"] > self.scope_depth: # Pop all the locals at the end of the scope
            clog("End scope pop")
            self.chunk.emit_pop()
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
            self.chunk.add_value(Value.init_string(name.lexeme))
        return index

    def define_variable(self, global_idx : int):
        if (self.scope_depth > 0):
            self.mark_initialized()
            return

        self.chunk.emit_byte(OP_DEFINE_GLOBAL)
        self.chunk.emit_const_w_count(self.chunk.constant_count)
        self.chunk.emit_1_or_3(global_idx)

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
        
        if is_assign:
            self.chunk.emit_byte(set_op)
        else:
            self.chunk.emit_byte(get_op)
        self.chunk.emit_const_w_count(self.chunk.constant_count)
        self.chunk.emit_1_or_3(arg)

    def write(self, path : str):
        bytecode = self.chunk.as_bytes

        # TODO: write to file

        with open(path, "wb") as f:
           f.write(bytes(bytecode))

    def dump(self): self.chunk.dump(self.chunk.as_bytes)

    def compile(self, path : str):
        self.chunk.emit_header()

        for stmt in self.statements: self.visit(stmt)

        self.chunk.emit_end()

        if ErrorReporter.HAD_ERROR: return

        self.write(path)
        assert not COMPILER_DEBUG, "Still in debug mode"

    def register_string(self, string : str): # For string interning optimisation, returns true if the string is unique and new
        if string not in self.interned_strings.keys(): # If new string
            self.interned_strings[string] = self.chunk.constant_count
            return (True, self.chunk.constant_count) # Return index of string in constant pool
        return (False, self.interned_strings[string]) # Otherwise return the index of the furst string in the constant pool

    def emit_empty_str(self):
        new, index = self.register_string("") # There might not have been an empty string registered yet
        if new:
            self.chunk.add_value(Value.init_string("")) # If not then add it
        self.chunk.emit_const_w_count(index) # We shouldn't have to decide if we want to push it to the stack because there is no reason not to
        self.chunk.emit_1_or_3(index)

    def emit_constant(self, value : Value, with_instruction : bool = True): # Adds a constant to the constant pool. If with_instruction is false then the push instruction will not be emitted
        index = self.chunk.add_value(value)
        if with_instruction:
            self.chunk.emit_const_w_count(index)
            self.chunk.emit_1_or_3(index)

    def emit_string(self, string : str, with_instruction = True):
        new, index = self.register_string(string) # Check for interned strings

        if new:
            val = Value.init_string(string)
            i = self.chunk.add_value(val) # Confirm that the string index matches the calculated index
            assert i == index, "WTF happened with string interning"

        if with_instruction:
            self.chunk.emit_const_w_count(index)
            self.chunk.emit_1_or_3(index)

    def patch_break(self, stmt : Stmt): # Take statement position for error reporting
        if self.breaking: # If we encountered a break statatement recently that hasnt been handled
            jump_distance = self.inner_loop_end - self.break_position - 2 # Get jump size between the required position to jump to and the break instruction

            if jump_distance > 2**16 - 1:
                ErrorReporter.compile_error(stmt, "Too much code to jump")

            self.chunk.code[self.break_position] = jump_distance & 0xff # Little endian
            self.chunk.code[self.break_position + 1] = (jump_distance >> 8) & 0xff
            self.breaking = False # Turn of toggle to prevent overwriting the instruction

    def patch_continue(self, stmt : Stmt, jump_pos : int = -1): # Take statement position for error reporting
        if self.continuing: # If we encountered a continue statatement recently that hasnt been handled
            if jump_pos == -1:
                jump_pos = self.inner_loop_start
            jump_distance = abs(jump_pos - self.continue_position - 2) # Get jump size

            if jump_distance > 2**16 - 1:
                ErrorReporter.compile_error(stmt, "Too much code to jump")

            self.chunk.code[self.continue_position] = jump_distance & 0xff # Little endian
            self.chunk.code[self.continue_position + 1] = (jump_distance >> 8) & 0xff
            self.continuing = False # Turn of toggle to prevent overwriting the instruction

    ### Return the original position

    def begin_loop(self):
        previous = self.inner_loop_start
        self.inner_loop_start = self.chunk.code_length
        return previous

    def end_loop(self):
        previous = self.inner_loop_end
        self.inner_loop_end = self.chunk.code_length
        return previous

    def exit_loop(self, previous_start, previous_end): # Resets positions, at the end of program should both be -1
        self.inner_loop_start = previous_start
        self.inner_loop_end = previous_end

    ### Statements ###

    def visitBlock(self, block: Block):
        previous_depth = self.scope_depth
        self.begin_scope()
        assert self.scope_depth == previous_depth + 1, "Error in creating new scope"
        for stmt in block.statements:
            self.visit(stmt)
        self.end_scope()

    def visitBreakStmt(self, stmt: BreakStmt):
        if self.inner_loop_start == -1:
            ErrorReporter.compile_error(stmt, "Break statement outside of loop")
        self.break_position = self.chunk.emit_jump(OP_JUMP)
        self.breaking = True # Set to true to allow for patching

    def visitContinueStmt(self, stmt: ContinueStmt):
        if self.inner_loop_start == -1:
            ErrorReporter.compile_error(stmt, "Continue statement outside of loop")
        self.continue_position = self.chunk.emit_jump(self.continue_type)
        self.continuing = True

    def visitExprStmt(self, stmt: ExprStmt):
        self.visit(stmt.expr)
        clog("Expr pop")
        self.chunk.emit_pop()

    def visitForStmt(self, stmt: ForStmt):
        if stmt.initializer != None:
            self.visit(stmt.initializer)

        previous_continue_type = self.continue_type
        if stmt.step != None: # If there is a step, it will be at the very end of the body, and in a for loop, continue should jump to the step statement before looping
            self.continue_type = OP_JUMP

        previous_start = self.begin_loop()

        exit_jump = -1

        if stmt.condition != None:
            self.visit(stmt.condition)

            exit_jump = self.chunk.emit_jump(OP_JUMP_IF_FLS)
            clog("For stmt condition pop")
            self.chunk.emit_pop()

        self.begin_scope()

        self.visit(stmt.body)

        continue_pos = -1

        if stmt.step != None:
            continue_pos = self.chunk.code_length # If there is a step the VM needs to know where to go for the step in the case of a continue
            self.visit(stmt.step)
        
        self.chunk.emit_loop(stmt.body, self.inner_loop_start)
        
        if exit_jump != -1:
            self.chunk.patch_jump(stmt, exit_jump)
            clog("For stmt exit pop")
            self.chunk.emit_pop()

        self.end_scope()

        previous_end = self.end_loop()

        self.patch_break(stmt)
        self.patch_continue(stmt, continue_pos)

        self.exit_loop(previous_start, previous_end)

        self.continue_type = previous_continue_type

    def visitForeverStmt(self, stmt: ForeverStmt):
        previous_start = self.begin_loop()

        self.begin_scope()
        self.visit(stmt.body) # Compile body
        self.end_scope()

        self.chunk.emit_loop(stmt.body, self.inner_loop_start)

        previous_end = self.end_loop()

        self.patch_break(stmt)
        self.patch_continue(stmt)

        self.exit_loop(previous_start, previous_end)

    def visitIfStmt(self, stmt: IfStmt):
        self.visit(stmt.condition)

        then_jump = self.chunk.emit_jump(OP_JUMP_IF_FLS)
        clog("If stmt if clause pop")
        self.chunk.emit_pop()

        self.visit(stmt.if_branch)

        else_jump = self.chunk.emit_jump(OP_JUMP)

        self.chunk.patch_jump(stmt.if_branch, then_jump)
        clog("If stmt else clause pop")
        self.chunk.emit_pop()

        if stmt.else_branch != None:
            self.visit(stmt.else_branch)

        self.chunk.patch_jump(stmt.if_branch if stmt.else_branch == None else stmt.else_branch, else_jump)

    def visitPrintStmt(self, stmt: PrintStmt):
        if stmt.value == None: self.emit_empty_str()
        else: self.visit(stmt.value)
        self.chunk.emit_byte(OP_PRINT)

    def visitVarDeclStmt(self, stmt: VarDeclStmt):
        global_idx = self.parse_variable(stmt.name)
        if stmt.initializer == None:
            self.chunk.emit_null()
        else:
            self.visit(stmt.initializer)
        self.define_variable(global_idx)

    def visitWhileStmt(self, stmt: WhileStmt):
        previous_start = self.begin_loop()

        self.visit(stmt.condition)

        exit_jump = self.chunk.emit_jump(OP_JUMP_IF_FLS)
        clog("While stmt condition pop")
        self.chunk.emit_pop()

        self.begin_scope()

        self.visit(stmt.body)

        self.end_scope()

        self.chunk.emit_loop(stmt.body, self.inner_loop_start)

        self.chunk.patch_jump(stmt, exit_jump)
        clog("While stmt exit pop")
        self.chunk.emit_pop()

        previous_end = self.end_loop()

        self.patch_break(stmt)
        self.patch_continue(stmt)

        self.exit_loop(previous_start, previous_end)

    ### Expressions ###

    def visitAssignExpr(self, expr: AssignExpr):
        self.visit(expr.value)
        self.named_variable(expr.name, True)

    def visitBinaryExpr(self, expr: BinaryExpr):
        self.visit(expr.left)
        self.visit(expr.right)

        op = expr.operator.type

        if op == T_PLUS:        self.chunk.emit_byte(OP_ADD)
        elif op == T_MINUS:     self.chunk.emit_byte(OP_SUB)
        elif op == T_STAR:      self.chunk.emit_byte(OP_MUL)
        elif op == T_SLASH:     self.chunk.emit_byte(OP_DIV)
        elif op == T_PERCENT:   self.chunk.emit_byte(OP_MOD)
        elif op == T_CARET:     self.chunk.emit_byte(OP_POW)
        elif op == T_EE:        self.chunk.emit_byte(OP_EQ)
        elif op == T_NE:        self.chunk.emit_bytes(OP_EQ, OP_NOT)
        elif op == T_LT:        self.chunk.emit_byte(OP_LT)
        elif op == T_LTE:       self.chunk.emit_bytes(OP_GT, OP_NOT)
        elif op == T_GT:        self.chunk.emit_byte(OP_GT)
        elif op == T_GTE:       self.chunk.emit_bytes(OP_LT, OP_NOT)
        elif op == T_AND:       self.chunk.emit_byte(OP_AND)
        elif op == T_OR:        self.chunk.emit_byte(OP_OR)

    def visitFactorialExpr(self, expr: FactorialExpr):
        self.visit(expr.expr)
        self.chunk.emit_byte(OP_FACT)

    def visitInputExpr(self, expr: InputExpr):
        if expr.prompt != None:
            self.visit(expr.prompt)
        else:
            self.emit_empty_str()
        self.chunk.emit_byte(OP_GET_INPUT)

    def visitLiteralExpr(self, expr: LiteralExpr):
        value = expr.token.value
        expr_type = expr.token.type

        if expr_type == T_STRING:
            self.emit_string(expr.token.lexeme) 
        elif expr_type in (T_TRUE, T_FALSE): self.chunk.emit_byte(OP_TRUE if expr.token.type == T_TRUE else OP_FALSE)
        elif expr_type == T_NULL: self.chunk.emit_null()
        elif expr.token.type == T_FLOAT: self.emit_constant(Value(V_FLOAT, struct.pack('=d', value))) #Use native byte order for constants
        elif expr.token.type == T_INT:
            #If the number is a simple number like 1, we can emit an instruction specifically to emit it
            if value == 0: self.chunk.emit_byte(OP_0)
            elif value == 1: self.chunk.emit_byte(OP_1)
            elif value == 2: self.chunk.emit_byte(OP_2)
            else:
                # Add value to constant pool then add instruction
                self.emit_constant(Value(V_INT, struct.pack('=q', value)))

    def visitSubscriptExpr(self, expr: SubscriptExpr): # Like list indexing or dictionary key access
        self.visit(expr.iterable)
        self.visit(expr.subscript)
        self.chunk.emit_byte(OP_SUBSCRIPT)

    def visitTernaryExpr(self, expr: TernaryExpr): # Exactly like if statement
        self.visit(expr.condition)

        then_jump = self.chunk.emit_jump(OP_JUMP_IF_FLS)
        self.chunk.emit_pop()

        self.visit(expr.if_branch)

        else_jump = self.chunk.emit_jump(OP_JUMP)

        self.chunk.patch_jump(expr.if_branch, then_jump)
        self.chunk.emit_pop()

        if expr.else_branch != None:
            self.visit(expr.else_branch)

        self.chunk.patch_jump(expr.else_branch, else_jump)

    def visitUnaryExpr(self, expr: UnaryExpr):
        self.visit(expr.right)

        op = expr.operator.type

        if op == T_MINUS:
            if self.chunk.code[-1] == OP_1: # If the number is -1 we can emit a specific instruction for it
                self.chunk.code[-1] = OP_NEG1
                return
            self.chunk.emit_byte(OP_NEGATE)
        elif op == T_NOT: self.chunk.emit_byte(OP_NOT)
        elif op == T_PLUS: return

    def visitVariableExpr(self, expr: VariableExpr):
        self.named_variable(expr.name)