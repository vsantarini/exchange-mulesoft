module.exports = (targetVal, _opts, paths) => {
  const errors = [];

  // Defensive: derive a base path to make messages readable
  const basePath = Array.isArray(paths?.target) ? paths.target.join('.') : '(root)';

  if (!targetVal || typeof targetVal !== 'object' || !targetVal.properties) return [];

  const props = targetVal.properties;
  const keys = Object.keys(props);

  // Check if schema contains a currency-code property
  const hasCurrency = keys.some(k => /^currency-code$/i.test(k));

  // Iterate through all properties
  for (const key of keys) {
    // Case-insensitive match for "amount" anywhere in the property name
    if (/amount/i.test(key)) {
      // If there's no currency-code defined at this schema level → warn
      if (!hasCurrency) {
        errors.push({
          message: `Property "${key}" at ${basePath}.properties.${key} has 'amount' in its name but no sibling 'currency-code' property was found.`,
          path: Array.isArray(paths?.target)
            ? [...paths.target, 'properties', key]
            : ['properties', key],
        });
      }
    }

    // Recursively check nested objects
    const subSchema = props[key];
    if (subSchema && typeof subSchema === 'object' && subSchema.properties) {
      const nestedPath = Array.isArray(paths?.target)
        ? [...paths.target, 'properties', key]
        : ['properties', key];
      const nestedErrors = module.exports(subSchema, _opts, { target: nestedPath });
      errors.push(...nestedErrors);
    }
  }

  return errors;
};
