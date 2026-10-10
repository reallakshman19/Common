import test from 'node:test';
import assert from 'node:assert/strict';
import {PINNED_SOURCE_HEAD,FAILURES,classifyTap} from './t36-full-suite-red-baseline.mjs';
const names=Object.values(FAILURES).flat();
const tap=(list=names,summary={tests:283,pass:262,fail:21,skipped:0})=>
 list.map((n,i)=>'not ok '+(i+1)+' - '+n).join('\n')+'\n'+
 Object.entries(summary).map(([k,v])=>'# '+k+' '+v).join('\n')+'\n';
test('T36 exactly 21 named RED original regressions are an immutable negative witness only',()=>{
 const x=classifyTap(tap(),1);
 assert.equal(names.length,21);
 assert.equal(x.source_head,PINNED_SOURCE_HEAD);
 assert.equal(x.result,'EXACT_21_FAILURE_RED_BASELINE_REPRODUCED');
 assert.deepEqual(x.failures_by_group,{T03:3,T05:3,T14:7,PHYSICAL_U01_U04:8});
 assert.equal(x.evidence_admitted,false);
 assert.equal(x.required_ci_qualified,false);
 assert.equal(x.release_ready,false);
 assert.equal(x.writer_authorized,false);
});
test('T36 green suite, extra failure, missing historical failure and wrong summary refuse',()=>{
 const cases=[
  [tap(),0], // 21 failing tests but a false success process
  [tap(names.slice(1)),1],
  [tap([...names,'extra unapproved regression']),1],
  [tap(names,{tests:283,pass:263,fail:20,skipped:0}),1],
  [tap(names,{tests:282,pass:261,fail:21,skipped:0}),1],
  [tap(names,{tests:283,pass:262,fail:21,skipped:1}),1],
  [tap([names[0],names[0],...names.slice(2)]),1],
 ];
 for(const [s,exit] of cases){
  const x=classifyTap(s,exit);
  assert.equal(x.result,'BASELINE_UNVERIFIED');
  assert.equal(x.evidence_admitted,false);
 }
});
test('T36 historical failure manifest protects every separate original group and stable names',()=>{
 for(const [group,entries] of Object.entries(FAILURES)){
  assert.ok(entries.length>0,group);
  for(const n of entries){
   const x=classifyTap(tap(names.filter(x=>x!==n)),1);
   assert.equal(x.result,'BASELINE_UNVERIFIED',group+':'+n);
   assert.ok(x.missing_expected_names.includes(n));
  }
 }
});
