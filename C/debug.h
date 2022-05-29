#ifndef T_DEBUG_H
#define T_DEBUG_H

#define T_DB

#ifdef T_DBG
#define T_MEM_DBG
#define T_VM_DBG
#define T_STACK_DBG
#define T_TABLE_DBG
#define T_VAL_DBG
#define T_BLOCK_DBG
#define T_OBJ_DBG
#endif

#include <stdarg.h>

#include "block.h"

void dumpBlock(Block* block, const char* blockName);
void disassembleBlock(Block* block, const char* blockName);
int disassembleInstruction(Block* block, int offset);

#endif