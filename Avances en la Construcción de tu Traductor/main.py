#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

# ====================================================
# ANALIZADOR LÉXICO
# ====================================================

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

    PALABRAS_RESERVADAS = {
        "if": IF,
        "while": WHILE,
        "return": RETURN,
        "else": ELSE,
        "int": TIPO,
        "float": TIPO,
        "void": TIPO
    }

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
                        # Reportar error léxico: punto sin dígito
                        print(f"Error léxico: Se encontró un punto sin dígito tras el número en '{self.simbolo}'")
                        return None
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

        # Token no válido: Reportar error léxico
        print(f"Error léxico: Carácter no válido '{c}'")
        self.simbolo = c
        self.tipo = None
        return None

    def terminado(self):
        return self.ind >= len(self.fuente)


# ====================================================
# ANALIZADOR SINTÁCTICO (Parser LR)
# ====================================================

class ElementoPila:
    def muestra(self):
        raise NotImplementedError("Debe implementarse en la subclase.")

class Terminal(ElementoPila):
    def __init__(self, tipo, lexema):
        self.tipo = tipo
        self.lexema = lexema
    def muestra(self):
        print(f"Terminal({self.lexema})", end=' ')
    def get_tipo(self):
        return self.tipo

class NoTerminal(ElementoPila):
    def __init__(self, simbolo, nombre):
        self.simbolo = simbolo
        self.nombre = nombre
    def muestra(self):
        print(f"NoTerminal({self.nombre})", end=' ')
    def get_simbolo(self):
        return self.simbolo

class Estado(ElementoPila):
    def __init__(self, numero):
        self.numero = numero
    def muestra(self):
        print(f"Estado({self.numero})", end=' ')
    def get_numero(self):
        return self.numero

class Pila:
    def __init__(self):
        self.lista = []
    def push(self, elemento):
        self.lista.append(elemento)
    def pop(self):
        if not self.empty():
            return self.lista.pop()
        return None
    def top(self):
        if not self.empty():
            return self.lista[-1]
        return None
    def empty(self):
        return len(self.lista) == 0
    def muestra(self):
        print("Contenido de la pila (base -> tope):")
        for elem in self.lista:
            elem.muestra()
        print("\n")

reglas = [
    (3, 3, "E"),  # Regla 0: E -> id + E
    (3, 1, "E"),  # Regla 1: E -> id
]
tabla = {
    (0, 0): ('s', 2),   # En estado 0, con token 'id' (0): shift al estado 2.
    (0, 3): ('g', 1),   # En estado 0, con no terminal E (3): goto estado 1.
    (1, 1): ('r', 1),   # En estado 1, con token '+' (1): reduce por regla 1: E -> id.
    (1, 2): ('acc',),   # En estado 1, con token '$' (2): accept.
    (2, 1): ('s', 3),   # En estado 2, con token '+' (1): shift al estado 3.
    (2, 2): ('r', 1),   # En estado 2, con token '$' (2): reduce por regla 1.
    (3, 0): ('s', 2),   # En estado 3, con token 'id' (0): shift al estado 2.
    (3, 3): ('g', 4),   # En estado 3, con no terminal E (3): goto estado 4.
    (4, 1): ('r', 0),   # En estado 4, con token '+' (1): reduce por regla 0: E -> id + E.
    (4, 2): ('r', 0),   # En estado 4, con token '$' (2): reduce por regla 0.
}

def lexico_rapido(cadena):
    tokens = []
    partes = re.split(r'\s+', cadena.strip())
    for p in partes:
        if p == '+':
            tokens.append((1, '+'))
        elif p == '$':
            tokens.append((2, '$'))
        else:
            tokens.append((0, p))  # Todo lo demás se considera 'id'
    return tokens

def analizar(tokens):
    stack = Pila()
    stack.push(Estado(0))
    i = 0
    while True:
        top_elem = stack.top()
        if not top_elem:
            print("Error: la pila está vacía.")
            return False
        if not isinstance(top_elem, Estado):
            print("Error: el tope de la pila no es un Estado.")
            return False
        estado_actual = top_elem.get_numero()
        if i >= len(tokens):
            print("No hay más tokens, se esperaba '$'.")
            return False
        tipo_token, lexema_token = tokens[i]
        if (estado_actual, tipo_token) not in tabla:
            print(f"Error: no hay acción para estado {estado_actual} con token '{lexema_token}'")
            return False
        accion = tabla[(estado_actual, tipo_token)]
        stack.muestra()
        print(f"Token actual: {lexema_token} (tipo={tipo_token})")
        print(f"Acción: {accion}\n")
        if accion[0] == 's':
            estado_destino = accion[1]
            stack.push(Terminal(tipo_token, lexema_token))
            stack.push(Estado(estado_destino))
            i += 1
        elif accion[0] == 'r':
            num_regla = accion[1]
            lhs, rhs_len, lhs_nombre = reglas[num_regla]
            for _ in range(rhs_len):
                stack.pop()  # Quitar estado
                stack.pop()  # Quitar símbolo
            top_state = stack.top()
            if not isinstance(top_state, Estado):
                print("Error: tras la reducción el tope no es un Estado.")
                return False
            nuevo_estado = top_state.get_numero()
            if (nuevo_estado, lhs) not in tabla:
                print(f"Error: no hay goto para estado {nuevo_estado} con símbolo {lhs_nombre}")
                return False
            goto_accion = tabla[(nuevo_estado, lhs)]
            if goto_accion[0] != 'g':
                print("Error: se esperaba 'g' tras una reducción.")
                return False
            estado_destino = goto_accion[1]
            stack.push(NoTerminal(lhs, lhs_nombre))
            stack.push(Estado(estado_destino))
        elif accion[0] == 'acc':
            print("¡Cadena aceptada correctamente!\n")
            return True
        else:
            print(f"Acción desconocida: {accion}")
            return False

def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                fuente = f.read().strip()
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return
    else:
        fuente = "if x < 10 { x = x + 1; } $"
    print("=== Fuente a analizar ===")
    print(fuente, "\n")
    # Uso del analizador léxico:
    lexico_instance = Lexico(fuente)
    tokens = []
    while not lexico_instance.terminado():
        t = lexico_instance.sig_simbolo()
        if t is None:
            print(f"Token no reconocido: '{lexico_instance.simbolo}'")
            break
        tokens.append((t, lexico_instance.simbolo))
    print("=== Tokens generados por el analizador léxico ===")
    for tok in tokens:
        print(tok)
    print("")
    # Uso del parser LR:
    print("=== Análisis sintáctico LR ===")
    resultado = analizar(tokens)
    print(f"Resultado final: {'ACEPTADO' if resultado else 'RECHAZADO'}")

if __name__ == "__main__":
    main()
