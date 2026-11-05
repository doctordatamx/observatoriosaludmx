import assert from 'node:assert/strict';
import {test} from 'node:test';
import {yearOverYear} from '../src/profileData.ts';

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
