using System;
using System.IO;
using System.Collections.Generic;

using Timid.Lex;
using Timid.Debug;
using Timid.Parse;

namespace Timid {
    class Timid {
        public static void Main(String[] args) {
            if (args.Length > 1) {
                Console.WriteLine("Usage: Timid [script]");
                Environment.Exit(64);
            } else if (args.Length == 1) {
                Timid.RunFile(args[0]);
            } else {
                Timid.RunREPL();
            }
        }

        private static void Run(String source, String path) {
            Lexer lexer = new Lexer(source, path);
            List<Token> tokens = lexer.Lex();

            foreach (Token token in tokens) {
                Console.WriteLine(token);
            }

            Parser parser = new Parser(tokens);
            Expr? ast = parser.Parse();

            if (ErrorReporter.hadError) return;

            Console.WriteLine(ast);
        } 

        public static void RunREPL() {
            for (;;) {
                Console.Write("Timid> ");
                String? line = Console.ReadLine();

                if (line == null) break;

                Timid.Run(line, "<stdin>");
                ErrorReporter.hadError = false;
            }
        }

        public static void RunFile(String path) {
            string text = File.ReadAllText(path);
            Timid.Run(new String(text), path);

            if (ErrorReporter.hadError) Environment.Exit(65);
        }
    }
}