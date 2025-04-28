// index.js
// CLI Translator: DSL -> JSON Schema -> Ajv/Zod/Joi validator code

const fs = require('fs');
const path = require('path');

// Parser manual para el DSL
const TYPE_MAP = { Integer: 'integer', String: 'string', Boolean: 'boolean' };
function parseDSL(input) {
  const declRe = /^\s*(\w+)\s*\{([\s\S]*)\}\s*$/;
  const m = input.trim().match(declRe);
  if (!m) throw new Error('Formato inválido de declaración');
  const [, name, body] = m;

  const lines = body
    .split(/\r?\n/)              // dividir en líneas
    .map(l => l.trim().replace(/,$/, '')) // quitar comas final
    .filter(l => l);

  const fields = lines.map(line => {
    const [left, right] = line.split(':').map(s => s.trim());
    const optional = left.endsWith('?');
    const fieldName = optional ? left.slice(0, -1) : left;

    const parts = right.split('&').map(p => p.trim()).filter(p => p);
    let rawType = parts.shift();
    const constraints = parts.map(p => {
      const m = p.match(/(\w+)(?:\((\d+)\))?/);
      const [, cname, cval] = m;
      return { name: cname, value: cval ? Number(cval) : true };
    });

    const arrayMatch = rawType.match(/^\[(.+)\]$/);
    let type;
    if (arrayMatch) {
      const inner = arrayMatch[1].trim();
      type = { type: 'array', items: TYPE_MAP[inner] || inner.toLowerCase() };
    } else {
      rawType = rawType.trim();
      type = { type: TYPE_MAP[rawType] || rawType.toLowerCase() };
    }

    return { name: fieldName, optional, type, constraints };
  });

  return { type: 'Declaration', name, fields };
}

// Generador de JSON Schema
function generateJSONSchema(ast) {
  const { name, fields } = ast;
  const schema = {
    $schema: 'http://json-schema.org/draft-07/schema#',
    title: name,
    type: 'object',
    properties: {},
    required: []
  };

  fields.forEach(f => {
    const { name: fname, optional, type, constraints } = f;
    const prop = { type: type.type };
    if (type.type === 'array') prop.items = { type: type.items };

    constraints.forEach(c => {
      if (c.name === 'min') {
        if (prop.type === 'string') prop.minLength = c.value;
        else prop.minimum = c.value;
      }
      if (c.name === 'max') {
        if (prop.type === 'string') prop.maxLength = c.value;
        else prop.maximum = c.value;
      }
      if (c.name === 'email') prop.format = 'email';
    });

    schema.properties[fname] = prop;
    if (!optional) schema.required.push(fname);
  });
  if (!schema.required.length) delete schema.required;
  return schema;
}

// Generadores de código
function generateAjvCode(schema) {
  return `const Ajv = require('ajv');
const ajv = new Ajv();
const schema = ${JSON.stringify(schema, null, 2)};
const validate = ajv.compile(schema);
module.exports = validate;
`;
}

function generateZodCode(schema) {
  const lines = ["const { z } = require('zod');", "const schema = z.object({"];  
  Object.entries(schema.properties).forEach(([key, prop]) => {
    let expr = prop.type === 'string' ? 'z.string()'
      : prop.type === 'integer' ? 'z.number().int()'
      : prop.type === 'array' ? `z.array(z.${prop.items}())`
      : `z.${prop.type}()`;
    if (prop.minLength) expr += `.min(${prop.minLength})`;
    if (prop.maxLength) expr += `.max(${prop.maxLength})`;
    if (prop.format === 'email') expr += '.email()';
    if (schema.required && !schema.required.includes(key)) expr += '.optional()';
    lines.push(`  ${key}: ${expr},`);
  });
  lines.push('});', 'module.exports = schema;');
  return lines.join("\n");
}

function generateJoiCode(schema) {
  const lines = ["const Joi = require('joi');", "const schema = Joi.object({"];
  Object.entries(schema.properties).forEach(([key, prop]) => {
    let expr = prop.type === 'string' ? 'Joi.string()'
      : prop.type === 'integer' ? 'Joi.number().integer()'
      : prop.type === 'array' ? `Joi.array().items(Joi.${prop.items}())`
      : `Joi.${prop.type}()`;
    if (prop.minLength) expr += `.min(${prop.minLength})`;
    if (prop.maxLength) expr += `.max(${prop.maxLength})`;
    if (prop.format === 'email') expr += '.email()';
    if (schema.required && schema.required.includes(key)) expr += '.required()';
    lines.push(`  ${key}: ${expr},`);
  });
  lines.push('});', 'module.exports = schema;');
  return lines.join("\n");
}

// CLI
function printUsage() {
  console.log('Usage: node index.js <input.dsl> <output.js> <ajv|zod|joi>');
}

if (require.main === module) {
  const [,, input, output, lib] = process.argv;
  if (!input || !output || !lib) return printUsage();
  const dsl = fs.readFileSync(input, 'utf-8');
  const ast = parseDSL(dsl);
  const schema = generateJSONSchema(ast);
  let code;
  if (lib === 'ajv') code = generateAjvCode(schema);
  else if (lib === 'zod') code = generateZodCode(schema);
  else if (lib === 'joi') code = generateJoiCode(schema);
  else return printUsage();
  fs.writeFileSync(output, code);
  console.log(`Wrote ${lib} validator to ${output}`);
}
