import pytest
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.interpreter import Interpreter

def test_set_and_say(capsys):
    code = """
    give my the trait name to "Alice"
    say my name
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Alice"

def test_arithmetic(capsys):
    code = """
    give num the trait value1 to 10
    give num the trait value2 to 5
    give num the trait sum to num value1 + num value2
    say num sum

    give str the trait value1 to "Hello "
    give str the trait value2 to "World"
    give str the trait greeting to str value1 + str value2
    say str greeting
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0].strip() == "15"
    assert lines[1].strip() == "Hello World"

def test_repeat_loop(capsys):
    code = """
    give my the trait count to 0
    repeat 3 times
      give my the trait count to my count + 1
    end repeat
    say my count
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "3"

def test_until_loop(capsys):
    code = """
    give my the trait count to 0
    until my count == 3
      give my the trait count to my count + 1
    end until
    say my count
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "3"

def test_when_otherwise(capsys):
    code = """
    give test the trait value to 10
    when test value > 5
      give test the trait result to "Greater"
    otherwise
      give test the trait result to "Lesser"
    end when
    say test result

    give test the trait value to 3
    when test value > 5
      give test the trait result2 to "Greater"
    otherwise
      give test the trait result2 to "Lesser"
    end when
    say test result2
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0].strip() == "Greater"
    assert lines[1].strip() == "Lesser"

def test_creature_action_and_self(capsys):
    code = """
    creature Dragon
      when born with (name color)
        give self the trait name to name
        give self the trait color to color
        give self the trait health to 100
      end born

      action breathe fire
        say self name + " breathes " + self color + " fire!"
        give self the trait health to self health - 10
      end action
    end creature

    bring Ember to life as Dragon with ("Ember" "red")
    Ember does breathe fire
    say Ember health
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0].strip() == "Ember breathes red fire!"
    assert lines[1].strip() == "90"

def test_deprecated_compatibility(capsys):
    code = """
    class Character
      create with (given_name)
        set self name to given_name
      end create
      method describe
        say self name
      end method
    end class

    create Character bob with "Bob"
    call bob describe
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Bob"
