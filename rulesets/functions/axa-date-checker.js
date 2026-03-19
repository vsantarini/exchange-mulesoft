// AXA date checker (aggiornato)
// - Evita falsi positivi su termini come "mandate", "candidate", "update", ecc.
// - Accetta type: string e format: "date" oppure "date-time"
// - Consente di personalizzare whitelist/blacklist via options

module.exports = (targetVal, opts = {}, ctx) => {
  const stringType = 'string';
  const allowedFormats = new Set(['date', 'date-time']);

  // Parole da escludere esplicitamente (falsi positivi)
  const blacklist = new Set(
    (opts.blacklist || ['mandate', 'candidate', 'update', 'updated', 'updater', 'validate', 'validation'])
      .map(s => String(s).toLowerCase())
  );

  // Nomi che accettano specificamente solo "date" (opzionale, se vuoi forzare)
  const dateOnlyWhitelist = new Set(
    (opts.dateOnlyWhitelist || ['birthdate', 'birthday', 'dueDate', 'expiryDate', 'expirationDate'])
      .map(s => String(s).toLowerCase())
  );

  // Matcher più robusto:
  // - cattura esattamente "date" (come parola intera) o composti comuni: "createdAt", "updatedAt", "startDate", "endDate"
  // - evita match dentro parole più grandi (candidate, mandate, update)
  const looksLikeDate = (key) => {
    if (!key) return false;
    const k = String(key);

    // normalizzazioni utili
    const lower = k.toLowerCase();

    // esclusioni esplicite
    if (blacklist.has(lower)) return false;

    // pattern accettati:
    // - "date" da solo o come parola distinta (snake/kebab): ^date$ | _date$ | -date$
    // - camel/pascal come ...Date (es. birthDate, startDate, endDate)
    // - convenzioni "createdAt", "updatedAt"
    const patterns = [
      /\bdate\b/i,                // parola "date" isolata (funziona bene su snake/kebab/space)
      /[A-Za-z]Date$/,            // camel/pascal case: ...Date
      /^createdAt$/i,
      /^updatedAt$/i,
      /^issuedAt$/i,
      /^expiresAt$/i,
      /^startDate$/i,
      /^endDate$/i,
    ];

    return patterns.some((re) => re.test(k));
  };

  const results = [];

  if (targetVal && typeof targetVal === 'object' && !Array.isArray(targetVal)) {
    for (const key of Object.keys(targetVal)) {
      if (!looksLikeDate(key)) continue;

      const schema = targetVal[key] || {};
      const t = schema.type;
      const f = schema.format;
      const keyLower = key.toLowerCase();

      // 1) type deve essere string
      if (t == null) {
        results.push({ message: `Missing type (string) for date-like attribute '${key}'` });
      } else if (t !== stringType) {
        results.push({ message: `Wrong type for date-like attribute '${key}': '${t}' (expected 'string')` });
      }

      // 2) format deve essere "date" o "date-time"
      if (f == null) {
        // Puoi scegliere se segnalare come missing o suggerire il più adatto
        const hint = dateOnlyWhitelist.has(keyLower) ? 'date' : 'date-time or date';
        results.push({ message: `Missing format (${hint}) for date-like attribute '${key}'` });
      } else {
        // Se è in whitelist "solo date", consenti solo "date"
        if (dateOnlyWhitelist.has(keyLower)) {
          if (f !== 'date') {
            results.push({ message: `Wrong format for '${key}': '${f}' (expected 'date')` });
          }
        } else {
          // In generale accettiamo 'date' e 'date-time'
          if (!allowedFormats.has(f)) {
            results.push({ message: `Wrong format for '${key}': '${f}' (expected 'date' or 'date-time')` });
          }
        }
      }
    }
  }

  return results;
};