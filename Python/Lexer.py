import string

from Error import ErrorReporter
from TokenType import *
from Token import Token, Position

DIGITS = string.digits
LETTERS = string.ascii_letters + '_' # Allowed identifier characters
LETTERS_DIGITS = DIGITS + LETTERS
WHITESPACE = string.whitespace.replace('\n', '')

ESCAPE_CHAR = '\\'
ESCAPE_CHARS = {
    '"': '"',
    '\'': '\'',
    '\\': '\\',
    'n': '\n',
    't': '\t'
}

KEYWORDS = {
    'and': T_AND,
    'or': T_OR,
    'tru': T_TRUE,
    'fls': T_FALSE,
    'nul': T_NULL,
    'lam': T_LAMBDA,
    'print': T_PRINT,
    'const': T_CONST,
    'in': T_IN,
    'fn': T_FN,
    'if': T_IF,
    'else': T_ELSE,
    'while': T_WHILE,
    'for': T_FOR
}

class Lexer:
    def __init__(self, source : str, file : str):
        self.pos = Position(-1, 0, -1, source, file)
        self.source : str = source
        self.tokens : list[Token] = []
        self.is_empty = True
        self.advance()

    @property
    def is_at_end(self): return self.pos.index >= len(self.source) or self.pos.index < 0
    @property
    def current_char(self):
        if self.is_at_end: return '\0'
        return self.source[self.pos.index]

    @property
    def peek_next(self):
        if self.pos.index >= len(self.source) - 1: return '\0'
        return self.source[self.pos.index + 1]

    def advance(self):
        self.pos.advance(self.current_char)

        #print(ord(self.current_char))
        return self.current_char

    def skip_whitespace(self):
        while self.current_char in WHITESPACE:
            self.advance()

    def add_token(self, type : int, lexeme : str = None, value : object = None, pos_start : Position = None, pos_end : Position = None):
        self.tokens.append(self.make_token(type, lexeme, value, pos_start, pos_end))

    def single_char_token(self, type : int):
        self.add_token(type)
        self.advance()

    def make_token(self, type : int, lexeme : str = None, value : object = None, pos_start : Position = None, pos_end : Position = None):
        if lexeme == None: lexeme = self.current_char
        if pos_start == None: pos_start = self.pos.copy()
        if pos_end == None: pos_end = pos_start.copy().advance(self.current_char)
        self.is_empty = False
        return Token(type, lexeme, value, pos_start, pos_end)

    def two_char_token(self, type1 : int, type2 : int, match : str):
        pos_start = self.pos.copy()
        token_type : int = type1
        string : str = self.current_char
        self.advance()

        if self.current_char == match:
            token_type = type2
            string += self.current_char
            self.advance()

        self.add_token(token_type, string, None, pos_start, self.pos)

    def make_number(self):
        pos_start = self.pos.copy()
        num_str : str = ""
        token_type : int = T_INT

        while self.current_char in DIGITS:
            num_str += self.current_char
            self.advance()

        if self.current_char == '.' and self.peek_next in DIGITS:
            num_str += self.current_char
            self.advance() # Consume the dot

            while self.current_char in DIGITS:
                num_str += self.current_char
                self.advance()
            token_type = T_FLOAT

        if token_type == T_INT:
            literal = int(num_str)
        else:
            literal = float(num_str)
        self.add_token(token_type, num_str, literal, pos_start, self.pos)

    def make_string(self, opener : str, raw : bool = False):
        pos_start = self.pos.copy()
        string = ""
        escape = False

        self.advance() # Advance first quote

        while (self.current_char != opener or escape) and not self.is_at_end:
            if escape and not raw:
                escape = False
                string += ESCAPE_CHARS.get(self.current_char, self.current_char)
                self.advance()
                continue
            if self.current_char == ESCAPE_CHAR and not raw:
                escape = True
                self.advance()
                continue
            string += self.current_char
            self.advance()

        if self.is_at_end:
            ErrorReporter.missing_quote(self.pos.copy(), self.pos.advance().copy(), f"Missing '{opener}' string delimiter")

        self.advance() # Advance second quote
        self.add_token(T_STRING, string, string, pos_start, self.pos)

    def make_identifier(self):
        pos_start = self.pos.copy()
        id_str = ''
        token_type = T_IDENTIFIER

        while self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.advance()

        token_type = KEYWORDS.get(id_str, T_IDENTIFIER)
        self.add_token(token_type, id_str, None, pos_start, self.pos)
        
    def scan_token(self):
        self.skip_whitespace()
        match self.current_char:
            case '+': self.single_char_token(T_PLUS)
            case '-': self.single_char_token(T_MINUS)
            case '*': self.single_char_token(T_STAR)
            case '/': self.single_char_token(T_SLASH)
            case '%': self.single_char_token(T_PERCENT)
            case '^': self.single_char_token(T_CARET)

            case '=': self.two_char_token(T_EQ, T_EE, '=')
            case '!': self.two_char_token(T_NOT, T_NE, '=')
            case '<': self.two_char_token(T_LT, T_LTE, '=')
            case '>': self.two_char_token(T_GT, T_GTE, '=')

            case '(': self.single_char_token(T_LPAR)
            case ')': self.single_char_token(T_RPAR)
            case '{': self.single_char_token(T_LCURL)
            case '}': self.single_char_token(T_RCURL)
            case '[': self.single_char_token(T_LSQR)
            case ']': self.single_char_token(T_RSQR)

            case '@': self.single_char_token(T_AT)
            case '?': self.single_char_token(T_QMARK)
            case '.': self.single_char_token(T_DOT)
            case ',': self.single_char_token(T_COMMA)
            case ':': self.single_char_token(T_COLON)
            case ';'|'\n': self.single_char_token(T_SEMIC)
            case '$': self.single_char_token(T_DOLLAR)
            case '\0': self.single_char_token(T_EOF)

            case '|': self.two_char_token(T_BWOR, T_ASSERT, '-')

            case '"' | '\'': self.make_string(self.current_char)
            case '~':
                self.advance()
                if self.current_char == '~':
                    self.advance()
                    while not self.is_at_end and self.current_char != '~':
                        self.advance()
                    self.advance()
                else:
                    while not self.is_at_end and self.current_char != '\n':
                        self.advance()
            case _:
                if self.current_char.lower() == 'r' and self.peek_next in '"\'':
                    self.advance()
                    self.make_string(self.current_char, True)
                elif self.current_char in DIGITS:
                    self.make_number()
                elif self.current_char in LETTERS:
                    self.make_identifier()
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    ErrorReporter.invalid_character(pos_start, self.pos.copy(), f"Invalid character '{char}'")
                    self.advance()

    def lex(self):
        while not self.is_at_end:
            self.scan_token()

        self.add_token(T_EOF, "[EOF]")

        return self.tokens