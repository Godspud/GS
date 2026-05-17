#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "../include/lexer.h"

// keywords
static const char *keywords[] = {
    // PY ones
    "False", "class", "from", "or",
    "None", "continue", "global", "pass",
    "True", "def", "if", "raise",
    "and", "del", "import", "return",
    "as", "elif", "in", "try",
    "assert", "else", "is", "while",
    "async", "except", "lambda", "with",
    "await", "finally", "nonlocal", "yeild",
    "break", "for", "not",
    // C ones
    // i think thats all
    "alignas",
    "alignof",
    "bool",
    "break",
    "case",
    "char",
    "const",
    "constexpr",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "false",
    "float",
    "for",
    "if",
    "inline",
    "int",
    "long",
    "nullptr",
    "restrict",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "static_assert",
    "struct",
    "switch",
    "thread_local",
    "true",
    "typedef",
    "typeof",
    "typeof_unqual",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while",
    NULL};

static int
is_keyword(char *word)
{
    for (int counter = 0; keywords[counter] != NULL; counter++)
        if (strcmp(word, keywords[counter]) == 0)
            return 1;
    return 0;
}

// dynamic token array
typedef struct
{
    Token *data;
    int count;
    int capacity;
} TokenList;

TokenList tl_new()
{
    TokenList tl;
    tl.data = malloc(sizeof(Token) * 64);
    tl.count = 0;
    tl.capacity = 64;
    return tl;
}

void tl_push(TokenList *tl, Token tok)
{
    if (tl->count >= tl->capacity)
    {
        tl->capacity *= 2;
        tl->data = realloc(tl->data, sizeof(Token) * tl->capacity);
    }
    tl->data[tl->count++] = tok;
}

// make a token
static Token make_tok(TokenType type, char *start, int len, int line)
{
    Token tok;
    tok.type = type;
    tok.value = strndup(start, len); // copies the string
    tok.line = line;
    return tok;
}

TokenList lexer(char *src, unsigned int len)
{
    TokenList tl = tl_new();
    unsigned int curlen = 0;
    int line = 1;

    while (curlen < len)
    {
        // newline
        if (src[curlen] == '\n')
        {
            tl_push(&tl, make_tok(TOK_NEWLINE, "\n", 1, line));
            line++;
            curlen++;
        }

        // skip whitespace + carriage return
        else if (src[curlen] == ' ' || src[curlen] == '\r' || src[curlen] == '\t')
        {
            curlen++;
        }

        // single line comment  # like python
        else if (src[curlen] == '#')
        {
            while (curlen < len && src[curlen] != '\n')
                curlen++;
        }

        // string literal
        else if (src[curlen] == '"')
        {
            curlen++; // skip opening "
            unsigned int start = curlen;
            while (curlen < len && src[curlen] != '"')
                curlen++;
            tl_push(&tl, make_tok(TOK_STRING, src + start, curlen - start, line));
            curlen++; // skip closing "
        }

        // number
        else if (isdigit(src[curlen]))
        {
            unsigned int start = curlen;
            while (curlen < len && isdigit(src[curlen]))
                curlen++;
            // float
            if (src[curlen] == '.')
            {
                curlen++;
                while (curlen < len && isdigit(src[curlen]))
                    curlen++;
                tl_push(&tl, make_tok(TOK_FLOAT, src + start, curlen - start, line));
            }
            else
            {
                tl_push(&tl, make_tok(TOK_INT, src + start, curlen - start, line));
            }
        }

        // identifier or keyword
        else if (isalpha(src[curlen]) || src[curlen] == '_')
        {
            unsigned int start = curlen;
            while (curlen < len && (isalnum(src[curlen]) || src[curlen] == '_'))
                curlen++;
            char *word = strndup(src + start, curlen - start);
            TokenType type = is_keyword(word) ? TOK_KEYWORD : TOK_IDENT;
            Token tok = make_tok(type, word, curlen - start, line);
            free(word);
            tl_push(&tl, tok);
        }

        // operators + delimiters
        else if (src[curlen] == '+')
        {
            tl_push(&tl, make_tok(TOK_PLUS, "+", 1, line));
            curlen++;
        }
        else if (src[curlen] == '-')
        {
            tl_push(&tl, make_tok(TOK_MINUS, "-", 1, line));
            curlen++;
        }
        else if (src[curlen] == '*')
        {
            tl_push(&tl, make_tok(TOK_STAR, "*", 1, line));
            curlen++;
        }
        else if (src[curlen] == '/')
        {
            tl_push(&tl, make_tok(TOK_SLASH, "/", 1, line));
            curlen++;
        }
        else if (src[curlen] == '(')
        {
            tl_push(&tl, make_tok(TOK_LPAREN, "(", 1, line));
            curlen++;
        }
        else if (src[curlen] == ')')
        {
            tl_push(&tl, make_tok(TOK_RPAREN, ")", 1, line));
            curlen++;
        }
        else if (src[curlen] == '{')
        {
            tl_push(&tl, make_tok(TOK_LBRACE, "{", 1, line));
            curlen++;
        }
        else if (src[curlen] == '}')
        {
            tl_push(&tl, make_tok(TOK_RBRACE, "}", 1, line));
            curlen++;
        }
        else if (src[curlen] == ',')
        {
            tl_push(&tl, make_tok(TOK_COMMA, ",", 1, line));
            curlen++;
        }
        else if (src[curlen] == ':')
        {
            tl_push(&tl, make_tok(TOK_COLON, ":", 1, line));
            curlen++;
        }

        // = or ==
        else if (src[curlen] == '=')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_EQEQ, "==", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_EQ, "=", 1, line));
                curlen++;
            }
        }

        // ! or !=
        else if (src[curlen] == '!')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_NEQ, "!=", 2, line));
                curlen += 2;
            }
            else
            {
                curlen++; // unknown, skip
            }
        }

        // < or <=
        else if (src[curlen] == '<')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_LTE, "<=", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_LT, "<", 1, line));
                curlen++;
            }
        }

        // > or >=
        else if (src[curlen] == '>')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_GTE, ">=", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_GT, ">", 1, line));
                curlen++;
            }
        }

        // unknown char
        else
        {
            fprintf(stderr, "unknown char '%c' at line %d\n", src[curlen], line);
            curlen++;
        }
    }

    tl_push(&tl, make_tok(TOK_EOF, "", 0, line));
    return tl;
}

int main()
{
    char *src = "for counter in range(0,100):\nprint(counter) ";
    TokenList tl = lexer(src, strlen(src));

    for (int counter = 0; counter < tl.count; counter++)
        printf("line %d  %-10s  '%s'\n",
               tl.data[counter].line,
               // print token type as string
               tl.data[counter].type == TOK_IDENT ? "IDENT" : tl.data[counter].type == TOK_KEYWORD ? "KEYWORD"
                                                          : tl.data[counter].type == TOK_INT       ? "INT"
                                                          : tl.data[counter].type == TOK_FLOAT     ? "FLOAT"
                                                          : tl.data[counter].type == TOK_STRING    ? "STRING"
                                                          : tl.data[counter].type == TOK_EQ        ? "EQ"
                                                          : tl.data[counter].type == TOK_EQEQ      ? "EQEQ"
                                                          : tl.data[counter].type == TOK_NEQ       ? "NEQ"
                                                          : tl.data[counter].type == TOK_LT        ? "LT"
                                                          : tl.data[counter].type == TOK_GT        ? "GT"
                                                          : tl.data[counter].type == TOK_LTE       ? "LTE"
                                                          : tl.data[counter].type == TOK_GTE       ? "GTE"
                                                          : tl.data[counter].type == TOK_PLUS      ? "PLUS"
                                                          : tl.data[counter].type == TOK_MINUS     ? "MINUS"
                                                          : tl.data[counter].type == TOK_STAR      ? "STAR"
                                                          : tl.data[counter].type == TOK_SLASH     ? "SLASH"
                                                          : tl.data[counter].type == TOK_LPAREN    ? "LPAREN"
                                                          : tl.data[counter].type == TOK_RPAREN    ? "RPAREN"
                                                          : tl.data[counter].type == TOK_LBRACE    ? "LBRACE"
                                                          : tl.data[counter].type == TOK_RBRACE    ? "RBRACE"
                                                          : tl.data[counter].type == TOK_COMMA     ? "COMMA"
                                                          : tl.data[counter].type == TOK_COLON     ? "COLON"
                                                          : tl.data[counter].type == TOK_NEWLINE   ? "NEWLINE"
                                                          : tl.data[counter].type == TOK_EOF       ? "EOF"
                                                                                                   : "OTHER",
               tl.data[counter].value);

    return 0;
}