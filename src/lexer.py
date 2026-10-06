import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

# with open("/home/god_spud/STUFFS/GS/example/examples.txt", "r") as FILE:
#    code = FILE.read()


class Color:
    RESET = "\033[0m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BOLD = "\033[1m"


class ErrorCode(Enum):
    UNKNOWN_CHARACTER = auto()
    INVALID_NUMBER = auto()
    INVALID_IDENTIFIER = auto()
    UNTERMINATED_STRING = auto()
    UNTERMINATED_COMMENT = auto()
    INVALID_ESCAPE = auto()

    UNEXPECTED_EOF = auto()
    UNMATCHED_BRACKET = auto()
    INVALID_TOKEN = auto()
    INVALID_BASE_NUMBER = auto()
    INVALID_SUFFIX = auto()


class Severity(Enum):
    ERROR = auto()
    WARNING = auto()


@dataclass
class LexerDiagnostic:
    code: ErrorCode
    severity: Severity
    message: str
    row: int
    col: int
    source_line: str = ""
    highlight_length: int = 1


    def format(self):
        colour = Color.RED if self.severity == Severity.ERROR else Color.YELLOW
    
        out = []
    
        out.append(
            f"{colour}{self.severity.name}{Color.RESET}"
            f" [{self.code.name}]"
            f" at {self.row}:{self.col + 1}"
        )
    
        out.append(self.message)
    
        if self.source_line:
            out.append("")
            out.append(f"{self.row:>4} | {self.source_line}")
            out.append(
                " " * (len(str(self.row)) + 3)
                + "| "
                + " " * self.col
                + "^" * max(self.highlight_length, 1)
            )
    
        return "\n".join(out)


class LexerError(Exception):
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic
        super().__init__(diagnostic.message)


class LexerWarning:
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic


@dataclass
class LexResult:
    tokens: list
    errors: list
    warnings: list

    @property
    def success(self):
        return len(self.errors) == 0

    def finish(self):
        for warning in self.warnings:
            print(warning.diagnostic.format())
        for error in self.errors:
            print(error.diagnostic.format())
        if self.errors:
            sys.exit(1)

@dataclass
class Token:
    raw: object
    kind: str
    row: int
    col: int

    TOKENS = {
        # brackets
        "(": "LNORPAREN",
        ")": "RNORPAREN",
        "[": "LSQRPAREN",
        "]": "RSQRPAREN",
        "{": "LCRBPAREN",
        "}": "RCRBPAREN",
        # operators
        "+": "PLUS",
        "-": "MINUS",
        # * is down further as ASTERISK
        "/": "DIVIDE",
        # statements
        ";": "EOL",
        # control
        "if": "IF",
        # ternary if
        "?": "TIF",
        "elif": "ELIF",
        "else": "ELSE",
        "while": "WHILE",
        "for": "FOR",
        "in": "IN",
        "match": "MATCH",
        "case": "CASE",
        "default": "DEFAULT",
        "break": "BREAK",
        "continue": "CONTINUE",
        "pass": "PASS",
        # functions
        "def": "DEF",
        "class": "CLASS",
        "return": "RETURN",
        # types
        "int": "TYPE",
        "float": "TYPE",
        "str": "TYPE",
        "bool": "TYPE",
        "list": "TYPE",
        "dict": "TYPE",
        "set": "TYPE",
        "tuple": "TYPE",
        "void": "TYPE",
        "any": "TYPE",
        # exceptions
        "try": "TRY",
        "except": "EXCEPT",
        "finally": "FINALLY",
        "raise": "RAISE",
        "assert": "ASSERT",
        # operators words
        "and": "AND",
        "&&": "AND",
        "or": "OR",
        "||": "OR",
        "not": "NOT",
        "!": "NOT",
        "is": "IS",
        "=": "ASSIGN",
        "==": "EQ",
        "!=": "NE",
        "<": "LT",
        ">": "GT",
        "<=": "LE",
        ">=": "GE",
        # misc
        "const": "CONST",
        "del": "DEL",
        "with": "WITH",
        "from": "FROM",
        "as": "AS",
        "#include": "INCLUDE",
        # literals
        "True": "TRUE",
        "False": "FALSE",
        "None": "NONE",
        ",": "COMMA",
        ".": "DOT",
        ":": "COLON",
        "EOF": "EOF",
        "*": "ASTERISK",
        "&": "AMPERSAND",
        "@": "AT",
        "%": "MOD"
    }

    def __repr__(self):
        return f"Token(" f"{self.raw!r}, " f"{self.kind}, " f"{self.row}:{self.col})"

    @classmethod
    def make(cls, raw, row, col, forced=None):
        if forced:
            kind = forced
        elif raw in cls.TOKENS:
            kind = cls.TOKENS[raw]
        else:
            kind = "IDENT"
        return cls(raw, kind, row, col)


class Lexer:
    def __init__(self, source, emit_newlines=False):
        self.source = source
        self.length = len(source)
        self.cursor = 0
        self.row = 1
        self.col = 0
        self.lines = source.splitlines()
        self.tokens = []
        self.errors = []
        self.warnings = []
        self.bracket_stack = []
        self.token_cursor = 0
        self.emit_newlines = emit_newlines

    def peek(self, amount=0):
        pos = self.cursor + amount
        if pos >= self.length:
            return None
        return self.source[pos]

    def advance(self):
        char = self.peek()
        if char is None:
            return None
        self.cursor += 1
        if char == "\n":
            self.row += 1
            self.col = 0
        else:
            self.col += 1
        return char

    def match(self, text):
        end = self.cursor + len(text)
        if self.source[self.cursor : end] == text:
            for _ in text:
                self.advance()
            return True
        return False

    def add_token(self, raw, row, col, forced=None):
        self.tokens.append(Token.make(raw, row, col, forced))


    def error(
        self,
        code,
        message,
        row=None,
        col=None,
        length=1,
    ):
        if row is None:
            row = self.row

        if col is None:
            col = self.col

        # row is 1-based, list index is 0-based
        source_line = ""
        if 1 <= row <= len(self.lines):
            source_line = self.lines[row - 1]

        diagnostic = LexerDiagnostic(
            code=code,
            severity=Severity.ERROR,
            message=message,
            row=row,
            col=col,
            source_line=source_line,
            highlight_length=length,
        )

        self.errors.append(LexerError(diagnostic))


    def warning(
        self,
        code,
        message,
        row=None,
        col=None,
        length=1,
    ):
        if row is None:
            row = self.row

        if col is None:
            col = self.col

        # row is 1-based, list index is 0-based
        source_line = ""
        if 1 <= row <= len(self.lines):
            source_line = self.lines[row - 1]

        diagnostic = LexerDiagnostic(
            code=code,
            severity=Severity.WARNING,
            message=message,
            row=row,
            col=col,
            source_line=source_line,
            highlight_length=length,
        )

        self.warnings.append(LexerWarning(diagnostic))

    def lex(self):
        while self.peek() is not None:
            char = self.peek()
            if char == "&":
                self.lex_mem_modifier(self.row, self.col)
                continue
            if char == "@":
                self.lex_modifier(self.row, self.col)
                continue
            if char == "#":
                self.lex_include(self.row, self.col)
                continue
            if char.isspace():
                if char == "\n" and self.emit_newlines:
                    self.add_token("\n", self.row, self.col, "NEWLINE")
                self.advance()
                continue
            start_row = self.row
            start_col = self.col
            if char.isalpha() or char == "_":
                self.lex_identifier(start_row, start_col)
                continue
            if char.isdigit():
                self.lex_number(start_row, start_col)
                continue
            if char in "()[]{}":
                self.lex_bracket(start_row, start_col)
                continue
            if self.lex_comment():
                continue
            if char in "-,.;:?%":
                self.add_token(self.advance(), start_row, start_col)
                continue
            if self.lex_operator(start_row, start_col):
                continue
            if char in ("'", '"') or (char == "r" and self.peek(1) in ("'", '"')):
                self.lex_string(start_row, start_col)
                continue
            self.error(ErrorCode.UNKNOWN_CHARACTER, f"Unknown character {char!r}")
            self.advance()
            print("e")
        self.check_brackets()
        self.tokens.append(Token(None, "EOF", self.row, self.col))
        return LexResult(self.tokens, self.errors, self.warnings)

    def lex_identifier(self, row, col):
        out = []
        while True:
            char = self.peek()
            if char is not None and (char.isalnum() or char == "_"):
                out.append(self.advance())
            else:
                break
        value = "".join(out)
        if self.peek() is not None and (self.peek() in "$@"):
            self.error(
                ErrorCode.INVALID_IDENTIFIER,
                (f"Invalid character " f"in identifier {value!r}"),
            )
        literal_types = {"True": "BOOL", "False": "BOOL", "None": "NONE"}
        if value in literal_types:
            self.tokens.append(Token(value, literal_types[value], row, col))
        else:
            self.tokens.append(Token.make(value, row, col))

    def lex_number(self, row, col):
        out = []
        base = 10
        if self.peek() == "0" and self.peek(1) in ("x", "X"):
            base = 16
            out.append(self.advance())
            out.append(self.advance())
            while self.peek() is not None and (
                self.peek().isdigit() or self.peek().lower() in "abcdef"
            ):
                out.append(self.advance())
        elif self.peek() == "0" and self.peek(1) in ("b", "B"):
            base = 2
            out.append(self.advance())
            out.append(self.advance())
            while self.peek() in ("0", "1"):
                out.append(self.advance())
        elif self.peek() == "0" and self.peek(1) in ("o", "O"):
            base = 8
            out.append(self.advance())
            out.append(self.advance())
            while self.peek() is not None and self.peek() in "01234567":
                out.append(self.advance())
        else:
            while self.peek() is not None and self.peek().isdigit():
                out.append(self.advance())
            if self.peek() == ".":
                out.append(self.advance())
                while self.peek() is not None and self.peek().isdigit():
                    out.append(self.advance())
        value = "".join(out)
        suffix = None
        if self.peek() is not None and self.peek().isalpha():
            suffix = self.advance()
        try:
            if suffix == "f":
                token = Token(float(value), "FLOAT", row, col)
            elif base != 10:
                token = Token(int(value, base), "INT", row, col)
            elif "." in value:
                token = Token(float(value), "FLOAT", row, col)
            else:
                token = Token(int(value), "INT", row, col)
        except ValueError:
            self.error(
                ErrorCode.INVALID_BASE_NUMBER, f"Invalid number {value}", row, col
            )
            return
        self.tokens.append(token)

    def lex_bracket(self, row, col):
        char = self.advance()
        opening = {"(": ")", "[": "]", "{": "}"}
        closing = {")": "(", "]": "[", "}": "{"}
        if char in opening:
            self.bracket_stack.append((char, row, col))
        elif char in closing:
            if not self.bracket_stack:
                self.error(
                    ErrorCode.UNMATCHED_BRACKET,
                    f"Unexpected closing bracket {char!r}",
                    row,
                    col,
                )
            else:
                expected = self.bracket_stack[-1][0]
                if opening[expected] != char:
                    self.error(
                        ErrorCode.UNMATCHED_BRACKET,
                        (f"Expected " f"{opening[expected]!r}, " f"got {char!r}"),
                        row,
                        col,
                    )
                else:
                    self.bracket_stack.pop()
        self.add_token(char, row, col)

    def lex_operator(self, row, col):
        two_char = (self.peek() or "") + (self.peek(1) or "")
        operators_2 = {"==", "!=", "<=", ">=", "&&", "||"}
        if two_char in operators_2:
            self.advance()
            self.advance()
            self.add_token(two_char, row, col)
            return True
        operators_1 = {"+", "-", "*", "/", "=", "<", ">", "!"}
        if self.peek() in operators_1:
            char = self.advance()
            self.add_token(char, row, col)
            return True
        return False

    def lex_string(self, row, col):
        raw = False
        if self.peek() == "r":
            raw = True
            self.advance()
        quote = self.advance()
        triple = False
        if self.peek() == quote and self.peek(1) == quote:
            triple = True
            self.advance()
            self.advance()
        chars = []
        while True:
            current = self.peek()
            if current is None:
                self.error(
                    ErrorCode.UNTERMINATED_STRING, "String was never closed", row, col
                )
                return
            if current == quote:
                if triple:
                    if self.peek(1) == quote and self.peek(2) == quote:
                        self.advance()
                        self.advance()
                        self.advance()
                        break
                else:
                    self.advance()
                    break
            if current == "\\" and not raw:
                self.advance()
                escaped = self.peek()
                if escaped is None:
                    self.error(
                        ErrorCode.UNTERMINATED_STRING, "Escape reached EOF", row, col
                    )
                    return
                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    "'": "'",
                    '"': '"',
                }
                if escaped not in escapes:
                    self.error(
                        ErrorCode.INVALID_ESCAPE, (f"Unknown escape " f"\\{escaped}")
                    )
                    chars.append(escaped)
                else:
                    chars.append(escapes[escaped])
                self.advance()
                continue
            chars.append(self.advance())
        self.tokens.append(Token("".join(chars), "STR", row, col))

    def lex_comment(self):
        if self.peek() == "/" and self.peek(1) == "/":
            while self.peek() is not None and self.peek() != "\n":
                self.advance()
            return True
        if self.peek() == "/" and self.peek(1) == "*":
            start_row = self.row
            start_col = self.col
            self.advance()
            self.advance()
            while True:
                if self.peek() is None:
                    self.error(
                        ErrorCode.UNTERMINATED_COMMENT,
                        "Block comment was never closed",
                        start_row,
                        start_col,
                    )
                    return True
                if self.peek() == "*" and self.peek(1) == "/":
                    self.advance()
                    self.advance()
                    break
                self.advance()
            return True
        return False

    def check_brackets(self):
        while self.bracket_stack:
            bracket, row, col = self.bracket_stack.pop()
            self.error(
                ErrorCode.UNMATCHED_BRACKET,
                (f"Unclosed bracket " f"{bracket!r}"),
                row,
                col,
            )

    def peek_token(self, amount=0):
        pos = self.token_cursor + amount
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]

    def consume_token(self):
        token = self.peek_token()
        if token is not None:
            self.token_cursor += 1
        return token

    def expect_token(self, kind):
        token = self.consume_token()
        if token is None:
            return False
        if token.kind != kind:
            self.error(
                ErrorCode.INVALID_TOKEN,
                (f"Expected {kind}, " f"got {token.kind}"),
                token.row,
                token.col,
            )
            return False
        return True

    def lex_include(self, row, col):
        text = []
        while self.peek() is not None and not self.peek().isspace():
            text.append(self.advance())
        value = "".join(text)
        if value != "#include":
            self.error(ErrorCode.INVALID_TOKEN, f"Unknown directive {value}", row, col)
            return
        self.tokens.append(Token(value, "INCLUDE", row, col))

    def lex_modifier(self, row, col):
        modifier = []
        while self.peek() is not None and not self.peek().isspace():
            modifier.append(self.advance())
        value = "".join(modifier)
        self.tokens.append(Token(value, "AT", row, col))

    def lex_mem_modifier(self, row, col):
        type_of_op = self.peek()
        if type_of_op == "*":
            self.tokens.append(Token(type_of_op, "ASTERISK", row, col))
        elif type_of_op == "&":
            self.tokens.append(Token(type_of_op, "AMPERSAND", row, col))
        else:
            self.error(
                ErrorCode.INVALID_TOKEN,
                f"Unknown memory modifier {type_of_op}",
                row,
                col,
            )
            return
        self.advance()


class Run:
    def run_lexer(self, source):
        lexer = Lexer(source)
        result = lexer.lex()
        result.finish()
        return result.tokens

    def tokenize(self, source):
        result = Lexer(source).lex()
        if not result.success:
            result.finish()
        return result.tokens


# lexed = Run().run_lexer(code)
# out_path = Path("~/STUFFS/GS/lexed.txt").expanduser()
# out_path.parent.mkdir(parents=True, exist_ok=True)
# with out_path.open("w", encoding="utf-8") as FILE:
#     for out in lexed:
#         FILE.write(str(out) + "\n")
