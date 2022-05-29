#ifndef T_TABLE_H
#define T_TABLE_H

#include "common.h"
#include "value.h"

typedef struct {
    ObjString* key;
    Value value;
} Entry;

typedef struct {
    int count;
    int capacity;
    Entry* entries;
} Table;

void tableInit(Table* table);
bool tableGet(Table* table, ObjString* key, Value* value); // Returns true if the key was found
bool tableSet(Table* table, ObjString* key, Value value); // Returns true if the key value pair is a new pair
bool tableDelete(Table* table, ObjString* key); // Returns true if the delete was successful
void tableCopy(Table* source, Table* destination);
void tableFree(Table* table);
ObjString* tableFindString(Table* table, const char* chars, int length, uint32_t hash);

#endif