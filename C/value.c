#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "debug.h"
#include "memory.h"
#include "object.h"
#include "value.h"

void vaInit(ValueArray* va) {
    va->count = 0;
    va->capacity = 0;
    va->values = NULL;
    //assert(va->count == 0 && va->capacity == 0 && va->values == NULL);
    #ifdef T_VAL_DBG
    printf("value.c :: vaInit : initialize value array %p\n", va);
    #endif
}

void vaWrite(ValueArray* va, Value value) {
    if (va->capacity < va->count + 1) {
        int oldCapacity = va->capacity;
        va->capacity = GROW_CAPACITY(oldCapacity);
        //assert(va->capacity > oldCapacity);
        va->values = GROW_ARRAY(Value, va->values, oldCapacity, va->capacity);
        #ifdef T_VAL_DBG
        printf("value.c :: vaWrite : increase value array %p's capacity to %d values\n", va, va->capacity);
        #endif
    }
    va->values[va->count] = value;
    //assert(sizeof(va->values[va->count]) == sizeof(value));
    va->count++;
    #ifdef T_VAL_DBG
    printf("value.c :: vaWrite : write value to value array %p, member count is %d members\n", va, va->count);
    #endif
}

void vaFree(ValueArray* va) {
    FREE_ARRAY(Value, va->values, va->capacity);
    #ifdef T_VAL_DBG
    printf("value.c :: vaFree : free value array %p\n", va);
    #endif
    vaInit(va);
}

void vaPrint(ValueArray* va) {
    printf("VA %p: [", va);
    for (int i = 0; i < va->count; i++) {
        printValue(va->values[i]);
        if (i < va->count - 1) {
            printf(", ");
        }
    }
    printf("]\n");
}

t_int toInt(Value value) {
    switch (value.type) {
        case V_INT:
            return AS_INT(value);
        case V_FLOAT:
            return (t_int)AS_FLOAT(value);
        case V_BOOL:
            return (t_int)AS_BOOL(value);
        case V_NULL:
            return 0;
    }
}

t_float toFloat(Value value) {
    switch (value.type) {
        case V_INT:
            return (t_float) AS_INT(value);
        case V_FLOAT:
            return AS_FLOAT(value);
        case V_BOOL:
            return (t_float)AS_BOOL(value);
        case V_NULL:
            return (t_float)0;
    }
}

ObjString* toString(Value value) {
    switch (value.type) {
        case V_OBJ:
            switch (AS_OBJ(value)->type) {
                case OBJ_STRING:
                    return AS_STRING(value);
                default:
                    return NULL;
            }
        case V_INT: {
            char* buffer = ALLOCATE(char, 32);
            sprintf(buffer, "%d", AS_INT(value));
            return makeString(true, buffer, strlen(buffer));
        }
        case V_FLOAT: {
            char* buffer = ALLOCATE(char, 32);
            sprintf(buffer, "%g", AS_FLOAT(value));
            return makeString(true, buffer, strlen(buffer));
        }
        case V_BOOL: {
            char* buffer = ALLOCATE(char, 4);
            sprintf(buffer, AS_BOOL(value) ? "tru" : "fls");
            return makeString(true, buffer, strlen(buffer));
        }
        case V_NULL: {
            char* buffer = ALLOCATE(char, 4);
            sprintf(buffer, "nul");
            return makeString(true, buffer, strlen(buffer));
        }
        default:
            return NULL;

    }
}

bool subscriptValue(Value iterable, Value subscript, Value* vaPtr) {
    if (IS_STRING(iterable) && IS_INT(subscript)) {
        ObjString* string = AS_STRING(iterable);
        int index = AS_INT(subscript);

        if (index >= string->length) // Check if index is in bounds
            return false;

        while (index < 0) // If negative index, wrap around until positive
            index += string->length;

        char* buffer = ALLOCATE(char, 1); // Allocate buffer

        buffer[0] = string->chars[index];
        string = makeString(true, buffer, 1); // New buffer means char is owned

        *vaPtr = TIMID_STR_2_VAL(string);
        return true;
    }

    return false;
}

bool truth(Value value) {
    switch(value.type) {
        case V_INT:
            return AS_INT(value) != 0;
        case V_FLOAT:
            return AS_FLOAT(value) != 0.0;
        case V_BOOL:
            return AS_BOOL(value);
        case V_NULL:
            return false;
        case V_OBJ:
            return objTruth(value);
        default:
            return false;
    }
}

bool isNumeric(Value value) {
    return isIntegral(value) || value.type == V_FLOAT;
}

bool isIntegral(Value value) {
    return value.type == V_INT || value.type == V_BOOL || value.type == V_NULL;
}

bool equals(Value a, Value b) {
    if (a.type != b.type && !(isIntegral(a) && isIntegral(b))) return false;
    switch (a.type) {
        case V_INT:
        case V_FLOAT:
        case V_BOOL:
            return toInt(a) == toInt(b);
        case V_NULL:
            return true;
        case V_OBJ:
            return objEquals(a, b);
        default: return false;
    }
}

bool lessThan(Value a, Value b) {
    return asNumber(a) < asNumber(b);
}

bool greaterThan(Value a, Value b) {
    return asNumber(a) > asNumber(b);
}

t_float asNumber(Value value) {
    if (isNumeric(value))
        return toFloat(value);
    if (IS_STRING(value))
        return (t_float)AS_STRING(value)->length;
    return false;
}

bool typesEqual(Value a, Value b) {
    return a.type == b.type;
}

void printValue(Value value) {
    switch (value.type) {
        case V_INT:
            printf("%lld", AS_INT(value));
            break;
        case V_FLOAT:
            printf("%g", AS_FLOAT(value));
            break;
        case V_BOOL:
            printf("%s", AS_BOOL(value) ? "tru" : "fls");
            break;
        case V_NULL:
            printf("nul");
            break;
        case V_OBJ:
            printObject(value);
            break;
        default:
            printf("NaN");
            break;
    }
}