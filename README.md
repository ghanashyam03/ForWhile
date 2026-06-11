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
| Loops | `until condition:` | `until condition` |
| Conditionals | `if condition: ... else:` | `when condition: ... otherwise:` |
| Relationships | `alice.friend = bob` | `Alice knows Bob as friend` |
| Relationship Queries | `if hasattr(alice, 'friend'):` | `when Alice knows Bob as friend` |
| Collection Iteration | `for friend in alice.friends:` | `repeat through Alice friends as each friend` |
| Event Rule | `observer.on('action', callback)` | `whenever Ember does breathe fire` |
| State Change Reaction | `on_property_change(callback)` | `whenever Ember gets trait health changed` |
| Entity Removal | `del world.entities[bob]` | `remove bob from world` |
| World Announcement | `logging.info("[World] ...")` | `announce "A new day dawns!"` |
| **World Memory (Set)** | `world_mem["dragons"] = 0` | `the world remembers dragons as 0` |
| **World Memory (Get)** | `world_mem["dragons"]` | `the world knows dragons` |
| **World Memory (Forget)**| `del world_mem["dragons"]` | `the world forgets dragons` |
| **World Roster** | `[e for e in env if type(e) == Dragon]` | `the world's Dragon creatures` |
| **World Counters** | `len(roster(Dragon))` | `the world counts Dragon` |
| **World Persistence** | `json.dump(...)` / `json.load(...)` | `save the world to "save.fw"` / `restore the world from "save.fw"` |

## Scoping Rules

Inside a creature's action or `when born` block:
1. **Local Variables & Parameters**: Takes highest precedence. If a variable is in the current execution block (or loop alias, or parameter), it is resolved directly.
2. **Self Traits**: If a bare identifier is not found in the local scope, ForWhile automatically checks if it is a trait on the active creature (`self`). For example, writing `health` resolves directly to `self health`.
3. **Global Environment**: If the name is not in the local scope or `self` traits, ForWhile checks the global environment for other creature instances or global variables.
4. **World Memory Facts**: Must be explicitly requested using `the world knows <fact_name>` to teach that global facts belong to the simulation container, not the local context.

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
│   ├── test_basic.py     (Basic pytest test suite)
│   └── test_world_memory.py (World memory pytest suite)
├── examples/
│   ├── 01_hello.fw       (World-building hello world)
│   ├── 09_world_memory.fw (Kingdom simulation sample)
│   └── 10_roster.fw      (Creature list and counter sample)
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
forwhile examples/09_world_memory.fw
```
