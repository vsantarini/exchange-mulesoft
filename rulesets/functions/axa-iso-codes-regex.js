
module.exports = (targetValue, options, paths) => {

  var error = []
  
  Object.values(targetValue).forEach((elem, index)=>{
  const isString = elem.type==="string"
  const inDescr = elem.description && (elem.description.includes("ISO")) 
  const inFormat = elem.format && (elem.format.includes("ISO"))
  
  // if we detected an iso use case
  if ( isString && (inDescr || inFormat)) {
    if (! (elem.pattern)){
        error.push(
          {
            message: `the parameter '${Object.keys(targetValue)[index]}' does not define a pattern property with the associated regex`
          })
      }else{
		  const regValidator = new RegExp(elem.pattern);
		  if(elem.example){
		  if (! (regValidator.test(elem.example))){
            error.push(
			{
                message: `the example given for the parameter '${Object.keys(targetValue)[index]}' does not match the pattern '${elem.pattern}' used`,
              });
	  }
    }
	  }
  }
})
  return error

};