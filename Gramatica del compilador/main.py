#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# ====================================================
# 1) DEFINICIÓN DE LOS TOKENS SEGÚN compilador.inf
# ====================================================
class TokenType:
    identificador = 0
    entero = 1
    real = 2
    cadena = 3
    tipo = 4
    opSuma = 5
    opMul = 6
    opRelac = 7
    opOr = 8
    opAnd = 9
    opNot = 10
    opIgualdad = 11
    PYC = 12      # ;
    COMA = 13     # ,
    PA = 14       # (
    PC = 15       # )
    LLA = 16      # {
    LLC = 17      # }
    ASIG = 18     # =
    IF = 19
    WHILE = 20
    RETURN = 21
    ELSE = 22
    FIN = 23      # $

    PALABRAS_RESERVADAS = {
        "if": IF,
        "while": WHILE,
        "return": RETURN,
        "else": ELSE,
        "int": tipo,
        "float": tipo,
        "void": tipo
    }

# ====================================================
# 2) ANALIZADOR LÉXICO
# ====================================================
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
            self.tipo = TokenType.PALABRAS_RESERVADAS.get(self.simbolo, TokenType.identificador)
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
                        self.tipo = TokenType.real
                        return self.tipo
                    else:
                        self.retroceso()
                        break
                else:
                    self.retroceso()
                    break
            self.tipo = TokenType.entero
            return self.tipo

        # Operadores y símbolos especiales
        # Se asume que cada operador es de un solo carácter (salvo para los compuestos, que se gestionan a continuación)
        operadores = {
            '+': TokenType.opSuma, '-': TokenType.opSuma,
            '*': TokenType.opMul, '/': TokenType.opMul,
            ';': TokenType.PYC, ',': TokenType.COMA,
            '(': TokenType.PA, ')': TokenType.PC,
            '{': TokenType.LLA, '}': TokenType.LLC,
            '=': TokenType.ASIG,
            '!': TokenType.opNot, '<': TokenType.opRelac, '>': TokenType.opRelac
        }
        if c in operadores:
            self.simbolo = c
            # Para compuestos: ==, !=, <=, >=
            if c in ('<', '>', '!', '='):
                c2 = self.sig_caracter()
                if c2 == '=':
                    self.simbolo += c2
                    if self.simbolo in ('==', '!='):
                        self.tipo = TokenType.opIgualdad
                    else:
                        self.tipo = TokenType.opRelac
                    return self.tipo
                else:
                    self.retroceso()
            self.tipo = operadores[c]
            return self.tipo

        # Operadores lógicos && y ||
        if c == '&':
            c2 = self.sig_caracter()
            if c2 == '&':
                self.simbolo = '&&'
                self.tipo = TokenType.opAnd
                return self.tipo
            else:
                self.retroceso()
        if c == '|':
            c2 = self.sig_caracter()
            if c2 == '|':
                self.simbolo = '||'
                self.tipo = TokenType.opOr
                return self.tipo
            else:
                self.retroceso()

        # Fin de la entrada
        if c == '$':
            self.simbolo = c
            self.tipo = TokenType.FIN
            return self.tipo

        # Si no es token válido
        self.simbolo = c
        self.tipo = None
        return None

    def terminado(self):
        return self.ind >= len(self.fuente)


# ====================================================
# 3) LECTURA DEL ARCHIVO LR (compilador.lr)
# ====================================================
def leer_lr_file(filename):
    """
    Lee el archivo LR con el siguiente formato:
    1) Número de reglas (entero).
    2) Por cada regla: <id_no_terminal> <longitud> <nombre_no_terminal>
    3) Una línea con: <num_filas> <num_cols>
    4) <num_filas> líneas, cada una con <num_cols> enteros (la tabla LR)
    
    Retorna:
      - rules: lista de tuplas (nt_id, longitud, nt_name)
      - num_rows, num_cols
      - table: matriz (lista de listas de enteros)
    """
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    num_rules = int(lines[0])
    rules = []
    idx = 1
    for _ in range(num_rules):
        parts = lines[idx].split()
        idx += 1
        nt_id = int(parts[0])
        lon = int(parts[1])
        nt_name = parts[2]
        rules.append((nt_id, lon, nt_name))
    
    dims = lines[idx].split()
    idx += 1
    num_rows = int(dims[0])
    num_cols = int(dims[1])
    
    table = []
    for _ in range(num_rows):
        row_vals = [int(x) for x in lines[idx].split()]
        idx += 1
        table.append(row_vals)
    
    return rules, num_rows, num_cols, table


# ====================================================
# 4) PARSER LR (PILA DE ENTEROS)
# ====================================================
def parser_lr(tokens, rules, table):
    """
    :param tokens: lista de tokens en forma (tipo, lexema)
    :param rules: lista de reglas leídas del archivo LR (nt_id, lon, nt_name)
    :param table: la tabla LR (matriz de enteros)
    :return: True si se acepta la cadena, False en caso de error.
    
    Se utiliza la convención:
      - Si la celda contiene un número positivo: SHIFT a ese estado.
      - Si contiene un número negativo: REDUCE por la regla (-accion - 1).
      - Se asume que la acción de aceptación es -1.
    """
    stack = [0]  # pila de estados (enteros)
    i = 0  # índice de token actual

    while True:
        state = stack[-1]
        if i >= len(tokens):
            print("Error: fin de tokens sin encontrar aceptación.")
            return False

        token_type, token_lex = tokens[i]
        # Se asume que token_type es el número que indica la columna en la tabla LR
        if token_type < 0 or token_type >= len(table[state]):
            print(f"Error: token {token_lex} (tipo={token_type}) fuera de rango en la tabla.")
            return False

        accion = table[state][token_type]
        print(f"Pila: {stack} | Token: ({token_type}, '{token_lex}') | Acción: {accion}")

        if accion > 0:
            # SHIFT
            stack.append(token_type)  # opcional, para almacenar el símbolo
            stack.append(accion)       # nuevo estado
            i += 1  # consumimos token

        elif accion < 0:
            # Si la convención es que -1 es aceptación, se chequea primero:
            if accion == -1:
                print("¡Cadena aceptada!")
                return True
            # De lo contrario, es reducción: 
            regla_idx = -accion - 1  # Por ejemplo, si accion == -2, se reduce por la regla 1.
            if regla_idx < 0 or regla_idx >= len(rules):
                print(f"Error: regla {regla_idx} fuera de rango.")
                return False

            nt_id, lon, nt_name = rules[regla_idx]
            # Sacar 2*lon elementos (símbolos y estados)
            for _ in range(lon):
                if len(stack) < 2:
                    print("Error: pila insuficiente para reducción.")
                    return False
                stack.pop()  # Estado
                stack.pop()  # Símbolo

            # Después de reducción, el tope es un estado
            top_state = stack[-1]
            goto = table[top_state][nt_id]
            if goto < 0 or goto >= len(table):
                print(f"Error: GOTO inválido para estado {top_state} con nt_id {nt_id}.")
                return False
            stack.append(nt_id)  # Apilamos el no terminal
            stack.append(goto)   # Nuevo estado
        elif accion == 0:
            print("Error: acción 0 (celda vacía) en la tabla.")
            return False
        else:
            print(f"Acción desconocida: {accion}")
            return False

# ====================================================
# 5) MAIN: INTEGRANDO TODO
# ====================================================
def main():
    # 1) Leer la tabla LR desde el archivo (ejemplo: compilador.lr)
    lr_filename = "compilador.lr"
    try:
        rules, num_rows, num_cols, table = leer_lr_file(lr_filename)
    except Exception as e:
        print("Error al leer el archivo LR:", e)
        return

    print("=== Reglas de la gramática ===")
    for idx, (nt_id, lon, nt_name) in enumerate(rules):
        print(f"R{idx+1}: {nt_name} (ID: {nt_id}), longitud = {lon}")
    print("\n=== Dimensiones de la tabla LR ===")
    print(f"Filas: {num_rows}, Columnas: {num_cols}")
    print("\n=== Tabla LR ===")
    for row in table:
        print(" ".join(f"{elem:4d}" for elem in row))
    print("")

    # 2) Entrada a analizar (puedes pedir input al usuario)
    # Ejemplo de fuente: (asegúrate de incluir el símbolo final '$')
    fuente = "if x < 10 { x = x + 1; } $"
    print("=== Fuente a analizar ===")
    print(fuente)
    print("")

    # 3) Tokenizar la entrada usando el analizador léxico
    lexico = Lexico(fuente)
    tokens = []
    while not lexico.terminado():
        t = lexico.sig_simbolo()
        if t is None:
            print(f"Token no reconocido: '{lexico.simbolo}'")
            break
        tokens.append((t, lexico.simbolo))
    print("=== Tokens generados ===")
    for tok in tokens:
        print(tok)
    print("")

    # 4) Analizar sintácticamente (parser LR)
    print("=== Análisis sintáctico LR ===")
    resultado = parser_lr(tokens, rules, table)
    print(f"Resultado final: {'ACEPTADO' if resultado else 'RECHAZADO'}")

if __name__ == "__main__":
    main()
