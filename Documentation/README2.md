# Day 2 Progress

### Goals

- Define syntax rules.
- Specify the grammar for the language.
- Formalize the grammar for implementation.

### Syntax Rules

**Variables**
`set <variable> name to <value>`

**Arithmetic Operations**
`set <variable> to <variable> <operator> <value>`

**Classes**


`class <ClassName> set <attribute> to <value> end class`


**Creating and Attaching Characters**

`create character <CharacterName> attach <ClassName> to <CharacterName>`

**Loops**

`repeat <number> times <statement>* end repeat`

**Conditionals**

`if <condition> <statement>* else <statement>* end if`

**Input/Output**

`ask <text> set <variable> to (input) say <text>`

  

**Comments**
`# <comment>`

### Grammar Specification

**Grammar Definition (EBNF)**
```ebnf
<program> ::= <statement>*
<statement> ::= <set_statement>
             | <arithmetic_statement>
             | <class_definition>
             | <create_statement>
             | <attach_statement>
             | <repeat_statement>
             | <if_statement>
             | <ask_statement>
             | <say_statement>
             | <comment>
             
<set_statement> ::= 'set' <variable> 'to' <value>

<arithmetic_statement> ::= 'set' <variable> 'to' <arithmetic_expression>
<arithmetic_expression> ::= <variable> <operator> <value>
<operator> ::= '+' | '-' | '*' | '/'

<class_definition> ::= 'class' <identifier> <class_body> 'end class'
<class_body> ::= <set_statement>*

<create_statement> ::= 'create character' <identifier>
<attach_statement> ::= 'attach' <identifier> 'to' <identifier>

<repeat_statement> ::= 'repeat' <number> 'times' <block> 'end repeat'
<block> ::= <statement>*

<if_statement> ::= 'if' <condition> <block> ('else' <block>)? 'end if'
<condition> ::= <variable> <comparison_operator> <value>
<comparison_operator> ::= '>' | '<' | '=' | '!='

<ask_statement> ::= 'ask' "<question>" <newline> 'set' <variable> 'to' '(' 'input' ')'
<say_statement> ::= 'say' "<message>"

<comment> ::= '#' <text>

<variable> ::= <identifier>
<identifier> ::= <letter> <letter_or_digit>*
<letter> ::= 'a'..'z' | 'A'..'Z'
<letter_or_digit> ::= <letter> | <digit>
<digit> ::= '0'..'9'
<value> ::= <text> | <number> | <color>
<text> ::= '"' <letter_or_digit>* '"'
<number> ::= <digit>+
<color> ::= "'" <letter_or_digit>* "'"

```
### Formalized Grammar
The formalized grammar for ForWhile was outlined, specifying how each construct is parsed and interpreted. This includes defining the syntax and structure for statements, expressions, and control flow constructs.

### Summary
- Syntax rules were defined and documented.
- Grammar was specified in EBNF notation.
- Grammar was formalized to guide lexer and parser implementation.
