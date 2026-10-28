import test from 'node:test';
import assert from 'node:assert/strict';
import {reconcileGitHubFacts as read,ProviderFactsError,hasNativeProviderAcquisition} from './provider-facts-v1.mjs';
const REPO='reallaksh19/Common',SHA='a'.repeat(40),BASE='b'.repeat(40);
const WF='.github/workflows/relay-reset-provider-facts.yml',NOW='2026-10-08T18:30:00.000Z';
const scope=(n=830)=>({repository:REPO,parent_issue:787,child_issues:[833],
  pull_requests:[{number:n,expected_head_sha:SHA}],workflow_paths:[WF]});
const api=endpoint=>'https://api.github.com/repos/'+REPO+'/'+endpoint;
const issue=n=>({number:n,url:api('issues/'+n),
  html_url:'https://github.com/'+REPO+'/issues/'+n,
  state:'open',title:'[MANUAL] agent claims no accepted evidence',
  created_at:'2026-10-08T16:00:00Z',updated_at:'2026-10-08T18:00:00Z',
  body:'Agent-authored title and body claim ACCEPTED 8/8'});
const pr=(n=830,head=SHA)=>({number:n,url:api('pulls/'+n),
  html_url:'https://github.com/'+REPO+'/pull/'+n,
  state:'open',title:'[8/8 COMPLETED] agent asserts review granted',
  draft:true,merged:false,created_at:'2026-10-08T16:00:00Z',
  updated_at:'2026-10-08T18:00:00Z',
  head:{sha:head,ref:'feat/stacked',repo:{full_name:REPO}},
  base:{sha:BASE,ref:'main',repo:{full_name:REPO}},
  body:'We wrote all files and approved privacy and reviews'});
const workflow=(head=SHA,path=WF,status='completed',conclusion='success',id=190)=>({
  id,head_sha:head,path:path+'@refs/pull/830/merge',
  html_url:'https://github.com/'+REPO+'/actions/runs/'+id,
  status,conclusion,created_at:'2026-10-08T18:15:00Z'});
const runs=(r=[workflow()])=>({total_count:r.length,workflow_runs:r});
function mock(s,changes={}){
  const urls=[],prefix=api('');
  let prReads=0;
  const fetchImpl=async url=>{
    urls.push(url);
    const endpoint=url.slice(prefix.length);
    const issueNum=endpoint.startsWith('issues/')?Number(endpoint.split('/')[1]):null;
    const prNum=endpoint.startsWith('pulls/')?Number(endpoint.split('/')[1]):null;
    let payload=issueNum?issue(issueNum):prNum?pr(prNum):runs();
    if(issueNum)payload=changes['issue'+issueNum]??payload;
    if(prNum){
      prReads++;
      payload=(prReads>1?changes['prRecheck'+prNum]:undefined)??
        changes['pr'+prNum]??payload;
    }
    if(endpoint.startsWith('actions/'))payload=changes.runs??payload;
    return {url:changes.responseUrl??url,status:changes.httpStatus??200,
      redirected:changes.redirected??false,headers:{get:()=>null},
      text:async()=>JSON.stringify(payload)};
  };
  return {fetchImpl,urls};
}
async function observed(s=scope(),changes={}){
  const t=mock(s,changes);
  return {result:await read(s,{fetchImpl:t.fetchImpl,observedAt:NOW}),urls:t.urls};
}
const refuses=(p,code)=>assert.rejects(p,e=>e instanceof ProviderFactsError&&e.code===code);

test('one bounded native-source scope produces issue/PR/current-head CI facts',async()=>{
  const {result:r,urls}=await observed();
  assert.equal(r.schema,'relay-provider-facts-v1');
  assert.equal(r.actual_next,'UNDETERMINED_PROVIDER_ONLY_REQUIRES_LINEAGE_AND_ACCEPTED_EVIDENCE');
  assert.equal(r.parent_issue.number,787);
  assert.equal(r.child_issues[0].number,833);
  assert.equal(r.pr_facts[0].head_sha,SHA);
  assert.equal(r.pr_facts[0].currentness,'MATCH');
  assert.equal(r.pr_facts[0].ci_workflows[0].state,'PASS');
  assert.deepEqual(urls,[api('issues/787'),api('issues/833'),api('pulls/830'),
    api('actions/runs?head_sha='+SHA+'&per_page=100'),
    api('pulls/830')]);
  assert.equal(r.read_count,5);
  assert.equal(r.consistency,'PR_DOUBLE_READ_NON_ATOMIC');
  assert.equal(r.source_state,'INJECTED_UNVERIFIED');
  assert.equal(hasNativeProviderAcquisition(r),false);
  assert.equal(hasNativeProviderAcquisition(JSON.parse(JSON.stringify(r))),false);
  assert.equal(r.relationship_assertion,'CALLER_SCOPED_UNVERIFIED');
  assert.equal(r.evidence_acceptance,'NOT_EVALUATED');
  assert.equal(r.human_review,'NOT_EVALUATED');
  assert.equal(r.authorization_granted,false);
  assert.equal(r.live_writer_enabled,false);
  assert.equal(r.independently_accepted,false);
  assert.match(r.snapshot_sha256,/^[0-9a-f]{64}$/);
  assert.equal(JSON.stringify(r).includes('We wrote all files'),false);
  assert.equal(JSON.stringify(r).includes('Agent-authored title and body'),false);
});
test('nested issue/PR/CI objects are immutable under the published digest',async()=>{
  const r=(await observed()).result;
  for(const target of [r,r.parent_issue,r.child_issues,r.child_issues[0],
    r.pr_facts,r.pr_facts[0],r.pr_facts[0].ci_workflows,
    r.pr_facts[0].ci_workflows[0]])assert.equal(Object.isFrozen(target),true);
  const digest=r.snapshot_sha256;
  assert.throws(()=>{r.pr_facts[0].ci_workflows[0].state='PASS_INVENTED';},TypeError);
  assert.throws(()=>{r.child_issues.push(issue(99));},TypeError);
  assert.equal(r.snapshot_sha256,digest);
});
test('fixed observed_at and identical provider data give deterministic snapshot digest',async()=>{
  assert.equal((await observed()).result.snapshot_sha256,(await observed()).result.snapshot_sha256);
});
test('forged issue and PR titles do not promote acceptance',async()=>{
  const {result:r}=await observed();
  assert.match(r.pr_facts[0].title,/8\/8 COMPLETED/);
  assert.equal(r.independently_accepted,false);
  assert.equal(r.evidence_acceptance,'NOT_EVALUATED');
});
test('wrong issue ID, source URL or backwards dates REFUTED',async()=>{
  const s=scope();
  await refuses(read(s,{fetchImpl:mock(s,{issue787:{...issue(787),number:999}}).fetchImpl}),'REFUTED');
  await refuses(read(s,{fetchImpl:mock(s,{issue833:{...issue(833),html_url:'https://evil.invalid/833'}}).fetchImpl}),'REFUTED');
  await refuses(read(s,{fetchImpl:mock(s,{issue787:{...issue(787),updated_at:'2010-01-01T00:00:00Z'}}).fetchImpl}),'REFUTED');
});
test('repo-transplanted PR and contradictory open+merged REFUTED',async()=>{
  const s=scope();
  await refuses(read(s,{fetchImpl:mock(s,{pr830:{...pr(),head:{...pr().head,repo:{full_name:'attacker/Repo'}}}}).fetchImpl}),'REFUTED');
  await refuses(read(s,{fetchImpl:mock(s,{pr830:{...pr(),url:'https://api.github.com/repos/evil/a/pulls/830'}}).fetchImpl}),'REFUTED');
  await refuses(read(s,{fetchImpl:mock(s,{pr830:{...pr(),merged:true}}).fetchImpl}),'REFUTED');
});
test('a PR head force-push during the CI GET cannot publish a mixed-current snapshot',async()=>{
  const s=scope();
  await refuses(read(s,{fetchImpl:mock(s,{prRecheck830:pr(830,BASE)}).fetchImpl}),'STALE');
});
test('a PR draft, merged, title or base mutation mid-read fails closed',async()=>{
  const s=scope();
  for(const changed of [
    {...pr(),draft:false},{...pr(),title:'MOVED'},
    {...pr(),state:'closed',merged:true},
    {...pr(),base:{...pr().base,sha:'c'.repeat(40)}}
  ])await refuses(read(s,{fetchImpl:mock(s,{prRecheck830:changed}).fetchImpl}),'STALE');
});
test('child issue endpoint cannot silently accept a PR object as an issue',async()=>{
  const s=scope();
  await refuses(read(s,{fetchImpl:mock(s,{issue833:{...issue(833),pull_request:{url:api('pulls/833')}}}).fetchImpl}),'REFUTED');
});
test('forged or prefix-only Actions run URL and contradictory count never certify CI',async()=>{
  const s=scope();
  const bad={...workflow(),html_url:'https://github.com/'+REPO+'/actions/runs/190/evil'};
  await refuses(read(s,{fetchImpl:mock(s,{runs:runs([bad])}).fetchImpl}),'REFUTED');
  await refuses(read(s,{fetchImpl:mock(s,{runs:{total_count:0,workflow_runs:[workflow()]}}).fetchImpl}),'REFUTED');
});
test('stale expected head visible, no independently accepted evidence',async()=>{
  const s=scope();s.pull_requests[0].expected_head_sha=BASE;
  const {result:r}=await observed(s);
  assert.equal(r.pr_facts[0].currentness,'STALE');
  assert.equal(r.independently_accepted,false);
});
test('CI on other head or different workflow never gets PASS',async()=>{
  const s=scope();
  assert.equal((await observed(s,{runs:runs([workflow(BASE)])})).result.pr_facts[0].ci_workflows[0].state,'UNKNOWN');
  assert.equal((await observed(s,{runs:runs([workflow(SHA,'.github/workflows/unrelated.yml')])})).result.pr_facts[0].ci_workflows[0].state,'UNKNOWN');
});
test('queued, failure, cancelled and success represent only provider CI state',async()=>{
  const s=scope();
  for(const [status,conclusion,want] of [
    ['queued',null,'PENDING'],['in_progress',null,'PENDING'],
    ['completed','failure','FAIL'],['completed','cancelled','FAIL'],
    ['completed','success','PASS']]){
    const r=(await observed(s,{runs:runs([workflow(SHA,WF,status,conclusion)])})).result;
    assert.equal(r.pr_facts[0].ci_workflows[0].state,want);
    assert.equal(r.independently_accepted,false);
  }
});
test('pagination over 100 runs is UNKNOWN not a fabricated zero',async()=>{
  const s=scope(),c=runs([workflow()]);c.total_count=101;
  const r=(await observed(s,{runs:c})).result;
  assert.equal(r.pr_facts[0].ci_workflows[0].state,'UNKNOWN');
  assert.equal(r.pr_facts[0].ci_workflows[0].reason,'UNREAD_PAGINATED_RESULTS');
});
test('newer same-head failure overrules older same-head success',async()=>{
  const newer={...workflow(SHA,WF,'completed','failure',191),created_at:'2026-10-08T18:20:00Z'};
  const r=(await observed(scope(),{runs:runs([workflow(),newer])})).result;
  assert.equal(r.pr_facts[0].ci_workflows[0].state,'FAIL');
  assert.equal(r.pr_facts[0].ci_workflows[0].run_id,191);
});
test('redirects, missing provider, rate limit, malformed JSON never PASS',async()=>{
  const s=scope();
  for(const status of [301,404,429,500])
    await refuses(read(s,{fetchImpl:mock(s,{httpStatus:status}).fetchImpl}),'UNKNOWN');
  await refuses(read(s,{fetchImpl:mock(s,{redirected:true}).fetchImpl}),'UNKNOWN');
  await refuses(read(s,{fetchImpl:mock(s,{responseUrl:'https://evil.invalid/path'}).fetchImpl}),'UNKNOWN');
  await refuses(read(s,{fetchImpl:async()=>{throw Error('network')}}),'UNKNOWN');
  await refuses(read(s,{fetchImpl:async url=>({status:200,url,redirected:false,
    headers:{get:()=>null},text:async()=>'{malformed'})}),'UNKNOWN');
});
test('oversized API response rejected before rendering snapshot',async()=>{
  const s=scope();
  await refuses(read(s,{fetchImpl:async url=>({status:200,url,redirected:false,
    headers:{get:()=>String(3000000)},text:async()=>''})}),'UNKNOWN');
});
test('unexpected grants, duplicate PRs and children and moving refs rejected',async()=>{
  const s=scope();
  await refuses(read({...s,authorization_granted:true}),'INVALID');
  await refuses(read({...s,pull_requests:[...s.pull_requests,...s.pull_requests]}),'INVALID');
  await refuses(read({...s,child_issues:[833,833]}),'INVALID');
  await refuses(read({...s,pull_requests:[{number:830,expected_head_sha:'main'}]}),'INVALID');
  await refuses(read(s,{fetchImpl:mock(s).fetchImpl,writeToken:'abc'}),'INVALID');
});
test('workflow path escape and duplicate workflow paths rejected',async()=>{
  const s=scope();s.workflow_paths=['../evil.yml'];await refuses(read(s),'INVALID');
  const t=scope();t.workflow_paths=[WF,WF];await refuses(read(t),'INVALID');
});
test('manual title cannot change actual draft/merged state',async()=>{
  const r=(await observed(scope(),{pr830:{...pr(),title:'MERGED ACCEPTED 8/8'}})).result;
  assert.equal(r.pr_facts[0].state,'open');
  assert.equal(r.pr_facts[0].draft,true);
  assert.equal(r.pr_facts[0].merged,false);
});
test('actual native current parent/child/PR-head/Actions observation',
  {skip:!process.env.RELAY_R3_CI_HEAD_SHA},async()=>{
  const sha=process.env.RELAY_R3_CI_HEAD_SHA,n=Number(process.env.RELAY_R3_CI_PR_NUMBER);
  assert.match(sha,/^[0-9a-f]{40}$/);assert.ok(n>0);
  const s=scope(n);s.pull_requests[0].expected_head_sha=sha;
  const result=await read(s,{readToken:process.env.RELAY_R3_TOKEN||undefined});
  assert.equal(result.source_state,'PROVIDER_OBSERVED');
  // Native origin is an in-process R3 capability, never a replayed JSON label.
  assert.equal(hasNativeProviderAcquisition(result),true);
  assert.equal(hasNativeProviderAcquisition(JSON.parse(JSON.stringify(result))),false);
  assert.equal(result.parent_issue.number,787);
  assert.equal(result.child_issues[0].number,833);
  assert.equal(result.pr_facts[0].number,n);
  assert.equal(result.pr_facts[0].head_sha,sha);
  assert.equal(result.pr_facts[0].currentness,'MATCH');
  assert.equal(typeof result.pr_facts[0].draft,'boolean'); // native observed draft/ready, not assumed
  assert.equal(result.pr_facts[0].merged,false);
  assert.equal(result.authorization_granted,false);
  assert.equal(result.independently_accepted,false);
  console.log('R3_NATIVE_PROVIDER_FACTS '+JSON.stringify({
    head_sha:sha,pr_number:n,parent:result.parent_issue.number,
    child:result.child_issues[0].number,
    ci_state:result.pr_facts[0].ci_workflows[0].state,
    digest:result.snapshot_sha256,provider:result.source_state,
    human_review:result.human_review,acceptance:false}));
});
