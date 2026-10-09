// M0 reference-validator tests; synthetic mutations are negative controls, NOT provider GET.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateMigrationManifest} from './validate-migration-manifest-v1.mjs';

const baseline = JSON.parse(readFileSync(new URL('./migration-manifest-v1.json', import.meta.url), 'utf8'));
const copy = () => structuredClone(baseline);
const fails = (manifest, code) => {
  const outcome = validateMigrationManifest(manifest);
  assert.equal(outcome.valid, false);
  assert.ok(outcome.errors.some(s => s.startsWith(code)), JSON.stringify(outcome));
  assert.equal(outcome.writer_authorization, 'NOT_GRANTED');
  assert.equal(outcome.reviewer_authority, 'NOT_QUALIFIED');
};

test('positive: provider-referenced manifest structurally consistent, never authenticated', () => {
  const out = validateMigrationManifest(copy());
  assert.deepEqual(out.errors, []);
  assert.equal(out.valid,true);
  assert.equal(out.provider_identity,'CALLER_REFERENCED_NOT_LIVE_ATTESTED');
  assert.equal(out.owner_authority,'NOT_AUTHENTICATED');
  assert.equal(out.programme_acceptance,'NOT_EVALUATED');
});
test('same repository ID or slug is not a migration', () => {
  const v = copy(); v.repositories.destination.repository_id = v.repositories.historical.repository_id;
  fails(v,'IDENTICAL_REPOSITORY_NOT_MIGRATION');
  const w = copy(); w.repositories.destination.full_name = w.repositories.historical.full_name;
  fails(w,'IDENTICAL_REPOSITORY_NOT_MIGRATION');
});
test('no old-only issue may be assigned a destination by fabricated URL', () => {
  const v = copy(); v.objects[0].destination = {repository_id:1412133785,number:787,url:'https://github.com/reallakshman19/Common/issues/787'};
  fails(v,'HISTORICAL_ONLY_HAS_DESTINATION');
});
test('no cross-repo historical URL promoted to new issue authority', () => {
  const v = copy(); v.objects[6].destination.url='https://github.com/reallaksh19/Common/issues/1';
  fails(v,'DESTINATION_NAMESPACE_MISMATCH');
});
test('no old provider repository ID promoted to current destination', () => {
  const v = copy(); v.objects[6].destination.repository_id=1207996454;
  fails(v,'DESTINATION_NAMESPACE_MISMATCH');
});
test('PR namespace cannot use issue path or wrong native PR number', () => {
  const v = copy(); v.objects[9].destination.url='https://github.com/reallakshman19/Common/issues/3';
  fails(v,'DESTINATION_NAMESPACE_MISMATCH');
  const w = copy(); w.objects[9].destination.number=2;
  fails(w,'DESTINATION_NAMESPACE_MISMATCH');
});
test('no duplicate source or destination references', () => {
  const v = copy(); v.objects.push(structuredClone(v.objects[0]));
  fails(v,'DUPLICATE_ORIGIN');
  const w = copy(); w.objects[9].destination=structuredClone(w.objects[8].destination);
  fails(w,'DUPLICATE_DESTINATION');
});
test('no review, writer or acceptance escalation', () => {
  const v=copy(); v.trust_gates.accepted_programme_acs=8;
  fails(v,'FORGED_AUTHORITY_OR_PROGRESS');
  const w=copy(); w.trust_gates.live_publisher='ON';
  fails(w,'FORGED_AUTHORITY_OR_PROGRESS');
  const x=copy(); x.objects[8].authority='TRANSFERRED';
  fails(x,'BAD_OBJECT_SHAPE');
});
test('source SHA equality and head advancement cannot be misclassified', () => {
  const v=copy(); v.branches[2].relation='EXACT_HEAD_MATCH';
  fails(v,'UNVERIFIED_HEAD_CHANGE_CLASSIFICATION');
  const w=copy(); w.branches[0].ahead_commits=1;
  fails(w,'FALSE_EXACT_HEAD_CLASSIFICATION');
});
test('branch mismatch, absent PR and duplicate branch all fail closed', () => {
  const v=copy(); v.branches[0].origin_head_sha='BAD_SHA';
  fails(v,'BAD_BRANCH_SHAPE');
  const w=copy(); w.branches[0].origin_pr=666;
  fails(w,'BRANCH_WITHOUT_ORIGIN_PR');
  const x=copy(); x.branches.push(structuredClone(x.branches[0]));
  fails(x,'DUPLICATE_BRANCH');
});
test('unsupported relations and unexpected authority field are rejected', () => {
  const v=copy(); v.objects[6].relation='REVIEW_TRANSFERRED';
  fails(v,'UNAUTHORIZED_RELATION');
  const w=copy(); w.objects[6].approved=true;
  fails(w,'BAD_OBJECT_SHAPE');
  const x=copy(); x.publisher_authorization=true;
  fails(x,'BAD_ROOT_SHAPE');
});
