# WanX Lexer – Completely Original Vocabulary
# Keywords chosen to avoid resemblance to any major programming language

from enum import Enum, auto

class TokenType(Enum):
    NUMBER     = auto()
    IDENTIFIER = auto()
    STRING     = auto()
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    EQUAL      = auto()
    LPAREN     = auto()
    RPAREN     = auto()
    EQEQ       = auto()
    NOTEQ      = auto()
    LT         = auto()
    GT         = auto()
    LTE        = auto()
    GTE        = auto()
    PULSE      = auto()
    FORGE      = auto()
    PROBE      = auto()
    PATH       = auto()
    SHADOW     = auto()
    CLOSE      = auto()
    YES        = auto()
    NO         = auto()
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
    "pulse":  TokenType.PULSE,
    "forge":  TokenType.FORGE,
    "probe":  TokenType.PROBE,
    "path":   TokenType.PATH,
    "shadow": TokenType.SHADOW,
    "close":  TokenType.CLOSE,
    "yes":    TokenType.YES,
    "no":     TokenType.NO,
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
                '=': TokenType.EQUAL,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
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
