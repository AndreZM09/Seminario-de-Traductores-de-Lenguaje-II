import re
import sys

# Token specification
token_specification = [
    ('NUMBER',      r"\d+(?:\.\d+)?"),
    ('ID',          r"[A-Za-z_][A-Za-z0-9_]*"),
    ('EQ',          r"=="),
    ('NE',          r"!="),
    ('LE',          r"<="),
    ('GE',          r">="),
    ('ASSIGN',      r"="),
    ('LT',          r"<"),
    ('GT',          r">"),
    ('PLUS',        r"\+"),
    ('MINUS',       r"-"),
    ('TIMES',       r"\*"),
    ('DIVIDE',      r"/"),
    ('LPAREN',      r"\("),
    ('RPAREN',      r"\)"),
    ('LBRACE',      r"\{"),
    ('RBRACE',      r"\}"),
    ('SEMI',        r";"),
    ('SKIP',        r"[ \t]+"),
    ('NEWLINE',     r"\n"),
    ('MISMATCH',    r".")
]

Token = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_specification))

class LexError(Exception):
    pass

class Lexer:
    def __init__(self, code):
        self.code = code
        self.line = 1
        self.col = 1
        self.tokens = []

    def tokenize(self):
        for mo in Token.finditer(self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                tok = ('NUMBER', float(value), self.line, self.col)
            elif kind == 'ID':
                if value in ('if','else','while','print'):
                    tok = (value.upper(), value, self.line, self.col)
                else:
                    tok = ('ID', value, self.line, self.col)
            elif kind == 'SKIP':
                self._advance(value)
                continue
            elif kind == 'NEWLINE':
                self.line += 1
                self.col = 1
                continue
            elif kind == 'MISMATCH':
                raise LexError(f"Unexpected character '{value}' at {self.line}:{self.col}")
            else:
                tok = (kind, value, self.line, self.col)
            self.tokens.append(tok)
            self._advance(value)
        self.tokens.append(('EOF', '', self.line, self.col))
        return self.tokens

    def _advance(self, text):
        lines = text.split('\n')
        if len(lines) > 1:
            self.line += len(lines) - 1
            self.col = len(lines[-1]) + 1
        else:
            self.col += len(text)

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0]

    def eat(self, kind):
        if self.current[0] == kind:
            self.pos += 1
            self.current = self.tokens[self.pos]
        else:
            raise ParseError(f"Expected {kind} at {self.current[2]}:{self.current[3]}, got {self.current[0]}")

    def parse(self):
        self.program()
        if self.current[0] != 'EOF':
            raise ParseError(f"Unexpected token {self.current[0]} after program end")
        print("Parse successful.")

    def program(self):
        while self.current[0] != 'EOF':
            self.statement()

    def statement(self):
        if self.current[0] == 'ID':
            self.assignment()
        elif self.current[0] == 'IF':
            self.if_stmt()
        elif self.current[0] == 'WHILE':
            self.while_stmt()
        elif self.current[0] == 'PRINT':
            self.print_stmt()
        else:
            raise ParseError(f"Invalid statement start: {self.current[0]} at {self.current[2]}:{self.current[3]}")

    def assignment(self):
        self.eat('ID')
        self.eat('ASSIGN')
        self.expression()
        self.eat('SEMI')

    def if_stmt(self):
        self.eat('IF')
        self.eat('LPAREN')
        self.expression()
        self.eat('RPAREN')
        self.block()
        if self.current[0] == 'ELSE':
            self.eat('ELSE')
            self.block()

    def while_stmt(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        self.expression()
        self.eat('RPAREN')
        self.block()

    def print_stmt(self):
        self.eat('PRINT')
        self.eat('LPAREN')
        self.expression()
        self.eat('RPAREN')
        self.eat('SEMI')

    def block(self):
        self.eat('LBRACE')
        while self.current[0] not in ('RBRACE','EOF'):
            self.statement()
        self.eat('RBRACE')

    def expression(self):
        self.equality()

    def equality(self):
        self.comparison()
        while self.current[0] in ('EQ','NE'):
            self.eat(self.current[0])
            self.comparison()

    def comparison(self):
        self.term()
        while self.current[0] in ('LT','LE','GT','GE'):
            self.eat(self.current[0])
            self.term()

    def term(self):
        self.factor()
        while self.current[0] in ('PLUS','MINUS'):
            self.eat(self.current[0])
            self.factor()

    def factor(self):
        self.unary()
        while self.current[0] in ('TIMES','DIVIDE'):
            self.eat(self.current[0])
            self.unary()

    def unary(self):
        if self.current[0] == 'MINUS':
            self.eat('MINUS')
        self.primary()

    def primary(self):
        if self.current[0] == 'NUMBER':
            self.eat('NUMBER')
        elif self.current[0] == 'ID':
            self.eat('ID')
        elif self.current[0] == 'LPAREN':
            self.eat('LPAREN')
            self.expression()
            self.eat('RPAREN')
        else:
            raise ParseError(f"Unexpected token {self.current[0]} in expression at {self.current[2]}:{self.current[3]}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python lexer_parser.py <sourcefile>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print("Tokens:")
        for t in tokens:
            print(t)
        parser = Parser(tokens)
        parser.parse()
    except (LexError, ParseError) as e:
        print(f"Error: {e}")
        sys.exit(1)
