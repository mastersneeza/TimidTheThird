#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "common.h"
#include "debug.h"
#include "object.h"
#include "vm.h"
#include "memory.h"

VM vm;

static void resetStack() {
    vm.stackTop = vm.stack; // Set the top pointer to the beginning of the array
}

void push(Value value) {
    *vm.stackTop = value; // Set the top of the stack to the value
    vm.stackTop++; // Move the stack up by one
}

Value pop() {
    vm.stackTop--;
    return *vm.stackTop;
}

static Value peek(int distance) { return vm.stackTop[-1 - distance]; }

void vmInit() {
    resetStack();
    vm.objects = NULL;
    tableInit(&vm.globals);
    #ifdef T_VM_DBG
    printf("vm.c :: vmInit : initialize vm\n");
    #endif
}

void vmFree() {
    tableFree(&vm.strings);
    tableFree(&vm.globals);
    freeObjects();
    #ifdef T_VM_DBG
    printf("vm.c :: vmFree : free vm\n");
    #endif
}

void concatenate() {
    Value b_ = pop(); // Second operand
    Value a_ = pop(); // First operand
    ObjString* a = toString(a_);
    ObjString* b = toString(b_);

    int length = a->length + b->length;
    char* chars = ALLOCATE(char, length + 1);

    memcpy(chars, a->chars, a->length);
    memcpy(chars + a->length, b->chars, b->length);
    chars[length] = '\0';

    ObjString* result = makeString(true, chars, length);
    push(TIMID_STR_2_VAL(result));
}

void stringMultiplication(Value value, int times) {
    ObjString* string = toString(value);

    if (times <= 0) {
        push(TIMID_EMPTY_STR);
        return;
    }

    int length = string->length * times;
    char* chars = ALLOCATE(char, length + 1);

    for (int i = 0; i < times; i++)
        memcpy(chars + string->length * i, string->chars, string->length);

    chars[length] = '\0';

    ObjString* result = makeString(true, chars, length);
    push(TIMID_STR_2_VAL(result));
}

static void emitByte(uint8_t byte) {
    blockWrite(vm.block, byte);
}

typedef enum {
    B_INT, B_FLOAT, B_STRING, B_COUNT
} BytecodeValType;

#define HEADER_BYTES 0xFACC

static void readBytecode(uint8_t* bytecode, size_t bytecodeLength) {
    #define READ_BYTE() (bytecode[offset++])
    #define PEEK(distance) (bytecode[offset + distance])
    #ifdef T_VM_DBG
    printf("vm.c :: readBytecode : start bytecode read\n");
    #endif

    int offset = 0;
    bool readConstants = false;

    // Read constant pool
    for (; offset < bytecodeLength && !readConstants;) {
        BytecodeValType constantType = READ_BYTE(); // Our counter is one byte ahead of where we are
        switch (constantType) { // Add values to constant pool
            case B_INT: {
                union {
                    uint8_t bytes[T_INT_SIZE];
                    t_int i;
                } u;

                for (int intOffset = 0; intOffset < T_INT_SIZE; intOffset++) {
                    u.bytes[intOffset] = READ_BYTE();
                }

                addConstant(vm.block, TIMID_INT(u.i));
                break;
            }
            case B_FLOAT: {
                union {
                    uint8_t bytes[T_FLOAT_SIZE];
                    t_float f;
                } u;

                for (int floatOffset = 0; floatOffset < T_FLOAT_SIZE; floatOffset++) {
                    u.bytes[floatOffset] = READ_BYTE();
                }

                addConstant(vm.block, TIMID_FLOAT(u.f));
                break;
            }
            case B_STRING: {
                int len = 0;

                // Read string length
                while (READ_BYTE() != '\0') {
                    len++;
                }

                // Rewind to the start
                for (int i = 0; i < len + 1; i++) {
                    offset--;
                }
                
                char* buffer = ALLOCATE(char, len);

                // Set chars
                for (int i = 0; i < len; i++) {
                    buffer[i] = READ_BYTE();
                }

                READ_BYTE(); // Consume null terminator
                addConstant(vm.block, TIMID_STRING(buffer, len));
                break;
            }
            default:
                if (PEEK(-1) == 0xFA && PEEK(0) == 0xCC) {
                    //printf("Reached header\n");
                    readConstants = true;
                    break;
                } else {
                    fprintf(stderr, "Invalid file format\n");
                    return;
                }
        }
    }

    for (offset += 1; offset < bytecodeLength;) { // Loop through every byte, after checking the header
        uint8_t instruction = READ_BYTE(); // We can move our offset pointer further ahead based on certain instructions
        switch (instruction) {
            case OP_GET_LOCAL:
            case OP_SET_LOCAL:
            case OP_DEFINE_GLOBAL:
            case OP_GET_GLOBAL:
            case OP_SET_GLOBAL: {
                emitByte(instruction);
                uint8_t constType = READ_BYTE();
                emitByte(constType);

                if (constType == OP_CONSTANT) {
                    emitByte(READ_BYTE());
                } else if (constType == OP_CONSTANT_LONG) {
                    emitByte(READ_BYTE());
                    emitByte(READ_BYTE());
                    emitByte(READ_BYTE());
                }
                break;
            }
            default:
                emitByte(instruction);
                break;
        }
    }
    #undef READ_BYTE
    #undef PEEK
}

static void logInstruction(const char* message) {
    #ifdef T_STACK_DBG
    printf(message);
    #endif
}

static InterpretResult run() {
    #define READ_BYTE() (*vm.ip++)
    #define READ_SHORT() ((uint16_t)(READ_BYTE() | (READ_BYTE() << 8)))
    #define READ_LONG() ((READ_BYTE()) | (READ_BYTE() << 8) | (READ_BYTE() << 16))
    #define READ_BYTE_OR_LONG() ((READ_BYTE() == OP_CONSTANT) ? READ_BYTE() : READ_LONG())
    #define READ_CONSTANT() (vm.block->constants.values[READ_BYTE()])
    #define READ_CONSTANT_LONG() (vm.block->constants.values[READ_LONG()])
    
    #define READ_BYTE_OR_3_BYTES() ((READ_BYTE() == OP_CONSTANT) ? READ_CONSTANT() : READ_CONSTANT_LONG())
    #define READ_STRING() AS_STRING(READ_BYTE_OR_3_BYTES())
    uint8_t instruction;
    for (;;) {
        // Visualise the stack
        #ifdef T_STACK_DBG
        printf("        ");
        for (Value* slot = vm.stack; slot < vm.stackTop; slot++) {
            printf("[ ");
            printValue(*slot);
            printf(" ]");
        }
        printf("\n");
        disassembleInstruction(vm.block, (int)(vm.ip - vm.block->bytes)); // Get the relative offset from the start of the bytearray
        #endif
        switch (instruction = READ_BYTE()) {
            case OP_NOP: break; // No operation
            case OP_CONSTANT: {
                Value value = READ_CONSTANT();
                push(value);
                break;
            }
            case OP_CONSTANT_LONG: {
                Value value = READ_CONSTANT_LONG();
                push(value);
                break;
            }
            case OP_NEG1: push(TIMID_INT(-1));      break;
            case OP_0: push(TIMID_INT(0));          break;
            case OP_1: push(TIMID_INT(1));          break;
            case OP_2: push(TIMID_INT(2));          break;
            case OP_TRUE: push(TIMID_BOOL(true));   break;
            case OP_FALSE: push(TIMID_BOOL(false)); break;
            case OP_NULL: push(TIMID_NULL);         break;
            case OP_PRINT: {
                printValue(pop());
                printf("\n");
                break;
            }
            case OP_POP: pop(); break;
            case OP_NEGATE: {
                Value peeked = peek(0);
                if (IS_NUMERIC(peeked)) {
                    if (IS_BOOL(peeked) || IS_NULL(peeked))
                        push(TIMID_INT(-AS_INT(NUM_2_INT(pop()))));
                    else if (IS_INT(peeked))
                        push(TIMID_INT(-AS_INT(pop())));
                    else if (IS_FLOAT(peeked))
                        push(TIMID_FLOAT(-AS_FLOAT(pop())));
                    break;
                }
                printf("Expected a numeric value to negate\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_NOT: {
                Value value = pop();
                push(TIMID_BOOL(!truth(value)));
                break;
            }
            case OP_FACT: {
                if (isIntegral(peek(0))) {
                    int value = AS_INT(pop());
                    if (value < 0) {
                        printf("Math error: cannot factorial negative number '%d'\n", value);
                        return INTERPRET_RUNTIME_ERROR;
                    }
                    int result = 1;
                    
                    for (int i = 1; i <= value; i++) {
                        result *= i;
                    }
                    push(TIMID_INT(result));
                    break;

                }
                printf("Expected an integer to factorial\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_ADD: {
                if (isNumeric(peek(0)) && isNumeric(peek(1))) {
                    Value b = pop(), a = pop();
                    if (a.type == V_FLOAT || b.type == V_FLOAT) // If both values are numeric and one is a float, make the result a float
                        push(TIMID_FLOAT(toFloat(a) + toFloat(b)));
                    else
                        push(TIMID_INT(toInt(a) + toInt(b)));
                    break;
                } else if (IS_STRING(peek(0)) || IS_STRING(peek(1))) { // If any operand is a string then concatenation can occur;
                    concatenate();
                    break;
                }
                printf("Expected numerical values to add, or at least one string to concatenate\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_SUB: {
                if (isNumeric(peek(0)) && isNumeric(peek(1))) {
                    Value b = pop(), a = pop();
                    if (a.type == V_FLOAT || b.type == V_FLOAT)
                        push(TIMID_FLOAT(toFloat(a) - toFloat(b)));
                    else
                        push(TIMID_INT(toInt(a) - toInt(b)));
                    break;
                }
                printf("Expected numerical values to subtract\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_MUL: {
                if (isNumeric(peek(0)) && isNumeric(peek(1))) {
                    Value b = pop(), a = pop();
                    if (a.type == V_FLOAT || b.type == V_FLOAT)
                        push(TIMID_FLOAT(toFloat(a) * toFloat(b)));
                    else
                        push(TIMID_INT(toInt(a) * toInt(b)));
                    break;
                } else if (IS_STRING(peek(0)) && isIntegral(peek(1))) { // string * integer
                    Value value = pop();
                    int times = toInt(pop());  
                    if (times <= 0) { // If the times is less than or equal to zero then bail out and return an empty string
                        push(TIMID_EMPTY_STR);
                        break;
                    }
                    stringMultiplication(value, times);
                    break;

                } else if (IS_STRING(peek(1)) && isIntegral(peek(0))) { // integer * string
                    int times = toInt(pop());
                    if (times <= 0) {
                        push(TIMID_EMPTY_STR);
                        break;
                    }
                    Value value = pop();
                    stringMultiplication(value, times);
                    break;
                }
                printf("Expected numerical values to multiply, or a string and an integer\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_DIV: {
                if (isNumeric(peek(0)) && isNumeric(peek(1))) {
                    Value b = pop(), a = pop();
                    
                    if (a.type == V_FLOAT || b.type == V_FLOAT) {
                        if (toFloat(b) == 0) {
                            printf("Division by zero\n");
                            return INTERPRET_RUNTIME_ERROR;
                        } 
                        push(TIMID_FLOAT(toFloat(a) / toFloat(b)));
                    }
                    else {
                        if (toInt(b) == 0) {
                            printf("Division by zero\n");
                            return INTERPRET_RUNTIME_ERROR;
                        } 
                        push(TIMID_INT(toInt(a) / toInt(b)));
                    }
                    break;
                }
                printf("Expected numerical values to divide\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_MOD: {
                if (isNumeric(peek(0)) && isNumeric(peek(1))) {
                    Value b = pop(), a = pop();
                    
                    if (a.type == V_FLOAT || b.type == V_FLOAT) {
                        if (toFloat(b) == 0) {
                            printf("Division by zero\n");
                            return INTERPRET_RUNTIME_ERROR;
                        } 
                        push(TIMID_FLOAT((t_float)fmod(toFloat(a), toFloat(b))));
                    }
                    else {
                        if (toInt(b) == 0) {
                            printf("Division by zero\n");
                            return INTERPRET_RUNTIME_ERROR;
                        } 
                        push(TIMID_INT(toInt(a) % toInt(b)));
                    }
                    break;
                }
                printf("Expected numerical values to mod\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_POW: {
                if (isNumeric(peek(0)) && isNumeric(peek(1))) {
                    Value b = pop(), a = pop();

                    if (a.type == V_FLOAT || b.type == V_FLOAT) {
                        if (toFloat(a) == 0 && toFloat(b) == 0) {
                            printf("Zero to zero\n");
                            return INTERPRET_RUNTIME_ERROR;
                        }
                        
                        push(TIMID_FLOAT((t_float)pow(toFloat(a), toFloat(b))));
                    }
                    else {
                        if (toInt(a) == 0 && toInt(b) == 0) {
                            printf("Zero to zero\n");
                            return INTERPRET_RUNTIME_ERROR;
                        }
                        t_float result = (t_float)pow(toInt(a), toInt(b));
                        push(TIMID_INT((t_int)result));

                    }
                    break;
                }
                printf("Expected numerical values to exponentiate\n");
                return INTERPRET_RUNTIME_ERROR;
            }
            case OP_EQ: {
                Value b = pop(), a = pop();
                push(TIMID_BOOL(equals(a, b)));
                break;
            }
            case OP_LT: {
                Value b = pop(), a = pop();
                push(TIMID_BOOL(lessThan(a, b)));
                break;
            }
            case OP_GT: {
                Value b = pop(), a = pop();
                push(TIMID_BOOL(greaterThan(a, b)));
                break;
            }
            case OP_AND: {
                Value b = pop(), a = pop();
                push(TIMID_BOOL(truth(a) && truth(b)));
                break;
            }
            case OP_OR: {
                Value b = pop(), a = pop();
                push(TIMID_BOOL(truth(a) || truth(b)));
                break;
            }
            case OP_JUMP_IF_FLS: {
                uint16_t offset = READ_SHORT();
                if (!truth(peek(0))) vm.ip += offset;
                break;
            }
            case OP_JUMP: {
                uint16_t offset = READ_SHORT();
                vm.ip += offset;
                break;
            }
            case OP_LOOP: {
                uint16_t offset = READ_SHORT();
                vm.ip -= offset;
                break;
            }
            case OP_DEFINE_GLOBAL: {
                ObjString* name = AS_STRING(READ_BYTE_OR_3_BYTES()); // Get the variable name
                tableSet(&vm.globals, name, peek(0)); // Set the hashmap value to the value on the stack
                pop(); // Remove the temporary
                break;
            }
            case OP_GET_GLOBAL: {
                ObjString* name = READ_STRING();
                Value value;
                if (!tableGet(&vm.globals, name, &value)) {
                    printf("Undefined variable '");
                    printValue(TIMID_STR_2_VAL(name));
                    printf("'\n");
                    return INTERPRET_RUNTIME_ERROR;
                }
                push(value);
                break;
            }
            case OP_SET_GLOBAL: {
                ObjString* name = READ_STRING();
                if (tableSet(&vm.globals, name, peek(0))) {
                    tableDelete(&vm.globals, name);
                    printf("Undefined variable '");
                    printValue(TIMID_STR_2_VAL(name));
                    printf("'\n");
                    return INTERPRET_RUNTIME_ERROR;
                }
                break;
            }
            case OP_GET_LOCAL: {
                uint32_t slot = READ_BYTE_OR_LONG();
                push(vm.stack[slot]);
                break;
            }
            case OP_SET_LOCAL: {
                uint32_t slot = READ_BYTE_OR_LONG();
                vm.stack[slot] = peek(0);
                break;
            }
            case OP_GET_INPUT: {
                Value prompt = pop();
                printValue(prompt);

                size_t bufferSize = sizeof(char) * 1024;
                char* buffer = ALLOCATE(char, bufferSize);

                size_t size = getline(&buffer, &bufferSize, stdin) - 1;
                push(TIMID_STRING(buffer, size));
                break;
                
                
            }
            case OP_SUBSCRIPT: {
                Value subscript = pop();
                Value iterable = pop();
                Value value;

                if (!subscriptValue(iterable, subscript, &value)) {
                    printf("Expected a string and integer to subscript\n");
                    return INTERPRET_RUNTIME_ERROR;
                }

                push(value);
                break;
            }
            case OP_RETURN:
                // Exit program
                return INTERPET_OK;
            default:
                printf("Unknown opcode '%d'\n", instruction);
                break;
        }
    }
    #undef READ_STRING
    #undef READ_BYTE_OR_3_BYTES
    #undef READ_CONSTANT_LONG
    #undef READ_CONSTANT
    #undef READ_BYTE_OR_LONG
    #undef READ_LONG
    #undef READ_SHORT
    #undef READ_BYTE
    return INTERPET_OK;
}

InterpretResult interpret(uint8_t* bytecode, size_t bytecodeLength) {
    Block block;
    blockInit(&block);

    vm.block = &block;
    
    readBytecode(bytecode, bytecodeLength);

    #ifdef T_VM_DBG
    dumpBlock(vm.block, "Block");
    disassembleBlock(vm.block, "Block");
    #endif

    vm.ip = vm.block->bytes;

    #ifndef NO
    InterpretResult result = run();

    blockFree(&block);
    return result;
    #endif
    return INTERPET_OK;
}