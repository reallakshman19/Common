/* U05 cross-module negative benchmark: real U01/U02/U03 observers -> U04. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {observeCurrentCandidate} from './current-candidate-material-v1.mjs';
import {observeSelectedRequiredCi} from './required-ci-material-v1.mjs';
import {observeEvidenceComment} from './task-evidence-comment-v1.mjs';
import {observeCrossSource} from './cross-source-vector-v1.mjs';

const R='reallakshman19/Common',ID=1412133785,PR=27,C=6089537374;
const H='a'.repeat(40),OLD='4d90d0ff8a72d843c632d44ed4bc90b2a7da3ca1',B='c'.repeat(40);
const BASE='recovery/5-wp2a-u01-current-material-20261010',BR='recovery/5-wp2a-u05-integrated-regression-20261010';
const api='https://api.github.com/repos/'+R,web='https://github.com/'+R;
const tick=String.fromCharCode(96);
const input=()=>({repository:R,repository_id:ID,root_issue:5,leaf_issue:20,pr_number:PR,
 candidate_head_sha:H,base_branch:BASE,evidence_comment_id:C,evidence_claimed_head_sha:OLD,
 expected_author_login:'reallakshman19'});
const checkPath='commits/'+H+'/check-runs?per_page=100';
const statusPath='commits/'+H+'/status?per_page=100';
const classicPath='branches/'+encodeURIComponent(BASE)+'/protection/required_status_checks';
const rulesPath='rules/branches/'+encodeURIComponent(BASE);
const commentPath='issues/comments/'+C;
function fixture(){
 const src={
  '':{id:ID,full_name:R,default_branch:'main'},
  'issues/5':{number:5,html_url:web+'/issues/5',state:'open'},
  'issues/20':{number:20,html_url:web+'/issues/20',state:'open'},
  'pulls/27':{number:PR,html_url:web+'/pull/27',state:'open',
   head:{sha:H,ref:BR,repo:{id:ID,full_name:R}},
   base:{sha:B,ref:BASE,repo:{id:ID,full_name:R}}},
  [checkPath]:{total_count:1,check_runs:[{id:501,name:'unit',status:'completed',
   conclusion:'success',head_sha:H,app:{id:42}}]},
  [statusPath]:{sha:H,statuses:[]},
  [classicPath]:{contexts:[],checks:[{context:'unit',app_id:42}]},
  [rulesPath]:[],
  [commentPath]:{id:C,html_url:web+'/issues/20#issuecomment-'+C,
   issue_url:api+'/issues/20',user:{login:'reallakshman19',id:277598171,type:'User'},
   created_at:'2026-10-09T21:00:00Z',updated_at:'2026-10-09T21:00:00Z',
   body:'## TASK_EVIDENCE — historical source\n**Tested HEAD:** '+tick+OLD+tick+
     ' [draft PR #27]('+web+'/pull/27).'},
  ['commits/'+OLD]:{sha:OLD},
 };
 src['git/ref/heads/'+BR]={ref:'refs/heads/'+BR,object:{sha:H}};
 src['git/ref/heads/'+BASE]={ref:'refs/heads/'+BASE,object:{sha:B}};
 return src;
}
function readers(src,hook=()=>{}){
 let n=0;
 const get=async(repo,path)=>{
   assert.equal(repo,R);if(!Object.hasOwn(src,path))throw Error('HTTP 404');
   if(src[path] instanceof Error)throw src[path];
   return structuredClone(src[path]);
 };
 return {
  candidate:async x=>{hook('candidate',++n,src);return observeCurrentCandidate(x,get);},
  ci:async x=>{hook('ci',++n,src);return observeSelectedRequiredCi(x,get);},
  evidence:async x=>{hook('evidence',++n,src);return observeEvidenceComment(x,get);},
 };
}
async function integrated(change=()=>{},hook=()=>{}){
 const src=fixture();change(src);return observeCrossSource(input(),readers(src,hook));
}
function safe(r){
 assert.equal(r.evidence_admitted,false);assert.equal(r.owner_authenticated,false);
 assert.equal(r.reviewer_qualified,false);assert.equal(r.required_ci_qualified,false);
 assert.equal(r.writer_authorized,false);assert.equal(r.programme_progress,null);
 assert.equal(r.delp_projection,'NOT_CALCULATED');assert.equal(r.successor_lease,'NOT_PROVEN');
 assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');
}
test('physical U01-U04: clean selected and required checks do not admit historical E',async()=>{
 const r=await integrated();safe(r);
 assert.equal(r.source_consistent,true);
 assert.equal(r.material_status,'CONSISTENT_HISTORICAL_EVIDENCE_ONLY');
 assert.equal(r.source_vector.required_ci_result,'ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS');
 assert.equal(r.source_vector.evidence_currentness,'STALE_CANDIDATE_HEAD');
 assert.match(r.source_vector_sha256,/^sha256:[a-f0-9]{64}$/);
});
test('same provider objects yield the same composite digest',async()=>{
 const a=await integrated(),b=await integrated();safe(a);safe(b);
 assert.equal(a.source_vector_sha256,b.source_vector_sha256);
});
test('green selected check with unreadable required policy is UNKNOWN',async()=>{
 const r=await integrated(s=>{delete s[classicPath];});safe(r);
 assert.equal(r.source_consistent,true);assert.equal(r.source_vector.required_ci_policy,'UNKNOWN');
 assert.equal(r.source_vector.required_ci_result,'UNKNOWN');
});
test('failed required check is source fact, not accepted evidence',async()=>{
 const r=await integrated(s=>{s[checkPath].check_runs[0].conclusion='failure';});safe(r);
 assert.equal(r.source_consistent,true);assert.equal(r.source_vector.required_ci_result,'REQUIRED_CHECK_FAILED');
});
test('wrong GitHub App identity cannot satisfy a required status check',async()=>{
 const r=await integrated(s=>{s[checkPath].check_runs[0].app.id=99;});safe(r);
 assert.equal(r.source_consistent,true);
 assert.equal(r.source_vector.required_ci_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
});
test('old repository id rejected by the physical U01 validator',async()=>{
 const r=await integrated(s=>{s[''].id=1207996454;});safe(r);
 assert.equal(r.source_consistent,false);
});
test('old repository issue URL rejected by the physical U01 validator',async()=>{
 const r=await integrated(s=>{s['issues/20'].html_url='https://github.com/reallaksh19/Common/issues/20';});
 safe(r);assert.equal(r.source_consistent,false);
});
test('comment on parent instead of child cannot bind TaskEvidence',async()=>{
 const r=await integrated(s=>{s[commentPath].issue_url=api+'/issues/5';});safe(r);
 assert.equal(r.source_consistent,false);
});
test('edited comment between full U04 cycles invalidates snapshot',async()=>{
 const r=await integrated(()=>{},(stage,n,s)=>{if(stage==='candidate'&&n===4)s[commentPath].body+=' edited';});
 safe(r);assert.equal(r.source_consistent,false);
 assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');
});
test('CI run id changes between cycles invalidates the snapshot',async()=>{
 const r=await integrated(()=>{},(stage,n,s)=>{if(stage==='candidate'&&n===4)s[checkPath].check_runs[0].id=502;});
 safe(r);assert.equal(r.source_consistent,false);
 assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');
});
test('base branch tip changes between cycles invalidates the snapshot',async()=>{
 const r=await integrated(()=>{},(stage,n,s)=>{
  if(stage==='candidate'&&n===4){
   const next='d'.repeat(40);s['pulls/27'].base.sha=next;
   s['git/ref/heads/'+BASE].object.sha=next;
  }
 });safe(r);assert.equal(r.source_consistent,false);
 assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');
});
test('PR head changes between cycles is rejected, not counted as progress',async()=>{
 const r=await integrated(()=>{},(stage,n,s)=>{
  if(stage==='candidate'&&n===4){
   const next='e'.repeat(40);s['pulls/27'].head.sha=next;
   s['git/ref/heads/'+BR].object.sha=next;
  }
 });safe(r);assert.equal(r.source_consistent,false);
 assert.equal(r.error,'SOURCE_MATERIAL_UNVERIFIED');
});
test('comment GET rate limit cannot make an admitted evidence path',async()=>{
 const r=await integrated(s=>{s[commentPath]=new Error('HTTP 429');});
 safe(r);assert.equal(r.source_consistent,false);
});
test('duplicate selected check names do not count as one required success',async()=>{
 const r=await integrated(s=>{
  s[checkPath].total_count=2;s[checkPath].check_runs.push({...s[checkPath].check_runs[0],id:502});
 });safe(r);assert.equal(r.source_consistent,true);
 assert.equal(r.source_vector.required_ci_result,'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS');
});
