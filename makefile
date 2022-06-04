GCC = gcc
SOURCE_DIR = 'C\'
FILES = $(SOURCE_DIR)main.c $(SOURCE_DIR)block.c $(SOURCE_DIR)debug.c $(SOURCE_DIR)memory.c $(SOURCE_DIR)object.c $(SOURCE_DIR)table.c $(SOURCE_DIR)value.c $(SOURCE_DIR)vm.c
EX_NAME = Timid
FLAGS = -o

compile:
	$(GCC) $(FILES) $(FLAGS) $(EX_NAME)