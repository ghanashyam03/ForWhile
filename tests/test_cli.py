import sys
import pytest
from unittest.mock import patch
from forwhile.interpreter import main

def test_cli_version(capsys):
    with patch.object(sys, 'argv', ['forwhile', '--version']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "version 1.0.1" in captured.out

def test_cli_help(capsys):
    with patch.object(sys, 'argv', ['forwhile']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Usage:" in captured.out
    
    with patch.object(sys, 'argv', ['forwhile', 'unknown-cmd']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out

def test_cli_check_success(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'check', 'examples/01_hello.fw']):
        main()
    captured = capsys.readouterr()
    assert "Your story is valid" in captured.out

def test_cli_check_no_file(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'check']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Please provide the name of the story file" in captured.out

def test_cli_check_missing_file(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'check', 'missing.fw']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "File 'missing.fw' not found" in captured.out

def test_cli_check_syntax_error(capsys, tmp_path):
    bad_file = tmp_path / "bad.fw"
    bad_file.write_text("creature Dragon \n set health to 100", encoding='utf-8')
    with patch.object(sys, 'argv', ['forwhile', 'check', str(bad_file)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "I got stuck" in captured.out or "Story Error" in captured.out

def test_cli_run_no_file(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'run']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Please provide the name of the story file" in captured.out

def test_cli_run_missing_file(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'run', 'missing.fw']):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "File 'missing.fw' not found" in captured.out

def test_cli_run_success(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'run', 'examples/01_hello.fw']):
        main()
    captured = capsys.readouterr()
    assert "Alice says: Hello there!" in captured.out

def test_repl_interaction(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'start']):
        with patch('builtins.input', side_effect=['quit']):
            main()
    captured = capsys.readouterr()
    assert "Welcome to ForWhile" in captured.out

def test_repl_help(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'start']):
        with patch('builtins.input', side_effect=['help', 'quit']):
            main()
    captured = capsys.readouterr()
    assert "Creating things:" in captured.out

def test_repl_empty_line_exit(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'start']):
        with patch('builtins.input', side_effect=['']):
            main()
    captured = capsys.readouterr()
    assert "Welcome to ForWhile" in captured.out

def test_repl_execute_code(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'start']):
        with patch('builtins.input', side_effect=['announce "hello world"', 'quit']):
            main()
    captured = capsys.readouterr()
    assert "[World] hello world" in captured.out

def test_repl_execute_nested_code(capsys):
    with patch.object(sys, 'argv', ['forwhile', 'start']):
        with patch('builtins.input', side_effect=[
            'creature Dragon',
            '  when born',
            '    give self the trait health to 100',
            '  end born',
            'end creature',
            'bring d to life as Dragon',
            'announce d health',
            'quit'
        ]):
            main()
    captured = capsys.readouterr()
    assert "[World] 100" in captured.out
