# Proyecto de Análisis Léxico, Sintáctico y Semántico

Este proyecto implementa un **análisis léxico**, un **parser de tipo recursive-descent** y un **análisis semántico** básico para un lenguaje simplificado.

---

## Diseño General

1. **Análisis Léxico**: convierte el código fuente en tokens usando expresiones regulares (`re`).
2. **Análisis Sintáctico**: parser recursive-descent que construye un AST con nodos (`ProgramNode`, `VarDeclNode`, `FuncDeclNode`, etc.).
3. **Análisis Semántico**: recorre el AST para:
   - Gestionar tabla de símbolos y ámbitos.
   - Detectar redefiniciones de variables y funciones.
   - Verificar compatibilidad de tipos en expresiones, asignaciones y llamadas.

---

## Gramática Sintáctica

```bnf
program       → declaration*

declaration   → var_decl | func_decl | statement
var_decl      → ("int" | "float") ID ";"
func_decl     → ("int" | "float") ID "(" [param_list] ")" "{" statement* "}"
param_list    → ("int" | "float") ID ("," ("int" | "float") ID)*
statement     → var_decl | assignment | return_stmt | func_call ";"
assignment    → ID "=" expression
return_stmt   → "return" expression
func_call     → ID "(" [arg_list] ")"
arg_list      → expression ("," expression)*

expression    → equality
equality      → comparison ( ("==" | "!=") comparison )*
comparison    → term ( ("<" | "<=" | ">" | ">=") term )*
term          → factor ( ("+" | "-") factor )*
factor        → unary ( ("*" | "/") unary )*
unary         → ["-"] primary
primary       → NUMBER | ID | func_call | "(" expression ")"
```

---

## Manejo de Errores

- **Error Léxico** (`LexError`): carácter inesperado en la entrada.
- **Error Sintáctico** (`ParseError`): token faltante o inesperado.
- **Error Semántico**: acumulado en lista de errores:
  - Declaración no previa de `ID`.
  - Redefinición en mismo ámbito.
  - Mezcla de tipos incompatible.
  - Llamada a función no declarada o argumentos con tipos incorrectos.

---

## Uso

1. Edita la constante `SOURCE_FILE` en `lexer_parser.py` con el archivo de prueba `.src`.
2. Ejecuta:
   ```bash
   python lexer_parser.py
   ```
3. Se mostrarán los errores semánticos (si los hay) o un mensaje de éxito.

---

## Resultados de Ejemplo

### Ejemplo 1 (`ejemplo1.src`)
Código fuente:
```c
int main() {
    float a;
    int b;
    int c;
    c = a + b;
    c = suma(8, 9);
}
```
Salida:
```
Error: función 'suma' no declarada.
```

### Ejemplo 2 (`ejemplo2.src`)
Código fuente:
```c
int suma(int a, int b) {
    return a + b;
}

int main() {
    float a;
    int b;
    int c;
    c = a + b;
    c = suma(8.5, 9.9);
}
```
Salida:
```
Error: paso 'float' donde se espera 'int' en 'suma'.
Error: paso 'float' donde se espera 'int' en 'suma'.
```