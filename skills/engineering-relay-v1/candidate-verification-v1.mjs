/* RELAY RESET R12: single canonical, PURE provider-candidate state projection.
 * Normative: owner intent/decomposition/evidence remain V3.2 DELP concerns;
 * selected GitHub CI/head are material observations, NEVER task acceptance.
 * Consumers R9/R4/R3-B/R8 share this same content-addressed state.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {hasNativeProviderAcquisition} from './provider-facts-v1.mjs';

export class CandidateStateError extends Error{
 constructor(code,reason){super(code+': '+reason);this.name='CandidateStateError';this.code=code;}
}
const refuse=(code,reason)=>{throw new CandidateStateError(code,reason);};
const H40=/^[0-9a-f]{40}$/,H64=/^[0-9a-f]{64}$/;
const CI=new Set(['PASS','PENDING','FAIL','UNKNOWN']);
const hash=v=>createHash('sha256').update(canonicalJSON(v)).digest('hex');
function freeze(v){
 const pending=[v],seen=new Set();
 while(pending.length){
  const e=pending.pop();if(!e||typeof e!=='object'||seen.has(e))continue;
  seen.add(e);for(const x of Object.values(e))if(x&&typeof x==='object')pending.push(x);
  Object.freeze(e);
 }return v;
}
function copied(source){
 try{return JSON.parse(canonicalJSON(source));}
 catch{refuse('INVALID','source is not canonical JSON');}
}
function expectedDigest(observation){
 if(!observation||typeof observation!=='object'||!H64.test(observation.snapshot_sha256??''))
  refuse('INVALID','no provider snapshot digest');
 const p={...observation};delete p.snapshot_sha256;
 if(hash(p)!==observation.snapshot_sha256)
  refuse('SNAPSHOT_DIGEST_MISMATCH','provider was changed after observation');
}
function perPR(pr,nativeObserved){
 if(!pr||!Number.isSafeInteger(pr.number)||pr.number<1||
   !H40.test(pr.head_sha??'')||!H40.test(pr.base_sha??'')||
   !['MATCH','STALE','UNPINNED'].includes(pr.currentness)||
   !(pr.expected_head_sha===null||H40.test(pr.expected_head_sha??''))||
   (pr.currentness==='MATCH'&&pr.head_sha!==pr.expected_head_sha)||
   (pr.currentness==='STALE'&&pr.head_sha===pr.expected_head_sha)||
   (pr.currentness==='UNPINNED'&&pr.expected_head_sha!==null)||
   typeof pr.merged!=='boolean'||!['open','closed'].includes(pr.state)||
   (pr.merged&&pr.state!=='closed')||
   !Array.isArray(pr.ci_workflows)||pr.ci_workflows.length<1||
   pr.ci_workflows.length>8)
   refuse('INVALID','PR/head/scope invalid');
 const paths=new Set();
 const workflows=pr.ci_workflows.map(w=>{
  if(!w||typeof w.path!=='string'||!w.path.startsWith('.github/workflows/')||
    paths.has(w.path)||!CI.has(w.state)||w.head_sha!==pr.head_sha||
    (w.state==='PASS'&&w.run_conclusion!=='success')||
    (w.state==='PENDING'&&w.run_status==='completed')||
    (w.state==='UNKNOWN'&&w.run_id!==null))
    refuse('INVALID','selected workflow/head inconsistent');
  paths.add(w.path);
  return {path:w.path,state:w.state,run_id:w.run_id??null};
 });
 const states=workflows.map(w=>w.state);
 const ci=states.includes('UNKNOWN')?'UNKNOWN':
   states.includes('FAIL')?'FAIL':
   states.includes('PENDING')?'PENDING':'PASS';
 const head=pr.currentness==='MATCH'?'CURRENT':
   pr.currentness==='STALE'?'STALE':'UNPINNED';
 return {number:pr.number,head_sha:pr.head_sha,
   expected_head_sha:pr.expected_head_sha,merged:pr.merged,
   head_state:head,selected_ci_state:ci,selected_workflows:workflows,
   // "qualified" means qualified selected hosted facts only, NOT code acceptance.
   selected_ci_qualified:nativeObserved&&head==='CURRENT'&&ci==='PASS',
   material_status:head!=='CURRENT'?'STALE_OR_UNPINNED':
     ci==='UNKNOWN'?'UNKNOWN':
     ci==='FAIL'?'CI_NON_SUCCESS':
     ci==='PENDING'?'PENDING':'SELECTED_CI_PASS_ONLY'};
}
/** The ONE candidate state shared by R9/R4/full-chain/cold successor.
 * In particular, no real-time result changes the Owner/reviewer/consent axes.
 */
export function deriveCandidateState(source){
 // Only R3 can attest its exact in-process native source instance. JSON labels,
 // recomputed hashes and cross-process copies have no such capability.
 const nativeAcquisition=hasNativeProviderAcquisition(source);
 const p=copied(source);expectedDigest(p);
 if(p.schema!=='relay-provider-facts-v1'||!H64.test(p.snapshot_sha256)||
   typeof p.repository!=='string'||!Number.isSafeInteger(p.parent_issue?.number)||
   !['PROVIDER_OBSERVED','INJECTED_UNVERIFIED'].includes(p.source_state)||
   (p.source_state==='PROVIDER_OBSERVED')!==(p.provider_transport==='NATIVE_GITHUB_GET')||
   (nativeAcquisition&&p.source_state!=='PROVIDER_OBSERVED')||
   p.consistency!=='PR_DOUBLE_READ_NON_ATOMIC'||
   p.owner_intent!=='NOT_AUTHENTICATED'||
   p.evidence_acceptance!=='NOT_EVALUATED'||p.human_review!=='NOT_EVALUATED'||
   p.authorization_granted!==false||p.independently_accepted!==false||
   p.live_writer_enabled!==false||
   !Array.isArray(p.pr_facts)||p.pr_facts.length<1||p.pr_facts.length>4)
   refuse('UNTRUSTED','provider cannot grant human, CI or publication authority');
 const prs=p.pr_facts.map(pr=>perPR(pr,nativeAcquisition));
 if(new Set(prs.map(x=>x.number)).size!==prs.length)refuse('INVALID','duplicate PR');
 const blockers=[];
 // Untrusted/replayed PASS is still not a qualified native acquisition.
 // One canonical R12 contract owns this fact for every downstream consumer.
 if(!nativeAcquisition)blockers.push('SOURCE_ACQUISITION_UNATTESTED');
 if(prs.some(x=>x.head_state!=='CURRENT'))blockers.push('PROVIDER_HEAD_STALE_OR_UNPINNED');
 if(prs.some(x=>x.selected_ci_state!=='PASS'))
   blockers.push('SELECTED_CI_NOT_ALL_PASS');
 const next=blockers.includes('PROVIDER_HEAD_STALE_OR_UNPINNED')?
    'REFRESH_PROVIDER_CURRENT_PR_AND_EVIDENCE':
    blockers.includes('SELECTED_CI_NOT_ALL_PASS')?
    'QUALIFY_SELECTED_CURRENT_HEAD_CI':
    blockers.includes('SOURCE_ACQUISITION_UNATTESTED')?
    'REACQUIRE_NATIVE_PROVIDER_FACTS_FOR_CI':null;
 const core={
   schema:'relay-candidate-verification-v1',
   repository:p.repository,parent_issue:p.parent_issue.number,
   provider_snapshot_sha256:p.snapshot_sha256,
   source_observation:p.source_state,source_acquisition_attested:nativeAcquisition,
   consistency:'PR_DOUBLE_READ_NON_ATOMIC',
   pr_candidates:prs,blockers,next_candidate_verification:next,
   workflow_policy:'CALLER_SELECTED_NOT_REQUIRED_POLICY',
   acceptance_contract:'PARENT_787_AC1_AC8_UNADJUDICATED',
   accepted_claim_count:null,accepted_evidence_count:null,
   acceptance_denominator_state:'NOT_ADJUDICATED',
   authorization_granted:false,independently_accepted:false,
   live_writer_enabled:false,proposal_only:true
 };
 return freeze({...core,candidate_state_sha256:hash(core)});
}
export function verifyCandidateState(proof,provider){
 const expected=deriveCandidateState(provider);
 let candidate;
 try{candidate=copied(proof);}catch{refuse('INVALID','candidate invalid');}
 if(canonicalJSON(candidate)!==canonicalJSON(expected))
   refuse('STATE_MISMATCH','candidate must be recomputed from actual provider facts');
 return expected;
}
