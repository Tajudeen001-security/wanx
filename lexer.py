# WanX Lexer – Completely Original Vocabulary
# Keywords chosen to avoid resemblance to any major programming language
# Version 0.4 – Forge Edition – Built for complex systems, apps, games, websites & AI
# Created by JagX and JRILICENSE

from enum import Enum, auto

class TokenType(Enum):
    # Literals
    NUMBER     = auto()
    IDENTIFIER = auto()
    STRING     = auto()

    # Operators
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    PERCENT    = auto()
    EQUAL      = auto()
    EQEQ       = auto()
    NOTEQ      = auto()
    LT         = auto()
    GT         = auto()
    LTE        = auto()
    GTE        = auto()

    # Delimiters
    LPAREN     = auto()
    RPAREN     = auto()
    LBRACKET   = auto()
    RBRACKET   = auto()
    LBRACE     = auto()
    RBRACE     = auto()
    COMMA      = auto()
    DOT        = auto()
    COLON      = auto()

    # Original Core Keywords
    PULSE      = auto()   # print / output
    FORGE      = auto()   # variable declaration
    PROBE      = auto()   # if
    PATH       = auto()   # then
    SHADOW     = auto()   # else
    CLOSE      = auto()   # end of block
    YES        = auto()   # true
    NO         = auto()   # false

    # Power Keywords (still completely original)
    WEAVE      = auto()   # function definition
    EMIT       = auto()   # return
    ORBIT      = auto()   # while loop
    SCAN       = auto()   # for-each loop
    AS         = auto()   # used with scan
    BREAK      = auto()
    CONTINUE   = auto()
    AND        = auto()
    OR         = auto()
    NOT        = auto()
    VAULT      = auto()   # dictionary / map
    SUMMON     = auto()   # import / load another file
    UNLOCK     = auto()   # open file
    GATHER     = auto()   # read
    INSCRIBE   = auto()   # write
    SEAL       = auto()   # close file

    NEWLINE    = auto()
    EOF        = auto()


class Token:
    def __init__(self, type_, value=None, line=1):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, {repr(self.value)}, line={self.line})"
        return f"Token({self.type.name}, line={self.line})"


KEYWORDS = {
    "pulse":    TokenType.PULSE,
    "forge":    TokenType.FORGE,
    "probe":    TokenType.PROBE,
    "path":     TokenType.PATH,
    "shadow":   TokenType.SHADOW,
    "close":    TokenType.CLOSE,
    "yes":      TokenType.YES,
    "no":       TokenType.NO,
    "weave":    TokenType.WEAVE,
    "emit":     TokenType.EMIT,
    "orbit":    TokenType.ORBIT,
    "scan":     TokenType.SCAN,
    "as":       TokenType.AS,
    "break":    TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "and":      TokenType.AND,
    "or":       TokenType.OR,
    "not":      TokenType.NOT,
    "vault":    TokenType.VAULT,
    "summon":   TokenType.SUMMON,
    "unlock":   TokenType.UNLOCK,
    "gather":   TokenType.GATHER,
    "inscribe": TokenType.INSCRIBE,
    "seal":     TokenType.SEAL,
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def peek(self, offset=0):
        i = self.pos + offset
        if i >= len(self.source):
            return '\0'
        return self.source[i]

    def advance(self):
        char = self.peek()
        self.pos += 1
        if char == '\n':
            self.line += 1
        return char

    def add_token(self, type_, value=None):
        self.tokens.append(Token(type_, value, self.line))

    def skip_whitespace_and_comments(self):
        while True:
            char = self.peek()
            if char in ' \t\r':
                self.advance()
            elif char == ':' and self.peek(1) == ':':
                self.advance()
                self.advance()
                while self.peek() not in '\n\0':
                    self.advance()
            else:
                break

    def number(self):
        start = self.pos
        while self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek(1).isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        text = self.source[start:self.pos]
        value = float(text) if '.' in text else int(text)
        self.add_token(TokenType.NUMBER, value)

    def identifier(self):
        start = self.pos
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        text = self.source[start:self.pos]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)

        if token_type == TokenType.YES:
            self.add_token(TokenType.YES, True)
        elif token_type == TokenType.NO:
            self.add_token(TokenType.NO, False)
        elif token_type == TokenType.IDENTIFIER:
            self.add_token(TokenType.IDENTIFIER, text)
        else:
            self.add_token(token_type)

    def string(self):
        self.advance()
        start = self.pos
        while self.peek() not in '"\0':
            if self.peek() == '\n':
                self.line += 1
            if self.peek() == '\\':
                self.advance()
            self.advance()
        if self.peek() == '\0':
            raise SyntaxError(f"Unterminated string on line {self.line}")
        value = self.source[start:self.pos]
        self.advance()
        self.add_token(TokenType.STRING, value)

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break

            char = self.peek()

            if char == '\n':
                self.advance()
                self.add_token(TokenType.NEWLINE)
                continue

            if char.isdigit():
                self.number()
                continue

            if char.isalpha() or char == '_':
                self.identifier()
                continue

            if char == '"':
                self.string()
                continue

            if char == '=' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.EQEQ)
                continue
            if char == '!' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.NOTEQ)
                continue
            if char == '<' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.LTE)
                continue
            if char == '>' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.GTE)
                continue

            single = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.STAR,
                '/': TokenType.SLASH,
                '%': TokenType.PERCENT,
                '=': TokenType.EQUAL,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                ':': TokenType.COLON,
                '<': TokenType.LT,
                '>': TokenType.GT,
            }

            if char in single:
                self.advance()
                self.add_token(single[char])
                continue

            raise SyntaxError(f"Unexpected character '{char}' on line {self.line}")

        self.add_token(TokenType.EOF)
        return self.tokens