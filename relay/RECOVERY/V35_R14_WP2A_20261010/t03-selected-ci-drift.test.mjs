import test from 'node:test';
import assert from 'node:assert/strict';
import {compareSelectedSnapshots,diagnoseU02SelectedDrift} from './t03-selected-ci-drift.mjs';
const R='reallakshman19/Common',ID=1412133785,H='a'.repeat(40),BASE='recovery/5-wp2a-u05-integrated-regression-20261010';
const input={repository:R,repository_id:ID,pr_number:306,head_sha:H,base_branch:BASE};
const route={pr:'pulls/306',checks:'commits/'+H+'/check-runs?per_page=100',status:'commits/'+H+'/status?per_page=100',classic:'branches/'+encodeURIComponent(BASE)+'/protection/required_status_checks',rules:'rules/branches/'+encodeURIComponent(BASE)};
const data=()=>({
 [route.pr]:{number:306,html_url:'https://github.com/'+R+'/pull/306',head:{sha:H,repo:{id:ID,full_name:R}},base:{ref:BASE,repo:{id:ID,full_name:R}}},
 [route.checks]:{total_count:1,check_runs:[{id:12345,name:'SECRET_PRIVATE_JOB',head_sha:H,status:'in_progress',conclusion:null,app:{id:15368}}]},
 [route.status]:{sha:H,statuses:[]},[route.classic]:{contexts:[],checks:[]},[route.rules]:[]
});
const reader=(d,mutation)=>{let n=0;return async(r,p)=>{assert.equal(r,R);n++;if(n===7&&mutation)mutation(d);return structuredClone(d[p]);};};
test('T03 transition supplies exact numeric run id without revealing check name',async()=>{
 const d=data(),r=await diagnoseU02SelectedDrift(input,reader(d,x=>{x[route.checks].check_runs[0].status='completed';x[route.checks].check_runs[0].conclusion='success';}));
 assert.equal(r.u02_failure_reason,'SELECTED_CHECKS_DRIFT');
 assert.equal(r.diagnosis,'TRANSITION_ONLY');assert.equal(r.selected_delta.transition_count,1);
 assert.equal(r.selected_delta.details[0].run_id,12345);assert.equal(r.selected_delta.details[0].old_state,'in_progress');assert.equal(r.selected_delta.details[0].new_state,'completed');
 assert.equal(r.u02_required_policy,'UNKNOWN'); // drift => refused even if policy readable
 assert.equal(r.evidence_admitted,false);assert.equal(r.positive_ci_qualified,false);
 assert.ok(!JSON.stringify(r).includes('SECRET_PRIVATE_JOB'));
});
test('T03 member arrival remains a refusal, bounded redacted diff',async()=>{
 const d=data(),r=await diagnoseU02SelectedDrift(input,reader(d,x=>{x[route.checks].check_runs.push({id:67890,name:'SECRET_NEW_JOB',head_sha:H,status:'queued',conclusion:null,app:{id:15368}});x[route.checks].total_count=2;}));
 assert.equal(r.u02_failure_reason,'SELECTED_CHECKS_DRIFT');
 assert.equal(r.diagnosis,'MEMBERSHIP_ONLY');assert.equal(r.selected_delta.added_count,1);
 assert.equal(r.selected_delta.details[0].run_id,67890);
 assert.ok(!JSON.stringify(r).includes('SECRET_NEW_JOB'));
});
test('T03 stable second read is not a positive native CI or evidence attestation',async()=>{
 const r=await diagnoseU02SelectedDrift(input,reader(data()));
 assert.equal(r.u02_failure_reason,null);assert.equal(r.diagnosis,'STABLE');
 assert.equal(r.authority,'DIAGNOSIS_ONLY_CALLER_INJECTED_UNATTESTED');
 assert.equal(r.positive_ci_qualified,false);assert.equal(r.writer_authorized,false);
});
test('T03 comparison refuses missing or duplicate samples',()=>{
 assert.equal(compareSelectedSnapshots(null,[]),null);
 assert.equal(compareSelectedSnapshots([{key:'x'},{key:'x'}],[]),null);
});
test('T03 unavailable provider response does not expose error string or invent delta',async()=>{
 const d=data(),r=await diagnoseU02SelectedDrift(input,async(repo,path)=>{
  if(path===route.checks)throw Error('SECRET_TOKEN_OR_BODY');
  return structuredClone(d[path]);
 });
 assert.equal(r.diagnosis,'INCOMPLETE_SOURCE_WINDOW');assert.equal(r.selected_delta,null);
 assert.equal(r.positive_ci_qualified,false);
 assert.ok(!JSON.stringify(r).includes('SECRET_TOKEN_OR_BODY'));
});
