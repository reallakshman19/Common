import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {hasNativeProviderAcquisition} from '../../../skills/engineering-relay-v1/provider-facts-v1.mjs';
import {deriveCandidateState} from '../../../skills/engineering-relay-v1/candidate-verification-v1.mjs';
import {canonicalJSON} from '../../../skills/engineering-relay-v1/provenance-v1.mjs';
import {inspectPreAdmission} from './pre-admission-boundary-v1.mjs';

const ROOT=fileURLToPath(new URL('../../../',import.meta.url));
const read=path=>readFileSync(new URL('../../../'+path,import.meta.url),'utf8');
const REPO='reallakshman19/Common',HEAD='708416ebd05c300571097859fc6c1e3596cd7224';
const OLD='18de77d3176d87dd347ed95ad313ae330935bf27';
const B='98da09e40265becee5b15d4144813b99b38c0024';
const noAuthority=x=>{
  assert.equal(x.admission,'NOT_ADMITTED');
  assert.equal(x.evidence_admitted,false);
  assert.equal(x.owner_authenticated,false);
  assert.equal(x.reviewer_qualified,false);
  assert.equal(x.programme_progress,null);
  assert.equal(x.delp_projector_invoked,false);
  assert.equal(x.writer_authorized,false);
  assert.equal(x.runner_lease,'NOT_PROVEN');
};
const locator=()=>({
  repository:REPO,repository_id:1412133785,root_issue:5,leaf_issue:30,
  pr_number:31,candidate_head_sha:HEAD,
  base_branch:'recovery/5-wp2a-u05-integrated-regression-20261010',
  evidence_comment_id:6090013793,evidence_claimed_head_sha:OLD,
  expected_author_login:'reallakshman19',facts_schema_line:'V32',
});
// This object is deliberately forged to resemble a good native R3 outcome.
// A matching digest and green selected workflows MUST NOT create R3 authority.
const copiedProvider=()=>{
  const core={
    schema:'relay-provider-facts-v1',repository:REPO,
    parent_issue:{number:5},source_state:'PROVIDER_OBSERVED',
    provider_transport:'NATIVE_GITHUB_GET',
    consistency:'PR_DOUBLE_READ_NON_ATOMIC',
    owner_intent:'NOT_AUTHENTICATED',evidence_acceptance:'NOT_EVALUATED',
    human_review:'NOT_EVALUATED',authorization_granted:false,
    independently_accepted:false,live_writer_enabled:false,
    pr_facts:[{
      number:31,head_sha:HEAD,base_sha:B,expected_head_sha:HEAD,
      currentness:'MATCH',merged:false,state:'open',
      ci_workflows:[{
        path:'.github/workflows/v35-wp2b-pre-admission.yml',
        state:'PASS',head_sha:HEAD,run_conclusion:'success',
        run_status:'completed',run_id:37997181529,
      }],
    }],
  };
  return {...core,snapshot_sha256:createHash('sha256')
    .update(canonicalJSON(core)).digest('hex')};
};

test('B05 R3 native WeakSet cannot be reproduced by serialized GitHub-looking data',()=>{
  const copied=copiedProvider();
  assert.equal(hasNativeProviderAcquisition(copied),false);
  assert.equal(hasNativeProviderAcquisition(structuredClone(copied)),false);
  assert.equal(hasNativeProviderAcquisition({...copied,source_acquisition_attested:true}),false);
});

test('B05 physical R12 green selected CI from forged R3 source stays unqualified',()=>{
  const r12=deriveCandidateState(copiedProvider());
  assert.equal(r12.schema,'relay-candidate-verification-v1');
  assert.equal(r12.source_acquisition_attested,false);
  assert.ok(r12.blockers.includes('SOURCE_ACQUISITION_UNATTESTED'));
  assert.equal(r12.workflow_policy,'CALLER_SELECTED_NOT_REQUIRED_POLICY');
  assert.equal(r12.pr_candidates[0].selected_ci_state,'PASS');
  assert.equal(r12.pr_candidates[0].selected_ci_qualified,false);
  assert.equal(r12.accepted_claim_count,null);
  assert.equal(r12.accepted_evidence_count,null);
  assert.equal(r12.authorization_granted,false);
  assert.equal(r12.live_writer_enabled,false);
});

test('B05 tampering with an R3 serialized CI result cannot reuse its digest',()=>{
  const forged=copiedProvider();
  forged.pr_facts[0].ci_workflows[0].run_conclusion='failure';
  assert.throws(()=>deriveCandidateState(forged),e=>e.code==='SNAPSHOT_DIGEST_MISMATCH');
});

test('B05 fake Owner/reviewer/policy/witness fields are denied before reading provider',async()=>{
  let reads=0;
  const spies={
    candidate:async()=>{reads++;throw Error('must not run');},
    ci:async()=>{reads++;throw Error('must not run');},
    evidence:async()=>{reads++;throw Error('must not run');},
  };
  for(const key of ['owner_authenticated','reviewer_qualified',
    'policy_adopted','source_acquisition_attested','writer_authorized']){
    const out=await inspectPreAdmission({...locator(),[key]:true},spies);
    noAuthority(out);
    assert.deepEqual(out.admission_blockers,['INPUT_CONTRACT_OR_FACTS_SCHEMA_INVALID']);
  }
  assert.equal(reads,0);
});

test('B05 V3.2 and V3.5 wire names remain different without schema promotion',async()=>{
  const errorReader=async()=>{throw Error('source unavailable');};
  const readers={candidate:errorReader,ci:errorReader,evidence:errorReader};
  const v32=await inspectPreAdmission(locator(),readers);
  const v35=await inspectPreAdmission({...locator(),facts_schema_line:'V35'},readers);
  noAuthority(v32);noAuthority(v35);
  assert.equal(v32.candidate_facts_schema,'relay-v3.2-delp-checkpoint-facts');
  assert.equal(v35.candidate_facts_schema,'relay-v3.5-delp-checkpoint-facts');
  assert.notEqual(v32.candidate_facts_schema,v35.candidate_facts_schema);
  assert.equal(v32.target_delp_policy,'NOT_ADOPTED');
  assert.equal(v35.target_delp_policy,'NOT_ADOPTED');
});

test('B05 missing provider read cannot fabricate a positive eligible fact',async()=>{
  const unavailable=async()=>{throw Error('HTTP 403');};
  const out=await inspectPreAdmission(locator(),{
    candidate:unavailable,ci:unavailable,evidence:unavailable,
  });
  noAuthority(out);
  assert.equal(out.source_status,'UNKNOWN');
  assert.equal(out.source_digest,null);
});

test('B05 historical frozen graph is explicitly old-repository scoped',()=>{
  const graph=JSON.parse(read('.github/v32-evidence-spine/718-proposal-v2.json'));
  assert.equal(graph.programme.repository,'reallaksh19/Common');
  assert.equal(graph.programme.root,'Common#718');
  assert.notEqual(graph.programme.repository,REPO);
  assert.equal(graph.decomposition_policy.mode,'ENFORCED');
});

test('B05 physical source and C6 contract has no silent bridge or alternative DELP',()=>{
  const u04=read('relay/RECOVERY/V35_R14_WP2A_20261010/cross-source-vector-v1.mjs');
  const wp2b=read('relay/RECOVERY/V35_R14_WP2B_20261010/pre-admission-boundary-v1.mjs');
  const r3=read('skills/engineering-relay-v1/provider-facts-v1.mjs');
  const r12=read('skills/engineering-relay-v1/candidate-verification-v1.mjs');
  const c6=read('skills/engineering-pr-delivery-v3.2/scripts/plan_handover.py');
  assert.match(r3,/const nativeReadSnapshots=new WeakSet\(\)/);
  assert.match(r3,/export function hasNativeProviderAcquisition/);
  assert.match(r12,/hasNativeProviderAcquisition\(source\)/);
  assert.match(r12,/CALLER_SELECTED_NOT_REQUIRED_POLICY/);
  for(const path of ['current-candidate-material-v1.mjs','required-ci-material-v1.mjs','task-evidence-comment-v1.mjs'])
    assert.ok(u04.includes(path),'U04 must physically import '+path);
  assert.match(wp2b,/observeLiveCrossSource/);
  assert.match(wp2b,/NOT_ADMITTED/);
  assert.match(c6,/_assert_native_graph_current_release/);
  assert.match(c6,/build_delp_source_bound_successor/);
  assert.equal(typeof ROOT,'string');
});
