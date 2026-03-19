/**
*Custom spectral function that checks if the casing of the current targetValue matches with the case declared in the options.type
*/
module.exports = (targetValue, options, paths) => {
  if (!options.type) {
    return [
      {
        message:
          "Missing 'type' rule functionOptions eg : 'flat', 'camel', 'pascal', 'kebab', 'cobol', 'snake', 'macro'"
      }
    ];
  }
const case_type = options.type
const CASES = {
    ['flat']:  '^[a-z][a-z0-9]*$',
    ['camel']:  '^[a-z][a-z0-9]*(?:[A-Z0-9](?:[a-z0-9]+|$))*$',//'^[a-z][a-zA-Z0-9]+$',
    ['pascal']: '^[A-Z][a-z0-9]*(?:[A-Z0-9](?:[a-z0-9]+|$))*$',
    ['kebab']:   '^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$',//'^([a-z][a-z0-9]*)(-[a-z0-9]+)*$',
    ['cobol']: '^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$',
    ['snake']: '^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$',//'^([a-z][a-z0-9]*)(_[a-z0-9]+)*$',
    ['macro']: '^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$'
};
 if(!(case_type in CASES)){
	 return [
      {
        message:
          "Wrong 'type' rule functionOptions the possible ones are : 'flat', 'camel', 'pascal', 'kebab', 'cobol', 'snake', 'macro'"
      }
    ];
  } 
  // 2) Skip numerico solo per type === 'macro'
  if (case_type === 'macro') {
    // Se è un number JS -> non applicare la regola
    if (typeof targetValue === 'number') {
      return undefined;
    }
    // Se è una stringa numerica pura (intero o decimale con segno) -> non applicare la regola
    if (
      typeof targetValue === 'string' &&
      /^-?\d+(?:\.\d+)?$/.test(targetValue.trim())
    ) {
      return undefined;
    }
  }
const casingValidator = new RegExp(CASES[case_type]); 
return casingValidator.test(targetValue)
            ? undefined
            : [{
                message: `'${targetValue}' : must be ${case_type} case`,
                path: paths.target
              }];

};
//# sourceMappingURL=casing.js.map