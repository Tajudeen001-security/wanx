# wanx
A 🆕 powerful model programming language by JagX and JRILICENSE 
# WanX

# WanX

**WanX** is an original programming language created from scratch by JagX and JRILICENSE.

It uses a completely unique vocabulary and syntax. It does **not** copy Python, JavaScript, C, or any other major language.

**Goal of this version (0.3):** Provide enough power so that complete software systems — including foundational AI algorithms — can be built entirely inside WanX without relying on any other language or external libraries beyond the interpreter itself.

---

## Unique Keywords

| Action                    | Keyword     |
|---------------------------|-------------|
| Output / Print            | `pulse`     |
| Create / assign variable  | `forge`     |
| Conditional               | `probe`     |
| True branch               | `path`      |
| False branch              | `shadow`    |
| End of block              | `close`     |
| Boolean true              | `yes`       |
| Boolean false             | `no`        |
| Function definition       | `weave`     |
| Return from function      | `emit`      |
| While loop                | `orbit`     |
| Break from loop           | `break`     |
| Continue loop             | `continue`  |
| Logical and               | `and`       |
| Logical or                | `or`        |
| Logical not               | `not`       |
| Comments                  | `::`        |

---

## Core Syntax Examples

### Hello + Variables + Conditionals
```wanx
:: Welcome to WanX
pulse "Hello from WanX!"

forge name = "Creator"
pulse "Welcome, " + name

forge a = 10
forge b = 3

probe a > b path
    pulse "a is bigger"
shadow
    pulse "a is not bigger"
close