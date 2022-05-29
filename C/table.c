#include <stdio.h>
#include <string.h>

#include "debug.h"
#include "memory.h"
#include "object.h"
#include "table.h"

#define TABLE_MAX_LOAD 0.75

// TODO: add support for any value to be used as hashmap key

static void tableDbg(const char* funcName, const char* format, ...) {
    #ifdef T_TABLE_DBG
    fprintf(stderr, "table.c :: %s : ", funcName);
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputs("\n", stderr);
    #endif
}

static Entry* findEntry(Entry* entries, int capacity, ObjString* key) {
    uint32_t index = key->hash % capacity; // Start at the bucket where the entry should go, namely hash modded by capacity

    Entry* tombstone = NULL;
    
    for (;;) {
        Entry* entry = &entries[index]; // Get the first ideal bucket entry
        if (entry->key == NULL) {
            if (IS_NULL(entry->value)) // If the bucket is empty
                return tombstone != NULL ? tombstone : entry; // Return whichever bucket can be used
            else if (tombstone == NULL)
                tombstone = entry;
        } else if (entry->key == key) // If we found the entry, return the entry
            return entry;

        index = (index + 1) % capacity; // Go to the next entry by linear probing
    }
}

static void adjustCapacity(Table* table, int capacity) {
    Entry* entries = ALLOCATE(Entry, capacity);
    for (int i = 0; i < capacity; i++) {
        entries[i].key = NULL;
        entries[i].value = TIMID_NULL;
    }

    table->count = 0; // Reset the count and do not include tombstones in the count
    for (int i = 0; i < table->capacity; i++) {
        Entry* entry = &table->entries[i];
        if (entry->key == NULL) continue;

        Entry* destination = findEntry(entries, capacity, entry->key);
        destination->key = entry->key;
        destination->value = entry->value;
        table->count++;
    }

    FREE_ARRAY(Entry, table->entries, table->capacity);
    table->entries = entries;
    table->capacity = capacity;
}

void tableInit(Table* table) {
    table->count = 0;
    table->capacity = 0;
    table->entries = NULL;
    tableDbg("tableInit", "initialize table %p\n", table);
}

bool tableGet(Table* table, ObjString* key, Value* value) { // Accepts the pointer to the value to retrieve to
    // If table is empty we cannot return anything
    if (table->count == 0) return false;

    Entry* entry = findEntry(table->entries, table->capacity, key);
    // If the bucket is empty we cannot return anything
    if (entry->key == NULL) return false;

    // Otherwise get what is in the bucket
    *value = entry->value;
    return true;

}

bool tableSet(Table* table, ObjString* key, Value value) {
    if (table->count + 1 > table->capacity * TABLE_MAX_LOAD) {
        int capacity = GROW_CAPACITY(table->capacity);
        adjustCapacity(table, capacity);
        #ifdef T_TABLE_DBG
        printf("table.c :: tableSet : adjust table %p capacity to %d buckets\n", table, capacity);
        #endif
    }
    
    Entry* entry = findEntry(table->entries, table->capacity, key);
    bool isNewKey = entry->key == NULL;
    if (isNewKey && IS_NULL(entry->value)) table->count++; // If the entry is not going into a tombstone

    entry->key = key;
    entry->value = value;

    #ifdef T_TABLE_DBG
    printf("table.c :: tableSet : set key '");
    printObject(TIMID_OBJ(&key->obj));
    printf("' to value ");
    printValue(value);
    printf(", on table %p. Table buckets in use is now %d\n", table, table->count);
    #endif

    return isNewKey;
}

bool tableDelete(Table* table, ObjString* key) {
    if (table->count == 0) return false;

    Entry* entry = findEntry(table->entries, table->capacity, key);
    if (entry->key == NULL) return false;

    // Convert the entry into a tombstone
    entry->key = NULL;
    entry->value = TIMID_BOOL(true);
    #ifdef T_TABLE_DBG
    printf("table.c :: tableDelete : delete key '");
    printValue(TIMID_OBJ(&key->obj));
    printf("' from table %p\n", table);
    #endif
    return true;
}

void tableCopy(Table* source, Table* destination) {
    for (int i = 0; i < source->capacity; i++) {
        Entry* entry = &source->entries[i];
        if (entry->key != NULL) {
            tableSet(destination, entry->key, entry->value);
        }
    }
}

void tableFree(Table* table) {
    FREE_ARRAY(Entry, table->entries, table->capacity);
    #ifdef T_TABLE_DBG
    printf("table.c :: tableFree : free table %p\n", table);
    #endif
    tableInit(table);
}

ObjString* tableFindString(Table* table, const char* chars, int length, uint32_t hash) {
    if (table->count == 0) return NULL;

    uint32_t index = hash % table->capacity;
    for (;;) {
        Entry* entry = &table->entries[index];
        if (entry->key == NULL) {
            // Stop if a tombstone is found
            if (IS_NULL(entry->value)) return NULL;
        } else { 
            bool stringsEqualLength = entry->key->length == length;
            bool hashesEqual = entry->key->hash == hash;
            bool bytesEqual = memcmp(entry->key->chars, chars, length) == 0;
            if (stringsEqualLength && hashesEqual && bytesEqual) {
                // String is found
                return entry->key;
            }
        }

        index = (index + 1) % table->capacity;
    }
}