typedef enum
{
    // literals
    TOK_IDENT, // indent \t
    TOK_TYPE,  // all types eg void int bool

    // control flow
    TOK_IF,       // if statement
    TOK_ELIF,     // elif statement else if in C
    TOK_ELSE,     // else statement
    TOK_WHILE,    // while loop
    TOK_FOR,      // for loop
    TOK_BREAK,    // break out of a loop
    TOK_CONTINUE, // continue to next iteration of a loop
    TOK_RETURN,   // return from a function
    TOK_PASS,     // do nothing

    // logic
    TOK_AND, // && in C and and in PY
    TOK_OR,  // or in PY || in C
    TOK_NOT, // not in PY ! in C
    TOK_IN,  // in PY == in C
    TOK_IS,  // is in PY == in C but for types and None/True/False

    // definitions
    TOK_DEF,     // def funcs in C u use type func_name()
    TOK_CLASS,   // class in py
    TOK_STRUCT,  // struct in C
    TOK_ENUM,    // enum in C
    TOK_TYPEDEF, // typedef in C
    TOK_UNION,   // union in C

    // modifiers
    TOK_CONST,    // readonly vars in C
    TOK_STATIC,   // only visible in current file in C
    TOK_EXTERN,   // defined in another file in C
    TOK_INLINE,   // suggest to inline in C
    TOK_VOLATILE, // can be modified by other threads in C

    // memory (@CMEM stuff)
    TOK_SIZEOF,
    TOK_ALIGNAS,
    TOK_ALIGNOF,
    TOK_RESTRICT,
    TOK_NULLPTR,

    // imports
    TOK_IMPORT,
    TOK_FROM,
    TOK_AS,
    TOK_GLOBAL,
    TOK_NONLOCAL,

    // error handling
    TOK_TRY,
    TOK_EXCEPT,
    TOK_FINALLY,
    TOK_RAISE,
    TOK_ASSERT,

    // other
    TOK_DEL,
    TOK_LAMBDA,
    TOK_WITH,
    TOK_YIELD,
    TOK_SWITCH,
    TOK_CASE,
    TOK_DEFAULT,
    TOK_DO,

    // operators
    TOK_PLUS,    // +
    TOK_MINUS,   // -
    TOK_STAR,    // *
    TOK_SLASH,   // /
    TOK_PERCENT, // %
    TOK_AMP,     // &
    TOK_PIPE,    // |
    TOK_CARET,   // ^
    TOK_TILDE,   // ~
    TOK_LSHIFT,  //
    TOK_RSHIFT,  // >>

    // comparison
    TOK_EQ,   // =
    TOK_EQEQ, // ==
    TOK_NEQ,  // !=
    TOK_LT,   //
    TOK_GT,   // >
    TOK_LTE,  // <=
    TOK_GTE,  // >=

    // compound assignment
    TOK_PLUS_EQ,  // +=
    TOK_MINUS_EQ, // -=
    TOK_STAR_EQ,  // *=
    TOK_SLASH_EQ, // /=

    // delimiters
    TOK_LPAREN,    // (
    TOK_RPAREN,    // )
    TOK_LBRACE,    // {
    TOK_RBRACE,    // }
    TOK_LBRACKET,  // [
    TOK_RBRACKET,  // ]
    TOK_COMMA,     // ,
    TOK_COLON,     // :
    TOK_SEMICOLON, // ;
    TOK_DOT,       // .
    TOK_ARROW,     // ->
    TOK_AT,        // @

    // special
    TOK_NEWLINE,
    TOK_EOF,
    TOK_UNKNOWN,
} TokenType;

typedef struct
{
    TokenType type;
    char *value;
    int line;
} Token;
