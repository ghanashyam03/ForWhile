import ply.lex as lex

tokens = (
    'SET', 'CREATE', 'ATTACH', 'REPEAT', 'TIMES', 'END', 'IF', 'ELSE', 'ASK', 'SAY',
    'IDENTIFIER', 'NUMBER', 'STRING', 'PLUS', 'LPAREN', 'RPAREN', 'GT', 'LT', 'EQ', 'NEQ',
    'COLOR', 'TO'
)

t_SET = r'set'
t_CREATE = r'create'
t_ATTACH = r'attach'
t_REPEAT = r'repeat'
t_TIMES = r'times'
t_END = r'end'
t_IF = r'if'
t_ELSE = r'else'
t_ASK = r'ask'
t_SAY = r'say'
t_PLUS = r'\+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_GT = r'>'
t_LT = r'<'
t_EQ = r'=='
t_NEQ = r'!='
t_TO = r'to'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in {'set', 'create', 'attach', 'repeat', 'times', 'end', 'if', 'else', 'ask', 'say', 'to'}:
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

def t_COLOR(t):
    r'\'[a-zA-Z]+\''
    t.value = t.value[1:-1]  # Remove quotes
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()