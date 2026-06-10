import ply.yacc as yacc
from forwhile.lexer import tokens

def p_program(p):
    '''program : opt_newlines statements
               | opt_newlines'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []

def p_opt_newlines(p):
    '''opt_newlines : opt_newlines NEWLINE
                    | '''
    pass

def p_statements(p):
    '''statements : statements statement_with_newline
                  | statement_with_newline'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement_with_newline(p):
    '''statement_with_newline : statement separator
                              | statement'''
    p[0] = p[1]

def p_separator(p):
    '''separator : separator NEWLINE
                 | NEWLINE'''
    pass

def p_opt_separator(p):
    '''opt_separator : separator
                     | '''
    pass

def p_statement(p):
    '''statement : class_definition
                 | create_statement
                 | set_statement
                 | attach_statement
                 | repeat_statement
                 | repeat_through_statement
                 | until_statement
                 | if_statement
                 | ask_statement
                 | say_statement
                 | call_statement
                 | knows_statement
                 | forgets_statement'''
    p[0] = p[1]

def p_class_definition(p):
    '''class_definition : CLASS IDENTIFIER opt_separator class_body opt_separator END CLASS
                        | CLASS IDENTIFIER FROM IDENTIFIER opt_separator class_body opt_separator END CLASS
                        | CREATURE IDENTIFIER opt_separator class_body opt_separator END CREATURE
                        | CREATURE IDENTIFIER FROM IDENTIFIER opt_separator class_body opt_separator END CREATURE'''
    if p[3] == 'from':
        p[0] = ('CREATURE', p[2], p[4], p[6])
    else:
        p[0] = ('CREATURE', p[2], None, p[4])

def p_class_body(p):
    '''class_body : class_body separator class_member
                  | class_member'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_class_member(p):
    '''class_member : constructor
                    | method'''
    p[0] = p[1]

def p_constructor(p):
    '''constructor : CREATE WITH LPAREN parameters RPAREN opt_separator statements opt_separator END CREATE
                   | WHEN BORN WITH LPAREN parameters RPAREN opt_separator statements opt_separator END BORN
                   | WHEN BORN opt_separator statements opt_separator END BORN'''
    if p[1] == 'create':
        p[0] = ('WHEN_BORN', p[4], p[7])
    elif p[1] == 'when' and p[2] == 'born' and p[3] == 'with':
        p[0] = ('WHEN_BORN', p[5], p[8])
    else:
        p[0] = ('WHEN_BORN', [], p[4])

def p_method(p):
    '''method : METHOD IDENTIFIER opt_separator statements opt_separator END METHOD
              | ACTION action_name opt_separator statements opt_separator END ACTION'''
    p[0] = ('ACTION', p[2], p[4])

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

def p_attribute_path(p):
    '''attribute_path : IDENTIFIER
                      | attribute_path IDENTIFIER'''
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
    '''set_statement : SET attribute_path TO expression
                     | GIVE attribute_path THE TRAIT IDENTIFIER TO expression'''
    if p[1] == 'set':
        obj_path = p[2][:-1]
        attr_name = p[2][-1]
        p[0] = ('GIVE_TRAIT', obj_path, attr_name, p[4])
    else:
        p[0] = ('GIVE_TRAIT', p[2], p[5], p[7])

def p_attach_statement(p):
    '''attach_statement : ATTACH expression TO expression'''
    p[0] = ('ATTACH', p[2], p[4])

def p_repeat_statement(p):
    '''repeat_statement : REPEAT expression TIMES opt_separator statements opt_separator END REPEAT'''
    p[0] = ('REPEAT', p[2], p[5])

def p_repeat_through_statement(p):
    '''repeat_through_statement : REPEAT THROUGH expression AS attribute_path opt_separator statements opt_separator END REPEAT'''
    p[0] = ('REPEAT_THROUGH', p[3], p[5], p[7])

def p_until_statement(p):
    '''until_statement : UNTIL condition opt_separator statements opt_separator END UNTIL'''
    p[0] = ('UNTIL', p[2], p[4])

def p_if_statement(p):
    '''if_statement : IF condition opt_separator statements opt_separator ELSE opt_separator statements opt_separator END IF
                    | IF condition opt_separator statements opt_separator END IF
                    | WHEN condition opt_separator statements opt_separator OTHERWISE opt_separator statements opt_separator END WHEN
                    | WHEN condition opt_separator statements opt_separator END WHEN'''
    if len(p) == 12:
        p[0] = ('IF', p[2], p[4], p[8])
    else:
        p[0] = ('IF', p[2], p[4], [])

def p_ask_statement(p):
    '''ask_statement : ASK STRING'''
    p[0] = ('ASK', p[2])

def p_say_statement(p):
    '''say_statement : SAY expression'''
    p[0] = ('SAY', p[2])

def p_call_statement(p):
    '''call_statement : CALL attribute_path
                      | expression DOES action_name'''
    if p[1] == 'call':
        instance_path = p[2][:-1]
        action_name = p[2][-1]
        p[0] = ('DOES_ACTION', instance_path, action_name)
    else:
        p[0] = ('DOES_ACTION', p[1], p[3])

def p_knows_statement(p):
    '''knows_statement : expression KNOWS expression
                       | expression KNOWS expression AS IDENTIFIER'''
    if len(p) == 4:
        p[0] = ('KNOWS', p[1], p[3], None)
    else:
        p[0] = ('KNOWS', p[1], p[3], p[5])

def p_forgets_statement(p):
    '''forgets_statement : expression FORGETS IDENTIFIER'''
    p[0] = ('FORGETS', p[1], p[3])

def p_condition(p):
    '''condition : expression comparison_op expression
                 | expression KNOWS expression
                 | expression KNOWS expression AS IDENTIFIER
                 | expression KNOWS ANYONE AS IDENTIFIER'''
    if len(p) == 4:
        if p[2] == 'knows':
            p[0] = ('KNOWS_COND', p[1], p[3], None)
        else:
            p[0] = ('CONDITION', p[1], p[2], p[3])
    elif len(p) == 6:
        p[0] = ('KNOWS_COND', p[1], p[3], p[5])
    else:
        p[0] = ('CONDITION', p[1], p[2], p[3])

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
                  | attribute_path
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
