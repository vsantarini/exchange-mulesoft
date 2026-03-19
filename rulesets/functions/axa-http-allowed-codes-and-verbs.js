// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options) => {
  // a whitelist rule:
  // eg:
  // options.allowed = {'200': [ 'ALL' ],'201': [ 'POST', 'PUT']}
  // options.allowedVerbs = [ 'POST', 'GET', 'PUT', 'PATH', 'DELETE' ]

  if (!options.allowed) {
    return [
      {
        message:
          "Missing 'allowed' rule functionOptions. eg : {'200': [ 'ALL' ],'201': [ 'POST', 'PUT']}"
      }
    ];
  }
  if (!options.allowedVerbs) {
    return [
      {
        message:
          "Missing 'allowedVerbs' rule functionOptions. eg: [ 'POST', 'GET', 'PUT', 'PATH', 'DELETE' ]"
      }
    ];
  }

  const allowed = options.allowed;
  const allowedVerbs = options.allowedVerbs;


  return Object.entries(targetValue).flatMap(([pathKey, path]) => {
    //  "Cannot read property 'path' of undefined" if the path have description instead of verbs.
    return Object.entries(path).flatMap(([verb, endpoint]) => {
	  
      if (! endpoint.responses) return []
      return Object.keys(endpoint.responses)
        .map(code => {
          // check verb
          const verbIsAllowed = allowedVerbs.includes(verb.toUpperCase())
          if (!verbIsAllowed) {
            return {
              message: `Verb '${verb}' is not allowed`,
              path: ['paths', pathKey, verb]
            };
          }
          const allowedVerbsByCode = allowed[code];
          // check status code
          if (!allowedVerbsByCode) {
            return {
              message: `Status code '${code}' is not allowed`,
              path: ['paths', pathKey, verb, 'responses', code]
            };
          }
          // check couple verb-status code
          const isAllowed =
            allowedVerbsByCode.includes(verb.toUpperCase())
            || allowedVerbsByCode[0]==='ALL';
          return isAllowed
            ? undefined
            : {
                message: `Status code '${code}' is not allowed for '${verb}'`,
                path: ['paths', pathKey, verb, 'responses', code]
              };
			  
        })
        .filter(val => val)
    })
  });

};