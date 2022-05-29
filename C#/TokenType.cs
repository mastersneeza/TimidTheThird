namespace Timid.Lex {
    enum TokenType {
        T_INT, T_FLOAT, T_IDENTIFIER, T_STRING, 
        T_TRUE, T_FALSE, T_NULL,

        T_PLUS, T_MINUS, T_STAR, T_SLASH, T_PERCENT, T_CARET,

        T_EQ, T_EE, T_NOT, T_NE, T_LT, T_LTE, T_GT, T_GTE,

        T_LPAR, T_RPAR, T_LCURL, T_RCURL,

        T_QMARK, T_AT, T_DOLLAR, T_BWOR, T_BWAND,

        T_ASSERT,

        T_DOT, T_SEMIC, T_COLON,

        T_EOF
    };
}