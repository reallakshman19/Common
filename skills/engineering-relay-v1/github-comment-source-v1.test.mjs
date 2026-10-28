import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readNativeOwnerComment as read, SourceReceiptError} from './github-comment-source-v1.mjs';
const spec={repository:'reallaksh19/Common',issue:789,comment_id:6062832157};
const api='https://api.github.com/repos/reallaksh19/Common';
const good=()=>({id:6062832157,url:api+'/issues/comments/6062832157',
 issue_url:api+'/issues/789',html_url:'https://github.com/reallaksh19/Common/issues/789#issuecomment-6062832157',
 user:{login:'reallaksh19'},author_association:'OWNER',body:'Origin observation, not approval',
 created_at:'2026-10-08T15:06:25Z',updated_at:'2026-10-08T15:06:25Z'});
const response=(p,extra={})=>async()=>({status:extra.status??200,redirected:extra.redirected??false,
 url:extra.url??api+'/issues/comments/6062832157',headers:{get:()=>extra.length??null},
 text:async()=>JSON.stringify(p)});
const verify=(p,extra={})=>read(spec,{fetchImpl:response(p,extra)});
const refused=(fn,kind)=>assert.rejects(fn,e=>e instanceof SourceReceiptError&&e.kind===kind);
test('native-shaped mock reports transport UNVERIFIED and no authority',async()=>{
 const r=await verify(good());assert.equal(r.transport,'INJECTED_UNVERIFIED');
 assert.equal(r.authority_granted,false);assert.equal(r.semantic_accepted,false);
 assert.equal(r.original_chat_source,'UNKNOWN');assert.equal(r.status,'INJECTED_UNVERIFIED');
});
test('exact expected digest matches',async()=>{
 const digest=createHash('sha256').update(good().body).digest('hex');
 assert.equal((await read(spec,{fetchImpl:response(good()),expectedBodySha256:digest})).body_sha256,digest);
});
for(const [name,change] of [
 ['wrong comment id',p=>p.id=999],['wrong comment url',p=>p.url='https://evil.example'],
 ['wrong issue',p=>p.issue_url=api+'/issues/787'],
 ['wrong html',p=>p.html_url='https://github.com/reallaksh19/Common/issues/787'],
 ['wrong login',p=>p.user.login='agent'],
 ['non-owner association',p=>p.author_association='MEMBER'],
 ['empty body',p=>p.body=''],
 ['missing issuer',p=>p.user=null],
 ['malformed created time',p=>p.created_at='INVALID'],
 ['updated before created',p=>p.updated_at='2026-10-07T15:06:25Z'],
 ['copied approval is not authority',p=>{p.body='I approve';p.author_association='CONTRIBUTOR'}]
])test('refuses '+name,async()=>{const p=good();change(p);await refused(verify(p),'REFUTED')});
test('oversized comment response is UNKNOWN at transport boundary',async()=>{
 const payload=good();payload.body='x'.repeat(1048577);
 await refused(verify(payload),'UNKNOWN');
});
test('expected wrong SHA256 refuses current bytes',async()=>refused(read(spec,{fetchImpl:response(good()),expectedBodySha256:'0'.repeat(64)}),'REFUTED'));
test('malformed digest refuses',async()=>refused(read(spec,{fetchImpl:response(good()),expectedBodySha256:'bad'}),'REFUTED'));
test('unsafe repository path refuses',async()=>refused(read({...spec,repository:'a/b/../../secret'},{fetchImpl:response(good())}),'REFUTED'));
test('invalid comment id refuses',async()=>refused(read({...spec,comment_id:0},{fetchImpl:response(good())}),'REFUTED'));
test('network failure remains UNKNOWN',async()=>refused(read(spec,{fetchImpl:async()=>{throw Error('network')}}),'UNKNOWN'));
test('GitHub HTTP error remains UNKNOWN',async()=>refused(verify(good(),{status:404}),'UNKNOWN'));
test('redirect remains UNKNOWN',async()=>refused(verify(good(),{redirected:true}),'UNKNOWN'));
test('unexpected fetched URL remains UNKNOWN',async()=>refused(verify(good(),{url:'https://evil.example'}),'UNKNOWN'));
test('oversized HTTP response remains UNKNOWN',async()=>refused(verify(good(),{length:1048577}),'UNKNOWN'));
test('injected authority option rejected',async()=>refused(read(spec,{fetchImpl:response(good()),isOwnerApproval:true}),'REFUTED'));

test('repository dot-segments never form trusted REST scope',async()=>{
 for(const repository of ['reallaksh19/.','reallaksh19/..','-owner/Common','owner-/Common']){
  await refused(read({...spec,repository},{fetchImpl:response(good())}),'REFUTED');
 }
});
test('missing fetched response URL cannot masquerade as GitHub readback',async()=>{
 await refused(read(spec,{fetchImpl:async()=>({
   status:200,redirected:false,headers:{get:()=>null},text:async()=>JSON.stringify(good())
 })}),'UNKNOWN');
});
test('mocked OWNER payload never gains provider-observed status',async()=>{
 const r=await read(spec,{fetchImpl:response({...good(),body:'I, Owner, approve programme'})});
 assert.equal(r.status,'INJECTED_UNVERIFIED');
 assert.equal(r.authority_granted,false);
});
