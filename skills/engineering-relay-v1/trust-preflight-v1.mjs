/* R11. Read-only trust-axis preflight derived from ACTUAL source, provider,
 * and the source-bound R9/R10 frontier. A digest is NOT an Owner signature.
 * A GitHub comment author is NOT a separately authenticated reviewer.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
export class TrustPreflightError extends Error{
 constructor(code,message){super(code+': '+message);this.name='TrustPreflightError';this.code=code;}
}
const fail=(code,reason)=>{throw new TrustPreflightError(code,reason);};
const HASH=/^[0-9a-f]{64}$/;
const sha=v=>createHash('sha256').update(canonicalJSON(v)).digest('hex');
function deepFreeze(root){
 const pending=[root],seen=new Set();
 while(pending.length){
  const v=pending.pop();if(!v||typeof v!=='object'||seen.has(v))continue;
  seen.add(v);for(const child of Object.values(v))if(child&&typeof child==='object')pending.push(child);
  Object.freeze(v);
 }
 return root;
}
const axes=Object.freeze([
 ['owner_source','ORIGINAL_CHAT_AUTHENTICITY_UNKNOWN'],
 ['privacy_and_retention','NO_AUTHENTICATED_OWNER_CONSENT_SCOPE'],
 ['independent_reviewer','NO_INDEPENDENT_REVIEW_ADJUDICATION'],
 ['engineering_evidence','PUBLIC_PRODUCER_CLAIM_NOT_MATERIAL_ADJUDICATION'],
 ['github_writer','EXPLICITLY_DISABLED']
]);
function proofInputs(source,provider,frontier){
 if(!source||!provider||!frontier||
    !HASH.test(source.source_lineage_sha256??'')||
    !HASH.test(provider.snapshot_sha256??'')||
    !HASH.test(frontier.frontier_sha256??'')||
    source.source_lineage_sha256!==frontier.source_lineage_sha256||
    provider.snapshot_sha256!==frontier.provider_snapshot_sha256||
    provider.repository!==frontier.repository||
    provider.parent_issue?.number!==frontier.parent_issue||
    source.custody?.parent_issue!==
      provider.repository+'#'+provider.parent_issue?.number||
    frontier.acceptance_denominator_state!=='NOT_ADJUDICATED'||
    frontier.accepted_claim_count!==null||
    frontier.accepted_evidence_count!==null||
    source.original_chat_source!=='UNKNOWN'||
    source.owner_message_authenticated!==false||
    source.authorization_granted!==false||
    source.independently_accepted!==false||
    provider.owner_intent!=='NOT_AUTHENTICATED'||
    provider.human_review!=='NOT_EVALUATED'||
    provider.evidence_acceptance!=='NOT_EVALUATED'||
    provider.authorization_granted!==false||
    provider.independently_accepted!==false||
    provider.live_writer_enabled!==false||
    frontier.owner_message_authenticated!==false||
    frontier.independently_accepted!==false||
    frontier.authorization_granted!==false||
    frontier.live_writer_enabled!==false||
    frontier.original_owner_chat!=='UNKNOWN'||
    frontier.independent_review!=='NOT_ACCEPTED'||
    frontier.proposal_only!==true)
    fail('UNTRUSTED_SOURCE','source/provider/frontier must not promote asserted authority');
 const core={...frontier};delete core.frontier_sha256;
 if(sha(core)!==frontier.frontier_sha256)
   fail('DIGEST_MISMATCH','source-bound frontier was modified');
 if((frontier.public_task_evidence_receipt_sha256===null)!==
   (frontier.public_task_evidence_observation==='NOT_OBSERVED')||
   !(frontier.public_task_evidence_receipt_sha256===null||
      HASH.test(frontier.public_task_evidence_receipt_sha256)))
   fail('UNTRUSTED_SOURCE','public comment observation has inconsistent shape');
}
export function deriveTrustPreflight(source,provider,frontier){
 proofInputs(source,provider,frontier);
 const kinds=Object.fromEntries(axes.map(([name,reason])=>
   [name,{state:'NOT_QUALIFIED',reason}]));
 const core={
  schema:'relay-trust-preflight-v1',
  repository:provider.repository,parent_issue:provider.parent_issue.number,
  source_lineage_sha256:source.source_lineage_sha256,
  provider_snapshot_sha256:provider.snapshot_sha256,
  frontier_sha256:frontier.frontier_sha256,
  public_task_evidence_receipt_sha256:frontier.public_task_evidence_receipt_sha256,
  source_custody:'STRUCTURAL_AND_PRODUCER_ASSERTED_ONLY',
  comment_custody:frontier.public_task_evidence_receipt_sha256===null?
    'NOT_OBSERVED':'MUTABLE_COMMENT_DOUBLE_READ_PRODUCER_ASSERTED',
  axes:kinds,
  positive_authorization_sources:[],
  accepted_claim_count:null,accepted_evidence_count:null,
  acceptance_denominator_state:'NOT_ADJUDICATED',
  next_authorized_action:'NONE_FROM_THIS_PREFLIGHT',
  private_chat_export_allowed:false,
  private_chat_retention_allowed:false,
  independent_review_accepted:false,
  material_evidence_accepted:false,
  publication_writer_enabled:false,
  original_owner_authenticated:false,
  authorization_granted:false,
  proposal_only:true
 };
 return deepFreeze({...core,preflight_sha256:sha(core)});
}
/** Only verify a preflight whose *source inputs* have also been passed in.
 * A self-consistent checksum of a fabricated approval cannot pass.
 */
export function verifyTrustPreflight(proof,source,provider,frontier){
 const expected=deriveTrustPreflight(source,provider,frontier);
 if(!proof||typeof proof!=='object'||Array.isArray(proof)||
   canonicalJSON(proof)!==canonicalJSON(expected))
   fail('UNTRUSTED_PREFLIGHT','candidate proof must match recomputation from original sources');
 return expected;
}
