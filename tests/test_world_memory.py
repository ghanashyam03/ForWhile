import pytest
import os
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.interpreter import Interpreter, ForWhileRuntimeError

def test_world_basic_memory(capsys):
    code = """
    the world remembers dragon count as 5
    announce the world knows dragon count
    the world remembers dragon count as the world knows dragon count + 2
    announce the world knows dragon count
    the world forgets dragon count
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert lines == ["[World] 5", "[World] 7"]

    # Trying to read a forgotten/non-existent fact should error
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.run(parser.parse("announce the world knows dragon count"))
    assert "doesn't remember a fact named" in str(excinfo.value)

def test_world_condition(capsys):
    code = """
    the world remembers gold as 10
    when the world knows gold > 5
      announce "Wealthy"
    end when
    when the world knows gold < 5
      announce "Poor"
    end when
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[World] Wealthy"

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

    announce "Dragons total: " + the world counts Dragon
    announce "FireDragons total: " + the world counts FireDragon

    repeat through the world's Dragon creatures as d
      announce d name
    end repeat

    remove Ember from world
    announce "Dragons after remove: " + the world counts Dragon
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] Dragons total: 2" in lines
    assert "[World] FireDragons total: 1" in lines
    assert "[World] Ember" in lines
    assert "[World] Ash" in lines
    assert "[World] Dragons after remove: 1" in lines

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
        say "Health is now: " + health
        say "Gold is: " + gold
      end action
    end creature

    bring Ember to life as Dragon
    Ember does take damage
    announce "Global gold val: " + gold val
    announce "World fact gold: " + the world knows gold
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "Health is now: 100" in lines  # Since no damage was actually taken in this test, but action ran
    assert "Gold is: 50" in lines  # Resolves to self's trait 'gold' first
    assert "[World] Global gold val: 500" in lines # Resolves to global env 'gold val'
    assert "[World] World fact gold: 100" in lines  # Resolves to world memory fact 'gold'

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
    announce the world knows year
    announce Ember name
    announce Ember friend name
    """
    ast2 = parser.parse(restore_code)
    interpreter2 = Interpreter()
    interpreter2.run(ast2)
    
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] 5" in lines
    assert "[World] Ember" in lines
    assert "[World] Ash" in lines
    
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
