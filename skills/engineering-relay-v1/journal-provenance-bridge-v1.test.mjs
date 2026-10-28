import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {initJournal,appendJournal} from './session-journal-v1.mjs';
import {exportPortableJournal} from './session-bundle-v1.mjs';
import {validate,traceClaim,traceEvidence,traceModule} from './provenance-v1.mjs';
import {projectLocalJournal,projectPortableJournal,JournalLineageError} from './journal-provenance-bridge-v1.mjs';

const SHA='28841b5cfed9e9b6057a1a6f09090adcc512e1b8';
const PARENT='reallaksh19/Common#787';
const ZERO='0'.repeat(64),hash=s=>createHash('sha256').update(s).digest('hex');
const source=()=>({kind:'CHAT',status:'UNKNOWN',locator:null,sha256:null});
const seedSource=()=>({kind:'CHAT',status:'UNKNOWN',locator:null});
const bindings=()=>[{event_id:'EV-1',intent_id:'OI-1'}];
const seed=()=>({
  schema:'relay-provenance-v1',parent_issue:PARENT,
  owner_intents:[{id:'OI-1',raw_text:'Build one traceable lifecycle',
    original_source:seedSource(),
    first_durable_mirror:'https://github.com/reallaksh19/Common/issues/787'}],
  claims:[{id:'AC3',intent_ids:['OI-1'],criterion:'Both agent sessions trace to Owner intent'}],
  responsibilities:[
    {id:'R1',claim_ids:['AC3'],depends_on:[],scope:'Source bridge',
      write_surface:['src/alpha.mjs']},
    {id:'R2',claim_ids:['AC3'],depends_on:['R1'],scope:'Review bridge',
      write_surface:['src/beta.mjs']}],
  sessions:[],task_evidence:[],research_findings:[],owner_decisions:[]
});
let n=0;
function record(kind,text,{session_id='S1',responsibility_id='R1',agent_id='CODEX',
  visibility='PUBLIC',changed_files=[],commit_sha=null,evidence_id=null,
  prior_evidence_id=null,...other}={}) {
  const k=++n;
  return {event_id:'EV-'+k,session_id,responsibility_id,agent_id,base_sha:SHA,
    kind,recorded_at:new Date(Date.UTC(2026,9,8,17,0,k)).toISOString().replace('.000Z','Z'),
    source:source(),content:{visibility,text:visibility==='PUBLIC'?text:null,sha256:hash(text)},
    changed_files,commit_sha,evidence_id,prior_evidence_id,...other};
}
function records(){
  n=0;
  return [
    record('OWNER_PROMPT','Build one traceable lifecycle'),
    record('AGENT_RESPONSE','Agent one works on bridge'),
    record('TASK_EVIDENCE_START','claimed start',{evidence_id:'E-S1'}),
    record('CODE_CHANGE','alpha module change',{changed_files:['src/alpha.mjs']}),
    record('DEVIATION','Suggested unauthorized merge, rejected'),
    record('TASK_EVIDENCE_END','claimed end',{evidence_id:'E-E1',
      prior_evidence_id:'E-S1',changed_files:['src/alpha.mjs'],commit_sha:SHA}),
    record('AGENT_RESPONSE','Agent two independently reviews',{session_id:'S2',
      responsibility_id:'R2',agent_id:'CLAUDE'}),
    record('TASK_EVIDENCE_START','start two',{session_id:'S2',
      responsibility_id:'R2',agent_id:'CLAUDE',evidence_id:'E-S2'}),
    record('TASK_EVIDENCE_RECOVERY_START','recovered from crash',{session_id:'S2',
      responsibility_id:'R2',agent_id:'CLAUDE',evidence_id:'E-R2',prior_evidence_id:'E-S2'}),
    record('CODE_CHANGE','beta module change',{session_id:'S2',
      responsibility_id:'R2',agent_id:'CLAUDE',changed_files:['src/beta.mjs']}),
    record('ERROR','PRIVATE SECRET DO NOT EXPORT',{session_id:'S2',
      responsibility_id:'R2',agent_id:'CLAUDE',visibility:'REDACTED'}),
    record('TASK_EVIDENCE_END','end two',{session_id:'S2',
      responsibility_id:'R2',agent_id:'CLAUDE',evidence_id:'E-E2',
      prior_evidence_id:'E-S2',changed_files:['src/beta.mjs'],commit_sha:SHA})
  ];
}
async function fixture(mut=()=>{}) {
  const items=records();mut(items);
  const dir=await mkdtemp(join(tmpdir(),'relay-r1r2-real-'));
  let tip=(await initJournal(dir)).tip;
  for(const e of items) tip=(await appendJournal(dir,e,tip)).tip;
  return {dir,items,tip};
}
function approvals(items) {
  return {schema:'relay-export-policy-v1',revision:'PRIVACY-V1',
    approved_public:items.filter(e=>e.content.visibility==='PUBLIC').map(e=>({
      event_id:e.event_id,content_sha256:e.content.sha256}))};
}
async function exportBundle(f) {
  return exportPortableJournal(f.dir,{
    repository:'reallaksh19/Common',parent_issue:PARENT,source_sha:SHA,
    exported_at:'2026-10-08T18:00:00Z'},approvals(f.items));
}
function expected(b) {
  return {repository:'reallaksh19/Common',parent_issue:PARENT,source_sha:SHA,
    bundle_sha256:b.sha256,tip_sha256:b.manifest.tip.sha256};
}
const bridgeRefused=(p,code)=>assert.rejects(p,e=>e instanceof JournalLineageError&&e.code===code);

test('real two-agent R2-A replay projects into actual R1 validate/forward/reverse APIs',async()=>{
  const f=await fixture(),r=await projectLocalJournal(f.dir,seed(),bindings());
  assert.equal(validate(r.document).valid,true);
  assert.equal(r.document.sessions.length,2);
  assert.deepEqual(r.document.sessions.map(s=>s.agent_id),['CODEX','CLAUDE']);
  assert.equal(r.document.task_evidence.length,5);
  assert.equal(r.journal_tip.sha256,f.tip.sha256);
  assert.equal(r.deviations.length,1);
  assert.equal(r.deviations[0].disposition,'UNADOPTED_PRODUCER_ASSERTION');
  assert.equal(r.document.sessions[0].events.some(e=>e.summary.includes('unauthorized merge')),false);
  assert.equal(r.document.sessions[1].events.find(e=>e.kind==='ERROR').summary,
    'REDACTED_SHA256:'+hash('PRIVATE SECRET DO NOT EXPORT'));
  assert.equal(JSON.stringify(r).includes('PRIVATE SECRET DO NOT EXPORT'),false);
  assert.deepEqual(traceClaim(r.document,'AC3').session_ids,['S1','S2']);
  assert.deepEqual(traceModule(r.document,'src/alpha.mjs').session_ids,['S1']);
  assert.deepEqual(traceModule(r.document,'src/beta.mjs').session_ids,['S2']);
  const e=traceEvidence(r.document,'E-E2');
  assert.deepEqual(e.claim_ids,['AC3']);
  assert.equal(e.owner_intents[0].raw_text,'Build one traceable lifecycle');
  assert.equal(e.owner_intents[0].original_source.status,'UNKNOWN');
  assert.equal(r.evidence_links.find(x=>x.evidence_id==='E-R2').prior_evidence_id,'E-S2');
  assert.equal(r.authorization_granted,false);
  assert.equal(r.independently_accepted,false);
  assert.equal(r.externally_anchored,false);
  assert.equal(r.live_writer_enabled,false);
});

test('actual R2-B1 privacy bundle cold replay yields identical R1 projection digest',async()=>{
  const f=await fixture(),b=await exportBundle(f);
  const local=await projectLocalJournal(f.dir,seed(),bindings());
  const cold=await projectPortableJournal(b.bytes,expected(b),seed(),bindings());
  assert.equal(cold.custody,'PORTABLE_UNANCHORED');
  assert.equal(cold.projection_sha256,local.projection_sha256);
  assert.deepEqual(cold.module_traces,local.module_traces);
  assert.deepEqual(cold.evidence_links,local.evidence_links);
  assert.equal(b.bytes.includes('PRIVATE SECRET DO NOT EXPORT'),false);
  assert.equal(cold.owner_message_authenticated,false);
  assert.equal(cold.provider_authenticated,false);
});

test('forged Owner text or swapped original source is refused, not silently joined',async()=>{
  const f=await fixture();
  const a=seed();a.owner_intents[0].raw_text='a different owner instruction';
  await bridgeRefused(projectLocalJournal(f.dir,a,bindings()),'OWNER_SOURCE_MISMATCH');
  const b=seed();b.owner_intents[0].original_source={kind:'GITHUB_ISSUE',
    status:'CLAIMED',locator:'https://github.com/reallaksh19/Common/issues/787'};
  await bridgeRefused(projectLocalJournal(f.dir,b,bindings()),'OWNER_SOURCE_MISMATCH');
});
test('same-text Owner prompt cannot bind an unrelated claim ancestry',async()=>{
  const f=await fixture(),s=seed();
  s.owner_intents.push({id:'OI-OTHER',raw_text:'Build one traceable lifecycle',
    original_source:seedSource(),first_durable_mirror:null});
  await bridgeRefused(projectLocalJournal(f.dir,s,
    [{event_id:'EV-1',intent_id:'OI-OTHER'}]),'PROMPT_CLAIM_MISMATCH');
});
test('a prompt needs one explicit binding to an existing seed OwnerIntent',async()=>{
  const f=await fixture();
  await bridgeRefused(projectLocalJournal(f.dir,seed(),[]),'UNBOUND_OWNER_PROMPT');
  await bridgeRefused(projectLocalJournal(f.dir,seed(),[{event_id:'EV-1',intent_id:'OI-X'}]),'UNKNOWN_OWNER_INTENT');
  await bridgeRefused(projectLocalJournal(f.dir,seed(),[{event_id:'EV-999',intent_id:'OI-1'}]),'UNBOUND_OWNER_PROMPT');
});
test('unused or duplicate Owner bindings cannot be treated as an authoritative join',async()=>{
  const f=await fixture();
  await bridgeRefused(projectLocalJournal(f.dir,seed(),[...bindings(),
    {event_id:'EV-999',intent_id:'OI-1'}]),'FOREIGN_BINDING');
  await bridgeRefused(projectLocalJournal(f.dir,seed(),[...bindings(),...bindings()]),'INVALID_INPUT');
});
test('cannot invent code ownership from END-only paths in a real R2 journal',async()=>{
  const f=await fixture(items=>{items[5].changed_files=['src/unrecorded.mjs'];});
  await bridgeRefused(projectLocalJournal(f.dir,seed(),bindings()),'END_PATH_UNPROVEN');
});
test('R1 structural seed cannot inject producer-owned session/evidence rows',async()=>{
  const f=await fixture();
  const s=seed();s.sessions=[{id:'S2',responsibility_id:'R2',
    agent_id:'FAKE',base_sha:SHA,changed_files:[],
    events:[{kind:'AGENT_RESPONSE',source:seedSource(),summary:'forged'}]}];
  await bridgeRefused(projectLocalJournal(f.dir,s,bindings()),'SEED_CONFLICT');
});
test('R1 global ID namespace collisions fail closed rather than shadow Owner claims',async()=>{
  const f=await fixture();
  const s=seed();s.claims[0].id='S1';
  s.responsibilities[0].claim_ids=['S1'];s.responsibilities[1].claim_ids=['S1'];
  await assert.rejects(projectLocalJournal(f.dir,s,bindings()),
    e=>e.name==='ProvenanceError'&&e.message.includes('duplicate global ID S1'));
});
test('redacted Owner prompt is not fabricated into R1 raw_text',async()=>{
  const f=await fixture(items=>{items[0].content={visibility:'REDACTED',
    text:null,sha256:hash('Build one traceable lifecycle')};});
  await bridgeRefused(projectLocalJournal(f.dir,seed(),bindings()),'REDACTED_OWNER_PROMPT');
});
test('evidence-only journal session cannot become synthetic R1 conversation',async()=>{
  n=0;const dir=await mkdtemp(join(tmpdir(),'relay-orphan-session-'));
  let tip=(await initJournal(dir)).tip;
  const e=record('TASK_EVIDENCE_START','start only',{evidence_id:'E-S3'});
  await appendJournal(dir,e,tip);
  await bridgeRefused(projectLocalJournal(dir,seed(),[]),'UNREPRESENTABLE_SESSION');
});
test('unknown responsibility from actual journal is rejected',async()=>{
  const f=await fixture();
  const s=seed();s.responsibilities=s.responsibilities.slice(0,1);
  await bridgeRefused(projectLocalJournal(f.dir,s,bindings()),'RESPONSIBILITY_MISMATCH');
});
test('changed portable bundle or mismatched expected source fails in actual R2-B1',async()=>{
  const f=await fixture(),b=await exportBundle(f);
  const modified=b.bytes.replace('Build one traceable lifecycle','Impostor');
  await assert.rejects(projectPortableJournal(modified,expected(b),seed(),bindings()));
  await assert.rejects(projectPortableJournal(b.bytes,{...expected(b),source_sha:'a'.repeat(40)},seed(),bindings()));
});
test('actual R2-A detects tampering before the bridge reads any graph',async()=>{
  const f=await fixture(),path=join(f.dir,'0000000001.json');
  const raw=await readFile(path,'utf8');
  await writeFile(path,raw.replace('Build one traceable lifecycle','rogue owner rewrite'));
  await assert.rejects(projectLocalJournal(f.dir,seed(),bindings()),e=>e.code==='CORRUPT');
});
test('uncommitted crash debris blocks lineage projection',async()=>{
  const f=await fixture();
  await writeFile(join(f.dir,'.pending-00000000-0000-4000-8000-000000000000'),'crash residue');
  await bridgeRefused(projectLocalJournal(f.dir,seed(),bindings()),'UNRESOLVED');
});
test('forged acceptance and authority fields are rejected by merged producers',async()=>{
  await assert.rejects(fixture(items=>{items[0].accepted=true;}),e=>e.code==='INVALID');
});
