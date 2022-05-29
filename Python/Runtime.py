from Token import Position, Token
from Value import TimidCallable

def IsIntegral(value : object):
    return isinstance(value, (int, bool, type(None)))

def IsNumeric(value : object):
    return IsIntegral(value) or isinstance(value, float)

def IsEqual(a : object, b : object):
    if IsNumeric(a) and IsNumeric(b):
        return ToNumber(a) == ToNumber(b)

    val_type = type(a)
    if val_type != type(b):
        return False
    if val_type == int:
        return a == b
    elif val_type == float:
        return a == b
    elif val_type == bool:
        return a == b
    elif val_type == str:
        return a == b
    elif val_type == type(None):
        return True
    return False

def ToNumber(value : object):
    if isinstance(value, (int, float)): return value
    elif isinstance(value, bool): return int(value)
    elif isinstance(value, type(None)): return 0
    raise RuntimeError("Cannot convert to number") 

def ToInt(value : object):
    return int(ToNumber(value)) 

def ToString(value : object):
    if isinstance(value, bool):
        return "tru" if value else "fls"
    if value == None:
        return "nul"
    if isinstance(value, TimidCallable):
        return value.ToString
    return str(value)

def Truth(value : object):
    if isinstance(value, (int, float, bool)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    if isinstance(value, type(None)):
        return False

class Environment:
    def __init__(self , enclosing = None):
        self.enclosing : Environment = enclosing
        self.values : dict[str, object] = {}

    def define(self, name : str, value : object):
        self.values[name] = value

    def get(self, name : Token):
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        if self.enclosing != None:
            return self.enclosing.get(name)

        raise RuntimeError(name.pos_start, name.pos_end, f"Undefined variable '{name.lexeme}'")

    def assign(self, name : Token, value : object):
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(name.pos_start, name.pos_end, f"Undefined variable '{name.lexeme}'")

    def copy(self):
        copy = Environment(self.enclosing)
        copy.values = dict(self.values)
        return copy

class RuntimeError(Exception):
    def __init__(self, position : Position, pos_end : Position, message : str):
        super().__init__()
        self.message = message
        self.position = position
        self.pos_end = pos_end