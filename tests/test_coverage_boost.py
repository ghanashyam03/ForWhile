import pytest
from unittest.mock import patch
from forwhile.lexer import lexer
from forwhile.parser import parser
from forwhile.interpreter import Interpreter, ForWhileRuntimeError, Scope

def test_scope_parent_lookup():
    parent = Scope()
    parent.set("x", 42)
    child = Scope(parent=parent)
    assert child.exists_local_var("x") is True
    assert child.get_local_var("x") == 42

def test_ask_statement(capsys):
    code = """
    ask "What is your name?"
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "What is your name?" in captured.out

def test_input_expression():
    code = """
    give val to (input)
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    with patch('builtins.input', return_value="Arthur"):
        interpreter.run(ast)
    assert interpreter.env['val'] == "Arthur"

def test_attach_statement(capsys):
    code = """
    creature Leg
      when born
        give self the trait length to 10
      end born
    end creature

    creature Dragon
      when born
        announce "Dragon born"
      end born
    end creature

    bring draggy to life as Dragon
    attach Leg to draggy
    announce draggy Leg length
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World] 10" in captured.out

def test_attach_errors():
    interpreter = Interpreter()
    # Attach to non-creature
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('ATTACH', 'Leg', 'non_creature'))
    assert "is not a creature in this world" in str(excinfo.value)

def test_knows_multiple_role_list():
    code = """
    creature Villager
      when born
        announce "Villager born"
      end born
    end creature
    bring alice to life as Villager
    bring bob to life as Villager
    bring charlie to life as Villager
    bring david to life as Villager
    alice knows bob as friend
    alice knows charlie as friend
    alice knows david as friend
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    
    alice = interpreter.env['alice']
    friends = alice['__knows__']['friend']
    assert isinstance(friends, list)
    assert len(friends) == 3
    assert friends[0]['__name__'] == 'bob'
    assert friends[1]['__name__'] == 'charlie'
    assert friends[2]['__name__'] == 'david'

def test_interpreter_invalid_op_and_expr():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('INVALID_OP',))
    assert "unrecognized instruction" in str(excinfo.value)

    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.evaluate(('INVALID_EXPR_OP',))
    assert "unrecognized formula" in str(excinfo.value)

    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.evaluate_condition(('INVALID_COND_OP',))
    assert "unrecognized test" in str(excinfo.value)

def test_parent_constructor_and_method_inheritance(capsys):
    code = """
    creature Beast
      when born with (n)
        give self the trait name to n
      end born
      
      action roar
        announce "Roar!"
      end action
    end creature

    creature Dragon from Beast
      action fly
        announce "Fly"
      end action
    end creature

    bring draggy to life as Dragon with ("Ignis")
    announce draggy name
    draggy does roar
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World] Ignis" in captured.out
    assert "[World] Roar!" in captured.out

def test_parent_computed_trait_inheritance(capsys):
    code = """
    creature Beast
      traits
        age is a number
        double_age is age + age
      end traits
      when born
        give self the trait age to 50
      end born
    end creature

    creature Dragon from Beast
      action fly
        announce "Fly"
      end action
    end creature

    bring draggy to life as Dragon
    announce draggy double_age
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World] 100" in captured.out

def test_does_action_invalid_targets():
    interpreter = Interpreter()
    # Target not defined
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('DOES_ACTION', 'draggy', 'roar'))
    assert "is not a creature in this world" in str(excinfo.value)

    # Target is not a creature
    interpreter.env['draggy'] = 42
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('DOES_ACTION', 'draggy', 'roar'))
    assert "is not a creature in this world" in str(excinfo.value)

    # Action not found
    interpreter.env['draggy'] = {'__class__': 'Dragon', '__knows__': {}}
    interpreter.classes['Dragon'] = {'methods': {}, 'parent': None}
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('DOES_ACTION', 'draggy', 'roar'))
    assert "doesn't know how to 'roar'" in str(excinfo.value)

def test_knows_statement_invalid_targets():
    interpreter = Interpreter()
    interpreter.env['alice'] = {'__class__': 'Villager', '__knows__': {}}
    
    # Target a is not creature
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('KNOWS', ['bob'], ['alice'], 'friend'))
    assert "is not a creature in this world" in str(excinfo.value)

    # Target b is not creature
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('KNOWS', ['alice'], ['bob'], 'friend'))
    assert "is not a creature in this world" in str(excinfo.value)

def test_forget_statement_invalid_targets():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('FORGETS', ['alice'], 'friend'))
    assert "is not a creature in this world" in str(excinfo.value)

def test_whenever_the_one_who_died(capsys):
    code = """
    creature Mortal
      traits
        name is a word
      end traits
      when born with (name)
        give self the trait name to name
      end born
    end creature

    whenever anyone dies
      announce "The one who died is: " + the one who died name
    end whenever

    bring mortal1 to life as Mortal with ("mortal1")
    remove mortal1 from world
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "The one who died is: mortal1" in captured.out

def test_resolve_path_error():
    interpreter = Interpreter()
    # Trait not found on creature
    interpreter.env['draggy'] = {'__class__': 'Dragon', '__knows__': {}}
    interpreter.classes['Dragon'] = {'traits': {}, 'computed_traits': {}, 'parent': None}
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.resolve_path(['draggy', 'wings'])
    assert "doesn't seem to have a 'wings' trait" in str(excinfo.value)

    # Non-creature attribute access
    interpreter.env['draggy'] = 42
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.resolve_path(['draggy', 'wings'])
    assert "We can't look up 'wings' because the target isn't a creature." in str(excinfo.value)

def test_missing_argument_handling(capsys):
    # Constructor parameter default to None
    code = """
    creature Dragon
      when born with (name color)
        announce name
        announce color
      end born
    end creature
    bring draggy to life as Dragon with ("Ignis")
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] Ignis" in lines
    assert "[World] None" in lines

def test_get_local_var_none():
    assert Scope().get_local_var("nonexistent") is None

def test_interpreter_run_empty():
    interpreter = Interpreter()
    assert interpreter.run([]) is None
    assert interpreter.run(None) is None

def test_execute_non_tuple():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute("not_a_tuple")
    assert "unrecognized instruction" in str(excinfo.value)

def test_save_and_restore_errors():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.restore_world("missing_save_file.json")
    assert "history file" in str(excinfo.value)

def test_evaluate_various_expressions(capsys):
    code = """
    give x to 5 times 4
    give y to 10 - 2
    when x > y
      announce "x is greater"
    end when
    when y < x
      announce "y is less"
    end when
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] x is greater" in lines
    assert "[World] y is less" in lines

def test_validate_trait_casing_and_lenient(capsys):
    code = """
    the world is lenient
    creature Beast
      traits
        color is one of ("red" "blue")
        health is a number between 0 and 100
      end traits
      when born
        give self the trait color to "RED"
        give self the trait health to 150
      end born
    end creature
    bring draggy to life as Beast
    announce draggy color
    announce draggy health
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] red" in lines or "[World] RED" in lines
    assert "[World] 100" in lines

def test_world_roster(capsys):
    code = """
    creature Villager
      when born
        announce "Villager born"
      end born
    end creature
    bring v1 to life as Villager
    bring v2 to life as Villager
    announce the world's Villager creatures
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    # We should have a list representation containing the two creature dicts
    assert any("v1" in line and "v2" in line for line in lines)

def test_repeat_through_edge_cases(capsys):
    # repeat through None
    code1 = """
    repeat through my_null as x
      announce x
    end repeat
    """
    ast = parser.parse(code1)
    interpreter = Interpreter()
    interpreter.env['my_null'] = None
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World]" not in captured.out

    # repeat through single item (not a list)
    code2 = """
    repeat through 42 as x
      announce x
    end repeat
    """
    ast = parser.parse(code2)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World] 42" in captured.out

def test_syntax_errors():
    # Lexer syntax error
    from forwhile.errors import ForWhileSyntaxError
    with pytest.raises(ForWhileSyntaxError) as excinfo:
        parser.parse("@")
    assert "I couldn't understand the character '@'" in str(excinfo.value)

    # Parser EOF syntax error
    with pytest.raises(ForWhileSyntaxError) as excinfo:
        parser.parse("creature Dragon")
    assert "I got stuck at the end of the program" in str(excinfo.value)

def test_attach_with_constructor_params():
    code = """
    creature Leg
      when born with (length)
        announce "Leg made"
      end born
    end creature
    creature Dragon
      when born
        announce "Dragon made"
      end born
    end creature
    bring draggy to life as Dragon
    attach Leg to draggy
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)

def test_knows_shorthand_role(capsys):
    code = """
    creature Villager
      when born
        announce "born"
      end born
    end creature
    bring alice to life as Villager
    bring bob to life as Villager
    alice knows bob
    when alice knows bob as villager
      announce "alice knows bob as villager"
    end when
    when alice knows bob
      announce "alice knows bob"
    end when
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "alice knows bob as villager" in captured.out
    assert "alice knows bob" in captured.out

def test_remove_nonexistent_creature():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('REMOVE', 'nonexistent'))
    assert "nonexistent' hasn't been brought to life" in str(excinfo.value)

def test_world_forget_nonexistent_fact():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('WORLD_FORGET', 'missing_fact'))
    assert "The world doesn't remember a fact" in str(excinfo.value)

def test_forget_non_creature():
    interpreter = Interpreter()
    interpreter.env['not_creature'] = 123
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('FORGETS', ['not_creature'], 'friend'))
    assert "is not a creature" in str(excinfo.value)

def test_scene_errors_and_parameter_scoping(capsys):
    interpreter = Interpreter()
    # Play nonexistent scene
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('PLAY_SCENE', 'missing_scene', []))
    assert "doesn't have a scene named" in str(excinfo.value)

    # Play scene with wrong arguments count
    interpreter.scenes['greet'] = (['name'], [('ANNOUNCE', 'name')])
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.execute(('PLAY_SCENE', 'greet', []))
    assert "needs 1 details, but we only provided 0" in str(excinfo.value)

    # Dynamic parameters scoping override and restore
    code = """
    give name to "Alice"
    scene greet with (name)
      announce name
    end scene
    play scene greet with ("Bob")
    announce name
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    lines = [l.strip() for l in captured.out.split("\n") if l.strip()]
    assert "[World] Bob" in lines
    assert "[World] Alice" in lines

def test_computed_trait_shorthand(capsys):
    code = """
    creature Beast
      traits
        age is a number
        double_age is age + age
      end traits
      when born
        give self the trait age to 25
      end born
      action show
        announce double_age
      end action
    end creature
    bring draggy to life as Beast
    draggy does show
    """
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.run(ast)
    captured = capsys.readouterr()
    assert "[World] 50" in captured.out

def test_trait_kinds_strictness_and_validations(capsys):
    # Boolean error strict
    code1 = """
    the world is strict
    creature Beast
      traits
        alive is true or false
      end traits
      when born
        give self the trait alive to "maybe"
      end born
    end creature
    bring draggy to life as Beast
    """
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        Interpreter().run(parser.parse(code1))
    assert "must be yes or no" in str(excinfo.value)

    # Boolean warning lenient
    code2 = """
    the world is lenient
    creature Beast
      traits
        alive is true or false
      end traits
      when born
        give self the trait alive to "maybe"
      end born
    end creature
    bring draggy to life as Beast
    announce draggy alive
    """
    interpreter = Interpreter()
    interpreter.run(parser.parse(code2))
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "[World] True" in captured.out  # coerced "maybe" to True

    # List error strict
    code3 = """
    the world is strict
    creature Beast
      traits
        items is a list
      end traits
      when born
        give self the trait items to "not a list"
      end born
    end creature
    bring draggy to life as Beast
    """
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        Interpreter().run(parser.parse(code3))
    assert "must be a list" in str(excinfo.value)

    # List warning lenient
    code4 = """
    the world is lenient
    creature Beast
      traits
        items is a list
      end traits
      when born
        give self the trait items to "not a list"
      end born
    end creature
    bring draggy to life as Beast
    announce draggy items
    """
    interpreter = Interpreter()
    interpreter.run(parser.parse(code4))
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    # wrapped in list
    assert "[World] ['not a list']" in captured.out

    # Range strict invalid number
    code5 = """
    the world is strict
    creature Beast
      traits
        health is a number between 0 and 100
      end traits
      when born
        give self the trait health to "sick"
      end born
    end creature
    bring draggy to life as Beast
    """
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        Interpreter().run(parser.parse(code5))
    assert "must be a number between" in str(excinfo.value)

    # Range lenient invalid number
    code6 = """
    the world is lenient
    creature Beast
      traits
        health is a number between 0 and 100
      end traits
      when born
        give self the trait health to "sick"
      end born
    end creature
    bring draggy to life as Beast
    """
    interpreter = Interpreter()
    interpreter.run(parser.parse(code6))
    captured = capsys.readouterr()
    assert "Warning" in captured.out

    # Enum warning lenient
    code7 = """
    the world is lenient
    creature Beast
      traits
        color is one of ("red" "blue")
      end traits
      when born
        give self the trait color to "green"
      end born
    end creature
    bring draggy to life as Beast
    """
    interpreter = Interpreter()
    interpreter.run(parser.parse(code7))
    captured = capsys.readouterr()
    assert "Warning" in captured.out

def test_save_restore_serialization_edge_cases(tmp_path):
    # Non-serializable save
    interpreter = Interpreter()
    interpreter.env['unserializable'] = lambda x: x
    save_file = str(tmp_path / "save.json")
    interpreter.save_world(save_file)  # Should print warning but not crash

    # Non-existent reference in restore
    import json
    bad_data = {
        "creatures": {
            "draggy": {
                "__class__": "Dragon",
                "__name__": "draggy",
                "friend": {"__ref__": "missing_beast"}
            }
        },
        "variables": {
            "x": [1, 2, 3]
        }
    }
    bad_file = str(tmp_path / "bad.json")
    with open(bad_file, 'w') as f:
        json.dump(bad_data, f)
    
    interpreter2 = Interpreter()
    interpreter2.classes['Dragon'] = {'traits': {}, 'computed_traits': {}, 'parent': None}
    interpreter2.restore_world(bad_file)
    draggy = interpreter2.env['draggy']
    assert draggy['friend'] is None
    assert interpreter2.env['x'] == [1, 2, 3]

def test_unrecognized_formula_and_evaluate_none():
    interpreter = Interpreter()
    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.evaluate(None)
    assert "I couldn't understand this formula" in str(excinfo.value)

    with pytest.raises(ForWhileRuntimeError) as excinfo:
        interpreter.resolve_path(["nonexistent", "attr"])
    assert "nonexistent' hasn't been brought to life" in str(excinfo.value)

def test_find_trait_and_computed_methods_missing_class():
    interpreter = Interpreter()
    assert interpreter.find_trait_def("NonexistentClass", "trait") is None
    assert interpreter.find_computed_trait("NonexistentClass", "computed") is None
