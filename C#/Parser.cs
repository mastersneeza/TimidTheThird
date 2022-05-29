using System.Collections.Generic;
using System;

using Timid.Debug;
using Timid.Lex;

namespace Timid.Parse {

    class ParseError : Exception {};
    
    class Parser {

        private List<Token> tokens;
        private int index = -1;

        private Token CurrentTok { get => this.tokens[this.index]; }
        private Token Previous { get => this.tokens[this.index - 1]; }

        private bool IsAtEnd { get => this.CurrentTok.type == TokenType.T_EOF; }

        private bool Check(TokenType type) {
            if (this.IsAtEnd) return false;
            return this.CurrentTok.type == type;
        }

        private Token Advance() {
            if (! this.IsAtEnd) this.index++;
            return this.Previous;
        }

        private ParseError Error(Token token, string message) {
            ErrorReporter.SyntaxError(token, message);
            return new ParseError();
        }

        private Token Consume(TokenType type, string message) {
            if (this.Check(type)) return this.Advance();
            throw this.Error(this.CurrentTok, message);
        }

        private bool Match(params TokenType[] types) {
            foreach (TokenType type in types) {
                if (this.Check(type)) {
                    this.Advance();
                    return true;
                }
            }

            return false;
        }

        public Parser(List<Token> tokens) {
            this.tokens = tokens;
            this.Advance();
        }

        private Expr Expression() {
            return this.Unary();
        }

        private Expr Unary() {
            if (this.Match(TokenType.T_NOT, TokenType.T_PLUS, TokenType.T_MINUS)) {
                Token op = this.Previous;
                Expr right = this.Unary();
                return new Expr.UnaryExpr(op, right);
            };

            return this.Atom();
    
        }

        private Expr Atom() {
            if (this.Match(TokenType.T_INT, TokenType.T_FLOAT, TokenType.T_TRUE, TokenType.T_FALSE, TokenType.T_NULL)) return new Expr.LiteralExpr(this.Previous);
            if (this.Match(TokenType.T_LPAR)) {
                Expr expr = this.Expression();
                this.Consume(TokenType.T_RPAR, $"Expected a closing ')' (after {this.Previous.lexeme})");
                return expr;
            }

            throw this.Error(this.CurrentTok, "Expected an expression");
        }

        public Expr? Parse() {
            try {
                return this.Expression();
            } catch (ParseError) {
                return null;
            }
        }
    }
}