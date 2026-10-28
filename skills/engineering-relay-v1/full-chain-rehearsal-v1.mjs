/* RELAY RESET R3-B source+provider+R4 FULL-CHAIN REHEARSAL ONLY.
 * Exact unmerged candidate modules, read-only, synthetic journal.
 * No Owner-authenticated sources, independent approval, R5 writer, or merge.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {projectCommittedGithubLineage} from './github-journal-lineage-v1.mjs';
import {reconcileGitHubFacts} from './provider-facts-v1.mjs';
import {renderRelayPreviews} from './projection-preview-v1.mjs';
import {projectObservedFrontier} from './observed-frontier-v1.mjs';
import {observePublicTaskEvidence} from './github-task-evidence-receipt-v1.mjs';
import {deriveTrustPreflight,verifyTrustPreflight} from './trust-preflight-v1.mjs';
import {deriveCandidateState} from './candidate-verification-v1.mjs';

export class FullChainError extends Error {
  constructor(code,why){super(code+': '+why);this.name='FullChainError';this.code=code;}
}
const fail=(code,why)=>{throw new FullChainError(code,why);};
const HEX=/^[0-9a-f]{64}$/;
const sha=x=>createHash('sha256').update(canonicalJSON(x)).digest('hex');
function deepFreeze(value){
  const seen=new Set(),stack=[value];
  while(stack.length){
    const v=stack.pop();if(!v||typeof v!=='object'||seen.has(v))continue;
    seen.add(v);
    for(const child of Object.values(v))if(child&&typeof child==='object')stack.push(child);
    Object.freeze(v);
  }
  return value;
}
function safe(v,label){
  try{return JSON.parse(canonicalJSON(v));}
  catch{fail('INVALID',label+' is not safe canonical input');}
}
function boundedOpts(value,label,allowObservedAt=false){
  const allowed=allowObservedAt?['fetchImpl','readToken','observedAt']:['fetchImpl','readToken'];
  if(!value||typeof value!=='object'||Array.isArray(value)||
    Object.keys(value).some(k=>!allowed.includes(k)))
    fail('INVALID',label+' must contain only bounded read-only inputs');
}
function dataOnlyView(source,provider,preview,digest,candidates){
  const custody=source.custody;
  const view={
    schema:'relay-full-chain-synthetic-rehearsal-v1',
    status:source.status==='GITHUB_BYTES_TO_STRUCTURAL_LINEAGE'&&
      provider.source_state==='PROVIDER_OBSERVED'?
      'NATIVE_GITHUB_SYNTHETIC_REHEARSAL_UNANCHORED':
      'INJECTED_UNVERIFIED_REHEARSAL',
    repository:provider.repository,
    parent_issue:provider.parent_issue.number,
    source_url:custody.github_source_url,
    source_commit_sha:custody.commit_sha,
    source_blob_sha1:custody.git_blob_sha1,
    source_bundle_sha256:custody.bundle_sha256,
    source_tip_sha256:custody.tip.sha256,
    real_r2b1_replayed:custody.real_r2b1_replayed,
    event_count:custody.event_count,session_count:custody.session_ids.length,
    structural_lineage_sha256:source.lineage.projection_sha256,
    github_source_lineage_sha256:source.source_lineage_sha256,
    frontier_sha256:preview.frontier_sha256,
    candidate_state_sha256:preview.candidate_state_sha256,
    trust_preflight_sha256:preview.trust_preflight_sha256,
    source_consent_review_approval:'NOT_QUALIFIED',
    public_task_evidence_receipt_sha256:preview.public_task_evidence_receipt_sha256,
    public_task_evidence_observation:preview.public_task_evidence_observation,

    next_verification_category:preview.next_verification_category,
    blockers:preview.blockers,
    acceptance_denominator_state:'NOT_ADJUDICATED',
    provider_snapshot_sha256:provider.snapshot_sha256,
    r4_projection_sha256:preview.projection_sha256,
    verification_candidates:candidates.pr_candidates,
    pr_heads:provider.pr_facts.map(x=>({
      number:x.number,head_sha:x.head_sha,currentness:x.currentness,
      ci:x.ci_workflows.map(w=>({path:w.path,state:w.state}))
    })),
    // Pure R4 never includes raw provider issues/bodies or session prompt text.
    proposed_parent_title:preview.parent_issue.title,
    proposed_pr_titles:preview.pr_titles.map(x=>({number:x.number,title:x.title})),
    proposed_handover:preview.successor_handover,
    provider_observed_at:provider.observed_at,
    provider_consistency:'PR_DOUBLE_READ_NON_ATOMIC',
    original_chat_source:'UNKNOWN',
    source_history:'SYNTHETIC_PRODUCER_ASSERTED',
    workflow_scope:'CALLER_SELECTED_NOT_REQUIRED_POLICY',
    proposal_only:true,
    owner_message_authenticated:false,externally_anchored:false,
    authorization_granted:false,independently_accepted:false,
    live_writer_enabled:false
  };
  // A unified digest binds the exact immutable source SHA/lineage, provider
  // observation and the full pure preview; no new independent trust anchor.
  return deepFreeze({...view,full_chain_sha256:digest});
}

/** Compose ONE actual G2c source read and ONE actual R3 read. Never export raw
 * replay/lineage content, even when all synthetic journal entries are public.
 * Current PR head must match the immutable source commit SHA; otherwise refuse.
 */
export async function rehearseNativeFullChain(rawInput,options={}) {
  const input=safe(rawInput,'full-chain specification');
  if(!input||typeof input!=='object'||Array.isArray(input)||
    Object.keys(input).sort().join()!==['bindings','owner_seed','provider_scope','source_spec'].sort().join())
    fail('INVALID','full-chain specification requires exact four fields');
  if(!options||typeof options!=='object'||Array.isArray(options)||
    Object.keys(options).some(k=>!['sourceRead','providerRead','evaluation','publicEvidenceRead'].includes(k)))
    fail('INVALID','unexpected options');
  const sourceRead=options.sourceRead??{},providerRead=options.providerRead??{};
  const publicRead=options.publicEvidenceRead??null;
  if(publicRead!==null){
    if(typeof publicRead!=='object'||Array.isArray(publicRead)||
      Object.keys(publicRead).some(k=>!['scope','readToken','fetchImpl'].includes(k))||
      !Object.hasOwn(publicRead,'scope'))
      fail('INVALID','bounded public evidence scope required');
    boundedOpts({readToken:publicRead.readToken,fetchImpl:publicRead.fetchImpl},
      'public evidence read');
  }
  boundedOpts(sourceRead,'source read');
  boundedOpts(providerRead,'provider read',true);
  if(!options.evaluation||typeof options.evaluation!=='object'||Array.isArray(options.evaluation)||
    Object.keys(options.evaluation).sort().join()!=='evaluated_at,max_age_seconds')
    fail('INVALID','bounded pure-render evaluation required');
  const src=input.source_spec,scope=input.provider_scope;
  if(typeof src?.repository!=='string'||src.repository!==scope?.repository||
    src.parent_issue!==src.repository+'#'+scope.parent_issue||
    input.owner_seed?.parent_issue!==src.parent_issue)
    fail('SOURCE_SCOPE_MISMATCH','source, Owner seed and provider parent/repository must agree');
  if(!Array.isArray(scope.pull_requests)||scope.pull_requests.length===0||
    !scope.pull_requests.some(p=>p.expected_head_sha===src.commit_sha))
    fail('SOURCE_HEAD_UNPINNED','source commit must be an expected PR head in provider scope');

  // Physically perform both real consumers: one source Contents GET→R2→R1,
  // then R3 provider issue/PR/current CI read with its bounded PR double-read.
  const source=await projectCommittedGithubLineage(
    src,input.owner_seed,input.bindings,sourceRead);
  // Public comment custody is observed, not an Owner authorization or a
  // TaskEvidence acceptance. It is an optional source read, never a write.
  let publicReceipt=null;
  if(publicRead!==null){
    const e=publicRead.scope;
    if(e?.repository!==scope.repository||e.parent_issue!==scope.parent_issue||
      !scope.child_issues.includes(e.task_issue))
      fail('PUBLIC_EVIDENCE_SCOPE_MISMATCH','comment task not in current provider scope');
    const readOpts={};
    if(publicRead.fetchImpl!==undefined)readOpts.fetchImpl=publicRead.fetchImpl;
    if(publicRead.readToken!==undefined)readOpts.readToken=publicRead.readToken;
    publicReceipt=await observePublicTaskEvidence(e,readOpts);
  }
  const provider=await reconcileGitHubFacts(scope,providerRead);
  if(source.custody.parent_issue!==provider.repository+'#'+provider.parent_issue.number||
    source.custody.repository!==provider.repository||
    source.lineage.document.parent_issue!==source.custody.parent_issue||
    source.original_chat_source!=='UNKNOWN'||source.externally_anchored!==false||
    source.authorization_granted!==false||source.independently_accepted!==false||
    provider.authorization_granted!==false||provider.independently_accepted!==false)
    fail('TRUST_OR_PARENT_CONFLICT','source graph and GitHub issue scope conflict');
  const matching=provider.pr_facts.filter(p=>p.head_sha===source.custody.commit_sha&&
    p.expected_head_sha===source.custody.commit_sha&&p.currentness==='MATCH');
  if(matching.length!==1)fail('SOURCE_HEAD_CHANGED',
    'committed source SHA does not match exactly one current provider PR head');
  if(!HEX.test(source.source_lineage_sha256)||
    !HEX.test(provider.snapshot_sha256)||provider.consistency!=='PR_DOUBLE_READ_NON_ATOMIC')
    fail('INVALID_SOURCE_PROOF','missing digest or inconsistent R3 provider-current fence');
  const candidates=deriveCandidateState(provider);
  const frontier=projectObservedFrontier(source,provider,publicReceipt);
  if(frontier.candidate_state_sha256!==candidates.candidate_state_sha256)
    fail('STATE_MISMATCH','R9 frontier not bound to canonical candidate state');
  const trust=deriveTrustPreflight(source,provider,frontier);
  const preview=renderRelayPreviews(provider,options.evaluation,frontier,trust);
  verifyTrustPreflight(trust,source,provider,frontier);
  if(preview.candidate_state_sha256!==candidates.candidate_state_sha256||
    preview.successor_handover.candidate_state_sha256!==candidates.candidate_state_sha256)
    fail('STATE_MISMATCH','R4 handover not bound to R3/R9 candidate state');
  if(preview.trust_preflight_sha256!==trust.preflight_sha256||
    preview.successor_handover.trust_preflight_sha256!==trust.preflight_sha256)
    fail('RENDER_SOURCE_MISMATCH','R4 preview did not consume exact R11 trust boundary');
  if(preview.public_task_evidence_receipt_sha256!==
       (publicReceipt?.receipt_sha256??null)||
    preview.successor_handover.public_task_evidence_receipt_sha256!==
       (publicReceipt?.receipt_sha256??null))
    fail('RENDER_SOURCE_MISMATCH','R4 not bound to observed public comment');
  if(preview.frontier_sha256!==frontier.frontier_sha256||
    preview.successor_handover.frontier_sha256!==frontier.frontier_sha256||
    preview.frontier_source_lineage_sha256!==source.source_lineage_sha256)
    fail('RENDER_SOURCE_MISMATCH','R4 handover is not bound to actual R1/R3 frontier');
  if(preview.snapshot_sha256!==provider.snapshot_sha256||
    preview.parent_issue.snapshot_sha256!==provider.snapshot_sha256||
    preview.pr_titles.some(p=>p.snapshot_sha256!==provider.snapshot_sha256)||
    preview.child_issues.some(p=>p.snapshot_sha256!==provider.snapshot_sha256)||
    preview.successor_handover.snapshot_sha256!==provider.snapshot_sha256||
    preview.authorization_granted!==false||preview.live_writer_enabled!==false||
    preview.proposal_only!==true)
    fail('RENDER_SOURCE_MISMATCH','R4 projection consumed a different source snapshot');
  const digest=sha({
    source_lineage_sha256:source.source_lineage_sha256,
    frontier_sha256:frontier.frontier_sha256,
    candidate_state_sha256:candidates.candidate_state_sha256,
    trust_preflight_sha256:trust.preflight_sha256,
    public_task_evidence_receipt_sha256:publicReceipt?.receipt_sha256??null,
    source_commit_sha:source.custody.commit_sha,
    provider_snapshot_sha256:provider.snapshot_sha256,
    r4_projection_sha256:preview.projection_sha256,
    selected_current_pr:matching[0].number
  });
  // Never release G1 .document, raw .events, G2c .replay, or private body.
  return dataOnlyView(source,provider,preview,digest,candidates);
}
