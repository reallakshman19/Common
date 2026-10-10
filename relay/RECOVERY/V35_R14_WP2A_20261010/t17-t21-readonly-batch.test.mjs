import test from 'node:test';import assert from 'node:assert/strict';import {t17,t18,t19,t20,t21} from './t17-t21-readonly-batch.mjs';
const H='a'.repeat(40),I={repository:'reallakshman19/Common',repository_id:1412133785,pr_number:315,head_sha:H,base_branch:'codex/294-t13-r4-readonly-index-candidate'};
const r={authority:'DIAGNOSIS_ONLY_CALLER_INJECTED_UNATTESTED',tested_head_sha:H,pr_number:315,evidence_admitted:false,positive_ci_qualified:false,u02_failure_reason:'SELECTED_CHECKS_DRIFT',selected_delta:{classification:'TRANSITION_ONLY',first_count:34,second_count:34,added_count:0,removed_count:0,transition_count:1,details_truncated:false,details:[{run_id:123,change:'TRANSITION',old_state:'in_progress',new_state:'completed',name:'PRIVATE'}]}};
const U={diagnostic_only:true,source_grade:'CALLER_INJECTED_UNATTESTED',source_material_attested:false,positive_fact_admitted:false,original_u04_failure_stage:'JOIN',original_u04_failure_reason:'JOIN_U03_SOURCE_UNVERIFIED',u03_rounds:[{material_observed:false,failure_stage:'FIRST_READ',failure_reason:'COMMENT_GET_UNVERIFIED',outer_round:'FIRST'}]};
const c={status:200,data:{contexts:[],checks:[]}},p={status:200,data:[]};
test('T17 real-state transition is bounded by job id, with no name',async()=>{const x=await t17(I,async()=>r,async()=>({}));assert.equal(x.delta.first_job_id,123);assert.equal(x.verdict,'SELECTED_CHECKS_DRIFT');assert.ok(!JSON.stringify(x).includes('PRIVATE'));assert.equal(x.evidence_admitted,false)});
test('T17 forged accepted candidate and bad repo refuse',async()=>{const x=await t17({...I,repository:'reallaksh19/Common'},async()=>r,async()=>({}));assert.equal(x.delta,null)});
test('T17 reader error never discloses secret',async()=>{const x=await t17(I,async()=>{throw Error('MY_SECRET')},async()=>({}));assert.equal(x.verdict,'SOURCE_UNVERIFIED');assert.ok(!JSON.stringify(x).includes('MY_SECRET'))});
test('T18 actual nested U03 first read is a diagnostic-only cause',()=>{const x=t18(U);assert.equal(x.inner.reason,'COMMENT_GET_UNVERIFIED');assert.equal(x.evidence_admitted,false)});
test('T18 outer JOIN alone is not evidence of inner root',()=>{const x=t18({...U,u03_rounds:[{material_observed:true}]});assert.equal(x.inner,null);assert.equal(x.verdict,'INNER_REASON_NOT_CAPTURED')});
test('T18 refuse leaked provider error',()=>{const x=t18({...U,u03_rounds:[{material_observed:false,failure_stage:'FIRST_READ',failure_reason:'SECRET TOKEN'}]});assert.equal(x.inner,null)});
test('T19 real 200 empty is diagnostic, never effective clearance',()=>{const x=t19(c,p);assert.equal(x.reason,'EMPTY_POLICY_READABLE');assert.equal(x.required_ci_qualified,false)});
test('T19 403 classic is UNKNOWN, never empty',()=>{const x=t19({status:403},p);assert.equal(x.policy,'UNKNOWN')});
test('T19 rules 404 is UNKNOWN and malformed 200 is UNKNOWN',()=>{assert.equal(t19(c,{status:404}).policy,'UNKNOWN');assert.equal(t19(c,{status:200,data:[{type:'required_status_checks'}]}).policy,'UNKNOWN')});
test('T20 V3.1 missing workflows remain explicit',()=>{const x=t20(['.github/workflows/other.yml']);assert.equal(x.missing.length,2);assert.equal(x.release_ready,false)});
test('T20 restored paths alone do not grant release',()=>{const x=t20(['.github/workflows/engineering-pr-delivery-v2.5.yml','.github/workflows/engineering-pr-delivery-v3.yml']);assert.equal(x.verdict,'LEGACY_PATHS_PRESENT');assert.equal(x.release_ready,false)});
test('T20 forged relative path refused',()=>{assert.equal(t20(['../bad']).verdict,'INVENTORY_UNVERIFIED')});
const V=()=>({ci:{schema:'v35-294-t17',evidence_admitted:false,writer_authorized:false,verdict:'DIAGNOSTIC_ONLY',delta:{}},u03:{schema:'v35-294-t18',evidence_admitted:false,writer_authorized:false,verdict:'NO_U03_REFUSAL_IN_SAMPLE'},policy:{schema:'v35-294-t19',evidence_admitted:false,writer_authorized:false,policy:'OBSERVED_DIAGNOSTIC_ONLY'},legacy:{schema:'v35-294-t20',evidence_admitted:false,writer_authorized:false,verdict:'LEGACY_PATHS_PRESENT'}});
test('T21 missing inputs fail closed',()=>{assert.equal(t21({}).first_failed_edge,'INPUT_UNVERIFIED')});
test('T21 U02 refusal has first priority',()=>{const v=V();v.ci.verdict='SELECTED_CHECKS_DRIFT';assert.equal(t21(v).first_failed_edge,'U02')});
test('T21 unknown policy stays HOLD',()=>{const v=V();v.policy.policy='UNKNOWN';assert.equal(t21(v).first_failed_edge,'REQUIRED_POLICY')});
test('T21 all diagnostic probes clear still never authorize release',()=>{const x=t21(V());assert.equal(x.verdict,'DIAGNOSTICS_CLEAR_NO_AUTHORITY');assert.equal(x.release_ready,false);assert.equal(x.delp_projection,'NOT_CALCULATED')});
test('T21 forged evidence cannot pass',()=>{const v=V();v.u03.evidence_admitted=true;assert.equal(t21(v).first_failed_edge,'INPUT_UNVERIFIED')});

test('T22 reject contradictory U02 check count and membership arithmetic',async()=>{
 const x=structuredClone(r);x.selected_delta.second_count=35;
 const y=await t17(I,async()=>x,async()=>({}));
 assert.equal(y.verdict,'SOURCE_UNVERIFIED');assert.equal(y.delta,null);assert.equal(y.evidence_admitted,false);
});
test('T22 reject drift reason with stable set and forged native admission',async()=>{
 const x=structuredClone(r);x.selected_delta={classification:'STABLE',first_count:34,second_count:34,added_count:0,removed_count:0,transition_count:0,details:[],details_truncated:false};
 assert.equal((await t17(I,async()=>x,async()=>({}))).delta,null);
 const y=structuredClone(r);y.authority='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
 assert.equal((await t17(I,async()=>y,async()=>({}))).delta,null);
});
test('T22 reject oversized or malformed selected vectors',async()=>{
 for(const mutation of [
  d=>{d.first_count=201},d=>{d.transition_count=-1},d=>{d.details_truncated='true'},
  d=>{d.classification='MEMBERSHIP_ONLY'},
 ]){
  const x=structuredClone(r);mutation(x.selected_delta);
  assert.equal((await t17(I,async()=>x,async()=>({}))).delta,null);
 }
});
