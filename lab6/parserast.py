import re
from enum import Enum, auto


class TokenType(Enum):
    INT = auto()  # Integer number
    FLOAT = auto()  # Float number
    PLUS = auto()  # +
    MINUS = auto()  # -
    MUL = auto()  # *
    DIV = auto()  # /
    POW = auto()  # ^
    LOG = auto()  # log
    COS = auto()  # cos
    SIN = auto()  # sin
    TG = auto()  # tg
    CTG = auto()  # ctg
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    EOF = auto()  # End of file


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        if self.value is not None:
            return f'{self.type.name}:{self.value}'
        return f'{self.type.name}'


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        return f"{self.error_name}: {self.details}\n" \
               f"At line {self.pos_start.line_nr + 1}, column {self.pos_start.column_nr + 1}"


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class UnknownFunctionError(Error):
    def __init__(self, pos_start, pos_end, function_name):
        super().__init__(pos_start, pos_end, 'Unknown Function',
                         f"'{function_name}' is not a recognized function")


class ParserError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Parser Error', details)


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


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(0, 0, 0)

    def make_tokens(self):
        token_specification = [
            ('FLOAT', r'\d+\.\d+'),  # Float numbers
            ('INT', r'\d+'),  # Integer numbers
            ('PLUS', r'\+'),  # Addition operator
            ('MINUS', r'-'),  # Subtraction operator
            ('MUL', r'\*'),  # Multiplication operator
            ('DIV', r'/'),  # Division operator
            ('POW', r'\^'),  # Power operator
            ('LPAREN', r'\('),  # Left parenthesis
            ('RPAREN', r'\)'),  # Right parenthesis
            ('FUNCTION', r'(cos|sin|tg|ctg|log)'),  # Mathematical functions
            ('SKIP', r'[ \t\n]+'),  # Skip over spaces and tabs
            ('MISMATCH', r'.'),  # Any other character
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
            elif kind == 'FLOAT':
                tokens.append(Token(TokenType.FLOAT, float(value), start_pos, end_pos))
            elif kind == 'PLUS':
                tokens.append(Token(TokenType.PLUS, None, start_pos, end_pos))
            elif kind == 'MINUS':
                tokens.append(Token(TokenType.MINUS, None, start_pos, end_pos))
            elif kind == 'MUL':
                tokens.append(Token(TokenType.MUL, None, start_pos, end_pos))
            elif kind == 'DIV':
                tokens.append(Token(TokenType.DIV, None, start_pos, end_pos))
            elif kind == 'POW':
                tokens.append(Token(TokenType.POW, None, start_pos, end_pos))
            elif kind == 'LPAREN':
                tokens.append(Token(TokenType.LPAREN, None, start_pos, end_pos))
            elif kind == 'RPAREN':
                tokens.append(Token(TokenType.RPAREN, None, start_pos, end_pos))
            elif kind == 'FUNCTION':
                if value.lower() == 'cos':
                    tokens.append(Token(TokenType.COS, None, start_pos, end_pos))
                elif value.lower() == 'sin':
                    tokens.append(Token(TokenType.SIN, None, start_pos, end_pos))
                elif value.lower() == 'tg':
                    tokens.append(Token(TokenType.TG, None, start_pos, end_pos))
                elif value.lower() == 'ctg':
                    tokens.append(Token(TokenType.CTG, None, start_pos, end_pos))
                elif value.lower() == 'log':
                    tokens.append(Token(TokenType.LOG, None, start_pos, end_pos))

        tokens.append(Token(TokenType.EOF, None, self.pos, self.pos))
        return tokens, None


class Node:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class NumberNode(Node):
    def __init__(self, token):
        super().__init__(token.pos_start, token.pos_end)
        self.token = token

    def __repr__(self):
        return f'{self.token}'


class BinaryOpNode(Node):
    def __init__(self, left_node, op_token, right_node):
        super().__init__(left_node.pos_start, right_node.pos_end)
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node} {self.op_token} {self.right_node})'


class UnaryOpNode(Node):
    def __init__(self, op_token, node):
        super().__init__(op_token.pos_start, node.pos_end)
        self.op_token = op_token
        self.node = node

    def __repr__(self):
        return f'({self.op_token} {self.node})'


class FunctionNode(Node):
    def __init__(self, func_token, arg_node):
        super().__init__(func_token.pos_start, arg_node.pos_end)
        self.func_token = func_token
        self.arg_node = arg_node

    def __repr__(self):
        return f'{self.func_token}({self.arg_node})'


# 3. Parser implementation
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


    def expr(self):
        return self.bin_op(self.term, [TokenType.PLUS, TokenType.MINUS])

    def term(self):
        return self.bin_op(self.factor, [TokenType.MUL, TokenType.DIV])

    def factor(self):
        return self.bin_op(self.power, [TokenType.POW])

    def power(self):
        return self.atom()

    def atom(self):
        token = self.current_token

        if token.type in (TokenType.INT, TokenType.FLOAT):
            self.advance()
            return NumberNode(token)

        elif token.type in (TokenType.COS, TokenType.SIN, TokenType.TG, TokenType.CTG, TokenType.LOG):
            func_token = token
            self.advance()

            if self.current_token.type != TokenType.LPAREN:
                return None, ParserError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '('"
                )

            self.advance()
            expr = self.expr()

            if self.current_token.type != TokenType.RPAREN:
                return None, ParserError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                )

            self.advance()
            return FunctionNode(func_token, expr)

        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.expr()

            if self.current_token.type != TokenType.RPAREN:
                return None, ParserError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                )

            self.advance()
            return expr

        elif token.type in (TokenType.PLUS, TokenType.MINUS):
            self.advance()
            atom = self.atom()

            return UnaryOpNode(token, atom)

        return None, ParserError(
            token.pos_start, token.pos_end,
            "Expected int, float, identifier, '+', '-', '('"
        )

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


def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast, None


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


if __name__ == "__main__":
    main()