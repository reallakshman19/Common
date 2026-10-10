import test from 'node:test';
import assert from 'node:assert/strict';
import {
 HISTORICAL_SHA,HISTORICAL_PR,HISTORICAL_REPO,HISTORICAL_ROUTE,
 t28PinnedTerminalNegative,t28ReadHistoricalFailure,
} from './t28-pinned-terminal-negative.mjs';

const row=(name,id,head_sha=HISTORICAL_SHA,status='completed',conclusion='failure')=>({
 id,name,head_sha,app:{id:15368},status,conclusion,
});
const v31=()=>row('validate-v3-1-foundation',114313557296);
const u02=()=>row('live-selected-required-ci (windows-latest)',114313556975);
const response=(runs)=>({status:200,page_complete:true,data:{total_count:runs.length,check_runs:runs}});
const expected=response([v31(),u02()]);

test('T28 pinned immutable old PR319 head and explicit route, no current PR head implied',()=>{
 assert.equal(HISTORICAL_PR,319);
 assert.equal(HISTORICAL_REPO,'reallakshman19/Common');
 assert.equal(HISTORICAL_SHA,'1db18083b70005b6e228b3f40a5c206424c9704d');
 assert.equal(HISTORICAL_ROUTE,'commits/'+HISTORICAL_SHA+'/check-runs?per_page=100');
});
test('T28 two exact completed historical check IDs give negative-only witness',()=>{
 const x=t28PinnedTerminalNegative(expected);
 assert.equal(x.witness,'TWO_PINNED_HISTORICAL_FAILURES_VERIFIED');
 assert.deepEqual(x.witnessed_check_ids,[114313556975,114313557296]);
 assert.equal(x.relationship,'HISTORICAL_PREVIOUS_HEAD_NOT_CURRENT');
 assert.equal(x.evidence_admitted,false);
 assert.equal(x.delp_projection,'NOT_CALCULATED');
 assert.equal(x.required_ci_qualified,false);
 assert.equal(x.release_ready,false);
 assert.equal(x.writer_authorized,false);
});
test('T28 one failure absent, successful, pending or cancelled never satisfies golden negative witness',()=>{
 const candidates=[
 response([v31()]),
 response([v31(),row('live-selected-required-ci (windows-latest)',114313556975,HISTORICAL_SHA,'completed','success')]),
 response([v31(),row('live-selected-required-ci (windows-latest)',114313556975,HISTORICAL_SHA,'in_progress',null)]),
 response([v31(),row('live-selected-required-ci (windows-latest)',114313556975,HISTORICAL_SHA,'completed','cancelled')]),
 ];
 for(const resp of candidates){
  const x=t28PinnedTerminalNegative(resp);
  assert.equal(x.witness,'NOT_VERIFIED');
  assert.equal(x.evidence_admitted,false);
 }
});
test('T28 stale SHA or corrupted check-run app identity invalidates entire snapshot',()=>{
 for(const runs of [
  [v31(),u02().constructor===Object?{...u02(),head_sha:'b'.repeat(40)}:u02()],
  [v31(),{...u02(),app:{id:'forged'}}],
 ]){
  const x=t28PinnedTerminalNegative(response(runs));
  assert.equal(x.witness,'NOT_VERIFIED');
  assert.equal(x.observed_check_count,0);
 }
});
test('T28 incomplete page and inconsistent total count never prove failures',()=>{
 const paginated={...expected,page_complete:false};
 assert.equal(t28PinnedTerminalNegative(paginated).witness,'NOT_VERIFIED');
 const mismatch={...expected,data:{...expected.data,total_count:3}};
 assert.equal(t28PinnedTerminalNegative(mismatch).witness,'NOT_VERIFIED');
 const forbidden={...expected,status:403};
 assert.equal(t28PinnedTerminalNegative(forbidden).witness,'NOT_VERIFIED');
});
test('T28 provider exception redaction and route identity are enforced',async()=>{
 const x=await t28ReadHistoricalFailure(async ()=>{throw Error('TOP_SECRET_PROVIDER_TOKEN')});
 assert.equal(x.witness,'NOT_VERIFIED');
 assert.ok(!JSON.stringify(x).includes('TOP_SECRET_PROVIDER_TOKEN'));
 const y=await t28ReadHistoricalFailure(async (repo,route)=>{
  assert.equal(repo,HISTORICAL_REPO);
  assert.equal(route,HISTORICAL_ROUTE);
  return expected;
 });
 assert.equal(y.witness,'TWO_PINNED_HISTORICAL_FAILURES_VERIFIED');
});
test('T28 unknown private check details are never emitted to the user',()=>{
 const secret='SECRET_PROPRIETARY_CHECK_NAME';
 const x=t28PinnedTerminalNegative(response([...expected.data.check_runs,
  row(secret,995599)]));
 assert.equal(x.witness,'TWO_PINNED_HISTORICAL_FAILURES_VERIFIED');
 assert.ok(!JSON.stringify(x).includes(secret));
 assert.equal(x.evidence_admitted,false);
});
test('T28 duplicate check-run ID and wrong expected name both fail closed',()=>{
 const dup=t28PinnedTerminalNegative(response([v31(),u02(),u02()]));
 assert.equal(dup.witness,'NOT_VERIFIED');
 const renamed=t28PinnedTerminalNegative(response([v31(),{...u02(),name:'different'}]));
 assert.equal(renamed.witness,'NOT_VERIFIED');
});
