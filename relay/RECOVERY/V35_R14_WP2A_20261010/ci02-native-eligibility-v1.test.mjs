import test from 'node:test';
import assert from 'node:assert/strict';
import {parseCi02NativeEnvelope} from './ci02-native-eligibility-v1.mjs';
const good=()=>({GITHUB_EVENT_NAME:'pull_request',
  CANDIDATE_REPOSITORY:'reallakshman19/Common',
  CANDIDATE_HEAD_REPO:'reallakshman19/Common',
  CANDIDATE_PR_NUMBER:'331',CANDIDATE_HEAD_SHA:'a'.repeat(40),
  CANDIDATE_BASE_REF:'codex/294-t38-immutable-pr308-fixture-6acb041f'});
test('CI02 current in-repo PR/head/base envelope is bounded read-only input',()=>{
  assert.deepEqual(parseCi02NativeEnvelope(good()),{pr:331,sha:'a'.repeat(40),
    base:'codex/294-t38-immutable-pr308-fixture-6acb041f',
    repository:'reallakshman19/Common'});
});
test('CI02 old repository, forked head and event spoof cannot enter native probe',()=>{
  for(const x of [
    {CANDIDATE_REPOSITORY:'reallaksh19/Common'},
    {CANDIDATE_HEAD_REPO:'fork/Common'},
    {GITHUB_EVENT_NAME:'workflow_dispatch'},
    {GITHUB_EVENT_NAME:''}
  ])assert.equal(parseCi02NativeEnvelope({...good(),...x}),null);
});
test('CI02 missing/malformed PR number or ref fails closed',()=>{
  for(const x of [
    {CANDIDATE_PR_NUMBER:'0'}, {CANDIDATE_PR_NUMBER:'NaN'},
    {CANDIDATE_PR_NUMBER:'331.1'}, {CANDIDATE_HEAD_SHA:'b'.repeat(39)},
    {CANDIDATE_HEAD_SHA:'B'.repeat(40)},
    {CANDIDATE_BASE_REF:'../main'},
    {CANDIDATE_BASE_REF:'refs//heads/main'},
    {CANDIDATE_BASE_REF:'topic/'}
  ])assert.equal(parseCi02NativeEnvelope({...good(),...x}),null);
});
test('CI02 validation cannot mint admission/writer/projection',()=>{
  const r=parseCi02NativeEnvelope(good());
  assert.equal('evidence_admitted' in r,false);
  assert.equal('delp_projector_invoked' in r,false);
  assert.equal('writer_authorized' in r,false);
  assert.equal('owner_authenticated' in r,false);
});
