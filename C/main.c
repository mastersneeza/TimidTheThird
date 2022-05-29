#include <stdio.h>
#include <stdlib.h>

#include "common.h"

#include "vm.h"

bool hasError = false;

FILE* openFile(const char* path) {
    FILE* file = fopen(path, "rb");

    if (file == NULL) {
        fprintf(stderr, "File Not Found Error : File '%s' could not be found\n", path);
        hasError = true;
        return NULL;
    }

    return file;
}

static size_t sizeofFile(FILE* file) {
    fseek(file, 0L, SEEK_END);
    size_t fileSize = ftell(file);
    rewind(file);
    return fileSize;
}

static uint8_t* runFile(const char* path) {
    /* FILE OPENING */
    FILE* file = openFile(path);

    size_t fileSize = sizeofFile(file);

    uint8_t* bytecode = (uint8_t*) malloc(fileSize + 1); // Allocate enough memory to store the bytecode

    if (bytecode == NULL) {
        fprintf(stderr, "Memory Error : Not enough RAM to read file '%s'", path);
        hasError = true;
        return NULL;
    }

    size_t bytesRead = fread(bytecode, sizeof(uint8_t), fileSize, file);

    if (bytesRead < fileSize) {
        fprintf(stderr, "File Read Error : Unable to finish reading file '%s'", path);
        hasError = true;
        return NULL;
    }

    bytecode[bytesRead] = '\0';

    fclose(file);

    /* FILE RUNNING */

    InterpretResult result = interpret(bytecode, fileSize);
    if (result == INTERPRET_RUNTIME_ERROR)
        hasError = true;

    return bytecode;
}

int main(int argc, const char* argv[]) {
    vmInit();

    if (argc < 2)
        //exit(64);
        goto FREE;
        
    runFile(argv[1]);

    FREE:
    vmFree();
    return 0;
}