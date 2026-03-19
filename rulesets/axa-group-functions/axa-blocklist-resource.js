// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options) => {

  if (!options.blocklist || !Array.isArray(options.blocklist)) {
    return [
      {
        message:
          'Missing blocklist option. Expected an array of strings containing restricted words'
      }
    ];
  }
  
  const blocklist = options.blocklist.map(a =>a.toUpperCase());

  return Object.keys(targetValue)
    .map(path => {
      const resource = path.split('/').slice(-1).pop() || '';

      return blocklist.includes(resource.toUpperCase())
        ? {
            message: `'${path}' includes '${resource}' which is on the blocklist`,
            path: ['paths', path]
          }
        : undefined;
    })
    .filter(val => val);
};