#ifndef T_DEBUG_H
#define T_DEBUG_H

#define T_DB

#ifdef T_DBG
#define T_MEM_DB
#define T_VM_DBG
#define T_STACK_DB
#define T_TABLE_DB
#define T_VAL_DB
#define T_BLOCK_DB
#define T_OBJ_DB
#endif

#include <stdarg.h>

#include "block.h"

void dumpBlock(Block* block, const char* blockName);
void disassembleBlock(Block* block, const char* blockName);
int disassembleInstruction(Block* block, int offset);

#endif