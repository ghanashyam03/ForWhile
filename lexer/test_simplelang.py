from simplelang_lexer import lexer
from simplelang_parser import parser

# Test input
data = '''
# Define a class for character
class Character 
  # Constructor to set initial name
  create with (given name)
    set name to given name
    set age to 0  # Default age for every character
  end create

  # Method to describe character
  method describe
    say "I am " + name + " and I am " + age + " years old."
  end method
end class

# Define a Head class that inherits from Character
class Head from Character
  create with (shape color)
    set head shape to shape
    set head color to color
  end create
end class

# Define an Arm class that inherits from Character
class Arm from Character
  create with (length position)
    set arm length to length
    set arm position to position
  end create
end class

# Create and customize a character
create Character Alice with "Alice"

# Attach parts to Alice
create Head AliceHead with "round" "red"
attach Head to Alice

create Arm AliceArm with "long" "left"
attach Arm to Alice

# Set and update variables
create Character Bob with "Bob"
set Bob age to 10
set Bob favorite color to "blue"

# Loop: Bob grows older each time
repeat 5 times
  set Bob age to Bob age + 1
end repeat

# Conditional logic
if Bob age > 5
  set Bob favorite color to "red"
else
  set Bob favorite color to "green"
end if

# Input and output
ask "What is your favorite color?"
set Bob favorite color to (input)
say "Bob's favorite color is " + Bob favorite color

# Bob introduces himself
call Bob describe
'''

# Tokenize
print("Tokens:")
lexer.input(data)
for token in lexer:
    print(token)

# Parse
print("\nParse Tree:")
result = parser.parse(data, debug=True)  # Enable debug mode

def print_tree(node, indent=""):
    if isinstance(node, tuple):
        print(indent + node[0])
        for item in node[1:]:
            print_tree(item, indent + "  ")
    elif isinstance(node, list):
        for item in node:
            print_tree(item, indent)
    else:
        print(indent + str(node))

if result:
    print_tree(result)
else:
    print("Parsing failed")