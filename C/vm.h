#ifndef T_VM_H
#define T_VM_h

#include "block.h"
#include "object.h"
#include "table.h"

#define STACK_MAX

typedef struct {
    Block* block;
    uint8_t* ip;
    Obj* objects;
    Table globals;
    Table strings;
    Value* stackTop;
    Value stack[STACK_MAX];
} VM;

typedef enum {
    INTERPRET_RUNTIME_ERROR,
    INTERPET_OK
} InterpretResult;

extern VM vm;

void vmInit();
void vmFree();

InterpretResult interpret(uint8_t* bytecode, size_t bytecodeLength);

void push(Value value);
Value pop();

#endif