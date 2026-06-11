import pytest
from forwhile.parser import parser
from forwhile.interpreter import Interpreter
from forwhile.errors import ForWhileRuntimeError

def test_trait_kinds_word(capsys):
    # Word validation (strict mode)
    code_strict = """
    creature Dragon
      traits
        name is a word
      end traits
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring d to life as Dragon with (123)
    """
    ast = parser.parse(code_strict)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "it must be a word" in str(excinfo.value)

    # Word validation (lenient mode)
    code_lenient = """
    the world is lenient
    creature Dragon
      traits
        name is a word
      end traits
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring d to life as Dragon with (123)
    announce d name
    """
    ast = parser.parse(code_lenient)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[Warning]" in captured.out
    assert "123" in captured.out

def test_trait_kinds_number(capsys):
    # Number validation (strict mode)
    code_strict = """
    creature Dragon
      traits
        age is a number
      end traits
      when born with (age)
        give self the trait age to age
      end born
    end creature

    bring d to life as Dragon with ("old")
    """
    ast = parser.parse(code_strict)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "it must be a number" in str(excinfo.value)

def test_trait_kinds_number_range(capsys):
    # Number range validation (strict mode - out of bounds)
    code_strict = """
    creature Dragon
      traits
        health is a number between 0 and 100
      end traits
      when born with (health)
        give self the trait health to health
      end born
    end creature

    bring d to life as Dragon with (150)
    """
    ast = parser.parse(code_strict)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "it must be between 0 and 100" in str(excinfo.value)

    # Number range validation (lenient mode - clamping)
    code_lenient = """
    the world is lenient
    creature Dragon
      traits
        health is a number between 0 and 100
      end traits
      when born with (health)
        give self the trait health to health
      end born
    end creature

    bring d to life as Dragon with (150)
    announce d health
    """
    ast = parser.parse(code_lenient)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[Warning]" in captured.out
    assert "[World] 100" in captured.out

def test_trait_kinds_enum(capsys):
    # Enum validation (strict mode - invalid choice)
    code_strict = """
    creature Dragon
      traits
        color is one of ("red" "blue" "green")
      end traits
      when born with (color)
        give self the trait color to color
      end born
    end creature

    bring d to life as Dragon with ("purple")
    """
    ast = parser.parse(code_strict)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "isn't one of Dragon's allowed colors" in str(excinfo.value)

    # Enum validation - case insensitivity / normalization
    code_ok = """
    creature Dragon
      traits
        color is one of ("red" "blue" "green")
      end traits
      when born with (color)
        give self the trait color to color
      end born
    end creature

    bring d to life as Dragon with ("RED")
    announce d color
    """
    ast = parser.parse(code_ok)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World] red" in captured.out # Normalized to the list value case

def test_trait_kinds_boolean(capsys):
    # Boolean validation (yes/no aliases)
    code = """
    creature Device
      traits
        online is true or false
      end traits
      when born with (online)
        give self the trait online to online
      end born
      action toggle
        when online is yes
          give self the trait online to no
        otherwise
          give self the trait online to yes
        end when
      end action
    end creature

    bring d to life as Device with (yes)
    announce d online
    d does toggle
    announce d online
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert lines[0] == "[World] True"
    assert lines[1] == "[World] False"

def test_trait_kinds_list(capsys):
    # List validation (strict mode)
    code_strict = """
    creature Inv
      traits
        items is a list
      end traits
      when born with (items)
        give self the trait items to items
      end born
    end creature

    bring i to life as Inv with ("sword")
    """
    ast = parser.parse(code_strict)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "must be a list" in str(excinfo.value)

def test_computed_traits(capsys):
    code = """
    creature Rectangle
      traits
        width is a number
        height is a number
        area is width times height
      end traits
      when born with (width height)
        give self the trait width to width
        give self the trait height to height
      end born
    end creature

    bring r to life as Rectangle with (5 10)
    announce r area
    give r the trait width to 8
    announce r area
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert lines[0] == "[World] 50"
    assert lines[1] == "[World] 80"

def test_trait_shorthand(capsys):
    code = """
    creature Hero
      traits
        health is a number
      end traits
      when born
        give self the trait health to 100
      end born
      action take damage
        give health to health - 20
      end action
    end creature

    bring h to life as Hero
    announce h health
    h does take damage
    announce h health
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert lines[0] == "[World] 100"
    assert lines[1] == "[World] 80"
