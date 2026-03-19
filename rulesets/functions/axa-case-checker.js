// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.

// for oas3
// given: '$'

function constructErrorMessage(validator, property, value, failedRegexes) {
  return `${validator}: ${property}: '${value}' is not ${
    failedRegexes.length > 1
      ? `any of ${failedRegexes.map(a => a.name).join(', ')}`
      : failedRegexes[0].name
  }`;
}

function matchesRegexes(value, regexes) {
  return regexes
    .map(regex => regex.implementation.test(value))
    .reduce((accumulator, current) => accumulator || current, false);
}

function uniqueErrors(errors) {
  const errorsMap = {};

  errors.forEach(error => {
    errorsMap[error.message] = error;
  });

  return Object.values(errorsMap);
}

function mergeErrors(errors) {
  // it seems that Spectral only print the first message of the list.
  // TODO : look at https://meta.stoplight.io/docs/spectral/docs/guides/5-custom-functions.md
  // to include different path for each message

  if (!(errors && errors.length)) return []

  const withoutPath = errors.filter(a=>!a.path)
  const withPath = errors.filter(a=>a.path)
  const withoutPathJoined = [
    {"message":withoutPath
      .filter(a => a.message)
      .map(a => a.message)
      .join("; ")
    }]
    .filter(a => a.message)
  //console.log("RETURNED ERROR");console.log(withoutPathJoined.concat(withPath))
  return withoutPathJoined.concat(withPath)
}

function enumValues(target, regexes) {
  // TODO : don't catch some ENUM, such as object with sub object with enum
  const fromPaths = Object.entries(target.paths)
    .flatMap(([path, pathDefinition]) =>
      Object.entries(pathDefinition)
        .filter(([, verbDefinition]) => verbDefinition.parameters)
        .flatMap(([verb, verbDefinition]) =>
          verbDefinition.parameters
            .filter(
              parameterDefinition =>
                parameterDefinition && parameterDefinition.schema && parameterDefinition.schema.enum
            )
            .flatMap(parameterDefinition =>
              parameterDefinition.schema.enum.flatMap(enumValue =>
                matchesRegexes(enumValue, regexes)
                  ? undefined
                  : {
                      message: constructErrorMessage(
                        'enumValues',
                        `parameter ${parameterDefinition.name} of ${verb} ${path}`,
                        enumValue,
                        regexes
                      )
                      // TODO : add path

                    }
              )
            )
        )
    )
    .filter(a => a);

  const fromSchemas = Object.entries(target.components.schemas)
    .filter(
      ([, definition]) =>
        definition.allOf && definition.allOf.some(item => item.properties)
    )
    .flatMap(([key, definition]) =>
      definition.allOf
        .filter(item => item.properties)
        .flatMap(item =>
          Object.entries(item.properties)
            .filter(([, property]) => property.enum)
            .flatMap(([propertyKey, property]) =>
              property.enum.map(enumValue =>
                matchesRegexes(enumValue, regexes)
                  ? undefined
                  : {
                      message: constructErrorMessage(
                        'enumValues',
                        `property ${propertyKey} of ${key}`,
                        enumValue,
                        regexes
                      )
                      // TODO : add path

                    }
              )
            )
        )
    )
    .filter(a => a);

  return fromPaths.concat(fromSchemas);
}

function pathParameters(target, regexes) {
  return Object.keys(target.paths)
    .map(path =>
      (path.match(/({\w*})/g) || []).map(match => {
        const parameter = match.substring(1, match.length - 1);

        return matchesRegexes(parameter, regexes)
          ? undefined
          : {
              message: constructErrorMessage(
                'pathParameters',
                path,
                parameter,
                regexes
              ),
              path:['paths',path]
            };
      })
    )
    .filter(a => a);
}

function pathSegments(target, regexes) {
  return Object.keys(target.paths)
    .map(path =>
      path
        .split('/')
        .filter(a => {
          return a.length && !a.includes('{');
        })
        .map(pathSegment =>
          matchesRegexes(pathSegment, regexes)
            ? undefined
            : {
                message: constructErrorMessage(
                  'pathSegments',
                  `${path}`,
                  pathSegment,
                  regexes
                ),
                path:['paths',path]
              }
        )
    )
    .filter(a => a);
}

function propertyNames(target, regexes) {
  function f(target, regexes, allOf_oneOf){
    return Object.entries(target.components.schemas)
      .filter(
        ([, definition]) =>
        definition[allOf_oneOf] && definition[allOf_oneOf].some(item => item.properties)
      )
      .flatMap(([key, definition]) =>
          definition[allOf_oneOf]
          //TODO : see if there is a simpler way to drag the allOf index until the path.
          .map((item, i)=>{item._index=i;return item})
          .filter(item => item.properties)
          .map(item=>{item.properties._index=item._index;return item})
          // here we have the schema with 'properties' array
          .map(item => {
            const _index = item._index;
            return Object.keys(item.properties).map(property =>
              {
              return "_index"===property || matchesRegexes(property, regexes)
                ? undefined
                : {
                    message: constructErrorMessage(
                      'propertyNames',
                      `property '${property}' of '${key}'`,
                      property,
                      regexes
                    ),
                    path: ['components', 'schemas',key, allOf_oneOf,_index,'properties',property]
                  }
                }
            )
            }
          )
      )
      .filter(a => a);
  }
    const allOf=f(target, regexes, 'allOf')
    const oneOf=f(target, regexes, 'oneOf')

    const withoutAllOf = Object.entries(target.components.schemas)
      .filter(
        ([, definition]) =>
          definition.properties
      )
      .flatMap(([key, definition])=>
            Object.keys(definition.properties).map(property =>
              {
              return matchesRegexes(property, regexes)
                ? undefined
                : {
                    message: constructErrorMessage(
                      'propertyNames',
                      `property '${property}' of '${key}'`,
                      property,
                      regexes
                    ),
                    path: ['components', 'schemas',key,'properties',property]
                  }
                }
            )
      )
      .filter(a => a);

      return allOf.concat(oneOf).concat(withoutAllOf)
}

function queryParameters(target, regexes) {
  return Object.entries(target.paths)
    .flatMap(([path, pathValue]) => {
      return Object.entries(pathValue).map(([verb, verbValue]) => {
        return (verbValue.parameters || [])
          .filter(a => a.in === 'query')
          .map((queryParam,i) =>
            matchesRegexes(queryParam.name, regexes)
              ? undefined
              : {
                  message: constructErrorMessage(
                    'queryParameters',
                    `a ${verb} ${path} queryParam`,
                    queryParam.name,
                    regexes
                  ),
                  path: ['paths',path, verb,'parameters',i,'name']
                }
          );
      });
    })
    .filter(a => a);
}

function schemaKeys(target, regexes) {
  return Object.keys(target.components.schemas)
    .map(key =>
      matchesRegexes(key, regexes)
        ? undefined
        : {
            message: constructErrorMessage('schemaKeys', 'schema', key, regexes),
            path: ['components','schemas', key]

          }
    )
    .filter(a => a);
}

module.exports = (targetValue, options, paths) => {
  const { cases, validations } = options;

  const validators = {
    enumValues,
    pathParameters,
    pathSegments,
    propertyNames,
    queryParameters,
    schemaKeys
  };

  if (!cases) {
    return [
      {
        message:
          'Missing cases option. Expected an object containing the regexes to use'
      }
    ];
  }

  if (!validations || !Object.keys(validations).length) {
    return [
      {
        message:
          'Missing validations option. Expected an object with the validations to run'
      }
    ];
  }

  Object.keys(cases).forEach(key => {
    const regexpString = cases[key];

    const regexp = new RegExp(regexpString);

    cases[key] = regexp;
  });

  const errors = Object.entries(validations)
    .flatMap(([validationKey, regexKeys]) => {
      if (!regexKeys || !Array.isArray(regexKeys) || !regexKeys.length) {
        return {
          message: `No regexes to test for ${validationKey}`
        };
      }

      const regexes = regexKeys
        .map(key => ({ name: key, implementation: cases[key] }))
        .filter(a => a && a.implementation);

      if (!regexes.length || regexes.length !== regexKeys.length) {
        return {
          message: `Mismatch between defined and existing regexes in ${validationKey}`
        };
      }

      const validator = validators[validationKey];

      if (!validator) {
        return {
          message: `No validator function implemented for ${validationKey}`
        };
      }

      return validator(targetValue, regexes);
    })
    .flat()
    .filter(a => a);

  return mergeErrors(uniqueErrors(errors));
};