import re

class TokenType:
    IDENTIFICADOR = "Identificador"
    REAL = "Real"
    ERROR = "Error"
    FIN = "Fin de la Entrada"

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
        
        # Identificadores (letra seguido de letras o dígitos)
        if c.isalpha():
            self.simbolo += c
            while not self.terminado():
                c = self.sig_caracter()
                if c.isalnum():
                    self.simbolo += c
                else:
                    self.retroceso()
                    break
            self.tipo = TokenType.IDENTIFICADOR
            return self.tipo
        
        # Números reales (entero.entero+)
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
                        self.tipo = TokenType.ERROR
                        return self.tipo
                else:
                    self.retroceso()
                    break
            self.tipo = TokenType.ERROR
            return self.tipo
        
        # Fin de la entrada
        elif c == '$':
            self.simbolo = c
            self.tipo = TokenType.FIN
            return self.tipo
        
        # Si no es un token válido
        else:
            self.simbolo = c
            self.tipo = TokenType.ERROR
            return self.tipo
    
    def terminado(self):
        return self.ind >= len(self.fuente)
    
    def tipo_acad(self, tipo):
        return tipo

# Prueba del analizador léxico
if __name__ == "__main__":
    lexico = Lexico("x123 45.67 invalid .45 test 78.")
    
    print("Resultado del Análisis Léxico:\n")
    print("Simbolo\t\tTipo")
    
    while not lexico.terminado():
        tipo = lexico.sig_simbolo()
        print(f"{lexico.simbolo}\t\t{lexico.tipo_acad(tipo)}")
