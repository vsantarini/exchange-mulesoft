/**
 * Custom Spectral function: verifica che i segmenti letterali delle path siano plurali.
 * - Ignora segmenti parametro {…}
 * - Ignora segmenti tecnici whitelisted: "api", "vX", "vX.Y" (es. v1, v2, v1.2, v2.3.4)
 * - Messaggi distinti per:
 *   - ultimo segmento letterale (non parametro)
 *   - segmenti letterali intermedi
 * - Opzione checkIntermediates (default: true) per attivare/disattivare il controllo sui segmenti intermedi
 *
 * Uso nel ruleset:
 *   given: $.paths
 *   then:
 *     function: resourcesPluralCheck
 *     functionOptions:
 *       checkIntermediates: true   // opzionale (default true)
 */

module.exports = (pathsObject, opts = {}, ctx) => {
  const pluralize = require('pluralize');

  // Opzione per controllare i segmenti intermedi (default: true)
  const checkIntermediates = typeof opts.checkIntermediates === 'boolean'
    ? opts.checkIntermediates
    : true;

  // Utility
  const isParam = (s) => /^\{[^}]+\}$/.test(s);
  const norm = (s) => String(s || '').trim().toLowerCase();

  // Whitelist segmenti tecnici: "api", "v1", "v2", "v1.2", ecc.
  const isWhitelistedSegment = (raw) => {
    const s = norm(raw);
    if (!s) return true;             // ignora vuoti
    if (s === 'api') return true;    // "/api"
    // Versioni tipo vX(.Y)* (es. v1, v10, v1.0, v2.3.4)
    if (/^v\d+(\.\d+)*$/.test(s)) return true;
	if (s === 'rest') return true; // "/rest"
    return false;
  };

  const isLiteral = (s) => !!s && !isParam(s) && !isWhitelistedSegment(s);

  const isPlural = (raw) => {
    const s = norm(raw);
    if (!s) return true;
    // Rimuove caratteri non rilevanti per la pluralizzazione
    const base = s.replace(/[^a-z0-9_-]/gi, '');
    if (!base) return true;
    return pluralize.isPlural(base);
  };

  const results = [];

  if (!pathsObject || typeof pathsObject !== 'object' || Array.isArray(pathsObject)) {
    return [{ message: 'resource is empty, malformed swagger' }];
  }

  for (const apiPath of Object.keys(pathsObject)) {
    if (typeof apiPath !== 'string' || !apiPath.startsWith('/')) continue;

    const segmentsRaw = apiPath.split('/').filter(Boolean);

    // Indici dei segmenti letterali rilevanti (non param, non whitelisted)
    const literalIdxs = [];
    segmentsRaw.forEach((seg, idx) => {
      if (isLiteral(seg)) literalIdxs.push(idx);
    });

    if (literalIdxs.length === 0) continue;

    const lastLiteralIdx = literalIdxs[literalIdxs.length - 1];

    // 1) Controllo segmento letterale finale
    {
      const seg = segmentsRaw[lastLiteralIdx];
      if (!isPlural(seg)) {
        results.push({
          message: `'${apiPath}': l'ultimo segmento letterale '${seg}' dovrebbe essere plurale`,
          path: ['paths', apiPath],
          severity: 1, // warn
        });
      }
    }

    // 2) Controllo segmenti letterali intermedi (se abilitato)
    if (checkIntermediates && literalIdxs.length > 1) {
      for (let i = 0; i < literalIdxs.length - 1; i += 1) {
        const idx = literalIdxs[i];
        const seg = segmentsRaw[idx];
        if (!isPlural(seg)) {
          results.push({
            message: `'${apiPath}': il segmento letterale intermedio '${seg}' dovrebbe essere plurale`,
            path: ['paths', apiPath],
            severity: 1, // warn
          });
        }
      }
    }
  }

  return results.length ? results : undefined;
};