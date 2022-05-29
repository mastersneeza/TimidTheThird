from TokenType import *

### Position ###

class Position: # To help with error reporting
    def __init__(self, index : int, line : int, column : int, source : str, fn : str):
        self.index = index
        self.line = line
        self.column = column
        self.source = source
        self.fn = fn # Filename


    def advance(self, current_char : str = '\0'):
        self.index += 1
        self.column += 1

        if current_char == '\n':
            self.line += 1
            self.column = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.column, self.source, self.fn)
    def __repr__(self):
        return f"Position({self.index}, {self.line}, {self.column}, {self.source}, {self.fn})"
    def __str__(self): return f"({self.line + 1}, {self.column + 1})"

### Token ###

class Token:
    def __init__(self, type : int, lexeme : str, value : object, pos_start : Position, pos_end : Position = None):
        self.type : int = type
        self.lexeme : str = lexeme
        self.value : object = value
        self.pos_start : Position = pos_start.copy()
        if pos_end == None:
            self.pos_end = self.pos_start.copy()
            self.pos_end.advance()
        else:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        return f"<Token ({self.type}, {self.lexeme}, {self.value}, {self.pos_start}) >"