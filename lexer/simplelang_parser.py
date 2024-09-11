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
    '''statement : class_definition
                 | create_statement
                 | set_statement
                 | attach_statement
                 | repeat_statement
                 | if_statement
                 | ask_statement
                 | say_statement
                 | call_statement'''
    p[0] = p[1]

def p_class_definition(p):
    '''class_definition : CLASS IDENTIFIER class_body END CLASS
                        | CLASS IDENTIFIER FROM IDENTIFIER class_body END CLASS'''
    if len(p) == 6:
        p[0] = ('CLASS', p[2], p[3])
    else:
        p[0] = ('CLASS', p[2], p[4], p[5])

def p_class_body(p):
    '''class_body : class_body class_member
                  | class_member'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_class_member(p):
    '''class_member : constructor
                    | method'''
    p[0] = p[1]

def p_constructor(p):
    'constructor : CREATE WITH LPAREN parameters RPAREN statements END CREATE'
    p[0] = ('CONSTRUCTOR', p[4], p[6])

def p_method(p):
    'method : METHOD IDENTIFIER statements END METHOD'
    p[0] = ('METHOD', p[2], p[3])

def p_parameters(p):
    '''parameters : parameters IDENTIFIER
                  | IDENTIFIER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_create_statement(p):
    '''create_statement : CREATE IDENTIFIER IDENTIFIER WITH expression
                        | CREATE IDENTIFIER IDENTIFIER'''
    if len(p) == 6:
        p[0] = ('CREATE', p[2], p[3], p[5])
    else:
        p[0] = ('CREATE', p[2], p[3])

def p_set_statement(p):
    'set_statement : SET IDENTIFIER IDENTIFIER TO expression'
    p[0] = ('SET', p[2], p[3], p[5])

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
    'ask_statement : ASK STRING'
    p[0] = ('ASK', p[2])

def p_say_statement(p):
    'say_statement : SAY expression'
    p[0] = ('SAY', p[2])

def p_call_statement(p):
    'call_statement : CALL IDENTIFIER IDENTIFIER'
    p[0] = ('CALL', p[2], p[3])

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
                  | IDENTIFIER
                  | IDENTIFIER IDENTIFIER
                  | expression PLUS expression
                  | LPAREN IDENTIFIER RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ('ATTRIBUTE', p[1], p[2])
    elif len(p) == 4 and p[1] == '(':
        p[0] = ('INPUT', p[2])
    else:
        p[0] = ('ADD', p[1], p[3])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()