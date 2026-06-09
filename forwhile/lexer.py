import ply.lex as lex

tokens = (
    # New world-building tokens
    'CREATURE', 'BRING', 'LIFE', 'AS', 'GIVE', 'THE', 'TRAIT', 'DOES', 'ACTION',
    'WHEN', 'OTHERWISE', 'UNTIL', 'BORN',
    
    # Deprecated/Legacy tokens (kept for backward compatibility)
    'CLASS', 'END', 'CREATE', 'WITH', 'METHOD', 'FROM', 'SET', 'TO', 'SAY', 'ATTACH',
    'REPEAT', 'TIMES', 'IF', 'ELSE', 'ASK', 'CALL',
    
    # Literals and operators
    'IDENTIFIER', 'NUMBER', 'STRING', 'PLUS', 'MINUS', 'GT', 'LT', 'EQ', 'NEQ',
    'LPAREN', 'RPAREN'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_GT = r'>'
t_LT = r'<'
t_EQ = r'=='
t_NEQ = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    val_lower = t.value.lower()
    
    keywords = {
        # New syntax
        'creature': 'CREATURE',
        'bring': 'BRING',
        'life': 'LIFE',
        'as': 'AS',
        'give': 'GIVE',
        'the': 'THE',
        'trait': 'TRAIT',
        'does': 'DOES',
        'action': 'ACTION',
        'when': 'WHEN',
        'otherwise': 'OTHERWISE',
        'until': 'UNTIL',
        'born': 'BORN',
        
        # Old/Deprecated syntax (aliases)
        'class': 'CLASS',
        'end': 'END',
        'create': 'CREATE',
        'with': 'WITH',
        'method': 'METHOD',
        'from': 'FROM',
        'set': 'SET',
        'to': 'TO',
        'say': 'SAY',
        'attach': 'ATTACH',
        'repeat': 'REPEAT',
        'times': 'TIMES',
        'if': 'IF',
        'else': 'ELSE',
        'ask': 'ASK',
        'call': 'CALL'
    }
    
    if val_lower in keywords:
        t.type = keywords[val_lower]
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"[^"]*\"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
