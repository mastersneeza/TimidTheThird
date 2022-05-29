#ifndef T_MEMORY_H
#define T_MEMORY_H

#include "common.h"

#define GROW_CAPACITY(oldCapacity) ((oldCapacity) * 2 < 8 ? 8 : (oldCapacity) * 2)
#define GROW_ARRAY(type, pointer, oldCount, newCount) ((type*)reallocate(pointer, sizeof(type) * (oldCount), sizeof(type) * (newCount)))
#define FREE_ARRAY(type, pointer, oldCount) (reallocate(pointer, sizeof(type) * (oldCount), 0))

#define FREE(type, pointer) reallocate(pointer, sizeof(type), 0)

#define ALLOCATE(type, size) ((type*)reallocate(NULL, 0, sizeof(type) * size))

void* reallocate(void* pointer, size_t oldSize, size_t newSize);
void freeObjects();

#endif