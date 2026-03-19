
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
	  var p = path.split('/')
	  //extract the collections  
	   var el = p.map((a, index) => {
		  if (a.includes("{")){
			  return index -1;
			  }; 
			}).filter(function( element ) {
			return element !== undefined;
			});
		
	  if ( ! (el.length==0)){
		 el.forEach( element => {
			var path_element = p[element];
			check = !(path_element==(pluralize(path_element)));
			if(check && (el.length==1)){
				end_resource = path_element
			}else if(check){
				end_resource =  end_resource + path_element +','
			}
		 });
		if(end_resource.split(',')[1]==''){
			end_resource = end_resource.split(',')[0];
		}
	  }
	if (end_resource == '' && ! (check)){
	return undefined;
  }else if (end_resource.includes(',')){
	end_resource = end_resource.substring(0,end_resource.length-1);  
	return [{
	  message: `'${path}' includes '${end_resource}' which are not a plural resource`,
      path: ['paths', path]
	}]
  }else{
	//check on last branch  
	check = !(end_resource==(pluralize(end_resource)));
	return check
        ? [{
            message: `'${path}' includes '${end_resource}' which is not a plural resource`,
            path: ['paths', path]
          }]: undefined;	
  }  
	}
      
  }catch(e){
	  console.error("Exception thrown", e.stack);
  }
};
