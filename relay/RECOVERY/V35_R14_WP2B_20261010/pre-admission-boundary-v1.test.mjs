import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectPreAdmission} from './pre-admission-boundary-v1.mjs';
import {observeCurrentCandidate} from '../V35_R14_WP2A_20261010/current-candidate-material-v1.mjs';
import {observeSelectedRequiredCi} from '../V35_R14_WP2A_20261010/required-ci-material-v1.mjs';
import {observeEvidenceComment} from '../V35_R14_WP2A_20261010/task-evidence-comment-v1.mjs';

const R='reallakshman19/Common',ID=1412133785,ROOT=5,LEAF=20,PR=28,C=6089790172;
const H='a'.repeat(40), OLD='cd08d01d70f4ad034fc352f4ab44079982f33636';
const BASE='recovery/5-wp2a-u04-cross-source-vector-20261010';
const BRANCH='recovery/5-wp2b-b01-b03-pre-admission-20261010';
const BSHA='c'.repeat(40),API='https://api.github.com/repos/'+R, WEB='https://github.com/'+R;
const cp='commits/'+H+'/check-runs?per_page=100',sp='commits/'+H+'/status?per_page=100';
const bp='branches/'+encodeURIComponent(BASE)+'/protection/required_status_checks';
const rp='rules/branches/'+encodeURIComponent(BASE),cc='issues/comments/'+C;
const tick=String.fromCharCode(96);
function input(){return {
  repository:R,repository_id:ID,root_issue:ROOT,leaf_issue:LEAF,pr_number:PR,
  candidate_head_sha:H,base_branch:BASE,evidence_comment_id:C,
  evidence_claimed_head_sha:OLD,expected_author_login:'reallakshman19',
  facts_schema_line:'V35',
};}
function db(){
 const obj={
  '':{id:ID,full_name:R,default_branch:'main'},
  'issues/5':{number:5,html_url:WEB+'/issues/5',state:'open'},
  'issues/20':{number:20,html_url:WEB+'/issues/20',state:'open'},
  'pulls/28':{number:PR,html_url:WEB+'/pull/28',state:'open',
    head:{sha:H,ref:BRANCH,repo:{id:ID,full_name:R}},
    base:{sha:BSHA,ref:BASE,repo:{id:ID,full_name:R}}},
  [cp]:{total_count:1,check_runs:[{id:111,name:'unit',status:'completed',
    conclusion:'success',head_sha:H,app:{id:42}}]},
  [sp]:{sha:H,statuses:[]},
  [bp]:{contexts:[],checks:[{context:'unit',app_id:42}]},
  [rp]:[],
  [cc]:{id:C,html_url:WEB+'/issues/20#issuecomment-'+C,
    issue_url:API+'/issues/20',user:{login:'reallakshman19',id:277598171,type:'User'},
    created_at:'2026-10-09T22:00:00Z',updated_at:'2026-10-09T22:00:00Z',
    body:'## TASK_EVIDENCE — U05\n**Tested HEAD:** '+tick+OLD+tick+
      ' [source PR #28]('+WEB+'/pull/28).'},
  ['commits/'+OLD]:{sha:OLD},
 };
 obj['git/ref/heads/'+BRANCH]={ref:'refs/heads/'+BRANCH,object:{sha:H}};
 obj['git/ref/heads/'+BASE]={ref:'refs/heads/'+BASE,object:{sha:BSHA}};
 return obj;
}
function readers(state,hook=()=>{}){
 let counter=0;
 const read=async(repo,path)=>{
  assert.equal(repo,R);
  if(!Object.hasOwn(state,path))throw Error('404');
  if(state[path] instanceof Error)throw state[path];
  return structuredClone(state[path]);
 };
 return {
  candidate:async x=>{hook(++counter,'candidate',state);return observeCurrentCandidate(x,read);},
  ci:async x=>{hook(++counter,'ci',state);return observeSelectedRequiredCi(x,read);},
  evidence:async x=>{hook(++counter,'evidence',state);return observeEvidenceComment(x,read);},
 };
}
const run=async(modify=()=>{},hook=()=>{},contract=input())=>{
 const s=db();modify(s);return inspectPreAdmission(contract,readers(s,hook));
};
function closed(x){
 assert.equal(x.admission,'NOT_ADMITTED');
 assert.equal(x.owner_authenticated,false);
 assert.equal(x.reviewer_qualified,false);
 assert.equal(x.evidence_admitted,false);
 assert.equal(x.programme_progress,null);
 assert.equal(x.delp_projector_invoked,false);
 assert.equal(x.writer_authorized,false);
 assert.equal(x.runner_lease,'NOT_PROVEN');
 assert.equal(x.target_delp_policy,'NOT_ADOPTED');
 assert.equal(x.observation_grade,'CALLER_INJECTED_UNATTESTED');
}
test('B01 real U01-U04 full source positive diagnostic still REFUSES admission',async()=>{
 const x=await run();closed(x);assert.equal(x.source_status,'REFERENCES_COHERENT_BUT_UNADMITTED');
 assert.match(x.source_digest,/^sha256:[a-f0-9]{64}$/);
 assert.ok(x.admission_blockers.includes('EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN'));
 assert.ok(x.admission_blockers.includes('EVIDENCE_POLICY_VERSION_NOT_ADOPTED'));
 assert.ok(x.admission_blockers.includes('TWO_INDEPENDENT_REVIEW_VERDICTS_MISSING'));
});
test('B01 separate V3.2 version is not silently rewritten as V3.5',async()=>{
 const x=await run(()=>{},()=>{},{...input(),facts_schema_line:'V32'});
 closed(x);assert.equal(x.candidate_facts_schema,'relay-v3.2-delp-checkpoint-facts');
 assert.equal(x.target_delp_policy,'NOT_ADOPTED');
});
test('B01 explicit V3.5 fact schema is distinguished without projection',async()=>{
 const x=await run();closed(x);
 assert.equal(x.candidate_facts_schema,'relay-v3.5-delp-checkpoint-facts');
});
test('B01 unrecognized fact schema rejected before provider reads',async()=>{
 let calls=0;
 const x=await inspectPreAdmission({...input(),facts_schema_line:'V36'},{
  candidate:async()=>calls++,ci:async()=>calls++,evidence:async()=>calls++});
 closed(x);assert.equal(calls,0);
 assert.deepEqual(x.admission_blockers,['INPUT_CONTRACT_OR_FACTS_SCHEMA_INVALID']);
});
test('B01 forged policy-adopted, reviewer or owner flags rejected',async()=>{
 for(const [k,value] of [['policy_adopted',true],['reviewer_qualified',true],
   ['source_acquisition_attested',true],['writer_authorized',true]]){
  const x=await run(()=>{},()=>{},{...input(),[k]:value});
  closed(x);assert.equal(x.source_status,'UNKNOWN');
  assert.deepEqual(x.admission_blockers,['INPUT_CONTRACT_OR_FACTS_SCHEMA_INVALID']);
 }
});
test('B01 old repository name or stable ID denied before acquisition',async()=>{
 for(const k of ['repository','repository_id']){
  const modified={...input(),[k]:k==='repository'?'reallaksh19/Common':1207996454};
  const x=await inspectPreAdmission(modified,{});
  closed(x);assert.equal(x.source_status,'UNKNOWN');
 }
});
test('B02 selected-green but required policy unreadable does not become admission',async()=>{
 const x=await run(s=>delete s[bp]);closed(x);
 assert.equal(x.source_status,'REFERENCES_COHERENT_BUT_UNADMITTED');
 assert.ok(x.admission_blockers.includes('REQUIRED_CI_NOT_QUALIFIED'));
});
test('B02 failed required check does not become admitted E',async()=>{
 const x=await run(s=>s[cp].check_runs[0].conclusion='failure');closed(x);
 assert.ok(x.admission_blockers.includes('REQUIRED_CI_NOT_QUALIFIED'));
});
test('B02 old-repository copy of GitHub comment is not a current source',async()=>{
 const x=await run(s=>s[cc].html_url='https://github.com/reallaksh19/Common/issues/20#issuecomment-'+C);
 closed(x);assert.equal(x.source_status,'UNKNOWN');
 assert.ok(x.admission_blockers.includes('CROSS_SOURCE_NOT_VERIFIED'));
});
test('B02 forged account/reviewer claim cannot override native User identity',async()=>{
 const x=await run(s=>s[cc].user.login='fake-peer');
 closed(x);assert.equal(x.source_digest,null);
});
test('B02 mid-cycle CI change invalidates composite before eligibility',async()=>{
 const x=await run(()=>{},(n,k,s)=>{
  if(n===4)s[cp].check_runs[0].id=999;
 });
 closed(x);assert.equal(x.source_status,'UNKNOWN');assert.equal(x.source_digest,null);
});
test('B02 mid-cycle PR head move cannot be interpreted as current evidence',async()=>{
 const x=await run(()=>{},(n,k,s)=>{
  if(n===4){const h='b'.repeat(40);
    s['pulls/28'].head.sha=h;s['git/ref/heads/'+BRANCH].object.sha=h;}
 });
 closed(x);assert.equal(x.source_status,'UNKNOWN');
});
test('B02 HTTP 429 in U03 evidence receipt stops whole candidate',async()=>{
 const x=await run(s=>{s[cc]=new Error('429');});
 closed(x);assert.equal(x.source_status,'UNKNOWN');
});
test('B03 exact-current author claim still cannot adopt policy or qualify reviewer',async()=>{
 const target={...input(),evidence_claimed_head_sha:H};
 const x=await run(s=>{s[cc].body=s[cc].body.replace(OLD,H);
   s['commits/'+H]={sha:H};},()=>{},target);
 closed(x);assert.equal(x.source_status,'REFERENCES_COHERENT_BUT_UNADMITTED');
 assert.ok(x.admission_blockers.includes('ORIGINAL_OWNER_SOURCE_NOT_AUTHENTICATED'));
 assert.ok(x.admission_blockers.includes('CANONICAL_PROGRAMME_DELP_NOT_SELECTED'));
});
test('B03 same source material yields reproducible proposed fingerprint',async()=>{
 const a=await run(),b=await run();closed(a);closed(b);
 assert.equal(a.source_digest,b.source_digest);
});
test('B03 missing reader denied; no native claim from injection',async()=>{
 const x=await inspectPreAdmission(input(),{candidate:async()=>({})});
 closed(x);assert.deepEqual(x.admission_blockers,['PROVIDER_READERS_MISSING']);
});
test('B03 independently marked native stage cannot be laundered by injected functions',async()=>{
 const actual=readers(db());
 const spoof={
   candidate:async x=>({...await actual.candidate(x),source_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'}),
   ci:async x=>({...await actual.ci(x),source_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'}),
   evidence:async x=>({...await actual.evidence(x),source_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'}),
 };
 const x=await inspectPreAdmission(input(),spoof);closed(x);
 assert.equal(x.source_status,'UNKNOWN');
});
