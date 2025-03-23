# Lexer & Scanner

### Course: Formal Languages & Finite Automata
### Author: Gurev Andreea FAF-231

# Theory

Lexical analysis, also known as scanning or tokenization, is a fundamental process in the compilation 
and interpretation of programming languages, markup languages, and other structured text formats. It 
involves analyzing a sequence of characters to identify meaningful units known as lexemes, which are 
then classified into tokens based on predefined rules. The primary purpose of a lexer (or tokenizer/scanner)
is to break down the input into manageable components that the next stages of processing—such as 
parsing—can work with. Unlike lexemes, which are simply substrings extracted based on delimiters like 
whitespace, tokens provide a higher level of abstraction by categorizing lexemes into types, such as 
keywords, identifiers, numbers, or operators. A lexer typically operates using deterministic finite 
automata (DFA), transitioning between states to recognize patterns defined by regular expressions. 
For instance, numeric tokens might be recognized by a sequence of digits, while keywords are matched 
against a reserved set of words. The lexer's role is crucial in language processing because it not 
only simplifies parsing but also allows for early detection of errors, such as illegal characters. 
In a broader context, lexical analysis is essential in domains beyond compilers, including data 
validation, natural language processing, and code highlighting in IDEs. Implementing a lexer requires 
designing a system that correctly identifies and processes input symbols while managing position tracking, 
error handling, and token classification. A well-structured lexer ensures efficiency, correctness, and 
maintainability in the language processing pipeline.


# Objectives
1. Understand what lexical analysis is.
2. Get familiar with the inner workings of a lexer/scanner/tokenizer.
3. Implement a sample lexer and show how it works.

# Implementations
### Error handling class
The lexer implements an error handling system using a class hierarchy. This approach provides 
detailed error information including position tracking for helpful error messages.

The Error class stores:

1) Start and end positions of the error in the source text
2) Error name and details
3) Method to format the error as a user-friendly string

````
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        return f"{self.error_name}: {self.details}\n" \
               f"At line {self.pos_start.line_nr + 1}, column {self.pos_start.column_nr + 1}"
 ````            


#### Error Formatting (as_string Method)
This method generates a message that describes the error. It has:
1) The name of the error (for example, "Illegal Character").
2) The details of the error (for example, "Unexpected symbol @").
3) The location in the input text, using pos_start.line_nr + 1 and pos_start.column_nr + 1. 



#### Specialized Error Classes

This is a specific type of error that occurs when the user enters an invalid character that the program 
does not recognize. Instead of writing separate logic for illegal character errors, this class extends 
the Error class and predefines the error name as "Illegal Character".

Since an illegal character is just a type of error, this class inherits from Error. \
The super().__init__ call allows IllegalCharError to use all the functionality of Error while setting 
the error_name automatically. This means:\
• The pos_start and pos_end attributes are handled in the same way as in Error. \
• The details parameter is passed to describe the invalid character.


````
class IllegalCharError(Error):

    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)
        
class UnknownFunctionError(Error):

    def __init__(self, pos_start, pos_end, function_name):
        super().__init__(pos_start, pos_end, 'Unknown Function',
                         f"'{function_name}' is not a recognized function")
````


### Token class
The Token class serves as a container for lexical tokens identified during the parsing process. 
It has two main purposes:

#### Data Storage:
1) self.type: Stores the token category (like INT, FLOAT, PLUS, MINUS, SIN, etc.).
2) self.value: Optionally stores the actual value for tokens that need it (like numbers).

#### Display Representation:
1) The __repr__ method creates a human-readable string representation of the token.
2) For tokens with values (like numbers), it shows both type and value (e.g., INT:42).
3) For tokens without values (like operators), it shows only the type (e.g., PLUS).

````
class Token:

    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
````

### Position class 

Position tracking is implemented through a dedicated class that monitors the current position in the 
source text.

**This class tracks:**\
• index: The current position in the text as a number (for example, 0 for the first character, 1 for the second).\
• line_nr: The current line number. This starts at 0 and increases when a newline character (\n) is encountered.\
• column_nr: The column position within the current line, which resets when moving to a new line.


**advance() Method**\
Moves to the next character, handling newlines correctly:\
• It increases index by 1.\
• It increases column_nr by 1.\
• If the character is a newline (\n), it moves to the next line and resets column_nr to 0.


**copy() Method**\
Creates a clone of the current position (useful for error reporting)
````
class Position:
    def __init__(self, index, line_nr, column_nr):
        self.index = index
        self.line_nr = line_nr
        self.column_nr = column_nr

    def advance(self, current_char=None):
        self.index += 1
        self.column_nr += 1

        if current_char == '\n':
            self.line_nr += 1
            self.column_nr = 0

        return self

    def copy(self):
        return Position(self.index, self.line_nr, self.column_nr)
````


### Lexer Implementation
The lexer is the core component, responsible for converting text input into tokens. Here's a breakdown of its implementation:
#### Initialization

The initialization sets up:

• Storage of the input text. \
• Creation of a Position object starting before the first character. \
• Initial advancement to set the current character to the first one. \

The advance() method:

• Updates the position using the Position class. \
• Updates the current character or sets it to None when reaching the end. \


````
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(-1, 0, -1)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.index < len(self.text):
            self.current_char = self.text[self.pos.index]
        else:
            self.current_char = None
````

#### Generating tokens (make_tokens Method)
This method scans the text character by character:\
• If it finds whitespace (\t or space), it skips it.\
• If it finds +, -, *, /, (, ), it creates the corresponding token.\
• If it finds letters, it assumes it is a function (sin, cos, etc.) and calls make_function().\
• If it finds a number, it calls make_number() to process it.\
• If it finds an invalid character, it returns an IllegalCharError.\
• This method loops until the entire input is processed.

#### Function Recognition
The make_function() method:

• Records the starting position for potential error reporting. \
• Collects consecutive alphabetic characters to form a function name. \
• Checks if the name exists in the MATH_FUNCTIONS dictionary. \
• Returns either a valid token or an error. \

````
    def make_function(self):
        func_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char.isalpha():
            func_str += self.current_char
            self.advance()

        if func_str in MATH_FUNCTIONS:
            return Token(MATH_FUNCTIONS[func_str])

        return UnknownFunctionError(pos_start, self.pos, func_str)
````

#### Number Processing
The make_number() method:

• Collects consecutive digits and at most one decimal point. \
• Tracks decimal point count to handle malformed numbers. \
• Creates the appropriate token type (INT or FLOAT) based on presence of decimal point. \
• Converts the string to the correct numeric type. \
````
    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char is not None and (self.current_char in DIGITS or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1

            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
````
#### Runtime Functions
The run() function:

• Creates a lexer instance with the input text. \
• Calls the lexer to produce tokens. \
• Returns the tokens or error for further processing. \

# Results
````
Enter operation (or "exit" to quit): 1.2 + 3^(8) - ctg(12) - log(13.3)
[FLOAT:1.2, PLUS, INT:3, POW, LPAREN, INT:8, RPAREN, MINUS, CTG, LPAREN, INT:12, RPAREN, MINUS, LOG, LPAREN, FLOAT:13.3, RPAREN]

Enter operation (or "exit" to quit): 12 - sinus(4)
Unknown Function: 'sinus' is not a recognized function
At line 1, column 6

Enter operation (or "exit" to quit): exit
Exiting program...
````

# Conclusion

This laboratory work provided a hands-on approach to understanding lexical analysis and the role of a 
lexer in processing structured text. We successfully achieved all learning 
objectives: exploring lexical analysis theory, examining the internal mechanisms of lexers, and creating 
a working implementation that accurately tokenizes input according to established rules. Our code 
implementation effectively demonstrated critical elements including sophisticated token classification, 
robust error handling, and precise position tracking—all essential components that reinforce the core 
principles of lexical analysis in compiler design.