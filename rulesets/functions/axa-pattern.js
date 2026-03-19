module.exports = (targetValue, options, paths) => {
  if (!options.pattern) {
    return [
      {
        message:
          "Missing 'pattern' in functionOptions "
      }
    ];
  }
const pattern = options.pattern
const pattern_validator = new RegExp(pattern); 
return  pattern_validator.test(targetValue)
             ? undefined 
            : [{
                message: `'${targetValue}' : must be kebab case`,
				path: paths.target
              }];
};