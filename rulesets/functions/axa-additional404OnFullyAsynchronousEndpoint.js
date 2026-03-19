// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.

module.exports = (responses, _opts, paths) => {
  const resultCodes = Object.keys(responses);

  const rootPath = paths.target !== void 0 ? paths.target : paths.given;

  const successCodes = resultCodes.filter(resultCode => resultCode.startsWith('2'));
  const results = [];

  if (successCodes.includes('202') && successCodes.length === 1 && resultCodes.includes('404')) {
    results.push(
      {
        message: 'Fully Asynchronous endpoint must not define 404 response code',
        path: [...rootPath]
      },
    );
    return results;
  }
  return;
};