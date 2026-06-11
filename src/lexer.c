#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "../include/lexer.h"

typedef struct
{
    const char *name;
    TokenType type;
} Keyword;

static Keyword keywords[] = {
    // values
    {"True", TOK_IDENT},
    {"False", TOK_IDENT},
    {"None", TOK_NULLPTR},

    // types — all map to TOK_TYPE, name stored in value
    {"bool", TOK_TYPE},
    {"char", TOK_TYPE},
    {"double", TOK_TYPE},
    {"float", TOK_TYPE},
    {"int", TOK_TYPE},
    {"long", TOK_TYPE},
    {"short", TOK_TYPE},
    {"signed", TOK_TYPE},
    {"unsigned", TOK_TYPE},
    {"void", TOK_TYPE},

    // control flow
    {"if", TOK_IF},
    {"elif", TOK_ELIF},
    {"else", TOK_ELSE},
    {"while", TOK_WHILE},
    {"for", TOK_FOR},
    {"break", TOK_BREAK},
    {"continue", TOK_CONTINUE},
    {"return", TOK_RETURN},
    {"pass", TOK_PASS},

    // logic
    {"and", TOK_AND},
    {"or", TOK_OR},
    {"not", TOK_NOT},
    {"in", TOK_IN},
    {"is", TOK_IS},

    // definitions
    {"def", TOK_DEF},
    {"class", TOK_CLASS},
    {"struct", TOK_STRUCT},
    {"enum", TOK_ENUM},
    {"typedef", TOK_TYPEDEF},
    {"union", TOK_UNION},

    // modifiers
    {"const", TOK_CONST},
    {"static", TOK_STATIC},
    {"extern", TOK_EXTERN},
    {"inline", TOK_INLINE},
    {"volatile", TOK_VOLATILE},

    // memory
    {"sizeof", TOK_SIZEOF},
    {"alignas", TOK_ALIGNAS},
    {"alignof", TOK_ALIGNOF},
    {"restrict", TOK_RESTRICT},
    {"nullptr", TOK_NULLPTR},

    // imports
    {"import", TOK_IMPORT},
    {"from", TOK_FROM},
    {"as", TOK_AS},
    {"global", TOK_GLOBAL},
    {"nonlocal", TOK_NONLOCAL},

    // error handling
    {"try", TOK_TRY},
    {"except", TOK_EXCEPT},
    {"finally", TOK_FINALLY},
    {"raise", TOK_RAISE},
    {"assert", TOK_ASSERT},

    // other
    {"del", TOK_DEL},
    {"lambda", TOK_LAMBDA},
    {"with", TOK_WITH},
    {"yield", TOK_YIELD},
    {"switch", TOK_SWITCH},
    {"case", TOK_CASE},
    {"default", TOK_DEFAULT},
    {"do", TOK_DO},

    // c lowercase bools treated as idents
    {"true", TOK_IDENT},
    {"false", TOK_IDENT},

    {NULL, TOK_UNKNOWN}};

static TokenType
keyword_type(char *word)
{
    for (int counter = 0; keywords[counter].name != NULL; counter++)
        if (strcmp(word, keywords[counter].name) == 0)
            return keywords[counter].type;
    return TOK_IDENT;
}

static TokenList
tl_new()
{
    TokenList tl;
    tl.data = malloc(sizeof(Token) * 64);
    tl.count = 0;
    tl.capacity = 64;
    return tl;
}

static void
tl_push(TokenList *tl, Token tok)
{
    if (tl->count >= tl->capacity)
    {
        tl->capacity *= 2;
        tl->data = realloc(tl->data, sizeof(Token) * tl->capacity);
    }
    tl->data[tl->count++] = tok;
}

static Token
make_tok(TokenType type, char *start, int len, int line)
{
    Token tok;
    tok.type = type;
    tok.value = strndup(start, len);
    tok.line = line;
    return tok;
}

TokenList
lexer(char *src, unsigned int len)
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

        // whitespace
        else if (src[curlen] == ' ' ||
                 src[curlen] == '\r' ||
                 src[curlen] == '\t')
        {
            curlen++;
        }

        // comments
        else if (src[curlen] == '#')
        {
            while (curlen < len && src[curlen] != '\n')
                curlen++;
        }

        // strings
        else if (src[curlen] == '"')
        {
            curlen++;
            unsigned int start = curlen;
            while (curlen < len && src[curlen] != '"')
                curlen++;
            tl_push(&tl, make_tok(TOK_STRING, src + start, curlen - start, line));
            curlen++;
        }

        // numbers
        else if (isdigit(src[curlen]))
        {
            unsigned int start = curlen;
            while (curlen < len && isdigit(src[curlen]))
                curlen++;

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

        // identifiers / keywords
        else if (isalpha(src[curlen]) || src[curlen] == '_')
        {
            unsigned int start = curlen;
            while (curlen < len && (isalnum(src[curlen]) || src[curlen] == '_'))
                curlen++;

            char *word = strndup(src + start, curlen - start);
            TokenType type = keyword_type(word);
            tl_push(&tl, make_tok(type, word, strlen(word), line));
            free(word);
        }

        // +
        else if (src[curlen] == '+')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_PLUS_EQ, "+=", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_PLUS, "+", 1, line));
                curlen++;
            }
        }

        // -
        else if (src[curlen] == '-')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_MINUS_EQ, "-=", 2, line));
                curlen += 2;
            }
            else if (src[curlen + 1] == '>')
            {
                tl_push(&tl, make_tok(TOK_ARROW, "->", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_MINUS, "-", 1, line));
                curlen++;
            }
        }

        // *
        else if (src[curlen] == '*')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_STAR_EQ, "*=", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_STAR, "*", 1, line));
                curlen++;
            }
        }

        // /
        else if (src[curlen] == '/')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_SLASH_EQ, "/=", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_SLASH, "/", 1, line));
                curlen++;
            }
        }

        // %
        else if (src[curlen] == '%')
        {
            tl_push(&tl, make_tok(TOK_PERCENT, "%", 1, line));
            curlen++;
        }

        // &
        else if (src[curlen] == '&')
        {
            tl_push(&tl, make_tok(TOK_AMP, "&", 1, line));
            curlen++;
        }

        // |
        else if (src[curlen] == '|')
        {
            tl_push(&tl, make_tok(TOK_PIPE, "|", 1, line));
            curlen++;
        }

        // ^
        else if (src[curlen] == '^')
        {
            tl_push(&tl, make_tok(TOK_CARET, "^", 1, line));
            curlen++;
        }

        // ~
        else if (src[curlen] == '~')
        {
            tl_push(&tl, make_tok(TOK_TILDE, "~", 1, line));
            curlen++;
        }

        // =
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

        // !
        else if (src[curlen] == '!')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_NEQ, "!=", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_NOT, "!", 1, line));
                curlen++;
            }
        }

        //
        else if (src[curlen] == '<')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_LTE, "<=", 2, line));
                curlen += 2;
            }
            else if (src[curlen + 1] == '<')
            {
                tl_push(&tl, make_tok(TOK_LSHIFT, "<<", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_LT, "<", 1, line));
                curlen++;
            }
        }

        // >
        else if (src[curlen] == '>')
        {
            if (src[curlen + 1] == '=')
            {
                tl_push(&tl, make_tok(TOK_GTE, ">=", 2, line));
                curlen += 2;
            }
            else if (src[curlen + 1] == '>')
            {
                tl_push(&tl, make_tok(TOK_RSHIFT, ">>", 2, line));
                curlen += 2;
            }
            else
            {
                tl_push(&tl, make_tok(TOK_GT, ">", 1, line));
                curlen++;
            }
        }

        // delimiters
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
        else if (src[curlen] == '[')
        {
            tl_push(&tl, make_tok(TOK_LBRACKET, "[", 1, line));
            curlen++;
        }
        else if (src[curlen] == ']')
        {
            tl_push(&tl, make_tok(TOK_RBRACKET, "]", 1, line));
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
        else if (src[curlen] == ';')
        {
            tl_push(&tl, make_tok(TOK_SEMICOLON, ";", 1, line));
            curlen++;
        }
        else if (src[curlen] == '.')
        {
            tl_push(&tl, make_tok(TOK_DOT, ".", 1, line));
            curlen++;
        }
        else if (src[curlen] == '@')
        {
            tl_push(&tl, make_tok(TOK_AT, "@", 1, line));
            curlen++;
        }

        // unknown
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
    char *src = "x = 1 + 2\nif x == 3:\n    return x\n";
    TokenList tl = lexer(src, strlen(src));

    for (int idx = 0; idx < tl.count; idx++)
        printf("line %d  %d  '%s'\n", tl.data[idx].line, tl.data[idx].type, tl.data[idx].value);

    return 0;
}