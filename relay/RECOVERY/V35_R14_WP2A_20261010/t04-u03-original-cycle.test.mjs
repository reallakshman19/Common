import test from 'node:test';
import assert from 'node:assert/strict';
import {diagnoseU03OriginalCycle} from './t04-u03-original-cycle.mjs';
import {observeEvidenceComment} from './task-evidence-comment-v1.mjs';

const R='reallakshman19/Common',ID=1412133785,H1='a'.repeat(40),H2='b'.repeat(40);
const C=6098434621,BASE='recovery/5-wp2a-u05-integrated-regression-20261010';
const T=String.fromCharCode(96),PR='https://github.com/'+R+'/pull/306',SHA=x=>'sha256:'+x.repeat(64);
const input=()=>({repository:R,repository_id:ID,root_issue:5,leaf_issue:20,pr_number:306,
 candidate_head_sha:H2,base_branch:BASE,evidence_comment_id:C,
 evidence_claimed_head_sha:H1,expected_author_login:'reallakshman19'});
const body=()=> '## TASK_EVIDENCE\n[draft PR #306]('+PR+')\n**Tested HEAD:** '+T+H1+T+'\n';
function material(){
 return {
  '':{id:ID,full_name:R},
  'issues/5':{number:5,html_url:'https://github.com/'+R+'/issues/5',state:'open'},
  'issues/20':{number:20,html_url:'https://github.com/'+R+'/issues/20',state:'open'},
  'pulls/306':{number:306,html_url:PR,state:'open',head:{sha:H2,repo:{id:ID,full_name:R}}},
  ['issues/comments/'+C]:{id:C,html_url:'https://github.com/'+R+'/issues/20#issuecomment-'+C,
   issue_url:'https://api.github.com/repos/'+R+'/issues/20',
   user:{id:277598171,login:'reallakshman19',type:'User'},body:body(),
   created_at:'2026-10-10T10:00:00Z',updated_at:'2026-10-10T10:00:00Z'},
  ['commits/'+H1]:{sha:H1},
 };
}
const evidenceInput=i=>({repository:R,repository_id:ID,root_issue:5,leaf_issue:20,pr_number:306,
 evidence_comment_id:C,claimed_head_sha:H1,expected_author_login:'reallakshman19'});
function fixture({change=()=>{},badRound=null,badInner=null,u02bad=false}={}){
 let subreaders=0,outer=0,network=0;
 const readers={
  candidate:async()=>{
   subreaders++;
   return {source_grade:'CALLER_INJECTED_UNATTESTED',current:true,
    material_observation:'MATCH_AT_OBSERVATION',source_vector_sha256:SHA('a'),
    source_vector:{repository:R,provider_repo_id:ID,root_issue:5,leaf_issue:20,pr_number:306,
     candidate_sha:H2,base_branch:BASE},evidence_admitted:false,
    writer_authorized:false,programme_progress:null};
  },
  ci:async()=>{
   subreaders++;
   return {source_grade:'CALLER_INJECTED_UNATTESTED',selected_checks_observed:!u02bad,
    snapshot_sha256:u02bad?null:SHA('b'),required_check_policy:'UNKNOWN',
    required_checks_result:'UNKNOWN',evidence_admitted:false,
    writer_authorized:false,programme_progress:null};
  },
  evidence:async()=>{
   subreaders++;outer++;
   const d=material();
   change(d,outer);
   let count=0;
   return observeEvidenceComment(evidenceInput(input()),async(repo,p)=>{
    assert.equal(repo,R); network++;count++;
    if(badRound===outer&&p===badInner)throw Error('PRIVATE_PROVIDER_EXCEPTION_TOKEN');
    if(!(p in d))throw Error('NOT_FOUND_WITH_SECRET');
    return structuredClone(d[p]);
   });
  },
 };
 return {readers,stats:()=>({subreaders,outer,network})};
}
function protectedResult(x){
 assert.equal(x.source_grade,'CALLER_INJECTED_UNATTESTED');
 assert.equal(x.source_material_attested,false);
 assert.equal(x.positive_fact_admitted,false);
 assert.equal(x.effective_required_ci_qualified,false);
 assert.equal(x.owner_authenticated,false);
 assert.equal(x.reviewer_qualified,false);
 assert.equal(x.writer_authorized,false);
 assert.equal(x.programme_progress,null);
 assert.equal(x.delp_projection,'NOT_CALCULATED');
 assert.equal(x.successor_lease,'NOT_PROVEN');
 assert.ok(x.original_u04_subreader_calls<=6);
 assert.equal(x.no_extra_subreader_calls,true);
 assert.ok(!JSON.stringify(x).includes('PRIVATE_PROVIDER_EXCEPTION_TOKEN'));
 assert.equal(JSON.stringify(x).includes('"source_receipt"'),false);
 assert.equal(JSON.stringify(x).includes('277598171'),false);
}
test('T04 actual nested U03 original U04 order: historical stable is never admitted',async()=>{
 const f=fixture(),x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.result_class,'DIAGNOSTIC_HISTORICAL_SOURCE_OBSERVED');
 assert.equal(x.original_u04_source_consistent,true);
 assert.equal(x.u03_round_count,2);
 assert.deepEqual(x.u03_rounds.map(y=>[y.outer_round,y.material_observed,y.source_currentness]),
  [['FIRST',true,'STALE_CANDIDATE_HEAD'],['SECOND',true,'STALE_CANDIDATE_HEAD']]);
 assert.deepEqual(f.stats(),{subreaders:6,outer:2,network:24});
 protectedResult(x);
});
test('T04 U03 original first round COMMENT GET failure becomes U04 JOIN_U03 refusal',async()=>{
 const f=fixture({badRound:1,badInner:'issues/comments/'+C});
 const x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.original_u04_failure_stage,'JOIN');
 assert.equal(x.original_u04_failure_round,'FIRST');
 assert.equal(x.original_u04_failure_reason,'JOIN_U03_SOURCE_UNVERIFIED');
 assert.equal(x.result_class,'U03_NESTED_REFUSAL_CAUSES_JOIN');
 assert.equal(x.u03_round_count,1);
 assert.equal(x.u03_rounds[0].failure_stage,'FIRST_READ');
 assert.equal(x.u03_rounds[0].failure_reason,'COMMENT_GET_UNVERIFIED');
 assert.deepEqual(f.stats(),{subreaders:3,outer:1,network:12});
 protectedResult(x);
});
test('T04 U03 original second inner round COMMIT error preserved as SECOND_READ',async()=>{
 let attempt=0;
 const f=fixture();
 f.readers.evidence=async()=>{
  attempt++;
  const d=material();
  let count=0;
  return observeEvidenceComment(evidenceInput(input()),async(repo,p)=>{
   count++;
   if(count===12)throw Error('PRIVATE_PROVIDER_EXCEPTION_TOKEN');
   return structuredClone(d[p]);
  });
 };
 const x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.result_class,'U03_NESTED_REFUSAL_CAUSES_JOIN');
 assert.equal(x.u03_rounds[0].failure_stage,'SECOND_READ');
 assert.equal(x.u03_rounds[0].failure_reason,'COMMIT_GET_UNVERIFIED');
 assert.equal(x.original_u04_failure_round,'FIRST');
 protectedResult(x);
});
test('T04 U03 wrong GitHub actor becomes COMMENT_IDENTITY_INVALID and JOIN denial',async()=>{
 const f=fixture({change:d=>{d['issues/comments/'+C].user.login='impostor';}});
 const x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.result_class,'U03_NESTED_REFUSAL_CAUSES_JOIN');
 assert.equal(x.u03_rounds[0].failure_stage,'FIRST_VALIDATE');
 assert.equal(x.u03_rounds[0].failure_reason,'COMMENT_IDENTITY_INVALID');
 protectedResult(x);
});
test('T04 U03 wrong claim SHA and wrong PR URL cannot count',async()=>{
 for(const mutate of [
  d=>{d['issues/comments/'+C].body=d['issues/comments/'+C].body.replace(H1,H2);},
  d=>{d['issues/comments/'+C].body=d['issues/comments/'+C].body.replace(PR,'https://github.com/reallaksh19/Common/pull/306');},
 ]){
  const f=fixture({change:mutate});
  const x=await diagnoseU03OriginalCycle(input(),f.readers);
  assert.equal(x.result_class,'U03_NESTED_REFUSAL_CAUSES_JOIN');
  assert.equal(x.u03_rounds[0].failure_stage,'FIRST_VALIDATE');
  assert.ok(['HEAD_CLAIM_MISMATCH','CURRENT_PR_BINDING_MISSING'].includes(x.u03_rounds[0].failure_reason));
  protectedResult(x);
 }
});
test('T04 U03 second OUTER U04 original round failure is distinguishable',async()=>{
 const f=fixture({change:(d,outer)=>{
  if(outer===2)d['issues/comments/'+C].user.login='impostor';
 }});
 const x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.original_u04_failure_stage,'JOIN');
 assert.equal(x.original_u04_failure_round,'SECOND');
 assert.equal(x.original_u04_failure_reason,'JOIN_U03_SOURCE_UNVERIFIED');
 assert.equal(x.result_class,'U03_NESTED_REFUSAL_CAUSES_JOIN');
 assert.equal(x.u03_round_count,2);
 assert.equal(x.u03_rounds[0].material_observed,true);
 assert.equal(x.u03_rounds[1].failure_reason,'COMMENT_IDENTITY_INVALID');
 assert.deepEqual(f.stats(),{subreaders:6,outer:2,network:24});
 protectedResult(x);
});
test('T04 U03 stable but edited comment between OUTER rounds forces U04 SOURCE_VECTOR_CHANGED',async()=>{
 const f=fixture({change:(d,outer)=>{
  if(outer===2){d['issues/comments/'+C].body+='Edited reason line\n';
   d['issues/comments/'+C].updated_at='2026-10-10T10:01:00Z';}
 }});
 const x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.result_class,'OUTER_SOURCE_VECTOR_DRIFT');
 assert.equal(x.original_u04_failure_stage,'SECOND_ROUND_DRIFT');
 assert.equal(x.original_u04_failure_round,'SECOND');
 assert.equal(x.u03_round_count,2);
 assert.ok(x.u03_rounds.every(y=>y.material_observed));
 protectedResult(x);
});
test('T04 valid U03 cannot hide U02 original JOIN blocking',async()=>{
 const f=fixture({u02bad:true}),x=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(x.result_class,'U02_JOIN_BLOCKED_WITH_U03_OBSERVED');
 assert.equal(x.original_u04_failure_reason,'JOIN_U02_SOURCE_UNVERIFIED');
 assert.equal(x.u03_round_count,1);
 assert.equal(x.u03_rounds[0].material_observed,true);
 protectedResult(x);
});
test('T04 wrong repository rejects before provider call with no forged admission',async()=>{
 const f=fixture(),x=await diagnoseU03OriginalCycle({...input(),repository:'reallaksh19/Common'},f.readers);
 assert.equal(x.original_u04_source_consistent,false);
 assert.equal(x.u03_round_count,0);
 assert.equal(f.stats().subreaders,0);
 protectedResult(x);
});
test('T04 caller-injected alleged native grade is downshifted and not accepted',async()=>{
 const f=fixture();
 const orig=f.readers.candidate;
 f.readers.candidate=async x=>({...await orig(x),source_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'});
 const r=await diagnoseU03OriginalCycle(input(),f.readers);
 assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');
 assert.equal(r.original_u04_source_consistent,true);
 protectedResult(r);
});
