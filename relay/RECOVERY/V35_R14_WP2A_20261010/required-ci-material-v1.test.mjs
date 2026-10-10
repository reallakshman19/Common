import test from 'node:test';
import assert from 'node:assert/strict';
import {observeSelectedRequiredCi} from './required-ci-material-v1.mjs';
const R='reallakshman19/Common', ID=1412133785,H='a'.repeat(40),H2='b'.repeat(40);
const BASE='recovery/5-m0-reference-identity-census-20261009';
const input=()=>({repository:R,repository_id:ID,pr_number:21,head_sha:H,base_branch:BASE});
const p={pr:'pulls/21',check:'commits/'+H+'/check-runs?per_page=100',status:'commits/'+H+'/status?per_page=100',
  classic:'branches/'+encodeURIComponent(BASE)+'/protection/required_status_checks',
  rules:'rules/branches/'+encodeURIComponent(BASE)};
function data(){return {
  [p.pr]:{number:21,html_url:'https://github.com/'+R+'/pull/21',
    head:{sha:H,repo:{id:ID,full_name:R}},base:{ref:BASE,repo:{id:ID,full_name:R}}},
  [p.check]:{total_count:1,check_runs:[{id:17,name:'build',status:'completed',conclusion:'success',head_sha:H,app:{id:42}}]},
  [p.status]:{sha:H,statuses:[]},[p.classic]:{contexts:[],checks:[{context:'build',app_id:42}]},[p.rules]:[],
};}
function get(d=data(),observe=()=>{}){let calls=0;return async(repo,path)=>{
  assert.equal(repo,R);observe(++calls,path,d);
  if(!(path in d))throw Error('HTTP 404');
  if(d[path] instanceof Error)throw d[path];
  return structuredClone(d[path]);};}
const run=(d=data(),cb)=>observeSelectedRequiredCi(input(),get(d,cb));
function safe(r){
  assert.equal(r.evidence_admitted,false);assert.equal(r.programme_progress,null);
  assert.equal(r.writer_authorized,false);assert.equal(r.owner_authenticated,false);
  assert.equal(r.reviewer_qualified,false);assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');
}
test('U02 native failure-stage reason is fixed across first and second reads',async()=>{
  const cases=[
    ['FIRST_SELECTED','CHECK_RUNS_GET_UNVERIFIED',d=>{d[p.check]=new Error('SECRET_PRIVATE_CHECK_RUNS');}],
    ['FIRST_SELECTED','COMMIT_STATUS_GET_UNVERIFIED',d=>{d[p.status]=new Error('SECRET_PRIVATE_STATUS');}],
    ['FIRST_SELECTED','SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID',d=>{d[p.check].total_count=999;}],
    ['FIRST_SELECTED','CHECK_RUN_SHAPE_OR_SHA_INVALID',d=>{d[p.check].check_runs[0].head_sha=H2;}],
    ['FIRST_SELECTED','COMMIT_STATUS_SHAPE_INVALID',d=>{d[p.status].statuses=[{context:'bad',state:'unknown'}];}],
  ];
  for(const [phase,reason,mutate] of cases){
    const d=data();mutate(d);const r=await run(d);safe(r);
    assert.equal(r.errors[0],'CI_MATERIAL_OR_POLICY_UNVERIFIED');
    assert.equal(r.failure_stage,phase);assert.equal(r.failure_reason,reason);
    assert.equal(r.required_check_policy,'UNKNOWN');assert.equal(r.required_checks_result,'UNKNOWN');
    assert.equal(r.selected_checks_observed,false);assert.equal(r.snapshot_sha256,null);
    assert.ok(!JSON.stringify(r).includes('SECRET_PRIVATE_'));
  }
  for(const [path,reason] of [[p.check,'CHECK_RUNS_GET_UNVERIFIED'],[p.status,'COMMIT_STATUS_GET_UNVERIFIED']]){
    const d=data();
    const r=await run(d,(n,route,m)=>{
      if(n===7)m[path]=new Error('SECRET_SECOND_ROUND_ERROR');
    });
    assert.equal(r.failure_stage,'SECOND_SELECTED');assert.equal(r.failure_reason,reason);
    assert.equal(r.errors[0],'CI_MATERIAL_OR_POLICY_UNVERIFIED');safe(r);
    assert.ok(!JSON.stringify(r).includes('SECRET_SECOND_ROUND_ERROR'));
  }
});
test('U02 original round differentiates PR drift, CI drift and policy drift',async()=>{
  const prMoved=await run(data(),(n,route,d)=>{
    if(n===6)d[p.pr].head.sha=H2;
  });
  assert.equal(prMoved.failure_stage,'MIDDLE_PR');
  assert.equal(prMoved.failure_reason,'PR_HEAD_BASE_OR_REPO_MISMATCH');safe(prMoved);
  const checksDrift=await run(data(),(n,route,d)=>{
    if(n===7)d[p.check].check_runs[0].conclusion='failure';
  });
  assert.equal(checksDrift.failure_stage,'SOURCE_READBACK');
  assert.equal(checksDrift.failure_reason,'SELECTED_CHECKS_DRIFT');safe(checksDrift);
  const policyDrift=await run(data(),(n,route,d)=>{
    if(n===7)d[p.classic].checks[0].context='other';
  });
  assert.equal(policyDrift.failure_stage,'SOURCE_READBACK');
  assert.equal(policyDrift.failure_reason,'REQUIRED_POLICY_DRIFT');safe(policyDrift);
});
test('U02 provider-authored errors never become failure reason or grant authority',async()=>{
  let calls=0;
  const r=await observeSelectedRequiredCi(input(),async(repo,route)=>{
    calls++;
    throw Error('SECRET_PROVIDER_BODY; CHECK_RUNS_GET_UNVERIFIED');
  });
  assert.equal(calls,1);
  assert.equal(r.failure_stage,'INITIAL_PR');assert.equal(r.failure_reason,null);
  assert.equal(r.required_check_policy,'UNKNOWN');
  assert.equal(r.selected_checks_observed,false);
  assert.ok(!JSON.stringify(r).includes('SECRET_PROVIDER_BODY'));safe(r);
});
test('U02 fully valid selected-source observation has no failure fields',async()=>{
  const r=await run();
  assert.equal(r.failure_stage,null);assert.equal(r.failure_reason,null);
  assert.equal(r.selected_checks_observed,true);safe(r);
});
test('positive required check diagnostic distinguishes selected and required',async()=>{
  const r=await run();safe(r);assert.equal(r.observed,true);assert.equal(r.selected_checks_observed,true);
  assert.equal(r.required_check_policy,'OBSERVED_CLASSIC_AND_RULESET');
  assert.equal(r.required_checks_result,'ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS');
  assert.equal(r.selected_checks.length,1);assert.equal(r.required_checks.length,1);
  assert.match(r.snapshot_sha256,/^sha256:[a-f0-9]{64}$/);
});
test('same bytes have deterministic source digest',async()=>{
  assert.equal((await run()).snapshot_sha256,(await run()).snapshot_sha256);
});
test('green unrequired run does NOT imply required success',async()=>{
  const d=data();d[p.classic]={contexts:[],checks:[]};
  const r=await run(d);assert.equal(r.required_checks_result,'NO_REQUIRED_CHECKS_OBSERVED');safe(r);
});
test('ruleset alone supplies required checks',async()=>{
  const d=data();d[p.classic]={contexts:[],checks:[]};
  d[p.rules]=[{type:'required_status_checks',parameters:{required_status_checks:[{context:'build',integration_id:42}]}}];
  assert.equal((await run(d)).required_checks_result,'ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS');
});
test('branch protection and ruleset union, missing check stays pending',async()=>{
  const d=data();d[p.rules]=[{type:'required_status_checks',parameters:{required_status_checks:[{context:'security',integration_id:null}]}}];
  const r=await run(d);assert.equal(r.required_checks_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
  assert.equal(r.required_checks.length,2);
});
test('same check name but wrong GitHub App is not accepted',async()=>{
  const d=data();d[p.classic]={contexts:[],checks:[{context:'build',app_id:99}]};
  assert.equal((await run(d)).required_checks_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
});
test('failed required check is failure, not E',async()=>{
  const d=data();d[p.check].check_runs[0].conclusion='failure';
  const r=await run(d);assert.equal(r.required_checks_result,'REQUIRED_CHECK_FAILED');safe(r);
});
test('in-progress required check remains pending',async()=>{
  const d=data();d[p.check].check_runs[0].status='in_progress';d[p.check].check_runs[0].conclusion=null;
  assert.equal((await run(d)).required_checks_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
});
test('legacy status satisfies unrestricted classic context',async()=>{
  const d=data();d[p.check]={total_count:0,check_runs:[]};
  d[p.status]={sha:H,statuses:[{context:'legacy-ci',state:'success'}]};
  d[p.classic]={contexts:['legacy-ci'],checks:[]};
  assert.equal((await run(d)).required_checks_result,'ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS');
});
test('legacy status cannot impersonate app-pinned run',async()=>{
  const d=data();d[p.check]={total_count:0,check_runs:[]};
  d[p.status]={sha:H,statuses:[{context:'build',state:'success'}]};
  assert.equal((await run(d)).required_checks_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
});
test('duplicate check identities are ambiguous',async()=>{
  const d=data();d[p.check].total_count=2;
  d[p.check].check_runs.push({...d[p.check].check_runs[0],id:18});
  assert.equal((await run(d)).required_checks_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
});
test('wrong SHA check run rejects observation',async()=>{
  const d=data();d[p.check].check_runs[0].head_sha=H2;
  const r=await run(d);safe(r);assert.equal(r.observed,false);
});
test('truncated check-run pagination cannot produce positive required pass',async()=>{
  const d=data();d[p.check].total_count=101;
  assert.equal((await run(d)).required_checks_result,'UNKNOWN');
});
test('missing classic protection does not mean no required checks',async()=>{
  const d=data();delete d[p.classic];const r=await run(d);
  assert.equal(r.required_checks_result,'UNKNOWN');assert.equal(r.required_check_policy,'UNKNOWN');
  assert.equal(r.selected_checks_observed,true);assert.equal(r.selected_checks.length,1);safe(r);
});
test('missing ruleset endpoint remains UNKNOWN and selected checks are retained',async()=>{
  const d=data();d[p.rules]=new Error('403');const r=await run(d);
  assert.equal(r.required_checks_result,'UNKNOWN');assert.equal(r.selected_checks_observed,true);
});
test('foreign repo rejected before any GET',async()=>{
  let calls=0;
  const r=await observeSelectedRequiredCi({...input(),repository:'reallaksh19/Common'},async()=>{calls++;return null;});
  assert.equal(calls,0);assert.equal(r.required_checks_result,'UNKNOWN');safe(r);
});
test('candidate SHA moving between rounds gives UNKNOWN',async()=>{
  const d=data();const r=await run(d,(n,path,mut)=>{if(n===7)mut[p.pr].head.sha=H2;});
  assert.equal(r.observed,false);assert.equal(r.required_checks_result,'UNKNOWN');safe(r);
});
test('check changes between reads yields UNKNOWN',async()=>{
  const d=data();const r=await run(d,(n,path,mut)=>{if(n===7)mut[p.check].check_runs[0].conclusion='failure';});
  assert.equal(r.observed,false);assert.equal(r.required_checks_result,'UNKNOWN');
});
test('rules change between reads yields UNKNOWN',async()=>{
  const d=data();const r=await run(d,(n,path,mut)=>{if(n===7)mut[p.classic].checks[0].context='new-build';});
  assert.equal(r.observed,false);assert.equal(r.required_checks_result,'UNKNOWN');
});
test('unsupported GitHub policy shape is UNKNOWN not no requirements',async()=>{
  const d=data();d[p.classic]={contexts:[]};
  assert.equal((await run(d)).required_checks_result,'UNKNOWN');
});
test('partial status provider error refuses positive diagnosis',async()=>{
  const d=data();d[p.status]=new Error('HTTP 429');
  const r=await run(d);assert.equal(r.observed,false);assert.equal(r.required_checks_result,'UNKNOWN');safe(r);
});
test('injected reader cannot forge native grade by passing options',async()=>{
  const r=await observeSelectedRequiredCi(input(),get(),{native:true});safe(r);
});

test('T31 underreported first-round check count is unreadable, never selected or required pass',async()=>{
 const d=data();d[p.check].total_count=0;
 const x=await run(d);safe(x);
 assert.equal(x.failure_stage,'FIRST_SELECTED');
 assert.equal(x.failure_reason,'SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID');
 assert.equal(x.selected_checks_observed,false);
 assert.equal(x.required_checks_result,'UNKNOWN');
 assert.equal(x.snapshot_sha256,null);
});
test('T31 negative check count and extra undeclared rows refuse source',async()=>{
 for(const change of [
  d=>{d[p.check].total_count=-1},
  d=>{d[p.check].check_runs.push({...d[p.check].check_runs[0],id:987});},
 ]){
  const d=data();change(d);
  const x=await run(d);safe(x);
  assert.equal(x.failure_stage,'FIRST_SELECTED');
  assert.equal(x.failure_reason,'SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID');
  assert.equal(x.observed,false);
 }
});
test('T31 underreported second-round source refuses after first valid read',async()=>{
 const d=data();const x=await run(d,(n,route,m)=>{
  if(n===7)m[p.check].total_count=0;
 });
 safe(x);
 assert.equal(x.failure_stage,'SECOND_SELECTED');
 assert.equal(x.failure_reason,'SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID');
 assert.equal(x.selected_checks_observed,false);
 assert.equal(x.required_checks_result,'UNKNOWN');
});
test('T31 zero check count and zero check rows is structurally valid but cannot satisfy required check',async()=>{
 const d=data();d[p.check]={total_count:0,check_runs:[]};
 const x=await run(d);safe(x);
 assert.equal(x.selected_checks_observed,true);
 assert.equal(x.required_checks_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
 assert.equal(x.evidence_admitted,false);
});
