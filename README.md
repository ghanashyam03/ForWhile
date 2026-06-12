# ForWhile

A world-building programming language designed to teach Object-Oriented Programming (OOP) and core simulation concepts to young storytellers through a plain-English, narrative-driven syntax.

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


---

## 📖 Comprehensive Documentation

For every single detail about the language, please refer to our dedicated documentation files:

* **Language Specification**: [docs/LANGUAGE_SPEC.md](docs/LANGUAGE_SPEC.md) — The ultimate reference for grammar, design decisions, complete syntax rules, and language capabilities.
* **Educator's Guide**: [docs/EDUCATORS_GUIDE.md](docs/EDUCATORS_GUIDE.md) — CS concept mapping, teaching strategies, and 10 ready-to-use classroom exercises.

---

## 🛠️ Installation & Setup

ForWhile is now available on PyPI! It requires **Python 3.8+**.

### 🪟 Windows

1. Open **Command Prompt** or **PowerShell**.
2. Install ForWhile via pip:
   ```cmd
   pip install forwhile
   ```
3. Verify the installation:
   ```cmd
   forwhile --version
   ```
*(Note: If `forwhile` is not recognized, ensure your Python Scripts folder is added to your system's PATH.)*

### 🍎 macOS

1. Open **Terminal**.
2. Install ForWhile via pip3:
   ```bash
   pip3 install forwhile
   ```
3. Verify the installation:
   ```bash
   python3 -m forwhile --version
   ```
*(Note: If installed in `~/.local/bin` or `Library/Python/.../bin`, you can run it via `python3 -m forwhile` or add the directory to your PATH.)*

### 🐧 Ubuntu / Linux

1. Open your **Terminal**.
2. Install ForWhile using pip3:
   ```bash
   pip3 install forwhile
   ```
3. Verify the installation:
   ```bash
   forwhile --version
   # or
   python3 -m forwhile --version
   ```

### 💻 VS Code Extension

For the best coding experience, we provide a **Visual Studio Code extension** with full syntax highlighting for `.fw` files!

**How to Install:**
1. Open VS Code.
2. Go to the **Extensions** view (`Ctrl+Shift+X` or `Cmd+Shift+X`).
3. Search for **ForWhile** in the Marketplace.
4. Click **Install**.


---

## 🚀 Usage & CLI Commands

Once installed, the `forwhile` command (or `python -m forwhile`) is available in your terminal. It supports four subcommands:

### 1. Start the REPL (`forwhile start`)
Launch the interactive storytelling environment. 
```bash
forwhile start
```
Type `help` inside the REPL to see a visual cheat sheet of commands.

### 2. Run a Story File (`forwhile run <file.fw>`)
Bring a `.fw` story script to life and see the narration. Check out the 35+ examples in the `/examples` folder!
```bash
forwhile run examples/15_ecosystem.fw
```

### 3. Check a Story File (`forwhile check <file.fw>`)
Verify a story file for syntax errors or invalid vocabulary without running it.
```bash
forwhile check examples/01_hello.fw
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
├── forwhile/              # Core Source Code (interpreter, lexer, parser)
├── tests/                 # Comprehensive Test Suites
├── examples/              # Over 35 Sample Story Scripts (.fw files)
├── docs/                  # Documentation (Spec and Educator's Guide)
├── editors/vscode/        # VS Code Extension Source
├── pyproject.toml         # Modern package manifest
└── LICENSE                # MIT License
```

---
