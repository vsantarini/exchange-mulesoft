// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options) => {
  const { limit } = options;

  if (!limit || !Number.isInteger(limit)) {
    return [
      {
        message:
          'Missing limit option. Expected an integer representing the max allowed number of subresources in a path'
      }
    ];
  }

  return Object.keys(targetValue)
    .map(path =>
      path.split('/').filter(a => a).length > limit
        ? {
            message: `Path has more subresources than the limit of ${limit}`,
            path: ['paths', path]
          }
        : undefined
    )
    .filter(val => val);
};