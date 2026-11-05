type Row=[number,number,number,number,number,number,number?];
export type Cube={states:string[];causes:string[];municipalities?:string[];rows:Row[]};

export function readCube(value:unknown, municipal:boolean):Cube {
 const cube=value as (Cube & {schema_version?:number})|null;
 if (!cube || cube.schema_version!==(municipal?2:1) || !Array.isArray(cube.states)
   || !Array.isArray(cube.causes) || !Array.isArray(cube.rows)
   || (municipal ? !Array.isArray(cube.municipalities) : cube.municipalities!==undefined)) {
  throw new Error('El agregado tiene un esquema incompatible.');
 }
 return cube;
}

type Filters = {state:string; sex:string; age:string; cause:string; municipality:string};
export function aggregate(cube:Cube|null,{state,sex,age,cause,municipality}:Filters){
  const temporal=Array(13).fill(0) as number[],ages=Array(20).fill(0) as number[],men=Array(20).fill(0) as number[],women=Array(20).fill(0) as number[],sexes:Record<string,number>={},territories:Record<string,number>={},municipalities:Record<string,number>={},causes:Record<string,number>={};let total=0;const heat=Array.from({length:20},()=>Array(13).fill(0));
  if(cube)for(const r of cube.rows){const st=cube.states[r[0]],ca=cube.causes[r[4]],mu=cube.municipalities?.[r[6]??-1];if(municipality&&mu!==municipality)continue;if(state&&st!==state||sex&&String(r[1])!==sex||age&&String(r[2])!==age||cause&&ca!==cause)continue;const n=r[5];total+=n;if(mu)municipalities[mu]=(municipalities[mu]||0)+n;temporal[r[3]]+=n;ages[r[2]]+=n;if(r[1]===1)men[r[2]]+=n;if(r[1]===2)women[r[2]]+=n;sexes[r[1]]=(sexes[r[1]]||0)+n;territories[st]=(territories[st]||0)+n;causes[ca]=(causes[ca]||0)+n;heat[r[2]][r[3]]+=n;}
  return {total,temporal,ages,men,women,sexes,territories,municipalities,causes,heat};
}
