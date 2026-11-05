import assert from 'node:assert/strict';
import {test} from 'node:test';
import {yearOverYear} from '../src/profileData.ts';
import {aggregate,readCube} from '../src/aggregate.ts';

test('schema mismatch fails instead of displaying an empty or simulated query',()=>{
 const payload={schema_version:1,states:['19'],causes:['E11'],rows:[[0,2,14,1,0,12]]};
 assert.throws(()=>readCube(payload,true),/esquema incompatible/);
 assert.throws(()=>readCube({rows:[]},false),/esquema incompatible/);
 const result=aggregate(readCube(payload,false),{state:'19',sex:'2',age:'14',cause:'E11',municipality:''});
 assert.equal(result.total,12);
 assert.equal(result.causes.E11/result.total,1);
 assert.equal(result.women[14],12);
 assert.equal(result.temporal[1],12);
});

test('interannual change uses the previous full year as denominator',()=>{
 const prior={year:2024,partial:false,count:40};
 assert.equal(yearOverYear({year:2025,partial:false,count:50},prior),25);
 assert.equal(yearOverYear({year:2025,partial:false,count:0},prior),-100);
});

test('missing, partial, non-consecutive and zero-reference periods have no change value',()=>{
 const current={year:2025,partial:false,count:50};
 const prior={year:2024,partial:false,count:40};
 assert.equal(yearOverYear(current),null);
 assert.equal(yearOverYear({...current,partial:true},prior),null);
 assert.equal(yearOverYear({...current,count:null},prior),null);
 assert.equal(yearOverYear(current,{...prior,partial:true}),null);
 assert.equal(yearOverYear(current,{...prior,year:2023}),null);
 assert.equal(yearOverYear(current,{...prior,count:0}),null);
 assert.equal(yearOverYear(current,{...prior,count:null}),null);
});
