/* #294 T05 falsifier uses ACTUAL unmodified WP2-B and original
 * WP2-A U01/U02/U03/U04 source at the SAME integration HEAD.
 * Adversarial injected responses are NEVER proof of native source.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectPreAdmission} from '../V35_R14_WP2B_20261010/pre-admission-boundary-v1.mjs';
import {observeCurrentCandidate} from './current-candidate-material-v1.mjs';
import {observeSelectedRequiredCi} from './required-ci-material-v1.mjs';
import {observeEvidenceComment} from './task-evidence-comment-v1.mjs';
const R='reallakshman19/Common',ID=1412133785,PR=308,C=6098434621;
const H='b'.repeat(40),OLD='a'.repeat(40),BSHA='c'.repeat(40);
const BASE='codex/294-t01-wp2a-u02-u03-u04-pinned',HEAD='codex/294-t05-wp2a-wp2b-negative-same-head';
const WEB='https://github.com/'+R,API='https://api.github.com/repos/'+R;
const check='commits/'+H+'/check-runs?per_page=100',status='commits/'+H+'/status?per_page=100';
const classic='branches/'+encodeURIComponent(BASE)+'/protection/required_status_checks',rules='rules/branches/'+encodeURIComponent(BASE);
const tick=String.fromCharCode(96);
function input(){return {repository:R,repository_id:ID,root_issue:5,leaf_issue:20,pr_number:PR,
 candidate_head_sha:H,base_branch:BASE,evidence_comment_id:C,evidence_claimed_head_sha:OLD,
 expected_author_login:'reallakshman19',facts_schema_line:'V35'};}
function data(){
 const d={
  '':{id:ID,full_name:R,default_branch:'main'},
  'issues/5':{number:5,html_url:WEB+'/issues/5',state:'open'},
  'issues/20':{number:20,html_url:WEB+'/issues/20',state:'open'},
  'pulls/308':{number:PR,html_url:WEB+'/pull/308',state:'open',
   head:{sha:H,ref:HEAD,repo:{id:ID,full_name:R}},
   base:{sha:BSHA,ref:BASE,repo:{id:ID,full_name:R}}},
  [check]:{total_count:1,check_runs:[{id:9001,name:'selected',app:{id:1234},
    head_sha:H,status:'completed',conclusion:'success'}]},
  [status]:{sha:H,statuses:[]},
  [classic]:{contexts:[],checks:[{context:'selected',app_id:1234}]},
  [rules]:[],
  ['issues/comments/'+C]:{id:C,html_url:WEB+'/issues/20#issuecomment-'+C,
   issue_url:API+'/issues/20',user:{login:'reallakshman19',id:277598171,type:'User'},
   created_at:'2026-10-10T15:01:00Z',updated_at:'2026-10-10T15:01:00Z',
   body:'## TASK_EVIDENCE — T01\n[PR #308]('+WEB+'/pull/308). **Tested HEAD:** '+tick+OLD+tick},
  ['commits/'+OLD]:{sha:OLD},
 };
 d['git/ref/heads/'+HEAD]={ref:'refs/heads/'+HEAD,object:{sha:H}};
 d['git/ref/heads/'+BASE]={ref:'refs/heads/'+BASE,object:{sha:BSHA}};
 return d;
}
function provider(state,hook=()=>{}){
 let n=0;
 return async (repo,path)=>{
  assert.equal(repo,R);hook(++n,path,state);
  if(!Object.hasOwn(state,path))throw Error('PRIVATE_PROVIDER_403');
  if(state[path] instanceof Error)throw state[path];
  return structuredClone(state[path]);
 };
}
function readers(d,hook=()=>{}){
 const get=provider(d,hook);
 return {candidate:i=>observeCurrentCandidate(i,get),
  ci:i=>observeSelectedRequiredCi(i,get),
  evidence:i=>observeEvidenceComment(i,get)};
}
const run=async (mutate=()=>{},hook=()=>{},i=input())=>{
 const d=data();mutate(d);return inspectPreAdmission(i,readers(d,hook));
};
function closed(v){
 assert.equal(v.admission,'NOT_ADMITTED');
 assert.equal(v.evidence_admitted,false);
 assert.equal(v.owner_authenticated,false);
 assert.equal(v.reviewer_qualified,false);
 assert.equal(v.programme_progress,null);
 assert.equal(v.delp_projector_invoked,false);
 assert.equal(v.writer_authorized,false);
 assert.equal(v.target_delp_policy,'NOT_ADOPTED');
 assert.equal(v.observation_grade,'CALLER_INJECTED_UNATTESTED');
}
test('T05 same PR308 head: genuine U01-U04 source vector consumed by unmodified WP2-B but NEVER E',async()=>{
 const x=await run();closed(x);
 assert.equal(x.source_status,'REFERENCES_COHERENT_BUT_UNADMITTED');
 assert.match(x.source_digest,/^sha256:[a-f0-9]{64}$/);
 assert.equal(x.candidate_facts_schema,'relay-v3.5-delp-checkpoint-facts');
 assert.ok(x.admission_blockers.includes('EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN'));
 assert.ok(x.admission_blockers.includes('ORIGINAL_OWNER_SOURCE_NOT_AUTHENTICATED'));
 assert.ok(x.admission_blockers.includes('CANONICAL_PROGRAMME_DELP_NOT_SELECTED'));
});
test('T05 deterministic exact same head source produces same consumer fingerprint',async()=>{
 const a=await run(),b=await run();closed(a);closed(b);
 assert.equal(a.source_digest,b.source_digest);
});
test('T05 provider required-CI policy 403 remains UNKNOWN with NO admission',async()=>{
 const v=await run(d=>delete d[classic]);closed(v);
 assert.equal(v.source_status,'REFERENCES_COHERENT_BUT_UNADMITTED');
 assert.ok(v.admission_blockers.includes('REQUIRED_CI_NOT_QUALIFIED'));
});
test('T05 historical Owner comment with forged actor prevents physical join',async()=>{
 const v=await run(d=>{d['issues/comments/'+C].user.login='untrusted-actor';});closed(v);
 assert.equal(v.source_status,'UNKNOWN');assert.equal(v.source_digest,null);
 assert.ok(v.admission_blockers.includes('CROSS_SOURCE_NOT_VERIFIED'));
});
test('T05 wrong repository stable ID rejected before any nested source reader',async()=>{
 const v=await inspectPreAdmission({...input(),repository_id:1207996454},
  {candidate:async()=>{throw Error('SHOULD_NOT_CALL');},
   ci:async()=>{throw Error('SHOULD_NOT_CALL');},
   evidence:async()=>{throw Error('SHOULD_NOT_CALL');}});
 closed(v);assert.equal(v.source_status,'UNKNOWN');
 assert.deepEqual(v.admission_blockers,['INPUT_CONTRACT_OR_FACTS_SCHEMA_INVALID']);
});
test('T05 moving real PR308 head across U04 rounds revokes source even though same issue remains',async()=>{
 let prReads=0;
 const v=await run(()=>{},(n,p,d)=>{
  if(p==='pulls/308'&&++prReads===4){
   d['pulls/308'].head.sha='d'.repeat(40);
   d['git/ref/heads/'+HEAD].object.sha='d'.repeat(40);
  }
 });closed(v);assert.equal(v.source_status,'UNKNOWN');assert.equal(v.source_digest,null);
});
test('T05 moving selected-CI check run during acquisition refuses same-head admission',async()=>{
 let checks=0;
 const v=await run(()=>{},(n,p,d)=>{
  if(p===check&&++checks===2)d[check].check_runs[0].id=9002;
 });closed(v);assert.equal(v.source_status,'UNKNOWN');assert.equal(v.source_digest,null);
});
test('T05 same-source current comment still cannot mint R3 witness/DELP or reviewer',async()=>{
 const v=await run(d=>{
  d['issues/comments/'+C].body=d['issues/comments/'+C].body.replace(OLD,H);
  d['commits/'+H]={sha:H};
 },()=>{},{...input(),evidence_claimed_head_sha:H});
 closed(v);
 assert.equal(v.source_status,'REFERENCES_COHERENT_BUT_UNADMITTED');
 assert.ok(v.admission_blockers.includes('R12_R3_NATIVE_WITNESS_NOT_TRANSFERRED'));
 assert.ok(v.admission_blockers.includes('TWO_INDEPENDENT_REVIEW_VERDICTS_MISSING'));
});
test('T05 unauthorized grants/alternate facts schema contract refused before reads',async()=>{
 const v=await inspectPreAdmission({...input(),reviewer_qualified:true},
  {candidate:async()=>{throw Error('SHOULD_NOT_READ');},ci:async()=>{},
   evidence:async()=>{}});
 closed(v);assert.equal(v.source_status,'UNKNOWN');
});
