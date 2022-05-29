#ifndef T_VALUE_H
#define T_VALUE_H

#include "common.h"

typedef struct Obj Obj;
typedef struct ObjString ObjString;

typedef long long t_int;
typedef double t_float;

#define T_INT_SIZE (sizeof(t_int))
#define T_FLOAT_SIZE (sizeof(t_float))

#define IS_INT(value) ((value).type == V_INT)
#define IS_FLOAT(value) ((value).type == V_FLOAT)
#define IS_BOOL(value) ((value).type == V_BOOL)
#define IS_NULL(value) ((value).type == V_NULL)
#define IS_OBJ(value) ((value).type == V_OBJ)

#define IS_NUMERIC(value) (isNumeric(value))

#define TIMID_INT(number) ((Value){V_INT, {.integer = number}})
#define TIMID_FLOAT(number) ((Value){V_FLOAT, {.decimal = number}})
#define TIMID_BOOL(value) ((Value){V_BOOL, {.boolean = value}})
#define TIMID_NULL ((Value){V_NULL, {.boolean = false}})
#define TIMID_OBJ(object) ((Value){V_OBJ, {.obj = object}}) // Accepts a pointer to an object

#define AS_INT(value) ((value).as.integer)
#define AS_FLOAT(value) ((value).as.decimal)
#define AS_BOOL(value) ((value).as.boolean)
#define AS_OBJ(value) ((value).as.obj)

// Accepts a value object
#define NUM_2_INT(value) (TIMID_INT(toInt(value)))
#define NUM_2_FLOAT(value) (TIMID_FLOAT(toFloat(value)))

typedef enum {
    V_INT,
    V_FLOAT,
    V_BOOL,
    V_NULL,
    V_OBJ
} ValueType;

typedef struct {
    ValueType type;
    union {
        t_int integer;
        t_float decimal;
        bool boolean;
        Obj* obj;
    } as;
} Value;

typedef struct {
    int count;
    int capacity;
    Value* values;
} ValueArray;

void vaInit(ValueArray* va);
void vaWrite(ValueArray* va, Value Value);
void vaFree(ValueArray* va);
void vaPrint(ValueArray* va);

t_int toInt(Value value);
t_float toFloat(Value value);
ObjString* toString(Value value);
bool subscriptValue(Value iterable, Value subscript, Value* vaPtr);
bool truth(Value value);
bool isNumeric(Value value);
bool isIntegral(Value value);
bool equals(Value a, Value b);
bool lessThan(Value a, Value b);
bool greaterThan(Value a, Value b);
bool typesEqual(Value a, Value b);
void printValue(Value value);
double asNumber(Value value);
#endif