import os, sys
import subprocess, getopt, pathlib

from Compiler import *
from Error import ErrorReporter
from Lexer import Lexer
from Parser import *
from Interpreter import Interpreter
import Globals

class Timid:
    INTERPRETER = Interpreter()

    COMPILE_ONLY = False
    COMPILER_DEBUG = False

    BINARY_PATH = None

    @staticmethod
    def init():
        args = sys.argv[1:]
        if len(args) < 1:
            Timid.run_repl()
        else:
            Timid.run_files(Timid.get_args(args))

    @staticmethod
    def show_usage():
        print("Usage: Timid [-c | --compile] [-d | --dev] [--dest = <path>] [-h | --help] [-v | --version] <.timid files>")
        print("")
        print("Options:")
        print("-c, --compile:\tcompiles program without running it")
        #print("--dest:\t\tsets destination for binary files")
        print("-d, --dev:\tenables debug messages")
        print("-h, --help:\tprints this help message")
        print("-v, --version:\tprints Timid's version")

    @staticmethod
    def show_version():
        print(f"Timid version {Globals.VERSION}")

    @staticmethod
    def get_args(args):
        try:
            options, files = getopt.getopt(args, 'cdhv', ["compile", "dev", "help", "version"])
        except getopt.GetoptError as e:
            Timid.show_usage()
            sys.exit(1)

        for option, arg in options:
            match option:
                case '-c' | '--compile':
                    Timid.COMPILE_ONLY = True
                case '-d' | '--dev':
                    Timid.COMPILER_DEBUG = True
                case '-h' | '--help':
                    Timid.show_usage()
                    sys.exit(64)
                case '-v' | '--version':
                    Timid.show_version()
                    sys.exit(64)

        return files

    @staticmethod
    def run_files(files : list[str]):
        for file in files:
            path = pathlib.Path(file)

            Timid.compile_file(path)

    @staticmethod
    def read_file(path : pathlib.Path):
        if path.exists():
            with path.open('r') as f:
                source = f.read()
        else:
            ErrorReporter.file_not_found(path)
            sys.exit(65)
        return source

    @staticmethod
    def lex(path : pathlib.Path):
        source = Timid.read_file(path)

        lexer = Lexer(source, path.absolute())
        tokens = lexer.lex()

        return tokens

    @staticmethod
    def parse(tokens : list[Token]):
        parser = Parser(tokens)
        statements = parser.parse()

        return statements

    @staticmethod
    def compile_file(path : pathlib.Path):
        tokens = Timid.lex(path)

        if ErrorReporter.HAD_ERROR:
            return False

        statements = Timid.parse(tokens)

        if ErrorReporter.HAD_ERROR:
            return False

        compiler = Compiler(statements, Timid.COMPILER_DEBUG)

        binary_name = path.stem + ".timb"
        binary_path = path.absolute().parent / binary_name

        compiler.compile(binary_path)

    @staticmethod
    def run(source : str, path : str):
        lexer = Lexer(source, path)
        tokens = lexer.lex()

        parser = Parser(tokens)
        statements = parser.parse()

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
    