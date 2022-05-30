#include <stdio.h>

#include "debug.h"

void dumpBlock(Block* block, const char* blockName) {
    printf("== %s's Hex Dump ==\n", blockName);

    int i = 0;
    for (int offset = 0; offset < block->count; offset++) {
        printf("%02x ", block->bytes[offset]);
        i++;

        if (i >= 8) {
            printf("\n");
            i = 0;
        }
    }
    printf("\n");
}

void disassembleBlock(Block* block, const char* blockName) {
    printf("== %s ==\n", blockName);

    for (int offset = 0; offset < block->count;) {
        offset = disassembleInstruction(block, offset); // Get the index of the next instruction, not including immediate values like constant indoces
    }
}

static int simpleInstruction(const char* name, int offset) {
    printf("%s\n", name);
    return offset + 1;
}

static int constantInstruction(const char* name, Block* block, int offset) {
    uint8_t constantIndex = block->bytes[offset + 1]; // We get the next byte after the current opcode 
    printf("%-20s Index: %4d Value: '", name, constantIndex);
    printValue(block->constants.values[constantIndex]);
    printf("'\n");
    return offset + 2;
}

static int longConstantInstruction(const char* name, Block* block, int offset) {
    uint32_t constantIndex = block->bytes[offset + 1] | (block->bytes[offset + 2] << 8) | (block->bytes[offset + 3] << 8); // We get the next byte after the current opcode 
    printf("%-20s Index: %4d Value: '", name, constantIndex);
    printValue(block->constants.values[constantIndex]);
    printf("'\n");
    return offset + 4;
}

static int byteInstruction(const char* name, Block* block, int offset) {
    uint8_t slot = block->bytes[offset + 1];
    printf("%-16s %4d\n", name, slot);
    return offset + 2; 
}

static int jumpInstruction(const char* name, int sign, Block* block, int offset) {
    uint16_t jump = (uint16_t)(block->bytes[offset + 1]);
    jump |= (block->bytes[offset + 2] << 8);
    printf("%-16s %4d -> %d\n", name, offset,
            offset + 3 + sign * jump);
    return offset + 3;
}

int disassembleInstruction(Block* block, int offset) {
    printf("%04d ", offset);

    uint8_t currentInstruction = block->bytes[offset];
    switch (currentInstruction) {
        case OP_NOP:            return simpleInstruction("OP_NOP", offset);
        case OP_CONSTANT:       return constantInstruction("OP_CONSTANT", block, offset);
        case OP_CONSTANT_LONG:  return longConstantInstruction("OP_CONSTANT_LONG", block, offset);
        case OP_NEG1:           return simpleInstruction("OP_NEG1", offset);
        case OP_0:              return simpleInstruction("OP_0", offset);
        case OP_1:              return simpleInstruction("OP_1", offset);
        case OP_2:              return simpleInstruction("OP_2", offset);
        case OP_TRUE:           return simpleInstruction("OP_TRUE", offset);
        case OP_FALSE:          return simpleInstruction("OP_FALSE", offset);
        case OP_NULL:           return simpleInstruction("OP_NULL", offset);
        case OP_PRINT:          return simpleInstruction("OP_PRINT", offset);
        case OP_POP:            return simpleInstruction("OP_POP", offset);
        case OP_NEGATE:         return simpleInstruction("OP_NEGATE", offset);
        case OP_NOT:            return simpleInstruction("OP_NOT", offset);
        case OP_FACT:           return simpleInstruction("OP_FACT", offset);
        case OP_ADD:            return simpleInstruction("OP_ADD", offset);
        case OP_SUB:            return simpleInstruction("OP_SUB", offset);
        case OP_MUL:            return simpleInstruction("OP_MUL", offset);
        case OP_DIV:            return simpleInstruction("OP_DIV", offset);
        case OP_MOD:            return simpleInstruction("OP_MOD", offset);
        case OP_POW:            return simpleInstruction("OP_POW", offset);
        case OP_EQ:             return simpleInstruction("OP_EQ", offset);
        case OP_LT:             return simpleInstruction("OP_LT", offset);
        case OP_GT:             return simpleInstruction("OP_GT", offset);
        case OP_AND:            return simpleInstruction("OP_AND", offset);
        case OP_OR:             return simpleInstruction("OP_OR", offset);
        case OP_JUMP_IF_FLS:    return jumpInstruction("OP_JUMP_IF_FLS", 1, block, offset);
        case OP_JUMP:           return jumpInstruction("OP_JUMP", 1, block, offset);
        case OP_LOOP:           return jumpInstruction("OP_LOOP", -1, block, offset);
        case OP_DEFINE_GLOBAL:  return constantInstruction("OP_DEFINE_GLOBAL", block, offset + 1);
        case OP_GET_GLOBAL:     return constantInstruction("OP_GET_GLOBAL", block, offset + 1);
        case OP_SET_GLOBAL:     return constantInstruction("OP_SET_GLOBAL", block, offset + 1);
        case OP_GET_LOCAL:      return byteInstruction("OP_GET_LOCAL", block, offset + 1);
        case OP_SET_LOCAL:      return byteInstruction("OP_SET_LOCAL", block, offset + 1);
        case OP_GET_INPUT:      return simpleInstruction("OP_GET_INPUT", offset);
        case OP_SUBSCRIPT:      return simpleInstruction("OP_SUBSCRIPT", offset);
        case OP_RETURN:         return simpleInstruction("OP_RETURN", offset);
        default:
            printf("Unknown opcode '%d'\n", currentInstruction);
            return offset + 1;
    }
}