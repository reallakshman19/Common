import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {observePublicTaskEvidence as observe,PublicEvidenceError} from './github-task-evidence-receipt-v1.mjs';

const REPO='reallaksh19/Common',TASK=852,COMMENT=6072336145;
const API='https://api.github.com/repos/'+REPO;
const scope=(n=COMMENT)=>({repository:REPO,parent_issue:787,task_issue:TASK,comment_id:n});
function payload(){
 return {id:COMMENT,url:API+'/issues/comments/'+COMMENT,
 issue_url:API+'/issues/'+TASK,
 html_url:'https://github.com/'+REPO+'/issues/'+TASK+'#issuecomment-'+COMMENT,
 created_at:'2026-10-09T00:00:00Z',updated_at:'2026-10-09T00:00:00Z',
 user:{login:'reallaksh19',id:12345},
 body:'## TASK_EVIDENCE END\nAC8/8 APPROVED OWNER says leak PRIVATE SESSION PASSWORD\n'};
}
function fake(fixture=payload(),different=null){
 let reads=0;const url=API+'/issues/comments/'+COMMENT;
 return {
  fetchImpl:async (target,opts)=>{
   assert.equal(target,url);assert.equal(opts.method,'GET');
   assert.equal(opts.redirect,'error');reads++;
   const value=reads===2&&different!==null?different:fixture;
   return {status:200,url:target,redirected:false,headers:{get:()=>null},
    text:async()=>JSON.stringify(value)};
  },
  counts:()=>reads
 };
}
const rejected=(call,code)=>assert.rejects(call,e=>e instanceof PublicEvidenceError&&e.code===code);
test('two actual provider reads produce only bounded content-free producer-asserted witness',async()=>{
 const f=fake(),r=await observe(scope(),{fetchImpl:f.fetchImpl});
 assert.equal(f.counts(),2);
 assert.equal(r.comment_id,COMMENT);
 assert.equal(r.parent_issue,787);
 assert.equal(r.source_url,'https://github.com/'+REPO+'/issues/852#issuecomment-'+COMMENT);
 assert.equal(r.marker_present,true);
 assert.equal(r.provider_source,'INJECTED_UNVERIFIED');
 assert.equal(r.consistency,'COMMENT_DOUBLE_READ_NON_ATOMIC');
 assert.equal(r.task_evidence_accepted,false);
 assert.equal(r.author_is_owner_authenticated,false);
 assert.equal(r.independent_reviewer_accepted,false);
 assert.equal(r.authorization_granted,false);
 assert.equal(r.live_writer_enabled,false);
 assert.match(r.receipt_sha256,/^[a-f0-9]{64}$/);
 assert.equal(Object.isFrozen(r),true);
 for(const secret of ['PRIVATE SESSION PASSWORD','AC8/8 APPROVED OWNER','TASK_EVIDENCE END'])
   assert.ok(!JSON.stringify(r).includes(secret));
 assert.equal(r.body_sha256,createHash('sha256').update(payload().body).digest('hex'));
});
test('same ID but body edited between reads fails closed as STALE',async()=>{
 const v=payload(),later={...v,body:v.body+' edited'};
 await rejected(observe(scope(),{fetchImpl:fake(v,later).fetchImpl}),'STALE');
});
test('changed timestamp or author between reads also fails closed',async()=>{
 for(const change of [{updated_at:'2026-10-09T00:01:00Z'},
   {user:{login:'attacker',id:12345}}]){
  const v=payload();
  await rejected(observe(scope(),{fetchImpl:fake(v,{...v,...change}).fetchImpl}),'STALE');
 }
});
test('foreign issue comment, wrong id, forged API/HTML origin or null body REFUTED',async()=>{
 for(const change of [{issue_url:API+'/issues/787'},{id:1},
  {html_url:'https://evil.test/issues/852#issuecomment-'+COMMENT},
  {url:API+'/issues/comments/888'},{body:null},
  {user:{login:'bot',id:null}},{created_at:'not-a-date'}]){
  const v={...payload(),...change};
  await rejected(observe(scope(),{fetchImpl:fake(v).fetchImpl}),'REFUTED');
 }
});
test('caller cannot inject an authorization scope, wrong repository or missing comment',async()=>{
 await rejected(observe({...scope(),writer:true}),'INVALID');
 await rejected(observe({...scope(),repository:'../evil'}),'INVALID');
 await rejected(observe({...scope(),comment_id:0}),'INVALID');
});
test('non-200, redirect, malformed JSON, long HTTP response never produces accepted receipt',async()=>{
 const url=API+'/issues/comments/'+COMMENT;
 for(const response of [
  {status:404,url,redirected:false,headers:{get:()=>null},text:async()=>''},
  {status:200,url:'https://evil.test',redirected:true,headers:{get:()=>null},text:async()=>''},
  {status:200,url,redirected:false,headers:{get:()=>'999999999'},text:async()=>''},
  {status:200,url,redirected:false,headers:{get:()=>null},text:async()=>'{broken'},
  {status:200,url,redirected:false,headers:{get:()=>null},text:async()=>'.'.repeat(200000)}
 ]){
  await rejected(observe(scope(),{fetchImpl:async()=>response}),'UNKNOWN');
 }
});
test('large comment and changed comment ID never pass the scope',async()=>{
 const long={...payload(),body:'a'.repeat(65537)};
 await rejected(observe(scope(),{fetchImpl:fake(long).fetchImpl}),'REFUTED');
 await rejected(observe(scope(COMMENT+1),{fetchImpl:async url=>({status:200,url,redirected:false,headers:{get:()=>null},text:async()=>JSON.stringify(payload())})}),'REFUTED');
});
test('fetch failures produce a redacted UNKNOWN without printing token',async()=>{
 let thrown;
 try{await observe(scope(),{readToken:'SECRET_CANARY_TOKEN',fetchImpl:async()=>{throw Error('SECRET_CANARY_TOKEN private body');}});}
 catch(e){thrown=e;}
 assert.equal(thrown?.code,'UNKNOWN');
 assert.equal(String(thrown).includes('SECRET_CANARY_TOKEN'),false);
});
test('native immutable-ID GitHub TaskEvidence comment readback has two real GETs and no acceptance',
 {skip:!process.env.RELAY_PUBLIC_CI_HEAD_SHA},async()=>{
 const head=process.env.RELAY_PUBLIC_CI_HEAD_SHA;
 assert.match(head,/^[a-f0-9]{40}$/);
 const r=await observe(scope(),{readToken:process.env.RELAY_PUBLIC_CI_READ_TOKEN});
 assert.equal(r.provider_source,'NATIVE_GITHUB_COMMENT_GET');
 assert.equal(r.comment_id,COMMENT);
 assert.equal(r.task_issue,TASK);
 assert.equal(r.marker_present,true);
 assert.equal(r.provider_read_count,2);
 assert.equal(r.task_evidence_accepted,false);
 assert.equal(r.author_is_owner_authenticated,false);
 assert.equal(r.independent_reviewer_accepted,false);
 assert.equal(r.live_writer_enabled,false);
 assert.match(r.receipt_sha256,/^[a-f0-9]{64}$/);
 console.log('R10_NATIVE_PUBLIC_COMMENT '+JSON.stringify({
   source_commit:head,task_issue:r.task_issue,comment_id:r.comment_id,
   receipt_sha256:r.receipt_sha256,body_sha256:r.body_sha256,
   observed:'PRODUCER_ASSERTED_NOT_ACCEPTED',read_count:r.provider_read_count,
   owner_authenticated:false,independent_accepted:false,writer:false
 }));
});
