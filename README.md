# ForWhile

A children's programming language designed to teach Object-Oriented Programming (OOP) and core simulation concepts through a natural, world-building narrative syntax.

## Philosophy

Every feature in ForWhile is designed to serve a world-building and simulation philosophy:
1. **Teaches Real Programming Concepts**: Maps directly to classes, objects, traits/properties, composition, methods, constructor methods, loops, and conditions.
2. **Easy to Understand**: Reads like plain English narration.
3. **Unique Design**: Avoids being "Python with English words" by treating everything as creatures, traits, and actions.
4. **Reinforces World-building**: Code reads like a fantasy story or game setup.

## Syntax Comparison

| Concept | Python / Old Syntax | ForWhile Syntax |
| :--- | :--- | :--- |
| Class / Blueprint | `class Dragon:` | `creature Dragon` |
| Instantiation | `Ember = Dragon("Ember")` | `bring Ember to life as Dragon with ("Ember")` |
| State Mutation | `Ember.health = 100` | `give Ember the trait health to 100` |
| Composition | `attach Fire to Ember` | `attach Fire to Ember` |
| Method / Action | `def breathe(self):` | `action breathe` |
| Method Call | `Ember.breathe()` | `Ember does breathe` |
| Constructor | `def __init__(self):` | `when born` |
| Loops | `while not condition:` | `until condition` |
| Conditionals | `if condition: ... else:` | `when condition: ... otherwise:` |

## Directory Structure

```text
forwhile/
├── forwhile/
│   ├── __init__.py       (Exposes runner)
│   ├── lexer.py          (Lexer logic using PLY)
│   ├── parser.py         (Parser logic using PLY)
│   ├── interpreter.py    (CLI / Tree-walk interpreter)
│   └── errors.py         (Graceful custom exceptions)
├── tests/
│   └── test_basic.py     (Pytest test suite)
├── examples/
│   └── 01_hello.fw       (World-building story sample)
├── setup.py              (CLI configuration)
├── README.md             (Documentation)
└── requirements.txt      (Requirements list)
```

## Installation

Install in editable developer mode:

```bash
pip install -e .
```

## Usage

Run any ForWhile program using the CLI:

```bash
forwhile examples/01_hello.fw
```
