import {createContext} from 'react';

export type AssetReader = (path:string, init?:RequestInit)=>Promise<Response>;
export const siteAssets:AssetReader = (path, init)=>fetch(import.meta.env.BASE_URL+path, init);
export const ObservatoryAssets = createContext(siteAssets);

export function folderAssets(files:FileList):AssetReader {
 const assets = new Map<string,File>();
 for(const file of files){
  const path = file.webkitRelativePath.split('/').slice(1).join('/');
  if(path.startsWith('data/')||path.startsWith('geo/')) assets.set(path,file);
 }
 if(!assets.has('data/index.json')||!assets.has('geo/index.json')){
  throw new Error('Selecciona la carpeta frontend/public con las subcarpetas data y geo.');
 }
 return async (path,init)=>{
  init?.signal?.throwIfAborted();
  const file = assets.get(path);
  return file ? new Response(file) : new Response(null,{status:404});
 };
}
