/* RELAY RESET R4 Batch-01 — PURE proposals only, no GitHub access or writes.
 * One immutable R3-A native/provider-injected snapshot -> issue, PR, handover.
 * Source/provider truth != human review, Owner authenticity, or accepted evidence.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {deriveCandidateState} from './candidate-verification-v1.mjs';

export class PreviewError extends Error {
  constructor(code,why){super(code+': '+why);this.name='PreviewError';this.code=code;}
}
const fail=(code,why)=>{throw new PreviewError(code,why);};
const HASH=/^[0-9a-f]{64}$/,SHA=/^[0-9a-f]{40}$/;
const REPO=/^[a-zA-Z0-9-]{1,39}\/[a-zA-Z0-9_.-]{1,100}$/;
const STATES=new Set(['PASS','FAIL','PENDING','UNKNOWN']);
function sha(x){return createHash('sha256').update(canonicalJSON(x)).digest('hex');}
function exact(o,keys,label){
  if(!o||typeof o!=='object'||Array.isArray(o)||
    Object.keys(o).some(k=>!keys.includes(k))||
    keys.some(k=>!Object.hasOwn(o,k)))fail('INVALID',label+' missing or unknown property');
}
function freeze(root){
  const seen=new Set(),stack=[root];
  while(stack.length){
    const v=stack.pop();if(!v||typeof v!=='object'||seen.has(v))continue;
    seen.add(v);for(const w of Object.values(v))if(w&&typeof w==='object')stack.push(w);
    Object.freeze(v);
  }
  return root;
}
function utc(value){
  return typeof value==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(value)
    &&Number.isFinite(Date.parse(value));
}
function safeString(v){return typeof v==='string'&&v.length>0;}
function checkSnapshot(input){
  let s;
  try{s=JSON.parse(canonicalJSON(input));}catch{fail('INVALID','snapshot not canonical-safe JSON');}
  exact(s,['schema','repository','observed_at','parent_issue','child_issues','pr_facts',
    'relationship_assertion','provider_transport','read_count','source_state','consistency',
    'evidence_acceptance','human_review','owner_intent','independent_journal_tip','actual_next',
    'authorization_granted','independently_accepted','live_writer_enabled','snapshot_sha256'],'R3 snapshot');
  if(s.schema!=='relay-provider-facts-v1'||!HASH.test(s.snapshot_sha256)||
    !REPO.test(s.repository)||!utc(s.observed_at)||
    !['PROVIDER_OBSERVED','INJECTED_UNVERIFIED'].includes(s.source_state)||
    (s.source_state==='PROVIDER_OBSERVED')!==(s.provider_transport==='NATIVE_GITHUB_GET')||
    s.consistency!=='PR_DOUBLE_READ_NON_ATOMIC'||
    s.relationship_assertion!=='CALLER_SCOPED_UNVERIFIED'||
    s.evidence_acceptance!=='NOT_EVALUATED'||s.human_review!=='NOT_EVALUATED'||
    s.owner_intent!=='NOT_AUTHENTICATED'||s.independent_journal_tip!=='NOT_ANCHORED'||
    s.authorization_granted!==false||s.independently_accepted!==false||
    s.live_writer_enabled!==false||!Number.isSafeInteger(s.read_count)||s.read_count<4)
    fail('UNTRUSTED','R3 snapshot cannot be an accepted/atomic/authorizing source');
  const declared=s.snapshot_sha256;delete s.snapshot_sha256;
  if(sha(s)!==declared)fail('DIGEST_MISMATCH','snapshot was mutated after its digest was published');
  s.snapshot_sha256=declared;
  const base='https://github.com/'+s.repository+'/';
  if(!s.parent_issue||!Number.isSafeInteger(s.parent_issue.number)||
    s.parent_issue.number<1||s.parent_issue.source_url!==base+'issues/'+s.parent_issue.number||
    !['open','closed'].includes(s.parent_issue.state)||
    !Array.isArray(s.child_issues)||s.child_issues.length>3||
    !Array.isArray(s.pr_facts)||s.pr_facts.length<1||s.pr_facts.length>4)
    fail('UNTRUSTED','parent/children/PR shape invalid');
  const ids=new Set([s.parent_issue.number]);
  for(const c of s.child_issues){
    if(!c||!Number.isSafeInteger(c.number)||c.number<1||
      ids.has(c.number)||c.source_url!==base+'issues/'+c.number||
      !['open','closed'].includes(c.state))fail('UNTRUSTED','child issue invalid or repeated');
    ids.add(c.number);
  }
  const prs=new Set();
  for(const p of s.pr_facts){
    if(!p||!Number.isSafeInteger(p.number)||p.number<1||prs.has(p.number)||
      p.source_url!==base+'pull/'+p.number||!SHA.test(p.head_sha)||
      !SHA.test(p.base_sha)||typeof p.draft!=='boolean'||
      typeof p.merged!=='boolean'||!['open','closed'].includes(p.state)||
      !['MATCH','STALE','UNPINNED'].includes(p.currentness)||
      (p.currentness==='MATCH'&&p.expected_head_sha!==p.head_sha)||
      (p.currentness==='STALE'&&(!SHA.test(p.expected_head_sha)||p.expected_head_sha===p.head_sha))||
      (p.currentness==='UNPINNED'&&p.expected_head_sha!==null)||
      (p.merged&&p.state!=='closed')||
      !Array.isArray(p.ci_workflows)||p.ci_workflows.length<1||p.ci_workflows.length>8)
      fail('UNTRUSTED','PR observation or currentness invalid');
    prs.add(p.number);
    const paths=new Set();
    for(const w of p.ci_workflows){
      if(!w||!safeString(w.path)||paths.has(w.path)||!STATES.has(w.state)||
        w.head_sha!==p.head_sha||
        (w.run_id!==null&&(!Number.isSafeInteger(w.run_id)||w.run_id<1))||
        (w.state==='PASS'&&w.run_conclusion!=='success')||
        (w.state==='PENDING'&&w.run_status==='completed')||
        (w.state==='UNKNOWN'&&w.run_id!==null))
        fail('UNTRUSTED','CI observation inconsistent with selected PR HEAD');
      paths.add(w.path);
    }
  }
  return freeze(s);
}
function verifiedFrontier(raw,provider,candidateState){
  if(raw===undefined||raw===null)return null;
  let f;
  try{f=JSON.parse(canonicalJSON(raw));}
  catch{fail('INVALID','frontier not canonical-safe');}
  exact(f,[
    'schema','repository','parent_issue','source_lineage_sha256',
    'provider_snapshot_sha256','candidate_state_sha256','source_history','claim_count',
    'responsibility_count','structural_evidence_count','owner_intent_count',
    'acceptance_denominator_state','accepted_claim_count',
    'accepted_evidence_count','next_verification_category','blockers',
    'original_owner_chat','independent_review','provider_consistency',
    'producer_assertions_not_authority','owner_message_authenticated',
    'independently_accepted','authorization_granted','live_writer_enabled',
    'proposal_only','frontier_sha256','public_task_evidence_receipt_sha256',
    'public_task_evidence_source_url','public_task_evidence_comment_id',
    'public_task_evidence_observation'],'observed frontier');
  if(!HASH.test(f.frontier_sha256)||
    f.schema!=='relay-observed-frontier-v1'||
    f.repository!==provider.repository||
    f.parent_issue!==provider.parent_issue.number||
    f.provider_snapshot_sha256!==provider.snapshot_sha256||
    f.candidate_state_sha256!==candidateState.candidate_state_sha256||
    !HASH.test(f.source_lineage_sha256)||
    f.acceptance_denominator_state!=='NOT_ADJUDICATED'||
    f.accepted_claim_count!==null||f.accepted_evidence_count!==null||
    f.original_owner_chat!=='UNKNOWN'||f.independent_review!=='NOT_ACCEPTED'||
    (f.public_task_evidence_receipt_sha256===null)!==
      (f.public_task_evidence_source_url===null)||
    (f.public_task_evidence_receipt_sha256===null)!==
      (f.public_task_evidence_comment_id===null)||
    (f.public_task_evidence_receipt_sha256===null)!==
      (f.public_task_evidence_observation==='NOT_OBSERVED')||
    !(f.public_task_evidence_receipt_sha256===null||
      HASH.test(f.public_task_evidence_receipt_sha256))||
    !(f.public_task_evidence_comment_id===null||
      (Number.isSafeInteger(f.public_task_evidence_comment_id)&&f.public_task_evidence_comment_id>0))||
    !(f.public_task_evidence_source_url===null||
      (typeof f.public_task_evidence_source_url==='string'&&
        f.public_task_evidence_source_url.startsWith(
          'https://github.com/'+provider.repository+'/issues/')))||
    f.provider_consistency!==provider.consistency||
    f.producer_assertions_not_authority!==true||
    f.owner_message_authenticated!==false||
    f.independently_accepted!==false||
    f.authorization_granted!==false||f.live_writer_enabled!==false||
    f.proposal_only!==true||
    !Array.isArray(f.blockers)||f.blockers.length<1||f.blockers.length>8||
    new Set(f.blockers).size!==f.blockers.length||
    f.blockers.some(x=>typeof x!=='string'||!/^[A-Z0-9_]{3,100}$/.test(x))||
    typeof f.next_verification_category!=='string'||
    !/^[A-Z0-9_]{3,100}$/.test(f.next_verification_category)||
    ['claim_count','responsibility_count','structural_evidence_count','owner_intent_count']
      .some(key=>!Number.isSafeInteger(f[key])||f[key]<0||f[key]>10000))
    fail('UNTRUSTED','frontier source/parent/authority inconsistent with provider');
  const declared=f.frontier_sha256;delete f.frontier_sha256;
  if(sha(f)!==declared)fail('DIGEST_MISMATCH','frontier changed after deriving source facts');
  f.frontier_sha256=declared;
  return freeze(f);
}
function freshness(snapshot,options){
  exact(options,['evaluated_at','max_age_seconds'],'evaluation');
  if(!utc(options.evaluated_at)||!Number.isInteger(options.max_age_seconds)||
    options.max_age_seconds<1||options.max_age_seconds>3600)
    fail('INVALID','evaluation time or maximum age invalid');
  const delta=Date.parse(options.evaluated_at)-Date.parse(snapshot.observed_at);
  if(delta < -5000)fail('INVALID','evaluation precedes snapshot observation');
  return delta>options.max_age_seconds*1000?'STALE':'WITHIN_CONFIGURED_WINDOW';
}
function status(candidate,observedFresh,native){
  // A single R12 reducer owns CI/head precedence; the R4 renderer only
  // handles source transport/freshness presentation. Never infer acceptance.
  if(!native)return 'UNVERIFIED_TRANSPORT';
  if(observedFresh==='STALE')return 'STALE_OR_UNPINNED';
  return candidate.material_status;
}
function compactTitle(parts){
  const out=parts.join(' | ');
  if(out.length>235)fail('LIMIT','preview title exceeds safe bounded size');
  return out;
}

/** Pure/immutable: never fetch, write, or infer a human acceptance. */
export function renderRelayPreviews(rawSnapshot,rawOptions,rawFrontier=null,rawTrust=null){
  // Derive R12 from the ORIGINAL R3 instance. checkSnapshot() canonically
  // copies JSON and necessarily drops an ephemeral native-acquisition witness.
  const s=checkSnapshot(rawSnapshot);
  const candidateState=deriveCandidateState(rawSnapshot);
  let o;
  try{o=JSON.parse(canonicalJSON(rawOptions));}catch{fail('INVALID','evaluation parameters invalid');}
  const fresh=freshness(s,o),native=candidateState.source_acquisition_attested;
  const frontier=verifiedFrontier(rawFrontier,s,candidateState);
  // Only an exact content-free, no-grant R11 witness may be displayed.
  // Full-chain also recomputes R11 from original source/provider/frontier.
  let trust=null;
  if(rawTrust!==null&&rawTrust!==undefined){
    try{trust=JSON.parse(canonicalJSON(rawTrust));}
    catch{fail('INVALID','trust preflight cannot be canonicalized');}
    if(trust.schema!=='relay-trust-preflight-v1'||
      !HASH.test(trust.preflight_sha256??'')||
      !frontier||trust.frontier_sha256!==frontier.frontier_sha256||
      trust.provider_snapshot_sha256!==s.snapshot_sha256||
      trust.source_lineage_sha256!==frontier.source_lineage_sha256||
      trust.public_task_evidence_receipt_sha256!==frontier.public_task_evidence_receipt_sha256||
      trust.next_authorized_action!=='NONE_FROM_THIS_PREFLIGHT'||
      trust.acceptance_denominator_state!=='NOT_ADJUDICATED'||
      trust.accepted_claim_count!==null||trust.accepted_evidence_count!==null||
      trust.private_chat_export_allowed!==false||
      trust.private_chat_retention_allowed!==false||
      trust.independent_review_accepted!==false||
      trust.material_evidence_accepted!==false||
      trust.publication_writer_enabled!==false||
      trust.original_owner_authenticated!==false||
      trust.authorization_granted!==false||
      trust.proposal_only!==true||
      !trust.axes||typeof trust.axes!=='object'||
      Object.keys(trust.axes).sort().join('|')!==
       ['owner_source','privacy_and_retention','independent_reviewer',
        'engineering_evidence','github_writer'].sort().join('|')||
      Object.values(trust.axes).some(axis=>axis?.state!=='NOT_QUALIFIED'||
        typeof axis.reason!=='string'||!/^[A-Z0-9_]{3,100}$/.test(axis.reason))||
      !Array.isArray(trust.positive_authorization_sources)||
      trust.positive_authorization_sources.length!==0)
      fail('UNTRUSTED','preflight cannot grant owner/CI/review/write permissions');
    const copy={...trust};delete copy.preflight_sha256;
    if(sha(copy)!==trust.preflight_sha256)
      fail('DIGEST_MISMATCH','trust preflight mutated');
    trust=freeze(trust);
  }
  const nextVerification=frontier?.next_verification_category??'SOURCE_GRAPH_UNAVAILABLE_NO_AUTHORIZED_NEXT';
  const blockers=frontier?.blockers??['SOURCE_GRAPH_NOT_BOUND'];
  const source=s.snapshot_sha256;
  const prTitles=s.pr_facts.map(p=>{
    const candidate=candidateState.pr_candidates.find(x=>x.number===p.number);
    if(!candidate)fail('STATE_MISMATCH','provider PR lacks canonical candidate state');
    const health=status(candidate,fresh,native);
    return {number:p.number,source_url:p.source_url,head_sha:p.head_sha,
      state:health,original_provider_state:p.state,
      workflow_scope:'CALLER_SELECTED_NOT_REQUIRED_POLICY',
      checked_workflow_paths:p.ci_workflows.map(w=>w.path),
      consistency:s.consistency, freshness:fresh,
      title:compactTitle(['RELAY PROPOSED ONLY','PR#'+p.number,
        'HEAD '+p.head_sha.slice(0,8),'CI '+health,'REVIEW NOT_EVALUATED']),
      snapshot_sha256:source,proposal_only:true};
  });
  const children=s.child_issues.map(c=>({
    number:c.number,source_url:c.source_url,state:c.state,
    title:compactTitle(['RELAY PROPOSED ONLY','ISSUE#'+c.number,
      'STATE '+c.state.toUpperCase(),'ACCEPTANCE NOT_EVALUATED']),
    snapshot_sha256:source,proposal_only:true,
    freshness:fresh,consistency:s.consistency
  }));
  const parent=s.parent_issue;
  const summary={
    parent_number:parent.number,source_url:parent.source_url,
    title:compactTitle(['RELAY PROPOSED ONLY','PARENT#'+parent.number,
      'PRs '+s.pr_facts.length,'REVIEWS NOT_EVALUATED','ACCEPTANCE UNKNOWN']),
    child_count:children.length,pr_count:prTitles.length,
    freshness:fresh,consistency:s.consistency,
    states:prTitles.map(p=>({number:p.number,state:p.state})),
    snapshot_sha256:source,proposal_only:true,
    managed_block_preview:'<!-- RELAY_R4_DRAFT_ONLY; DO NOT WRITE -->\n'+
      'R3 observed: '+s.observed_at+'\n'+
      'Snapshot SHA256: '+source+'\n'+
      'Provider: '+s.source_state+'; '+s.consistency+'\n'+
      'Source-bound frontier SHA256: '+(frontier?.frontier_sha256??'NONE')+'\n'+
      'Canonical candidate-state SHA256: '+candidateState.candidate_state_sha256+'\n'+
      'Next verification category (NOT AUTHORIZED): '+nextVerification+'\n'+
      'Blockers: '+blockers.join(',')+'\n'+
      'R11 separated source/consent/reviewer gates (NOT ACCEPTED): '+
        (trust?.preflight_sha256??'NONE')+'\n'+
      'Observed public TaskEvidence receipt (NOT ACCEPTED): '+
        (frontier?.public_task_evidence_receipt_sha256??'NONE')+'\n'+


      'Reviewer status: NOT_EVALUATED; Owner authority: NOT_AUTHENTICATED\n'+
      'CI paths are CALLER_SELECTED, NOT proven required policy checks\n'+
      prTitles.map(p=>'PR #'+p.number+' '+p.head_sha.slice(0,8)+' '+p.state).join('\n')+
      '\n<!-- END RELAY_R4_DRAFT_ONLY -->'
  };
  const handover={
    title:'RELAY successor fact-only preview — NOT AN OWNER-AUTHORIZED HANDOVER',
    parent_url:parent.source_url,
    evidence_refs:[parent.source_url,...children.map(x=>x.source_url),
      ...prTitles.map(x=>x.source_url),
      ...(frontier?.public_task_evidence_source_url?[frontier.public_task_evidence_source_url]:[])],
    pr_heads:prTitles.map(p=>({number:p.number,head_sha:p.head_sha,state:p.state})),
    instructions:[
      'Fetch canonical parent and original Owner instructions; source chat permalink UNKNOWN',
      'Do not treat issue/PR titles, selected hosted green CI or this preview as accepted TaskEvidence',
      'CI workflow paths are caller-selected, NOT independently verified required checks',
      'Verify derived blockers against current Owner consent and different-principal review; no task is authorized by this preview',
      'Read the source-bound verification category: '+nextVerification,
      'Preserve human privacy/retention/Owner grant HOLD; do not activate R5 writer',
      'Read a new provider-current snapshot; this is bounded and non-atomic'
    ],
    public_task_evidence_receipt_sha256:frontier?.public_task_evidence_receipt_sha256??null,
    public_task_evidence_source_url:frontier?.public_task_evidence_source_url??null,
    public_task_evidence_observation:frontier?.public_task_evidence_observation??'NOT_OBSERVED',
    trust_preflight_sha256:trust?.preflight_sha256??null,
    trust_preflight_axes:trust?.axes??null,
    candidate_state_sha256:candidateState.candidate_state_sha256,
    frontier_sha256:frontier?.frontier_sha256??null,
    frontier_source_lineage_sha256:frontier?.source_lineage_sha256??null,
    actual_next_authority:'NOT_GRANTED',
    next_verification_category:nextVerification,
    blockers,
    source_status:s.source_state,consistency:s.consistency,
    freshness:fresh,observed_at:s.observed_at,evaluated_at:o.evaluated_at,
    owner_message_authenticated:false,independently_accepted:false,
    authorization_granted:false,live_writer_enabled:false,
    snapshot_sha256:source,proposal_only:true
  };
  const core={
    schema:'relay-projection-preview-v1',snapshot_sha256:source,
    source_state:s.source_state,freshness:fresh,
    observed_at:s.observed_at,evaluated_at:o.evaluated_at,
    parent_issue:summary,child_issues:children,pr_titles:prTitles,
    successor_handover:handover,
    trust_preflight_sha256:trust?.preflight_sha256??null,
    candidate_state_sha256:candidateState.candidate_state_sha256,
    frontier_sha256:frontier?.frontier_sha256??null,
    frontier_source_lineage_sha256:frontier?.source_lineage_sha256??null,
    next_verification_category:nextVerification,
    blockers,
    public_task_evidence_receipt_sha256:frontier?.public_task_evidence_receipt_sha256??null,
    public_task_evidence_observation:frontier?.public_task_evidence_observation??'NOT_OBSERVED',
    proposal_only:true,
    owner_message_authenticated:false,authorization_granted:false,
    independently_accepted:false,live_writer_enabled:false
  };
  const result={...core,projection_sha256:sha(core)};
  return freeze(result);
}
