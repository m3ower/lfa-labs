# Laboratory Work Nr. 6: Parser & Building an Abstract Syntax Tree

__Course: Formal Languages & Finite Automata__  

__Author: Gurev Andreea, FAF0-231__
## Overview

This project implements a complete parser and Abstract Syntax Tree (AST) builder for mathematical expressions. It can process basic arithmetic operations, nested expressions with parentheses, and trigonometric functions (sin, cos, tg, ctg). The implementation follows a structured approach with lexical analysis using regular expressions, followed by recursive descent parsing to build a comprehensive AST representation of the input expression.

## Features

- Tokenization using regular expressions
- Support for basic arithmetic operations (+, -, *, /)
- Support for mathematical functions (sin, cos, tg, ctg)
- Proper operator precedence handling
- Detailed error reporting with position information
- Visual AST representation

## Components

### 1. TokenType Enum

The `TokenType` enum defines all possible token categories that can be recognized by the lexer. Using Python's `Enum` class provides a clean, type-safe way to represent token types throughout the application.

```python
class TokenType(Enum):
    INT = auto()         # Integer number
    FLOAT = auto()       # Float number
    PLUS = auto()        # +
    MINUS = auto()       # -
    MUL = auto()         # *
    DIV = auto()         # /
    POW = auto()         # ^
    LOG = auto()         # log
    COS = auto()         # cos
    SIN = auto()         # sin
    TG = auto()          # tg
    CTG = auto()         # ctg
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    EOF = auto()         # End of file
```

This implementation provides a clear categorization of tokens and allows for easy extension when new token types need to be added. Each token type is given a unique value through Python's `auto()` function, which automatically assigns incrementing integer values.

### 2. Token Class

The `Token` class represents individual tokens identified during lexical analysis. Each token contains:

```python
class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_        # The token's type (from TokenType enum)
        self.value = value       # Optional value (e.g., the actual number for INT/FLOAT)
        self.pos_start = pos_start  # Position information for error reporting
        self.pos_end = pos_end      # Position information for error reporting

    def __repr__(self):
        if self.value is not None:
            return f'{self.type.name}:{self.value}'
        return f'{self.type.name}'
```

The class includes position tracking for error reporting and a custom string representation method that displays the token type and value (if present). This is particularly useful for debugging and visualizing the tokenization process.

### 3. Position Tracking

The `Position` class keeps track of the current position in the input text:

```python
class Position:
    def __init__(self, index, line_nr, column_nr):
        self.index = index       # Index in the input string
        self.line_nr = line_nr   # Line number (for multi-line input)
        self.column_nr = column_nr  # Column number within the line

    def advance(self, current_char=None):
        self.index += 1
        self.column_nr += 1

        if current_char == '\n':  # Handle newlines
            self.line_nr += 1
            self.column_nr = 0

        return self

    def copy(self):
        return Position(self.index, self.line_nr, self.column_nr)
```

This class provides the foundation for precise error reporting by tracking both the absolute position in the input text and the line/column information. The `advance` method moves the position forward, handling newlines correctly, while the `copy` method creates a new Position object with the same values, which is useful for creating token position ranges.

### 4. Error Handling

A robust error handling system is implemented with several error classes:

```python
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        return f"{self.error_name}: {self.details}\n" \
               f"At line {self.pos_start.line_nr + 1}, column {self.pos_start.column_nr + 1}"
```

Specific error classes include:
- `IllegalCharError`: For unrecognized characters during lexical analysis
- `UnknownFunctionError`: For invalid function names
- `ParserError`: For syntax errors during parsing

Each error provides detailed information about what went wrong and where it occurred in the input text, making debugging and understanding the errors much easier for the user.

### 5. Lexer Implementation

The `Lexer` class is responsible for breaking down the input text into tokens using regular expressions:

```python
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(0, 0, 0)
        
    def make_tokens(self):
        token_specification = [
            ('FLOAT',      r'\d+\.\d+'),              # Float numbers
            ('INT',        r'\d+'),                   # Integer numbers
            ('PLUS',       r'\+'),                    # Addition operator
            ('MINUS',      r'-'),                     # Subtraction operator
            ('MUL',        r'\*'),                    # Multiplication operator
            ('DIV',        r'/'),                     # Division operator
            ('POW',        r'\^'),                    # Power operator
            ('LPAREN',     r'\('),                    # Left parenthesis
            ('RPAREN',     r'\)'),                    # Right parenthesis
            ('FUNCTION',   r'(cos|sin|tg|ctg|log)'),  # Mathematical functions
            ('SKIP',       r'[ \t\n]+'),              # Skip over spaces and tabs
            ('MISMATCH',   r'.'),                     # Any other character
        ]
        
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        tokens = []
        
        for mo in re.finditer(tok_regex, self.text):
            kind = mo.lastgroup
            value = mo.group()
            start_pos = Position(mo.start(), 0, mo.start())
            end_pos = Position(mo.end(), 0, mo.end())
            
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                return [], IllegalCharError(start_pos, end_pos, f"'{value}' is not a valid token")
            elif kind == 'INT':
                tokens.append(Token(TokenType.INT, int(value), start_pos, end_pos))
                    
        tokens.append(Token(TokenType.EOF, None, self.pos, self.pos))
        return tokens, None
```

The lexer defines regular expression patterns for each token type and uses Python's `re.finditer()` to iterate through all matches in the input text. Each match is converted to an appropriate token based on its pattern group. This implementation is highly efficient, as it leverages the power of regular expressions for pattern matching rather than manually parsing character by character.

The use of named capture groups (`(?P<name>pattern)`) makes the code more readable and allows for clear association between regex patterns and token types. Additionally, the inclusion of a catch-all pattern (`MISMATCH`) ensures that any invalid character is properly reported as an error.

### 6. AST Node Classes

The Abstract Syntax Tree is built using several node classes:

#### Base Node

```python
class Node:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
```

The base `Node` class provides position tracking for error reporting during parsing and potential future steps like interpretation or code generation.

#### Number Node

```python
class NumberNode(Node):
    def __init__(self, token):
        super().__init__(token.pos_start, token.pos_end)
        self.token = token
        
    def __repr__(self):
        return f'{self.token}'
```

`NumberNode` represents numeric literals (both integers and floating-point numbers). It stores the original token to preserve both the value and position information.

#### Binary Operation Node

```python
class BinaryOpNode(Node):
    def __init__(self, left_node, op_token, right_node):
        super().__init__(left_node.pos_start, right_node.pos_end)
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
        
    def __repr__(self):
        return f'({self.left_node} {self.op_token} {self.right_node})'
```

`BinaryOpNode` represents operations with two operands, such as addition, subtraction, multiplication, and division. It stores references to both operand nodes and the operator token. The position information spans from the start of the left operand to the end of the right operand, effectively covering the entire expression.

#### Unary Operation Node

```python
class UnaryOpNode(Node):
    def __init__(self, op_token, node):
        super().__init__(op_token.pos_start, node.pos_end)
        self.op_token = op_token
        self.node = node
        
    def __repr__(self):
        return f'({self.op_token} {self.node})'
```

`UnaryOpNode` handles unary operations like unary plus and minus (e.g., +5 or -3). It stores the operator token and the operand node.

#### Function Node

```python
class FunctionNode(Node):
    def __init__(self, func_token, arg_node):
        super().__init__(func_token.pos_start, arg_node.pos_end)
        self.func_token = func_token
        self.arg_node = arg_node
        
    def __repr__(self):
        return f'{self.func_token}({self.arg_node})'
```

`FunctionNode` represents function calls, such as sin(x) or cos(y). It stores the function token and the argument node. The position spans from the start of the function name to the end of the argument expression.

These AST node classes provide a flexible and hierarchical representation of the input expression, preserving both structure and position information for further processing.

### 7. Parser Implementation

The `Parser` class implements a recursive descent parser to build the AST:

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_token = None
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_token = self.tokens[self.tok_idx]
        return self.current_token

    def parse(self):
        if not self.tokens:
            return None, ParserError(
                Position(0, 0, 0), Position(0, 0, 0),
                "No tokens to parse"
            )
            
        result = self.expr()
        
        if self.current_token.type != TokenType.EOF:
            return None, ParserError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+', '-', '*', '/', '^'"
            )
            
        return result
```

The parser follows a carefully defined grammar to ensure correct operator precedence:

```
expr   : term ((PLUS|MINUS) term)*
term   : factor ((MUL|DIV) factor)*
factor : power ((POW) factor)*
power  : atom
atom   : INT|FLOAT|LPAREN expr RPAREN|function LPAREN expr RPAREN|(PLUS|MINUS) atom
function : COS|SIN|TG|CTG|LOG
```

Each grammar rule is implemented as a method in the Parser class:

```python
def expr(self):
    return self.bin_op(self.term, [TokenType.PLUS, TokenType.MINUS])
    
def term(self):
    return self.bin_op(self.factor, [TokenType.MUL, TokenType.DIV])
    
def factor(self):
    return self.bin_op(self.power, [TokenType.POW])
    
def power(self):
    return self.atom()
```

The recursive nature of these methods allows the parser to correctly handle nested expressions and ensure proper operator precedence. The `bin_op` helper method encapsulates the common pattern of binary operations:

```python
def bin_op(self, func, ops):
    left = func()
    
    if isinstance(left, tuple) and left[0] is None:
        return left
        
    while self.current_token.type in ops:
        op_token = self.current_token
        self.advance()
        right = func()
        
        if isinstance(right, tuple) and right[0] is None:
            return right
            
        left = BinaryOpNode(left, op_token, right)
        
    return left
```

The `atom` method handles the base cases of the grammar:

```python
def atom(self):
    token = self.current_token
    
    if token.type in (TokenType.INT, TokenType.FLOAT):
        self.advance()
        return NumberNode(token)
        
    elif token.type in (TokenType.COS, TokenType.SIN, TokenType.TG, TokenType.CTG, TokenType.LOG):
        # Function call parsing
        # ...
        
    elif token.type == TokenType.LPAREN:
        # Parenthesized expression parsing
        # ...
        
    elif token.type in (TokenType.PLUS, TokenType.MINUS):
        # Unary operation parsing
        # ...
        
    return None, ParserError(
        token.pos_start, token.pos_end,
        "Expected int, float, identifier, '+', '-', '('"
    )
```

The parser implementation carefully handles error conditions, ensuring that syntax errors are reported with precise position information. The recursive descent approach allows for clear and maintainable code that directly reflects the grammar rules.

### 8. AST Visualization

The `print_ast` function provides a visual representation of the AST:

```python
def print_ast(node, indent='', last=True):
    prefix = indent + ('└── ' if last else '├── ')
    
    if isinstance(node, NumberNode):
        print(prefix + f'Number({node.token.value})')
    elif isinstance(node, BinaryOpNode):
        print(prefix + f'Operation({node.op_token.type.name})')
        new_indent = indent + ('    ' if last else '│   ')
        print_ast(node.left_node, new_indent, False)
        print_ast(node.right_node, new_indent, True)
    elif isinstance(node, UnaryOpNode):
        print(prefix + f'UnaryOp({node.op_token.type.name})')
        new_indent = indent + ('    ' if last else '│   ')
        print_ast(node.node, new_indent, True)
    elif isinstance(node, FunctionNode):
        print(prefix + f'Function({node.func_token.type.name})')
        new_indent = indent + ('    ' if last else '│   ')
        print_ast(node.arg_node, new_indent, True)
    else:
        print(prefix + 'Unknown node')
```

This function recursively traverses the AST and prints each node with appropriate indentation and branch symbols, creating a tree-like visualization that makes the structure of the expression clear.

### 9. Main Program Loop

The `run` function combines the lexer and parser to process an expression:

```python
def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
        
    parser = Parser(tokens)
    ast = parser.parse()
    
    return ast, None
```

The `main` function provides a simple REPL (Read-Eval-Print Loop) for testing the parser:

```python
def main():
    while True:
        try:
            text = input("Enter an expression (or 'exit' to quit): ")
            
            if text.lower() == 'exit':
                print("Exiting program...")
                break
                
            result, error = run(text)
            
            if error:
                if isinstance(error, str):
                    print(error)
                else:
                    print(error.as_string())
            else:
                print("\nAbstract Syntax Tree:")
                print_ast(result)
                print()
                
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
```

This loop allows interactive testing of the parser with different expressions, displaying either the resulting AST or detailed error messages.

## Usage Examples

```
Enter an expression (or 'exit' to quit): sin(2) + 3 * cos(4-1)

Abstract Syntax Tree:
└── Operation(PLUS)
    ├── Function(SIN)
    │   └── Number(2)
    └── Operation(MUL)
        ├── Number(3)
        └── Function(COS)
            └── Operation(MINUS)
                ├── Number(4)
                └── Number(1)

Enter an expression (or 'exit' to quit): tg(5/7) - log(45) * 3^(8)

Abstract Syntax Tree:
└── Operation(MINUS)
    ├── Function(TG)
    │   └── Operation(DIV)
    │       ├── Number(5)
    │       └── Number(7)
    └── Operation(MUL)
        ├── Function(LOG)
        │   └── Number(45)
        └── Operation(POW)
            ├── Number(3)
            └── Number(8)
```

## Error Handling Examples

```
Enter an expression (or 'exit' to quit): 2 + * 3

Parser Error: Expected int, float, identifier, '+', '-', '('
At line 1, column 5

Enter an expression (or 'exit' to quit): sin(2

Parser Error: Expected ')'
At line 1, column 6
```

## Conclusion

This implementation demonstrates a complete lexer and parser for mathematical expressions, using standard techniques from compiler design. The code is structured in a way that clearly separates concerns: lexical analysis (tokenization), syntactic analysis (parsing), and abstract syntax tree representation. The use of regular expressions for token identification and recursive descent parsing for AST construction provides a clear and maintainable codebase that can be extended with additional features, such as new operators or functions.

The error reporting system provides detailed information about syntax errors, making it easier for users to correct their input. The visual representation of the AST helps in understanding the structure of expressions and how operator precedence rules are applied.

Overall, this project serves as a good foundation for building more complex language processors, such as interpreters or compilers for domain-specific languages.