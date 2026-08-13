#!/usr/bin/env python3
"""
WanX Programming Language
Version 0.4 – Forge Edition
Completely original language created by JagX and JRILICENSE
Powerful enough for systems, apps, games, web backends and AI
"""

import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, RuntimeError

def run(source: str, interpreter: Interpreter):
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter.interpret(ast)
    except SyntaxError as e:
        print(f"[Syntax Error] {e}")
    except RuntimeError as e:
        print(f"[Runtime Error] {e}")
    except Exception as e:
        print(f"[Error] {e}")

def run_file(filename: str):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return
    interpreter = Interpreter()
    run(source, interpreter)

def run_repl():
    print("WanX v0.4 Forge Edition")
    print("Original language by JagX and JRILICENSE")
    print("Type 'exit' or Ctrl+C to quit")
    print("-" * 50)
    interpreter = Interpreter()

    while True:
        try:
            line = input("wanx> ")
            if line.strip().lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            if not line.strip():
                continue
            run(line, interpreter)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

def main():
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        run_repl()

if __name__ == "__main__":
    main()