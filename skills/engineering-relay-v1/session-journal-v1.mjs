/* RELAY RESET R2-A: LOCAL append-only source-ASSERTION journal.
 * Disk bytes and a SHA256 chain detect accidental/unauthorized edits at replay,
 * not hostile writers who can rewrite the entire local directory.
 * Never an Owner authorization, accepted evidence, GitHub writer or auto-capture.
 */
import * as fs from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';

const ZERO='0'.repeat(64),HASH=/^[a-f0-9]{64}$/,SHA=/^[a-f0-9]{40}$/;
const ID=/^[A-Z][A-Z0-9._:-]{0,63}$/;
const DATE=/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;
const FILE=/^\d{10}\.json$/;
const STAGE=/^\.pending-[0-9a-f-]{36}$/;
const KINDS=new Set(['OWNER_PROMPT','AGENT_RESPONSE','CODE_CHANGE','DECISION','DEVIATION','ERROR','RECOVERY',
  'TASK_EVIDENCE_START','TASK_EVIDENCE_END','TASK_EVIDENCE_RECOVERY_START']);
const EVIDENCE=new Set(['TASK_EVIDENCE_START','TASK_EVIDENCE_END','TASK_EVIDENCE_RECOVERY_START']);
const MAX_ENTRIES=10000,MAX_BYTES=24576,MAX_TEXT=8192,MAX_FILES=128;
export class JournalError extends Error {
 constructor(code,why){super(code+': '+why);this.name='JournalError';this.code=code;}
}
function reject(code,why){throw new JournalError(code,why);}
function obj(v,fields,label){
 if(!v||typeof v!=='object'||Array.isArray(v))reject('INVALID',label+' expected object');
 if(Object.keys(v).some(k=>!fields.includes(k))||fields.some(k=>!Object.hasOwn(v,k)))
   reject('INVALID',label+' shape incorrect');
}
function id(v,name){if(typeof v!=='string'||!ID.test(v))reject('INVALID',name+' invalid ID');}
function text(v,name){if(typeof v!=='string'||!v.trim())reject('INVALID',name+' blank text');}
function time(v){
 if(typeof v!=='string'||!DATE.test(v)||!Number.isFinite(Date.parse(v))||
   new Date(Date.parse(v)).toISOString().replace('.000Z','Z')!==v)reject('INVALID','bad UTC timestamp');
 return Date.parse(v);
}
function path(v){
 text(v,'changed file');
 if(v.length>512||v.startsWith('/')||v.includes('\\')||v.includes('\0')||
    v.split('/').some(x=>!x||x==='..'||x==='.'))reject('INVALID','unsafe changed file path');
}
function snapshot(input){
 let serialized;
 try{serialized=canonicalJSON(input)}catch(e){reject('INVALID','not safe bounded JSON: '+e.message);}
 if(Buffer.byteLength(serialized,'utf8')>MAX_BYTES)reject('INVALID','event exceeds byte budget');
 return JSON.parse(serialized);
}
function validateRecord(e){
 obj(e,['event_id','session_id','responsibility_id','agent_id','base_sha','kind',
   'recorded_at','source','content','changed_files','commit_sha','evidence_id','prior_evidence_id'],'event');
 for(const name of ['event_id','session_id','responsibility_id'])id(e[name],name);
 text(e.agent_id,'agent_id');
 if(!SHA.test(e.base_sha))reject('INVALID','invalid base_sha');
 if(!KINDS.has(e.kind))reject('INVALID','unsupported event kind');
 time(e.recorded_at);
 obj(e.source,['kind','status','locator','sha256'],'source');
 if(!['CHAT','GITHUB_COMMENT','GITHUB_ISSUE','GIT_BLOB','FILE','OTHER'].includes(e.source.kind)||
    !['UNKNOWN','CLAIMED'].includes(e.source.status))reject('INVALID','source is never pre-verified');
 if(e.source.status==='UNKNOWN'){
   if(e.source.locator!==null||e.source.sha256!==null)reject('INVALID','unknown source cannot claim locator/digest');
 }else{
   text(e.source.locator,'source locator');
   if(e.source.locator.length>1024||!(e.source.sha256===null||HASH.test(e.source.sha256)))
     reject('INVALID','source claim invalid');
 }
 obj(e.content,['visibility','text','sha256'],'content');
 if(!['PUBLIC','REDACTED'].includes(e.content.visibility)||!HASH.test(e.content.sha256))
   reject('INVALID','invalid content visibility/hash');
 if(e.content.visibility==='PUBLIC'){
   text(e.content.text,'public content');
   if(Buffer.byteLength(e.content.text,'utf8')>MAX_TEXT)reject('INVALID','public text oversized');
   if(hash(e.content.text)!==e.content.sha256)reject('INVALID','public text digest mismatch');
 }else if(e.content.text!==null)reject('INVALID','redacted content may not store bytes');
 if(!Array.isArray(e.changed_files)||e.changed_files.length>MAX_FILES||
   new Set(e.changed_files).size!==e.changed_files.length)reject('INVALID','duplicate/oversized changed paths');
 e.changed_files.forEach(path);
 if(e.commit_sha!==null&&!SHA.test(e.commit_sha))reject('INVALID','invalid exact commit SHA');
 if(EVIDENCE.has(e.kind)){
   id(e.evidence_id,'evidence_id');
   if(e.kind==='TASK_EVIDENCE_START'){
     if(e.prior_evidence_id!==null)reject('INVALID','START cannot point to earlier evidence');
   }else {
     id(e.prior_evidence_id,'prior_evidence_id');
     if(e.kind==='TASK_EVIDENCE_END'&&e.commit_sha===null)reject('INVALID','END needs exact commit SHA');
   }
 }else if(e.evidence_id!==null||e.prior_evidence_id!==null)
   reject('INVALID','non-evidence event cannot assert evidence identity');
 if(e.kind==='CODE_CHANGE'&&e.changed_files.length===0)reject('INVALID','CODE_CHANGE requires changed files');
 if(e.kind==='TASK_EVIDENCE_END'&&e.changed_files.length===0)
   reject('INVALID','END needs explicitly changed paths');
 if(e.changed_files.length&&e.kind!=='CODE_CHANGE'&&e.kind!=='TASK_EVIDENCE_END')
   reject('INVALID','changed files only from code-change or END');
}
function hash(v){return createHash('sha256').update(v,'utf8').digest('hex');}
function filename(n){return String(n).padStart(10,'0')+'.json';}
async function rootDir(folder,create=false){
 if(typeof folder!=='string'||!folder.trim())reject('INVALID','journal directory missing');
 const abs=resolve(folder);
 if(create)await fs.mkdir(abs,{recursive:true});
 let stat;
 try{stat=await fs.lstat(abs)}catch(e){if(e.code==='ENOENT')reject('MISSING_JOURNAL','journal directory absent');throw e;}
 if(stat.isSymbolicLink()||!stat.isDirectory())reject('INVALID','journal root must be an actual directory');
 return abs;
}
function checkChainState(events){
 const eventIds=new Set(),evidenceIds=new Set(),sessions=new Map(),starts=new Map();
 let latest=0;
 for(const e of events){
   if(eventIds.has(e.event_id))reject('CORRUPT','duplicate event ID');
   eventIds.add(e.event_id);
   const t=time(e.recorded_at);
   if(t<latest)reject('CORRUPT','out-of-order timestamps');latest=t;
   if(sessions.has(e.session_id)){
     const old=sessions.get(e.session_id);
     if(old.agent_id!==e.agent_id||old.responsibility_id!==e.responsibility_id||old.base_sha!==e.base_sha)
       reject('CORRUPT','session actor/responsibility/base changed');
   }else sessions.set(e.session_id,{agent_id:e.agent_id,responsibility_id:e.responsibility_id,base_sha:e.base_sha});
   if(EVIDENCE.has(e.kind)){
     if(evidenceIds.has(e.evidence_id))reject('CORRUPT','duplicate evidence ID');
     evidenceIds.add(e.evidence_id);
     const key=e.session_id;
     if(e.kind==='TASK_EVIDENCE_START'){
       if(starts.has(key))reject('CORRUPT','duplicate evidence START for session');
       starts.set(key,{id:e.evidence_id,ended:false});
     }else{
       const s=starts.get(key);
       if(!s||s.ended||s.id!==e.prior_evidence_id)
         reject('CORRUPT','END/RECOVERY has no matching current START');
       if(e.kind==='TASK_EVIDENCE_END')s.ended=true;
     }
   }
 }
}
export async function readJournal(folder){
 const root=await rootDir(folder);
 const names=await fs.readdir(root);
 const stage=names.filter(x=>STAGE.test(x)).sort();
 const journalFiles=names.filter(x=>FILE.test(x)).sort();
 const unexpected=names.filter(x=>!STAGE.test(x)&&!FILE.test(x));
 if(unexpected.length)reject('CORRUPT','unexpected file in journal directory');
 if(journalFiles.length>MAX_ENTRIES)reject('CORRUPT','journal entry count exceeds limit');
 const events=[];let prev=ZERO;
 for(let i=0;i<journalFiles.length;i++){
   if(journalFiles[i]!==filename(i+1))reject('CORRUPT','sequence gap or unexpected journal name');
   const p=join(root,journalFiles[i]);
   const stat=await fs.lstat(p);
   if(!stat.isFile()||stat.isSymbolicLink()||stat.size>MAX_BYTES*2)
     reject('CORRUPT','journal entry is not a bounded regular file');
   const raw=await fs.readFile(p,'utf8');
   let entry;
   try{entry=JSON.parse(raw)}catch{reject('CORRUPT','unparseable journal entry');}
   try{obj(entry,['schema','seq','prev_sha256','record','sha256'],'entry');}
   catch{reject('CORRUPT','entry shape invalid');}
   if(entry.schema!=='relay-session-entry-v1'||entry.seq!==i+1||
      entry.prev_sha256!==prev||!HASH.test(entry.sha256))
     reject('CORRUPT','sequence/schema/parent hash mismatch');
   let encoded;
   try{encoded=canonicalJSON({schema:entry.schema,seq:entry.seq,prev_sha256:entry.prev_sha256,record:entry.record});}
   catch{reject('CORRUPT','invalid canonical record');}
   if(hash(encoded)!==entry.sha256)reject('CORRUPT','stored record hash mismatch');
   try{validateRecord(entry.record)}catch{reject('CORRUPT','invalid stored record');}
   events.push(entry.record);prev=entry.sha256;
 }
 checkChainState(events);
 return Object.freeze({tip:Object.freeze({seq:events.length,sha256:prev}),events:Object.freeze(events),
   uncommitted_temp_files:Object.freeze(stage),authorization_granted:false,
   provider_authenticated:false,independently_accepted:false,live_writer_enabled:false});
}
export async function initJournal(folder){
 await rootDir(folder,true);
 return readJournal(folder);
}
async function syncCommitDirectory(root){
  // On Windows/NTFS, Node directory fsync may be unsupported. The entry FILE
  // has already been synced, but directory-link crash durability is NOT proven.
  if(process.platform==='win32')return 'FILE_SYNCED_DIRECTORY_PERSISTENCE_UNCONFIRMED';
  const dir=await fs.open(root,'r');
  try{await dir.sync();}finally{await dir.close();}
  return 'FILE_AND_DIRECTORY_SYNCED';
}
async function appendWithBarrier(folder,input,expected,barrier){
  const root=await rootDir(folder);
  obj(expected,['seq','sha256'],'expected tip');
  if(!Number.isSafeInteger(expected.seq)||expected.seq<0||!HASH.test(expected.sha256))
    reject('INVALID','bad CAS expectation');
  const event=snapshot(input);
  validateRecord(event);
  const now=await readJournal(root);
  if(now.tip.seq!==expected.seq||now.tip.sha256!==expected.sha256)
    reject('STALE_TIP','journal changed; reload before append');
  if(now.tip.seq>=MAX_ENTRIES)reject('LIMIT','journal full');
  checkChainState([...now.events,event]);
  const seq=now.tip.seq+1;
  const body={schema:'relay-session-entry-v1',seq,prev_sha256:now.tip.sha256,record:event};
  const sha256=hash(canonicalJSON(body));
  const target=join(root,filename(seq)),temp=join(root,'.pending-'+randomUUID());
  const bytes=canonicalJSON({...body,sha256})+'\n';
  let staged=false,durability;
  try{
    const out=await fs.open(temp,'wx',0o600);
    staged=true;
    try{await out.writeFile(bytes,'utf8');await out.sync();}finally{await out.close();}
    try{await fs.link(temp,target);}catch(e){
      if(e.code==='EEXIST')reject('STALE_TIP','another writer committed expected sequence');
      throw e;
    }
    // A directory-sync error occurs AFTER the target link becomes visible:
    // throwing never means the append rolled back. Verify what was committed.
    try{durability=await barrier(root);}
    catch{
      let committed=false;
      try{
        const recovery=await readJournal(root);
        committed=recovery.tip.seq===seq&&recovery.tip.sha256===sha256;
      }catch{}
      reject(committed?'POST_COMMIT_DURABILITY_UNKNOWN':'POST_LINK_RECOVERY_REQUIRED',
        'post-link durability unconfirmed; re-read journal tip before retry');
    }
  }finally{if(staged)await fs.unlink(temp).catch(()=>{});}
  // Stage file removed before readback; successful callers never see phantom
  // pending debris in their returned immutable snapshot.
  const replay=await readJournal(root);
  if(replay.tip.seq!==seq||replay.tip.sha256!==sha256)
    reject('CORRUPT','append readback mismatch');
  return Object.freeze({...replay,durability_state:durability});
}
export async function appendJournal(folder,input,expected){
  return appendWithBarrier(folder,input,expected,syncCommitDirectory);
}
/** Fault boundary for source-level tests only; production appendJournal
 * always invokes the real OS-specific durability barrier.
 */
export async function __appendWithDirectoryBarrierForTest(folder,input,expected,barrier){
  if(typeof barrier!=='function')reject('INVALID','test barrier must be callable');
  return appendWithBarrier(folder,input,expected,barrier);
}
