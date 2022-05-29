using System;
using System.Collections.Generic;

using Timid.Debug;

namespace Timid.Lex {
    class Token {
        public TokenType type;
        public string lexeme;
        public object? value;
        public Position posStart;
        public Position posEnd;
        public Token(TokenType type, string lexeme, object? value, Position posStart, Position? posEnd) {
            this.type = type;
            this.lexeme = lexeme;
            this.value = value;
            this.posStart = posStart.Copy();
            if (posEnd == null) 
                this.posEnd = this.posStart.Copy().Advance('\0');
            else
                this.posEnd = posEnd.Copy();
        }

        public override string ToString() {
            return $"Tok {this.type} {this.lexeme} {this.posStart} {this.posEnd}";
        }
    }

    class Lexer {
        private static Dictionary<string, TokenType> KEYWORDS = new Dictionary<string, TokenType>();

        static Lexer() {
            Lexer.KEYWORDS.Add("tru", TokenType.T_TRUE);
            Lexer.KEYWORDS.Add("fls", TokenType.T_FALSE);
            Lexer.KEYWORDS.Add("nul", TokenType.T_NULL);
        }
        private bool IsAtEnd { get => this.pos.Index >= this.source.Length; }

        private char CurrentChar {
            get {
                if (this.IsAtEnd)
                    return '\0';
                return this.source[this.pos.Index];
            }
        }
        private char NextChar {
            get {
                if (this.pos.Index + 1 >= this.source.Length)
                    return '\0';
                return this.source[this.pos.Index + 1];
            }
        }

        private string source;
        private List<Token> tokens = new List<Token>();
        private Position pos;
        public Lexer(String source, String path) {
            this.source = source;
            this.pos = new Position(0, 0, 0, source, path);
        }

        private bool IsDigit(char c) => c >= '0' && c <= '9';
        private bool IsAlpha(char c) => (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '_';
        private bool IsAlphaNum(char c) => this.IsDigit(c) || this.IsAlpha(c);

        private char Advance() {
            this.pos.Advance(this.CurrentChar);
            return this.CurrentChar;
        }

        private bool Match(char expected) {
            if (this.IsAtEnd) return false; 
            if (expected != this.CurrentChar) return false;
            this.Advance();
            return true;
        } 

        private void AddToken(TokenType type, string lexeme, object? literal, Position posStart, Position? posEnd) => this.tokens.Add(new Token(type, lexeme, literal, posStart, posEnd));

        private void SingleCharToken(TokenType type) {
            this.AddToken(type, this.CurrentChar.ToString(), null, this.pos, null);
            this.Advance();
        }

        private void LexNumber() {
            Position posStart = this.pos.Copy();
            String number = "";
            bool isInt = true;

            while (IsDigit(this.CurrentChar)) {
                number += this.CurrentChar;
                this.Advance();

                if (this.CurrentChar == '.' && this.IsDigit(this.NextChar)) {
                    isInt = false;
                    number += this.CurrentChar;
                    this.Advance(); // Consume the dot

                    while (IsDigit(this.CurrentChar)) {
                        number += this.CurrentChar;
                        this.Advance();
                    }
                }
            }

            this.AddToken(isInt ? TokenType.T_INT : TokenType.T_FLOAT, number, isInt ? Int64.Parse(number) : Double.Parse(number), posStart, this.pos);
        }

        private void LexID() {
            Position posStart = this.pos.Copy();
            string idStr = "";

            while (this.IsAlphaNum(this.CurrentChar)) {
                idStr += this.CurrentChar;
                this.Advance();
            }

            TokenType kwType;
            if (Lexer.KEYWORDS.ContainsKey(idStr)) kwType = Lexer.KEYWORDS[idStr];
            else kwType = TokenType.T_IDENTIFIER;

            this.AddToken(kwType, idStr, null, posStart, this.pos);
        }

        private void TwoCharToken(char expected, TokenType single, TokenType two) {
            Position posStart = this.pos.Copy();
            TokenType type = single;
            string lexeme = this.CurrentChar.ToString();
            this.Advance();

            if (this.CurrentChar == expected) {
                type = two;
                lexeme += this.CurrentChar;
                this.Advance();
            }

            this.AddToken(type, lexeme, null, posStart, this.pos);
        }

        private void ScanToken() {
            char c = this.CurrentChar;

            switch (c) {
                case ' ':
                case '\n':
                case '\r':
                    this.Advance();
                    break;
                case '~':
                    this.Advance();
                    if (this.CurrentChar == '~') {
                        this.Advance();
                        while (!this.IsAtEnd && this.CurrentChar != '~') 
                            this.Advance();
                        this.Advance();
                        break;
                    }
                    while (!this.IsAtEnd && this.CurrentChar != '\n')
                        this.Advance();
                    break;

                case '+': this.SingleCharToken(TokenType.T_PLUS); break;
                case '-': this.SingleCharToken(TokenType.T_MINUS); break;
                case '*': this.SingleCharToken(TokenType.T_STAR); break;
                case '/': this.SingleCharToken(TokenType.T_SLASH); break;
                case '%': this.SingleCharToken(TokenType.T_PERCENT); break;
                case '^': this.SingleCharToken(TokenType.T_CARET); break;

                case '(': this.SingleCharToken(TokenType.T_LPAR); break;
                case ')': this.SingleCharToken(TokenType.T_RPAR); break;
                case '{': this.SingleCharToken(TokenType.T_LCURL); break;
                case '}': this.SingleCharToken(TokenType.T_RCURL); break;

                case '?': this.SingleCharToken(TokenType.T_QMARK); break;
                case '@': this.SingleCharToken(TokenType.T_AT); break;
                case '$': this.SingleCharToken(TokenType.T_DOLLAR); break;
                case '.': this.SingleCharToken(TokenType.T_DOT); break;
                case ';': this.SingleCharToken(TokenType.T_SEMIC); break;

                case '=': this.TwoCharToken('=', TokenType.T_EQ, TokenType.T_EE); break;
                case '!': this.TwoCharToken('=', TokenType.T_NOT, TokenType.T_NE); break;
                case '<': this.TwoCharToken('=', TokenType.T_LT, TokenType.T_LTE); break;
                case '>': this.TwoCharToken('=', TokenType.T_GTE, TokenType.T_GTE); break;
                case '|': this.TwoCharToken('-', TokenType.T_BWOR, TokenType.T_ASSERT); break;

                default: {
                    if (IsDigit(c)) {
                        this.LexNumber();
                    } else if (IsAlpha(c)) {
                        this.LexID();
                    }
                    else {
                        Position start = this.pos.Copy();
                        char invalid = this.CurrentChar;
                        this.Advance();

                        ErrorReporter.InvalidCharError(start, this.pos, $"Invalid character '{invalid}'");
                    }
                    break;
                }
            }
        }

        public List<Token> Lex() {
            while (!this.IsAtEnd) {
                this.ScanToken();
            }

            this.AddToken(TokenType.T_EOF, "\0", null, this.pos, null);

            return this.tokens;
        }
    }
}