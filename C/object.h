#ifndef T_OBJ_H
#define T_OBJ_H

#include "common.h"
#include "value.h"

#define OBJ_TYPE(object) (AS_OBJ(object)->type)

#define IS_STRING(value) isObjType(value, OBJ_STRING)

#define TIMID_STR_2_VAL(string) (TIMID_OBJ(&string->obj))


#define TIMID_STRING(chars, length) (TIMID_STR_2_VAL(makeString(false, chars, length)))

#define AS_STRING(value) ((ObjString*)AS_OBJ(value))
#define AS_CSTRING(value) (((ObjString*)AS_OBJ(value))->chars)


#define TIMID_EMPTY_STR (TIMID_STRING("", 0))

typedef enum {
    OBJ_STRING
} ObjType;

struct Obj {
    ObjType type;
    struct Obj* next;
};

struct ObjString {
    Obj obj;
    bool ownsChars;
    int length;
    uint32_t hash;
    const char* chars;
};

ObjString* makeString(bool ownsChars, char* chars, int length); // Like copyString and takeString but with extra guarding on freeing and ownership
ObjString* copyString(const char* chars, int length); // DONOTUSE Return a new string, so ownership of the original string is not transferred
ObjString* takeString(char* chars, int length); //DONUTUSE Transfer ownership of original string
static inline bool isObjType(Value value, ObjType type) { return IS_OBJ(value) && AS_OBJ(value)->type == type; }
void printObject(Value value);

bool objTruth(Value value);
bool objEquals(Value a, Value b);
#endif