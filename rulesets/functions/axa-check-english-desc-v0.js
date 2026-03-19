 function checkString(s,words){
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
 module.exports = (targetValue, options, paths) => {
  try{  
	//if a parameter description exist in schema there is a problem to ascertain
	var desc;
	if(Object.keys(targetValue).includes('description')){
	desc = targetValue.description;	
	}else if(Object.keys(targetValue).includes('type')){
	desc = targetValue.type
	}	
	else{	
	desc = Object.values(targetValue).join('');
	}

	var checkWord = require('check-word');
	const words = checkWord('en');
	var check;
	
	var punctuationless = desc.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g," ");
	var finalString = punctuationless.replace(/\s{2,}/g," ");
	const path_arr = finalString.split(" ");
	
	
	if(path_arr.length>6){
	//use language library instead of word dictionary
	const LanguageDetect = require('languagedetect');
	const lngDetector = new LanguageDetect();
	lngDetector.setLanguageType('iso2');
	const ldet = lngDetector.detect(finalString,3);
		if(ldet.toString().includes('en')){
			check = false
		}else{
			check = true
		}

	}else{	
	path_arr.some(word=>{
				if(! (word == '')){
				check = checkString(word,words);
				
				}
				return check;
			})
	}
	if (check) {
		return [{
			message: `'${desc}' is not in english language`
		}];
	}
return undefined;
		
	}catch(e){
	  console.error("Exception thrown", e.stack);
	}	
};

