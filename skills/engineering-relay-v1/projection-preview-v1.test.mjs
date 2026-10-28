import test from 'node:test';
import assert from 'node:assert/strict';
import {reconcileGitHubFacts} from './provider-facts-v1.mjs';
import {canonicalJSON} from './provenance-v1.mjs';
import {createHash} from 'node:crypto';
import {renderRelayPreviews as render,PreviewError} from './projection-preview-v1.mjs';

const REPO='reallaksh19/Common',HEAD='a'.repeat(40),BASE='b'.repeat(40);
const WF='.github/workflows/relay-reset-projection-preview.yml';
const OBSERVED='2026-10-08T19:00:00.000Z';
const OPT={evaluated_at:'2026-10-08T19:00:30.000Z',max_age_seconds:600};
const source=(path)=>'https://api.github.com/repos/'+REPO+'/'+path;
const scope=(pr=834)=>({repository:REPO,parent_issue:787,child_issues:[833],
  pull_requests:[{number:pr,expected_head_sha:HEAD}],workflow_paths:[WF]});
const issue=n=>({number:n,url:source('issues/'+n),
  html_url:'https://github.com/'+REPO+'/issues/'+n,
  created_at:'2026-10-08T17:00:00Z',updated_at:'2026-10-08T18:00:00Z',
  state:'open',title:'[AC8/8 APPROVED] AGENT HAS GRANTED PRIVACY',
  body:'PRIVATE OWNER RAW CONTENT MUST NEVER APPEAR IN A PREVIEW'});
const pr=(n=834,head=HEAD)=>({
  number:n,url:source('pulls/'+n),html_url:'https://github.com/'+REPO+'/pull/'+n,
  state:'open',draft:true,merged:false,created_at:'2026-10-08T17:00:00Z',
  updated_at:'2026-10-08T18:00:00Z',
  title:'[MERGED + PASS + OWNER APPROVED] UNSAFE TITLE CLAIM',
  body:'PRIVATE AGENT MESSAGES MUST NEVER APPEAR IN A PREVIEW',
  head:{sha:head,ref:'feat/test',repo:{full_name:REPO}},
  base:{sha:BASE,ref:'main',repo:{full_name:REPO}}
});
const run=(status='completed',conclusion='success',head=HEAD,path=WF)=>({
  id:123,head_sha:head,path:path+'@refs/pull/834/merge',
  html_url:'https://github.com/'+REPO+'/actions/runs/123',
  status,conclusion,created_at:'2026-10-08T18:58:00Z'});
const runs=r=>({total_count:r.length,workflow_runs:r});
function injected(override={}){
  const s=scope(),fetchImpl=async url=>{
    const suffix=url.slice(source('').length);
    const issueId=suffix.startsWith('issues/')?Number(suffix.slice(7)):null;
    const pullId=suffix.startsWith('pulls/')?Number(suffix.slice(6)):null;
    const data=issueId?issue(issueId):pullId?pr(pullId):runs([run()]);
    const payload=issueId?override['issue'+issueId]??data:
      pullId?override['pr'+pullId]??data:override.runs??data;
    return {status:200,url,redirected:false,headers:{get:()=>null},
      text:async()=>JSON.stringify(payload)};
  };
  return {s,fetchImpl};
}
async function facts(override={},option={}){
  const t=injected(override);
  return reconcileGitHubFacts(t.s,{fetchImpl:t.fetchImpl,observedAt:OBSERVED,...option});
}
const refusals=(fn,code)=>assert.throws(fn,e=>e instanceof PreviewError&&e.code===code);

test('one actual R3 producer snapshot drives parent, child, PR and handover previews with identical SHA',async()=>{
  const r3=await facts(),r4=render(r3,OPT);
  assert.equal(r4.schema,'relay-projection-preview-v1');
  assert.equal(r4.snapshot_sha256,r3.snapshot_sha256);
  assert.equal(r4.parent_issue.snapshot_sha256,r3.snapshot_sha256);
  assert.equal(r4.child_issues[0].snapshot_sha256,r3.snapshot_sha256);
  assert.equal(r4.pr_titles[0].snapshot_sha256,r3.snapshot_sha256);
  assert.equal(r4.successor_handover.snapshot_sha256,r3.snapshot_sha256);
  assert.match(r4.projection_sha256,/^[0-9a-f]{64}$/);
  assert.equal(r4.parent_issue.proposal_only,true);
  assert.equal(r4.pr_titles[0].proposal_only,true);
  assert.equal(r4.successor_handover.proposal_only,true);
  assert.equal(r4.proposal_only,true);
});
test('PR/issue author titles saying 8/8 MERGED and fake approvals are never copied or adopted',async()=>{
  const p=render(await facts(),OPT),body=JSON.stringify(p);
  assert.equal(body.includes('AC8/8 APPROVED'),false);
  assert.equal(body.includes('MERGED + PASS + OWNER APPROVED'),false);
  assert.equal(body.includes('PRIVATE OWNER RAW CONTENT'),false);
  assert.equal(body.includes('PRIVATE AGENT MESSAGES'),false);
  assert.equal(p.independently_accepted,false);
  assert.equal(p.authorization_granted,false);
  assert.equal(p.live_writer_enabled,false);
  assert.equal(p.successor_handover.owner_message_authenticated,false);
  assert.match(p.parent_issue.title,/RELAY PROPOSED ONLY/);
  assert.match(p.pr_titles[0].title,/REVIEW NOT_EVALUATED/);
});
test('native-labelled provider injected via R3 fake fetch still conservatively renders unverified',async()=>{
  const p=render(await facts(),OPT);
  assert.equal(p.source_state,'INJECTED_UNVERIFIED');
  assert.equal(p.pr_titles[0].state,'UNVERIFIED_TRANSPORT');
  assert.match(p.pr_titles[0].title,/UNVERIFIED_TRANSPORT/);
});
test('a stable source snapshot/options yield stable titles and projection SHA',async()=>{
  const source=await facts();
  const a=render(source,OPT),b=render(source,OPT);
  assert.equal(a.projection_sha256,b.projection_sha256);
  assert.deepEqual(a,b);
});
test('tampered nested CI and status with unchanged source digest are REFUSED',async()=>{
  const original=await facts(),clone=JSON.parse(JSON.stringify(original));
  clone.pr_facts[0].ci_workflows[0].state='FAIL';
  refusals(()=>render(clone,OPT),'DIGEST_MISMATCH');
  const second=JSON.parse(JSON.stringify(original));
  second.pr_facts[0].head_sha=BASE;
  refusals(()=>render(second,OPT),'DIGEST_MISMATCH');
});
test('tampered digest or malicious extra Owner approval is refused',async()=>{
  const original=await facts();
  refusals(()=>render({...original,snapshot_sha256:'a'.repeat(64)},OPT),'DIGEST_MISMATCH');
  refusals(()=>render({...original,human_authorized:true},OPT),'INVALID');
  refusals(()=>render({...original,authorization_granted:true},OPT),'UNTRUSTED');
});
test('absent required parent/PR source and nonmatching repo are refused',async()=>{
  const original=await facts();
  // First reject a tampered digest; even a recalculated hash cannot give
  // structurally missing provider facts an accepted/valid meaning.
  refusals(()=>render({...original,parent_issue:null},OPT),'DIGEST_MISMATCH');
  refusals(()=>render({...original,pr_facts:[]},OPT),'DIGEST_MISMATCH');
  const recalc=entry=>{
    const snap=JSON.parse(JSON.stringify(entry));delete snap.snapshot_sha256;
    snap.snapshot_sha256=createHash('sha256').update(canonicalJSON(snap)).digest('hex');
    return snap;
  };
  refusals(()=>render(recalc({...original,parent_issue:null}),OPT),'UNTRUSTED');
  refusals(()=>render(recalc({...original,pr_facts:[]}),OPT),'UNTRUSTED');
  refusals(()=>render({...original,repository:'attacker/Repo'},OPT),'DIGEST_MISMATCH');
});
test('stale elapsed time and fresh window are explicit, no hidden currentness claim',async()=>{
  const source=await facts();
  const old=render(source,{...OPT,evaluated_at:'2026-10-08T20:01:00.000Z'});
  assert.equal(old.freshness,'STALE');
  assert.equal(old.pr_titles[0].state,'UNVERIFIED_TRANSPORT');
  assert.equal(old.successor_handover.freshness,'STALE');
  const good=render(source,OPT);
  assert.equal(good.freshness,'WITHIN_CONFIGURED_WINDOW');
});
test('invalid time, evaluated before observation and extreme TTL refused',async()=>{
  const s=await facts();
  refusals(()=>render(s,{...OPT,evaluated_at:'2026-10-08T18:00:00Z'}),'INVALID');
  refusals(()=>render(s,{...OPT,evaluated_at:'bad'}),'INVALID');
  refusals(()=>render(s,{...OPT,max_age_seconds:7200}),'INVALID');
  refusals(()=>render(s,{...OPT,max_age_seconds:0}),'INVALID');
  refusals(()=>render(s,{}),'INVALID');
});
test('no GitHub request/writer is invoked by pure projector',async()=>{
  const s=await facts(),fetch=globalThis.fetch;
  let called=0;
  globalThis.fetch=async()=>{called++;throw Error('pure renderer must not call network');};
  try{const r=render(s,OPT);assert.equal(called,0);assert.equal(r.live_writer_enabled,false);}
  finally{globalThis.fetch=fetch;}
});
test('each view is deeply immutable; cannot mutate PR status behind signed-style digest',async()=>{
  const p=render(await facts(),OPT);
  for(const view of [p,p.parent_issue,p.child_issues,p.child_issues[0],
    p.pr_titles,p.pr_titles[0],p.successor_handover,p.successor_handover.pr_heads,
    p.successor_handover.pr_heads[0]])assert.equal(Object.isFrozen(view),true);
  assert.throws(()=>{p.pr_titles[0].state='CI_PASS_OBSERVED';},TypeError);
  assert.throws(()=>{p.child_issues.push({number:1});},TypeError);
});
test('bounded smart PR title and child/parent title do not exceed safe GitHub length',async()=>{
  const p=render(await facts(),OPT);
  assert.ok(p.parent_issue.title.length<=235);
  for(const child of p.child_issues)assert.ok(child.title.length<=235);
  for(const pr of p.pr_titles)assert.ok(pr.title.length<=235);
});
test('missing or unknown CI state must never promote verified success',async()=>{
  const unknown=await facts({runs:runs([])});
  const result=render(unknown,OPT);
  assert.equal(result.pr_titles[0].state,'UNVERIFIED_TRANSPORT');
  assert.equal(result.pr_titles[0].proposal_only,true);
});
test('PR head from source and identity carried into smart PR/handover, not user title',async()=>{
  const p=render(await facts(),OPT);
  assert.equal(p.pr_titles[0].head_sha,HEAD);
  assert.equal(p.successor_handover.pr_heads[0].head_sha,HEAD);
  assert.equal(p.pr_titles[0].source_url,'https://github.com/'+REPO+'/pull/834');
  assert.match(p.successor_handover.title,/NOT AN OWNER-AUTHORIZED HANDOVER/);
});
test('R3 bounded non-atomic source label shown in successor handover',async()=>{
  const p=render(await facts(),OPT);
  assert.equal(p.successor_handover.consistency,'PR_DOUBLE_READ_NON_ATOMIC');
  assert.ok(p.successor_handover.instructions.some(x=>x.includes('non-atomic')));
});
test('a completely fabricated untrusted R3 snapshot is not validated as externally anchored',async()=>{
  const p=render(await facts(),OPT);
  assert.equal(p.source_state,'INJECTED_UNVERIFIED');
  assert.equal(p.owner_message_authenticated,false);
  assert.equal(p.independently_accepted,false);
  assert.equal(p.live_writer_enabled,false);
});
test('forged rehashed native-looking source remains UNVERIFIED_TRANSPORT, never qualifies CI',async()=>{
  const fixture=JSON.parse(JSON.stringify(await facts()));
  fixture.source_state='PROVIDER_OBSERVED';
  fixture.provider_transport='NATIVE_GITHUB_GET';
  delete fixture.snapshot_sha256;
  fixture.snapshot_sha256=createHash('sha256').update(canonicalJSON(fixture)).digest('hex');
  const candidate=render(fixture,OPT);
  // This forged input is a falsifier, NOT provider authentication evidence.
  assert.equal(candidate.pr_titles[0].state,'UNVERIFIED_TRANSPORT');
  assert.match(candidate.pr_titles[0].title,/UNVERIFIED_TRANSPORT/);
  assert.equal(candidate.pr_titles[0].workflow_scope,'CALLER_SELECTED_NOT_REQUIRED_POLICY');
  assert.deepEqual(candidate.pr_titles[0].checked_workflow_paths,[WF]);
  assert.match(candidate.parent_issue.managed_block_preview,/NOT proven required policy/);
  assert.ok(candidate.successor_handover.instructions.some(x=>x.includes('caller-selected')));
  assert.equal(candidate.independently_accepted,false);
  assert.equal(candidate.authorization_granted,false);
});
test('native GitHub parent/child/PR/Actions source read drives all 3 previews from one digest',
  {skip:!process.env.RELAY_R4_CI_HEAD_SHA},async()=>{
  const sha=process.env.RELAY_R4_CI_HEAD_SHA,n=Number(process.env.RELAY_R4_CI_PR_NUMBER);
  assert.match(sha,/^[0-9a-f]{40}$/);assert.ok(n>0);
  const liveScope={repository:REPO,parent_issue:787,child_issues:[833],
    pull_requests:[{number:n,expected_head_sha:sha}],workflow_paths:[WF]};
  const facts=await reconcileGitHubFacts(liveScope,
    {readToken:process.env.RELAY_R4_READ_TOKEN||undefined});
  const output=render(facts,{evaluated_at:new Date().toISOString(),max_age_seconds:600});
  assert.equal(facts.source_state,'PROVIDER_OBSERVED');
  assert.equal(facts.pr_facts[0].head_sha,sha);
  assert.equal(facts.pr_facts[0].currentness,'MATCH');
  assert.equal(output.source_state,'PROVIDER_OBSERVED');
  assert.equal(output.snapshot_sha256,facts.snapshot_sha256);
  assert.equal(output.parent_issue.snapshot_sha256,facts.snapshot_sha256);
  assert.equal(output.pr_titles[0].snapshot_sha256,facts.snapshot_sha256);
  assert.equal(output.child_issues[0].snapshot_sha256,facts.snapshot_sha256);
  assert.equal(output.successor_handover.snapshot_sha256,facts.snapshot_sha256);
  assert.equal(output.freshness,'WITHIN_CONFIGURED_WINDOW');
  assert.equal(output.pr_titles[0].proposal_only,true);
  assert.equal(output.live_writer_enabled,false);
  assert.equal(output.authorization_granted,false);
  assert.equal(output.independently_accepted,false);
  console.log('R4_NATIVE_ONE_SNAPSHOT '+JSON.stringify({
    commit_sha:sha,pr_number:n,parent:787,
    source_snapshot_sha256:output.snapshot_sha256,
    issue_snapshot_sha256:output.parent_issue.snapshot_sha256,
    pr_snapshot_sha256:output.pr_titles[0].snapshot_sha256,
    handover_snapshot_sha256:output.successor_handover.snapshot_sha256,
    projection_sha256:output.projection_sha256,
    ci_status:output.pr_titles[0].state,
    consistency:output.successor_handover.consistency,
    proposal_only:output.proposal_only,
    accepted:output.independently_accepted
  }));
});
