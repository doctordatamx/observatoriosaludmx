export type ProfileCube = {
 states:string[]; causes:string[]; municipalities?:string[];
 rows:[number,number,number,number,number,number,number?][];
};
export type ProfileScope = {state:string;municipality:string;sex:string;age:string;cause:string};
export function countProfile(cube:ProfileCube, scope:ProfileScope) {
 if(scope.municipality&&!cube.municipalities) return null;
 const state=scope.state?cube.states.indexOf(scope.state):null;
 const municipality=scope.municipality?cube.municipalities!.indexOf(scope.municipality):null;
 const cause=cube.causes.indexOf(scope.cause);
 let count=0, denominator=0;
 for(const row of cube.rows){
  if((state!==null&&row[0]!==state)||(municipality!==null&&row[6]!==municipality)
   ||(scope.sex&&row[1]!==Number(scope.sex))||(scope.age&&row[2]!==Number(scope.age))) continue;
  denominator+=row[5];
  if(row[4]===cause)count+=row[5];
 }
 return {count,denominator};
}
export function profileFile(national:string, municipal:string|undefined, scope:ProfileScope){
 return scope.municipality?municipal: national;
}

type AnnualCount = {year:number; partial:boolean; count:number|null};
export function yearOverYear(current:AnnualCount, previous?:AnnualCount) {
 if (!previous || previous.year !== current.year - 1 || previous.partial || current.partial
   || previous.count === null || previous.count <= 0 || current.count === null) return null;
 return 100 * (current.count - previous.count) / previous.count;
}
