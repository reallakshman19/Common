/* Reconstructed observations from exact-head GitHub Actions stdout, NOT native GETs.
 * Provenance: H9 Windows #114164209436 (both UNKNOWN),
 * H10 Windows #114169711626 (UNKNOWN then coherent),
 * H10 Ubuntu #114169711565 (coherent at first attempt).
 * This is a regression for existing retry + smoke-refusal code, not CI acceptance.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {observeNativeWithUnknownRetry} from './native-read-retry-v1.mjs';
import {qualifiesNegativeSmoke} from './native-smoke-config-v1.mjs';
const LOCATOR=Object.freeze({repository:'reallakshman19/Common',pr_number:292});
const hold=(kind,digest)=>Object.freeze({
  schema:'common-v35-r12-u3-delp-pre-admission-v1',
  source_status:kind,
  source_digest:digest,
  observation_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION',
  admission:'NOT_ADMITTED',
  admission_blockers:kind==='UNKNOWN'?['CROSS_SOURCE_NOT_VERIFIED']:
   ['REQUIRED_CI_NOT_QUALIFIED','EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN',
    'EVIDENCE_POLICY_VERSION_NOT_ADOPTED','U3_POSITIVE_ADMISSION_NOT_IMPLEMENTED'],
  evidence_admitted:false,owner_authenticated:false,reviewer_qualified:false,
  delp_projector_invoked:false,programme_progress:null,writer_authorized:false,
});
const unknown=hold('UNKNOWN',null);
const windowsCoherent=hold('REFERENCES_COHERENT_BUT_UNADMITTED',
  'sha256:cf71160beee1df0b834a420fd3c16213246142b367fcf72d45e82e2c73f617c3');
const ubuntuCoherent=hold('REFERENCES_COHERENT_BUT_UNADMITTED',
  'sha256:078e62b03bf8436b9979615fb8e6ed056f66b27a25d6519938afd1913265195b');
async function replay(observations){
  const inputs=[...observations],log=[];let count=0;
  const final=await observeNativeWithUnknownRetry(LOCATOR,async got=>{
    assert.equal(got,LOCATOR);count++;return inputs.shift();
  },line=>log.push(JSON.parse(line)));
  return {final,log,count,remaining:inputs.length};
}
const neverAdmitted=x=>{
  assert.equal(x.admission,'NOT_ADMITTED');assert.equal(x.evidence_admitted,false);
  assert.equal(x.writer_authorized,false);assert.equal(x.programme_progress,null);
  assert.equal(x.delp_projector_invoked,false);
};
test('H9 Windows incident: two UNKNOWN native observations stay hard HOLD',async()=>{
  const r=await replay([unknown,unknown]);
  assert.equal(r.count,2);assert.equal(r.remaining,0);
  assert.deepEqual(r.log.map(x=>x.native_read_attempt),[1,2]);
  assert.deepEqual(r.log.map(x=>x.source_status),['UNKNOWN','UNKNOWN']);
  assert.equal(r.final.source_digest,null);neverAdmitted(r.final);
  assert.equal(qualifiesNegativeSmoke(r.final,'HISTORICAL_STALE'),false);
});
test('H10 Windows incident: UNKNOWN then coherent consumes bounded retry only',async()=>{
  const r=await replay([unknown,windowsCoherent]);
  assert.equal(r.count,2);assert.equal(r.remaining,0);
  assert.deepEqual(r.log.map(x=>x.native_read_attempt),[1,2]);
  assert.deepEqual(r.log.map(x=>x.source_status),
    ['UNKNOWN','REFERENCES_COHERENT_BUT_UNADMITTED']);
  assert.equal(r.final.source_digest,windowsCoherent.source_digest);
  neverAdmitted(r.final);
  assert.equal(qualifiesNegativeSmoke(r.final,'HISTORICAL_STALE'),true);
  assert.equal(qualifiesNegativeSmoke(r.final,'CURRENT_AUTHOR_CLAIM'),false);
});
test('H10 Ubuntu incident: coherent at first attempt, no extra source GET',async()=>{
  const r=await replay([ubuntuCoherent,unknown]);
  assert.equal(r.count,1);assert.equal(r.remaining,1);
  assert.deepEqual(r.log.map(x=>x.native_read_attempt),[1]);
  neverAdmitted(r.final);
  assert.equal(qualifiesNegativeSmoke(r.final,'HISTORICAL_STALE'),true);
});
test('a previously successful retry cannot launder the author policy or writer',async()=>{
  const payload={...windowsCoherent,admission:'ADMITTED',evidence_admitted:true,
   owner_authenticated:true,writer_authorized:true,programme_progress:100};
  const r=await replay([unknown,payload]);
  assert.equal(r.count,2);
  // The retry helper is transport-only; the actual CLI gate MUST reject it.
  assert.equal(r.final.admission,'ADMITTED');
  assert.equal(qualifiesNegativeSmoke(r.final,'HISTORICAL_STALE'),false);
});
