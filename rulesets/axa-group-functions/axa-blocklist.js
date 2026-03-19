// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options, path) => {
  const blocklist = options.blocklist.map(a =>a.toUpperCase());

  if (!blocklist || !Array.isArray(blocklist)) {
    return [
      {
        message:
          'Missing blocklist option. Expected an array of strings containing restricted words'
      }
    ];
  }
  return blocklist.includes(targetValue.toUpperCase())
    ? [{
        message: `'${targetValue}' is on the blocklist`,
        path: path.target
      }]
    : undefined;
};