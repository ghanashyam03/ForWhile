import ply.yacc as yacc
from simplelang_lexer import tokens

def p_program(p):
    '''program : statements'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : set_statement
                 | create_statement
                 | attach_statement
                 | repeat_statement
                 | if_statement
                 | ask_statement
                 | say_statement'''
    p[0] = p[1]

def p_set_statement(p):
    'set_statement : SET IDENTIFIER IDENTIFIER TO expression'
    p[0] = ('SET', p[2], p[3], p[5])

def p_create_statement(p):
    'create_statement : CREATE IDENTIFIER IDENTIFIER'
    p[0] = ('CREATE', p[2], p[3])

def p_attach_statement(p):
    'attach_statement : ATTACH IDENTIFIER TO IDENTIFIER'
    p[0] = ('ATTACH', p[2], p[4])

def p_repeat_statement(p):
    'repeat_statement : REPEAT NUMBER TIMES statements END REPEAT'
    p[0] = ('REPEAT', p[2], p[4])

def p_if_statement(p):
    'if_statement : IF condition statements ELSE statements END IF'
    p[0] = ('IF', p[2], p[3], p[5])

def p_ask_statement(p):
    'ask_statement : ASK STRING SET IDENTIFIER IDENTIFIER TO LPAREN IDENTIFIER RPAREN'
    p[0] = ('ASK', p[2], p[4], p[5], p[8])

def p_say_statement(p):
    'say_statement : SAY expression'
    p[0] = ('SAY', p[2])

def p_condition(p):
    'condition : IDENTIFIER IDENTIFIER comparison_op expression'
    p[0] = ('CONDITION', p[1], p[2], p[3], p[4])

def p_comparison_op(p):
    '''comparison_op : GT
                     | LT
                     | EQ
                     | NEQ'''
    p[0] = p[1]

def p_expression(p):
    '''expression : STRING
                  | NUMBER
                  | COLOR
                  | IDENTIFIER
                  | IDENTIFIER IDENTIFIER
                  | expression PLUS expression'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ('ATTRIBUTE', p[1], p[2])
    else:
        p[0] = ('ADD', p[1], p[3])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()