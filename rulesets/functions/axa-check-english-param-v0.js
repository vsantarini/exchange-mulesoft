 function checkString2(s,words){
	var result;
	
		if(s.includes("-")){
			const path_arr = s.split("-");
			path_arr.every(word=>{
				word = word.toLowerCase();
				result = ! words.check(word);
				if(result){
					return false;
				}
				
			})
		}else if (s.includes("_")){
			const path_arr = s.split("_");
			path_arr.every(word=>{
				word = word.toLowerCase();
				return result = ! words.check(word);
				if(result){
					return false;
				}
			})
		}else if(s.match(/\b[A-Z][A-Z0-9]+\b/)){
			s = s.toLowerCase();	
			result = ! words.check(s);
				if(result){
					return false;
				}		
		}else if(s.match(/([A-Z]?[^A-Z]*)/g).slice(0,-1).length>1){
			const path_arr = s.match(/([A-Z]?[^A-Z]*)/g).slice(0,-1);
			path_arr.every(word=>{
				word = word.toLowerCase();
				result = ! words.check(word);
				if(result){
					return false;
				}
				
			}) 
		}else{	
		s = s.toLowerCase();	
		result = ! words.check(s);
		}
			
	 return result
 }
 function checkString(s,words){
	var result;
	var punctuationless = s.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g," ");
	var finalString = punctuationless.replace(/\s{2,}/g," ");
	if( finalString.match(/([A-Z]?[^A-Z]*)/g).slice(0,-1).length>1 ){
		finalString = finalString.match(/([A-Z]?[^A-Z]*)/g).slice(0,-1).join(" ");
	}
	const path_arr = finalString.split(" ");
		if (path_arr.length >1){
			path_arr.some(word=>{	
				word = word.toLowerCase();
				result = ! (words.check(word));
				return result;
			});
		}else{
		s = finalString.toLowerCase();	
		result = ! (words.check(s));
		}		
	 return result
 }
 
 module.exports = (targetValue) => { 
  const isEmpty = Object.keys(targetValue).length === 0;
  if(isEmpty){
	  return{
		  message: `no element found, malformed swagger`
	  };
  } 
  try{  
	var path = Object.values(targetValue).join('');
	var checkWord = require('check-word');
	const words = checkWord('en');
	var check;
	
		if (path.includes("/")){
			const path_arr = path.split("/").slice(1,path.split("/").length);
			path_arr.some(word=>{			
				if(word.includes("{")){
				word = word.replace("}","").replace("{","");
				}
				
				check = checkString2(word,words);

				return check;
			})
		}else{	    	
		check = checkString2(path,words);
		}
	
	if (check) {
		return [{
			message: `'${path}' is not in english language`
		}];
	}
return undefined;
		
	}catch(e){
	  console.error("Exception thrown", e.stack);
	}	
};

