using System;
using System.Linq;

using Timid.Lex;

namespace Timid.Debug {
    class Position {
        private int index;
        private int line;
        private int column;
        private string source;
        private string path;

        public int Index { get => this.index; }
        public int Line { get => this.line; }
        public int Column { get => this.column; }
        public string Source { get => this.source; }
        public string Path { get => this.path; }
        public Position(int index, int line, int column, string source, string path) {
            this.index = index;
            this.line = line;
            this.column = column;
            this.source = source;
            this.path = path;
        }

        public Position Advance(char currentChar) {
            this.index++;
            this.column++;

            if (currentChar == '\n') {
                this.line++;
                this.column = 0;
            }

            return this;
        }

        public Position Copy() => new Position(this.Index, this.Line, this.Column, this.Source, this.Path);
        public override string ToString() => $"({this.Line + 1}, {this.Column + 1})";
        
        //public override string ToString() => $"Position({this.Index}, {this.Line}, {this.Column}, {this.Source}, {this.Path})";
    }
    class ErrorReporter {
        public static bool hadError = false;
        public static bool hadRuntimeError = false;

        private static string StringWithArrows(Position posStart, Position posEnd) {
            String result = "";
            String text = posStart.Source;

            // Calculate indices
            //Console.WriteLine(posStart.Index + " " + text.Length);
            int idxStart = 0;
            idxStart = Math.Max(text.LastIndexOf('\n', 0), 0);
            int idxEnd = text.IndexOf('\n', idxStart + 1);
            if (idxEnd < 0)
                idxEnd = text.Length;
            
            // Generate each line
            int lineCount = posEnd.Line - posStart.Line + 1;
            for (int i = 0; i < lineCount; i++) {
                // Calculate line columns
                string line = text.Substring(idxStart, idxEnd - idxStart);
                int colStart = i == 0 ? posStart.Column : 0;
                int colEnd = i == lineCount - 1 ? posEnd.Column : line.Length - 1;

                // Append to result
                result += line + '\n';
                result += String.Concat(Enumerable.Repeat(" ", colStart)) + String.Concat(Enumerable.Repeat("^", (colEnd - colStart)));

                // Re-calculate indices
                idxStart = idxEnd;
                idxEnd = text.IndexOf('\n', idxStart);
                if (idxEnd < 0) idxEnd = text.Length;
            }
            return result.Replace('\t', ' ');
        }

        public static void InvalidCharError(Position posStart, Position posEnd, String message) {
            ErrorReporter.Report("Invalid Character", posStart, posEnd, message);
        }

        public static void SyntaxError(Token token, String message) {
            ErrorReporter.Report("Syntax", token.posStart, token.posEnd, message);
        }

        public static void Report(String errorName, Position posStart, Position posEnd, String message) {
            Console.Error.WriteLine($"{errorName} Error @ {posStart}");
            Console.Error.WriteLine($"        {message}");
            Console.Error.WriteLine(ErrorReporter.StringWithArrows(posStart, posEnd));
            ErrorReporter.hadError = true;
        }
    }
}