# Analizador Sintáctico LR(1) en Python

Este proyecto implementa un analizador sintáctico LR(1) sencillo en Python utilizando una pila de objetos para representar estados, terminales y no terminales. El objetivo es replicar, en Python, la idea de un analizador LR que utilice una pila de objetos para facilitar la trazabilidad del análisis.

## Características

- **Gramática utilizada:**
  - Regla 0: `E -> id + E` (longitud 3)
  - Regla 1: `E -> id` (longitud 1)

- **Tokens:**
  - `id` (tipo 0)
  - `+` (tipo 1)
  - `$` (tipo 2, fin de cadena)

- **Clases principales:**
  - `ElementoPila`: Clase base para elementos en la pila.
  - `Terminal`: Representa un token terminal.
  - `NoTerminal`: Representa un símbolo no terminal.
  - `Estado`: Representa un estado del autómata LR.
  - `Pila`: Implementación de una pila que maneja objetos de tipo `ElementoPila`.

- **Tabla LR:**  
  La tabla se implementa como un diccionario que asocia (estado, token) a acciones de tipo shift, reduce, goto o accept.

- **Analizador Léxico Simple:**  
  Una función que tokeniza la cadena de entrada. Todo lo que no sea '+' o '$' se asume como un `id`.

- **Proceso de Análisis:**  
  Se traza el contenido de la pila en cada paso, mostrando el token actual, la acción aplicada y el resultado de la operación, hasta llegar a la aceptación o detectar un error.

## Cómo usar el proyecto

1. **Requisitos:**
   - Python 3.6 o superior.

3. **Ejemplos de Entrada:**
   - `id + id $`
   - `id $`
   - `id + id + id $`
   - `id + $` (ejemplo de error)
   - `$` (ejemplo de error)

## Estructura del Código

- **Definición de Clases:**  
  Incluye `ElementoPila`, `Terminal`, `NoTerminal` y `Estado` para representar cada elemento en la pila.

- **Pila de Objetos:**  
  La clase `Pila` maneja los elementos mediante una lista de Python, permitiendo operaciones de push, pop y top.

- **Tabla LR y Reglas:**  
  La gramática y la tabla LR se definen mediante arreglos y diccionarios. Esto permite determinar, según el estado actual y el token, qué acción realizar.

- **Analizador Léxico:**  
  La función `lexico_rapido` convierte una cadena de entrada en una lista de tokens (tuplas de tipo y lexema).

- **Analizador Sintáctico:**  
  La función `analizar` implementa el algoritmo LR(1) utilizando la pila de objetos, mostrando en cada paso el contenido de la pila, el token actual y la acción tomada.

- **Función `main`:**  
  Ejecuta ejemplos de prueba, mostrando la traza del análisis y el resultado final (aceptado o rechazado).
