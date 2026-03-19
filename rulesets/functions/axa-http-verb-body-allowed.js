// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options) => {
  const { allowed } = options;

  if (!allowed && !Array.isArray(allowed)) {
    return [
      {
        message:
          'Missing allowed option. Expected an array of allowed verbs in uppercase'
      }
    ];
  }

  return Object.entries(targetValue)
    .flatMap(([pathKey, path]) => {
      return Object.entries(path)
        .filter(([, endpoint]) => endpoint.requestBody)
        .flatMap(([verb]) =>
          allowed.includes(verb.toUpperCase())
            ? undefined
            : {
                message: `Request body not allowed for '${verb}'`,
                path: ['paths', pathKey]
              }
        );
    })
    .filter(val => val);
};