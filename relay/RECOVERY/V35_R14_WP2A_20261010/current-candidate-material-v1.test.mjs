import test from 'node:test';
import assert from 'node:assert/strict';
import {observeCurrentCandidate} from './current-candidate-material-v1.mjs';

const REPO='reallakshman19/Common', ID=1412133785, H1='a'.repeat(40), H2='b'.repeat(40), B1='c'.repeat(40);
const BASE='recovery/5-m0-reference-identity-census-20261009';
const contract=()=>({repository:REPO,repository_id:ID,root_issue:5,leaf_issue:20,pr_number:22,expected_candidate_sha:H1,expected_base_ref:BASE});
function payload(){return {
  '':{id:ID,full_name:REPO,default_branch:'main'},
  'issues/5':{number:5,html_url:`https://github.com/${REPO}/issues/5`,state:'open'},
  'issues/20':{number:20,html_url:`https://github.com/${REPO}/issues/20`,state:'open'},
  'pulls/22':{number:22,html_url:`https://github.com/${REPO}/pull/22`,state:'open',
    head:{sha:H1,ref:'recovery/5-wp2a-u01-test',repo:{id:ID,full_name:REPO}},
    base:{sha:B1,ref:BASE,repo:{id:ID,full_name:REPO}}},
  'git/ref/heads/recovery/5-wp2a-u01-test':{ref:'refs/heads/recovery/5-wp2a-u01-test',object:{sha:H1}},
  [`git/ref/heads/${BASE}`]:{ref:`refs/heads/${BASE}`,object:{sha:B1}},
};}
function makeReader(data=payload(),onRead=()=>{}){
  let n=0;return async(repo,path)=>{assert.equal(repo,REPO);onRead(++n,path,data);if(!(path in data))throw Error('404');return structuredClone(data[path]);};
}
async function checkBad(change){const p=payload();change(p);const r=await observeCurrentCandidate(contract(),makeReader(p));assert.equal(r.current,false);assert.equal(r.evidence_admitted,false);assert.equal(r.writer_authorized,false);assert.equal(r.source_vector,null);assert.equal(r.programme_progress,null);}

test('U01 positive two-round material binding cannot promote injected objects to authority',async()=>{
  let calls=0;const r=await observeCurrentCandidate(contract(),makeReader(payload(),()=>calls++));
  assert.equal(calls,12);assert.equal(r.current,true);assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');
  assert.equal(r.material_observation,'MATCH_AT_OBSERVATION');assert.equal(r.source_vector.candidate_sha,H1);
  assert.match(r.source_vector_sha256,/^sha256:[a-f0-9]{64}$/);
  assert.equal(r.ci_required_status,'UNKNOWN');assert.equal(r.task_evidence_status,'NOT_CHECKED');
  assert.equal(r.evidence_admitted,false);assert.equal(r.canonical_delp_projection,'NOT_CALCULATED');
  assert.equal(r.programme_progress,null);assert.equal(r.writer_authorized,false);
});
test('U01 stable digest across independent equivalent reads',async()=>{
  const a=await observeCurrentCandidate(contract(),makeReader());const b=await observeCurrentCandidate(contract(),makeReader());
  assert.equal(a.source_vector_sha256,b.source_vector_sha256);
});
test('U01 wrong expected repo id is rejected before any network',async()=>{
  let calls=0;const v={...contract(),repository_id:1207996454};
  const r=await observeCurrentCandidate(v,async()=>{calls++;throw Error('unexpected');});
  assert.equal(calls,0);assert.equal(r.current,false);assert.deepEqual(r.errors,['WRONG_CURRENT_REPOSITORY']);
});
test('U01 unknown contract extension denied',async()=>{
  const r=await observeCurrentCandidate({...contract(),evidence_admitted:true},makeReader());
  assert.deepEqual(r.errors,['INVALID_CONTRACT_SHAPE']);
});
test('U01 invalid branch pathname rejected before transport',async()=>{
  const r=await observeCurrentCandidate({...contract(),expected_base_ref:'a/../b'},makeReader());
  assert.deepEqual(r.errors,['INVALID_EXPECTED_BASE_REF']);
});
test('U01 mismatched repo ID from provider',()=>checkBad(p=>{p[''].id=1207996454;}));
test('U01 historical issue URL in current leaf',()=>checkBad(p=>{p['issues/20'].html_url='https://github.com/reallaksh19/Common/issues/20';}));
test('U01 PR pretending to be a root issue',()=>checkBad(p=>{p['issues/5'].pull_request={};}));
test('U01 wrong PR kind, number or repo',()=>checkBad(p=>{p['pulls/22'].head.repo.id=1207996454;}));
test('U01 wrong candidate SHA',()=>checkBad(p=>{p['pulls/22'].head.sha=H2;}));
test('U01 wrong base branch',()=>checkBad(p=>{p['pulls/22'].base.ref='main';}));
test('U01 ref mismatch',()=>checkBad(p=>{p['git/ref/heads/recovery/5-wp2a-u01-test'].object.sha=H2;}));
test('U01 missing/403/429 provider reads remain untrusted and unverified',async()=>{
  for(const status of [404,403,429]){
    const r=await observeCurrentCandidate(contract(),async()=>{throw Error(String(status));});
    assert.equal(r.current,false);assert.equal(r.material_observation,'NOT_CURRENT_OR_UNVERIFIED');
    assert.equal(r.ci_required_status,'UNKNOWN');
  }
});
test('U01 head moves between first and second reads, deny',async()=>{
  const p=payload();let count=0;const read=makeReader(p,(n,path,data)=>{
    if(n===7){data['pulls/22'].head.sha=H2;data['git/ref/heads/recovery/5-wp2a-u01-test'].object.sha=H2;}
    count=n;
  });
  const r=await observeCurrentCandidate(contract(),read);
  assert.equal(count>=7,true);assert.equal(r.current,false);assert.equal(r.evidence_admitted,false);
});
test('U01 base moves between independent reads, deny',async()=>{
  const p=payload();const read=makeReader(p,(n,path,data)=>{
    if(n===7){data['pulls/22'].base.sha=H2;data[`git/ref/heads/${BASE}`].object.sha=H2;}
  });
  const r=await observeCurrentCandidate(contract(),read);
  assert.equal(r.current,false);assert.equal(r.writer_authorized,false);
});
test('U01 cannot present original Owner/Reviewer/CI as positive on valid material',async()=>{
  const r=await observeCurrentCandidate(contract(),makeReader());
  assert.equal(r.owner_authenticated,false);assert.equal(r.independent_reviewer_qualified,false);
  assert.equal(r.evidence_admitted,false);assert.equal(r.successor_lease,'NOT_PROVEN');
});
