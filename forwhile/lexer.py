import ply.lex as lex

tokens = (
    # New world-building tokens
    'CREATURE', 'BRING', 'LIFE', 'AS', 'GIVE', 'TRAIT', 'DOES', 'ACTION',
    'WHEN', 'OTHERWISE', 'UNTIL', 'BORN',
    
    # Relationship and collection tokens
    'KNOWS', 'ANYONE', 'THROUGH', 'FORGETS',
    
    # Event system tokens
    'WHENEVER', 'GETS', 'CHANGED', 'REMOVE', 'WORLD', 'ANNOUNCE',

    # World Memory tokens
    'THE_WORLD', 'THE_WORLDS', 'REMEMBERS', 'COUNTS', 'CREATURES', 'SAVE', 'RESTORE',

    # Narrative tokens
    'SCENE', 'PLAY', 'TICKS', 'TICK', 'SAYS', 'ON_EACH_TICK',

    # Trait Kind tokens
    'TRAITS', 'IS', 'WORD', 'NUMBER_KIND', 'BETWEEN', 'AND', 'ONE_OF',
    'TRUE_KEYWORD', 'FALSE_KEYWORD', 'OR_KEYWORD', 'LIST_KIND', 'YES', 'NO',
    'STRICT', 'LENIENT', 'IS_A',

    # Deprecated/Legacy tokens (kept for backward compatibility)
    'CLASS', 'END', 'CREATE', 'WITH', 'METHOD', 'FROM', 'SET', 'TO', 'SAY', 'ATTACH',
    'REPEAT', 'TIMES', 'IF', 'ELSE', 'ASK', 'CALL',
    
    # Literals and operators
    'IDENTIFIER', 'NUMBER', 'STRING', 'PLUS', 'MINUS', 'GT', 'LT', 'EQ', 'NEQ',
    'LPAREN', 'RPAREN',
    
    # Separator
    'NEWLINE'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_GT = r'>'
t_LT = r'<'
t_EQ = r'=='
t_NEQ = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_THE_WORLDS(t):
    r"[tT][hH][eE]\s+[wW][oO][rR][lL][dD]'[sS]"
    return t

def t_THE_WORLD(t):
    r"[tT][hH][eE]\s+[wW][oO][rR][lL][dD]"
    return t

def t_ON_EACH_TICK(t):
    r"[oO][nN]\s+[eE][aA][cC][hH]\s+[tT][iI][cC][kK]"
    return t

def t_IS_A(t):
    r"[iI][sS]\s+[aA][nN]?\b"
    return t

def t_ONE_OF(t):
    r"[oO][nN][eE]\s+[oO][fF]\b"
    return t

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
        'trait': 'TRAIT',
        'does': 'DOES',
        'action': 'ACTION',
        'when': 'WHEN',
        'otherwise': 'OTHERWISE',
        'until': 'UNTIL',
        'born': 'BORN',
        
        # Relationships & collection syntax
        'knows': 'KNOWS',
        'anyone': 'ANYONE',
        'through': 'THROUGH',
        'forgets': 'FORGETS',
        'forget': 'FORGETS',
        
        # Event system syntax
        'whenever': 'WHENEVER',
        'gets': 'GETS',
        'changed': 'CHANGED',
        'remove': 'REMOVE',
        'world': 'WORLD',
        'announce': 'ANNOUNCE',

        # World Memory keywords
        'remembers': 'REMEMBERS',
        'counts': 'COUNTS',
        'creatures': 'CREATURES',
        'save': 'SAVE',
        'restore': 'RESTORE',

        # Narrative keywords
        'scene': 'SCENE',
        'play': 'PLAY',
        'ticks': 'TICKS',
        'tick': 'TICK',
        'says': 'SAYS',

        # Trait Kind keywords
        'traits': 'TRAITS',
        'is': 'IS',
        'word': 'WORD',
        'number': 'NUMBER_KIND',
        'between': 'BETWEEN',
        'and': 'AND',
        'true': 'TRUE_KEYWORD',
        'false': 'FALSE_KEYWORD',
        'or': 'OR_KEYWORD',
        'list': 'LIST_KIND',
        'yes': 'YES',
        'no': 'NO',
        'strict': 'STRICT',
        'lenient': 'LENIENT',
        
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

def t_comment(t):
    r'\#[^\n]*'
    pass  # Ignore comments

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NEWLINE'
    return t

t_ignore = ' \t\r'

def t_error(t):
    from forwhile.errors import ForWhileSyntaxError
    raise ForWhileSyntaxError(f"I couldn't understand the character '{t.value[0]}' on line {t.lexer.lineno}. Did you make a typo?", line=t.lexer.lineno)

lexer = lex.lex()
