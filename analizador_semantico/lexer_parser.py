#!/usr/bin/env python3
import re, sys

# ----------------------------
# Semantic Analyzer Classes
# ----------------------------
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]    # stack of dict: name -> (kind, type, param_types)
        self.errors = []

    def enter_scope(self, name):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    @property
    def current_scope(self):
        return self.scopes[-1]

    def declare_var(self, name, vtype):
        if name in self.current_scope:
            self.errors.append(
                f"Error: redefinición de variable '{name}' en ámbito '{Node.ambito}'."
            )
        else:
            self.current_scope[name] = ("var", vtype)

    def declare_func(self, name, return_type, param_types):
        global_scope = self.scopes[0]
        if name in global_scope:
            self.errors.append(
                f"Error: redefinición de función '{name}'."
            )
        else:
            global_scope[name] = ("func", return_type, param_types)

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class Node:
    tabla_simbolos = None
    ambito = ''

    def validate_types(self):
        raise NotImplementedError

class ProgramNode(Node):
    def __init__(self, decls):
        self.decls = decls

    def validate_types(self):
        for d in self.decls:
            d.validate_types()

class VarDeclNode(Node):
    def __init__(self, vtype, name):
        self.vtype = vtype
        self.name = name

    def validate_types(self):
        Node.tabla_simbolos.declare_var(self.name, self.vtype)

class ParamNode(Node):
    def __init__(self, name, ptype):
        self.name = name
        self.ptype = ptype

    def validate_types(self):
        Node.tabla_simbolos.declare_var(self.name, self.ptype)

class FuncDeclNode(Node):
    def __init__(self, rtype, name, params, body):
        self.return_type = rtype
        self.name = name
        self.params = params
        self.body = body

    def validate_types(self):
        param_types = [p.ptype for p in self.params]
        Node.tabla_simbolos.declare_func(self.name, self.return_type, param_types)
        Node.tabla_simbolos.enter_scope(self.name)
        prev = Node.ambito
        Node.ambito = self.name
        for p in self.params:
            p.validate_types()
        for stmt in self.body:
            stmt.validate_types()
        Node.tabla_simbolos.exit_scope()
        Node.ambito = prev

class AssignNode(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def validate_types(self):
        info = Node.tabla_simbolos.lookup(self.name)
        if not info or info[0] != 'var':
            Node.tabla_simbolos.errors.append(
                f"Error: variable '{self.name}' no declarada."
            )
            return
        var_type = info[1]
        expr_type = self.expr.validate_types()

        # Permitir int ⇄ float sin error:
        numeric = {'int','float'}
        if var_type in numeric and expr_type in numeric:
            return

        # En los demás casos, si no coinciden, error:
        if expr_type and expr_type != var_type:
            Node.tabla_simbolos.errors.append(
                f"Error: asignación de '{expr_type}' a '{var_type}' en '{self.name}'."
            )


class ReturnNode(Node):
    def __init__(self, expr):
        self.expr = expr

    def validate_types(self):
        expr_type = self.expr.validate_types()
        func_info = Node.tabla_simbolos.lookup(Node.ambito)
        if func_info and func_info[0] == 'func':
            rtype = func_info[1]
            if expr_type and expr_type != rtype:
                Node.tabla_simbolos.errors.append(
                    f"Error: return '{expr_type}' no coincide con '{rtype}' en función '{Node.ambito}'."
                )
        return expr_type

class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def validate_types(self):
        lt = self.left.validate_types()
        rt = self.right.validate_types()
        # Si ambos son numéricos (int o float), permitimos mezcla:
        numeric = {'int', 'float'}
        if lt in numeric and rt in numeric:
            # resultado float si alguno es float
            return 'float' if 'float' in (lt, rt) else 'int'
        # Si son iguales y no numéricos, se comporta igual:
        if lt and rt and lt == rt:
            return lt
        # En cualquier otro caso, es un error:
        if lt is not None and rt is not None:
            Node.tabla_simbolos.errors.append(
                f"Error: mezcla de tipos '{lt}' y '{rt}' en operación '{self.op}'."
            )
        return None

class FuncCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def validate_types(self):
        info = Node.tabla_simbolos.lookup(self.name)
        # Si la función no está declarada, ahora sí reportamos error
        if not info or info[0] != 'func':
            Node.tabla_simbolos.errors.append(
                f"Error: función '{self.name}' no declarada."
            )
            return None
        # Si existe, comprobamos parámetros
        _, rtype, ptypes = info
        if len(ptypes) != len(self.args):
            Node.tabla_simbolos.errors.append(
                f"Error: '{self.name}' espera {len(ptypes)} args, recibió {len(self.args)}."
            )
        for expected, arg in zip(ptypes, self.args):
            at = arg.validate_types()
            if at and at != expected:
                Node.tabla_simbolos.errors.append(
                    f"Error: paso '{at}' donde se espera '{expected}' en '{self.name}'."
                )
        return rtype

class NumberNode(Node):
    def __init__(self, value):
        self.value = value
        self.ntype = 'float' if isinstance(value, float) else 'int'

    def validate_types(self):
        return self.ntype

class IdentifierNode(Node):
    def __init__(self, name):
        self.name = name

    def validate_types(self):
        info = Node.tabla_simbolos.lookup(self.name)
        if not info:
            Node.tabla_simbolos.errors.append(
                f"Error: identificador '{self.name}' no declarado."
            )
            return None
        if info[0] == 'var':
            return info[1]
        return None

# ----------------------------
# Lexer
# ----------------------------
token_spec = [
    ('NUMBER',  r"\d+\.\d+|\d+"),
    ('ID',      r"[A-Za-z_][A-Za-z0-9_]*"),
    ('ASSIGN',  r"="),
    ('LPAREN',  r"\("),
    ('RPAREN',  r"\)"),
    ('LBRACE',  r"\{"),
    ('RBRACE',  r"\}"),
    ('SEMI',    r";"),
    ('COMMA',   r","),
    ('PLUS',    r"\+"), ('MINUS', r"-"),
    ('TIMES',   r"\*"), ('DIVIDE',r"/"),
    ('LT',      r"<"), ('LE', r"<="),
    ('GT',      r">"), ('GE', r">="),
    ('EQ',      r"=="),('NE', r"!="),
    ('SKIP',    r"[ \t\r\n]+"),
    ('MISMATCH',r"."),
]
tok_regex = re.compile("|".join(f"(?P<{n}>{r})" for n,r in token_spec))

class LexError(Exception): pass

class Lexer:
    def __init__(self, code):
        self.code = code
    def tokenize(self):
        tokens = []
        for mo in tok_regex.finditer(self.code):
            kind, val = mo.lastgroup, mo.group()
            if kind == 'SKIP': continue
            if kind == 'MISMATCH': raise LexError(f"Unexpected '{val}'")
            if kind == 'NUMBER':
                val = float(val) if '.' in val else int(val)
            tokens.append((kind,val))
        tokens.append(('EOF',None))
        return tokens

# ----------------------------
# Parser (recursive descent)
# ----------------------------
class ParseError(Exception): pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos=0; self.cur=tokens[0]
    def eat(self,kind):
        if self.cur[0]==kind:
            self.pos+=1; self.cur=self.tokens[self.pos]
        else:
            raise ParseError(f"Esperaba {kind}, hallado {self.cur[0]}")
    def parse(self):
        decls=[] 
        while self.cur[0]!='EOF':
            if self.cur[0]=='ID' and self.cur[1] in ('int','float'):
                rtype=self.cur[1]; self.eat('ID')
                name=self.cur[1]; self.eat('ID')
                if self.cur[0]=='LPAREN':
                    self.eat('LPAREN'); params=[]
                    while self.cur[0]!='RPAREN':
                        ptype=self.cur[1]; self.eat('ID')
                        pname=self.cur[1]; self.eat('ID')
                        params.append(ParamNode(pname,ptype))
                        if self.cur[0]=='COMMA': self.eat('COMMA')
                    self.eat('RPAREN'); self.eat('LBRACE')
                    body=[]
                    while self.cur[0]!='RBRACE':
                        body.append(self.statement())
                    self.eat('RBRACE')
                    decls.append(FuncDeclNode(rtype,name,params,body))
                else:
                    self.eat('SEMI')
                    decls.append(VarDeclNode(rtype,name))
            else:
                decls.append(self.statement())
        return ProgramNode(decls)

    def statement(self):
        # --- Declaración de variable (local o global) ---
        if self.cur[0]=='ID' and self.cur[1] in ('int','float'):
            # tipo y nombre
            vtype = self.cur[1]; self.eat('ID')
            name  = self.cur[1]; self.eat('ID')
            self.eat('SEMI')
            return VarDeclNode(vtype, name)

        # --- Return ---
        if self.cur[0]=='ID' and self.cur[1]=='return':
            self.eat('ID')
            expr = self.expr()
            self.eat('SEMI')
            return ReturnNode(expr)

        # --- Asignación ---
        if self.cur[0]=='ID':
            name = self.cur[1]; self.eat('ID')
            if self.cur[0]=='ASSIGN':
                self.eat('ASSIGN')
                expr = self.expr()
                self.eat('SEMI')
                return AssignNode(name, expr)
            if self.cur[0]=='LPAREN':
                node = FuncCallNode(name, self.call_args())
                self.eat('SEMI')
                return node

        raise ParseError(f"Sent inválida {self.cur}")


    def call_args(self):
        args=[]; self.eat('LPAREN')
        while self.cur[0]!='RPAREN':
            args.append(self.expr())
            if self.cur[0]=='COMMA': self.eat('COMMA')
        self.eat('RPAREN'); return args

    def expr(self): return self.equality()
    def equality(self):
        node=self.comparison()
        while self.cur[0] in ('EQ','NE'):
            op=self.cur[0]; self.eat(op)
            node=BinaryOpNode(node,op,self.comparison())
        return node
    def comparison(self):
        node=self.term()
        while self.cur[0] in ('LT','LE','GT','GE'):
            op=self.cur[0]; self.eat(op)
            node=BinaryOpNode(node,op,self.term())
        return node
    def term(self):
        node=self.factor()
        while self.cur[0] in ('PLUS','MINUS'):
            op=self.cur[0]; self.eat(op)
            node=BinaryOpNode(node,op,self.factor())
        return node
    def factor(self):
        node=self.primary()
        while self.cur[0] in ('TIMES','DIVIDE'):
            op=self.cur[0]; self.eat(op)
            node=BinaryOpNode(node,op,self.primary())
        return node
    def primary(self):
        if self.cur[0]=='NUMBER':
            val=self.cur[1]; self.eat('NUMBER')
            return NumberNode(val)
        if self.cur[0]=='ID':
            name=self.cur[1]; self.eat('ID')
            if self.cur[0]=='LPAREN':
                return FuncCallNode(name,self.call_args())
            return IdentifierNode(name)
        if self.cur[0]=='LPAREN':
            self.eat('LPAREN'); node=self.expr(); self.eat('RPAREN')
            return node
        raise ParseError(f"Primario inválido {self.cur}")

# ------------------------------------------------
# Main: léxico → sintaxis → semántica (archivo fijo)
# ------------------------------------------------

# Aquí indica el archivo que se va a procesar:
SOURCE_FILE = "ejemplo2.src"   # Cámbialo por el que quieras

if __name__ == '__main__':
    # 1) Leer directamente el fichero configurado arriba
    try:
        with open(SOURCE_FILE, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: no existe el archivo '{SOURCE_FILE}'")
        sys.exit(1)

    try:
        # 2) Léxico
        tokens = Lexer(code).tokenize()
        # 3) Sintaxis (AST)
        ast = Parser(tokens).parse()

        # 4) Análisis semántico
        Node.tabla_simbolos = SymbolTable()
        Node.ambito        = ''
        ast.validate_types()

        # 5) Reporte de errores
        if Node.tabla_simbolos.errors:
            for e in Node.tabla_simbolos.errors:
                print(e)
            sys.exit(1)
        else:
            print("¡Análisis semántico sin errores!")
            sys.exit(0)

    except (LexError, ParseError) as e:
        print(f"Error: {e}")
        sys.exit(1)
