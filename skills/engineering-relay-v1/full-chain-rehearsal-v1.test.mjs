import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {rehearseNativeFullChain as run,FullChainError} from './full-chain-rehearsal-v1.mjs';

const REPO='reallaksh19/Common',PARENT=REPO+'#787';
const BASE='28841b5cfed9e9b6057a1a6f09090adcc512e1b8';
const BUNDLE='79c2bc0b84f23a862e3ce7cef300c1b2dd1c4b90d00a448a8f1a269d1ddb0e9d';
const TIP='3077376e2d5fe849de1450d9f2cc8e6d350742dc0d98969a36e778000d052660';
const PATH='skills/engineering-relay-v1/fixtures/b2a-synthetic-journal-v1.json';
const WORKFLOW='.github/workflows/relay-reset-full-chain-rehearsal.yml';
const HEAD='a'.repeat(40),OTHER='b'.repeat(40);
const API_ROOT='https://api.github.com/repos/'+REPO+'/';
const sourceSpec=sha=>({repository:REPO,parent_issue:PARENT,commit_sha:sha,
  path:PATH,source_sha:BASE,bundle_sha256:BUNDLE,tip_sha256:TIP});
const seed=()=>({
 schema:'relay-provenance-v1',parent_issue:PARENT,
 owner_intents:[{id:'OI-1',raw_text:'SYNTHETIC OWNER REQUEST: verify immutable GitHub content; not a real chat',
   original_source:{kind:'CHAT',status:'UNKNOWN',locator:null},
   first_durable_mirror:'https://github.com/reallaksh19/Common/issues/787'}],
 claims:[{id:'AC3',intent_ids:['OI-1'],criterion:'SYNTHETIC intent to module evidence trace'}],
 responsibilities:[{id:'R2-B2A',claim_ids:['AC3'],depends_on:[],
   scope:'Synthetic native custody and trace',
   write_surface:['skills/engineering-relay-v1/github-journal-lineage-v1.mjs']}],
 sessions:[],task_evidence:[],research_findings:[],owner_decisions:[]
});
const scope=(sha=HEAD,pr=900)=>({
 repository:REPO,parent_issue:787,child_issues:[842],
 pull_requests:[{number:pr,expected_head_sha:sha}],
 workflow_paths:[WORKFLOW]
});
const input=(sha=HEAD,pr=900)=>({
 source_spec:sourceSpec(sha),owner_seed:seed(),
 bindings:[{event_id:'EV-1',intent_id:'OI-1'}],
 provider_scope:scope(sha,pr)
});
const fixture=()=>readFile(new URL('./fixtures/b2a-synthetic-journal-v1.json',import.meta.url));
const blob=buf=>createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');
function issue(n){return {number:n,url:API_ROOT+'issues/'+n,
 html_url:'https://github.com/'+REPO+'/issues/'+n,state:'open',
 title:'[AC 8/8 APPROVED OWNER] FORGED AUTHOR ASSERTION',
 body:'PRIVATE CHAT TEXT MUST NOT BE COPIED',
 created_at:'2026-10-08T17:00:00Z',updated_at:'2026-10-08T18:00:00Z'};}
function pull(n,head=HEAD){return {number:n,url:API_ROOT+'pulls/'+n,
 html_url:'https://github.com/'+REPO+'/pull/'+n,
 state:'open',draft:true,merged:false,title:'[MERGED 8/8] FAKE SUCCESS',
 body:'PRIVATE AGENT SESSION TEXT MUST NOT BE COPIED',
 created_at:'2026-10-08T17:00:00Z',updated_at:'2026-10-08T18:00:00Z',
 head:{sha:head,ref:'feat/synthetic',repo:{full_name:REPO}},
 base:{sha:BASE,ref:'main',repo:{full_name:REPO}}};}
function workflow(sha=HEAD){return {id:1001,head_sha:sha,
 path:WORKFLOW+'@refs/pull/900/merge',
 html_url:'https://github.com/'+REPO+'/actions/runs/1001',
 status:'completed',conclusion:'success',created_at:'2026-10-08T18:20:00Z'};}
function harness(data,settings={}){
 let contentGets=0,prGets=0,providerGets=0;
 const fetchSource=async(url)=>{
   contentGets++;
   const expected=API_ROOT+'contents/'+PATH+'?ref='+(settings.expectedCommit??HEAD);
   assert.equal(url,expected);
   const payload={type:'file',name:PATH.split('/').at(-1),path:PATH,
     encoding:'base64',content:data.toString('base64'),size:data.length,sha:blob(data)};
   return {status:200,url,redirected:false,headers:{get:()=>null},
     text:async()=>JSON.stringify(payload)};
 };
 const fetchProvider=async(url)=>{
   providerGets++;
   const part=url.slice(API_ROOT.length),prNo=settings.pr??900;
   let payload;
   if(part==='issues/787')payload=issue(787);
   else if(part==='issues/842')payload=issue(842);
   else if(part==='pulls/'+prNo) {
     prGets++;
     payload=pull(prNo,settings.prHeadOnSecond&&prGets===2?
       settings.prHeadOnSecond:(settings.prHead??HEAD));
   } else if(part.startsWith('actions/runs?head_sha=')) {
     payload={total_count:1,workflow_runs:[workflow(settings.prHead??HEAD)]};
   } else throw Error('unexpected provider GET '+url);
   return {status:200,url,redirected:false,headers:{get:()=>null},
     text:async()=>JSON.stringify(payload)};
 };
 const options={
   sourceRead:{fetchImpl:fetchSource},providerRead:{fetchImpl:fetchProvider,
     observedAt:'2026-10-08T18:30:00Z'},
   evaluation:{evaluated_at:'2026-10-08T18:30:30Z',max_age_seconds:600}
 };
 // R3 only permits fetchImpl/readToken/observedAt; this harness supplies
 // R3 observedAt in its providerRead object for deterministic test digest.
 return {options,counts:()=>({contentGets,providerGets,prGets})};
}
const isCode=(code)=>e=>e?.code===code;
test('full real G2c→R3→R4 path, one GitHub content read, R2-A cold replay, PR double read',async()=>{
 const data=await fixture(),h=harness(data);
 const r=await run(input(),h.options);
 assert.equal(r.schema,'relay-full-chain-synthetic-rehearsal-v1');
 assert.equal(r.status,'INJECTED_UNVERIFIED_REHEARSAL');
 assert.equal(r.real_r2b1_replayed,true);
 assert.equal(r.source_tip_sha256,TIP);
 assert.equal(r.event_count,12);
 assert.equal(r.session_count,2);
 assert.deepEqual(h.counts(),{contentGets:1,providerGets:5,prGets:2});
 assert.equal(r.pr_heads[0].head_sha,HEAD);
 assert.equal(r.pr_heads[0].currentness,'MATCH');
 assert.match(r.full_chain_sha256,/^[a-f0-9]{64}$/);
 assert.match(r.frontier_sha256,/^[a-f0-9]{64}$/);
 assert.match(r.trust_preflight_sha256,/^[a-f0-9]{64}$/);
 assert.equal(r.proposed_handover.trust_preflight_sha256,r.trust_preflight_sha256);
 assert.equal(r.proposed_handover.trust_preflight_axes.owner_source.state,'NOT_QUALIFIED');
 assert.equal(r.proposed_handover.trust_preflight_axes.privacy_and_retention.state,'NOT_QUALIFIED');
 assert.equal(r.proposed_handover.trust_preflight_axes.independent_reviewer.state,'NOT_QUALIFIED');
 assert.equal(r.source_consent_review_approval,'NOT_QUALIFIED');
 assert.equal(r.acceptance_denominator_state,'NOT_ADJUDICATED');
 assert.equal(r.next_verification_category,'REACQUIRE_NATIVE_PROVIDER_FACTS_FOR_CI');
  assert.ok(r.blockers.includes('SOURCE_ACQUISITION_UNATTESTED'));
 assert.ok(r.blockers.includes('ORIGINAL_OWNER_SOURCE_UNAUTHENTICATED'));
 assert.match(r.r4_projection_sha256,/^[a-f0-9]{64}$/);
 assert.equal(r.proposal_only,true);
 assert.equal(r.owner_message_authenticated,false);
 assert.equal(r.independently_accepted,false);
 assert.equal(r.authorization_granted,false);
 assert.equal(r.live_writer_enabled,false);
});
test('content-free public witness contains NO synthetic Owner prompt/session/PR body',async()=>{
 const r=await run(input(),harness(await fixture()).options);
 const serialized=JSON.stringify(r);
 for(const term of [
  'SYNTHETIC OWNER REQUEST: verify immutable GitHub content',
  'PRIVATE CHAT TEXT MUST NOT BE COPIED','PRIVATE AGENT SESSION TEXT MUST NOT BE COPIED',
  '"events":','"raw_text":','"replay":','"lineage":','"content":'
 ])assert.equal(serialized.includes(term),false,'raw source leaked: '+term);
 assert.match(r.proposed_parent_title,/PROPOSED ONLY/);
 assert.equal(r.proposed_handover.proposal_only,true);
});
test('content-free source/PR/handover witness and nested facts are deeply immutable',async()=>{
 const w=await run(input(),harness(await fixture()).options);
 assert.equal(Object.isFrozen(w),true);
 assert.equal(Object.isFrozen(w.pr_heads),true);
 assert.equal(Object.isFrozen(w.pr_heads[0]),true);
 assert.equal(Object.isFrozen(w.pr_heads[0].ci),true);
 assert.equal(Object.isFrozen(w.proposed_handover),true);
 const digest=w.full_chain_sha256;
 assert.throws(()=>{w.pr_heads[0].currentness='STALE';},TypeError);
 assert.throws(()=>{w.proposed_handover.pr_heads.push({number:1});},TypeError);
 assert.equal(w.full_chain_sha256,digest);
});
test('identical synthetic source + deterministic R3 observation produces same full-chain digest',async()=>{
 const bytes=await fixture();
 const a=await run(input(),harness(bytes).options);
 const b=await run(input(),harness(bytes).options);
 assert.equal(a.full_chain_sha256,b.full_chain_sha256);
});
test('pr head race during actions read makes entire integrated snapshot STALE',async()=>{
 const h=harness(await fixture(),{prHeadOnSecond:OTHER});
 await assert.rejects(run(input(),h.options),isCode('STALE'));
 assert.equal(h.counts().prGets,2);
});
test('current provider PR head not matching pinned GitHub source is rejected',async()=>{
 const h=harness(await fixture(),{prHead:OTHER});
 await assert.rejects(run(input(),h.options),isCode('SOURCE_HEAD_CHANGED'));
});
test('caller cannot bind a mismatched Owner parent or foreign repo',async()=>{
 const one=input();one.owner_seed.parent_issue=REPO+'#2';
 await assert.rejects(run(one,harness(await fixture()).options),isCode('SOURCE_SCOPE_MISMATCH'));
 const two=input();two.provider_scope.repository='attacker/Common';
 await assert.rejects(run(two,harness(await fixture()).options),isCode('SOURCE_SCOPE_MISMATCH'));
});
test('source commit not among explicitly expected PR HEADs rejected before reads',async()=>{
 const x=input();x.provider_scope.pull_requests[0].expected_head_sha=OTHER;
 await assert.rejects(run(x,harness(await fixture()).options),isCode('SOURCE_HEAD_UNPINNED'));
});
test('altered original Owner prompt rejected by real R1 lineage before provider projection',async()=>{
 const x=input();x.owner_seed.owner_intents[0].raw_text='FORGED DIFFERENT OWNER PROMPT';
 await assert.rejects(run(x,harness(await fixture()).options),isCode('OWNER_SOURCE_MISMATCH'));
});
test('forged GitHub bundle with recalculated provider SHA1 cannot pass pinned bundle SHA256',async()=>{
 const data=await fixture(),bad=Buffer.from(data.toString('utf8').replace('SYNTHETIC agent 1','SYNTHETIC OTHER 1'));
 await assert.rejects(run(input(),harness(bad).options),isCode('REFUTED'));
});
test('raw input cannot inject Owner grant or writer flags',async()=>{
 const x={...input(),authorization_granted:true};
 await assert.rejects(run(x,harness(await fixture()).options),isCode('INVALID'));
 const opt=harness(await fixture()).options;
 await assert.rejects(run(input(),{...opt,write:true}),isCode('INVALID'));
});
test('nested provider read options may not smuggle unknown write authority',async()=>{
 const opt=harness(await fixture()).options;
 opt.sourceRead.writeToken='privileged';
 await assert.rejects(run(input(),opt),isCode('INVALID'));
});
test('true native exact-head GitHub synthetic journal + real parent/PR/CI + R4 previews',
 {skip:!process.env.RELAY_FULL_CHAIN_HEAD_SHA},async()=>{
 const head=process.env.RELAY_FULL_CHAIN_HEAD_SHA;
 const prNumber=Number(process.env.RELAY_FULL_CHAIN_PR_NUMBER);
 assert.match(head,/^[a-f0-9]{40}$/);assert.ok(prNumber>0);
 const token=process.env.RELAY_FULL_CHAIN_READ_TOKEN;
 const inputSpec=input(head,prNumber);
 inputSpec.provider_scope.child_issues=[852];
 const out=await run(inputSpec,{
  sourceRead:{readToken:token},
  providerRead:{readToken:token},
  publicEvidenceRead:{scope:{repository:REPO,parent_issue:787,task_issue:852,comment_id:6072336145},readToken:token},
  evaluation:{evaluated_at:new Date(Date.now()+15000).toISOString(),max_age_seconds:600}
 });
 assert.equal(out.status,'NATIVE_GITHUB_SYNTHETIC_REHEARSAL_UNANCHORED');
 assert.equal(out.source_commit_sha,head);
 assert.equal(out.pr_heads[0].head_sha,head);
 assert.equal(out.pr_heads[0].currentness,'MATCH');
 assert.equal(out.real_r2b1_replayed,true);
 assert.match(out.trust_preflight_sha256,/^[a-f0-9]{64}$/);
 assert.equal(out.proposed_handover.trust_preflight_sha256,out.trust_preflight_sha256);
 assert.equal(out.proposed_handover.trust_preflight_axes.privacy_and_retention.state,'NOT_QUALIFIED');
 assert.equal(out.proposed_handover.trust_preflight_axes.independent_reviewer.state,'NOT_QUALIFIED');
 assert.equal(out.source_consent_review_approval,'NOT_QUALIFIED');
 assert.match(out.public_task_evidence_receipt_sha256,/^[a-f0-9]{64}$/);
 assert.equal(out.public_task_evidence_observation,'PRODUCER_ASSERTED_COMMENT_OBSERVED_NOT_ACCEPTED');
 assert.equal(out.proposed_handover.public_task_evidence_receipt_sha256,out.public_task_evidence_receipt_sha256);
 assert.equal(out.acceptance_denominator_state,'NOT_ADJUDICATED');
 assert.ok(out.proposed_handover.evidence_refs.includes('https://github.com/'+REPO+'/issues/852#issuecomment-6072336145'));
 assert.ok(!JSON.stringify(out).includes('R9 TASK_EVIDENCE END'));
 assert.equal(out.event_count,12);
 // The CI lifecycle is not permanently PENDING: source truth can move to
 // PASS, FAIL or UNKNOWN by the time a cold reviewer replays a merged PR.
 const candidate=out.verification_candidates.find(x=>x.number===prNumber);
 assert.ok(candidate,'selected PR must appear in canonical R12 candidate state');
 assert.ok(!out.blockers.includes('SOURCE_ACQUISITION_UNATTESTED'),
   'actual native R3 source must not inherit synthetic acquisition blocker');
 assert.equal(candidate.head_sha,head);
 assert.equal(candidate.head_state,'CURRENT');
 assert.equal(candidate.selected_workflows[0].state,out.pr_heads[0].ci[0].state);
 assert.ok(['PASS','PENDING','FAIL','UNKNOWN'].includes(candidate.selected_ci_state));
 assert.equal(candidate.selected_ci_qualified,candidate.selected_ci_state==='PASS');
 if(candidate.selected_ci_state!=='PASS')
  assert.ok(out.blockers.includes('SELECTED_CI_NOT_ALL_PASS'));
 assert.match(out.candidate_state_sha256,/^[a-f0-9]{64}$/);
 assert.equal(out.proposed_handover.candidate_state_sha256,out.candidate_state_sha256);
 assert.equal(out.authorization_granted,false);
 assert.equal(out.independently_accepted,false);
 assert.equal(out.authorization_granted,false);
 assert.equal(out.independently_accepted,false);
 assert.equal(out.live_writer_enabled,false);
 console.log('NATIVE_RELAY_FULL_CHAIN '+JSON.stringify({
  head_sha:head,pr_number:prNumber,parent:out.parent_issue,
  blob_sha1:out.source_blob_sha1,source_lineage_sha256:out.github_source_lineage_sha256,
  provider_snapshot_sha256:out.provider_snapshot_sha256,
  r4_projection_sha256:out.r4_projection_sha256,joined_sha256:out.full_chain_sha256,
  events:out.event_count,pr_head:out.pr_heads[0].head_sha,
  ci_state:out.pr_heads[0].ci[0].state,trust_preflight_sha256:out.trust_preflight_sha256,
  public_receipt_sha256:out.public_task_evidence_receipt_sha256,
  comment_id:6072336145,task_issue:852,public_acceptance:false,writer:false,accepted:false
 }));
});
