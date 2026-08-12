# wanx
A 🆕 powerful model programming language by JagX and JRILICENSE 
# WanX

**WanX** is an original programming language created from scratch.

It uses a completely unique vocabulary and syntax. It does not copy Python, JavaScript, C, or any other major language.

## Unique Keywords

| Action              | Keyword   |
|---------------------|-----------|
| Output / Print      | `pulse`   |
| Create variable     | `forge`   |
| Conditional         | `probe`   |
| True branch         | `path`    |
| False branch        | `shadow`  |
| End of block        | `close`   |
| Boolean true        | `yes`     |
| Boolean false       | `no`      |
| Comments            | `::`      |

## Example Code

```wanx
:: Welcome to WanX

pulse "Hello from WanX!"

forge name = "Creator"
pulse "Welcome, " + name

forge a = 10
forge b = 3

pulse a + b
pulse a * b

probe a > b path
    pulse "a is bigger than b"
shadow
    pulse "a is not bigger"
close
