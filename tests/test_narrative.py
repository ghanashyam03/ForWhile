import pytest
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.interpreter import Interpreter, ForWhileRuntimeError

def test_scene_basic(capsys):
    code = """
    scene wake up
      announce "The sun rises."
    end scene

    play scene wake up
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[World] The sun rises."

def test_scene_parameters(capsys):
    code = """
    scene greet with (name greeting)
      announce name + " says: " + greeting
    end scene

    play scene greet with ("Arthur" "Good day!")
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[World] Arthur says: Good day!"

def test_scene_parameter_isolation(capsys):
    code = """
    give name the trait val to "Alice"
    
    scene greet with (name)
      announce "Greeting " + name
    end scene

    play scene greet with ("Bob")
    announce name val
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert lines == ["[World] Greeting Bob", "[World] Alice"]

def test_scene_recursion_guard():
    code = """
    scene recursive
      play scene recursive
    end scene

    play scene recursive
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "scene depth > 20" in str(excinfo.value)

def test_tick_loop_and_on_tick(capsys):
    code = """
    the world remembers count as 0

    on each tick
      the world remembers count as the world knows count + 1
    end tick

    the world ticks 5 times
      announce "Ticking..."
    end ticks

    announce the world knows count
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    
    # 5 "Ticking..." outputs, and then the final count (5)
    assert lines.count("[World] Ticking...") == 5
    assert lines[-1] == "[World] 5"

def test_character_says_syntaxes(capsys):
    code = """
    Alice says "Good morning!"
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Alice] Good morning!"

def test_say_voice_enforcement():
    code = """
    say "Hello"
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(ast)
    assert "speak as the narrator instead" in str(excinfo.value)
