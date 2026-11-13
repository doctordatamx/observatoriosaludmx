import assert from 'node:assert/strict';
import {test} from 'node:test';
import {matchesDisease,normalizeSearch} from '../src/diseaseSearch.ts';

test('clinical aliases and accent variants find the available category',()=>{
 assert.equal(normalizeSearch('  CÁNCER de HÍGADO '),'cancer de higado');
 for(const query of ['ca de colon','cáncer colon','cancer de colon','C18']){
  assert.ok(matchesDisease('C18','TUMOR MALIGNO DEL COLON',query),query);
 }
 for(const query of ['hepatocarcinoma','cáncer hígado','carcinoma hepatocelular']){
  assert.ok(matchesDisease('C22','TUMOR MALIGNO DEL HÍGADO Y DE LAS VÍAS BILIARES INTRAHEPÁTICAS',query),query);
 }
 assert.equal(matchesDisease('C18','TUMOR MALIGNO DEL COLON','hepatocarcinoma'),false);
 assert.ok(matchesDisease('J18','NEUMONÍA','neumonia'));
});
