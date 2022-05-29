import sys

from Runtime import RuntimeError
from Token import *

class ErrorReporter: # To report errors
    HAD_ERROR = False
    HAD_RUNTIME_ERROR = False

    def string_with_arrows(pos_start : Position, pos_end : Position):
        result = ''
        text = pos_start.source

        # Calculate indices
        idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)
        
        # Generate each line
        line_count = pos_end.line - pos_start.line + 1
        for i in range(line_count):
            # Calculate line columns
            line = text[idx_start:idx_end]
            col_start = pos_start.column if i == 0 else 0
            col_end = pos_end.column if i == line_count - 1 else len(line) - 1

            # Append to result
            result += line + '\n'
            result += ' ' * col_start + '^' * (col_end - col_start)

            # Re-calculate indices
            idx_start = idx_end
            idx_end = text.find('\n', idx_start + 1)
            if idx_end < 0: idx_end = len(text)

        return result.replace('\t', '')

    @staticmethod
    def invalid_character(pos_start : Position, pos_end : Position, message : str): # Lexer
        ErrorReporter.report("Invalid Character", pos_start, pos_end, message)

    @staticmethod
    def missing_quote(pos_start : Position, pos_end : Position, message : str): # Lexer
        ErrorReporter.report("Missing Quote", pos_start, pos_end, message)

    @staticmethod
    def syntax_error(token : Token, message : str): # Parser
        ErrorReporter.report("Syntax", token.pos_start, token.pos_end, message)

    @staticmethod
    def resolve_error(token : Token, message : str): # Parser
        ErrorReporter.report("Resolution", token.pos_start, token.pos_end, message)

    @staticmethod
    def compile_error(expr, message : str): # Parser
        ErrorReporter.report("Compile", expr.pos_start, expr.pos_end, message)

    @staticmethod
    def assertion_error(error : RuntimeError):
        sys.stderr.write(f"Assertion Error @ {error.position}:\n")
        sys.stderr.write(f"\t{error.message}\n")
        sys.stderr.write(ErrorReporter.string_with_arrows(error.position, error.pos_end) + "\n")
        ErrorReporter.HAD_RUNTIME_ERROR = True

    @staticmethod
    def runtime_error(error : RuntimeError): # Interpreter
        sys.stderr.write(f"Runtime Error @ {error.position}:\n")
        sys.stderr.write(f"\t{error.message}\n")
        sys.stderr.write(ErrorReporter.string_with_arrows(error.position, error.pos_end) + "\n")
        ErrorReporter.HAD_RUNTIME_ERROR = True

    @staticmethod
    def report(err_name : str, pos_start : Position, pos_end, message : str):
        sys.stderr.write(f"{err_name} Error @ {pos_start}:\n")
        sys.stderr.write(f"\t{message}\n")
        sys.stderr.write(ErrorReporter.string_with_arrows(pos_start, pos_end) + "\n")
        ErrorReporter.HAD_ERROR = True