from src.lexer import Run
from src.parser import Parser
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description="A CLI tool that uses a lexer.")
parser.add_argument("filepath", type=Path, help="Path to the file you want to process")

args = parser.parse_args()

if not args.filepath.is_file():
    print(f"Error: The file '{args.filepath}' does not exist.")
    raise SystemExit(1)

print(f"Successfully loaded file path: {args.filepath}")

with open(args.filepath, "r") as FILE:
    code = FILE.read()

lexed = Run().run_lexer(code)

with open("out.txt", "a") as FILE:
    print(f"===== {args.filepath} =====", file=FILE)

    # Tokens
    print("\n--- TOKENS ---", file=FILE)
    for token in lexed:
        print(token, file=FILE)

    # Parser / AST
    print("\n--- AST ---", file=FILE)

    try:
        parser = Parser(lexed, source=code)
        ast = parser.parse()

        print(ast, file=FILE)

    except Exception as error:
        # Error goes AFTER everything else
        print("\n--- ERROR ---", file=FILE)
        print(error, file=FILE)

    print("\n" + "=" * 60 + "\n", file=FILE)
