## Introducción

Este documento describe el diseño e implementación del componente de análisis léxico y sintáctico para un lenguaje de programación simplificado. Se abordan las decisiones de diseño, la organización del código y el manejo de errores, tanto léxicos como sintácticos.

## Estructura General del Proyecto

El proyecto se ha dividido en dos componentes principales:

1. **Analizador Léxico:**  
   - **Objetivo:** Leer el código fuente y convertirlo en una secuencia de tokens.
   - **Implementación:**  
     Se ha implementado en Python utilizando un enfoque basado en un autómata simple. La clase `Lexico` recorre el texto de entrada caracter por caracter, omitiendo espacios en blanco, y agrupa secuencias de caracteres en tokens según reglas definidas.
   - **Tokens:**  
     Se definen mediante la clase `TokenType`, donde se asignan números a cada token (por ejemplo, identificador = 0, entero = 1, etc.), de acuerdo con la especificación proporcionada en `compilador.inf`.
   - **Manejo de Errores Léxicos:**  
     - Se verifica, por ejemplo, que después de un punto en un número exista al menos un dígito; si no es así, se imprime un mensaje de error.
     - Para cualquier carácter inesperado (no reconocido según las reglas), se emite un mensaje de error indicando el carácter inválido.

2. **Analizador Sintáctico (Parser LR):**  
   - **Objetivo:** Validar que la secuencia de tokens generada por el analizador léxico se ajuste a la gramática del lenguaje.
   - **Implementación:**  
     Se utiliza un parser LR basado en una tabla LR mínima, implementada en Python.  
     - Se utilizan estructuras de datos como **pilas** para almacenar estados y símbolos (representados con clases como `Terminal`, `NoTerminal` y `Estado`).
     - La tabla LR se implementa como un diccionario que, dada una pareja (estado, token), determina la acción (shift, reduce o accept).
   - **Manejo de Errores Sintácticos:**  
     - Si en el estado actual el token no tiene acción definida (por ejemplo, al iniciar con un token que la gramática no espera), se imprime un mensaje indicando que no hay acción para ese estado y token.
     - En caso de errores en las reducciones o en la transición (GOTO), se emiten mensajes específicos para facilitar la depuración.

## Decisiones Importantes

- **Elección del Lenguaje:**  
  Se eligió Python por su sencillez para implementar autómatas y por la facilidad para trabajar con expresiones regulares y estructuras de datos como listas y diccionarios.
  
- **Enfoque en el Analizador Léxico:**  
  Se implementó manualmente el analizador léxico en lugar de utilizar herramientas generadoras de analizadores (como Lex/Flex), ya que la especificación es para un lenguaje simplificado y el objetivo es demostrar la capacidad de transformar el código fuente en una secuencia de tokens.

- **Implementación del Parser LR:**  
  Se optó por un parser LR básico, implementado utilizando una pila. Aunque la gramática mínima es muy simple (por ejemplo, solo se considera la producción para expresiones con suma), este enfoque se puede extender para cubrir más producciones.

- **Manejo de Errores:**  
  Se priorizó la emisión de mensajes claros tanto en la fase léxica como en la sintáctica, de modo que si la entrada no es válida, se indique de manera precisa cuál es el problema (por ejemplo, "carácter no válido", "no hay acción para estado X con token Y", etc.).

## Conclusión

El diseño se centra en la simplicidad y en la claridad de la implementación, facilitando la extensión del analizador para cubrir una gramática más completa en fases posteriores del proyecto. El manejo explícito de errores y la utilización de estructuras de datos claras (como pilas y diccionarios) permiten un mantenimiento y depuración más efectivos.

# Casos de Prueba y Salidas Esperadas
## 1. Caso Válido Básico

### Entrada:
`id + id $`
### Salida Esperada:
- **Tokens Generados:**
  - (0, "id")
  - (1, "+")
  - (0, "id")
  - (2, "$")
- **Análisis Sintáctico:**  
  El parser realiza las reducciones y llega a la aceptación.  
- **Resultado:** ACEPTADO

## 2. Caso Válido Simple

### Entrada:
`id $`
### Salida Esperada:
- **Tokens Generados:**
  - (0, "id")
  - (2, "$")
- **Análisis Sintáctico:**  
  Se reduce mediante la producción `E -> id` y se acepta.
- **Resultado:** ACEPTADO

## 3. Caso Inválido Sintáctico

### Entrada:
`id + $`
### Salida Esperada:
- **Tokens Generados:**
  - (0, "id")
  - (1, "+")
  - (2, "$")
- **Análisis Sintáctico:**  
  Falta el token después del operador '+'.  
  El parser no encuentra acción para el estado correspondiente y emite un mensaje de error: "No hay acción para estado X con token '...'"
- **Resultado:** RECHAZADO

## 4. Caso Inválido Léxico

### Entrada:
`if x < 10 { x = x + 1; } $`
### Salida Esperada:
- **Tokens Generados:**
  - (19, "if")
  - (0, "x")
  - (7, "<")
  - (1, "10")
  - (16, "{")
  - (0, "x")
  - (18, "=")
  - (0, "x")
  - (5, "+")
  - (1, "1")
  - (12, ";")
  - (17, "}")
  - (23, "$")
- **Análisis Sintáctico:**  
  Dado que la gramática mínima implementada solo admite secuencias que comienzan con un identificador, el parser no encontrará acción para el token "if" (tipo 19) en el estado inicial.
- **Resultado:** RECHAZADO

---
