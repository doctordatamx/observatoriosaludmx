import assert from 'node:assert/strict';
import {mkdtemp, rm} from 'node:fs/promises';
import {pathToFileURL, fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {test} from 'node:test';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {build} from 'vite';

test('public views show official totals and keep unavailable modules explicit', async () => {
 const root=fileURLToPath(new URL('..',import.meta.url));
 const outDir=await mkdtemp(join(root,'node_modules','.pages-test-'));
 try {
  await build({root,mode:'pages',logLevel:'silent',build:{ssr:'src/main.tsx',outDir}});
  const {App}=await import(pathToFileURL(join(outDir,'main.js')).href);
  for(const view of ['panorama','enfermedades','atlas','laboratorio','fuentes','metodologia']){
   globalThis.location=new URL('https://example.org/observatoriosaludmx/?view='+view);
   const html=renderToStaticMarkup(createElement(App));
   assert.match(html,/Edición pública/);
   assert.doesNotMatch(html,/Datos reales, lectura provisional|Datos simulados/);
   const expected={
    panorama:/819,672/,
    enfermedades:/192,518/,
    atlas:/Mapa de frecuencias por entidad/,
    metodologia:/Qué se puede interpretar en esta versión/,
   };
   assert.match(html,expected[view]??/Datos no disponibles en la edición pública/);
   if(view==='atlas')assert.match(html,/36,807/);
  }
 } finally {
  delete globalThis.location;
  await rm(outDir,{recursive:true,force:true});
 }
});
