import sys

from Compiler import *
from Error import ErrorReporter
from Lexer import Lexer
from Parser import *
from Interpreter import Interpreter

class Timid:
    INTERPRETER = Interpreter()
    @staticmethod
    def init():
        args = sys.argv[1:]
        if len(args) < 1:
            Timid.run_repl()
        else:
            for file in args:
                Timid.run_file(file)

    @staticmethod
    def run(source : str, path : str):
        lexer = Lexer(source, path)
        tokens = lexer.lex()

        parser = Parser(tokens)
        statements = parser.parse()

        if ErrorReporter.HAD_ERROR:
            return

        c = Compiler(statements)
        c.compile("mai1.timb")

        if ErrorReporter.HAD_ERROR:
            return

        Timid.INTERPRETER.interpret(statements)

    @staticmethod
    def run_file(path):
        with open(path) as f:
            source = f.read()

        if len(source) <= 0: # If the file is empty then don't do anything
            sys.exit(64)

        Timid.run(source, path)

    @staticmethod
    def run_repl():
        while True:
            ErrorReporter.HAD_ERROR = False

            source = input("Timid > ")

            if len(source) <= 0: continue

            Timid.run(source, "<stdin>")

if __name__ == "__main__":
    Timid.init()
    