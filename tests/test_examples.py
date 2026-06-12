import pytest
import os
import glob
from forwhile.parser import parser
from forwhile.interpreter import Interpreter
from forwhile.errors import ForWhileRuntimeError

# Get path to examples directory
examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples'))
example_files = glob.glob(os.path.join(examples_dir, '*.fw'))

@pytest.mark.parametrize("filepath", example_files)
def test_example_file(filepath, capsys):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # We parse the file
    ast = parser.parse(code)
    assert ast is not None, f"Failed to parse {os.path.basename(filepath)}"
    
    # Run the interpreter on the AST
    interpreter = Interpreter()
    
    if "13_trait_kinds" in filepath:
        with pytest.raises(ForWhileRuntimeError) as excinfo:
            interpreter.run(ast)
        assert "isn't one of MythicalBeast's allowed colors" in str(excinfo.value)
    else:
        interpreter.run(ast)
    
    # Check that execution succeeded (it would raise an exception otherwise)
