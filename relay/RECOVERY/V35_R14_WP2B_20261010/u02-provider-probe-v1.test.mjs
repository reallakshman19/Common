import test from 'node:test';
import assert from 'node:assert/strict';
import {probeU02NativeEndpoints} from './u02-provider-probe-v1.mjs';
const HEAD='a'.repeat(40),R='reallakshman19/Common',BRANCH='recovery/5-wp2b-b01-b03-pre-admission-20261010';
const locator=()=>({repository:R,repository_id:1412133785,pr_number:292,
 candidate_head_sha:HEAD,base_branch:BRANCH});
const good={
 PR_IDENTITY:{number:292,head:{sha:HEAD},base:{ref:BRANCH}},
 SELECTED_CHECK_RUNS:{total_count:1,check_runs:[{id:17,head_sha:HEAD,name:'build',status:'completed',conclusion:'success',app:{id:42}}]},
 COMBINED_STATUS:{sha:HEAD,statuses:[]},
 CLASSIC_POLICY:{contexts:[],checks:[]},BRANCH_RULES:[],
};
const sequence=['PR_IDENTITY','SELECTED_CHECK_RUNS','COMBINED_STATUS','CLASSIC_POLICY','BRANCH_RULES'];
function fixture(overrides={}){
 const routes=Object.fromEntries(sequence.map((kind,i)=>[kind,overrides[kind]??{status:200,data:good[kind]}]));
 let n=0;
 return async function req(url,opts){
  assert.equal(opts.method,'GET');assert.equal(opts.redirect,'error');
  assert.equal(new URL(url).origin,'https://api.github.com');
  assert.equal(opts.headers.Authorization,undefined);
  let kind=sequence[n++];assert.ok(kind,'extra request');
  let row=routes[kind];if(row.throw)throw Error('SECRET PRIVATE TOKEN');
  return {url,status:row.status,redirected:false,headers:{get:()=>row.link??null},
   text:async()=>JSON.stringify(row.data)};
 };
}
const checkHold=o=>{
 assert.equal(o.basis,'INDEPENDENT_POST_FAILURE_NON_ATOMIC_HTTP_PROBE');
 assert.equal(o.admission,'NOT_ADMITTED');assert.equal(o.evidence_admitted,false);
 assert.equal(o.required_ci_qualified,false);assert.equal(o.writer_authorized,false);
 assert.equal(o.programme_progress,null);assert.equal(o.delp_projector_invoked,false);
};
test('all endpoint shapes valid still NO required CI verdict or admission',async()=>{
 const o=await probeU02NativeEndpoints(locator(),{request:fixture()});checkHold(o);
 assert.deepEqual(o.readings.map(x=>x.endpoint),sequence);
 assert.deepEqual(o.readings.map(x=>x.shape),['MATCH','SHAPE_COMPATIBLE','SHAPE_COMPATIBLE','SHAPE_COMPATIBLE','SHAPE_COMPATIBLE']);
 assert.equal(JSON.stringify(o).includes('build'),false);
});
test('missing classic policy is explicitly FORBIDDEN, never zero required checks',async()=>{
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({CLASSIC_POLICY:{status:403}})});checkHold(o);
 assert.deepEqual(o.readings[3],{endpoint:'CLASSIC_POLICY',http:'FORBIDDEN',shape:'NOT_READ'});
});
test('selected check paging of >100 is a recognizable fail-closed reason',async()=>{
 const d={total_count:101,check_runs:good.SELECTED_CHECK_RUNS.check_runs};
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({SELECTED_CHECK_RUNS:{status:200,data:d}})});checkHold(o);
 assert.equal(o.readings[1].shape,'PAGINATED_OR_INCOMPLETE');
});
test('same SHA is required for selected check input',async()=>{
 const d={total_count:1,check_runs:[{...good.SELECTED_CHECK_RUNS.check_runs[0],head_sha:'b'.repeat(40)}]};
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({SELECTED_CHECK_RUNS:{status:200,data:d}})});checkHold(o);
 assert.equal(o.readings[1].shape,'SHAPE_OR_HEAD_MISMATCH');
});
test('head moving during verification reports identity mismatch',async()=>{
 const d={number:292,head:{sha:'b'.repeat(40)},base:{ref:BRANCH}};
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({PR_IDENTITY:{status:200,data:d}})});checkHold(o);
 assert.equal(o.readings[0].shape,'MISMATCH');
});
test('rate-limited source and thrown secret are never exposed',async()=>{
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({COMBINED_STATUS:{status:429},CLASSIC_POLICY:{throw:true}})});checkHold(o);
 assert.equal(o.readings[2].http,'RATE_LIMITED');assert.equal(o.readings[3].http,'TRANSPORT_UNKNOWN');
 assert.ok(!JSON.stringify(o).includes('PRIVATE TOKEN'));
});
test('malformed rule JSON is not silently treated as no rules',async()=>{
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({BRANCH_RULES:{status:200,data:{rules:[]}}})});checkHold(o);
 assert.equal(o.readings[4].shape,'MALFORMED');
});
test('GitHub Link next marks check-run data incomplete',async()=>{
 const o=await probeU02NativeEndpoints(locator(),{request:fixture({SELECTED_CHECK_RUNS:{status:200,data:good.SELECTED_CHECK_RUNS,link:'<next>; rel="next"'}})});checkHold(o);
 assert.equal(o.readings[1].shape,'PAGINATED_OR_INCOMPLETE');
});
test('invalid new-repository, unsafe branch, missing SHA never issues GET',async()=>{
 for(const l of [{...locator(),repository:'reallaksh19/Common'},
  {...locator(),base_branch:'x/../evil'},{...locator(),candidate_head_sha:'bad'}]){
  let calls=0;const o=await probeU02NativeEndpoints(l,{request:()=>{calls++;throw Error('FAIL');}});checkHold(o);
  assert.equal(calls,0);assert.equal(o.readings[0].shape,'INVALID_INPUT');
 }
});
