# WanX Interpreter – Version 0.5 Titan Edition + Defensive Security Helpers
# Completely original language by JagX and JRILICENSE
# Classes, systems, apps, games, web backends, AI and defensive security tools

from parser import (
    NumberNode, StringNode, BoolNode, VarNode,
    BinaryOpNode, UnaryOpNode, AssignNode, PulseNode,
    ProbeNode, BlockNode, WeaveNode, EmitNode, OrbitNode,
    ScanNode, BreakNode, ContinueNode, CallNode, ListNode,
    VaultNode, IndexNode, IndexAssignNode, SummonNode,
    FormNode, GetAttrNode, SetAttrNode, NewNode
)
import math
import random
import time
import os
import json
import urllib.request
import urllib.error
import hashlib
import base64
from datetime import datetime

class RuntimeError(Exception):
    pass

class ReturnValue(Exception):
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
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            try:
                self.parent.set(name, value)
                return
            except RuntimeError:
                pass
        self.values[name] = value


class Function:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure

    def __repr__(self):
        return f"<weave {self.name}>"


class Form:
    def __init__(self, name, methods):
        self.name = name
        self.methods = {m.name: m for m in methods} if methods else {}

    def __repr__(self):
        return f"<form {self.name}>"


class Instance:
    def __init__(self, form):
        self.form = form
        self.fields = {}

    def __repr__(self):
        return f"<instance of {self.form.name}>"


class BoundMethod:
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method

    def __repr__(self):
        return f"<bound {self.method.name}>"


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._install_builtins(self.global_env)
        self.loaded_modules = set()

    def _install_builtins(self, env):
        def builtin_pulse(*args):
            print(*args)
            return args[-1] if args else None

        def builtin_input(prompt=""):
            return input(str(prompt))

        def builtin_type(x):
            if isinstance(x, bool): return "bool"
            if isinstance(x, int): return "int"
            if isinstance(x, float): return "float"
            if isinstance(x, str): return "string"
            if isinstance(x, list): return "list"
            if isinstance(x, dict): return "vault"
            if isinstance(x, Function): return "weave"
            if isinstance(x, Form): return "form"
            if isinstance(x, Instance): return "instance"
            return "unknown"

        def builtin_str(x): return str(x)
        def builtin_num(x):
            try:
                if isinstance(x, str) and "." in x: return float(x)
                return int(x)
            except: raise RuntimeError(f"Cannot convert {x} to number")
        def builtin_float(x): return float(x)
        def builtin_int(x): return int(x)

        def builtin_len(x): return len(x)
        def builtin_push(lst, item):
            if not isinstance(lst, list): raise RuntimeError("push expects a list")
            lst.append(item)
            return lst
        def builtin_pop(lst):
            if not isinstance(lst, list) or len(lst) == 0:
                raise RuntimeError("pop on empty or non-list")
            return lst.pop()
        def builtin_slice(lst, start, end=None):
            if end is None: return lst[start:]
            return lst[start:end]

        def builtin_keys(v):
            if not isinstance(v, dict): raise RuntimeError("keys expects a vault")
            return list(v.keys())
        def builtin_values(v):
            if not isinstance(v, dict): raise RuntimeError("values expects a vault")
            return list(v.values())
        def builtin_has(v, key):
            if not isinstance(v, dict): raise RuntimeError("has expects a vault")
            return key in v

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

        def builtin_random(): return random.random()
        def builtin_randint(a, b): return random.randint(int(a), int(b))
        def builtin_choice(lst): return random.choice(lst)
        def builtin_shuffle(lst):
            random.shuffle(lst)
            return lst

        def builtin_time(): return time.time()
        def builtin_sleep(seconds):
            time.sleep(float(seconds))
            return None

        def builtin_dot(a, b):
            if len(a) != len(b): raise RuntimeError("dot requires equal length")
            return sum(x*y for x,y in zip(a,b))
        def builtin_scale(lst, factor): return [x * factor for x in lst]
        def builtin_addvec(a, b):
            if len(a) != len(b): raise RuntimeError("vectors must match length")
            return [x+y for x,y in zip(a,b)]
        def builtin_subvec(a, b):
            if len(a) != len(b): raise RuntimeError("vectors must match length")
            return [x-y for x,y in zip(a,b)]

        def builtin_unlock(path, mode="r"):
            try:
                return open(path, mode, encoding="utf-8")
            except Exception as e:
                raise RuntimeError(f"Cannot unlock file: {e}")
        def builtin_gather(f):
            try: return f.read()
            except Exception as e: raise RuntimeError(f"Cannot gather: {e}")
        def builtin_inscribe(f, text):
            try:
                f.write(str(text))
                return None
            except Exception as e: raise RuntimeError(f"Cannot inscribe: {e}")
        def builtin_seal(f):
            try:
                f.close()
                return None
            except Exception as e: raise RuntimeError(f"Cannot seal: {e}")

        def builtin_tojson(obj): return json.dumps(obj)
        def builtin_fromjson(s): return json.loads(s)
        def builtin_exists(path): return os.path.exists(path)

        def builtin_upper(s): return str(s).upper()
        def builtin_lower(s): return str(s).lower()
        def builtin_split(s, sep=" "): return str(s).split(sep)
        def builtin_join(lst, sep=""): return sep.join(str(x) for x in lst)
        def builtin_replace(s, old, new): return str(s).replace(str(old), str(new))
        def builtin_startswith(s, prefix): return str(s).startswith(str(prefix))
        def builtin_endswith(s, suffix): return str(s).endswith(str(suffix))
        def builtin_contains(s, sub): return str(sub) in str(s)
        def builtin_trim(s): return str(s).strip()

        def builtin_fetch(url, method="GET", data=None):
            try:
                if data is not None:
                    data = str(data).encode("utf-8")
                req = urllib.request.Request(url, data=data, method=method)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.read().decode("utf-8", errors="replace")
            except Exception as e:
                raise RuntimeError(f"fetch failed: {e}")

        def builtin_distance(x1, y1, x2, y2):
            return math.sqrt((x2-x1)**2 + (y2-y1)**2)
        def builtin_collide(x1, y1, w1, h1, x2, y2, w2, h2):
            return (x1 < x2 + w2 and x1 + w1 > x2 and
                    y1 < y2 + h2 and y1 + h1 > y2)

        # ===== Defensive Cybersecurity Helpers =====
        def builtin_sha256(data):
            if isinstance(data, str):
                data = data.encode("utf-8")
            return hashlib.sha256(data).hexdigest()

        def builtin_md5(data):
            if isinstance(data, str):
                data = data.encode("utf-8")
            return hashlib.md5(data).hexdigest()

        def builtin_b64encode(data):
            if isinstance(data, str):
                data = data.encode("utf-8")
            return base64.b64encode(data).decode("utf-8")

        def builtin_b64decode(data):
            return base64.b64decode(data).decode("utf-8", errors="replace")

        def builtin_now():
            return datetime.utcnow().isoformat() + "Z"

        def builtin_filesize(path):
            try:
                return os.path.getsize(path)
            except Exception as e:
                raise RuntimeError(f"filesize error: {e}")

        def builtin_filehash(path, algo="sha256"):
            try:
                h = hashlib.sha256() if algo == "sha256" else hashlib.md5()
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        h.update(chunk)
                return h.hexdigest()
            except Exception as e:
                raise RuntimeError(f"filehash error: {e}")

        def builtin_fetch_status(url, method="GET", data=None):
            try:
                if data is not None:
                    data = str(data).encode("utf-8")
                req = urllib.request.Request(url, data=data, method=method)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    return {
                        "status": resp.getcode(),
                        "body": body,
                        "url": url
                    }
            except urllib.error.HTTPError as e:
                return {
                    "status": e.code,
                    "body": str(e),
                    "url": url
                }
            except Exception as e:
                raise RuntimeError(f"fetch_status failed: {e}")

        builtins = {
            "pulse": builtin_pulse, "input": builtin_input, "type": builtin_type,
            "str": builtin_str, "num": builtin_num, "float": builtin_float, "int": builtin_int,
            "len": builtin_len, "push": builtin_push, "pop": builtin_pop, "slice": builtin_slice,
            "keys": builtin_keys, "values": builtin_values, "has": builtin_has,
            "abs": builtin_abs, "sqrt": builtin_sqrt, "pow": builtin_pow,
            "floor": builtin_floor, "ceil": builtin_ceil, "round": builtin_round,
            "sin": builtin_sin, "cos": builtin_cos, "tan": builtin_tan,
            "log": builtin_log, "exp": builtin_exp, "min": builtin_min, "max": builtin_max,
            "sum": builtin_sum, "pi": builtin_pi, "e": builtin_e,
            "random": builtin_random, "randint": builtin_randint, "choice": builtin_choice,
            "shuffle": builtin_shuffle, "time": builtin_time, "sleep": builtin_sleep,
            "dot": builtin_dot, "scale": builtin_scale, "addvec": builtin_addvec, "subvec": builtin_subvec,
            "unlock": builtin_unlock, "gather": builtin_gather, "inscribe": builtin_inscribe, "seal": builtin_seal,
            "tojson": builtin_tojson, "fromjson": builtin_fromjson, "exists": builtin_exists,
            "upper": builtin_upper, "lower": builtin_lower, "split": builtin_split,
            "join": builtin_join, "replace": builtin_replace, "startswith": builtin_startswith,
            "endswith": builtin_endswith, "contains": builtin_contains, "trim": builtin_trim,
            "fetch": builtin_fetch, "distance": builtin_distance, "collide": builtin_collide,
            "sha256": builtin_sha256, "md5": builtin_md5,
            "b64encode": builtin_b64encode, "b64decode": builtin_b64decode,
            "now": builtin_now, "filesize": builtin_filesize, "filehash": builtin_filehash,
            "fetch_status": builtin_fetch_status,
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

    def visit_VaultNode(self, node, env):
        result = {}
        for key_node, value_node in node.pairs:
            key = self.visit(key_node, env)
            value = self.visit(value_node, env)
            result[key] = value
        return result

    def visit_UnaryOpNode(self, node, env):
        value = self.visit(node.operand, env)
        if node.op == "-": return -value
        if node.op == "not": return not value
        raise RuntimeError(f"Unknown unary operator {node.op}")

    def visit_BinaryOpNode(self, node, env):
        if node.op == "or":
            left = self.visit(node.left, env)
            if left: return left
            return self.visit(node.right, env)
        if node.op == "and":
            left = self.visit(node.left, env)
            if not left: return left
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
        if op == "-": return left - right
        if op == "*": return left * right
        if op == "/":
            if right == 0: raise RuntimeError("Division by zero")
            return left / right
        if op == "%": return left % right
        if op == "==": return left == right
        if op == "!=": return left != right
        if op == "<": return left < right
        if op == ">": return left > right
        if op == "<=": return left <= right
        if op == ">=": return left >= right
        raise RuntimeError(f"Unknown operator {op}")

    def visit_AssignNode(self, node, env):
        value = self.visit(node.value, env)
        env.define(node.name, value)
        return value

    def visit_IndexAssignNode(self, node, env):
        collection = self.visit(node.collection, env)
        index = self.visit(node.index, env)
        value = self.visit(node.value, env)
        if isinstance(collection, list):
            collection[int(index)] = value
        elif isinstance(collection, dict):
            collection[index] = value
        else:
            raise RuntimeError("Can only index-assign into list or vault")
        return value

    def visit_IndexNode(self, node, env):
        collection = self.visit(node.collection, env)
        index = self.visit(node.index, env)
        try:
            if isinstance(collection, list):
                return collection[int(index)]
            if isinstance(collection, dict):
                return collection[index]
            raise RuntimeError("Cannot index this type")
        except (IndexError, KeyError, TypeError) as e:
            raise RuntimeError(f"Index error: {e}")

    def visit_PulseNode(self, node, env):
        value = self.visit(node