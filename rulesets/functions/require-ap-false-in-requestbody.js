module.exports = (paths, opts, ctx) => {
  const results = [];
  const doc = ctx.document.data;

  const methods = ['post', 'put', 'patch'];

  function resolveRef(ref) {
    // supporta solo ref interni '#/...'
    if (!ref || typeof ref !== 'string' || !ref.startsWith('#/')) return null;
    const parts = ref.slice(2).split('/').map(p => p.replace(/~1/g, '/').replace(/~0/g, '~'));
    let cur = doc;
    for (const p of parts) {
      if (cur && Object.prototype.hasOwnProperty.call(cur, p)) cur = cur[p];
      else return null;
    }
    return cur;
  }

  function hasAdditionalPropsFalse(schema, seen = new Set()) {
    if (!schema || typeof schema !== 'object') return false;

    // evita loop su ref circolari
    if (schema.$ref) {
      if (seen.has(schema.$ref)) return false;
      seen.add(schema.$ref);
      const target = resolveRef(schema.$ref);
      return hasAdditionalPropsFalse(target, seen);
    }

    // caso diretto
    if (schema.type === 'object' || schema.properties) {
      return schema.additionalProperties === false;
    }

    // composizioni: cerca un object “risultante”
    for (const k of ['allOf', 'oneOf', 'anyOf']) {
      if (Array.isArray(schema[k])) {
        // regola conservativa: se *qualunque* ramo porta a object con additionalProperties false -> ok
        // (se vuoi più severità, puoi richiedere che TUTTI i rami object lo abbiano)
        if (schema[k].some(s => hasAdditionalPropsFalse(s, new Set(seen)))) return true;
      }
    }

    return false;
  }

  for (const [pathKey, pathItem] of Object.entries(paths || {})) {
    for (const m of methods) {
      const op = pathItem?.[m];
      if (!op?.requestBody?.content) continue;

      for (const [ct, media] of Object.entries(op.requestBody.content)) {
        const schema = media?.schema;
        if (!schema) continue;

        if (!hasAdditionalPropsFalse(schema)) {
          results.push({
            message: `Missing additionalProperties: false for ${m.toUpperCase()} ${pathKey} (${ct})`,
            path: ['paths', pathKey, m, 'requestBody', 'content', ct, 'schema'],
          });
        }
      }
    }
  }

  return results;
};