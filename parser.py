# WanX Parser – Original syntax
# Version 0.5 – Titan Edition
# Created by JagX and JRILICENSE

from lexer import TokenType

# ---------- AST Nodes ----------

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

class WeaveNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class EmitNode:
    def __init__(self, value=None):
        self.value = value

class OrbitNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ScanNode:
    def __init__(self, collection, var_name, body):
        self.collection = collection
        self.var_name = var_name
        self.body = body

class BreakNode:
    pass

class ContinueNode:
    pass

class CallNode:
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class ListNode:
    def __init__(self, elements):
        self.elements = elements

class VaultNode:
    def __init__(self, pairs):
        self.pairs = pairs

class IndexNode:
    def __init__(self, collection, index):
        self.collection = collection
        self.index = index

class IndexAssignNode:
    def __init__(self, collection, index, value):
        self.collection = collection
        self.index = index
        self.value = value

class SummonNode:
    def __init__(self, path):
        self.path = path

# Titan Edition – Classes
class FormNode:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods   # list of WeaveNode

class GetAttrNode:
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

class SetAttrNode:
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.value = value

class NewNode:
    def __init__(self, class_name, args):
        self.class_name = class_name
        self.args = args


# ---------- Parser ----------

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

        if self.match(TokenType.WEAVE):
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            params = []
            if not self.match(TokenType.RPAREN):
                params.append(self.expect(TokenType.IDENTIFIER).value)
                while self.match(TokenType.COMMA):
                    params.append(self.expect(TokenType.IDENTIFIER).value)
                self.expect(TokenType.RPAREN)
            self.skip_newlines()
            body_stmts = []
            while self.current().type not in (TokenType.CLOSE, TokenType.EOF):
                body_stmts.append(self.statement())
                self.skip_newlines()
            self.expect(TokenType.CLOSE)
            return WeaveNode(name, params, BlockNode(body_stmts))

        if self.match(TokenType.FORM):
            name = self.expect(TokenType.IDENTIFIER).value
            self.skip_newlines()
            methods = []
            while self.current().type not in (TokenType.CLOSE, TokenType.EOF):
                if self.match(TokenType.WEAVE):
                    mname = self.expect(TokenType.IDENTIFIER).value
                    self.expect(TokenType.LPAREN)
                    params = []
                    if not self.match(TokenType.RPAREN):
                        params.append(self.expect(TokenType.IDENTIFIER).value)
                        while self.match(TokenType.COMMA):
                            params.append(self.expect(TokenType.IDENTIFIER).value)
                        self.expect(TokenType.RPAREN)
                    self.skip_newlines()
                    body_stmts = []
                    while self.current().type not in (TokenType.CLOSE, TokenType.EOF, TokenType.WEAVE):
                        body_stmts.append(self.statement())
                        self.skip_newlines()
                    self.expect(TokenType.CLOSE)
                    methods.append(WeaveNode(mname, params, BlockNode(body_stmts)))
                else:
                    self.skip_newlines()
                    if self.current().type not in (TokenType.CLOSE, TokenType.EOF, TokenType.WEAVE):
                        raise SyntaxError(f"Expected weave inside form on line {self.current().line}")
            self.expect(TokenType.CLOSE)
            return FormNode(name, methods)

        if self.match(TokenType.EMIT):
            if self.current().type in (TokenType.NEWLINE, TokenType.CLOSE, TokenType.EOF,
                                       TokenType.SHADOW, TokenType.PATH, TokenType.BREAK,
                                       TokenType.CONTINUE):
                return EmitNode(None)
            return EmitNode(self.expression())

        if self.match(TokenType.ORBIT):
            condition = self.expression()
            self.skip_newlines()
            body_stmts = []
            while self.current().type not in (TokenType.CLOSE, TokenType.EOF):
                body_stmts.append(self.statement())
                self.skip_newlines()
            self.expect(TokenType.CLOSE)
            return OrbitNode(condition, BlockNode(body_stmts))

        if self.match(TokenType.SCAN):
            collection = self.expression()
            self.expect(TokenType.AS)
            var_name = self.expect(TokenType.IDENTIFIER).value
            self.skip_newlines()
            body_stmts = []
            while self.current().type not in (TokenType.CLOSE, TokenType.EOF):
                body_stmts.append(self.statement())
                self.skip_newlines()
            self.expect(TokenType.CLOSE)
            return ScanNode(collection, var_name, BlockNode(body_stmts))

        if self.match(TokenType.BREAK):
            return BreakNode()
        if self.match(TokenType.CONTINUE):
            return ContinueNode()

        if self.match(TokenType.SUMMON):
            path = self.expect(TokenType.STRING).value
            return SummonNode(path)

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
        return self.logic_or()

    def logic_or(self):
        node = self.logic_and()
        while self.match(TokenType.OR):
            right = self.logic_and()
            node = BinaryOpNode(node, "or", right)
        return node

    def logic_and(self):
        node = self.equality()
        while self.match(TokenType.AND):
            right = self.equality()
            node = BinaryOpNode(node, "and", right)
        return node

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
            elif self.match(TokenType.PERCENT):
                right = self.unary()
                node = BinaryOpNode(node, "%", right)
            else:
                break
        return node

    def unary(self):
        if self.match(TokenType.MINUS):
            operand = self.unary()
            return UnaryOpNode("-", operand)
        if self.match(TokenType.NOT):
            operand = self.unary()
            return UnaryOpNode("not", operand)
        return self.call()

    def call(self):
        node = self.primary()

        while True:
            if self.match(TokenType.LPAREN):
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                    self.expect(TokenType.RPAREN)
                node = CallNode(node, args)
            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                self.expect(TokenType.RBRACKET)
                if self.match(TokenType.EQUAL):
                    value = self.expression()
                    node = IndexAssignNode(node, index, value)
                else:
                    node = IndexNode(node, index)
            elif self.match(TokenType.DOT):
                attr = self.expect(TokenType.IDENTIFIER).value
                if self.match(TokenType.EQUAL):
                    value = self.expression()
                    node = SetAttrNode(node, attr, value)
                else:
                    node = GetAttrNode(node, attr)
            else:
                break
        return node

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
        if self.match(TokenType.CORE):
            return VarNode("core")
        if self.match(TokenType.IDENTIFIER):
            return VarNode(token.value)

        if self.match(TokenType.NEW):
            class_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            args = []
            if not self.match(TokenType.RPAREN):
                args.append(self.expression())
                while self.match(TokenType.COMMA):
                    args.append(self.expression())
                self.expect(TokenType.RPAREN)
            return NewNode(class_name, args)

        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.match(TokenType.RBRACKET):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    elements.append(self.expression())
                self.expect(TokenType.RBRACKET)
            return ListNode(elements)

        if self.match(TokenType.VAULT):
            self.expect(TokenType.LBRACE)
            pairs = []
            if not self.match(TokenType.RBRACE):
                key = self.expression()
                self.expect(TokenType.COLON)
                value = self.expression()
                pairs.append((key, value))
                while self.match(TokenType.COMMA):
                    key = self.expression()
                    self.expect(TokenType.COLON)
                    value = self.expression()
                    pairs.append((key, value))
                self.expect(TokenType.RBRACE)
            return VaultNode(pairs)

        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Unexpected token {token.type.name} on line {token.line}")