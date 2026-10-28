import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateDeclaredScope as evaluate,ScopePolicyError} from './owner-decision-scope-v1.mjs';
const P='reallaksh19/Common#787',S='b89993d7e256522156ee71da6af9e7e81c9fcdd0',H='a'.repeat(64);
const G=()=>({
 schema:'relay-declared-grant-v1',grant_id:'G1',revision_sha:'a'.repeat(40),
 parent_issue:P,principal_login:'reallaksh19',role:'OWNER',
 actions:['RESEARCH_ADOPTION','TASK_RELEASE'],claim_ids:['AC7','AC2'],
 resources:['reallaksh19/Common#787'],exact_head_sha:S,
 valid_from:'2026-10-08T00:00:00Z',valid_until:'2026-10-09T00:00:00Z',
 revoked_at:null,source_comment_url:'https://github.com/reallaksh19/Common/issues/787#issuecomment-6064020826',
 source_body_sha256:H
});
const R=()=>({
 schema:'relay-decision-candidate-v1',decision_id:'D1',parent_issue:P,claim_id:'AC7',
 issuer_login:'reallaksh19',role:'OWNER',action:'RESEARCH_ADOPTION',
 resource:'reallaksh19/Common#787',exact_head_sha:S,issued_at:'2026-10-08T13:00:00Z',
 finding_ids:['F1'],subject_author_login:null,
 source_receipt:{status:'PROVIDER_ISSUER_OBSERVED',transport:'NATIVE_FIXED_HTTPS_GET',
 author_login:'reallaksh19',
 source_url:'https://github.com/reallaksh19/Common/issues/787#issuecomment-6064020826',
 body_sha256:H}
});
const edit=(mut)=>{const g=G(),r=R();mut(g,r);return evaluate(g,r)};
test('a perfect declared match is NOT an actual Owner permission',()=>{
 const result=evaluate(G(),R());
 assert.equal(result.status,'MATCHES_DECLARED_POLICY_ONLY');
 assert.equal(result.candidate_scope_match,true);
 assert.equal(result.authorization_granted,false);
 assert.equal(result.trusted_issuer_verified,false);
 assert.equal(result.requires_native_provider_recheck,true);
 assert.equal(result.independently_accepted,false);
});
const cases=[
 ['different parent',(g,r)=>r.parent_issue='reallaksh19/Common#600','PARENT_MISMATCH'],
 ['different issuer',(g,r)=>r.issuer_login='attacker','ISSUER_MISMATCH'],
 ['different role',(g,r)=>r.role='COORDINATOR','ROLE_MISMATCH'],
 ['role cannot adopt research',(g,r)=>r.role='COORDINATOR','ROLE_ACTION_FORBIDDEN'],
 ['forbidden action',(g,r)=>r.action='MERGE_AUTHORITY','ACTION_OUT_OF_SCOPE'],
 ['wrong claim',(g,r)=>r.claim_id='AC8','CLAIM_OUT_OF_SCOPE'],
 ['wrong exact resource',(g,r)=>r.resource='reallaksh19/Common#789','RESOURCE_OUT_OF_SCOPE'],
 ['changed PR head',(g,r)=>r.exact_head_sha='b'.repeat(40),'EXACT_HEAD_NOT_BOUND'],
 ['missing exact head',(g,r)=>r.exact_head_sha=null,'EXACT_HEAD_NOT_BOUND'],
 ['unbound grant',(g,r)=>g.exact_head_sha=null,'EXACT_HEAD_NOT_BOUND'],
 ['issued before grant',(g,r)=>r.issued_at='2026-10-07T23:59:59Z','BEFORE_GRANT'],
 ['expired grant',(g,r)=>r.issued_at='2026-10-10T00:00:00Z','GRANT_EXPIRED'],
 ['revoked grant',(g,r)=>g.revoked_at='2026-10-08T12:00:00Z','GRANT_REVOKED'],
 ['forged injected transport',(g,r)=>r.source_receipt.transport='INJECTED_UNVERIFIED','NOT_NATIVE_SOURCE_OBSERVATION'],
 ['fake source status',(g,r)=>r.source_receipt.status='CLAIMED','NOT_NATIVE_SOURCE_OBSERVATION'],
 ['mismatched comment author',(g,r)=>r.source_receipt.author_login='agent','RECEIPT_ISSUER_MISMATCH'],
 ['not a real GitHub comment URL',(g,r)=>r.source_receipt.source_url='https://evil.invalid/comment','NOT_GITHUB_COMMENT'],
 ['research not adopted',(g,r)=>r.finding_ids=[],'MISSING_RESEARCH_FINDING'],
 ['finding IDs on task release',(g,r)=>{r.action='TASK_RELEASE';r.finding_ids=['F1']},'UNEXPECTED_RESEARCH_FINDING']
];
for(const [name,mut,reason]of cases)test('denies '+name,()=>{
 const result=edit(mut);
 assert.equal(result.candidate_scope_match,false);
 assert.equal(result.authorization_granted,false);
 assert.ok(result.reasons.includes(reason),JSON.stringify(result.reasons));
});
test('refuses unauthenticated reviewer self-review even with declared matching reviewer grant',()=>{
 const result=edit((g,r)=>{
  g.role='REVIEWER';g.actions=['REVIEW_VERDICT'];g.claim_ids=['AC4'];
  r.role='REVIEWER';r.action='REVIEW_VERDICT';r.claim_id='AC4';
  r.finding_ids=[];r.subject_author_login='reallaksh19';
 });
 assert.equal(result.authorization_granted,false);
 assert.ok(result.reasons.includes('SELF_REVIEW'));
});
test('different-principal reviewer scope can match but never authorizes review submission',()=>{
 const result=edit((g,r)=>{
  g.role='REVIEWER';g.actions=['REVIEW_VERDICT'];g.claim_ids=['AC4'];
  r.role='REVIEWER';r.action='REVIEW_VERDICT';r.claim_id='AC4';
  r.finding_ids=[];r.subject_author_login='implementer';
 });
 assert.equal(result.candidate_scope_match,true);
 assert.equal(result.authorization_granted,false);
});
test('wrong expected schema and injected approval keys are rejected',()=>{
 const a=G(),p=R();a.schema='v99';assert.throws(()=>evaluate(a,p),ScopePolicyError);
 const b=G();b.owner_approved=true;assert.throws(()=>evaluate(b,p),ScopePolicyError);
});
test('invalid timestamp, digest, sha and duplicate action fail closed',()=>{
 assert.throws(()=>edit((g,r)=>r.issued_at='2026-10-08T25:00:00Z'),ScopePolicyError);
 assert.throws(()=>edit((g,r)=>r.source_receipt.body_sha256='fake'),ScopePolicyError);
 assert.throws(()=>edit((g,r)=>g.revision_sha='fake'),ScopePolicyError);
 assert.throws(()=>edit((g,r)=>g.actions.push('RESEARCH_ADOPTION')),ScopePolicyError);
});
test('blank and oversized scope definitions fail closed',()=>{
 assert.throws(()=>edit((g,r)=>g.claim_ids=[]),ScopePolicyError);
 assert.throws(()=>edit((g,r)=>g.claim_ids=Array.from({length:129},(_,i)=>'AC'+i)),ScopePolicyError);
});
test('authority is never minted even if caller explicitly forges OWNER receipt and grant',()=>{
 const result=evaluate(G(),R());
 assert.equal(Object.hasOwn(result,'write_permission'),false);
 assert.equal(result.authorization_granted,false);
});

test('a lookalike GitHub comment from a different repository never matches',()=>{
 const r=edit((g,p)=>p.source_receipt.source_url=
   'https://github.com/attacker/Common/issues/787#issuecomment-6064020826');
 assert.equal(r.candidate_scope_match,false);
 assert.ok(r.reasons.includes('COMMENT_REPO_MISMATCH'));
});
test('an Owner-declared grant sourced in a different repository cannot match',()=>{
 const r=edit((g,p)=>g.source_comment_url=
   'https://github.com/attacker/Common/issues/787#issuecomment-6064020826');
 assert.equal(r.candidate_scope_match,false);
 assert.ok(r.reasons.includes('GRANT_SOURCE_REPO_MISMATCH'));
});
test('cross-repository resource remains ineligible even if fake grant lists it',()=>{
 const r=edit((g,p)=>{
   g.resources=['attacker/Common#787'];p.resource='attacker/Common#787';
 });
 assert.equal(r.candidate_scope_match,false);
 assert.ok(r.reasons.includes('RESOURCE_REPO_MISMATCH'));
});
