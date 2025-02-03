# 📌 Analizador Léxico en Python

Este proyecto implementa un analizador léxico en Python basado en una lista de símbolos léxicos especificados en el archivo de referencia. El analizador reconoce identificadores, números, operadores, palabras reservadas y símbolos especiales.

---

## ✨ Características
- **Identificadores**: Secuencias que comienzan con una letra y pueden contener letras y dígitos.
- **Números enteros y reales**: En formato `entero` y `entero.entero+`.
- **Operadores**: 
  - **Aritméticos**: `+`, `-`, `*`, `/`
  - **Relacionales**: `<`, `>`, `<=`, `>=`, `==`, `!=`
  - **Lógicos**: `&&`, `||`, `!`
  - **Asignación**: `=`
- **Símbolos especiales**: `;`, `,`, `(`, `)`, `{`, `}`
- **Palabras reservadas**: `if`, `while`, `return`, `else`, `int`, `float`

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

lexico = Lexico("if x >= 10 { return 3.14; }")

print("Resultado del Análisis Léxico:\n")
print("Simbolo\t\tTipo")

while not lexico.terminado():
    tipo = lexico.sig_simbolo()
    if tipo is not None:
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
if x >= 10 { return 3.14; }
```

### **Salida Esperada:**
```
Resultado del Análisis Léxico:

Simbolo		Tipo
if		19
x		0
>=		7
10		1
{		16
return		21
3.14		2
;		12
}		17
```

---

## 🤝 Contribución
Si deseas mejorar este proyecto, ¡siéntete libre de hacer un fork y enviar un pull request! Toda colaboración es bienvenida.

---

## 📜 Licencia
Este proyecto se distribuye bajo la licencia MIT.

---

🎯 **Gracias por tu interés en este proyecto. Esperamos tus contribuciones!** 🚀
