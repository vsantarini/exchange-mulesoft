
module.exports = (targetValue) => {
  var pluralize = require('pluralize')
  const isEmpty = Object.keys(targetValue).length === 0;
  
  if(isEmpty){
	  return{
		  message: `resource is empty, malformed swagger`
	  };
  }
  try{
	
  const path = Object.values(targetValue).join('');
  const resource = path.split('/')[1];
  var check = false ;
  var end_resource = '';
  if(! (path.split('/').length==2)){
	//checks if there are any collections in the path
	if (path.includes("{")){
		return undefined;
	}else{
		end_resource = path.split('/')[path.split('/').length -1];
		}
	}
 if (end_resource == '' ){
	//check on root  
	check = !(resource==(pluralize(resource)));
	return check
        ? [{
            message: `'${path}' includes '${resource}' which is not a plural resource`,
            path: ['paths', path]
          }]: undefined;
	}else{
	//check on last branch  
	check = !(end_resource==(pluralize(end_resource)));
	return check
        ? [{
            message: `'${path}' includes '${end_resource}' which is not a plural resource`,
            path: ['paths', path]
          }]: undefined;	
	}  
      
  }catch(e){
	  console.error("Exception thrown", e.stack);
  }
};
