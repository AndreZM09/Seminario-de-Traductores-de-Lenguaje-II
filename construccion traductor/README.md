# Proyecto de Análisis Léxico y Sintáctico

Este proyecto implementa un **análisis léxico** y un **parser de tipo recursive-descent** para un lenguaje simplificado, cumpliendo con los requisitos de la fase actual.

---

## Diseño del Lexer y Parser

- **Tokens definidos**:
  - **Palabras reservadas**: `if`, `else`, `while`, `print`
  - **Identificadores**: `[A-Za-z_][A-Za-z0-9_]*`
  - **Números**: enteros y decimales (`\d+(?:\.\d+)?`)
  - **Operadores**: `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `<=`, `>`, `>=`
  - **Delimitadores**: `(`, `)`, `{`, `}`, `;`

- **Gramática (síntesis)**:
  ```bnf
  program       → statement_list
  statement_list→ (statement)*
  statement     → assignment | if_stmt | while_stmt | print_stmt
  assignment    → ID '=' expression ';'
  if_stmt       → 'if' '(' expression ')' block ('else' block)?
  while_stmt    → 'while' '(' expression ')' block
  print_stmt    → 'print' '(' expression ')' ';'
  block         → '{' statement_list '}'
  expression    → equality
  equality      → comparison ( ( '==' | '!=' ) comparison )*
  comparison    → term ( ( '<' | '<=' | '>' | '>=' ) term )*
  term          → factor ( ( '+' | '-' ) factor )*
  factor        → unary ( ( '*' | '/' ) unary )*
  unary         → ( '-' )? primary
  primary       → NUMBER | ID | '(' expression ')'
  ```

---

## Decisiones importantes

1. **Lexer a mano**: uso de expresiones regulares (`re`) con un único patrón combinado para capturar el token más largo posible.
2. **Parser recursive-descent**: claridad y facilidad de extensión para futuras fases (generación de código, optimizaciones, etc.).
3. **Clases y excepciones**:
   - `Lexer` y `Parser` organizados en módulos.
   - Excepciones específicas `LexError` y `ParseError` con mensajes detallados (línea y columna).

---

## Manejo de errores

- **Error léxico**: carácter desconocido o formato inválido → `LexError: Unexpected character '<símbolo>' at <línea>:<columna>`
- **Error sintáctico**: token inesperado o elemento faltante → `ParseError: Expected <TOKEN> at <línea>:<columna>, got <OTRO_TOKEN>`

---

## Uso

1. Colocar en el mismo directorio:
   - `lexer_parser.py` (implementación)
   - Archivo de código fuente, p. ej. `test.src`
2. Ejecutar:
   ```bash
   python lexer_parser.py test.src
   ```
3. Salida:
   - Lista de tokens con `(TIPO, valor, línea, columna)`
   - Mensaje `Parse successful.` o detalle del error.

---

## Archivos de prueba y salidas esperadas

### 1. `test.src` (válido)
```c
x = 42;
print(x);
if (x > 10) {
    print(x);
} else {
    print(0);
}
```
**Salida esperada**:
```
Tokens:
('ID', 'x', 1, 1)
('ASSIGN', '=', 1, 3)
('NUMBER', 42.0, 1, 5)
...
('EOF', '', 8, 1)
Parse successful.
```

### 2. `error_lex.src` (error léxico)
```c
x = 4$;
```
**Salida esperada**:
```
Error: Unexpected character '$' at 1:6
```

### 3. `error_syntax.src` (error sintáctico)
```c
x = 10
print(x);
```
**Salida esperada**:
```
Tokens:
('ID', 'x', 1, 1)
('ASSIGN', '=', 1, 3)
('NUMBER', 10.0, 1, 5)
('PRINT', 'print', 2, 1)
...
Error: Expected SEMI at 2:1, got PRINT
```
