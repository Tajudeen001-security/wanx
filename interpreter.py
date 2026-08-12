# WanX Interpreter

from parser import (
    NumberNode, StringNode, BoolNode, VarNode,
    BinaryOpNode, UnaryOpNode, AssignNode, PulseNode,
    ProbeNode, BlockNode
)

class RuntimeError(Exception):
    pass


class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined name '{name}'")


class Interpreter:
    def __init__(self):
        self.global_env = Environment()

    def interpret(self, node, env=None):
        if env is None:
            env = self.global_env
        return self.visit(node, env)

    def visit(self, node, env):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise RuntimeError(f"No visit method for {type(node).__name__}")
        return method(node, env)

    def visit_NumberNode(self, node, env):
        return node.value

    def visit_StringNode(self, node, env):
        return node.value

    def visit_BoolNode(self, node, env):
        return node.value

    def visit_VarNode(self, node, env):
        return env.get(node.name)

    def visit_UnaryOpNode(self, node, env):
        value = self.visit(node.operand, env)
        if node.op == "-":
            return -value
        raise RuntimeError(f"Unknown unary operator {node.op}")

    def visit_BinaryOpNode(self, node, env):
        left = self.visit(node.left, env)
        right = self.visit(node.right, env)

        op = node.op
        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        if op == ">=":
            return left >= right

        raise RuntimeError(f"Unknown operator {op}")

    def visit_AssignNode(self, node, env):
        value = self.visit(node.value, env)
        env.define(node.name, value)
        return value

    def visit_PulseNode(self, node, env):
        value = self.visit(node.expr, env)
        print(value)
        return value

    def visit_ProbeNode(self, node, env):
        condition = self.visit(node.condition, env)
        if condition:
            return self.visit(node.path_branch, env)
        elif node.shadow_branch:
            return self.visit(node.shadow_branch, env)
        return None

    def visit_BlockNode(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt, env)
        return result
