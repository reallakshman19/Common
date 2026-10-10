import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizeSourceStageDiagnostics} from './native-source-stage-diagnostic-v1.mjs';
const candidate=()=>({current:true,material_observation:'MATCH_AT_OBSERVATION',errors:[]});
const ci=()=>({selected_checks_observed:true,required_check_policy:'UNKNOWN',required_checks_result:'UNKNOWN',errors:[]});
const evidence=()=>({material_observed:true,source_currentness:'STALE_CANDIDATE_HEAD',errors:[]});
const observe=(a=candidate(),b=ci(),c=evidence())=>summarizeSourceStageDiagnostics(a,b,c);
function held(out){
 assert.equal(out.admission,'NOT_ADMITTED');assert.equal(out.evidence_admitted,false);
 assert.equal(out.programme_progress,null);assert.equal(out.delp_projector_invoked,false);
 assert.equal(out.owner_authenticated,false);assert.equal(out.reviewer_qualified,false);
 assert.equal(out.writer_authorized,false);
 assert.equal(out.basis,'INDEPENDENT_POST_FAILURE_NON_ATOMIC_READS');
}
test('coherent individual stages never imply joined or accepted evidence',()=>{
 const out=observe();held(out);
 assert.deepEqual(Object.values(out.stages).map(x=>x.status),['OBSERVED','OBSERVED','OBSERVED']);
 assert.equal(out.stages.ci.required_policy,'UNKNOWN');
 assert.equal(out.stages.evidence.comment_currentness,'STALE_CANDIDATE_HEAD');
});
test('failed candidate GET is visible independently of CI and comment',()=>{
 const out=observe({current:false,material_observation:'NOT_CURRENT_OR_UNVERIFIED',errors:['PROVIDER_READ_OR_IDENTITY_FAILURE']});held(out);
 assert.equal(out.stages.candidate.status,'UNKNOWN');
 assert.deepEqual(out.stages.candidate.reason_codes,['PROVIDER_READ_OR_IDENTITY_FAILURE']);
 assert.equal(out.stages.ci.status,'OBSERVED');
});
test('unavailable required CI is UNKNOWN even when selected runs observed',()=>{
 const out=observe();held(out);
 assert.equal(out.stages.ci.status,'OBSERVED');
 assert.equal(out.stages.ci.required_policy,'UNKNOWN');
 assert.equal(out.stages.ci.required_result,'UNKNOWN');
});
test('missing evidence comment isolates the U03 error',()=>{
 const out=observe(candidate(),ci(),{material_observed:false,source_currentness:'UNKNOWN',errors:['PROVIDER_SOURCE_OR_CLAIM_UNVERIFIED']});held(out);
 assert.equal(out.stages.evidence.status,'UNKNOWN');
 assert.deepEqual(out.stages.evidence.reason_codes,['PROVIDER_SOURCE_OR_CLAIM_UNVERIFIED']);
});
test('current head author claim is still diagnostic-only',()=>{
 const out=observe(candidate(),ci(),{material_observed:true,source_currentness:'MATCH_AT_OBSERVATION',errors:[]});held(out);
 assert.equal(out.stages.evidence.comment_currentness,'MATCH_AT_OBSERVATION');
});
test('invalid and thrown source objects cannot earn status',()=>{
 const out=observe(null,null,{errors:['DIAGNOSTIC_READ_THROWN']});held(out);
 for(const x of Object.values(out.stages))assert.equal(x.status,'UNKNOWN');
 assert.deepEqual(out.stages.candidate.reason_codes,['SOURCE_RESULT_NOT_OBJECT']);
 assert.deepEqual(out.stages.evidence.reason_codes,['DIAGNOSTIC_READ_THROWN']);
});
test('do not leak arbitrary provider error text or JSON-like owner flags',()=>{
 const out=observe({current:true,material_observation:'MATCH_AT_OBSERVATION',
  errors:['SECRET access token 123','PROVIDER_READ_OR_IDENTITY_FAILURE'],
  owner_authenticated:true,writer_authorized:true},ci(),evidence());held(out);
 assert.deepEqual(out.stages.candidate.reason_codes,['PROVIDER_READ_OR_IDENTITY_FAILURE']);
 assert.equal(JSON.stringify(out).includes('SECRET'),false);
 assert.equal(JSON.stringify(out).includes('token'),false);
});
test('forged required policy labels and evidence status are not printed',()=>{
 const out=observe(candidate(),{selected_checks_observed:false,
   required_check_policy:'SUCCESS_BY_AUTHOR',required_checks_result:'FORGED_PASS',
   errors:['SOURCE_IS_UNVERIFIED']},{material_observed:true,
   source_currentness:'TRUSTED_BY_AUTHOR',errors:[]});held(out);
 assert.equal(out.stages.ci.status,'UNKNOWN');
 assert.equal(out.stages.ci.required_policy,'UNKNOWN');
 assert.equal(out.stages.ci.required_result,'UNKNOWN');
 assert.equal(out.stages.evidence.comment_currentness,'UNKNOWN');
});
