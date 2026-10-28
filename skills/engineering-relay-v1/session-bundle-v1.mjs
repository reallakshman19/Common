/* R2-B1: portable privacy-gated local journal bundle, NO NETWORK OR AUTHORITY.
 * Export uses the real merged R2-A readJournal and R1 canonicalJSON.
 * Import reconstitutes actual R2-A entry files and replays them; this bundle
 * is NOT externally authenticated without an independently pinned digest/tip.
 */
import * as fs from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {readJournal} from './session-journal-v1.mjs';

export class BundleError extends Error {
  constructor(code,message){super(code+': '+message);this.name='BundleError';this.code=code;}
}
const SHA=/^[a-f0-9]{40}$/;
const HASH=/^[a-f0-9]{64}$/;
const REPO=/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const PARENT=/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+#[1-9][0-9]*$/;
const ID=/^[A-Z][A-Z0-9._:-]{0,63}$/;
const MAX_BYTES=4*1024*1024,MAX_EVENTS=256,MAX_PUBLIC=256;
const ZERO='0'.repeat(64);
function fail(code,message){throw new BundleError(code,message);}
function hash(v){return createHash('sha256').update(v,'utf8').digest('hex');}
function safeCanonical(v){
  try{return canonicalJSON(v);}catch(e){fail('INVALID','unsafe non-canonical input: '+e.message);}
}
function only(value,keys,name){
  if(!value||typeof value!=='object'||Array.isArray(value))fail('INVALID',name+' expected object');
  const own=Object.keys(value);
  if(keys.some(k=>!Object.hasOwn(value,k))||own.some(k=>!keys.includes(k)))
    fail('INVALID',name+' unexpected/missing keys');
}
function utc(v,name){
  if(typeof v!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(v)
    ||!Number.isFinite(Date.parse(v))||new Date(Date.parse(v)).toISOString().replace('.000Z','Z')!==v)
    fail('INVALID',name+' must be strict UTC seconds');
}
function context(c){
  only(c,['repository','parent_issue','source_sha','exported_at'],'context');
  if(typeof c.repository!=='string'||!REPO.test(c.repository)
    ||typeof c.parent_issue!=='string'||!PARENT.test(c.parent_issue)
    ||c.parent_issue.split('#')[0].toLowerCase()!==c.repository.toLowerCase()
    ||typeof c.source_sha!=='string'||!SHA.test(c.source_sha))
    fail('INVALID','invalid repository/parent/source SHA');
  utc(c.exported_at,'exported_at');
}
function policy(p){
  only(p,['schema','revision','approved_public'],'privacy_policy');
  if(p.schema!=='relay-export-policy-v1'||typeof p.revision!=='string'
    ||!ID.test(p.revision))fail('INVALID','unrecognized privacy policy');
  if(!Array.isArray(p.approved_public)||p.approved_public.length>MAX_PUBLIC)
    fail('INVALID','privacy list too large');
  const map=new Map();
  for(const item of p.approved_public){
    only(item,['event_id','content_sha256'],'privacy approval');
    if(typeof item.event_id!=='string'||!ID.test(item.event_id)
      ||typeof item.content_sha256!=='string'||!HASH.test(item.content_sha256)
      ||map.has(item.event_id))fail('INVALID','invalid/duplicate privacy approval');
    map.set(item.event_id,item.content_sha256);
  }
  return map;
}
function enforcePrivacy(events,p){
  const approvals=policy(p),seen=new Set();
  for(const e of events){
    if(e.content.visibility==='PUBLIC'){
      const approved=approvals.get(e.event_id);
      if(approved!==e.content.sha256)
        fail('PRIVACY_DENIED','unapproved PUBLIC event ID or exact content digest');
      seen.add(e.event_id);
    }else if(e.content.visibility!=='REDACTED'||e.content.text!==null)
      fail('PRIVACY_DENIED','unknown visibility or redacted text leaked');
  }
  if(seen.size!==approvals.size)fail('PRIVACY_DENIED','unused/foreign public consent');
}
function encodeEntries(events){
  let prev=ZERO;
  return events.map((record,i)=>{
    const withoutDigest={schema:'relay-session-entry-v1',seq:i+1,prev_sha256:prev,record};
    const sha256=hash(safeCanonical(withoutDigest));
    prev=sha256;
    return {...withoutDigest,sha256};
  });
}
async function safelyReadJournal(folder){
  try{return await readJournal(folder);}
  catch(e){
    fail(e.code==='INVALID'||e.code==='MISSING_JOURNAL'?'INVALID':'CORRUPT',
      'R2-A source journal failed replay: '+e.message);
  }
}
function checkedBytes(bufferOrText){
  if(!(typeof bufferOrText==='string'||Buffer.isBuffer(bufferOrText)))
    fail('INVALID','bundle must be canonical JSON text or Buffer');
  const size=Buffer.byteLength(bufferOrText,'utf8');
  if(size>MAX_BYTES)fail('LIMIT','bundle exceeds maximum size');
  const raw=Buffer.isBuffer(bufferOrText)?bufferOrText.toString('utf8'):bufferOrText;
  if(Buffer.isBuffer(bufferOrText)&&!Buffer.from(raw,'utf8').equals(bufferOrText))
    fail('INVALID','invalid UTF-8 bundle');
  return raw;
}
function expose(tip,events,manifest,bundleSha){
  return Object.freeze({
    schema:'relay-portable-check-v1',
    repository:manifest.repository,parent_issue:manifest.parent_issue,
    source_sha:manifest.source_sha,
    event_count:events.length,session_ids:Object.freeze(manifest.session_ids.slice()),
    tip:Object.freeze({...tip}),
    policy_sha256:manifest.policy_sha256,
    bundle_sha256:bundleSha,
    events:Object.freeze(events),
    original_chat_source:'UNKNOWN',
    owner_message_authenticated:false,
    source_attribution:'PRODUCER_ASSERTED_UNVERIFIED',
    externally_anchored:false,
    authorization_granted:false,
    independently_accepted:false,
    live_writer_enabled:false
  });
}
/** Byte-stable payload for a SPECIFIC, caller-provided export UTC second. */
export async function exportPortableJournal(folder,rawContext,rawPolicy){
  const c=JSON.parse(safeCanonical(rawContext));
  const p=JSON.parse(safeCanonical(rawPolicy));
  context(c);
  policy(p);
  const state=await safelyReadJournal(folder);
  if(state.uncommitted_temp_files.length)
    fail('UNRESOLVED','journal has uncommitted crash/staging debris');
  if(state.tip.seq<1)fail('EMPTY','do not export an evidence-free journal');
  if(state.tip.seq>MAX_EVENTS)fail('LIMIT','bundle event count exceeds bounded export');
  enforcePrivacy(state.events,p);
  const entries=encodeEntries(state.events);
  if(entries.at(-1).sha256!==state.tip.sha256)
    fail('CORRUPT','rebuilt R2-A chain differs from recorded tip');
  const sessions=[...new Set(state.events.map(x=>x.session_id))].sort();
  const manifest={
    schema:'relay-portable-manifest-v1',
    repository:c.repository,parent_issue:c.parent_issue,
    source_sha:c.source_sha,exported_at:c.exported_at,
    event_count:entries.length,session_ids:sessions,
    tip:{...state.tip},
    public_count:state.events.filter(x=>x.content.visibility==='PUBLIC').length,
    redacted_count:state.events.filter(x=>x.content.visibility==='REDACTED').length,
    policy_revision:p.revision,
    policy_sha256:hash(safeCanonical(p)),
    authority_status:'PRODUCER_ASSERTED_NOT_AUTHENTICATED'
  };
  const value={schema:'relay-portable-bundle-v1',manifest,privacy_policy:p,entries};
  const bytes=safeCanonical(value);
  if(Buffer.byteLength(bytes,'utf8')>MAX_BYTES)fail('LIMIT','encoded bundle too large');
  // Detect normal concurrent appends before delivering a stable export view.
  const reread=await safelyReadJournal(folder);
  if(reread.tip.seq!==state.tip.seq||reread.tip.sha256!==state.tip.sha256||
    reread.uncommitted_temp_files.length)fail('STALE_TIP','journal changed during export');
  return Object.freeze({bytes,sha256:hash(bytes),manifest:Object.freeze(manifest),
    authorization_granted:false,externally_anchored:false,live_writer_enabled:false});
}
/** Cold verification uses the actual merged R2-A file replay on fresh private disk. */
export async function verifyPortableJournal(bundleBytes,rawExpected){
  const bytes=checkedBytes(bundleBytes);
  let parsed;
  try{parsed=JSON.parse(bytes);}catch{fail('INVALID','bundle is not valid JSON');}
  if(safeCanonical(parsed)!==bytes)fail('INVALID','bundle is not byte-canonical JSON');
  const expected=JSON.parse(safeCanonical(rawExpected));
  only(expected,['repository','parent_issue','source_sha','bundle_sha256','tip_sha256'],'expected');
  if(typeof expected.repository!=='string'||!REPO.test(expected.repository)
    ||typeof expected.parent_issue!=='string'||!PARENT.test(expected.parent_issue)
    ||expected.parent_issue.split('#')[0].toLowerCase()!==expected.repository.toLowerCase()
    ||typeof expected.source_sha!=='string'||!SHA.test(expected.source_sha)
    ||typeof expected.bundle_sha256!=='string'||!HASH.test(expected.bundle_sha256)
    ||typeof expected.tip_sha256!=='string'||!HASH.test(expected.tip_sha256))
    fail('INVALID','bad expected identity/checksums');
  const bundleSha=hash(bytes);
  if(bundleSha!==expected.bundle_sha256)fail('REFUTED','external expected bundle digest mismatch');
  only(parsed,['schema','manifest','privacy_policy','entries'],'bundle');
  if(parsed.schema!=='relay-portable-bundle-v1')fail('REFUTED','unsupported bundle schema');
  const m=parsed.manifest;
  only(m,['schema','repository','parent_issue','source_sha','exported_at',
    'event_count','session_ids','tip','public_count','redacted_count',
    'policy_revision','policy_sha256','authority_status'],'manifest');
  if(m.schema!=='relay-portable-manifest-v1'
    ||m.authority_status!=='PRODUCER_ASSERTED_NOT_AUTHENTICATED')
    fail('REFUTED','unsupported schema or claimed authentication');
  context({repository:m.repository,parent_issue:m.parent_issue,
    source_sha:m.source_sha,exported_at:m.exported_at});
  if(m.repository.toLowerCase()!==expected.repository.toLowerCase()
    ||m.parent_issue!==expected.parent_issue
    ||m.source_sha!==expected.source_sha)fail('REFUTED','foreign repository/parent/source');
  const p=parsed.privacy_policy;
  policy(p);
  if(m.policy_revision!==p.revision||m.policy_sha256!==hash(safeCanonical(p)))
    fail('REFUTED','privacy policy revision/digest mismatch');
  only(m.tip,['seq','sha256'],'tip');
  if(!Array.isArray(parsed.entries)||parsed.entries.length<1||parsed.entries.length>MAX_EVENTS
    ||m.event_count!==parsed.entries.length||m.tip.seq!==parsed.entries.length
    ||!HASH.test(m.tip.sha256)||m.tip.sha256!==expected.tip_sha256)
    fail('REFUTED','event count, boundary or anchored tip mismatch');
  if(!Array.isArray(m.session_ids)||m.session_ids.length>MAX_EVENTS
    ||!m.session_ids.every(x=>typeof x==='string'&&ID.test(x))
    ||new Set(m.session_ids).size!==m.session_ids.length)
    fail('REFUTED','invalid listed sessions');
  if(!Number.isInteger(m.public_count)||!Number.isInteger(m.redacted_count)
    ||m.public_count<0||m.redacted_count<0
    ||m.public_count+m.redacted_count!==m.event_count)fail('REFUTED','invalid exposure counts');
  const scratch=await fs.mkdtemp(join(tmpdir(),'relay-bundle-replay-'));
  try{
    for(let i=0;i<parsed.entries.length;i++){
      // The journal itself checks strict schema, hashes, link order, event IDs,
      // sources, session actor, START/END and changed files on cold replay.
      const filename=String(i+1).padStart(10,'0')+'.json';
      const recordBytes=safeCanonical(parsed.entries[i])+'\n';
      if(Buffer.byteLength(recordBytes,'utf8')>49152)
        fail('LIMIT','journal entry byte bound');
      await fs.writeFile(join(scratch,filename),recordBytes,{flag:'wx',mode:0o600});
    }
    let replay;
    try{replay=await readJournal(scratch);}
    catch(e){fail('CORRUPT','R2-A cold replay refused bundle: '+e.message);}
    if(replay.tip.seq!==m.tip.seq||replay.tip.sha256!==m.tip.sha256)
      fail('REFUTED','replayed tip differs from declared manifest');
    enforcePrivacy(replay.events,p);
    const sessions=[...new Set(replay.events.map(x=>x.session_id))].sort();
    if(safeCanonical(sessions)!==safeCanonical(m.session_ids)
      ||replay.events.filter(x=>x.content.visibility==='PUBLIC').length!==m.public_count
      ||replay.events.filter(x=>x.content.visibility==='REDACTED').length!==m.redacted_count)
      fail('REFUTED','session IDs or privacy counts changed');
    return expose(replay.tip,replay.events,m,bundleSha);
  }finally{
    await fs.rm(scratch,{recursive:true,force:true});
  }
}
