import sys
from forwhile.lexer import lexer
from forwhile.parser import parser

def main():
    if len(sys.argv) < 2:
        print("Usage: forwhile <filename.fw>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
        
    print(f"Parsing {filename}...")
    result = parser.parse(code)
    if result is not None:
        print("AST parsed successfully:")
        print(result)
    else:
        print("Parsing failed.")

if __name__ == "__main__":
    main()
