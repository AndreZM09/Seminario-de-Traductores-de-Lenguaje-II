#!/usr/bin/env python3

import re

# ==========================
# 1) Definición de clases
# ==========================

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

    def get_lexema(self):
        return self.lexema


class NoTerminal(ElementoPila):
    def __init__(self, simbolo, nombre):
        self.simbolo = simbolo
        self.nombre = nombre

    def muestra(self):
        print(f"NoTerminal({self.nombre})", end=' ')

    def get_simbolo(self):
        return self.simbolo

    def get_nombre(self):
        return self.nombre


class Estado(ElementoPila):
    def __init__(self, numero):
        self.numero = numero

    def muestra(self):
        print(f"Estado({self.numero})", end=' ')

    def get_numero(self):
        return self.numero


# ==========================
# 2) Pila de objetos
# ==========================

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
        return (len(self.lista) == 0)

    def muestra(self):
        print("Contenido de la pila (base -> tope):")
        for elem in self.lista:
            elem.muestra()
        print("\n")


# ==========================
# 3) Tabla LR y Reglas
# ==========================

reglas = [
    (3, 3, "E"),  
    (3, 1, "E"),  
]

tabla = {
    # Estado 0
    (0, 0): ('s', 2),   
    (0, 3): ('g', 1),  

    # Estado 1
    (1, 1): ('r', 1),   
    (1, 2): ('acc',),   

    # Estado 2
    (2, 1): ('s', 3),   
    (2, 2): ('r', 1), 

    # Estado 3
    (3, 0): ('s', 2),  
    (3, 3): ('g', 4),  

    # Estado 4
    (4, 1): ('r', 0),   
    (4, 2): ('r', 0),   
}


# ==========================
# 4) Analizador léxico simple
# ==========================

def lexico_rapido(cadena):
    tokens = []
    partes = re.split(r'\s+', cadena.strip())

    for p in partes:
        if p == '+':
            tokens.append((1, '+'))
        elif p == '$':
            tokens.append((2, '$'))
        else:
            # Cualquier otra cosa la consideramos 'id'
            tokens.append((0, p))  # 0 = 'id'
    return tokens


# ==========================
# 5) Función principal de análisis
# ==========================

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
                stack.pop()
                stack.pop()

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


# ==========================
# 6) Pruebas / Main
# ==========================

def main():
    entradas = [
        "id + id $",
        "id $",
        "id + id + id $",
        "id + $",
        "$"
    ]

    for cadena in entradas:
        print("======================================")
        print(f"Analizando la cadena: {cadena}")
        tokens = lexico_rapido(cadena)
        aceptado = analizar(tokens)
        print("Resultado:", "ACEPTADO" if aceptado else "RECHAZADO")
        print("======================================\n")


if __name__ == "__main__":
    main()
