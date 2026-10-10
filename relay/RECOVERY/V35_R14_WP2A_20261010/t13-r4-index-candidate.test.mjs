import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {inspectInjectedCandidate,CANDIDATE_PATH} from './t13-r4-index-candidate.mjs';

const R='reallakshman19/Common',ID=1412133785,API='https://api.github.com/repos/'+R;
const S='e'.repeat(40),H='087cf43193febffc31375e71359e767489d3ae68';
const B='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const HB='codex/294-t05-wp2a-wp2b-negative-same-head';
const BB='codex/294-t01-wp2a-u02-u03-u04-pinned';
const issues=[5,284,294,20,30,289,288,12];
const comments=[[294,6099941506],[294,6100475989],[294,6100703214]];
const source=readFileSync(new URL('./t13-r4-index-candidate.json',import.meta.url));
const hash=b=>createHash('sha1').update(Buffer.concat([Buffer.from('blob '+b.length+'\0'),b])).digest('hex');
const locator=(bytes=source)=>({type:'file',path:CANDIDATE_PATH,encoding:'base64',
 sha:hash(bytes),content:Buffer.from(bytes).toString('base64')});
const issueUrl=n=>'https://github.com/'+R+'/issues/'+n;
const db=()=>{
 const data={
  ['contents/'+CANDIDATE_PATH+'?ref='+S]:locator(),
  '':{id:ID,full_name:R},
  'pulls/308':{number:308,state:'open',
   html_url:'https://github.com/'+R+'/pull/308',
   head:{sha:H,ref:HB,repo:{id:ID,full_name:R}},
   base:{sha:B,ref:BB,repo:{id:ID,full_name:R}}},
  ['git/ref/heads/'+HB]:{ref:'refs/heads/'+HB,object:{sha:H}},
  ['git/ref/heads/'+BB]:{ref:'refs/heads/'+BB,object:{sha:B}},
 };
 for(const n of issues)data['issues/'+n]={number:n,state:'open',html_url:issueUrl(n)};
 for(const [n,id] of comments)data['issues/comments/'+id]={
  id,html_url:issueUrl(n)+'#issuecomment-'+id,issue_url:API+'/issues/'+n};
 return data;
};
const reader=(records,hook=()=>{})=>{
 let calls=0;
 return {get:async p=>{
  calls++;hook(calls,p,records);
  if(!Object.hasOwn(records,p))throw Error('PRIVATE_TEST_ACCESS_SECRET');
  return structuredClone(records[p]);
 },count:()=>calls};
};
function noAuthority(v){
 assert.equal(v.index_authority,'NOT_GOVERNED_NOT_CANONICAL');
 assert.equal(v.candidate_class,'UNADOPTED_READ_ONLY_FIXTURE');
 assert.equal(v.entry_route,'REPOSITORY_INDEX_CANDIDATE_ONLY');
 assert.equal(v.observation_grade,'CALLER_INJECTED_UNATTESTED');
 assert.equal(v.r4_independent_trial,'NOT_RUN');
 assert.equal(v.owner_authenticated,false);
 assert.equal(v.admitted_graph,false);
 assert.equal(v.evidence_admitted,false);
 assert.equal(v.accepted_task_facts,false);
 assert.equal(v.independent_reviewer_qualified,false);
 assert.equal(v.effective_required_ci_qualified,false);
 assert.equal(v.delp_invoked,false);
 assert.equal(v.progress,null);
 assert.equal(v.writer_authorized,false);
 assert.equal(v.publisher_authorized,false);
 assert.equal(v.successor_writer_custody,false);
 assert.equal(v.next_permitted_action,'RECONCILE_REAL_CANONICAL_INDEX_AND_D1_D5_READ_ONLY');
 assert.ok(!JSON.stringify(v).includes('PRIVATE_TEST_ACCESS_SECRET'));
}
test('T13 complete candidate issue/comment/PR chain validates as non-governed only',async()=>{
 const r=reader(db()),v=await inspectInjectedCandidate(S,r.get);
 assert.equal(v.status,'CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD');
 assert.equal(v.index_links_verified,true);
 assert.equal(v.index_blob_sha,hash(source));
 assert.equal(v.source_head,H);
 assert.equal(v.provider_pass_count,2);
 assert.equal(r.count(),34);
 noAuthority(v);
});
test('T13 candidate locator wrong repo or historic repo ID fails closed',async()=>{
 const d=db();d[''].id=1207996454;
 const x=await inspectInjectedCandidate(S,reader(d).get);
 assert.equal(x.reason,'REPOSITORY_ID_MISMATCH');noAuthority(x);
});
test('T13 untrusted index cannot adopt itself by flipping kind or authority',async()=>{
 for(const patch of [m=>m.kind='CANONICAL_INDEX',m=>m.authority='OWNER_ADOPTED']){
  const m=JSON.parse(source);patch(m);const d=db();
  d['contents/'+CANDIDATE_PATH+'?ref='+S]=locator(Buffer.from(JSON.stringify(m)));
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'CANDIDATE_INDEX_SCHEMA_OR_LINK_MISMATCH');noAuthority(v);
 }
});
test('T13 internally consistent but wrong source/head link rejected',async()=>{
 const m=JSON.parse(source);m.source.head_sha='a'.repeat(40);
 const d=db();d['contents/'+CANDIDATE_PATH+'?ref='+S]=locator(Buffer.from(JSON.stringify(m)));
 const v=await inspectInjectedCandidate(S,reader(d).get);
 assert.equal(v.reason,'CANDIDATE_INDEX_SCHEMA_OR_LINK_MISMATCH');noAuthority(v);
});
test('T13 poisoned parent, source owner, consumer, policy or successor issue URL refused',async()=>{
 for(const n of [5,294,20,30,289,288,12,284]){
  const m=JSON.parse(source);m.issue_links.find(x=>x.number===n).url='https://github.com/reallaksh19/Common/issues/'+n;
  const d=db();d['contents/'+CANDIDATE_PATH+'?ref='+S]=locator(Buffer.from(JSON.stringify(m)));
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'CANDIDATE_INDEX_SCHEMA_OR_LINK_MISMATCH');
  noAuthority(v);
 }
});
test('T13 forged or cross-repo comment deep link rejected',async()=>{
 for(const id of comments.map(x=>x[1])){
  const m=JSON.parse(source);
  m.evidence_links.find(x=>x.comment_id===id).url='https://github.com/reallaksh19/Common/issues/294#issuecomment-'+id;
  const d=db();d['contents/'+CANDIDATE_PATH+'?ref='+S]=locator(Buffer.from(JSON.stringify(m)));
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'CANDIDATE_INDEX_SCHEMA_OR_LINK_MISMATCH');noAuthority(v);
 }
});
test('T13 PR308 actual HEAD move invalidates draft repository locator',async()=>{
 const d=db();d['pulls/308'].head.sha='a'.repeat(40);
 const v=await inspectInjectedCandidate(S,reader(d).get);
 assert.equal(v.reason,'PR308_IDENTITY_OR_SOURCE_CHANGED');noAuthority(v);
});
test('T13 actual provider PR URL spoof or old identity rejected',async()=>{
 for(const change of [d=>d['pulls/308'].html_url='https://github.com/'+R+'/pull/292',
    d=>d['pulls/308'].head.repo.id=1207996454]){
  const d=db();change(d);
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'PR308_IDENTITY_OR_SOURCE_CHANGED');noAuthority(v);
 }
});
test('T13 branch-head or base-ref drift rejects seemingly current PR',async()=>{
 for(const role of [HB,BB]){
  const d=db();d['git/ref/heads/'+role].object.sha='a'.repeat(40);
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'SOURCE_BRANCH_REF_CHANGED');noAuthority(v);
 }
});
test('T13 live issue link or PR-shaped issue mismatch rejected',async()=>{
 for(const mutate of [d=>d['issues/288'].html_url=issueUrl(20),
    d=>d['issues/289'].pull_request={}]){
  const d=db();mutate(d);
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'ISSUE_LINK_CHANGED');noAuthority(v);
 }
});
test('T13 live comment ID or issue relationship swap rejected',async()=>{
 for(const mutate of [d=>d['issues/comments/6099941506'].id=333,
    d=>d['issues/comments/6100703214'].issue_url=API+'/issues/30']){
  const d=db();mutate(d);
  const v=await inspectInjectedCandidate(S,reader(d).get);
  assert.equal(v.reason,'EVIDENCE_COMMENT_LINK_CHANGED');noAuthority(v);
 }
});
test('T13 missing physical comment returns unknown not false absence',async()=>{
 const d=db();delete d['issues/comments/6100475989'];
 const v=await inspectInjectedCandidate(S,reader(d).get);
 assert.equal(v.status,'HOLD_LINK_OR_PROVIDER');
 assert.equal(v.reason,'NATIVE_PROVIDER_GET_FAILED');noAuthority(v);
});
test('T13 provider moves PR head between first and second passes, fail closed',async()=>{
 const d=db();const r=reader(d,(n,p,x)=>{
  if(n===18)x['pulls/308'].head.sha='a'.repeat(40);
 });
 const v=await inspectInjectedCandidate(S,r.get);
 assert.equal(v.status,'HOLD_LINK_OR_PROVIDER');
 assert.equal(v.reason,'PR308_IDENTITY_OR_SOURCE_CHANGED');noAuthority(v);
});
test('T13 PR head moves at late same-pass check and is refused',async()=>{
 const d=db();const r=reader(d,(n,p,x)=>{
  if(n===17)x['pulls/308'].head.sha='a'.repeat(40);
 });
 const v=await inspectInjectedCandidate(S,r.get);
 assert.equal(v.reason,'SOURCE_CHANGED_BETWEEN_PASSES');noAuthority(v);
});
test('T13 bytes changed under previous Git blob hash get refused',async()=>{
 const d=db();const meta=d['contents/'+CANDIDATE_PATH+'?ref='+S];
 meta.content=Buffer.from('not same bytes').toString('base64');
 const v=await inspectInjectedCandidate(S,reader(d).get);
 assert.equal(v.reason,'CANDIDATE_BYTES_UNVERIFIED');noAuthority(v);
});
test('T13 invalid tested candidate HEAD refused before GET',async()=>{
 const r=reader(db()),v=await inspectInjectedCandidate('historical-main',r.get);
 assert.equal(v.reason,'BAD_TESTED_SHA');
 assert.equal(r.count(),0);noAuthority(v);
});
test('T13 fake reviewer grants in issue fields cannot mint an admitted R4 index',async()=>{
 const d=db();d['issues/5'].owner_authenticated=true;
 d['issues/288'].r4_qualified=true;d['pulls/308'].evidence_admitted=true;
 const v=await inspectInjectedCandidate(S,reader(d).get);
 assert.equal(v.index_links_verified,true);noAuthority(v);
});
test('T13 secret-bearing native failure cannot leak provider response',async()=>{
 const d=db();const rr=reader(d,(n)=>{if(n===8)throw Error('PRIVATE_TEST_ACCESS_SECRET')});
 const v=await inspectInjectedCandidate(S,rr.get);
 assert.equal(v.reason,'NATIVE_PROVIDER_GET_FAILED');noAuthority(v);
});
