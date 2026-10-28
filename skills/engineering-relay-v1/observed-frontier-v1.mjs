/* RELAY RESET R9: join an actual R1 structural lineage and an R3
 * provider-current observation into one READ-ONLY frontier.  This is NOT
 * acceptance adjudication, Owner authentication or a GitHub publisher.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {deriveCandidateState} from './candidate-verification-v1.mjs';

export class ObservedFrontierError extends Error {
  constructor(code,reason){super(code+': '+reason);this.name='ObservedFrontierError';this.code=code;}
}
const fail=(code,reason)=>{throw new ObservedFrontierError(code,reason);};
const H64=/^[0-9a-f]{64}$/;
const digest=x=>createHash('sha256').update(canonicalJSON(x)).digest('hex');
function deepFreeze(root){
  const seen=new Set(),pending=[root];
  while(pending.length){
    const v=pending.pop();if(!v||typeof v!=='object'||seen.has(v))continue;
    seen.add(v);for(const x of Object.values(v))if(x&&typeof x==='object')pending.push(x);
    Object.freeze(v);
  }
  return root;
}
function idArray(items){
  if(!Array.isArray(items)||items.length>10000)fail('INVALID','unbounded R1 lineage array');
  if(items.some(item=>!item||typeof item!=='object'||typeof item.id!=='string'))
    fail('INVALID','malformed R1 lineage entity');
  return items;
}
function sourceGraph(source,provider){
  const d=source?.lineage?.document,c=source?.custody;
  if(!d||!c||!H64.test(source?.source_lineage_sha256??'')||
    !H64.test(provider?.snapshot_sha256??'')||
    typeof provider?.repository!=='string'||
    !Number.isSafeInteger(provider?.parent_issue?.number)||
    d.parent_issue!==provider.repository+'#'+provider.parent_issue.number||
    c.parent_issue!==d.parent_issue||c.repository!==provider.repository||
    source.lineage.status!=='STRUCTURAL_LINEAGE_ONLY'||
    source.owner_message_authenticated!==false||
    source.original_chat_source!=='UNKNOWN'||
    source.independently_accepted!==false||source.authorization_granted!==false||
    provider.owner_intent!=='NOT_AUTHENTICATED'||
    provider.evidence_acceptance!=='NOT_EVALUATED'||
    provider.independently_accepted!==false||provider.authorization_granted!==false)
    fail('SOURCE_SCOPE_MISMATCH','R1 source facts and R3 provider parent/trust must agree');
  return d;
}
/**
 * This frontier counts only STRUCTURAL source nodes, not accepted tasks or
 * verified human instructions. Provider facts are fresh-ish non-atomic GETs;
 * no selected hosted CI can grant acceptance. Actual next is a bounded
 * derived *verification category*, never an agent execution directive.
 */
function verifiedPublicReceipt(receipt,provider){
 if(receipt===undefined||receipt===null)return null;
 if(receipt.schema!=='relay-public-task-evidence-receipt-v1'||
   receipt.repository!==provider.repository||
   receipt.parent_issue!==provider.parent_issue.number||
   !provider.child_issues.some(c=>c.number===receipt.task_issue)||
   !H64.test(receipt.body_sha256)||!H64.test(receipt.receipt_sha256)||
   receipt.provider_read_count!==2||
   receipt.consistency!=='COMMENT_DOUBLE_READ_NON_ATOMIC'||
   receipt.observation!=='PRODUCER_ASSERTED_PUBLIC_COMMENT_NOT_ACCEPTED'||
   !['INJECTED_UNVERIFIED','NATIVE_GITHUB_COMMENT_GET'].includes(receipt.provider_source)||
   (provider.source_state==='PROVIDER_OBSERVED')!==
      (receipt.provider_source==='NATIVE_GITHUB_COMMENT_GET')||
   receipt.task_evidence_accepted!==false||
   receipt.author_is_owner_authenticated!==false||
   receipt.independent_reviewer_accepted!==false||
   receipt.authorization_granted!==false||
   receipt.live_writer_enabled!==false)
   fail('UNTRUSTED_PUBLIC_RECEIPT','comment custody is not bound to provider task/authority');
 const copy=JSON.parse(canonicalJSON(receipt)),declared=copy.receipt_sha256;
 delete copy.receipt_sha256;
 if(digest(copy)!==declared)fail('PUBLIC_RECEIPT_DIGEST_MISMATCH','comment witness mutated');
 return receipt;
}
export function projectObservedFrontier(source,provider,publicReceipt=null){
  const d=sourceGraph(source,provider);
  const intents=idArray(d.owner_intents),claims=idArray(d.claims),
    tasks=idArray(d.responsibilities),evidence=idArray(d.task_evidence);
  if(intents.length<1||!Array.isArray(provider.pr_facts)||provider.pr_facts.length<1||
    provider.consistency!=='PR_DOUBLE_READ_NON_ATOMIC')
    fail('INVALID','missing bounded structural graph or provider-current facts');
  const receipt=verifiedPublicReceipt(publicReceipt,provider);
  const candidates=deriveCandidateState(provider);
  // CI/head policy is owned ONLY by candidate-verification-v1, not repeated.
  const blockers=[
    ...candidates.blockers,
    receipt?'PUBLIC_TASK_EVIDENCE_NOT_ADJUDICATED':'PUBLIC_TASK_EVIDENCE_NOT_OBSERVED'
  ];
  if(source.original_chat_source==='UNKNOWN')
    blockers.push('ORIGINAL_OWNER_SOURCE_UNAUTHENTICATED');
  if(provider.human_review==='NOT_EVALUATED'||source.independently_accepted===false)
    blockers.push('INDEPENDENT_REVIEW_NOT_ACCEPTED');
  if(source.authorization_granted===false)
    blockers.push('PRIVACY_AND_PUBLICATION_AUTHORITY_NOT_GRANTED');
  const next=candidates.next_candidate_verification??
    (blockers.includes('ORIGINAL_OWNER_SOURCE_UNAUTHENTICATED')?
    'DEFINE_PRIVACY_SAFE_OWNER_SOURCE_CUSTODY':
    blockers.includes('INDEPENDENT_REVIEW_NOT_ACCEPTED')?
    'OBTAIN_DIFFERENT_PRINCIPAL_SOURCE_REVIEW':
    'REQUIRE_EXPLICIT_OWNER_AUTHORIZATION');
  const core={
    schema:'relay-observed-frontier-v1',
    repository:provider.repository,parent_issue:provider.parent_issue.number,
    source_lineage_sha256:source.source_lineage_sha256,
    provider_snapshot_sha256:provider.snapshot_sha256,
    candidate_state_sha256:candidates.candidate_state_sha256,
    source_history:'STRUCTURAL_SYNTHETIC_OR_PRODUCER_ASSERTED',
    claim_count:claims.length,responsibility_count:tasks.length,
    structural_evidence_count:evidence.length,owner_intent_count:intents.length,
    acceptance_denominator_state:'NOT_ADJUDICATED',
    accepted_claim_count:null,accepted_evidence_count:null,
    public_task_evidence_receipt_sha256:receipt?.receipt_sha256??null,
    public_task_evidence_source_url:receipt?.source_url??null,
    public_task_evidence_comment_id:receipt?.comment_id??null,
    public_task_evidence_observation:receipt?
      'PRODUCER_ASSERTED_COMMENT_OBSERVED_NOT_ACCEPTED':'NOT_OBSERVED',

    next_verification_category:next,blockers,
    original_owner_chat:'UNKNOWN',independent_review:'NOT_ACCEPTED',
    provider_consistency:provider.consistency,
    producer_assertions_not_authority:true,
    owner_message_authenticated:false,independently_accepted:false,
    authorization_granted:false,live_writer_enabled:false,proposal_only:true
  };
  return deepFreeze({...core,frontier_sha256:digest(core)});
}
