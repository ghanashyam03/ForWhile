import ply.yacc as yacc
from forwhile.lexer import tokens

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES'),
)

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
                 | forgets_statement
                 | whenever_statement
                 | remove_statement
                 | announce_statement
                 | world_remembers
                 | world_forgets
                 | save_world
                 | restore_world
                 | scene_definition
                 | play_scene
                 | tick_loop
                 | on_tick
                 | character_says
                 | world_strictness'''
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
                    | method
                    | traits_block'''
    p[0] = p[1]

def p_traits_block(p):
    '''traits_block : TRAITS opt_separator trait_defs opt_separator END TRAITS'''
    p[0] = ('TRAITS_BLOCK', p[3])

def p_trait_defs(p):
    '''trait_defs : trait_defs separator trait_def
                  | trait_def'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_trait_def(p):
    '''trait_def : IDENTIFIER IS_A WORD
                 | IDENTIFIER IS_A NUMBER_KIND
                 | IDENTIFIER IS_A NUMBER_KIND BETWEEN expression AND expression
                 | IDENTIFIER IS ONE_OF expression
                 | IDENTIFIER IS TRUE_KEYWORD OR_KEYWORD FALSE_KEYWORD
                 | IDENTIFIER IS YES OR_KEYWORD NO
                 | IDENTIFIER IS_A LIST_KIND
                 | IDENTIFIER IS expression'''
    if len(p) == 4:
        if p[2].lower() == 'is':
            p[0] = ('COMPUTED_TRAIT', p[1], p[3])
        elif p[3].lower() == 'word':
            p[0] = ('TRAIT_DEF', p[1], 'word', None)
        elif p[3].lower() == 'number':
            p[0] = ('TRAIT_DEF', p[1], 'number', None)
        elif p[3].lower() == 'list':
            p[0] = ('TRAIT_DEF', p[1], 'list', None)
    elif len(p) == 5:
        p[0] = ('TRAIT_DEF', p[1], 'enum', p[4])
    elif len(p) == 6:
        p[0] = ('TRAIT_DEF', p[1], 'boolean', None)
    elif len(p) == 8:
        p[0] = ('TRAIT_DEF', p[1], 'number_range', (p[5], p[7]))

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
                     | GIVE attribute_path IDENTIFIER TRAIT IDENTIFIER TO expression
                     | GIVE attribute_path TRAIT IDENTIFIER TO expression
                     | GIVE attribute_path TO expression'''
    if p[1] == 'set':
        obj_path = p[2][:-1]
        attr_name = p[2][-1]
        p[0] = ('GIVE_TRAIT', obj_path, attr_name, p[4])
    else:
        if len(p) == 8:
            p[0] = ('GIVE_TRAIT', p[2], p[5], p[7])
        elif len(p) == 7:
            p[0] = ('GIVE_TRAIT', p[2], p[4], p[6])
        else:
            obj_path = p[2][:-1]
            attr_name = p[2][-1]
            p[0] = ('GIVE_TRAIT', obj_path, attr_name, p[4])

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

def p_whenever_statement(p):
    '''whenever_statement : WHENEVER subject DOES action_name opt_separator statements opt_separator END WHENEVER
                          | WHENEVER subject GETS TRAIT IDENTIFIER CHANGED opt_separator statements opt_separator END WHENEVER
                          | WHENEVER subject IDENTIFIER BORN opt_separator statements opt_separator END WHENEVER
                          | WHENEVER subject IDENTIFIER opt_separator statements opt_separator END WHENEVER'''
    if len(p) == 10:
        if p[3] == 'does':
            # WHENEVER subject DOES action_name ...
            p[0] = ('WHENEVER', 'DOES_ACTION', p[2], p[4], p[6])
        else:
            # WHENEVER subject IDENTIFIER BORN ...
            action = p[3] + " " + p[4]
            p[0] = ('WHENEVER', 'DOES_ACTION', p[2], action, p[6])
    elif len(p) == 12:
        # WHENEVER subject GETS TRAIT IDENTIFIER CHANGED ...
        p[0] = ('WHENEVER', 'TRAIT_CHANGED', p[2], p[5], p[8])
    elif len(p) == 9:
        # WHENEVER subject IDENTIFIER ... (e.g. dies)
        p[0] = ('WHENEVER', 'DOES_ACTION', p[2], p[3], p[5])

def p_subject(p):
    '''subject : IDENTIFIER
               | ANYONE'''
    p[0] = p[1]

def p_remove_statement(p):
    '''remove_statement : REMOVE IDENTIFIER FROM WORLD'''
    p[0] = ('REMOVE', p[2])

def p_announce_statement(p):
    '''announce_statement : ANNOUNCE expression'''
    p[0] = ('ANNOUNCE', p[2])

def p_world_remembers(p):
    '''world_remembers : THE_WORLD REMEMBERS fact_name AS expression'''
    p[0] = ('WORLD_SET', p[3], p[5])

def p_world_forgets(p):
    '''world_forgets : THE_WORLD FORGETS fact_name'''
    p[0] = ('WORLD_FORGET', p[3])

def p_save_world(p):
    '''save_world : SAVE THE_WORLD TO expression'''
    p[0] = ('SAVE_WORLD', p[4])

def p_restore_world(p):
    '''restore_world : RESTORE THE_WORLD FROM expression'''
    p[0] = ('RESTORE_WORLD', p[4])

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
                     | NEQ
                     | IS'''
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
                  | expression TIMES expression
                  | LPAREN expression_list RPAREN
                  | LPAREN RPAREN
                  | world_expr
                  | YES
                  | NO'''
    if len(p) == 2:
        if isinstance(p[1], str) and p[1].lower() == 'yes':
            p[0] = True
        elif isinstance(p[1], str) and p[1].lower() == 'no':
            p[0] = False
        else:
            p[0] = p[1]
    elif len(p) == 3:
        if p[1] == '(':
            p[0] = []
        else:
            p[0] = ('ATTRIBUTE', p[1], p[2])
    elif len(p) == 4 and p[1] == '(':
        if len(p[2]) == 1:
            if p[2][0] == 'input':
                p[0] = ('INPUT', 'input')
            else:
                p[0] = p[2][0]
        else:
            p[0] = ('LIST_LITERAL', p[2])
    else:
        if p[2] == '+':
            p[0] = ('ADD', p[1], p[3])
        elif p[2] == '-':
            p[0] = ('MINUS', p[1], p[3])
        else:
            p[0] = ('MULTIPLY', p[1], p[3])

def p_world_expr(p):
    '''world_expr : THE_WORLD KNOWS fact_name
                  | THE_WORLDS IDENTIFIER CREATURES
                  | THE_WORLD COUNTS IDENTIFIER'''
    p2_lower = p[2].lower() if isinstance(p[2], str) else ""
    p3_lower = p[3].lower() if (len(p) > 3 and isinstance(p[3], str)) else ""
    
    if p2_lower == 'knows':
        p[0] = ('WORLD_GET', p[3])
    elif p3_lower == 'creatures':
        p[0] = ('WORLD_ROSTER', p[2])
    else:
        p[0] = ('WORLD_COUNTS', p[3])

def p_fact_name(p):
    '''fact_name : IDENTIFIER
                 | fact_name IDENTIFIER'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + " " + p[2]

def p_scene_definition(p):
    '''scene_definition : SCENE scene_name opt_separator statements opt_separator END SCENE
                        | SCENE scene_name WITH LPAREN parameters RPAREN opt_separator statements opt_separator END SCENE'''
    if len(p) == 8:
        p[0] = ('SCENE', p[2], [], p[4])
    else:
        p[0] = ('SCENE', p[2], p[5], p[8])

def p_play_scene(p):
    '''play_scene : PLAY SCENE scene_name
                  | PLAY SCENE scene_name WITH LPAREN expression_list RPAREN'''
    if len(p) == 4:
        p[0] = ('PLAY_SCENE', p[3], [])
    else:
        p[0] = ('PLAY_SCENE', p[3], p[6])

def p_tick_loop(p):
    '''tick_loop : THE_WORLD TICKS expression TIMES opt_separator statements opt_separator END TICKS'''
    p[0] = ('TICK_LOOP', p[3], p[6])

def p_on_tick(p):
    '''on_tick : ON_EACH_TICK opt_separator statements opt_separator END TICK'''
    p[0] = ('ON_TICK', p[3])

def p_character_says(p):
    '''character_says : IDENTIFIER SAYS expression'''
    p[0] = ('CHARACTER_SAYS', p[1], p[3])

def p_scene_name(p):
    '''scene_name : IDENTIFIER
                  | scene_name IDENTIFIER'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + " " + p[2]

def p_world_strictness(p):
    '''world_strictness : THE_WORLD IS STRICT
                        | THE_WORLD IS LENIENT'''
    p[0] = ('WORLD_STRICTNESS', p[3].lower())

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()
