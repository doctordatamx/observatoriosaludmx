import assert from 'node:assert/strict';
import {test} from 'node:test';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {countProfile,profileFile} from '../src/profileData.ts';
const scope={state:'19',municipality:'',sex:'2',age:'14',cause:'E11'};
const read=(path)=>JSON.parse(gunzipSync(readFileSync(new URL('../public/data/'+path,import.meta.url))));
test('real filtered 2024 mortality matches the independently verified Nuevo Leon result',()=>{
 const value=countProfile(read('defunciones-2024.json.gz'),scope);
 assert.equal(value.count,184);
 assert.ok(value.denominator>value.count);
});
test('municipal count matches previously verified Monterrey profile',()=>{
 const cube=read('municipal/defunciones-2024/19.json.gz');
 const result=countProfile(cube,{...scope,municipality:'19039',sex:'',age:'',cause:'E11'});
 assert.equal(result.denominator,9859);
 assert.ok(result.count>0&&result.count<9859);
});
test('missing municipal data cannot be substituted by a national file',()=>{
 const filter={...scope,municipality:'19039'};
 assert.equal(profileFile('state.gz',undefined,filter),undefined);
 assert.equal(countProfile({states:['19'],causes:['E11'],rows:[]},filter),null);
});
test('absence of cause and age group zero have distinct meanings',()=>{
 const cube={states:['19'],causes:['E11','A19'],rows:[[0,2,0,1,1,7],[0,2,1,1,0,3]]};
 assert.deepEqual(countProfile(cube,{...scope,age:'0'}),{count:0,denominator:7});
});
