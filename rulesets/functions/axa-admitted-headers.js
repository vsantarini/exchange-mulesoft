// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options, path) => {
  const allowedHeaders = options.allowedHeaders;

  if (!allowedHeaders || !Array.isArray(allowedHeaders)) {
    return [
      {
        message:
          'Missing allowed headers list option. Expected an array of strings containing restricted words'
      }
    ];
  }
  return allowedHeaders.includes(targetValue)
    ? undefined
    : [{
        message: `The header parameter '${targetValue}' is not allowed in AXA IT`,
        path: path.target
      }];
};