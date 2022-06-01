from Enum import iota

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