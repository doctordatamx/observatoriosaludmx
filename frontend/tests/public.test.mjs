import assert from 'node:assert/strict';
import {mkdtemp, rm} from 'node:fs/promises';
import {pathToFileURL, fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {test} from 'node:test';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {build} from 'vite';

test('public module links resolve to an availability notice or methodology', async () => {
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
   assert.match(html,view==='metodologia'?/Qué se puede interpretar en esta versión/:/Datos no disponibles en la edición pública/);
  }
 } finally {
  delete globalThis.location;
  await rm(outDir,{recursive:true,force:true});
 }
});
