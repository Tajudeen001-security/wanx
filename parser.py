# WanX Parser – Original syntax
# Structure: probe ... path ... shadow ... close

from lexer import TokenType

class NumberNode:
    def __init__(self, value):
        self.value = value

class StringNode:
    def __init__(self, value):
        self.value = value

class BoolNode:
    def __init__(self, value):
        self.value = value

class VarNode:
    def __init__(self, name):
        self.name = name

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class AssignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PulseNode:
    def __init__(self, expr):
        self.expr = expr

class ProbeNode:
    def __init__(self, condition, path_branch, shadow_branch=None):
        self.condition = condition
        self.path_branch = path_branch
        self.shadow_branch = shadow_branch

class BlockNode:
    def __init__(self, statements):
        self.statements = statements


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.current()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def match(self, *types):
        if self.current().type in types:
            return self.advance()
        return None

    def expect(self, type_):
        token = self.match(type_)
        if not token:
            raise SyntaxError(
                f"Expected {type_.name}, got {self.current().type.name} on line {self.current().line}"
            )
        return token

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            pass

    def parse(self):
        statements = []
        self.skip_newlines()
        while self.current().type != TokenType.EOF:
            statements.append(self.statement())
            self.skip_newlines()
        return BlockNode(statements)

    def statement(self):
        if self.match(TokenType.PULSE):
            expr = self.expression()
            return PulseNode(expr)

        if self.match(TokenType.FORGE):
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUAL)
            value = self.expression()
            return AssignNode(name, value)

        if self.match(TokenType.PROBE):
            condition = self.expression()
            self.skip_newlines()
            self.expect(TokenType.PATH)
            self.skip_newlines()

            path_statements = []
            while self.current().type not in (TokenType.SHADOW, TokenType.CLOSE, TokenType.EOF):
                path_statements.append(self.statement())
                self.skip_newlines()

            shadow_statements = None
            if self.match(TokenType.SHADOW):
                self.skip_newlines()
                shadow_statements = []
                while self.current().type not in (TokenType.CLOSE, TokenType.EOF):
                    shadow_statements.append(self.statement())
                    self.skip_newlines()

            self.expect(TokenType.CLOSE)

            path_block = BlockNode(path_statements)
            shadow_block = BlockNode(shadow_statements) if shadow_statements is not None else None
            return ProbeNode(condition, path_block, shadow_block)

        return self.expression()

    def expression(self):
        return self.equality()

    def equality(self):
        node = self.comparison()
        while True:
            if self.match(TokenType.EQEQ):
                right = self.comparison()
                node = BinaryOpNode(node, "==", right)
            elif self.match(TokenType.NOTEQ):
                right = self.comparison()
                node = BinaryOpNode(node, "!=", right)
            else:
                break
        return node

    def comparison(self):
        node = self.term()
        while True:
            if self.match(TokenType.LT):
                right = self.term()
                node = BinaryOpNode(node, "<", right)
            elif self.match(TokenType.GT):
                right = self.term()
                node = BinaryOpNode(node, ">", right)
            elif self.match(TokenType.LTE):
                right = self.term()
                node = BinaryOpNode(node, "<=", right)
            elif self.match(TokenType.GTE):
                right = self.term()
                node = BinaryOpNode(node, ">=", right)
            else:
                break
        return node

    def term(self):
        node = self.factor()
        while True:
            if self.match(TokenType.PLUS):
                right = self.factor()
                node = BinaryOpNode(node, "+", right)
            elif self.match(TokenType.MINUS):
                right = self.factor()
                node = BinaryOpNode(node, "-", right)
            else:
                break
        return node

    def factor(self):
        node = self.unary()
        while True:
            if self.match(TokenType.STAR):
                right = self.unary()
                node = BinaryOpNode(node, "*", right)
            elif self.match(TokenType.SLASH):
                right = self.unary()
                node = BinaryOpNode(node, "/", right)
            else:
                break
        return node

    def unary(self):
        if self.match(TokenType.MINUS):
            operand = self.unary()
            return UnaryOpNode("-", operand)
        return self.primary()

    def primary(self):
        token = self.current()

        if self.match(TokenType.NUMBER):
            return NumberNode(token.value)
        if self.match(TokenType.STRING):
            return StringNode(token.value)
        if self.match(TokenType.YES):
            return BoolNode(True)
        if self.match(TokenType.NO):
            return BoolNode(False)
        if self.match(TokenType.IDENTIFIER):
            return VarNode(token.value)
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Unexpected token {token.type.name} on line {token.line}")
