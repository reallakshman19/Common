import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile,readdir,unlink,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {initJournal,appendJournal,readJournal,JournalError,__appendWithDirectoryBarrierForTest} from './session-journal-v1.mjs';

const SHA='49ff9e03366470cb6282ff6697b5034e610a703c';
const zero='0'.repeat(64),H=message=>createHash('sha256').update(message,'utf8').digest('hex');
const src=()=>({kind:'CHAT',status:'UNKNOWN',locator:null,sha256:null});
const claimed=()=>({kind:'GITHUB_COMMENT',status:'CLAIMED',
 locator:'https://github.com/reallaksh19/Common/issues/812',sha256:null});
const actor={session_id:'S1',responsibility_id:'R2-A',agent_id:'CHATGPT-6',base_sha:SHA};
let next=0;
function record(kind,text,opts={}){
 const n=++next;
 return {
  event_id:'EV-'+n,...actor,kind,
  recorded_at:new Date(Date.UTC(2026,9,8,17,0,n)).toISOString().replace('.000Z','Z'),
  source:src(),
  content:{visibility:'PUBLIC',text,sha256:H(text)},
  changed_files:[],commit_sha:null,evidence_id:null,prior_evidence_id:null,
  ...opts
 };
}
const create=async()=>{const folder=await mkdtemp(join(tmpdir(),'relay-r2a-'));await initJournal(folder);return folder;};
const rejected=async(promise,code)=>assert.rejects(promise,e=>e instanceof JournalError&&e.code===code);
const append=async(folder,event,tip)=>(await appendJournal(folder,event,tip)).tip;
test('actual disk journal preserves verbatim prompt, agent reply, code and evidence across restart',async()=>{
 const dir=await create();let tip={seq:0,sha256:zero};
 const items=[
  record('OWNER_PROMPT','ok next; preserve my original instructions'),
  record('AGENT_RESPONSE','I will create a bounded session recorder.'),
  record('TASK_EVIDENCE_START','START evidence', {evidence_id:'E-START',source:claimed()}),
  record('CODE_CHANGE','Changed the local journal',{changed_files:['skills/engineering-relay-v1/session-journal-v1.mjs']}),
  record('DEVIATION','Agent suggested extra permissions; not adopted'),
  record('TASK_EVIDENCE_END','END claimed, not provider accepted',{
   evidence_id:'E-END',prior_evidence_id:'E-START',
   commit_sha:SHA,changed_files:['skills/engineering-relay-v1/session-journal-v1.mjs']
  })
 ];
 for(const e of items)tip=await append(dir,e,tip);
 const fresh=await readJournal(dir);
 assert.equal(fresh.tip.seq,6);
 assert.equal(fresh.tip.sha256,tip.sha256);
 assert.equal(fresh.events[0].content.text,'ok next; preserve my original instructions');
 assert.equal(fresh.events[1].content.text,'I will create a bounded session recorder.');
 assert.equal(fresh.events[4].kind,'DEVIATION');
 assert.equal(fresh.events[5].commit_sha,SHA);
 assert.equal(fresh.events[2].source.status,'CLAIMED');
 assert.equal(fresh.provider_authenticated,false);
 assert.equal(fresh.authorization_granted,false);
});
test('redacted input never writes the private content to journal files',async()=>{
 const dir=await create();const secret='PRIVATE INSTRUCTION super-secret test value';
 const e=record('OWNER_PROMPT','not persisted');
 e.content={visibility:'REDACTED',text:null,sha256:H(secret)};
 e.source=src();
 await append(dir,e,{seq:0,sha256:zero});
 const saved=await readFile(join(dir,'0000000001.json'),'utf8');
 assert.equal(saved.includes(secret),false);
 assert.equal(saved.includes('not persisted'),false);
 const replay=await readJournal(dir);
 assert.equal(replay.events[0].content.text,null);
 assert.equal(replay.events[0].content.sha256,H(secret));
 assert.equal(replay.events[0].source.status,'UNKNOWN');
});
test('two concurrent writers racing on one sequence accept precisely one append',async()=>{
 const dir=await create();const expected={seq:0,sha256:zero};
 const events=[record('OWNER_PROMPT','writer one'),record('OWNER_PROMPT','writer two')];
 const results=await Promise.allSettled(events.map(e=>appendJournal(dir,e,expected)));
 assert.equal(results.filter(x=>x.status==='fulfilled').length,1);
 const lost=results.find(x=>x.status==='rejected');
 assert.ok(lost.reason instanceof JournalError);
 assert.equal(lost.reason.code,'STALE_TIP');
 const state=await readJournal(dir);
 assert.equal(state.events.length,1);
 assert.ok(['writer one','writer two'].includes(state.events[0].content.text));
});
test('stale head after process restart cannot append',async()=>{
 const dir=await create();const tip=await append(dir,record('OWNER_PROMPT','one'),{seq:0,sha256:zero});
 await rejected(appendJournal(dir,record('AGENT_RESPONSE','two'),{seq:0,sha256:zero}),'STALE_TIP');
 const nextTip=await append(dir,record('AGENT_RESPONSE','two'),tip);
 assert.equal(nextTip.seq,2);
});
test('flipping one stored content byte never replays green',async()=>{
 const dir=await create();await append(dir,record('OWNER_PROMPT','unchanged'),{seq:0,sha256:zero});
 const file=join(dir,'0000000001.json');const raw=await readFile(file,'utf8');
 await writeFile(file,raw.replace('unchanged','tampered'),'utf8');
 await rejected(readJournal(dir),'CORRUPT');
});
test('removing first entry after two appends is a sequence gap',async()=>{
 const dir=await create();const tip=await append(dir,record('OWNER_PROMPT','one'),{seq:0,sha256:zero});
 await append(dir,record('AGENT_RESPONSE','two'),tip);
 await unlink(join(dir,'0000000001.json'));
 await rejected(readJournal(dir),'CORRUPT');
});
test('unfinished staging debris is surfaced but never accepted as evidence',async()=>{
 const dir=await create(),name='.pending-00000000-0000-4000-8000-000000000000';
 await writeFile(join(dir,name),'crashed writer private candidate');
 const a=await readJournal(dir);
 assert.equal(a.tip.seq,0);
 assert.deepEqual(a.uncommitted_temp_files,[name]);
 assert.equal(a.events.length,0);
});
test('duplicate event IDs fail closed',async()=>{
 const dir=await create(),e=record('OWNER_PROMPT','same identity');
 const tip=await append(dir,e,{seq:0,sha256:zero});
 const repeated={...record('AGENT_RESPONSE','later'),event_id:e.event_id};
 await rejected(appendJournal(dir,repeated,tip),'CORRUPT');
});
test('evidence END without its same-session START is refused',async()=>{
 const dir=await create();
 const e=record('TASK_EVIDENCE_END','fake END',{
  evidence_id:'E-END',prior_evidence_id:'E-START',
  commit_sha:SHA,changed_files:['skills/engineering-relay-v1/session-journal-v1.mjs']
 });
 await rejected(appendJournal(dir,e,{seq:0,sha256:zero}),'CORRUPT');
});
test('evidence START / RECOVERY and END must join same source session',async()=>{
 const dir=await create();
 const e=record('TASK_EVIDENCE_START','START',{evidence_id:'E-START'});
 const tip=await append(dir,e,{seq:0,sha256:zero});
 const wrong=record('TASK_EVIDENCE_END','END',{
  session_id:'S2',evidence_id:'E-END',prior_evidence_id:'E-START',commit_sha:SHA,
  changed_files:['skills/engineering-relay-v1/session-journal-v1.mjs']
 });
 await rejected(appendJournal(dir,wrong,tip),'CORRUPT');
 const recovered=record('TASK_EVIDENCE_RECOVERY_START','RECOVERY',{evidence_id:'E-REC',prior_evidence_id:'E-START'});
 const state=await appendJournal(dir,recovered,tip);
 assert.equal(state.events[1].kind,'TASK_EVIDENCE_RECOVERY_START');
});
test('duplicate START and duplicate evidence ID fail closed',async()=>{
 const dir=await create();const tip=await append(dir,record('TASK_EVIDENCE_START','START',{evidence_id:'E-S'}),{seq:0,sha256:zero});
 await rejected(appendJournal(dir,record('TASK_EVIDENCE_START','START2',{evidence_id:'E-S2'}),tip),'CORRUPT');
 await rejected(appendJournal(dir,record('TASK_EVIDENCE_RECOVERY_START','RECOVERY',{evidence_id:'E-S',prior_evidence_id:'E-S'}),tip),'CORRUPT');
});
test('out-of-order clock and actor drift are rejected',async()=>{
 const dir=await create();const e=record('OWNER_PROMPT','begin');
 const tip=await append(dir,e,{seq:0,sha256:zero});
 const prior=record('AGENT_RESPONSE','prior',{recorded_at:'2026-10-08T16:00:01Z'});
 await rejected(appendJournal(dir,prior,tip),'CORRUPT');
 const actorDrift=record('AGENT_RESPONSE','not same actor',{agent_id:'CLAUDE'});
 await rejected(appendJournal(dir,actorDrift,tip),'CORRUPT');
});
test('unsafe source file path, forged hash, missing commit and unknown accepted flag are invalid',async()=>{
 const dir=await create();const tip={seq:0,sha256:zero};
 const evil=record('CODE_CHANGE','Changed',{changed_files:['../passwords']});
 await rejected(appendJournal(dir,evil,tip),'INVALID');
 const forged=record('OWNER_PROMPT','exact');forged.content.sha256='0'.repeat(64);
 await rejected(appendJournal(dir,forged,tip),'INVALID');
 const end=record('TASK_EVIDENCE_END','claimed END',{evidence_id:'E-E',prior_evidence_id:'E-S',
 changed_files:['src/file.mjs']});
 await rejected(appendJournal(dir,end,tip),'INVALID');
 const unauthorized=record('OWNER_PROMPT','I approve', {accepted:true});
 await rejected(appendJournal(dir,unauthorized,tip),'INVALID');
});
test('accessor source input is refused without invoking getter',async()=>{
 const dir=await create();let accessed=false;const e=record('OWNER_PROMPT','no secrets');
 Object.defineProperty(e,'accepted',{enumerable:true,get(){accessed=true;return true;}});
 await rejected(appendJournal(dir,e,{seq:0,sha256:zero}),'INVALID');
 assert.equal(accessed,false);
});
test('source status VERIFIED and forged claimed locator are refused',async()=>{
 const dir=await create(),e=record('OWNER_PROMPT','claim');
 e.source.status='VERIFIED';await rejected(appendJournal(dir,e,{seq:0,sha256:zero}),'INVALID');
 const fake=record('OWNER_PROMPT','unknown');fake.source.locator='https://evil.invalid';
 await rejected(appendJournal(dir,fake,{seq:0,sha256:zero}),'INVALID');
});
test('public content byte size bound is enforced, not stored',async()=>{
 const dir=await create();const big='X'.repeat(8193);
 const e=record('OWNER_PROMPT',big);
 await rejected(appendJournal(dir,e,{seq:0,sha256:zero}),'INVALID');
 const files=await readdir(dir);
 assert.deepEqual(files,[]);
});
test('unexpected non-journal entry refuses replay',async()=>{
 const dir=await create();await writeFile(join(dir,'unexpected.json'),'{}');
 await rejected(readJournal(dir),'CORRUPT');
});
test('symlink root is rejected',async()=>{
 const dir=await create(),parent=await mkdtemp(join(tmpdir(),'relay-link-')),alias=join(parent,'link');
 await symlink(dir,alias,process.platform==='win32'?'junction':'dir');
 await rejected(readJournal(alias),'INVALID');
});


test('post-link directory fsync failure is a typed committed-but-durability-unknown result, not rollback',async()=>{
 const dir=await create(),old={seq:0,sha256:zero};
 const event=record('OWNER_PROMPT','SYNTHETIC commit with directory fsync failure');
 await rejected(__appendWithDirectoryBarrierForTest(dir,event,old,async()=>{
  const e=new Error('SYNTHETIC EPERM after link');e.code='EPERM';throw e;
 }),'POST_COMMIT_DURABILITY_UNKNOWN');
 const replay=await readJournal(dir);
 assert.equal(replay.tip.seq,1);
 assert.equal(replay.events[0].event_id,event.event_id);
 assert.equal(replay.events[0].content.text,event.content.text);
 await rejected(appendJournal(dir,event,old),'STALE_TIP');
 const recovered=await appendJournal(dir,record('AGENT_RESPONSE','continued after reconciled tip'),replay.tip);
 assert.equal(recovered.tip.seq,2);
 assert.equal(recovered.events.length,2);
});
test('successful append explicitly labels platform durability and never grants acceptance',async()=>{
 const dir=await create();
 const out=await appendJournal(dir,record('OWNER_PROMPT','SYNTHETIC file sync scope'),{seq:0,sha256:zero});
 assert.equal(out.durability_state,process.platform==='win32'?
  'FILE_SYNCED_DIRECTORY_PERSISTENCE_UNCONFIRMED':'FILE_AND_DIRECTORY_SYNCED');
 assert.equal(out.authorization_granted,false);
 assert.equal(out.independently_accepted,false);
});
