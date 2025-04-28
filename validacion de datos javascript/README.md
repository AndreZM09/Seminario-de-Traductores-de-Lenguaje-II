# Validador de Datos DSL → JSON Schema → Ajv/Zod/Joi

**Proyecto:** Traductor de esquemas para validación automática de datos en JavaScript  
**Autor:** MICHEL EMANUEL LÓPEZ FRANCO  
**Fecha de entrega:** 7 abr  

---

## Descripción

Este proyecto implementa un traductor de un lenguaje de dominio específico (DSL) para la validación automática de datos en JavaScript. Permite:

1. Definir esquemas de datos en un formato amigable (`.dsl`).  
2. Transformar esas definiciones en un AST en JavaScript.  
3. Generar un **JSON Schema** (Draft-07).  
4. Emitir automáticamente código de validación para **Ajv**, **Zod** o **Joi**.  
5. Usarlo desde la línea de comandos para convertir `.dsl` en un validador `.js` listo para exportar.  

---

## Requisitos

- **Node.js** v14 o superior  
- **npm** v6+  

Dependencias principales:

```bash
npm install ajv zod joi
```

---

## Estructura del proyecto

```plaintext
VALIDACION-DE-DATOS-EN-JAVASCRIPT/
├─ node_modules/       # dependencias de npm
├─ index.js            # script principal (parser + generadores + CLI)
├─ package.json        # configuración del proyecto
├─ schema.dsl          # definición DSL de entrada
├─ validator.js        # validador generado (salida de la CLI)
└─ README.md           # este archivo
```

---

## Formato DSL (`schema.dsl`)

```plaintext
User {
  id: Integer,
  name: String &min(3)&max(50),
  email: String &email,
  tags?: [String]
}
```

- `identifier?`: nombre de campo (`?` indica opcional).  
- `type`: `Integer`, `String`, `Boolean` o arreglos (`[Type]`).  
- `constraints`: `&min(n)`, `&max(n)`, `&email`.  

---

## Uso de la CLI

1. Instalar dependencias:

   ```bash
   npm install
   ```

2. Ejecutar el traductor:

   ```bash
   node index.js <input.dsl> <output.js> <ajv|zod|joi>
   ```

   - `<input.dsl>`: archivo con definición DSL.  
   - `<output.js>`: archivo de salida con el validador.  
   - `ajv`, `zod` o `joi`: librería de validación deseada.  

3. Ejemplo:

   ```bash
   node index.js schema.dsl validator.js ajv
   ```

Esto generará `validator.js` con un validador Ajv similar a:

```javascript
const Ajv = require('ajv');
const ajv = new Ajv();
const schema = { /* JSON Schema generado */ };
const validate = ajv.compile(schema);
module.exports = validate;
```

---

## Integración en tu proyecto

```javascript
const validate = require('./validator');

const data = { id: 1, name: 'Ana', email: 'ana@example.com' };
if (!validate(data)) {
  console.error(validate.errors);
} else {
  console.log('Datos válidos');
}
