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

---

## 5. Complete EBNF Grammar (with CS Annotations)

Below is the complete EBNF specification of the ForWhile grammar, mapping syntax rules to corresponding computer science structures.

```ebnf
(* Program Structure *)
program             ::= opt_newlines statements | opt_newlines
statements          ::= statements statement_with_newline | statement_with_newline
statement_with_newline ::= statement (NEWLINE | ";")

(* Statements (Procedures / Control Flow) *)
statement           ::= create_statement
                      | set_statement
                      | attach_statement
                      | repeat_statement
                      | repeat_through_statement
                      | conditional_statement
                      | call_statement
                      | knows_statement
                      | forgets_statement
                      | whenever_statement
                      | remove_statement
                      | announce_statement
                      | world_set_statement
                      | world_forget_statement
                      | save_statement
                      | restore_statement
                      | scene_statement
                      | play_scene_statement
                      | tick_loop_statement
                      | ask_statement
                      | creature_definition
                      | world_strictness

(* Object Instantiation (Constructors) *)
create_statement    ::= "create" IDENTIFIER IDENTIFIER ["with" expression]
                      | "bring" IDENTIFIER "to" "life" "as" IDENTIFIER ["with" expression]

(* Variable Assignment *)
set_statement       ::= "set" attribute_path "to" expression
                      | "give" attribute_path IDENTIFIER "trait" IDENTIFIER "to" expression
                      | "give" attribute_path "trait" IDENTIFIER "to" expression
                      | "give" attribute_path "to" expression

(* Component Composition (Mixins) *)
attach_statement    ::= "attach" expression "to" expression

(* Fixed-Iteration Loops *)
repeat_statement    ::= "repeat" expression "times" opt_separator statements opt_separator "end" "repeat"

(* For-Each Collection Iteration *)
repeat_through_statement ::= "repeat" "through" expression "as" attribute_path opt_separator statements opt_separator "end" "repeat"

(* Branching Logic (Conditionals) *)
conditional_statement ::= "when" condition opt_separator statements opt_separator ["otherwise" opt_separator statements opt_separator] "end" "when"

(* Method Invocations *)
call_statement      ::= "call" attribute_path
                      | expression "does" IDENTIFIER

(* Object Reference Mapping *)
knows_statement     ::= expression "knows" expression ["as" IDENTIFIER]
forgets_statement   ::= expression "forgets" IDENTIFIER

(* Reactive Event Listeners (Observer Pattern) *)
whenever_statement  ::= "whenever" subject "does" IDENTIFIER opt_separator statements opt_separator "end" "whenever"
                      | "whenever" subject "gets" "trait" IDENTIFIER "changed" opt_separator statements opt_separator "end" "whenever"
                      | "whenever" subject IDENTIFIER "born" opt_separator statements opt_separator "end" "whenever"
                      | "whenever" subject IDENTIFIER opt_separator statements opt_separator "end" "whenever"

subject             ::= IDENTIFIER | "anyone"

(* Memory Management (Deallocation / Garbage Collection) *)
remove_statement    ::= "remove" IDENTIFIER "from" "world"

(* Input / Output *)
announce_statement  ::= "announce" expression
ask_statement       ::= "ask" expression

(* Global Memory *)
world_set_statement ::= "the" "world" "remembers" IDENTIFIER "as" expression
world_forget_statement ::= "the" "world" "forgets" IDENTIFIER

(* Persistence / Serialization *)
save_statement      ::= "save" "the" "world" "to" expression
restore_statement   ::= "restore" "the" "world" "from" expression

(* Modular Procedures (Function Definitions & Calls) *)
scene_statement     ::= "scene" scene_name ["with" params_list] opt_separator statements opt_separator "end" "scene"
play_scene_statement ::= "play" "scene" scene_name ["with" arguments_list]
scene_name          ::= IDENTIFIER | scene_name IDENTIFIER
params_list         ::= "(" (IDENTIFIER)* ")"
arguments_list      ::= "(" (expression)* ")"

(* Simulation Main Loop *)
tick_loop_statement ::= "the" "world" "ticks" expression "times" opt_separator statements opt_separator "end" "ticks"
                      | "on" "each" "tick" opt_separator statements opt_separator "end" "tick"

(* Blueprints (Class Definitions) *)
creature_definition ::= "creature" IDENTIFIER ["from" IDENTIFIER] opt_separator
                          [traits_block]
                          [constructor_block]
                          (action_block)*
                        "end" "creature"

traits_block        ::= "traits" opt_separator (trait_definition)* opt_separator "end" "traits"
trait_definition    ::= IDENTIFIER trait_kind opt_separator
trait_kind          ::= "is" "a" "word"
                      | "is" "a" "number"
                      | "is" "a" "number" "between" expression "and" expression
                      | "is" "one" "of" expression
                      | "is" "true" "or" "false"
                      | "is" "a" "list"
                      | "is" expression

constructor_block   ::= "when" "born" ["with" params_list] opt_separator statements opt_separator "end" "born"
action_block        ::= "action" IDENTIFIER opt_separator statements opt_separator "end" "action"

(* Expressions & Literals *)
expression          ::= STRING
                      | NUMBER
                      | attribute_path
                      | expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | "(" expression_list ")"
                      | "(" ")"
                      | "yes"
                      | "no"
                      | world_expr

world_expr          ::= "the" "world" "knows" IDENTIFIER
                      | "the" "world's" IDENTIFIER "creatures"
                      | "the" "world" "counts" IDENTIFIER

attribute_path      ::= IDENTIFIER | attribute_path IDENTIFIER
```

---

## 6. What We Left Out and Why (Design Rationale)

To make ForWhile a highly effective educational tool, we deliberately excluded several traditional programming constructs. Below is the rationale for these omissions:

### 1. Traditional Loop Syntax (`while` / `for`)
* **Why we left it out**: Raw loops often lead to infinite execution crashes or off-by-one index arithmetic errors which frustrate children.
* **What we did instead**: We replaced them with `repeat N times` (bounded loops) and `repeat through collection` (for-each pattern). This prevents infinite loops and hides array index bounds entirely.

### 2. Traditional Boolean operators (`&&`, `||`, `!`)
* **Why we left it out**: Symbolic operators like `&&` or `!` are syntax barriers that lack immediate semantic meaning for children.
* **What we did instead**: Branching checks are driven by direct narrative assertions (e.g. `when draggy alive is yes` or `when alice knows bob`). Logical operators are avoided by using clean nested condition scopes, which align with how stories are naturally told.

### 3. Explicit `return` Statements
* **Why we left it out**: The concept of returning values from functions breaks the "story flow" metaphor and forces children to think about stack frames and expressions rather than narrative sequence.
* **What we did instead**: Scenes modify the global world memory or creature traits directly. Computed traits (`power is health times 2`) acts as lazy-evaluated getters, allowing derivation of traits without writing return routines.

### 4. Raw Type Syntax (`int`, `str`, `double`, `boolean`)
* **Why we left it out**: Kids think in attributes and adjectives (e.g. "a name is a word"), not computer representation types.
* **What we did instead**: Trait kinds define semantic categories: `is a word` (string), `is a number`, `is true or false` (boolean). This bridges natural descriptions to data validations seamlessly.
