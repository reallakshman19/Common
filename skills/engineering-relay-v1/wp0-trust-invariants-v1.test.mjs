/* V3.5 WP0 N4/N5 native read-only negative oracles.
 * Import ACTUAL R11 production code; no writer, approvals or CI claims.
 * All fixtures synthetic and deliberately not Owner-authenticated.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {deriveTrustPreflight,verifyTrustPreflight,TrustPreflightError} from './trust-preflight-v1.mjs';

const REPO='reallaksh19/Common',A='a'.repeat(64),B='b'.repeat(64);
const sha=x=>createHash('sha256').update(canonicalJSON(x)).digest('hex');
const untrusted=error=>error instanceof TrustPreflightError&&error.code==='UNTRUSTED_SOURCE';
const rejected=error=>error instanceof TrustPreflightError&&error.code==='UNTRUSTED_PREFLIGHT';

function specimen(){
  const source={
    source_lineage_sha256:A,
    custody:{parent_issue:REPO+'#787'},
    original_chat_source:'UNKNOWN',
    owner_message_authenticated:false,
    authorization_granted:false,
    independently_accepted:false,
  };
  const provider={
    repository:REPO,parent_issue:{number:787},
    snapshot_sha256:B,owner_intent:'NOT_AUTHENTICATED',
    human_review:'NOT_EVALUATED',evidence_acceptance:'NOT_EVALUATED',
    authorization_granted:false,independently_accepted:false,
    live_writer_enabled:false,
  };
  const core={
    schema:'wp0-synthetic-frontier-v1',repository:REPO,parent_issue:787,
    source_lineage_sha256:A,provider_snapshot_sha256:B,
    acceptance_denominator_state:'NOT_ADJUDICATED',
    accepted_claim_count:null,accepted_evidence_count:null,
    owner_message_authenticated:false,
    independently_accepted:false,authorization_granted:false,
    live_writer_enabled:false,
    original_owner_chat:'UNKNOWN',independent_review:'NOT_ACCEPTED',
    proposal_only:true,public_task_evidence_receipt_sha256:null,
    public_task_evidence_observation:'NOT_OBSERVED',
  };
  return {source,provider,frontier:{...core,frontier_sha256:sha(core)}};
}

test('N5 positive control: actual R11 keeps all five trust axes NOT_QUALIFIED',()=>{
  const {source,provider,frontier}=specimen();
  const r=deriveTrustPreflight(source,provider,frontier);
  assert.equal(r.schema,'relay-trust-preflight-v1');
  assert.deepEqual(Object.keys(r.axes).sort(),[
    'engineering_evidence','github_writer','independent_reviewer',
    'owner_source','privacy_and_retention',
  ]);
  for(const axis of Object.values(r.axes))assert.equal(axis.state,'NOT_QUALIFIED');
  assert.equal(r.independent_review_accepted,false);
  assert.equal(r.material_evidence_accepted,false);
  assert.equal(r.original_owner_authenticated,false);
  assert.equal(r.publication_writer_enabled,false);
  assert.equal(r.authorization_granted,false);
  assert.equal(r.next_authorized_action,'NONE_FROM_THIS_PREFLIGHT');
  assert.equal(r.accepted_claim_count,null);
  assert.equal(r.accepted_evidence_count,null);
  assert.equal(r.acceptance_denominator_state,'NOT_ADJUDICATED');
  assert.deepEqual(verifyTrustPreflight(r,source,provider,frontier),r);
  assert.equal(Object.isFrozen(r),true);
  assert.equal(Object.isFrozen(r.axes.github_writer),true);
});

test('N5 negative: fabricated original Owner authentication is never admissible',()=>{
  const {source,provider,frontier}=specimen();
  assert.throws(()=>deriveTrustPreflight(
    {...source,owner_message_authenticated:true},provider,frontier),untrusted);
  assert.throws(()=>deriveTrustPreflight(
    {...source,original_chat_source:'https://example.invalid/owner'},provider,frontier),untrusted);
});

test('N5 negative: accepted reviewer/evidence fields in provider are not authority',()=>{
  const {source,provider,frontier}=specimen();
  for(const change of [
    {human_review:'ACCEPTED'},
    {evidence_acceptance:'ACCEPTED'},
    {independently_accepted:true},
    {live_writer_enabled:true},
  ])assert.throws(()=>deriveTrustPreflight(source,{...provider,...change},frontier),untrusted);
});

test('N5 negative: even a rehashed accepted-frontier claim cannot authorize',()=>{
  const {source,provider,frontier}=specimen();
  const {frontier_sha256:discard,...core}=frontier;
  const forged={...core,independent_review:'ACCEPTED',accepted_evidence_count:1};
  assert.throws(()=>deriveTrustPreflight(
    source,provider,{...forged,frontier_sha256:sha(forged)}),untrusted);
});

test('N4 negative: cross-repository or wrong-parent source/provenance is rejected',()=>{
  const {source,provider,frontier}=specimen();
  assert.throws(()=>deriveTrustPreflight(
    source,{...provider,repository:'another/repo'},frontier),untrusted);
  assert.throws(()=>deriveTrustPreflight(
    {...source,custody:{parent_issue:REPO+'#999'}},provider,frontier),untrusted);
  assert.throws(()=>deriveTrustPreflight(
    source,{...provider,parent_issue:{number:999}},frontier),untrusted);
});

test('N5 negative: self-consistent source digests do not validate forged preflight output',()=>{
  const {source,provider,frontier}=specimen();
  const r=deriveTrustPreflight(source,provider,frontier);
  const fake={...r,independent_review_accepted:true,authorization_granted:true};
  assert.throws(()=>verifyTrustPreflight(fake,source,provider,frontier),rejected);
  assert.throws(()=>verifyTrustPreflight(
    {...r,positive_authorization_sources:['actor-self-assertion']},
    source,provider,frontier),rejected);
});
