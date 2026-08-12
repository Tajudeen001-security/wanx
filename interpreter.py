# WanX Interpreter – Version 0.3
# Completely original language designed to build full systems and AI from the ground up.
# No external language influence in vocabulary or core design philosophy.

from parser import (
    NumberNode, StringNode, BoolNode, VarNode,
    BinaryOpNode, UnaryOpNode, AssignNode, PulseNode,
    ProbeNode, BlockNode, WeaveNode, EmitNode, OrbitNode,
    BreakNode, ContinueNode, CallNode, ListNode, IndexNode, IndexAssignNode
)
import math
import random
import time

class RuntimeError(Exception):
    pass

class ReturnValue(Exception):
    """Used to unwind the call stack on emit"""
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
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

    def set(self, name, value):
        """Assign to existing or define in current scope"""
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            try:
                self.parent.set(name, value)
                return
            except RuntimeError:
                pass
        # If not found anywhere, define in current
        self.values[name] = value


class Function:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure   # environment where it was defined

    def __repr__(self):
        return f"<weave {self.name}>"


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._install_builtins(self.global_env)

    def _install_builtins(self, env):
        """Core built-ins so WanX can build complete systems & AI without anything else."""

        # --- Output / Input ---
        def builtin_pulse(*args):
            print(*args)
            return args[-1] if args else None

        def builtin_input(prompt=""):
            return input(str(prompt))

        # --- Type & conversion ---
        def builtin_type(x):
            if isinstance(x, bool):
                return "bool"
            if isinstance(x, int):
                return "int"
            if isinstance(x, float):
                return "float"
            if isinstance(x, str):
                return "string"
            if isinstance(x, list):
                return "list"
            if isinstance(x, Function):
                return "weave"
            return "unknown"

        def builtin_str(x):
            return str(x)

        def builtin_num(x):
            try:
                if isinstance(x, str) and "." in x:
                    return float(x)
                return int(x)
            except:
                raise RuntimeError(f"Cannot convert {x} to number")

        def builtin_float(x):
            return float(x)

        def builtin_int(x):
            return int(x)

        # --- List helpers ---
        def builtin_len(x):
            return len(x)

        def builtin_push(lst, item):
            if not isinstance(lst, list):
                raise RuntimeError("push expects a list")
            lst.append(item)
            return lst

        def builtin_pop(lst):
            if not isinstance(lst, list) or len(lst) == 0:
                raise RuntimeError("pop on empty or non-list")
            return lst.pop()

        def builtin_slice(lst, start, end=None):
            if end is None:
                return lst[start:]
            return lst[start:end]

        # --- Math (essential for AI / numerics) ---
        def builtin_abs(x): return abs(x)
        def builtin_sqrt(x): return math.sqrt(x)
        def builtin_pow(base, exp): return math.pow(base, exp)
        def builtin_floor(x): return math.floor(x)
        def builtin_ceil(x): return math.ceil(x)
        def builtin_round(x): return round(x)
        def builtin_sin(x): return math.sin(x)
        def builtin_cos(x): return math.cos(x)
        def builtin_tan(x): return math.tan(x)
        def builtin_log(x): return math.log(x)
        def builtin_exp(x): return math.exp(x)
        def builtin_min(*args): return min(args)
        def builtin_max(*args): return max(args)
        def builtin_sum(lst): return sum(lst)
        def builtin_pi(): return math.pi
        def builtin_e(): return math.e

        # --- Random (for AI experiments, stochastic algorithms) ---
        def builtin_random(): return random.random()
        def builtin_randint(a, b): return random.randint(int(a), int(b))
        def builtin_choice(lst): return random.choice(lst)

        # --- Time ---
        def builtin_time(): return time.time()
        def builtin_sleep(seconds): time.sleep(float(seconds)); return None

        # --- Simple vector helpers useful for AI foundations ---
        def builtin_dot(a, b):
            if len(a) != len(b):
                raise RuntimeError("dot product requires equal length lists")
            return sum(x * y for x, y in zip(a, b))

        def builtin_scale(lst, factor):
            return [x * factor for x in lst]

        def builtin_addvec(a, b):
            if len(a) != len(b):
                raise RuntimeError("vectors must be same length")
            return [x + y for x, y in zip(a, b)]

        def builtin_subvec(a, b):
            if len(a) != len(b):
                raise RuntimeError("vectors must be same length")
            return [x - y for x, y in zip(a, b)]

        # Register them
        builtins = {
            "pulse": builtin_pulse,   # also available as function
            "input": builtin_input,
            "type": builtin_type,
            "str": builtin_str,
            "num": builtin_num,
            "float": builtin_float,
            "int": builtin_int,
            "len": builtin_len,
            "push": builtin_push,
            "pop": builtin_pop,
            "slice": builtin_slice,
            "abs": builtin_abs,
            "sqrt": builtin_sqrt,
            "pow": builtin_pow,
            "floor": builtin_floor,
            "ceil": builtin_ceil,
            "round": builtin_round,
            "sin": builtin_sin,
            "cos": builtin_cos,
            "tan": builtin_tan,
            "log": builtin_log,
            "exp": builtin_exp,
            "min": builtin_min,
            "max": builtin_max,
            "sum": builtin_sum,
            "pi": builtin_pi,
            "e": builtin_e,
            "random": builtin_random,
            "randint": builtin_randint,
            "choice": builtin_choice,
            "time": builtin_time,
            "sleep": builtin_sleep,
            "dot": builtin_dot,
            "scale": builtin_scale,
            "addvec": builtin_addvec,
            "subvec": builtin_subvec,
        }
        for name, fn in builtins.items():
            env.define(name, fn)

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

    # ---- Literals & variables ----
    def visit_NumberNode(self, node, env):
        return node.value

    def visit_StringNode(self, node, env):
        return node.value

    def visit_BoolNode(self, node, env):
        return node.value

    def visit_VarNode(self, node, env):
        return env.get(node.name)

    def visit_ListNode(self, node, env):
        return [self.visit(el, env) for el in node.elements]

    # ---- Operators ----
    def visit_UnaryOpNode(self, node, env):
        value = self.visit(node.operand, env)
        if node.op == "-":
            return -value
        if node.op == "not":
            return not value
        raise RuntimeError(f"Unknown unary operator {node.op}")

    def visit_BinaryOpNode(self, node, env):
        # Short-circuit for logical ops
        if node.op == "or":
            left = self.visit(node.left, env)
            if left:
                return left
            return self.visit(node.right, env)
        if node.op == "and":
            left = self.visit(node.left, env)
            if not left:
                return left
            return self.visit(node.right, env)

        left = self.visit(node.left, env)
        right = self.visit(node.right, env)

        op = node.op
        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        if op == "%":
            return left % right
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

    # ---- Assignment ----
    def visit_AssignNode(self, node, env):
        value = self.visit(node.value, env)
        env.define(node.name, value)
        return value

    def visit_IndexAssignNode(self, node, env):
        collection = self.visit(node.collection, env)
        index = self.visit(node.index, env)
        value = self.visit(node.value, env)
        if not isinstance(collection, list):
            raise RuntimeError("Can only index-assign into a list")
        collection[int(index)] = value
        return value

    def visit_IndexNode(self, node, env):
        collection = self.visit(node.collection, env)
        index = self.visit(node.index, env)
        try:
            return collection[int(index)]
        except (IndexError, TypeError) as e:
            raise RuntimeError(f"Index error: {e}")

    # ---- Control flow ----
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

    def visit_OrbitNode(self, node, env):
        result = None
        while self.visit(node.condition, env):
            try:
                result = self.visit(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return result

    def visit_BreakNode(self, node, env):
        raise BreakSignal()

    def visit_ContinueNode(self, node, env):
        raise ContinueSignal()

    def visit_BlockNode(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt, env)
        return result

    # ---- Functions ----
    def visit_WeaveNode(self, node, env):
        fn = Function(node.name, node.params, node.body, env)
        env.define(node.name, fn)
        return fn

    def visit_EmitNode(self, node, env):
        value = None
        if node.value is not None:
            value = self.visit(node.value, env)
        raise ReturnValue(value)

    def visit_CallNode(self, node, env):
        callee = self.visit(node.callee, env)
        args = [self.visit(arg, env) for arg in node.args]

        # Native Python functions (builtins)
        if callable(callee) and not isinstance(callee, Function):
            try:
                return callee(*args)
            except Exception as e:
                raise RuntimeError(f"Error calling built-in: {e}")

        # User-defined weave
        if isinstance(callee, Function):
            if len(args) != len(callee.params):
                raise RuntimeError(
                    f"weave '{callee.name}' expects {len(callee.params)} arguments, got {len(args)}"
                )
            # Create new local environment that closes over definition site
            local = Environment(parent=callee.closure)
            for param, arg in zip(callee.params, args):
                local.define(param, arg)
            try:
                self.visit(callee.body, local)
                return None   # no emit → returns nothing
            except ReturnValue as ret:
                return ret.value

        raise RuntimeError(f"'{callee}' is not callable")