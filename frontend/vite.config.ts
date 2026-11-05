import { defineConfig } from 'vite';
import { execFileSync } from 'node:child_process';

function commitId(){
 try {
  return execFileSync('git',['rev-parse','--short=12','HEAD'],{encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();
 } catch {
  return 'desconocido';
 }
}

export default defineConfig(({mode,command})=>({
 base:'./',
 publicDir:mode==='pages'?false:'public',
 build:{outDir:mode==='pages'?'dist-pages':'dist'},
 define:{
  __BUILD_COMMIT__:JSON.stringify(commitId()),
  __BUILD_AT__:JSON.stringify(command==='build'?new Date().toISOString():null),
 },
 server:{host:'127.0.0.1',port:5173,strictPort:true},
}));
