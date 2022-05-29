#include <stdio.h>
#include <stdlib.h>

#include "debug.h"
#include "memory.h"
#include "vm.h"

void* reallocate(void* pointer, size_t oldSize, size_t newSize) {
    if (newSize == 0) {
        //#ifdef T_MEM_DBG
        //printf("memory.c :: reallocate : free %x\n", pointer);
        //#endif
        free(pointer);
        return NULL;
    }

    void* result = realloc(pointer, newSize);
    #ifdef T_MEM_DBG
    printf("memory.c :: reallocate : reallocate %4d bytes of memory for %p\n", newSize, result);
    #endif

    if (result == NULL) {
        fprintf(stderr, "memory.c :: reallocate : failed to reallocate %d bytes of memory for %p", newSize, pointer);
        exit(1);
    }

    return result;
}

static void freeObject(Obj* object) {
    #ifdef T_MEM_DBG
    printf("memory.c :: freeObject : free object %p of type %d\n", object, object->type);
    #endif
    switch (object->type) {
        case OBJ_STRING: {
            ObjString* string = (ObjString*)object;
            if (string->ownsChars) { // The characters in the heap can only be freed if the string owns them
                FREE_ARRAY(char, (char*) string->chars, string->length + 1);
            }
            FREE(ObjString, object);
            break;
        }
    }
} 

void freeObjects() {
    Obj* object = vm.objects;
    while (object != NULL) {
        Obj* next = object->next;
        freeObject(object);
        object = next;
    }
}