import ply.lex as lex

tokens = (
    'CLASS', 'END', 'CREATE', 'WITH', 'METHOD', 'FROM', 'SET', 'TO', 'SAY', 'ATTACH',
    'REPEAT', 'TIMES', 'IF', 'ELSE', 'ASK', 'CALL',
    'IDENTIFIER', 'NUMBER', 'STRING', 'PLUS', 'GT', 'LT', 'EQ', 'NEQ',
    'LPAREN', 'RPAREN'
)

t_PLUS = r'\+'
t_GT = r'>'
t_LT = r'<'
t_EQ = r'=='
t_NEQ = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value.lower() in {'class', 'end', 'create', 'with', 'method', 'from', 'set', 'to', 'say', 'attach',
                           'repeat', 'times', 'if', 'else', 'ask', 'call'}:
        t.type = t.value.upper()
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