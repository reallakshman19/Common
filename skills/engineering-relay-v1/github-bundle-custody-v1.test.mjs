import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {verifyPortableJournal} from './session-bundle-v1.mjs';
import {canonicalJSON} from './provenance-v1.mjs';
import {readCommittedPortableJournal as read,CustodyError} from './github-bundle-custody-v1.mjs';

const REPO='reallaksh19/Common',PARENT=REPO+'#787';
const SOURCE='28841b5cfed9e9b6057a1a6f09090adcc512e1b8';
const PATH='skills/engineering-relay-v1/fixtures/b2a-synthetic-journal-v1.json';
const BUNDLE='79c2bc0b84f23a862e3ce7cef300c1b2dd1c4b90d00a448a8f1a269d1ddb0e9d';
const TIP='3077376e2d5fe849de1450d9f2cc8e6d350742dc0d98969a36e778000d052660';
const H=x=>createHash('sha256').update(x).digest('hex');
const blob=x=>createHash('sha1').update('blob '+x.length+'\0').update(x).digest('hex');
const fixture=()=>readFile(new URL('./fixtures/b2a-synthetic-journal-v1.json',import.meta.url));
const spec=(sha=SOURCE)=>({repository:REPO,parent_issue:PARENT,commit_sha:sha,path:PATH,
  source_sha:SOURCE,bundle_sha256:BUNDLE,tip_sha256:TIP});
function response(specifier,data,overrides={}) {
  const expectedUrl='https://api.github.com/repos/'+specifier.repository+'/contents/'+specifier.path+
    '?ref='+specifier.commit_sha;
  const obj={type:'file',name:specifier.path.split('/').at(-1),path:specifier.path,
    sha:blob(data),size:data.length,content:data.toString('base64').replace(/.{72}/g,'$&\n'),
    encoding:'base64',...overrides};
  return {expectedUrl,obj};
}
function injected(specifier,data,overrides={}) {
  const r=response(specifier,data,overrides);
  return async (url,request)=>({
    status:200,url:r.expectedUrl,redirected:false,
    headers:{get:()=>null},text:async()=>JSON.stringify(r.obj)
  });
}
const refused=(p,code)=>assert.rejects(p,e=>e instanceof CustodyError&&e.code===code);
test('committed synthetic golden is canonical, bounded, and accepted by actual merged R2-B1',async()=>{
  const data=await fixture();
  assert.equal(H(data),BUNDLE);
  assert.equal(data.toString('utf8'),canonicalJSON(JSON.parse(data.toString('utf8'))));
  const replay=await verifyPortableJournal(data,{repository:REPO,parent_issue:PARENT,
    source_sha:SOURCE,bundle_sha256:BUNDLE,tip_sha256:TIP});
  assert.equal(replay.event_count,12);
  assert.deepEqual(replay.session_ids,['S1','S2']);
  assert.equal(replay.events[4].kind,'DEVIATION');
  assert.equal(replay.events[8].kind,'TASK_EVIDENCE_RECOVERY_START');
  assert.equal(replay.events[10].content.visibility,'REDACTED');
  assert.equal(replay.events[10].content.text,null);
  assert.equal(replay.authorization_granted,false);
});
test('the actual R2-B1 replay runs on precisely provider-decoded Git blob bytes',async()=>{
  const data=await fixture(), s=spec();
  const v=await read(s,{fetchImpl:injected(s,data)});
  assert.equal(v.status,'INJECTED_UNVERIFIED');
  assert.equal(v.real_r2b1_replayed,true);
  assert.equal(v.provider_bytes_observed,false);
  assert.equal(v.git_blob_sha1,blob(data));
  assert.equal(v.bundle_sha256,BUNDLE);
  assert.equal(v.tip.sha256,TIP);
  assert.deepEqual(v.session_ids,['S1','S2']);
  assert.equal(v.event_count,12);
  assert.equal(v.authorization_granted,false);
  assert.equal(v.externally_anchored,false);
  assert.equal(v.owner_message_authenticated,false);
  assert.equal(v.independently_accepted,false);
  assert.equal(v.live_writer_enabled,false);
  assert.equal(Object.hasOwn(v,'events'),false); // Never return potentially private PUBLIC bodies.
});
test('committed source locator binds a full immutable commit, never a branch name',async()=>{
  const data=await fixture(),v=await read(spec(),{fetchImpl:injected(spec(),data)});
  assert.equal(v.github_source_url,
    'https://github.com/'+REPO+'/blob/'+SOURCE+'/'+PATH);
  await refused(read({...spec(),commit_sha:'main'},{fetchImpl:injected(spec(),data)}),'INVALID');
  await refused(read({...spec(),commit_sha:'a'.repeat(39)},{fetchImpl:injected(spec(),data)}),'INVALID');
});
test('cross-repository and malformed issue-parent relationship denied before fetching',async()=>{
  const data=await fixture();
  await refused(read({...spec(),parent_issue:'attacker/Common#787'},
    {fetchImpl:injected(spec(),data)}),'INVALID');
  await refused(read({...spec(),parent_issue:REPO+'#0'},
    {fetchImpl:injected(spec(),data)}),'INVALID');
  await refused(read({...spec(),repository:'attacker/Common'},
    {fetchImpl:injected(spec(),data)}),'INVALID');
});
test('path traversal, percent-encoded path, query and newlines denied',async()=>{
  const data=await fixture();
  for(const path of ['../session.json','safe/../file.json','safe/%2e%2e/file.json',
    'safe/a.json?ref=main','safe//file.json','safe\\file.json','safe\nX']){
    await refused(read({...spec(),path},{fetchImpl:injected(spec(),data)}),'INVALID');
  }
});
test('untrusted caller authority, title, or accepted flag is refused',async()=>{
  const data=await fixture();
  await refused(read({...spec(),accepted:true},{fetchImpl:injected(spec(),data)}),'INVALID');
  await refused(read({...spec(),human_owner_grant:true},{fetchImpl:injected(spec(),data)}),'INVALID');
  await refused(read(spec(),{fetchImpl:injected(spec(),data),writeToken:'abc'}),'INVALID');
});
test('native payload must bind exact path and Git blob SHA1 independently',async()=>{
  const data=await fixture(),s=spec();
  await refused(read(s,{fetchImpl:injected(s,data,{path:'evil/other.json'})}),'REFUTED');
  await refused(read(s,{fetchImpl:injected(s,data,{sha:'a'.repeat(40)})}),'REFUTED');
  await refused(read(s,{fetchImpl:injected(s,data,{name:'different.json'})}),'REFUTED');
  await refused(read(s,{fetchImpl:injected(s,data,{size:data.length+2})}),'REFUTED');
});
test('a maliciously rewritten payload with recalculated blob SHA still needs trusted expected SHA256',async()=>{
  const data=await fixture(),s=spec();
  const changed=Buffer.from(data.toString().replace(
    'SYNTHETIC agent 1: write read-only source preflight',
    'SYNTHETIC agent 1: forge independent approval'));
  await refused(read(s,{fetchImpl:injected(s,changed)}),'REFUTED');
});
test('bundle expected tip/source SHA are verified by the actual B1 consumer',async()=>{
  const data=await fixture(),s=spec();
  await refused(read({...s,tip_sha256:'a'.repeat(64)},
    {fetchImpl:injected(s,data)}),'REFUTED');
  await refused(read({...s,source_sha:'a'.repeat(40)},
    {fetchImpl:injected(s,data)}),'REFUTED');
  await refused(read({...s,bundle_sha256:'b'.repeat(64)},
    {fetchImpl:injected(s,data)}),'REFUTED');
});
test('changed privacy policy cannot be laundered by a matching blob SHA and new caller digest',async()=>{
  const data=await fixture(),s=spec(),obj=JSON.parse(data);
  obj.privacy_policy.approved_public=[];
  obj.manifest.policy_sha256=H(canonicalJSON(obj.privacy_policy));
  const altered=Buffer.from(canonicalJSON(obj));
  await refused(read({...s,bundle_sha256:H(altered)},
    {fetchImpl:injected(s,altered)}),'REFUTED');
});
test('provider 302 and rate-limit/404/unavailable never become source success',async()=>{
  const data=await fixture(),s=spec();
  for(const status of [302,404,429,500]){
    await refused(read(s,{fetchImpl:async url=>({status,url,redirected:status===302,
      headers:{get:()=>null},text:async()=>''})}),'UNKNOWN');
  }
  await refused(read(s,{fetchImpl:async()=>{throw Error('unavailable')}}),'UNKNOWN');
});
test('redirected or invented native URL is UNKNOWN, not a native proof',async()=>{
  const s=spec(),data=await fixture(),good=response(s,data);
  for(const props of [{url:'https://evil.invalid/content',redirected:false},
    {url:good.expectedUrl,redirected:true}]){
    await refused(read(s,{fetchImpl:async()=>({
      status:200,headers:{get:()=>null},text:async()=>JSON.stringify(good.obj),...props
    })}),'UNKNOWN');
  }
});
test('invalid provider base64 and encoding fail closed',async()=>{
  const s=spec(),data=await fixture();
  await refused(read(s,{fetchImpl:injected(s,data,{content:'@@@@'})}),'REFUTED');
  await refused(read(s,{fetchImpl:injected(s,data,{encoding:'utf-8'})}),'REFUTED');
  await refused(read(s,{fetchImpl:injected(s,data,{content:''})}),'REFUTED');
});
test('oversized provider object and oversized HTTP response refused',async()=>{
  const s=spec(),data=await fixture();
  await refused(read(s,{fetchImpl:injected(s,data,{size:4194305})}),'REFUTED');
  await refused(read(s,{fetchImpl:async url=>({status:200,url,
    redirected:false,headers:{get:()=>String(6500000)},text:async()=>''})}),'UNKNOWN');
});
test('injected transport status can NEVER claim provider observed, even if URL/body perfect',async()=>{
  const s=spec(),data=await fixture();
  const r=await read(s,{fetchImpl:injected(s,data)});
  assert.equal(r.status,'INJECTED_UNVERIFIED');
  assert.equal(r.provider_bytes_observed,false);
});
test('real native GitHub GET uses exact immutable PR-head commit and cold replays committed bytes',
  {skip:!process.env.RELAY_B2A_CI_HEAD_SHA},async()=>{
  const ref=process.env.RELAY_B2A_CI_HEAD_SHA;
  assert.match(ref,/^[a-f0-9]{40}$/);
  const s=spec(ref);
  const receipt=await read(s,{readToken:process.env.RELAY_B2A_TOKEN||undefined});
  assert.equal(receipt.status,'GITHUB_COMMITTED_BYTES_OBSERVED');
  assert.equal(receipt.provider_bytes_observed,true);
  assert.equal(receipt.real_r2b1_replayed,true);
  assert.equal(receipt.commit_sha,ref);
  assert.equal(receipt.event_count,12);
  assert.equal(receipt.tip.sha256,TIP);
  assert.equal(receipt.authorization_granted,false);
  assert.equal(receipt.independently_accepted,false);
  console.log('NATIVE_COMMITTED_READBACK '+JSON.stringify({
    status:receipt.status,commit_sha:ref,git_blob_sha1:receipt.git_blob_sha1,
    bundle_sha256:receipt.bundle_sha256,tip_sha256:receipt.tip.sha256,
    events:receipt.event_count,authority:false}));
});
