#include <stdio.h>

#include "common.h"
#include "block.h"
#include "debug.h"
#include "memory.h"

void blockInit(Block* block) {
    block->count = 0;
    block->capacity = 0;
    block->bytes = NULL;
    #ifdef T_BLOCK_DBG
    printf("block.c :: blockInit : initialize block %p\n", block);
    #endif
    vaInit(&block->constants);
    //assert(block->count == 0 && block->capacity == 0 && block->bytes == NULL);
}

void blockWrite(Block* block, uint8_t byte) {
    if (block->capacity < block->count + 1) { // If the array is full then double its size
        int oldCapacity = block->capacity;
        block->capacity = GROW_CAPACITY(oldCapacity);
        //assert(block->capacity > oldCapacity);
        block->bytes = GROW_ARRAY(uint8_t, block->bytes, oldCapacity, block->capacity);
        #ifdef T_BLOCK_DBG
        printf("block.c :: blockWrite : increase block %p's capacity to %d bytes\n", block, block->capacity);
        #endif
    }

    block->bytes[block->count] = byte;
    //assert(block->bytes[block->count] == byte);
    block->count++;
    #ifdef T_BLOCK_DBG
    printf("block.c :: blockWrite : write byte '%x' to block %p, block byte count is %d bytes\n", byte, block, block->count);
    #endif
}

void blockFree(Block* block) { // Free the block's members, then free the block itself
    vaFree(&block->constants);
    FREE_ARRAY(uint8_t, block->bytes, block->capacity);
    #ifdef T_BLOCK_DBG
    printf("block.c :: blockFree : free block %p\n", block);
    #endif
    blockInit(block);
}

int addConstant(Block* block, Value constant) {
    vaWrite(&block->constants, constant); // Add the value to the block's constant pool
    /*printf("Constant ");
    printValue(constant);
    printf("\t\tINDEX %d\n", block->constants.count - 1);*/
    return block->constants.count - 1; // Return the index of the placed constant
}

void writeConstant(Block* block, Value constant) {
    int constantIndex = addConstant(block, constant); // Get the constant's index in the constant pool

    if (constantIndex < UINT8_MAX) { // If the constant pool has less than 256 constants, append the constant and represent its index as a single byte
        blockWrite(block, OP_CONSTANT);
        blockWrite(block, (uint8_t) constantIndex);
    } else { // Otherwise split the number into three bytes and write a different instrcution
        blockWrite(block, OP_CONSTANT_LONG);
        blockWrite(block, (uint8_t) (constantIndex & 0xff));
        blockWrite(block, (uint8_t) ((constantIndex >> 8) & 0xff));
        blockWrite(block, (uint8_t) ((constantIndex >> 16) & 0xff));
    }
}