# 📌 Analizador Léxico en Python

Este proyecto implementa un analizador léxico en Python que identifica identificadores y números reales en una cadena de entrada. Se basa en un código de referencia en C++ y ha sido adaptado para su ejecución en Python.

---

## ✨ Características
- **Identificadores**: Secuencias que comienzan con una letra y pueden contener letras y dígitos.
- **Números reales**: Números en formato `entero.entero+`.
- **Manejo de errores**: Identifica entradas no válidas.
- **Indicación de fin de entrada** con el símbolo `$`.

---

## 🛠️ Estructura del Código
- **`TokenType`**: Define los tipos de tokens que el analizador reconoce.
- **`Lexico`**: Implementa las funciones del analizador, incluyendo la lectura de caracteres y el reconocimiento de tokens.
- **`sig_simbolo()`**: Extrae el siguiente token de la cadena de entrada.
- **`terminado()`**: Verifica si la entrada ha sido completamente procesada.

---

## 🚀 Uso

```python
from lexico import Lexico

lexico = Lexico("x123 45.67 invalid .45 test 78.")

print("Resultado del Análisis Léxico:\n")
print("Simbolo\t\tTipo")

while not lexico.terminado():
    tipo = lexico.sig_simbolo()
    print(f"{lexico.simbolo}\t\t{lexico.tipo_acad(tipo)}")
```

---

## 🔧 Instalación y Ejecución
1. Clona el repositorio.
   ```sh
   git clone https://github.com/tu-repositorio/analizador-lexico.git
   cd analizador-lexico
   ```
2. Asegúrate de tener Python instalado (versión 3.x recomendada).
3. Ejecuta el código con:
   ```sh
   python lexico.py
   ```

---

## 📊 Ejemplo de Entrada y Salida
### **Entrada:**
```
x123 45.67 invalid .45 test 78.
```

### **Salida Esperada:**
```
Resultado del Análisis Léxico:

Simbolo		Tipo
x123		Identificador
45.67		Real
invalid		Error
.45		Error
test		Identificador
78.		Error
