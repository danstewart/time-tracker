const pascalToKebab=str=>str[0].toLowerCase()+str.slice(1,str.length).replace(/[A-Z0-9]/g,letter=>`-${letter.toLowerCase()}`);const kebabToCamel=str=>str[0].toLowerCase()+str.slice(1,str.length).replace(/-([a-z0-9])/g,letter=>`${letter[1].toUpperCase()}`);const permutations=(arr,toString=false)=>{let chunks={};chunks[1]=arr.map(item=>[item]);for(let targetLen=2;targetLen<=arr.length;targetLen++){let newChunk=[];for(let permutation of chunks[targetLen-1]){for(let item of arr){if(permutation.includes(item))continue;newChunk.push([item,...permutation])}}chunks[targetLen]=newChunk}let results=Object.values(chunks);if(toString){let formattedResults=[];for(let group of results){for(let permutation of group){formattedResults.push(permutation.join(""))}}return formattedResults}return results};const parseDuration=duration=>{const[_,interval,unit]=/(\d+)(\w+)/.exec(duration);let timeout=0;switch(unit){case"ms":timeout=interval;break;case"s":timeout=interval*1e3;break;case"m":timeout=interval*1e3*60;break;case"h":timeout=interval*1e3*60*60;break}return timeout};const template=(strings,...values)=>{return strings.reduce((acc,str,i)=>{return acc+str+(values[i]||"")},"")};const parseBoolean=value=>{if(!value||value==""||value=="0"){return false}if(value&&value.toLowerCase&&value.toLowerCase()=="false"){return false}return true};export{pascalToKebab,kebabToCamel,permutations,parseDuration,template as html,template as css,parseBoolean}
//# sourceMappingURL=util.js.map