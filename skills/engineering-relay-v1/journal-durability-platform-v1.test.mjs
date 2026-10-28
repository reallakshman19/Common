import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {initJournal,appendJournal,readJournal,JournalError,
  __appendWithDirectoryBarrierForTest} from './session-journal-v1.mjs';

const ZERO='0'.repeat(64),BASE='a'.repeat(40);
const event=(n)=>({
 event_id:'EV-'+n,session_id:'S1',responsibility_id:'R2-A',agent_id:'SYNTHETIC',
 base_sha:BASE,kind:n===1?'OWNER_PROMPT':'AGENT_RESPONSE',
 recorded_at:'2026-10-09T00:00:0'+n+'Z',
 source:{kind:'CHAT',status:'UNKNOWN',locator:null,sha256:null},
 content:{visibility:'PUBLIC',text:'SYNTHETIC EVENT '+n,
  sha256:createHash('sha256').update('SYNTHETIC EVENT '+n).digest('hex')},
 changed_files:[],commit_sha:null,evidence_id:null,prior_evidence_id:null
});
const make=async()=>{const dir=await mkdtemp(join(tmpdir(),'relay-win-durability-'));await initJournal(dir);return dir;};
test('post-link directory EPERM must not produce false rollback or permit duplicate retry',async()=>{
 const dir=await make(),old={seq:0,sha256:ZERO};
 await assert.rejects(
  __appendWithDirectoryBarrierForTest(dir,event(1),old,async()=>{
   const e=new Error('simulated EPERM after hardlink');e.code='EPERM';throw e;
  }),
  e=>e instanceof JournalError&&e.code==='POST_COMMIT_DURABILITY_UNKNOWN');
 const r=await readJournal(dir);
 assert.equal(r.tip.seq,1);
 await assert.rejects(appendJournal(dir,event(1),old),
  e=>e instanceof JournalError&&e.code==='STALE_TIP');
 const next=await appendJournal(dir,event(2),r.tip);
 assert.equal(next.tip.seq,2);
 assert.equal(next.authorization_granted,false);
});
test('platform sync contract never pretends Windows directory power-loss durability',async()=>{
 const dir=await make();
 const state=await appendJournal(dir,event(1),{seq:0,sha256:ZERO});
 const expected=process.platform==='win32'?
  'FILE_SYNCED_DIRECTORY_PERSISTENCE_UNCONFIRMED':'FILE_AND_DIRECTORY_SYNCED';
 assert.equal(state.durability_state,expected);
 assert.equal(state.tip.seq,1);
 assert.deepEqual(state.uncommitted_temp_files,[]);
 assert.equal(state.independently_accepted,false);
});
