
# Day 3 Progress

### Goals

- Implement the Lexer and Parser based on the formalized grammar.

### Lexer and Parser Implementation

Today, the lexer and parser for the programming language were implemented using ANTLR. The following steps were taken:

1. **Set Up ANTLR**: Installed and configured ANTLR for the project.
2. **Created the Grammar File**: Defined the grammar rules in `SimpleLang.g4` using EBNF notation.
3. **Generated Lexer and Parser**: Used ANTLR to generate lexer and parser code from the grammar file.
4. **Implemented the Interpreter**: Developed a basic interpreter to process and execute parsed code.

### ANTLR Grammar File (`SimpleLang.g4`)

The grammar file includes the following rules:

```antlr
// Grammar definition in ANTLR

grammar SimpleLang;

program: statement*;

statement: set_statement
         | arithmetic_statement
         | class_definition
         | create_statement
         | attach_statement
         | repeat_statement
         | if_statement
         | ask_statement
         | say_statement
         | comment;

set_statement: 'set' variable 'to' value;
arithmetic_statement: 'set' variable 'to' arithmetic_expression;
arithmetic_expression: variable operator value;
operator: '+' | '-' | '*' | '/';
class_definition: 'class' identifier class_body 'end class';
class_body: set_statement*;
create_statement: 'create character' identifier;
attach_statement: 'attach' identifier 'to' identifier;
repeat_statement: 'repeat' number 'times' block 'end repeat';
block: statement*;
if_statement: 'if' condition block ('else' block)? 'end if';
condition: variable comparison_operator value;
comparison_operator: '>' | '<' | '=' | '!=';
ask_statement: 'ask' text '\n' 'set' variable 'to' '(' 'input' ')';
say_statement: 'say' text;
comment: '#' text;
variable: identifier;
identifier: LETTER (LETTER | DIGIT)*;
text: '"' (LETTER | DIGIT)* '"';
number: DIGIT+;
color: '\'' (LETTER | DIGIT)* '\'';
LETTER: 'a'..'z' | 'A'..'Z';
DIGIT: '0'..'9';
WS: [ \t\n\r]+ -> skip;

```

### Testing and Validation

- Created a test file with sample code to validate the lexer and parser.
- Ran the interpreter against the test file and verified that all syntax rules are correctly processed.

### Summary

- The lexer and parser for the programming language were successfully implemented using ANTLR.
- The grammar rules were validated and tested using sample code.
- The foundation is now set for further development of the interpreter and additional language features.
