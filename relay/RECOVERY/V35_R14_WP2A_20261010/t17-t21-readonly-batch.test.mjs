import test from 'node:test';import assert from 'node:assert/strict';import {t17,t18,t19,t20,t21,t26U03SourceScope} from './t17-t21-readonly-batch.mjs';
const H='a'.repeat(40),I={repository:'reallakshman19/Common',repository_id:1412133785,pr_number:315,head_sha:H,base_branch:'codex/294-t13-r4-readonly-index-candidate'};
const r={authority:'DIAGNOSIS_ONLY_CALLER_INJECTED_UNATTESTED',tested_head_sha:H,pr_number:315,evidence_admitted:false,positive_ci_qualified:false,u02_failure_reason:'SELECTED_CHECKS_DRIFT',selected_delta:{classification:'TRANSITION_ONLY',first_count:34,second_count:34,added_count:0,removed_count:0,transition_count:1,details_truncated:false,details:[{run_id:123,change:'TRANSITION',old_state:'in_progress',new_state:'completed',name:'PRIVATE'}]}};
const U={diagnostic_only:true,source_grade:'CALLER_INJECTED_UNATTESTED',source_material_attested:false,positive_fact_admitted:false,original_u04_failure_stage:'JOIN',original_u04_failure_reason:'JOIN_U03_SOURCE_UNVERIFIED',original_u04_failure_round:'FIRST',result_class:'U03_NESTED_REFUSAL_CAUSES_JOIN',u03_round_count:1,original_u04_subreader_calls:3,no_extra_subreader_calls:true,u03_rounds:[{material_observed:false,failure_stage:'FIRST_READ',failure_reason:'COMMENT_GET_UNVERIFIED',outer_round:'FIRST'}]};
const c={status:200,page_complete:true,data:{contexts:[],checks:[]}},p={status:200,page_complete:true,data:[]};
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
const V=()=>({ci:{schema:'v35-294-t17',evidence_admitted:false,writer_authorized:false,verdict:'DIAGNOSTIC_ONLY',delta:{classification:'STABLE'}},u03:{schema:'v35-294-t18',evidence_admitted:false,writer_authorized:false,verdict:'NO_U03_REFUSAL_IN_SAMPLE'},u03_scope:{schema:'v35-294-t26-u03-source-scope-v1',evidence_admitted:false,writer_authorized:false,relationship:'SAME_HEAD_DIAGNOSTIC_ONLY'},policy:{schema:'v35-294-t19',evidence_admitted:false,writer_authorized:false,policy:'OBSERVED_DIAGNOSTIC_ONLY'},legacy:{schema:'v35-294-t20',evidence_admitted:false,writer_authorized:false,verdict:'LEGACY_PATHS_PRESENT'}});
test('T21 missing inputs fail closed',()=>{assert.equal(t21({}).first_failed_edge,'INPUT_UNVERIFIED')});
test('T21 U02 refusal has first priority',()=>{const v=V();v.ci.verdict='SELECTED_CHECKS_DRIFT';assert.equal(t21(v).first_failed_edge,'U02')});
test('T21 unknown policy stays HOLD',()=>{const v=V();v.policy.policy='UNKNOWN';assert.equal(t21(v).first_failed_edge,'REQUIRED_POLICY')});
test('T21 all diagnostic probes clear still never authorize release',()=>{const x=t21(V());assert.equal(x.verdict,'HOLD_DIAGNOSTIC');assert.equal(x.first_failed_edge,'EFFECTIVE_CI_AND_V31_NOT_QUALIFIED');assert.equal(x.release_ready,false);assert.equal(x.delp_projection,'NOT_CALCULATED')});
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

test('T23 missing or invented outer U04 round cannot become first-round U03 root',()=>{
 for(const forged of [undefined,'THIRD','SECOND']){
  const x=structuredClone(U);
  x.u03_rounds[0].outer_round=forged;
  assert.equal(t18(x).verdict,'INNER_REASON_NOT_CAPTURED');
  assert.equal(t18(x).inner,null);
 }
});
test('T23 require original U04 round and exact subreader count',()=>{
 const wrong=structuredClone(U);wrong.original_u04_failure_round='SECOND';
 assert.equal(t18(wrong).inner,null);
 const extra=structuredClone(U);extra.original_u04_subreader_calls=7;
 assert.equal(t18(extra).verdict,'UNVERIFIED');
 const badCount=structuredClone(U);badCount.u03_round_count=2;
 assert.equal(t18(badCount).verdict,'UNVERIFIED');
});
test('T23 a U03 failure under another outer JOIN is not an identified U03 root',()=>{
 const x=structuredClone(U);x.original_u04_failure_reason='JOIN_U02_SOURCE_UNVERIFIED';
 assert.equal(t18(x).verdict,'INNER_NOT_CAUSAL');
 assert.equal(t18(x).inner,null);
 const spoof=structuredClone(U);spoof.result_class='DIAGNOSTIC_HISTORICAL_SOURCE_OBSERVED';
 assert.equal(t18(spoof).verdict,'UNVERIFIED');
});

test('T24 app-scoped classic contexts preserve different integration identities',()=>{
 const cl={status:200,page_complete:true,data:{contexts:['build'],checks:[{context:'build',app_id:123},{context:'build',app_id:456}]}};
 const rl={status:200,page_complete:true,data:[{type:'required_status_checks',parameters:{required_status_checks:[{context:'build',integration_id:123}]}}]};
 const x=t19(cl,rl);assert.equal(x.required_count,3);assert.equal(x.reason,'REQUIREMENTS_PRESENT');
 assert.equal(x.required_ci_qualified,false);assert.equal(x.evidence_admitted,false);
});
test('T24 missing pagination proof or explicit next-page condition never means empty',()=>{
 for(const p of [undefined,false]){
  const x=t19(c,{status:200,page_complete:p,data:[]});
  assert.equal(x.policy,'UNKNOWN');assert.equal(x.reason,'POLICY_PAGINATION_UNVERIFIED');
 }
});
test('T24 invalid integration ID and malformed source are UNKNOWN',()=>{
 const bad={status:200,page_complete:true,data:{contexts:[],checks:[{context:'job',app_id:'forged'}]}};
 assert.equal(t19(bad,p).policy,'UNKNOWN');
 const missing={status:200,page_complete:true,data:[{type:'required_status_checks',parameters:{required_status_checks:null}}]};
 assert.equal(t19(c,missing).policy,'UNKNOWN');
});

test('T25 stable diagnostic never implies qualified effective CI, V3.1, or release',()=>{
 const x=t21(V());assert.equal(x.verdict,'HOLD_DIAGNOSTIC');
 assert.equal(x.first_failed_edge,'EFFECTIVE_CI_AND_V31_NOT_QUALIFIED');
 assert.equal(x.release_ready,false);assert.equal(x.evidence_admitted,false);
 assert.ok(x.unproven_gates.includes('V31_EXACT_HEAD'));
});
test('T25 observed U03 original fault has priority over readable policy',()=>{
 const v=V();v.u03.verdict='SAME_INVOCATION_U03_REASON';
 const x=t21(v);assert.equal(x.first_failed_edge,'U03');assert.equal(x.writer_authorized,false);
});
test('T25 missing U03 observation is a HOLD even if CI appears stable',()=>{
 const v=V();v.u03.verdict='UNVERIFIED';
 assert.equal(t21(v).first_failed_edge,'U03_UNVERIFIED');
});
test('T25 falsified success flag never escapes inherited negative-only contract',()=>{
 const v=V();v.ci.verdict='ALL_REQUIRED_CHECKS_SUCCESS';
 assert.equal(t21(v).first_failed_edge,'U02');
 const second=V();second.policy.policy='UNKNOWN';
 assert.equal(t21(second).first_failed_edge,'REQUIRED_POLICY');
});

const nativeHistoricalT04=()=>({diagnostic_only:true,source_grade:'CALLER_INJECTED_UNATTESTED',
 source_material_attested:false,positive_fact_admitted:false,
 tested_candidate_head:'4f4dfa0497169d51ab86fbc27db1598121c6f25e'});
test('T26 same original PR306 observation under PR319 cannot be called current-source evidence',()=>{
 const x=t26U03SourceScope(I,nativeHistoricalT04());
 assert.equal(x.relationship,'HISTORICAL_PROXY_NOT_CURRENT');
 assert.equal(x.observer_pr_number,306);
 assert.equal(x.current_pr_u03_verified,false);
 assert.equal(x.evidence_admitted,false);
 assert.equal(x.delp_projection,'NOT_CALCULATED');
});
test('T26 historical PR306 same-head is still a diagnostic, not admitted evidence',()=>{
 const x=t26U03SourceScope({...I,pr_number:306,head_sha:'4f4dfa0497169d51ab86fbc27db1598121c6f25e'},nativeHistoricalT04());
 assert.equal(x.relationship,'SAME_HEAD_DIAGNOSTIC_ONLY');
 assert.equal(x.current_pr_u03_verified,false);
 assert.equal(x.writer_authorized,false);
});
test('T26 missing historical head and forged grades are not qualified',()=>{
 for(const changed of [
  {tested_candidate_head:'a'.repeat(40)},
  {source_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'},
  {positive_fact_admitted:true},
 ]){
  const x=t26U03SourceScope(I,{...nativeHistoricalT04(),...changed});
  assert.equal(x.relationship,'UNVERIFIED');
  assert.equal(x.current_pr_u03_verified,false);
 }
});
test('T26 downstream first-failure edge never treats historical probe as current',()=>{
 const v=V();v.u03_scope=t26U03SourceScope(I,nativeHistoricalT04());
 assert.equal(t21(v).first_failed_edge,'U03_HISTORICAL_PROXY_NOT_CURRENT');
 const x=V();delete x.u03_scope;
 assert.equal(t21(x).first_failed_edge,'INPUT_UNVERIFIED');
});
