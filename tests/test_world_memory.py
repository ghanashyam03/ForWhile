import pytest
import os
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.interpreter import Interpreter, ForWhileRuntimeError

def test_world_basic_memory(capsys):
    code = """
    the world remembers dragon count as 5
    say the world knows dragon count
    the world remembers dragon count as the world knows dragon count + 2
    say the world knows dragon count
    the world forgets dragon count
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert lines == ["5", "7"]

    # Trying to read a forgotten/non-existent fact should error
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(parser.parse("say the world knows dragon count"))
    assert "World memory does not contain fact" in str(excinfo.value)

def test_world_condition(capsys):
    code = """
    the world remembers gold as 10
    when the world knows gold > 5
      say "Wealthy"
    end when
    when the world knows gold < 5
      say "Poor"
    end when
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Wealthy"

def test_world_roster_and_counts(capsys):
    code = """
    creature Dragon
      when born with (name)
        give self the trait name to name
      end born
    end creature

    creature FireDragon from Dragon
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring Ember to life as Dragon with ("Ember")
    bring Ash to life as FireDragon with ("Ash")

    say "Dragons total: " + the world counts Dragon
    say "FireDragons total: " + the world counts FireDragon

    repeat through the world's Dragon creatures as d
      say d name
    end repeat

    remove Ember from world
    say "Dragons after remove: " + the world counts Dragon
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "Dragons total: 2" in lines
    assert "FireDragons total: 1" in lines
    assert "Ember" in lines
    assert "Ash" in lines
    assert "Dragons after remove: 1" in lines

def test_scoping_rules(capsys):
    code = """
    the world remembers gold as 100
    give gold the trait val to 500 # global variable/creature named gold
    
    creature Dragon
      when born
        give self the trait health to 100
        give self the trait gold to 50
      end born

      action take damage
        give self the trait health to health - 10
        say "Health is now: " + health
        say "Gold is: " + gold
      end action
    end creature

    bring Ember to life as Dragon
    Ember does take damage
    say "Global gold val: " + gold val
    say "World fact gold: " + the world knows gold
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "Health is now: 90" in lines
    assert "Gold is: 50" in lines  # Resolves to self's trait 'gold' first
    assert "Global gold val: 500" in lines # Resolves to global env 'gold val'
    assert "World fact gold: 100" in lines  # Resolves to world memory fact 'gold'

def test_save_and_restore(capsys):
    code = """
    creature Dragon
      when born with (name)
        give self the trait name to name
      end born
    end creature

    bring Ember to life as Dragon with ("Ember")
    bring Ash to life as Dragon with ("Ash")
    Ember knows Ash as friend
    
    the world remembers year as 5
    save the world to "test_world.json"
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    
    assert os.path.exists("test_world.json")
    
    # Now restore in a fresh interpreter
    restore_code = """
    creature Dragon
      when born with (name)
        give self the trait name to name
      end born
    end creature

    restore the world from "test_world.json"
    say the world knows year
    say Ember name
    say Ember friend name
    """
    ast2 = parser.parse(restore_code)
    interpreter2 = Interpreter()
    interpreter2.run(ast2)
    
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "5" in lines
    assert "Ember" in lines
    assert "Ash" in lines
    
    # Cleanup temp file
    if os.path.exists("test_world.json"):
        os.remove("test_world.json")

def test_save_world_warnings(capsys):
    interpreter = Interpreter()
    # Bring creature to life manually
    interpreter.env['Ember'] = {
        '__class__': 'Dragon',
        '__name__': 'Ember',
        '__knows__': {},
        'health': 100,
        'unsavable': lambda x: x  # Non-serializable
    }
    interpreter.save_world("test_warning.json")
    captured = capsys.readouterr()
    assert "Warning: could not save Ember's unsavable" in captured.out
    
    # Cleanup temp file
    if os.path.exists("test_warning.json"):
        os.remove("test_warning.json")
