import { defineConfig } from 'vite';
export default defineConfig(({mode})=>({
 base:'./',
 publicDir:mode==='pages'?false:'public',
 build:{outDir:mode==='pages'?'dist-pages':'dist'},
 server:{host:'127.0.0.1',port:5173,strictPort:true},
}));
