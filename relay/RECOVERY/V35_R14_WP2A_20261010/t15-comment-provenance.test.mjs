import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectInjectedComments} from './t15-comment-provenance.mjs';
const R='reallakshman19/Common',API='https://api.github.com/repos/'+R;
const H='087cf43193febffc31375e71359e767489d3ae68';
const N='6a1598b0e09af0d0010a3e4c45ac3c0712799a66';
const H1='5d70e46d264909a576ccbbb074752004d1e9cb81';
const H2='eaa6ba95878e810f34c624354f7fc6e01f2e5bb0';
const items=[
 [6099941506,'## TASK_EVIDENCE — T05 PR #308 '+H+' NOT_ADMITTED source diagnostic. '.repeat(4)],
 [6100475989,('## TASK_RESULT — T11 PR #308 '+H+' '+N+' read-only HOLD. ').repeat(4)],
 [6100703214,('## TASK_RESULT — T12 '+N+' '+H1+' '+H2+' HOLD_STALE_H1 NOT_ADMITTED. ').repeat(4)],
];
const db=()=>{
 const out={'':{full_name:R,id:1412133785},'pulls/308':{number:308,state:'open',head:{sha:H}}};
 for(const [id,body] of items)out['issues/comments/'+id]={
  id,issue_url:API+'/issues/294',html_url:'https://github.com/'+R+'/issues/294#issuecomment-'+id,
  user:{login:'reallakshman19',id:277598171},body};
 return out;
};
function reader(d,hook=()=>{}){
 let n=0;return {read:async path=>{
  hook(++n,path,d);
  if(!Object.hasOwn(d,path))throw Error('TOKEN_FROM_PRIVATE_STORE');
  return structuredClone(d[path]);
 },calls:()=>n};
}
function gate(x){
 assert.equal(x.claim_grade,'AUTHOR_DIAGNOSTIC_ONLY_UNATTESTED_OWNER');
 assert.equal(x.comment_owner_authenticated,false);assert.equal(x.evidence_admitted,false);
 assert.equal(x.required_ci_qualified,false);assert.equal(x.independent_reviewer_qualified,false);
 assert.equal(x.delp_invoked,false);assert.equal(x.writer_authorized,false);
 assert.equal(x.publisher_authorized,false);assert.equal(x.programme_progress,null);
 assert.equal(x.observation_grade,'CALLER_INJECTED_UNATTESTED');
 assert.ok(!JSON.stringify(x).includes('TOKEN_FROM_PRIVATE_STORE'));
}
test('T15 all 3 current authored diagnostic comments match source meaning, not E',async()=>{
 const rr=reader(db());const x=await inspectInjectedComments(rr.read);
 assert.equal(x.status,'AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD');
 assert.equal(x.provider_pass_count,2);assert.equal(rr.calls(),12);
 assert.equal(x.comment_fingerprints.length,3);gate(x);
});
test('T15 correct issue URL but wrong body/source SHA cannot be used',async()=>{
 const d=db();d['issues/comments/6099941506'].body='## TASK_EVIDENCE PR #308 '+N+' NOT_ADMITTED '.repeat(5);
 const x=await inspectInjectedComments(reader(d).read);
 assert.equal(x.reason,'COMMENT_SOURCE_MEANING_MISMATCH');gate(x);
});
test('T15 T12 stale H1/H2 distinction cannot be silently omitted',async()=>{
 const d=db();d['issues/comments/6100703214'].body=('## TASK_RESULT '+H1+' '+H2+' NOT_ADMITTED ').repeat(4);
 const x=await inspectInjectedComments(reader(d).read);
 assert.equal(x.reason,'COMMENT_SOURCE_MEANING_MISMATCH');gate(x);
});
test('T15 old repo issue comment and forged actor are refused',async()=>{
 for(const change of [d=>d['issues/comments/6100475989'].user.id=1,
  d=>d['issues/comments/6099941506'].issue_url='https://api.github.com/repos/reallaksh19/Common/issues/294']){
  const d=db();change(d);
  const x=await inspectInjectedComments(reader(d).read);
  assert.equal(x.reason,'COMMENT_IDENTITY_CHANGED');gate(x);
 }
});
test('T15 comment body changes between rounds must deny the prior digest',async()=>{
 const d=db(),rr=reader(d,(n,p,y)=>{
  if(n===7)y['issues/comments/6100475989'].body+='Unattested edit!';
 });
 const x=await inspectInjectedComments(rr.read);
 assert.equal(x.status,'HOLD_COMMENT_DRIFT');
 assert.equal(x.reason,'COMMENT_EDITED_BETWEEN_READS');gate(x);
});
test('T15 comment producer PR moves mid-round and refuses claims',async()=>{
 const d=db(),rr=reader(d,(n,p,y)=>{
  if(n===6)y['pulls/308'].head.sha='a'.repeat(40);
 });
 const x=await inspectInjectedComments(rr.read);
 assert.equal(x.reason,'SOURCE_HEAD_CHANGED_DURING_ROUND');gate(x);
});
test('T15 new PR head H2 invalidates historical source claims',async()=>{
 const d=db();d['pulls/308'].head.sha='a'.repeat(40);
 const x=await inspectInjectedComments(reader(d).read);
 assert.equal(x.reason,'SOURCE_HEAD_CHANGED');gate(x);
});
test('T15 native reader exception never copies token',async()=>{
 const d=db(),rr=reader(d,(n)=>{if(n===4)throw Error('TOKEN_FROM_PRIVATE_STORE')});
 const x=await inspectInjectedComments(rr.read);
 assert.equal(x.reason,'PROVIDER_GET_UNKNOWN');gate(x);
});
