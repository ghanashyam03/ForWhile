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

def test_relationships_and_navigation(capsys):
    code = """
    creature Person
      when born with (name)
        give self the trait name to name
      end born
      action greet
        say self name + " says hello!"
      end action
    end creature

    bring Alice to life as Person with ("Alice")
    bring Bob to life as Person with ("Bob")

    Alice knows Bob as friend
    say Alice friend name
    Alice friend does greet
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0].strip() == "Bob"
    assert lines[1].strip() == "Bob says hello!"

def test_relationship_groups_and_iteration(capsys):
    code = """
    creature Person
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring Alice to life as Person with ("Alice")
    bring Bob to life as Person with ("Bob")
    bring Carol to life as Person with ("Carol")

    Alice knows Bob as friend
    Alice knows Carol as friend

    repeat through Alice friends as each friend
      say each friend name
    end repeat
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [line.strip() for line in captured.out.strip().split("\n") if line.strip()]
    assert "Bob" in lines
    assert "Carol" in lines
    assert len(lines) == 2

def test_relationship_conditions_and_forget(capsys):
    code = """
    creature Person
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring Alice to life as Person with ("Alice")
    bring Bob to life as Person with ("Bob")

    when Alice knows Bob
      say "Unexpected"
    otherwise
      say "Disconnected"
    end when

    Alice knows Bob as friend
    when Alice knows Bob as friend
      say "Connected"
    end when

    when Alice knows anyone as friend
      say "Has friend"
    end when

    Alice forgets friend
    when Alice knows anyone as friend
      say "Has friend still"
    otherwise
      say "Lonely"
    end when
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [line.strip() for line in captured.out.strip().split("\n") if line.strip()]
    assert lines[0] == "Disconnected"
    assert lines[1] == "Connected"
    assert lines[2] == "Has friend"
    assert lines[3] == "Lonely"

def test_trait_change_reaction(capsys):
    code = """
    creature Fire
      when born
        give self the trait brightness to 50
      end born
    end creature

    bring my_fire to life as Fire

    whenever my_fire gets trait brightness changed
      say "Brightness is now " + my_fire brightness
    end whenever

    give my_fire the trait brightness to 80
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "Brightness is now 80" in lines

def test_death_event_and_context(capsys):
    code = """
    creature Villager
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring bob to life as Villager with ("Bob")

    whenever anyone dies
      announce the one who died name + " has left us."
    end whenever

    remove bob from world
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] Bob has left us." in lines

def test_infinite_loop_prevention():
    code = """
    creature Villager
      when born
        give self the trait value to 0
      end born
    end creature

    bring bob to life as Villager

    whenever bob gets trait value changed
      give bob the trait value to bob value + 1
    end whenever

    give bob the trait value to 1
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(Exception) as excinfo:
        interpreter.run(ast)
    assert "The world is stuck in a loop!" in str(excinfo.value)
