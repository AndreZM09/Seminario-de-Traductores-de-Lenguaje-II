import re

class TokenType:
    IDENTIFICADOR = 0
    ENTERO = 1
    REAL = 2
    CADENA = 3
    TIPO = 4  # int, float, void
    OP_SUMA = 5  # +, -
    OP_MUL = 6  # *, /
    OP_RELAC = 7  # <, <=, >, >=
    OP_OR = 8  # ||
    OP_AND = 9  # &&
    OP_NOT = 10  # !
    OP_IGUALDAD = 11  # ==, !=
    PUNTO_Y_COMA = 12  # ;
    COMA = 13  # ,
    PARENTESIS_ABRE = 14  # (
    PARENTESIS_CIERRA = 15  # )
    LLAVE_ABRE = 16  # {
    LLAVE_CIERRA = 17  # }
    ASIGNACION = 18  # =
    IF = 19
    WHILE = 20
    RETURN = 21
    ELSE = 22
    FIN = 23  # $

    PALABRAS_RESERVADAS = {"if": IF, "while": WHILE, "return": RETURN, "else": ELSE, "int": TIPO, "float": TIPO}

class Lexico:
    def __init__(self, fuente=""):
        self.fuente = fuente
        self.ind = 0
        self.simbolo = ""
        self.tipo = None
    
    def entrada(self, fuente):
        self.fuente = fuente
        self.ind = 0
    
    def sig_caracter(self):
        if self.terminado():
            return '$'
        c = self.fuente[self.ind]
        self.ind += 1
        return c
    
    def retroceso(self):
        if self.ind > 0:
            self.ind -= 1
    
    def sig_simbolo(self):
        self.simbolo = ""
        c = self.sig_caracter()
        
        # Ignorar espacios en blanco
        while c.isspace():
            c = self.sig_caracter()
        
        # Identificadores o palabras reservadas
        if c.isalpha():
            self.simbolo += c
            while not self.terminado():
                c = self.sig_caracter()
                if c.isalnum():
                    self.simbolo += c
                else:
                    self.retroceso()
                    break
            self.tipo = TokenType.PALABRAS_RESERVADAS.get(self.simbolo, TokenType.IDENTIFICADOR)
            return self.tipo
        
        # Números enteros y reales
        elif c.isdigit():
            self.simbolo += c
            while not self.terminado():
                c = self.sig_caracter()
                if c.isdigit():
                    self.simbolo += c
                elif c == '.':
                    self.simbolo += c
                    c = self.sig_caracter()
                    if c.isdigit():
                        self.simbolo += c
                        while not self.terminado():
                            c = self.sig_caracter()
                            if c.isdigit():
                                self.simbolo += c
                            else:
                                self.retroceso()
                                break
                        self.tipo = TokenType.REAL
                        return self.tipo
                    else:
                        self.retroceso()
                        break
                else:
                    self.retroceso()
                    break
            self.tipo = TokenType.ENTERO
            return self.tipo
        
        # Operadores y símbolos especiales
        operadores = {
            '+': TokenType.OP_SUMA, '-': TokenType.OP_SUMA,
            '*': TokenType.OP_MUL, '/': TokenType.OP_MUL,
            '=': TokenType.ASIGNACION, ';': TokenType.PUNTO_Y_COMA,
            ',': TokenType.COMA, '(': TokenType.PARENTESIS_ABRE, ')': TokenType.PARENTESIS_CIERRA,
            '{': TokenType.LLAVE_ABRE, '}': TokenType.LLAVE_CIERRA,
            '!': TokenType.OP_NOT, '<': TokenType.OP_RELAC, '>': TokenType.OP_RELAC
        }

        if c in operadores:
            self.simbolo = c
            if c in ('<', '>', '!', '='):
                c2 = self.sig_caracter()
                if c2 == '=':
                    self.simbolo += c2
                    self.tipo = TokenType.OP_IGUALDAD if c in ('!', '=') else TokenType.OP_RELAC
                    return self.tipo
                else:
                    self.retroceso()
            self.tipo = operadores[c]
            return self.tipo
        
        # Operadores lógicos
        if c == '&' and self.sig_caracter() == '&':
            self.simbolo = '&&'
            self.tipo = TokenType.OP_AND
            return self.tipo
        if c == '|' and self.sig_caracter() == '|':
            self.simbolo = '||'
            self.tipo = TokenType.OP_OR
            return self.tipo
        
        # Fin de la entrada
        if c == '$':
            self.simbolo = c
            self.tipo = TokenType.FIN
            return self.tipo
        
        # Si no es un token válido
        self.simbolo = c
        self.tipo = None
        return None
    
    def terminado(self):
        return self.ind >= len(self.fuente)
    
    def tipo_acad(self, tipo):
        return tipo

# Prueba del analizador léxico
if __name__ == "__main__":
    lexico = Lexico("if x >= 10 { return 3.14; }")
    
    print("Resultado del Análisis Léxico:\n")
    print("Simbolo\t\tTipo")
    
    while not lexico.terminado():
        tipo = lexico.sig_simbolo()
        if tipo is not None:
            print(f"{lexico.simbolo}\t\t{lexico.tipo_acad(tipo)}")
