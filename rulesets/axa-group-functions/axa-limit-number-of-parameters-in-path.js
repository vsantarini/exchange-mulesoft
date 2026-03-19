// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options) => {
  const { limit } = options;

  if (!limit || !Number.isInteger(limit)) {
    return [
      {
        message:
          'Missing limit option. Expected an integer representing the max allowed number of parameters in a path'
      }
    ];
  }

  return Object.keys(targetValue)
    .map(path =>
      (path.match(/({\w*})/g) || []).length > limit
        ? {
            message: `Path has more path parameter than the limit of ${limit}`,
            path: ['paths', path]
          }
        : undefined
    )
    .filter(val => val);
};