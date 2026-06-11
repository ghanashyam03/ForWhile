# ForWhile Language Specification: The Story Model

ForWhile introduces a **Narrative Structure** model that maps traditional programming constructs (like functions, loops, and scope boundaries) to intuitive storytelling abstractions (scenes, passage of time, and dramatic voice boundaries).

---

## 1. Scenes: Abstraction as Story Beats

In standard programming, functions/procedures are used to group statements. In ForWhile, functions are replaced by **Scenes**.

### Syntax
```fw
scene the forest awakens
  announce "Dawn breaks over the forest."
  Owl does hoot
end scene

play scene the forest awakens
```

### Philosophy & Teaching Outcomes
- **Teaches Procedures & Calls**: Defining a scene maps to writing a procedure. Playing a scene represents calling it.
- **Teaches the Call Stack**: Scenes can be nested (a scene playing another scene). This introduces the concept of a call stack. ForWhile enforces a story depth limit of 20 levels, raising: `"The story is getting too complicated! (scene depth > 20)"` to guard against infinite recursion.
- **Dynamic Variable Binding**: When scenes are defined with parameters (e.g. `scene greet with (name)`), argument values are bound to names dynamically in the global environment and restored when the scene exits, preserving variable isolation without requiring child users to learn local vs. lexical variable scoping blocks.

---

## 2. Time Ticks: The Simulation Heartbeat

Instead of relying on arbitrary `while` or `for` loops to advance a simulation's state, ForWhile frames time-progression around a simulation heartbeat.

### Syntax
```fw
on each tick
  the world remembers year as the world knows year + 1
end tick

the world ticks 10 times
  # actions executed on each tick
end ticks
```

### Philosophy & Teaching Outcomes
- **Teaches the Game Loop Pattern**: Decouples one-time setups from cyclical/per-frame updates.
- **Decouples Time from Loop Syntax**: A child understands that a world has a heartbeat ("clock ticks"). In each tick, the world's internal clock advances by 1, the code block executes, and any registered tick rules (event hooks) execute. This is an intuitive framing of delta-time updates and tick-based game loops.

---

## 3. Voice Distinction: Narrator vs. Character Scope

ForWhile draws a strict semantic boundary between the narrator (the programmer/simulation environment) and the characters (creatures inside the simulation).

### Syntax
- `announce <expr>`: Narration by the world. Valid anywhere. Prints with a `[World] ` prefix.
- `say <expr>`: Character dialogue. Valid **only** inside creature actions/constructors. Prints with no prefix (for backward compatibility).
- `<CharacterName> says <expr>`: Direct character speech shorthand. Evaluates `<expr>` and prints as `[{CharacterName}] <value>`.

### Philosophy & Teaching Outcomes
- **Enforces Block Context**: Attempting to use a raw `say` outside a creature's action/constructor block raises a compiler/runtime exception. This teaches children that a character cannot speak unless they have been given context (an action method block).
- **Teaches Method Calls with Arguments**: `<CharacterName> says <expr>` acts as a natural, story-driven shorthand for calling a speech method on a specific creature instance, mapping directly to method invocations.

---

## 4. Trait Kinds: Secret Type Systems & Invariants

To teach data types, validation, and invariants without intimidating children with compiler terminology, ForWhile introduces **Trait Kinds** and **Bounds**. Creatures have defined traits that must conform to specific rules.

### Syntax
```fw
creature Dragon
  traits
    name is a word
    health is a number between 0 and 100
    color is one of ("red" "blue" "green" "black")
    alive is true or false
    treasures is a list
    power is health times 2            # Computed trait
  end traits
end creature
```

### Supported Trait Kinds & Pedagogical Mapping

| Trait Kind | Syntax | Friendly Error Message (Strict Mode) | Secretly Taught Concept |
| :--- | :--- | :--- | :--- |
| **Word** | `is a word` | `Dragons can't have a name of 123 — it must be a word.` | String type validation |
| **Number** | `is a number` | `Dragons can't have a health of "strong" — it must be a number.` | Numeric type validation |
| **Number Range** | `is a number between X and Y` | `Dragons can't have a health of 150 — it must be between 0 and 100.` | Value constraint, range boundaries |
| **Enum** | `is one of (...)` | `The color 'purple' isn't one of Dragon's allowed colors.` | Enumeration type, domain validation |
| **Boolean** | `is true or false` | `Dragons can't have a alive of "maybe" — it must be yes or no.` | Boolean algebra, binary state |
| **List** | `is a list` | `Dragons can't have a treasures of "gold" — it must be a list.` | Collection type, arrays |
| **Computed Trait** | `is [expression]` | *(N/A - dynamically recomputed on read)* | Getters, derived state, lazy evaluation |

### World Strictness Modes
ForWhile lets teachers control how strictly the world enforces these invariants, reflecting development vs. production environments:
- `the world is strict`: (Default) Trait violations halt the simulation immediately with a friendly runtime error.
- `the world is lenient`: Trait violations emit a gentle `[Warning] ...` to the console. Range violations are silently clamped (e.g., a health of `150` clamps to `100`), teaching defensive programming and fallback strategies.
