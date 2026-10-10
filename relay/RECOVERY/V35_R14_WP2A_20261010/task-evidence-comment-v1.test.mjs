import test from 'node:test';
import assert from 'node:assert/strict';
import {observeEvidenceComment} from './task-evidence-comment-v1.mjs';
const R='reallakshman19/Common',ID=1412133785;
const H1='a'.repeat(40),H2='b'.repeat(40),C=6089024942;
const input=()=>({repository:R,repository_id:ID,root_issue:5,leaf_issue:20,
 pr_number:21,evidence_comment_id:C,claimed_head_sha:H1,expected_author_login:'reallakshman19'});
const PR='https://github.com/'+R+'/pull/21';
const tick=String.fromCharCode(96);
function body(head=H1,link=PR){
 return '## TASK_EVIDENCE — U02\n**Owner scope:** [leaf #20](https://github.com/'+R+
  '/issues/20) → [draft PR #21]('+link+'). **Tested HEAD:** '+tick+head+tick+', source claim only.';
}
function source(){return {
 '':{id:ID,full_name:R},
 'issues/5':{number:5,html_url:'https://github.com/'+R+'/issues/5',state:'open'},
 'issues/20':{number:20,html_url:'https://github.com/'+R+'/issues/20',state:'open'},
 'pulls/21':{number:21,html_url:PR,state:'open',head:{sha:H1,repo:{id:ID,full_name:R}}},
 ['issues/comments/'+C]:{id:C,html_url:'https://github.com/'+R+'/issues/20#issuecomment-'+C,
  issue_url:'https://api.github.com/repos/'+R+'/issues/20',
  user:{login:'reallakshman19',id:277598171,type:'User'},
  created_at:'2026-10-09T20:00:00Z',updated_at:'2026-10-09T20:00:00Z',body:body()},
 ['commits/'+H1]:{sha:H1},
};}
function injected(data=source(),hook=()=>{}){
 let n=0;
 return async(repo,path)=>{
  assert.equal(repo,R);hook(++n,path,data);
  if(!Object.hasOwn(data,path))throw Error('404');
  if(data[path] instanceof Error)throw data[path];
  return structuredClone(data[path]);
 };
}
const noAuthority=r=>{
 assert.equal(r.evidence_admitted,false);assert.equal(r.reviewer_qualified,false);
 assert.equal(r.owner_authenticated,false);assert.equal(r.writer_authorized,false);
 assert.equal(r.programme_progress,null);assert.equal(r.delp_projection,'NOT_CALCULATED');
};
async function bad(fn){
 const s=source();fn(s);
 const r=await observeEvidenceComment(input(),injected(s));
 assert.equal(r.material_observed,false);assert.equal(r.source_receipt,null);noAuthority(r);
}
test('U03 first and second native round attribute each endpoint without exposing provider errors',async()=>{
 const routes=[
  ['','REPOSITORY'],['issues/5','ROOT'],['issues/20','LEAF'],
  ['pulls/21','PR'],['issues/comments/'+C,'COMMENT'],['commits/'+H1,'COMMIT'],
 ];
 for(const [path,label] of routes)for(const phase of ['FIRST','SECOND']){
  const d=source();
  if(phase==='FIRST')d[path]=new Error('SECRET_PROVIDER_RESPONSE');
  const r=await observeEvidenceComment(input(),injected(d,(n,p,src)=>{
   if(phase==='SECOND'&&n===7)src[path]=new Error('SECRET_PROVIDER_RESPONSE');
  }));
  assert.equal(r.material_observed,false,label+phase);
  assert.deepEqual(r.errors,['PROVIDER_SOURCE_OR_CLAIM_UNVERIFIED']);
  assert.equal(r.failure_stage,phase+'_READ');
  assert.equal(r.failure_reason,label+'_GET_UNVERIFIED');
  assert.equal(r.source_receipt_sha256,null);noAuthority(r);
  assert.ok(!JSON.stringify(r).includes('SECRET_PROVIDER_RESPONSE'));
 }
});
test('U03 malformed native response is distinct from GET unavailable',async()=>{
 for(const [path,label] of [['','REPOSITORY'],['issues/comments/'+C,'COMMENT'],['commits/'+H1,'COMMIT']]){
  const d=source();d[path]=null;
  const r=await observeEvidenceComment(input(),injected(d));
  assert.equal(r.failure_stage,'FIRST_READ');
  assert.equal(r.failure_reason,label+'_RESPONSE_SHAPE_INVALID');noAuthority(r);
 }
});
test('U03 original validation retains safe reason for wrong source and author claims',async()=>{
 const cases=[
  ['REPO_MISMATCH',s=>{s[''].id=42;}],
  ['ROOT_INVALID',s=>{s['issues/5'].state='closed';}],
  ['LEAF_INVALID',s=>{s['issues/20'].number=999;}],
  ['PR_ROLE_INVALID',s=>{s['pulls/21'].head.sha='short';}],
  ['COMMENT_IDENTITY_INVALID',s=>{s['issues/comments/'+C].user.login='imposter';}],
  ['COMMIT_NOT_RESOLVED',s=>{s['commits/'+H1].sha=H2;}],
  ['NOT_TASK_EVIDENCE',s=>{s['issues/comments/'+C].body='## TASK_RESULT';}],
  ['HEAD_CLAIM_MISMATCH',s=>{s['issues/comments/'+C].body=body(H2);}],
  ['CURRENT_PR_BINDING_MISSING',s=>{s['issues/comments/'+C].body=body(H1,'https://github.com/reallaksh19/Common/pull/21');}],
 ];
 for(const [reason,change] of cases){
  const d=source();change(d);
  const r=await observeEvidenceComment(input(),injected(d));
  assert.equal(r.failure_stage,'FIRST_VALIDATE',reason);
  assert.equal(r.failure_reason,reason);
  assert.equal(r.source_currentness,'UNKNOWN');noAuthority(r);
 }
});
test('U03 edited receipt triggers second-round drift, never admitted material',async()=>{
 const r=await observeEvidenceComment(input(),injected(source(),(n,p,d)=>{
  if(n===7)d['issues/comments/'+C].body+=' edit';
 }));
 assert.deepEqual(r.errors,['PROVIDER_COMMENT_OR_HEAD_CHANGED_BETWEEN_READS']);
 assert.equal(r.failure_stage,'SECOND_ROUND_DRIFT');
 assert.equal(r.failure_reason,'SOURCE_RECEIPT_CHANGED');
 assert.equal(r.material_observed,false);noAuthority(r);
});
test('U03 source-authentic-looking successful read does not grant evidence',async()=>{
 const r=await observeEvidenceComment(input(),injected());
 assert.equal(r.failure_stage,null);assert.equal(r.failure_reason,null);
 assert.equal(r.material_observed,true);noAuthority(r);
});
test('U03 valid-shaped source is material only, never evidence admission',async()=>{
 let reads=0;
 const r=await observeEvidenceComment(input(),injected(source(),()=>reads++));
 assert.equal(reads,12);assert.equal(r.material_observed,true);
 assert.equal(r.source_currentness,'MATCH_AT_OBSERVATION');
 assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');
 assert.equal(r.source_receipt.comment_id,C);
 assert.equal(r.source_receipt.comment_author_login,'reallakshman19');
 assert.equal(r.body_claim_grade,'CLAIMED_TEXT_ONLY');
 assert.match(r.source_receipt_sha256,/^sha256:[0-9a-f]{64}$/);noAuthority(r);
});
test('U03 digest deterministic for same bytes',async()=>{
 const a=await observeEvidenceComment(input(),injected()),b=await observeEvidenceComment(input(),injected());
 assert.equal(a.source_receipt_sha256,b.source_receipt_sha256);
});
test('U03 pinned historical comment is observed but current PR head stale',async()=>{
 const s=source();s['pulls/21'].head.sha=H2;
 const r=await observeEvidenceComment(input(),injected(s));
 assert.equal(r.material_observed,true);assert.equal(r.source_currentness,'STALE_CANDIDATE_HEAD');noAuthority(r);
});
test('U03 old repository rejected pre-network',async()=>{
 let reads=0;
 const r=await observeEvidenceComment({...input(),repository:'reallaksh19/Common'},async()=>{reads++;});
 assert.equal(reads,0);assert.deepEqual(r.errors,['CURRENT_REPOSITORY_MISMATCH']);noAuthority(r);
});
test('U03 authority injected in caller contract rejected',async()=>{
 const r=await observeEvidenceComment({...input(),evidence_admitted:true},injected());
 assert.deepEqual(r.errors,['INPUT_SHAPE_INVALID']);noAuthority(r);
});
test('U03 malformed comment ID rejected',async()=>{
 const r=await observeEvidenceComment({...input(),evidence_comment_id:-1},injected());
 assert.deepEqual(r.errors,['ROLE_NUMBER_INVALID']);
});
test('U03 historical stable repository ID refused',()=>bad(s=>{s[''].id=1207996454;}));
test('U03 PR masquerading as child issue refused',()=>bad(s=>{s['issues/20'].pull_request={};}));
test('U03 wrong root issue refused',()=>bad(s=>{s['issues/5'].number=50;}));
test('U03 closed child issue refused',()=>bad(s=>{s['issues/20'].state='closed';}));
test('U03 historical PR source repo refused',()=>bad(s=>{s['pulls/21'].head.repo.full_name='reallaksh19/Common';}));
test('U03 forged comment ID refused',()=>bad(s=>{s['issues/comments/'+C].id=C+1;}));
test('U03 copied old repo comment URL refused',()=>bad(s=>{s['issues/comments/'+C].html_url='https://github.com/reallaksh19/Common/issues/20#issuecomment-'+C;}));
test('U03 comment belonging to root, not leaf, refused',()=>bad(s=>{s['issues/comments/'+C].issue_url='https://api.github.com/repos/'+R+'/issues/5';}));
test('U03 unexpected GitHub actor refused',()=>bad(s=>{s['issues/comments/'+C].user.login='other';}));
test('U03 GitHub bot not an expected user',()=>bad(s=>{s['issues/comments/'+C].user.type='Bot';}));
test('U03 no TASK_EVIDENCE heading refused',()=>bad(s=>{s['issues/comments/'+C].body='## TASK_RESULT\n'+body();}));
test('U03 incorrect claimed full source HEAD refused',()=>bad(s=>{s['issues/comments/'+C].body=body(H2);}));
test('U03 old repository PR URL cannot bind current PR',()=>bad(s=>{s['issues/comments/'+C].body=body(H1,'https://github.com/reallaksh19/Common/pull/21');}));
test('U03 duplicated Tested HEAD anchors refused',()=>bad(s=>{s['issues/comments/'+C].body=body()+'\n**Tested HEAD:** '+tick+H1+tick;}));
test('U03 independently unresolved commit refused',()=>bad(s=>{s['commits/'+H1].sha=H2;}));
test('U03 403, 404, 429 read failure refused without inventing absence',async()=>{
 for(const status of [403,404,429]){
  const s=source();s['issues/comments/'+C]=new Error(String(status));
  const r=await observeEvidenceComment(input(),injected(s));
  assert.equal(r.material_observed,false);assert.equal(r.source_currentness,'UNKNOWN');noAuthority(r);
 }
});
test('U03 edited comment between reads refused',async()=>{
 const s=source();const r=await observeEvidenceComment(input(),injected(s,(n,path,d)=>{
  if(n===7)d['issues/comments/'+C].body+='\nEDIT';
 }));
 assert.equal(r.material_observed,false);noAuthority(r);
});
test('U03 PR moved H1 to H2 between reads refused',async()=>{
 const s=source();const r=await observeEvidenceComment(input(),injected(s,(n,path,d)=>{
  if(n===7)d['pulls/21'].head.sha=H2;
 }));
 assert.equal(r.material_observed,false);noAuthority(r);
});
test('U03 caller-injected reader cannot claim native acquisition',async()=>{
 const r=await observeEvidenceComment(input(),injected(),{native:true});
 assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');noAuthority(r);
});
