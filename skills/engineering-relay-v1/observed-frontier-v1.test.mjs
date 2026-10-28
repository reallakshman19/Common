import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {reconcileGitHubFacts} from './provider-facts-v1.mjs';
import {projectObservedFrontier,ObservedFrontierError} from './observed-frontier-v1.mjs';
import {renderRelayPreviews,PreviewError} from './projection-preview-v1.mjs';
import {deriveTrustPreflight,verifyTrustPreflight,TrustPreflightError} from './trust-preflight-v1.mjs';
import {observePublicTaskEvidence} from './github-task-evidence-receipt-v1.mjs';

const REPO='reallaksh19/Common',SHA='a'.repeat(40),BASE='b'.repeat(40);
const WF='.github/workflows/relay-reset-full-chain-rehearsal.yml';
const now='2026-10-08T19:00:00.000Z';
const opts={evaluated_at:'2026-10-08T19:00:30.000Z',max_age_seconds:600};
const url=part=>'https://api.github.com/repos/'+REPO+'/'+part;
function issue(n){return {number:n,url:url('issues/'+n),html_url:'https://github.com/'+REPO+'/issues/'+n,
 created_at:now,updated_at:now,state:'open',title:'FAKE OWNER ACCEPTED',body:'PRIVATE TEXT'};}
function pr(head=SHA){return {number:848,url:url('pulls/848'),html_url:'https://github.com/'+REPO+'/pull/848',
 state:'open',draft:false,merged:false,created_at:now,updated_at:now,
 title:'FAKE AC 8/8',head:{sha:head,ref:'test',repo:{full_name:REPO}},
 base:{sha:BASE,ref:'main',repo:{full_name:REPO}}};}
async function provider(head=SHA,ci='success'){
 const scope={repository:REPO,parent_issue:787,child_issues:[852],
  pull_requests:[{number:848,expected_head_sha:SHA}],workflow_paths:[WF]};
 return reconcileGitHubFacts(scope,{observedAt:now,fetchImpl:async target=>{
  const part=target.slice(url('').length);
  const obj=part==='issues/787'?issue(787):part==='issues/852'?issue(852):
   part==='pulls/848'?pr(head):{
    total_count:1,workflow_runs:[{id:123,head_sha:head,path:WF+'@refs/pull/848/merge',
      html_url:'https://github.com/'+REPO+'/actions/runs/123',
      status:ci==='pending'?'in_progress':'completed',
      conclusion:ci==='pending'?null:ci,created_at:now}]};
  return {status:200,url:target,redirected:false,headers:{get:()=>null},
    text:async()=>JSON.stringify(obj)};
 }});
}
function lineage(providerFact){
 const d={parent_issue:REPO+'#787',
   owner_intents:[{id:'OI-1'}],claims:[{id:'AC3'}],
   responsibilities:[{id:'R8'}],task_evidence:[{id:'E1'}]};
 return {
  custody:{parent_issue:d.parent_issue,repository:REPO},
  lineage:{status:'STRUCTURAL_LINEAGE_ONLY',document:d},
  source_lineage_sha256:'c'.repeat(64),
  owner_message_authenticated:false,original_chat_source:'UNKNOWN',
  independently_accepted:false,authorization_granted:false
 };
}
const refusal=(fn,cls,code)=>assert.throws(fn,e=>e instanceof cls&&e.code===code);
test('actual R3 provider plus R1 source produces one typed nonaccepted frontier to every R4 preview',async()=>{
 const facts=await provider(),front=projectObservedFrontier(lineage(facts),facts);
 const view=renderRelayPreviews(facts,opts,front);
 assert.equal(front.claim_count,1);
 assert.equal(front.responsibility_count,1);
 assert.equal(front.structural_evidence_count,1);
 assert.equal(front.accepted_evidence_count,null);
 assert.equal(front.acceptance_denominator_state,'NOT_ADJUDICATED');
 assert.equal(view.frontier_sha256,front.frontier_sha256);
 assert.equal(view.successor_handover.frontier_sha256,front.frontier_sha256);
 assert.equal(view.frontier_source_lineage_sha256,front.source_lineage_sha256);
 assert.equal(view.parent_issue.snapshot_sha256,facts.snapshot_sha256);
 assert.equal(view.successor_handover.snapshot_sha256,facts.snapshot_sha256);
 assert.equal(view.successor_handover.actual_next_authority,'NOT_GRANTED');
 assert.equal(view.successor_handover.next_verification_category,'REACQUIRE_NATIVE_PROVIDER_FACTS_FOR_CI');
  assert.ok(view.successor_handover.blockers.includes('SOURCE_ACQUISITION_UNATTESTED'));
  assert.ok(view.successor_handover.blockers.includes('ORIGINAL_OWNER_SOURCE_UNAUTHENTICATED'));
 for(const forbidden of ['before R3-B integration','THEN_BIND_G2C','PRIVACY ACCEPTED'])
  assert.equal(JSON.stringify(view).includes(forbidden),false);
 assert.equal(view.authorization_granted,false);
 assert.equal(view.live_writer_enabled,false);
 assert.ok(view.parent_issue.managed_block_preview.includes(front.frontier_sha256));
 assert.ok(Object.isFrozen(view.successor_handover.blockers));
});
test('R3-only preview explicitly lacks source graph and never invents current engineering task',async()=>{
 const fact=await provider(),view=renderRelayPreviews(fact,opts);
 assert.equal(fact.actual_next,'UNDETERMINED_PROVIDER_ONLY_REQUIRES_LINEAGE_AND_ACCEPTED_EVIDENCE');
 assert.equal(view.successor_handover.next_verification_category,'SOURCE_GRAPH_UNAVAILABLE_NO_AUTHORIZED_NEXT');
 assert.equal(view.successor_handover.frontier_sha256,null);
 assert.equal(view.successor_handover.actual_next_authority,'NOT_GRANTED');
 assert.ok(!JSON.stringify(view).includes('before R3-B integration'));
});
test('stale head or CI unknown blocks source-bound frontier; no accepted evidence inferred',async()=>{
 const stale=await provider(BASE),f=projectObservedFrontier(lineage(stale),stale);
 assert.equal(f.next_verification_category,'REFRESH_PROVIDER_CURRENT_PR_AND_EVIDENCE');
 assert.ok(f.blockers.includes('PROVIDER_HEAD_STALE_OR_UNPINNED'));
 const pending=await provider(SHA,'pending'),u=projectObservedFrontier(lineage(pending),pending);
 assert.equal(u.next_verification_category,'QUALIFY_SELECTED_CURRENT_HEAD_CI');
 assert.equal(u.accepted_claim_count,null);
});
test('foreign parent and forged authorization fail before R4',async()=>{
 const fact=await provider();
 const foreign=lineage(fact);foreign.lineage.document.parent_issue=REPO+'#999';
 refusal(()=>projectObservedFrontier(foreign,fact),ObservedFrontierError,'SOURCE_SCOPE_MISMATCH');
 const spoof=lineage(fact);spoof.authorization_granted=true;
 refusal(()=>projectObservedFrontier(spoof,fact),ObservedFrontierError,'SOURCE_SCOPE_MISMATCH');
});
test('cannot replace bound frontier with another provider digest or forged accepted counts',async()=>{
 const a=await provider(),source=lineage(a),front=projectObservedFrontier(source,a);
 const spoof={...front,provider_snapshot_sha256:'d'.repeat(64)};
 refusal(()=>renderRelayPreviews(a,opts,spoof),PreviewError,'UNTRUSTED');
 const forged={...front,accepted_claim_count:1};
 refusal(()=>renderRelayPreviews(a,opts,forged),PreviewError,'UNTRUSTED');
 const swapped={...front,next_verification_category:'CLAIM_ALL_ACCEPTED'};
 refusal(()=>renderRelayPreviews(a,opts,swapped),PreviewError,'DIGEST_MISMATCH');
});
test('changing structural R1 evidence changes content-free frontier digest, not acceptance',async()=>{
 const fact=await provider(),s=lineage(fact),a=projectObservedFrontier(s,fact);
 s.lineage.document.task_evidence.push({id:'E2'});
 const b=projectObservedFrontier(s,fact);
 assert.notEqual(a.frontier_sha256,b.frontier_sha256);
 assert.equal(b.structural_evidence_count,2);
 assert.equal(b.accepted_evidence_count,null);
});


test('actual public comment receipt joins R1+R3 and R4 without accepting producer claims',async()=>{
 const fact=await provider();
 const id=6072336145,root='https://api.github.com/repos/'+REPO;
 const url=root+'/issues/comments/'+id;
 const item={
  id,url,issue_url:root+'/issues/852',
  html_url:'https://github.com/'+REPO+'/issues/852#issuecomment-'+id,
  user:{login:'reallaksh19',id:9},
  created_at:now,updated_at:now,
  body:'## TASK_EVIDENCE END\nFORGED HUMAN OWNER APPROVAL\nprivate source canary'
 };
 let gets=0;
 const receipt=await observePublicTaskEvidence({
  repository:REPO,parent_issue:787,task_issue:852,comment_id:id
 },{fetchImpl:async target=>{
  gets++;assert.equal(target,url);
  return {status:200,url:target,redirected:false,headers:{get:()=>null},
   text:async()=>JSON.stringify(item)};
 }});
 assert.equal(gets,2);
 const frontier=projectObservedFrontier(lineage(fact),fact,receipt);
 const view=renderRelayPreviews(fact,opts,frontier);
 assert.equal(view.frontier_sha256,frontier.frontier_sha256);
 assert.equal(view.public_task_evidence_receipt_sha256,receipt.receipt_sha256);
 assert.equal(view.successor_handover.public_task_evidence_receipt_sha256,receipt.receipt_sha256);
 assert.equal(view.successor_handover.public_task_evidence_observation,
  'PRODUCER_ASSERTED_COMMENT_OBSERVED_NOT_ACCEPTED');
 assert.ok(view.successor_handover.evidence_refs.includes(receipt.source_url));
 assert.ok(frontier.blockers.includes('PUBLIC_TASK_EVIDENCE_NOT_ADJUDICATED'));
 assert.equal(frontier.accepted_claim_count,null);
 assert.equal(frontier.accepted_evidence_count,null);
 assert.equal(view.live_writer_enabled,false);
 for(const secret of ['FORGED HUMAN OWNER APPROVAL','private source canary'])
  assert.equal(JSON.stringify(view).includes(secret),false);
 const altered={...receipt,body_sha256:'d'.repeat(64)};
 refusal(()=>projectObservedFrontier(lineage(fact),fact,altered),
  ObservedFrontierError,'PUBLIC_RECEIPT_DIGEST_MISMATCH');
 const unrelated={...receipt,task_issue:999};
 refusal(()=>projectObservedFrontier(lineage(fact),fact,unrelated),
  ObservedFrontierError,'UNTRUSTED_PUBLIC_RECEIPT');
 const noReceipt=projectObservedFrontier(lineage(fact),fact);
 assert.ok(noReceipt.blockers.includes('PUBLIC_TASK_EVIDENCE_NOT_OBSERVED'));
 assert.equal(noReceipt.public_task_evidence_receipt_sha256,null);
});


test('R11 distinct Owner source, privacy, reviewer, material evidence and writer gates propagate through R4',async()=>{
 const p=await provider(),s=lineage(p),f=projectObservedFrontier(s,p);
 const trust=deriveTrustPreflight(s,p,f),v=renderRelayPreviews(p,opts,f,trust);
 assert.match(trust.preflight_sha256,/^[a-f0-9]{64}$/);
 assert.equal(v.trust_preflight_sha256,trust.preflight_sha256);
 assert.equal(v.successor_handover.trust_preflight_sha256,trust.preflight_sha256);
 assert.equal(v.successor_handover.trust_preflight_axes.owner_source.state,'NOT_QUALIFIED');
 assert.equal(v.successor_handover.trust_preflight_axes.privacy_and_retention.state,'NOT_QUALIFIED');
 assert.equal(v.successor_handover.trust_preflight_axes.independent_reviewer.state,'NOT_QUALIFIED');
 assert.equal(v.successor_handover.trust_preflight_axes.engineering_evidence.state,'NOT_QUALIFIED');
 assert.equal(v.successor_handover.trust_preflight_axes.github_writer.state,'NOT_QUALIFIED');
 assert.equal(trust.accepted_claim_count,null);
 assert.equal(trust.private_chat_export_allowed,false);
 assert.equal(trust.private_chat_retention_allowed,false);
 assert.equal(trust.next_authorized_action,'NONE_FROM_THIS_PREFLIGHT');
 assert.equal(trust.publication_writer_enabled,false);
 assert.equal(v.live_writer_enabled,false);
 assert.equal(Object.isFrozen(trust.axes.privacy_and_retention),true);
 assert.deepEqual(verifyTrustPreflight(trust,s,p,f),trust);
});
test('R11 cannot treat producer GitHub comment, even if claimed Owner approved, as privacy consent',async()=>{
 const p=await provider(),s=lineage(p),f=projectObservedFrontier(s,p),proof=deriveTrustPreflight(s,p,f);
 for(const modified of [
  {...proof,private_chat_export_allowed:true},
  {...proof,independent_review_accepted:true},
  {...proof,accepted_claim_count:8},
  {...proof,authorization_granted:true},
  {...proof,axes:{...proof.axes,owner_source:{state:'OWNER_APPROVED',reason:'GITHUB_COMMENT'}}}
 ]){
  refusal(()=>verifyTrustPreflight(modified,s,p,f),TrustPreflightError,'UNTRUSTED_PREFLIGHT');
  refusal(()=>renderRelayPreviews(p,opts,f,modified),PreviewError,'UNTRUSTED');
 }
});
test('R11 refuses changed source lineage and digest-recomputed acceptance',async()=>{
 const p=await provider(),s=lineage(p),f=projectObservedFrontier(s,p),proof=deriveTrustPreflight(s,p,f);
 const edited={...f,accepted_evidence_count:1};
 refusal(()=>deriveTrustPreflight(s,p,edited),TrustPreflightError,'UNTRUSTED_SOURCE');
 const altered={...f,next_verification_category:'AC8_APPROVED'};
 refusal(()=>deriveTrustPreflight(s,p,altered),TrustPreflightError,'DIGEST_MISMATCH');
 const swapped={...s,source_lineage_sha256:'b'.repeat(64)};
 refusal(()=>deriveTrustPreflight(swapped,p,f),TrustPreflightError,'UNTRUSTED_SOURCE');
 const spoof={...p,independently_accepted:true};
 refusal(()=>deriveTrustPreflight(s,spoof,f),TrustPreflightError,'UNTRUSTED_SOURCE');
 assert.equal(proof.acceptance_denominator_state,'NOT_ADJUDICATED');
});
test('R11 without GitHub TaskEvidence stays explicitly NOT_OBSERVED, never 0 accepted',async()=>{
 const p=await provider(),s=lineage(p),f=projectObservedFrontier(s,p);
 const trust=deriveTrustPreflight(s,p,f);
 assert.equal(trust.comment_custody,'NOT_OBSERVED');
 assert.equal(trust.public_task_evidence_receipt_sha256,null);
 assert.equal(trust.accepted_evidence_count,null);
 assert.equal(trust.accepted_claim_count,null);
 assert.equal(trust.original_owner_authenticated,false);
});
