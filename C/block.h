#ifndef T_BLOCK_H
#define T_BLOCK_H

#include "common.h"
#include "value.h"

typedef enum {
    OP_NOP,
    OP_CONSTANT, OP_CONSTANT_LONG, 
    OP_NEG1, OP_0, OP_1, OP_2,
    OP_TRUE, OP_FALSE, OP_NULL,
    OP_PRINT,
    OP_POP,
    OP_NEGATE, OP_NOT,
    OP_FACT,
    OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD, OP_POW,
    OP_EQ, OP_LT, OP_GT,
    OP_AND, OP_OR,

    OP_JUMP_IF_FLS, OP_JUMP, OP_LOOP,

    OP_DEFINE_GLOBAL, OP_GET_GLOBAL, OP_SET_GLOBAL, OP_GET_LOCAL, OP_SET_LOCAL,
    OP_GET_INPUT,
    OP_SUBSCRIPT,
    OP_RETURN
} OpCode;

typedef struct {
    int count;
    int capacity;
    uint8_t* bytes;
    ValueArray constants;
} Block;

void blockInit(Block* block);
void blockWrite(Block* block, uint8_t byte);
void blockFree(Block* block);
int addConstant(Block* block, Value constant);
void writeConstant(Block* block, Value constant);

#endif