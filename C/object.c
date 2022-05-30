#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "debug.h"
#include "memory.h"
#include "object.h"
#include "table.h"
#include "vm.h"

#define ALLOCATE_OBJ(type, objType) ((type*)allocateObj(sizeof(type), objType))

static Obj* allocateObj(size_t size, ObjType objType) {
    Obj* obj = (Obj*) reallocate(NULL, 0, size);
    obj->type = objType;
    obj->next = vm.objects;
    vm.objects = obj;
    return obj;
}

static ObjString* allocateString(char* heapChars, int length, uint32_t hash) { // DONOTUSE
    ObjString* string = ALLOCATE_OBJ(ObjString, OBJ_STRING);
    string->chars = heapChars;
    string->length = length;
    string->hash = hash;
    tableSet(&vm.strings, string, TIMID_NULL);
    #ifdef T_OBJ_DBG
    printf("object.c :: allocateString : allocate string %p\n", string);
    #endif
    return string;
}

static uint32_t hashString(const char* key, int length) {
    uint32_t hash = 2166136261u;
    for (int i = 0; i < length; i++) {
        hash ^= (uint8_t)key[i];
        hash *= 16777619;
    }
    return hash;
}

ObjString* makeString(bool ownsChars, char* chars, int length) { // Maintains a pointer to the original characters
    uint32_t hash = hashString(chars, length);
    ObjString* internedString = tableFindString(&vm.strings, chars, length, hash);
    if (internedString != NULL) { // Check if the string is already interned
        #ifdef T_OBJ_DBG
        printf("object.c :: makeString : found interned string %p\n", internedString);
        #endif
        return internedString;
    }
    //printf("Hash: %d\n", hash);
    ObjString* string = ALLOCATE_OBJ(ObjString, OBJ_STRING);
    string->ownsChars = ownsChars;
    string->length = length;
    string->chars = chars;
    string->hash = hash;
    tableSet(&vm.strings, string, TIMID_NULL); // Intern string
    #ifdef T_OBJ_DBG
    printf("object.c :: makeString : make string %p with%s ownership\n", string, !ownsChars ? "out" : "");
    #endif
    return string;
}

ObjString* copyString(const char* chars, int length) { //DONOTUSE
    uint32_t hash = hashString(chars, length);

    ObjString* internedString = tableFindString(&vm.strings, chars, length, hash);
    if (internedString !=  NULL) return internedString;

    char* heapChars = ALLOCATE(char, length + 1);
    memcpy(heapChars, chars, length);
    heapChars[length] = '\0';
    #ifdef T_OBJ_DBG
    printf("object.c :: copyString : copy string\n");
    #endif
    return allocateString(heapChars, length, hash);
}

ObjString* takeString(char* chars, int length) { // DONOTUSE
    uint32_t hash = hashString(chars, length);
    ObjString* internedString = tableFindString(&vm.strings, chars, length, hash);
    if (internedString != NULL) {
        FREE_ARRAY(char, chars, length + 1);
        return internedString;
    }
    #ifdef T_OBJ_DBG
    printf("object.c :: takeString : take ownership of string\n");
    #endif
    return allocateString(chars, length, hash);
}

void printObject(Value value) {
    switch (OBJ_TYPE(value)) {
        case OBJ_STRING:
            printf("%.*s", AS_STRING(value)->length, AS_CSTRING(value));
            break;
        default:
            printf("NaN");
            break;
    }
}

bool objTruth(Value value) {
    switch (AS_OBJ(value)->type) {
        case OBJ_STRING: {
            ObjString* string = AS_STRING(value);
            return string->length > 0; // See if the string contains more than the NULL terminator character
        }
        default:
            return false;
    }
}

bool objEquals(Value a, Value b) {
    switch (AS_OBJ(a)->type) {
        case OBJ_STRING: {
            ObjString* aStr = AS_STRING(a);
            ObjString* bStr = AS_STRING(b);
            bool stringsEqualLength = aStr->length == bStr->length;
            bool hashesEqual = aStr->hash == bStr->hash;
            bool bytesEqual = memcmp(aStr->chars, bStr->chars, aStr->length) == 0;
            if (stringsEqualLength && hashesEqual && bytesEqual) {
                // Strings are equal
                return true;
            }
            return false;
        }
        default:
            return false;
    }
}