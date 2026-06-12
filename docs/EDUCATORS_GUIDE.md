# ForWhile Educator's Guide: Mapping Narrative to Computer Science

Welcome to the Educator's Guide for **ForWhile**. This guide is designed to help teachers, instructors, and parents translate the story-based metaphors of ForWhile into professional Computer Science and programming paradigms. By using this mapping, children can construct complex systems naturally through creative writing, preparing them for traditional languages like Python, Java, or JavaScript later.

---

## The Secret Computer Science Mapping Table

The table below maps the narrative surfaces of ForWhile to their professional programming counterparts:

| ForWhile Narrative Syntax | Professional Computer Science Term | Pedagogical Description |
| :--- | :--- | :--- |
| `creature <Name>` | **Class / Blueprint** | Defines a new template with properties and actions. |
| `bring <name> to life as <Creature>` | **Object Instantiation / Constructor call** | Creates a live instance of a class in memory. |
| `when born` / `when born with (...)` | **Constructor Method (`__init__` or `constructor`)** | Initializes object state when it is created. |
| `give self the trait <name> to <val>` | **Instance Variable / Attribute Assignment** | Sets a property unique to that specific instance. |
| `the world remembers <fact> as <val>` | **Global Variable** | Sets state in the global runtime environment. |
| `the world knows <fact>` | **Global Variable Lookup** | Reads a value from the global state. |
| `action <name>` / `does <name>` | **Instance Method / Method Call** | Defines behavior on an object and invokes it. |
| `knows <other> as <role>` | **Object Referencing / Directed Graph edge** | Stores a reference to another object in an attribute. |
| `forget <role>` | **Nullifying a reference** | Deletes a reference attribute or resets it to null. |
| `whenever <subject> does <action>` | **Event Listener / Observer Pattern** | Registers a callback that runs reactively on an event. |
| `on each tick` | **Game Loop / Periodic Clock cycle** | Executes a block of code on every iteration of a timer. |
| `the world ticks <N> times` | **For loop (fixed bounds step)** | Runs the main simulation loop for a set number of steps. |
| `scene <name>` / `play scene <name>` | **Procedure / Function Declaration & Call** | Organizes statements into a callable story beat. |
| `traits` block (e.g. `is a number`) | **Type Constraints / Type System** | Validates properties without exposing syntax like `int` or `str`. |
| `the world is strict` / `lenient` | **Strict vs. Lenient Execution Modes** | Toggles between crash-on-error and clamping/warning modes. |

---

## 10 Classroom Exercises

Each exercise includes a **Story Premise**, the **Targeted CS Concepts**, and a **Complete Solution** that can be run directly in the ForWhile interpreter.

---

### Exercise 1: The Sleeping Forest
* **Story Premise**: The forest is quiet at dawn. The narrator must announce three events in order: the sun rising, the birds waking up, and the forest awakening.
* **Targeted CS Concepts**: Sequential execution, output statements (`announce`), comments.
* **Solution**:
```fw
# Step 1: The sun rises
announce "The first light of dawn shines through the trees."

# Step 2: The birds wake up
announce "Birds begin to chirp in the canopy."

# Step 3: The forest awakens
announce "The forest is now fully awake!"
```

---

### Exercise 2: The Magic Wand
* **Story Premise**: A wizard finds a magic wand. The world needs to remember the wand's current spell charge (starts at 3) and spell name ("Fireball"). The charge decreases by 1, and the world announces the status.
* **Targeted CS Concepts**: Variables, state modification, basic math.
* **Solution**:
```fw
# Store the initial facts in the world
the world remembers spell_name as "Fireball"
the world remembers charges as 3

announce "The wand is charged with: " + the world knows spell_name
announce "Charges left: " + the world knows charges

# Use the wand: decrease charges by 1
the world remembers charges as the world knows charges - 1
announce "The wizard casts the spell! Charges remaining: " + the world knows charges
```

---

### Exercise 3: The Dragon's Health
* **Story Premise**: Define a Dragon creature that has a health trait initialized to 100 when born. Create an instance named `ignis`.
* **Targeted CS Concepts**: Classes, instance variables, constructors, instantiation.
* **Solution**:
```fw
creature Dragon
  when born
    give self the trait health to 100
    announce "A mighty dragon is born with " + self health + " health!"
  end born
end creature

# Bring the dragon to life
bring ignis to life as Dragon
```

---

### Exercise 4: The Merchant's Inventory
* **Story Premise**: A merchant is preparing for travel. They start with an empty list of items. Add a "Sword" and a "Shield" to their inventory, then list them.
* **Targeted CS Concepts**: Lists/Collections, list literals, loops (`repeat through`).
* **Solution**:
```fw
creature Merchant
  traits
    inventory is a list
  end traits

  when born
    # Initialize with an empty list
    give self the trait inventory to ()
  end born

  action pack
    # Add items to list
    give inventory to ("Sword" "Shield")
  end action
end creature

bring shopkeeper to life as Merchant
shopkeeper does pack

announce "The merchant's pack contains:"
repeat through shopkeeper inventory as item
  announce "- " + item
end repeat
```

---

### Exercise 5: The Friendly Goblin
* **Story Premise**: A lonely goblin named `gimble` wants to make friends with a villager named `alice`. Establish a friendship relationship between them and have `gimble` check if they know `alice`.
* **Targeted CS Concepts**: Object relations/references, reference checks, conditionals.
* **Solution**:
```fw
creature Goblin
  when born
    announce "Gimble emerges from the cave."
  end born
end creature

creature Villager
  when born
    announce "Alice is gardening in the village."
  end born
end creature

bring gimble to life as Goblin
bring alice to life as Villager

# Establish friendship
gimble knows alice as friend

# Check relationship
when gimble knows alice as friend
  announce "Gimble and Alice are friends!"
otherwise
  announce "Gimble is still lonely."
end when
```

---

### Exercise 6: The Ticking Clock
* **Story Premise**: Create a cyclic day/night cycle. Every time the simulation clock ticks, advance the world's hour by 1. Run the simulation for 3 ticks.
* **Targeted CS Concepts**: Periodic loops, game loop tick cycles, state increments.
* **Solution**:
```fw
the world remembers hour as 8

on each tick
  the world remembers hour as the world knows hour + 1
  announce "The clock ticks. The hour is now " + the world knows hour
end tick

announce "--- Starting Simulation ---"
the world ticks 3 times
  announce "A tick has passed in the world."
end ticks
announce "--- Simulation Complete ---"
```

---

### Exercise 7: The Weather Machine
* **Story Premise**: A machine controls the weather. If the world temperature is above 30, it rains. Otherwise, it is sunny.
* **Targeted CS Concepts**: Branching logic, relational operators (`>`), conditionals (`when/otherwise`).
* **Solution**:
```fw
the world remembers temperature as 35

when the world knows temperature > 30
  announce "The weather machine activates: It is raining heavily!"
otherwise
  announce "The weather machine stays quiet: It is a sunny day."
end when
```

---

### Exercise 8: The Guard at the Gate
* **Story Premise**: A royal guard stands watch. Write a reactive rule: whenever anyone dies, the guard announces a tribute to them.
* **Targeted CS Concepts**: Event-driven programming, callbacks, observer pattern, contextual keywords (`the one who died`).
* **Solution**:
```fw
creature Knight
  traits
    name is a word
  end traits
  when born with (name)
    give self the trait name to name
  end born
end creature

# Set up event observer
whenever anyone dies
  announce "The Guard rings the bell and says: We mourn " + the one who died name + "."
end whenever

# Bring a brave knight to life and remove them
bring arthur to life as Knight with ("Sir Arthur")
remove arthur from world
```

---

### Exercise 9: The Castle Keep
* **Story Premise**: Organize a story beat into a scene called "castle_defense" with parameters `guards` and `invaders`. When played, announce the combat status.
* **Targeted CS Concepts**: Modular procedures, parameter passing, dynamic scoping.
* **Solution**:
```fw
scene castle_defense with (guards invaders)
  announce "The battle begins!"
  announce "We have " + guards + " guards defending against " + invaders + " invaders!"
end scene

# Play the scene with arguments
play scene castle_defense with (10 5)
```

---

### Exercise 10: The Strict Spellbook
* **Story Premise**: A wizard's spell health is a number between 0 and 100. Toggle the world between strict and lenient mode to show how a spell's health gets validated and clamped.
* **Targeted CS Concepts**: Type bounds, validation invariants, strict vs lenient error models.
* **Solution**:
```fw
creature FireSpell
  traits
    intensity is a number between 0 and 100
  end traits
  when born
    # Try setting intensity to an invalid high value
    give self the trait intensity to 150
  end born
end creature

announce "--- 1. Testing in LENIENT mode ---"
the world is lenient
bring spell1 to life as FireSpell
announce "Spell intensity was clamped to: " + spell1 intensity

announce "--- 2. Testing in STRICT mode ---"
the world is strict
# This next line will halt with a friendly story error
bring spell2 to life as FireSpell
```
