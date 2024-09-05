from simplelang_lexer import lexer
from simplelang_parser import parser

# Test input
data = '''
create character Bob
set Bob name to "Bob"
set Bob age to 10
create character Alice
set Alice name to "Alice"
attach Head to Alice
repeat 5 times
  set Bob age to Bob age + 1
end repeat
if Bob age > 5
  set Bob color to 'red'
else
  set Bob color to 'green'
end if
ask "What is your favorite color?" set Bob favorite to (input)
say "Bob's favorite color is " + Bob favorite
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