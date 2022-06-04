from Enum import iota

### Constants ###
T_INT = iota(True)
T_FLOAT = iota()
T_STRING = iota()
T_IDENTIFIER = iota()
T_TRUE = iota()
T_FALSE = iota()
T_NULL = iota()

### Keywords ###
T_AND = iota()
T_BREAK = iota()
T_CONST = iota()
T_CONTINUE = iota()
T_ELSE = iota()
T_FN = iota()
T_FOR = iota()
T_FOREVER = iota()
T_GOTO = iota()
T_IF = iota()
T_IN = iota()
T_LAMBDA = iota()
T_OR = iota()
T_PRINT = iota()
T_WHILE = iota()

### Arithmetic ###
T_PLUS = iota(True, 40)
T_MINUS = iota()
T_STAR = iota()
T_SLASH = iota()
T_PERCENT = iota()
T_CARET = iota()

### Boolean ###
T_EQ = iota()
T_EE = iota()
T_NOT = iota()
T_NE = iota()
T_LT = iota()
T_LTE = iota()
T_GT = iota()
T_GTE = iota()

### Misc ###
T_LPAR = iota(True, 70)
T_RPAR = iota()
T_LCURL = iota()
T_RCURL = iota()
T_LSQR = iota()
T_RSQR = iota()

T_AT = iota()
T_QMARK = iota()
T_DOT = iota()
T_COMMA = iota()
T_COLON = iota()
T_SEMIC = iota()
T_DOLLAR = iota()

T_BWOR = iota()
T_BWAND = iota()

T_NL = iota() # Newline

T_ARROW = iota() # ->
T_ASSERT = iota()

T_EOF = iota(True, 120)