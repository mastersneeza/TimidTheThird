import time

from Nodes import *
import Runtime
from Token import Position

class Object:
    def __init__(self, pos_start : Position, pos_end : Position):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def Negate(self): raise RuntimeError(self.pos_start, "Not implemented")
    def Not(self): return not self.Truth

    def And(self, other): return Boolean(self.Truth and other.Truth).SetPos(self.pos_start, other.pos_end)
    def Or(self, other): return Boolean(self.Truth or other.Truth).SetPos(self.pos_start, other.pos_end)

    def Equals(self, other): return False
    def Less(self, other): return False
    def Greater(self, other): return False

    @property
    def Truth(self): return False

    @property
    def IsNull(self): return False
    @property
    def IsNumeric(self): return False
    @property
    def IsIntegral(self): return False
    @property
    def IsString(Self): return False

    @property
    def ToInt(self): return 0
    @property
    def ToFloat(self): return 0.0
    @property
    def ToNumber(self): return self.ToFloat()
    @property
    def ToString(self): return "Value"

    def SetPos(self, pos_start : Position, pos_end : Position):
        self.pos_start = pos_start
        self.pos_end = pos_end

    @property    
    def Copy(self): return Object(self.pos_start, self.pos_end)

class Null(Object):
    def __init__(self):
        pass

    def Equals(self, other): return type(other) == type(self)
    def Less(self, other): return True
    def Greater(self, other): return False

    @property
    def IsNull(self): return True
    @property
    def ToString(self): return "nul"

class Boolean(Object):
    def __init__(self, value : bool):
        self.value = value
    
    @property
    def Truth(self):
        return self.value

    @property
    def ToString(self):
        return "tru" if self.value else "fls"

class TimidCallable(Object):
    def __init__(self):
        pass
    def call(self, interpreter, args : list[object]):
        pass

    @property
    def arity(self): return 0

class TimidAnon(TimidCallable):
    def __init__(self, declaration : LambdaExpr, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, args: list[object]):
        environment = Runtime.Environment(self.closure)

        environment.define(self.declaration.identifier.lexeme, args[0])

        return interpreter.evaluate(self.declaration.body, environment)

    @property
    def arity(self):
        return 1
    
    def Copy(self):
        return TimidAnon(self.declaration)

    @property
    def ToString(self):
        return f"<anon {self.declaration}>"

class Clock(TimidCallable):
    def call(self, interpreter, args : list[object]):
        return time.time()

    @property
    def ToString(self):
        return "<foreign fn Clock>"