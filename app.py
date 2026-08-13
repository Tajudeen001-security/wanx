#!/usr/bin/env python3
"""
WanX Playground Website + Database + Defensive Security Helpers
Created for JagX and JRILICENSE
"""

import sys
import os
import io
import sqlite3
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from flask import Flask, render_template, request, jsonify, g

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, RuntimeError

app = Flask(__name__)

# ---------- Database ----------
DATABASE = os.path.join(os.path.dirname(__file__), "wanx.db")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        db.commit()

init_db()

# ---------- WanX Runner ----------
MAX_OUTPUT_CHARS = 8000

def run_wanx(source: str) -> dict:
    output = io.StringIO()
    error = None

    try:
        with redirect_stdout(output), redirect_stderr(output):
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            interp = Interpreter()
            interp.interpret(ast)
    except SyntaxError as e:
        error = f"[Syntax Error] {e}"
    except RuntimeError as e:
        error = f"[Runtime Error] {e}"
    except Exception as e:
        error = f"[Error] {e}"

    result = output.getvalue()
    if len(result) > MAX_OUTPUT_CHARS:
        result = result[:MAX_OUTPUT_CHARS] + "\n... (output truncated)"

    return {
        "success": error is None,
        "output": result,
        "error": error
    }


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/playground")
def playground():
    return render_template("playground.html")


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"success": False, "output": "", "error": "No code provided"})
    if len(code) > 15000:
        return jsonify({"success": False, "output": "", "error": "Code too long"})
    result = run_wanx(code)
    return jsonify(result)


@app.route("/api/examples")
def api_examples():
    examples = {
        "hello": ''':: Welcome to WanX
pulse "Hello from WanX!"
forge name = "Creator"
pulse "Welcome, " + name''',

        "variables": '''forge a = 10
forge b = 3
pulse a + b
pulse a * b
pulse a / b''',

        "conditionals": '''forge score = 85
probe score >= 90 path
    pulse "Excellent"
shadow
    probe score >= 70 path
        pulse "Good"
    shadow
        pulse "Keep practicing"
    close
close''',

        "functions": '''weave add(x, y)
    emit x + y
close

weave greet(person)
    pulse "Hello, " + person
close

pulse add(12, 30)
greet("WanX Learner")''',

        "loops": '''forge i = 1
orbit i <= 5
    pulse "Count: " + str(i)
    forge i = i + 1
close''',

        "lists": '''forge nums = [10, 20, 30, 40]
pulse nums
pulse "Length: " + str(len(nums))
pulse nums[0]
nums[1] = 99
push(nums, 50)
pulse nums''',

        "vault": '''forge player = vault {
    "name" : "Hero",
    "hp" : 100,
    "level" : 1
}
pulse player["name"]
player["hp"] = 85
pulse player''',

        "classes": '''form Player
    weave init(name, hp)
        core.name = name
        core.hp = hp
    close
    weave heal(amount)
        core.hp = core.hp + amount
        emit core.hp
    close
    weave status()
        pulse core.name + " has " + str(core.hp) + " HP"
    close
close

forge p = new Player("Hero", 100)
p.status()
pulse p.heal(25)
p.status()''',

        "ai": ''':: Simple gradient descent
forge xs = [1, 2, 3, 4, 5]
forge ys = [3, 5, 7, 9, 11]
forge w = 0.0
forge b = 0.0
forge lr = 0.01

weave predict(x)
    emit w * x + b
close

forge epoch = 0
orbit epoch < 100
    forge dw = 0.0
    forge db = 0.0
    forge i = 0
    orbit i < len(xs)
        forge pred = predict(xs[i])
        forge err = pred - ys[i]
        forge dw = dw + err * xs[i]
        forge db = db + err
        forge i = i + 1
    close
    forge w = w - lr * (dw / len(xs))
    forge b = b - lr * (db / len(xs))
    forge epoch = epoch + 1
close

pulse "Learned w ≈ " + str(w)
pulse "Learned b ≈ " + str(b)
pulse "Prediction for x=6: " + str(predict(6))''',

        "integrity": ''':: File / Data Integrity Check (defensive)
forge data = "important configuration data"
pulse "SHA-256: " + sha256(data)
pulse "MD5: " + md5(data)

forge encoded = b64encode(data)
pulse "Base64: " + encoded
pulse "Decoded: " + b64decode(encoded)''',

        "httpcheck": ''':: HTTP Status Check (defensive monitoring)
forge result = fetch_status("https://httpbin.org/status/200")
pulse "Status code: " + str(result["status"])
pulse "URL: " + result["url"]

forge bad = fetch_status("https://httpbin.org/status/404")
pulse "404 Status: " + str(bad["status"])''',

        "logging": ''':: Simple Security-style Logging
forge event = vault {
    "time" : now(),
    "level" : "INFO",
    "message" : "User login successful",
    "source" : "auth-service"
}
pulse tojson(event)

forge alert = vault {
    "time" : now(),
    "level" : "WARN",
    "message" : "Multiple failed attempts detected",
    "count" : 5
}
pulse tojson(alert)''',

        "hashdemo": ''':: Hashing Demo (integrity & verification)
forge password_check = sha256("user_input_here")
pulse "Hash: " + password_check

forge file_content = "config version 1.2.3"
pulse "Content hash: " + sha256(file_content)'''
    }
    return jsonify(examples)


# ---------- Database API ----------
@app.route("/api/snippets", methods=["GET"])
def list_snippets():
    db = get_db()
    rows = db.execute(
        "SELECT id, title, created_at FROM snippets ORDER BY id DESC LIMIT 50"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/snippets/<int:snippet_id>", methods=["GET"])
def get_snippet(snippet_id):
    db = get_db()
    row = db.execute(
        "SELECT id, title, code, created_at FROM snippets WHERE id = ?",
        (snippet_id,)
    ).fetchone()
    if not row:
        return jsonify({"error": "Snippet not found"}), 404
    return jsonify(dict(row))


@app.route("/api/snippets", methods=["POST"])
def save_snippet():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled").strip()[:80]
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Code is empty"}), 400
    if len(code) > 15000:
        return jsonify({"error": "Code too long"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO snippets (title, code, created_at) VALUES (?, ?, ?)",
        (title, code, datetime.utcnow().isoformat())
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "title": title, "message": "Saved"})


@app.route("/api/snippets/<int:snippet_id>", methods=["DELETE"])
def delete_snippet(snippet_id):
    db = get_db()
    db.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
    db.commit()
    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)