# ForWhile

[![ForWhile CI](https://github.com/ghanashyam03/ForWhile/actions/workflows/ci.yml/badge.svg)](https://github.com/ghanashyam03/ForWhile/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()

A world-building programming language designed to teach Object-Oriented Programming (OOP) and core simulation concepts to young storytellers through a plain-English, narrative-driven syntax.

---

## 📖 Quick Links

* **Language Specification**: [docs/LANGUAGE_SPEC.md](docs/LANGUAGE_SPEC.md) — Reference grammar and design decisions.
* **Educator's Guide**: [docs/EDUCATORS_GUIDE.md](docs/EDUCATORS_GUIDE.md) — CS concept mapping and 10 classroom exercises.
* **Contributor Guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md) — Set up local environment and coverage goals.
* **License**: [LICENSE](LICENSE) — MIT License.

---

## 🌟 Philosophy

Every feature in ForWhile is designed to serve a world-building and simulation philosophy:
1. **Teaches Real Programming Concepts**: Maps directly to classes, objects, traits/properties, composition, methods, constructor methods, loops, and conditions.
2. **Easy to Understand**: Reads like plain English narration.
3. **No Developer Jargon**: Avoids being "Python with English words" by replacing technical keywords (like `def`, `class`, `return`) with narrative concepts (like `creature`, `action`, `play scene`).
4. **Reinforces World-building**: Code reads like a fantasy story or simulation setup.

---

## ⚔️ Syntax Comparison

Here is how ForWhile maps common programming paradigms to storytelling:

| Programming Concept | Traditional Language (e.g., Python) | ForWhile Narrative Syntax |
| :--- | :--- | :--- |
| **Class / Blueprint** | `class Dragon:` | `creature Dragon` |
| **Instantiation** | `Ember = Dragon("Ember")` | `bring Ember to life as Dragon with ("Ember")` |
| **State Mutation** | `Ember.health = 100` | `give Ember the trait health to 100` |
| **Composition (Mixin)** | `attach Fire to Ember` | `attach Fire to Ember` |
| **Method / Action** | `def breathe(self):` | `action breathe` |
| **Method Call** | `Ember.breathe()` | `Ember does breathe` |
| **Constructor** | `def __init__(self):` | `when born` |
| **Conditional Block** | `if condition: ... else:` | `when condition: ... otherwise:` |
| **Objects Graph / Edge** | `alice.friend = bob` | `alice knows bob as friend` |
| **Plural References** | `[x for x in env if type(x) == Dragon]` | `the world's Dragon creatures` |
| **Event Callback** | `observer.on('die', callback)` | `whenever anyone dies` |
| **Time-Step Loop** | `for _ in range(10):` | `the world ticks 10 times` |
| **Functions / Calls** | `def greet(n):` / `greet("Bob")` | `scene greet with (n)` / `play scene greet with ("Bob")` |
| **Getter / Computed** | `@property \n def power(self):` | `power is health times 2` |

---

## 🛠️ Installation

ForWhile requires **Python 3.8+**. Install it from your local package folder:

```bash
# Clone the repository
git clone https://github.com/ghanashyam03/ForWhile.git
cd ForWhile

# Install the package in editable development mode
pip install -e .
```

---

## 🚀 Usage & CLI Commands

Once installed, the `forwhile` command is available directly in your terminal. It supports four subcommands:

### 1. Start the REPL (`forwhile start`)
Launch the interactive storytelling environment. 
```bash
forwhile start
```
Type `help` inside the REPL to see a visual cheat sheet of commands.

### 2. Run a Story File (`forwhile run <file.fw>`)
Bring a `.fw` story script to life and see the narration.
```bash
forwhile run examples/11_story_structure.fw
```

### 3. Check a Story File (`forwhile check <file.fw>`)
Verify a story file for syntax errors or invalid vocabulary without running it.
```bash
forwhile check examples/13_trait_kinds.fw
```

### 4. Version Check (`forwhile --version`)
Print the current version of the ForWhile engine.
```bash
forwhile --version
```

---

## 🏠 Project Structure

```text
ForWhile/
├── forwhile/              # Core Source Code
│   ├── errors.py          # Custom child-friendly errors
│   ├── interpreter.py     # Main AST evaluation, CLI, and REPL
│   ├── lexer.py           # PLY Lexer (tokenization)
│   └── parser.py          # PLY Parser (Abstract Syntax Tree builder)
├── tests/                 # Comprehensive Test Suites
│   ├── test_basic.py
│   ├── test_cli.py
│   ├── test_coverage_boost.py
│   ├── test_examples.py
│   └── ...
├── examples/              # Sample Story Scripts
│   ├── 01_hello.fw
│   ├── 11_story_structure.fw
│   └── 15_ecosystem.fw    # Fox/Rabbit/Grass ecosystem simulation
├── docs/                  # Documentation
│   ├── LANGUAGE_SPEC.md
│   └── EDUCATORS_GUIDE.md
├── editors/vscode/        # VS Code Extension Support
│   ├── package.json       # Extension configuration
│   └── syntaxes/          # Syntax highlighting definition
├── setup.py               # legacy setuptools installation
├── pyproject.toml         # Modern package manifest
└── LICENSE                # MIT License
```

---

## 🧪 Development & Testing

We maintain a strict code coverage requirement of $\ge 90\%$ on `forwhile/interpreter.py`.

Install test dependencies and run the tests:
```bash
pip install pytest pytest-cov
python -m pytest --cov=forwhile --cov-report=term-missing
```
