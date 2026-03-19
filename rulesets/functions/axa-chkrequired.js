const $RefParser = require('json-schema-ref-parser');

module.exports = async (targetValue) => {
  const isEmpty = Object.keys(targetValue).length === 0;

  if (isEmpty) {
    return {
      message: `malformed swagger`,
    };
  }

  try {
    const dereferencedDoc = await $RefParser.dereference(targetValue);

    const results = [];

    for (const [path, pathItem] of Object.entries(dereferencedDoc.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        const requestBody =
          operation?.requestBody?.content?.['application/json']?.schema;

        if (!requestBody) continue;

        // Flatten required fields and properties, resolving allOf, oneOf, etc.
        const { requiredFields, definedFields } = extractSchemaFields(requestBody);

        const missingFields = requiredFields.filter((field) => !definedFields.includes(field));

        if (missingFields.length > 0) {
          results.push({
            message: `Missing required fields: ${missingFields.join(', ')}`,
            path: ['paths', path, method, 'requestBody'],
          });
        }
      }
    }

    return results;
  } catch (e) {
    console.error('Exception thrown', e.stack);
  }
};

// Recursively extract `required` fields and `properties` from schema, resolving allOf, anyOf, etc.
function extractSchemaFields(schema, collected = { required: new Set(), properties: new Set() }) {
  if (!schema) return { requiredFields: [], definedFields: [] };

  // Collect required fields
  if (Array.isArray(schema.required)) {
    schema.required.forEach((r) => collected.required.add(r));
  }

  // Collect property names
  if (schema.properties) {
    Object.keys(schema.properties).forEach((p) => collected.properties.add(p));
  }

  // Handle `allOf`, `oneOf`, and `anyOf`
  ['allOf', 'oneOf', 'anyOf'].forEach((key) => {
    if (Array.isArray(schema[key])) {
      schema[key].forEach((subSchema) => extractSchemaFields(subSchema, collected));
    }
  });

  return {
    requiredFields: [...collected.required],
    definedFields: [...collected.properties],
  };
}