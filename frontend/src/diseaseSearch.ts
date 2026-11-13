export function normalizeSearch(value:string){
 return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es-MX')
  .replace(/[^a-z0-9]+/g,' ').trim();
}

// Aliases identify available three-character categories, not a histological diagnosis.
const aliases:Record<string,string>={
 C18:'cancer ca carcinoma colon',
 C19:'cancer ca rectosigmoide union rectosigmoidea',
 C20:'cancer ca recto',
 C22:'cancer ca higado hepatocarcinoma carcinoma hepatocelular hepatoma',
 C34:'cancer ca pulmon pulmonar bronquios',
 C50:'cancer ca mama seno',
 C61:'cancer ca prostata prostatico',
};

export function matchesDisease(code:string,label:string,query:string){
 const tokens=normalizeSearch(query).split(' ').filter(token=>!['de','del','la','el','los','las'].includes(token));
 const terms=normalizeSearch(code+' '+label+' '+(aliases[code]??'')+(/^C\d{2}$/.test(code)?' cancer ca neoplasia carcinoma':''));
 return tokens.every(token=>terms.split(' ').some(word=>word.includes(token)));
}
