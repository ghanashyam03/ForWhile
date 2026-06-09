# ForWhile

A children's programming language designed to teach Object-Oriented Programming (OOP) and core programming concepts through a plain-English syntax.

## Directory Structure

```text
forwhile/
├── forwhile/
│   ├── __init__.py
│   ├── lexer.py          (Lexer logic using PLY)
│   ├── parser.py         (Parser logic using PLY)
│   ├── interpreter.py    (CLI / Interpreter entry point)
│   └── errors.py         (Error handling stub)
├── tests/
│   └── test_basic.py     (Test suite verification)
├── examples/
│   └── hello.fw          (A simple hello world in ForWhile syntax)
├── setup.py
├── README.md
└── requirements.txt
```

## Installation

To install in editable developer mode:

```bash
pip install -e .
```

## Usage

Run any ForWhile program using the CLI:

```bash
forwhile examples/hello.fw
```
