import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {projectCommittedGithubLineage as project} from './github-journal-lineage-v1.mjs';

const REPO='reallaksh19/Common',PARENT=REPO+'#787';
const SOURCE='28841b5cfed9e9b6057a1a6f09090adcc512e1b8';
const PATH='skills/engineering-relay-v1/fixtures/b2a-synthetic-journal-v1.json';
const BUNDLE='79c2bc0b84f23a862e3ce7cef300c1b2dd1c4b90d00a448a8f1a269d1ddb0e9d';
const TIP='3077376e2d5fe849de1450d9f2cc8e6d350742dc0d98969a36e778000d052660';
const hash=x=>createHash('sha256').update(x).digest('hex');
const blob=x=>createHash('sha1').update('blob '+x.length+'\0').update(x).digest('hex');
const fixture=()=>readFile(new URL('./fixtures/b2a-synthetic-journal-v1.json',import.meta.url));
const spec=(sha=SOURCE)=>({repository:REPO,parent_issue:PARENT,commit_sha:sha,path:PATH,
  source_sha:SOURCE,bundle_sha256:BUNDLE,tip_sha256:TIP});
const original=()=>({kind:'CHAT',status:'UNKNOWN',locator:null});
const seed=()=>({
  schema:'relay-provenance-v1',parent_issue:PARENT,
  owner_intents:[{id:'OI-1',
    raw_text:'SYNTHETIC OWNER REQUEST: verify immutable GitHub content; not a real chat',
    original_source:original(),first_durable_mirror:'https://github.com/reallaksh19/Common/issues/787'}],
  claims:[{id:'AC3',intent_ids:['OI-1'],criterion:'SYNTHETIC intent to module evidence trace'}],
  responsibilities:[{id:'R2-B2A',claim_ids:['AC3'],depends_on:[],
    scope:'Synthetic native custody and trace',write_surface:['skills/engineering-relay-v1/github-journal-lineage-v1.mjs']}],
  sessions:[],task_evidence:[],research_findings:[],owner_decisions:[]
});
const bindings=()=>[{event_id:'EV-1',intent_id:'OI-1'}];
function apiUrl(s){return 'https://api.github.com/repos/'+s.repository+'/contents/'+s.path+'?ref='+s.commit_sha;}
function provider(s,data,changes={}) {
  return {type:'file',name:s.path.split('/').at(-1),path:s.path,encoding:'base64',
    content:data.toString('base64'),size:data.length,sha:blob(data),...changes};
}
function transport(s,data,{payload=null,responseUrl=null,status=200}={}){
  const state={reads:0,tokens:[]};
  state.fetchImpl=async (url,req)=>{
    state.reads++;state.tokens.push(req.headers?.Authorization??null);
    return {url:responseUrl??apiUrl(s),status,redirected:false,
      headers:{get:()=>null},text:async()=>JSON.stringify(payload??provider(s,data))};
  };
  return state;
}
test('exact same native-source byte stream reaches actual B1 disk replay and G1 R1 graph',async()=>{
  const data=await fixture(),s=spec(),t=transport(s,data);
  const r=await project(s,seed(),bindings(),{fetchImpl:t.fetchImpl});
  assert.equal(t.reads,1,'one native GitHub GET, no second fetch');
  assert.equal(r.status,'INJECTED_UNVERIFIED_STRUCTURAL_LINEAGE');
  assert.equal(r.custody.status,'INJECTED_UNVERIFIED');
  assert.equal(r.custody.real_r2b1_replayed,true);
  assert.equal(r.custody.bundle_sha256,BUNDLE);
  assert.equal(r.lineage.journal_tip.sha256,TIP);
  assert.equal(r.lineage.document.sessions.length,2);
  assert.deepEqual(r.lineage.document.sessions.map(x=>x.agent_id),['CODEX','CLAUDE']);
  assert.equal(r.lineage.evidence_links.length,5);
  assert.equal(r.lineage.deviations.length,1);
  assert.equal(r.lineage.deviations[0].disposition,'UNADOPTED_PRODUCER_ASSERTION');
  assert.equal(r.lineage.claim_traces[0].session_ids.length,2);
  assert.equal(r.lineage.evidence_traces.find(x=>x.evidence_id==='E-E1').owner_intents[0].original_source.status,'UNKNOWN');
  const module1=r.lineage.module_traces.find(x=>x.module_path==='fixtures/relay-synthetic-one.mjs');
  const module2=r.lineage.module_traces.find(x=>x.module_path==='fixtures/relay-synthetic-two.mjs');
  assert.deepEqual(module1.session_ids,['S1']);
  assert.deepEqual(module2.session_ids,['S2']);
  assert.ok(r.source_lineage_sha256.match(/^[a-f0-9]{64}$/));
  assert.equal(Object.hasOwn(r.custody,'events'),false);
  assert.equal(r.owner_message_authenticated,false);
  assert.equal(r.authorization_granted,false);
  assert.equal(r.independently_accepted,false);
  assert.equal(r.externally_anchored,false);
  assert.equal(r.live_writer_enabled,false);
  assert.equal(r.lineage.document.sessions[1].events.find(e=>e.kind==='ERROR').summary.startsWith('REDACTED_SHA256:'),true);
  assert.equal(JSON.stringify(r).includes('SYNTHETIC REDACTED MARKER, NOT A REAL SECRET'),false);
});
test('deterministic combined source+lineage digest for the exact same verified data',async()=>{
  const s=spec(),b=await fixture();
  const a=await project(s,seed(),bindings(),{fetchImpl:transport(s,b).fetchImpl});
  const c=await project(s,seed(),bindings(),{fetchImpl:transport(s,b).fetchImpl});
  assert.equal(a.source_lineage_sha256,c.source_lineage_sha256);
});
test('different byte stream with a valid new Git SHA still cannot replace pinned bundle',async()=>{
  const s=spec(),data=await fixture();
  const forged=Buffer.from(data.toString('utf8').replace('SYNTHETIC agent 1','SYNTHETIC FAKE agent 1'));
  await assert.rejects(project(s,seed(),bindings(),{fetchImpl:transport(s,forged).fetchImpl}),
    e=>e.code==='REFUTED');
});
test('wrong external bundle tip, source SHA or committed object identity refused',async()=>{
  const s=spec(),data=await fixture();
  for(const change of [
    {tip_sha256:'0'.repeat(64)}, {source_sha:'1'.repeat(40)},
    {bundle_sha256:'a'.repeat(64)}, {parent_issue:'attacker/Common#787'},
    {commit_sha:'main'}, {path:'../../secrets'}])
    await assert.rejects(project({...s,...change},seed(),bindings(),
      {fetchImpl:transport({...s,...change},data).fetchImpl}));
});
test('Owner prompt wrong content is refused despite genuine matching Git blob and journal',async()=>{
  const s=spec(),data=await fixture(),wrong=seed();
  wrong.owner_intents[0].raw_text='SYNTHETIC a different Owner statement';
  await assert.rejects(project(s,wrong,bindings(),{fetchImpl:transport(s,data).fetchImpl}),
    e=>e.code==='OWNER_SOURCE_MISMATCH');
});
test('Owner claim ancestry cannot be fabricated by a same-text unrelated intent',async()=>{
  const s=spec(),data=await fixture(),graph=seed();
  graph.owner_intents.push({id:'OI-OTHER',raw_text:graph.owner_intents[0].raw_text,
    original_source:original(),first_durable_mirror:null});
  await assert.rejects(project(s,graph,[{event_id:'EV-1',intent_id:'OI-OTHER'}],
    {fetchImpl:transport(s,data).fetchImpl}),e=>e.code==='PROMPT_CLAIM_MISMATCH');
});
test('foreign but structurally valid R1 graph cannot be laundered into GitHub custody parent',async()=>{
  const s=spec(),data=await fixture(),graph=seed();
  graph.parent_issue='reallaksh19/Common#1';
  await assert.rejects(project(s,graph,bindings(),{fetchImpl:transport(s,data).fetchImpl}),
    e=>e.code==='SOURCE_LINEAGE_MISMATCH');
});
test('fake original GitHub source cannot promote a claimed synthetic CHAT source',async()=>{
  const s=spec(),data=await fixture(),graph=seed();
  graph.owner_intents[0].original_source={kind:'GITHUB_ISSUE',status:'CLAIMED',
    locator:'https://github.com/reallaksh19/Common/issues/787'};
  await assert.rejects(project(s,graph,bindings(),{fetchImpl:transport(s,data).fetchImpl}),
    e=>e.code==='OWNER_SOURCE_MISMATCH');
});
test('preexisting producer-owned session or fake accepted evidence in seed is refused',async()=>{
  const s=spec(),data=await fixture(),graph=seed();
  graph.sessions.push({id:'FORGED',responsibility_id:'R2-B2A',agent_id:'ROGUE',
    base_sha:SOURCE,changed_files:[],events:[{kind:'AGENT_RESPONSE',
      source:original(),summary:'synthetic fabricated session'}]});
  await assert.rejects(project(s,graph,bindings(),{fetchImpl:transport(s,data).fetchImpl}),
    e=>e.code==='SEED_CONFLICT');
});
test('the missing explicit Owner binding cannot infer human Owner from native GitHub blob',async()=>{
  const s=spec(),data=await fixture();
  await assert.rejects(project(s,seed(),[],{fetchImpl:transport(s,data).fetchImpl}),
    e=>e.code==='UNBOUND_OWNER_PROMPT');
});
test('forged GitHub API origin and body object SHA rejected before source-to-lineage join',async()=>{
  const s=spec(),data=await fixture();
  const wrong=provider(s,data,{sha:'a'.repeat(40)});
  await assert.rejects(project(s,seed(),bindings(),{fetchImpl:transport(s,data,{payload:wrong}).fetchImpl}),
    e=>e.code==='REFUTED');
  await assert.rejects(project(s,seed(),bindings(),{fetchImpl:transport(s,data,{responseUrl:'https://evil.invalid/contents'}).fetchImpl}),
    e=>e.code==='UNKNOWN');
});
test('a native read-only caller never acquires a GitHub writer or accepted evidence',async()=>{
  const s=spec(),data=await fixture(),r=await project(s,seed(),bindings(),{fetchImpl:transport(s,data).fetchImpl});
  for(const obj of [r,r.custody,r.lineage]){
    assert.equal(obj.authorization_granted,false);
    assert.equal(obj.live_writer_enabled,false);
    assert.equal(obj.independently_accepted,false);
  }
  assert.equal(r.lineage.evidence_links.every(e=>e.accepted===false),true);
});
test('native exact-head GitHub readback drives R1 lineage via one GET and real B1',
  {skip:!process.env.RELAY_G2C_CI_HEAD_SHA},async()=>{
  const sha=process.env.RELAY_G2C_CI_HEAD_SHA;
  assert.match(sha,/^[a-f0-9]{40}$/);
  const r=await project(spec(sha),seed(),bindings(),
    {readToken:process.env.RELAY_G2C_TOKEN||undefined});
  assert.equal(r.status,'GITHUB_BYTES_TO_STRUCTURAL_LINEAGE');
  assert.equal(r.custody.provider_bytes_observed,true);
  assert.equal(r.custody.real_r2b1_replayed,true);
  assert.equal(r.custody.commit_sha,sha);
  assert.equal(r.lineage.document.sessions.length,2);
  assert.equal(r.lineage.evidence_links.length,5);
  assert.equal(r.lineage.journal_tip.sha256,TIP);
  assert.equal(r.authorization_granted,false);
  console.log('NATIVE_GITHUB_R1_LINEAGE '+JSON.stringify({
    status:r.status,commit_sha:sha,blob_sha1:r.custody.git_blob_sha1,
    bundle_sha256:r.custody.bundle_sha256,tip_sha256:r.lineage.journal_tip.sha256,
    projection_sha256:r.lineage.projection_sha256,joined_sha256:r.source_lineage_sha256,
    sessions:r.lineage.document.sessions.length,authority:false}));
});
