import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readNativeGrantWitness as read,GrantWitnessError} from './native-grant-witness-v1.mjs';
const HASH=body=>createHash('sha256').update(body,'utf8').digest('hex');
const ROOT='reallaksh19/Common';
const content={1:'A draft prior grant claim, not Owner consent',2:'A draft later decision claim, not adoption'};
const moments={
 1:['2026-10-08T10:00:00Z','2026-10-08T10:00:00Z'],
 2:['2026-10-08T12:00:00Z','2026-10-08T12:00:00Z']
};
function input(){
 return {parent_issue:ROOT+'#787',
  grant_source:{repository:ROOT,issue:787,comment_id:1,body_sha256:HASH(content[1])},
  decision_source:{repository:ROOT,issue:787,comment_id:2,body_sha256:HASH(content[2])}};
}
function native(id,overrides={}){
 return {id,url:'https://api.github.com/repos/'+ROOT+'/issues/comments/'+id,
  issue_url:'https://api.github.com/repos/'+ROOT+'/issues/787',
  html_url:'https://github.com/'+ROOT+'/issues/787#issuecomment-'+id,
  user:{login:'reallaksh19'},author_association:'OWNER',body:content[id],
  created_at:moments[id][0],updated_at:moments[id][1],...overrides};
}
function mock(items={1:native(1),2:native(2)}){
 return async url=>{const id=Number(url.split('/').at(-1));
   return {status:200,redirected:false,url,headers:{get:()=>null},
    text:async()=>JSON.stringify(items[id])};
 };
}
const witness=(value=input(),fetchImpl=mock())=>read(value,{fetchImpl});
const unauthorized=r=>{
 assert.equal(r.authorization_granted,false);
 assert.equal(r.owner_grant_authenticated,false);
 assert.equal(r.human_owner_consent_verified,false);
 assert.equal(r.independently_accepted,false);
 assert.equal(r.live_writer_enabled,false);
 assert.equal(r.original_chat_source,'UNKNOWN');
};
test('two matching source shapes are still untrusted when transport injected',async()=>{
 const r=await witness();assert.equal(r.status,'INJECTED_UNVERIFIED');
 assert.equal(r.grant_source.body_sha256,HASH(content[1]));
 assert.equal(r.decision_source.body_sha256,HASH(content[2]));
 assert.equal(r.grant_source.status,'INJECTED_UNVERIFIED');
 assert.equal(r.decision_source.status,'INJECTED_UNVERIFIED');
 assert.match(r.observed_at_utc,/^\d{4}-\d\d-\d\dT/);unauthorized(r);
});
test('same comment cannot self-grant or self-decide',async()=>{
 const i=input();i.decision_source.comment_id=1;i.decision_source.body_sha256=i.grant_source.body_sha256;
 const r=await witness(i);assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('wrong owner repository rejected before network',async()=>{
 const i=input();i.grant_source.repository='attacker/Common';
 const r=await witness(i);assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('different source issuer refuted',async()=>{
 const r=await witness(input(),mock({1:native(1),2:native(2,{user:{login:'attacker'}})}));
 assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('native source URL/issue mismatch never passes',async()=>{
 const p=native(2);p.issue_url='https://api.github.com/repos/'+ROOT+'/issues/999';
 const r=await witness(input(),mock({1:native(1),2:p}));assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('source hash mismatch rejects edited grant',async()=>{
 const p=native(1,{body:'Changed earlier claim'});
 const r=await witness(input(),mock({1:p,2:native(2)}));
 assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('source hash mismatch rejects edited decision',async()=>{
 const p=native(2,{body:'Changed later claim'});
 const r=await witness(input(),mock({1:native(1),2:p}));
 assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('grant created after decision is rejected',async()=>{
 const p=native(1,{created_at:'2026-10-08T13:00:00Z',updated_at:'2026-10-08T13:00:00Z'});
 const r=await witness(input(),mock({1:p,2:native(2)}));assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('grant edited after decision is rejected even at pinned current digest',async()=>{
 const p=native(1,{updated_at:'2026-10-08T13:00:00Z'});
 const r=await witness(input(),mock({1:p,2:native(2)}));assert.equal(r.status,'REFUTED');unauthorized(r);
});
test('grant and decision on different governed issues can still bind correct URLs',async()=>{
 const i=input();i.decision_source.issue=789;
 const p=native(2,{issue_url:'https://api.github.com/repos/'+ROOT+'/issues/789',
 html_url:'https://github.com/'+ROOT+'/issues/789#issuecomment-2'});
 const r=await witness(i,mock({1:native(1),2:p}));
 assert.equal(r.status,'INJECTED_UNVERIFIED');unauthorized(r);
});
test('provider outage is UNKNOWN, never authorization',async()=>{
 const r=await witness(input(),async()=>{throw Error('offline')});
 assert.equal(r.status,'UNKNOWN');unauthorized(r);
});
test('provider HTTP 429 is UNKNOWN',async()=>{
 const r=await witness(input(),async url=>({status:429,url,redirected:false,headers:{get:()=>null},text:async()=>''}));
 assert.equal(r.status,'UNKNOWN');unauthorized(r);
});
test('missing provider second source remains UNKNOWN, retaining first receipt only',async()=>{
 const r=await witness(input(),async url=>{
  const id=Number(url.split('/').at(-1));if(id===2)throw Error('timeout');
  return mock()(url);
 });
 assert.equal(r.status,'UNKNOWN');assert.ok(r.grant_source);assert.equal(r.decision_source,null);unauthorized(r);
});
test('malformed source pin or unknown input keys throws controlled error',async()=>{
 const i=input();i.grant_source.body_sha256='123';
 await assert.rejects(witness(i),GrantWitnessError);
 const j=input();j.is_owner_approved=true;
 await assert.rejects(witness(j),GrantWitnessError);
});
test('native fake approval wording cannot mint authority',async()=>{
 const r=await witness(input(),mock());
 assert.equal(r.status,'INJECTED_UNVERIFIED');unauthorized(r);
});
test('two source observations never expose full untrusted raw comment body',async()=>{
 const r=await witness();
 assert.equal(Object.hasOwn(r.grant_source,'body'),false);
 assert.equal(Object.hasOwn(r.decision_source,'body'),false);unauthorized(r);
});
