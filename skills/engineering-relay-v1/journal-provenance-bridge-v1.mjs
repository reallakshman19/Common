/* RELAY RESET #822 — R2 journal -> R1 structural lineage, READ ONLY.
 * Real producer/consumer imports; no provider custody, human consent or authority.
 */
import {createHash} from 'node:crypto';
import {readJournal} from './session-journal-v1.mjs';
import {verifyPortableJournal} from './session-bundle-v1.mjs';
import {canonicalJSON,validate,traceClaim,traceEvidence,traceModule} from './provenance-v1.mjs';

export class JournalLineageError extends Error {
  constructor(code,message) { super(code+': '+message);this.name='JournalLineageError';this.code=code; }
}
const MAX_EVENTS=256;
const KINDS=new Set(['OWNER_PROMPT','AGENT_RESPONSE','DECISION','CODE_CHANGE','ERROR','RECOVERY']);
const EVIDENCE=Object.freeze({
  TASK_EVIDENCE_START:'START',
  TASK_EVIDENCE_END:'END',
  TASK_EVIDENCE_RECOVERY_START:'RECOVERY_START'
});
function reject(code,message) { throw new JournalLineageError(code,message); }
function cloneSafe(v,label) {
  try { return JSON.parse(canonicalJSON(v)); }
  catch(e) { reject('INVALID_INPUT',label+': '+e.message); }
}
function keys(v,expected,label) {
  if(!v||typeof v!=='object'||Array.isArray(v)
     ||Object.keys(v).some(k=>!expected.includes(k))
     ||expected.some(k=>!Object.hasOwn(v,k))) reject('INVALID_INPUT',label+' shape');
}
function source(e) {
  return {kind:e.source.kind,status:e.source.status,locator:e.source.locator,
    ...(e.source.sha256===null?{}:{digest:e.source.sha256})};
}
function summarize(e) {
  return e.content.visibility==='PUBLIC' ? e.content.text :
    'REDACTED_SHA256:'+e.content.sha256;
}
function sha256(v) { return createHash('sha256').update(v).digest('hex'); }

/** Takes only the results of genuine merged R2-A/R2-B1 readers; never raw caller events. */
function assemble(state,rawSeed,rawBindings,custody) {
  const seed=cloneSafe(rawSeed,'seed'),bindings=cloneSafe(rawBindings,'owner_prompt_bindings');
  validate(seed); // Actual merged R1 validator.
  if(seed.sessions.length||seed.task_evidence.length)
    reject('SEED_CONFLICT','structural seed must not contain producer-owned session/evidence rows');
  if(!Array.isArray(bindings)||bindings.length>MAX_EVENTS)
    reject('INVALID_INPUT','owner prompt bindings must be bounded array');
  if(!state||!Array.isArray(state.events)||state.events.length<1||state.events.length>MAX_EVENTS)
    reject('LIMIT','journal event count must be 1..256');
  if(state.uncommitted_temp_files?.length)
    reject('UNRESOLVED','journal contains crash/staging debris');

  const byPrompt=new Map();
  for(const b of bindings) {
    keys(b,['event_id','intent_id'],'owner_prompt_binding');
    if(typeof b.event_id!=='string'||typeof b.intent_id!=='string'||byPrompt.has(b.event_id))
      reject('INVALID_INPUT','duplicate/invalid Owner prompt binding');
    byPrompt.set(b.event_id,b.intent_id);
  }
  const doc={...seed,sessions:[],task_evidence:[]};
  const sessions=new Map(),seenPrompts=new Set();
  const eventLinks=[],deviations=[],evidenceLinks=[];
  for(const [i,e] of state.events.entries()) {
    if(!seed.responsibilities.some(x=>x.id===e.responsibility_id))
      reject('RESPONSIBILITY_MISMATCH','journal responsibility not present in seed: '+e.responsibility_id);
    let s=sessions.get(e.session_id);
    if(!s) {
      s={id:e.session_id,responsibility_id:e.responsibility_id,
        agent_id:e.agent_id,base_sha:e.base_sha,changed_files:[],events:[]};
      sessions.set(e.session_id,s);
      doc.sessions.push(s);
    } else if(s.responsibility_id!==e.responsibility_id
      ||s.agent_id!==e.agent_id||s.base_sha!==e.base_sha)
      reject('ACTOR_DRIFT','same session changed actor/owner/base');
    const link={event_id:e.event_id,session_id:e.session_id,kind:e.kind,
      journal_sequence:i+1,recorded_at:e.recorded_at,content_sha256:e.content.sha256,
      visibility:e.content.visibility,source_status:e.source.status,session_event_index:null};
    if(e.kind==='OWNER_PROMPT') {
      const intentId=byPrompt.get(e.event_id);
      if(!intentId)reject('UNBOUND_OWNER_PROMPT','Owner prompt must bind an explicit intent ID');
      const intent=seed.owner_intents.find(x=>x.id===intentId);
      if(!intent)reject('UNKNOWN_OWNER_INTENT','prompt binding has no seed OwnerIntent');
      // A same-text prompt from an unrelated intent must not be laundered into
      // the responsibility's Owner ancestry.
      const owning=seed.responsibilities.find(x=>x.id===e.responsibility_id);
      const allowable=new Set(seed.claims.filter(c=>owning.claim_ids.includes(c.id))
        .flatMap(c=>c.intent_ids));
      if(!allowable.has(intentId))
        reject('PROMPT_CLAIM_MISMATCH','bound OwnerIntent not among this responsibility claims');
      if(e.content.visibility!=='PUBLIC')
        reject('REDACTED_OWNER_PROMPT','R1 raw_text cannot honestly represent digest-only Owner prompt');
      if(intent.raw_text!==e.content.text || canonicalJSON(intent.original_source)!==canonicalJSON(source(e)))
        reject('OWNER_SOURCE_MISMATCH','Owner prompt differs from declared intent text/source');
      seenPrompts.add(e.event_id);
    }
    if(KINDS.has(e.kind)) {
      link.session_event_index=s.events.length;
      s.events.push({kind:e.kind,source:source(e),summary:summarize(e)});
      if(e.kind==='CODE_CHANGE') {
        for(const p of e.changed_files)if(!s.changed_files.includes(p))s.changed_files.push(p);
      }
    } else if(e.kind==='DEVIATION') {
      // R1 has no DEVIATION variant. Preserve it as a typed sidecar, NOT a fake decision.
      deviations.push({event_id:e.event_id,session_id:e.session_id,
        source:source(e),visibility:e.content.visibility,
        content_sha256:e.content.sha256,text:e.content.text,
        disposition:'UNADOPTED_PRODUCER_ASSERTION'});
    } else if(Object.hasOwn(EVIDENCE,e.kind)) {
      if(e.kind==='TASK_EVIDENCE_END' && e.changed_files.some(p=>!s.changed_files.includes(p)))
        reject('END_PATH_UNPROVEN','END changed file has no same-session CODE_CHANGE event');
      doc.task_evidence.push({id:e.evidence_id,kind:EVIDENCE[e.kind],
        responsibility_id:e.responsibility_id,session_id:e.session_id,
        source:source(e),commit_sha:e.commit_sha});
      evidenceLinks.push({evidence_id:e.evidence_id,event_id:e.event_id,
        prior_evidence_id:e.prior_evidence_id,session_id:e.session_id,
        changed_files:e.changed_files.slice(),source_status:e.source.status,
        accepted:false,provider_verified:false});
    } else reject('UNREPRESENTABLE_KIND','unexpected R2 event kind');
    eventLinks.push(link);
  }
  for(const id of byPrompt.keys())if(!seenPrompts.has(id))
    reject('FOREIGN_BINDING','unused Owner prompt binding: '+id);
  for(const s of doc.sessions)if(!s.events.length)
    reject('UNREPRESENTABLE_SESSION','R1 requires a real non-evidence session event: '+s.id);
  // R2 ensures evidence sequence; also prove the projection retained each prior edge.
  const evidenceIDs=new Set(doc.task_evidence.map(e=>e.id));
  for(const l of evidenceLinks)
    if(l.prior_evidence_id!==null && !evidenceIDs.has(l.prior_evidence_id))
      reject('DANGLING_EVIDENCE','lost journal prior evidence: '+l.prior_evidence_id);
  validate(doc); // Cross-schema, ID and responsibility checks from actual R1.
  const claimTraces=doc.claims.map(c=>traceClaim(doc,c.id));
  const evidenceTraces=doc.task_evidence.map(e=>traceEvidence(doc,e.id));
  const paths=[...new Set(doc.sessions.flatMap(s=>s.changed_files))].sort();
  const moduleTraces=paths.map(p=>traceModule(doc,p));
  const proof={document:doc,event_links:eventLinks,evidence_links:evidenceLinks,
    deviations,journal_tip:state.tip};
  return Object.freeze({
    status:'STRUCTURAL_LINEAGE_ONLY',custody,projection_sha256:sha256(canonicalJSON(proof)),
    ...proof,claim_traces:claimTraces,evidence_traces:evidenceTraces,module_traces:moduleTraces,
    original_chat_source:'UNKNOWN',source_attribution:'PRODUCER_ASSERTED_UNVERIFIED',
    provider_authenticated:false,externally_anchored:false,owner_message_authenticated:false,
    authorization_granted:false,independently_accepted:false,live_writer_enabled:false
  });
}

/** Filesystem entrypoint: always replays actual R2-A before deriving the R1 graph. */
export async function projectLocalJournal(folder,seed,bindings) {
  const state=await readJournal(folder);
  return assemble(state,seed,bindings,'LOCAL_UNANCHORED');
}
/** Portable entrypoint: actual R2-B1 checks bytes + replays through R2-A first. */
export async function projectPortableJournal(bytes,expected,seed,bindings) {
  const state=await verifyPortableJournal(bytes,expected);
  if(state.externally_anchored!==false||state.authorization_granted!==false)
    reject('INVALID_TRUST','portable reader unexpectedly claimed authority');
  return assemble(state,seed,bindings,'PORTABLE_UNANCHORED');
}

/** Narrow composition entry: exactly the replay result obtained from merged R2-B1.
 * Structurally valid check objects remain UNTRUSTED unless accompanied by a
 * separate native custody witness and independently supplied expectation.
 * This method does not authenticate the caller or the original Owner.
 */
export function projectVerifiedPortableReplay(replay,seed,bindings) {
  if(!replay||replay.schema!=='relay-portable-check-v1'
    ||replay.authorization_granted!==false||replay.externally_anchored!==false
    ||replay.independently_accepted!==false||replay.live_writer_enabled!==false)
    reject('UNTRUSTED_REPLAY','R2-B1 replay shape/authority does not match verified-reader contract');
  return assemble(replay,seed,bindings,'PORTABLE_UNANCHORED');
}
