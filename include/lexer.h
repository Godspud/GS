#ifndef LEXER_H
#define LEXER_H

typedef enum
{
    // literals
    TOK_INT,    // integer literal eg 42
    TOK_FLOAT,  // float literal eg 3.14
    TOK_STRING, // string literal eg "hello"
    TOK_IDENT,  // identifier names eg my_var func_name Player
    TOK_TYPE,   // all primitive/builtin types eg void int bool float

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
    TOK_AND, // logical and
    TOK_OR,  // logical or
    TOK_NOT, // logical not
    TOK_IN,  // membership test
    TOK_IS,  // identity comparison

    // definitions
    TOK_DEF,     // define a function
    TOK_CLASS,   // class definition
    TOK_STRUCT,  // struct definition
    TOK_ENUM,    // enum definition
    TOK_TYPEDEF, // create type alias
    TOK_UNION,   // union definition

    // modifiers
    TOK_CONST,    // readonly
    TOK_STATIC,   // static lifetime
    TOK_EXTERN,   // defined in another file
    TOK_INLINE,   // suggest inlining
    TOK_VOLATILE, // value may change unexpectedly

    // memory (@CMEM stuff)
    TOK_SIZEOF,   // size of type in bytes
    TOK_ALIGNAS,  // specify alignment
    TOK_ALIGNOF,  // get alignment of type
    TOK_RESTRICT, // pointer does not alias
    TOK_NULLPTR,  // null pointer literal

    // imports
    TOK_IMPORT,   // import module
    TOK_FROM,     // from x import y
    TOK_AS,       // alias import name
    TOK_GLOBAL,   // declare global variable
    TOK_NONLOCAL, // access outer non-global scope

    // error handling
    TOK_TRY,     // try block
    TOK_EXCEPT,  // exception handling block
    TOK_FINALLY, // always executed cleanup block
    TOK_RAISE,   // raise an exception
    TOK_ASSERT,  // runtime assertion check

    // other
    TOK_DEL,     // delete variable/reference
    TOK_LAMBDA,  // anonymous inline function
    TOK_WITH,    // context manager scope
    TOK_YIELD,   // yield value from generator
    TOK_SWITCH,  // switch statement
    TOK_CASE,    // switch case label
    TOK_DEFAULT, // default switch case
    TOK_DO,      // do while loop

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
    TOK_NEWLINE, // newline
    TOK_EOF,     // end of file
    TOK_UNKNOWN, // unrecognized token
} TokenType;

typedef struct
{
    TokenType type;
    char *value;
    int line;
} Token;

// token list
typedef struct
{
    Token *data;
    int count;
    int capacity;
} TokenList;

TokenList lexer(char *src, unsigned int len);

#endif