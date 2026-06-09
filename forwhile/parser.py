import ply.yacc as yacc
from forwhile.lexer import tokens

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
                 | until_statement
                 | if_statement
                 | ask_statement
                 | say_statement
                 | call_statement'''
    p[0] = p[1]

def p_class_definition(p):
    '''class_definition : CLASS IDENTIFIER class_body END CLASS
                        | CLASS IDENTIFIER FROM IDENTIFIER class_body END CLASS
                        | CREATURE IDENTIFIER class_body END CREATURE
                        | CREATURE IDENTIFIER FROM IDENTIFIER class_body END CREATURE'''
    if len(p) == 6:
        # ('CREATURE', name, parent_or_None, members)
        p[0] = ('CREATURE', p[2], None, p[3])
    else:
        p[0] = ('CREATURE', p[2], p[4], p[5])

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
    '''constructor : CREATE WITH LPAREN parameters RPAREN statements END CREATE
                   | WHEN BORN WITH LPAREN parameters RPAREN statements END BORN
                   | WHEN BORN statements END BORN'''
    if p[1] == 'create':
        p[0] = ('WHEN_BORN', p[4], p[6])
    elif p[1] == 'when' and len(p) == 10:
        p[0] = ('WHEN_BORN', p[5], p[7])
    else:
        p[0] = ('WHEN_BORN', [], p[3])

def p_method(p):
    '''method : METHOD IDENTIFIER statements END METHOD
              | ACTION action_name statements END ACTION'''
    p[0] = ('ACTION', p[2], p[3])

def p_action_name(p):
    '''action_name : IDENTIFIER
                   | action_name IDENTIFIER'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + " " + p[2]

def p_parameters(p):
    '''parameters : parameters IDENTIFIER
                  | IDENTIFIER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_create_statement(p):
    '''create_statement : CREATE IDENTIFIER IDENTIFIER WITH expression
                        | CREATE IDENTIFIER IDENTIFIER
                        | BRING IDENTIFIER TO LIFE AS IDENTIFIER WITH expression
                        | BRING IDENTIFIER TO LIFE AS IDENTIFIER'''
    if p[1] == 'create':
        if len(p) == 6:
            p[0] = ('BRING_TO_LIFE', p[2], p[3], p[5])
        else:
            p[0] = ('BRING_TO_LIFE', p[2], p[3], None)
    else:
        instance = p[2]
        creature = p[6]
        if len(p) == 9:
            p[0] = ('BRING_TO_LIFE', creature, instance, p[8])
        else:
            p[0] = ('BRING_TO_LIFE', creature, instance, None)

def p_set_statement(p):
    '''set_statement : SET IDENTIFIER IDENTIFIER TO expression
                     | GIVE IDENTIFIER THE TRAIT IDENTIFIER TO expression'''
    if p[1] == 'set':
        p[0] = ('GIVE_TRAIT', p[2], p[3], p[5])
    else:
        p[0] = ('GIVE_TRAIT', p[2], p[5], p[7])

def p_attach_statement(p):
    '''attach_statement : ATTACH IDENTIFIER TO IDENTIFIER'''
    p[0] = ('ATTACH', p[2], p[4])

def p_repeat_statement(p):
    '''repeat_statement : REPEAT NUMBER TIMES statements END REPEAT'''
    p[0] = ('REPEAT', p[2], p[4])

def p_until_statement(p):
    '''until_statement : UNTIL condition statements END UNTIL'''
    p[0] = ('UNTIL', p[2], p[3])

def p_if_statement(p):
    '''if_statement : IF condition statements ELSE statements END IF
                    | WHEN condition statements OTHERWISE statements END WHEN'''
    p[0] = ('IF', p[2], p[3], p[5])

def p_ask_statement(p):
    '''ask_statement : ASK STRING'''
    p[0] = ('ASK', p[2])

def p_say_statement(p):
    '''say_statement : SAY expression'''
    p[0] = ('SAY', p[2])

def p_call_statement(p):
    '''call_statement : CALL IDENTIFIER IDENTIFIER
                      | IDENTIFIER DOES action_name'''
    if p[1] == 'call':
        p[0] = ('DOES_ACTION', p[2], p[3])
    else:
        p[0] = ('DOES_ACTION', p[1], p[3])

def p_condition(p):
    '''condition : IDENTIFIER IDENTIFIER comparison_op expression'''
    p[0] = ('CONDITION', p[1], p[2], p[3], p[4])

def p_comparison_op(p):
    '''comparison_op : GT
                     | LT
                     | EQ
                     | NEQ'''
    p[0] = p[1]

def p_expression_list(p):
    '''expression_list : expression_list expression
                       | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_expression(p):
    '''expression : STRING
                  | NUMBER
                  | IDENTIFIER
                  | IDENTIFIER IDENTIFIER
                  | expression PLUS expression
                  | expression MINUS expression
                  | LPAREN expression_list RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ('ATTRIBUTE', p[1], p[2])
    elif len(p) == 4 and p[1] == '(':
        if len(p[2]) == 1:
            if p[2][0] == 'input':
                p[0] = ('INPUT', 'input')
            else:
                p[0] = p[2][0]
        else:
            p[0] = p[2]
    else:
        if p[2] == '+':
            p[0] = ('ADD', p[1], p[3])
        else:
            p[0] = ('MINUS', p[1], p[3])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()
