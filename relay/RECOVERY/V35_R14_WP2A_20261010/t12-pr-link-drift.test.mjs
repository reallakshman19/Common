import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectInjectedDrift} from './t12-pr-link-drift.mjs';
const R='reallakshman19/Common',ID=1412133785,N=477;
const H1='a'.repeat(40),H2='b'.repeat(40),BASE='c'.repeat(40);
const HB='codex/t12-h1-h2-experiment',BB='codex/294-t11-pr308-cold-entry-hold';
const issueIds=[5,20,30,288,289,294];
function target(h=H1){return {repository:R,repository_id:ID,pr_number:N,
 entry_url:'https://github.com/'+R+'/pull/'+N,
 head_branch:HB,base_branch:BB,head_expected_sha:h,base_expected_sha:BASE};}
function db(head=H1){
 const out={
  '':{full_name:R,id:ID},
  ['pulls/'+N]:{number:N,state:'open',draft:true,html_url:target().entry_url,
   head:{repo:{full_name:R,id:ID},sha:head,ref:HB},
   base:{repo:{full_name:R,id:ID},sha:BASE,ref:BB}},
  ['git/ref/heads/'+HB]:{ref:'refs/heads/'+HB,object:{sha:head}},
  ['git/ref/heads/'+BB]:{ref:'refs/heads/'+BB,object:{sha:BASE}},
 };
 for(const n of issueIds)out['issues/'+n]={
  number:n,state:'open',html_url:'https://github.com/'+R+'/issues/'+n,
 };
 return out;
}
function reader(d,hook=()=>{}){
 let reads=0;
 return {read:async(repo,path)=>{
  assert.equal(repo,R);hook(++reads,path,d);
  if(!Object.hasOwn(d,path))throw Error('PRIVATE_GITHUB_TOKEN_UNSAFE');
  return structuredClone(d[path]);
 },calls:()=>reads};
}
function noAuthority(x){
 assert.equal(x.observation_grade,'CALLER_INJECTED_UNATTESTED');
 assert.equal(x.source_digest,null);
 assert.equal(x.admission,'NOT_ADMITTED');
 assert.equal(x.evidence_admitted,false);
 assert.equal(x.owner_authenticated,false);
 assert.equal(x.admitted_plan_graph,false);
 assert.equal(x.independent_successor_qualified,false);
 assert.equal(x.reviewer_qualified,false);
 assert.equal(x.required_ci_qualified,false);
 assert.equal(x.delp_projector_invoked,false);
 assert.equal(x.programme_progress,null);
 assert.equal(x.writer_authorized,false);
 assert.equal(x.publisher_authorized,false);
 assert.equal(x.local_responsibility_complete,false);
 assert.ok(!JSON.stringify(x).includes('PRIVATE_GITHUB_TOKEN_UNSAFE'));
}
test('T12 H1 current diagnostic is source-only HOLD, not evidence',async()=>{
 const d=db(),rr=reader(d),x=await inspectInjectedDrift(target(),rr.read);
 assert.equal(x.status,'CURRENT_SOURCE_READ_ONLY_HOLD');
 assert.equal(x.reason,'SOURCE_CURRENT_OWNER_HOLD');
 assert.equal(x.source_verified,true);assert.equal(x.provider_pass_count,2);
 assert.equal(x.issue_links_verified,true);assert.equal(rr.calls(),22);
 noAuthority(x);
});
test('T12 actual H1→H2 stable later head refuses prior evidence and exposes observed HEAD',async()=>{
 const d=db(H2),x=await inspectInjectedDrift(target(H1),reader(d).read);
 assert.equal(x.status,'HOLD_STALE_H1');
 assert.equal(x.reason,'PR_HEAD_CHANGED_SINCE_CHECKPOINT');
 assert.equal(x.source_verified,false);
 assert.equal(x.observed_head_sha,H2);
 assert.equal(x.next_permitted_action,'REFETCH_PR_AND_RECONCILE_H1_H2_NO_ADMISSION');
 noAuthority(x);
});
test('T12 re-fetched H2 can only be current-source HOLD, never reused E',async()=>{
 const x=await inspectInjectedDrift(target(H2),reader(db(H2)).read);
 assert.equal(x.status,'CURRENT_SOURCE_READ_ONLY_HOLD');
 assert.equal(x.source_verified,true);noAuthority(x);
});
test('T12 H1→H2 between outer reads cannot appear current and cannot be accepted',async()=>{
 const d=db(),rr=reader(d,(n,path,s)=>{
  if(n===12){s['pulls/'+N].head.sha=H2;s['git/ref/heads/'+HB].object.sha=H2;}
 });
 const x=await inspectInjectedDrift(target(H1),rr.read);
 assert.equal(x.status,'HOLD_SOURCE_DRIFT');
 assert.equal(x.reason,'SOURCE_CHANGED_DURING_DOUBLE_READ');
 assert.equal(x.source_verified,false);
 noAuthority(x);
});
test('T12 head moves within late GET of one round and gets refused',async()=>{
 const d=db(),rr=reader(d,(n,p,s)=>{
  if(n===11)s['pulls/'+N].head.sha=H2;
 });
 const x=await inspectInjectedDrift(target(),rr.read);
 assert.equal(x.status,'HOLD_UNVERIFIED_SOURCE');
 assert.equal(x.reason,'SOURCE_CHANGED_DURING_DOUBLE_READ');
 noAuthority(x);
});
test('T12 existing branch pointer mismatch rejects even if PR head looks current',async()=>{
 const d=db();d['git/ref/heads/'+HB].object.sha=H2;
 const x=await inspectInjectedDrift(target(),reader(d).read);
 assert.equal(x.reason,'SOURCE_REF_DISAGREES_WITH_PR');
 assert.equal(x.source_verified,false);noAuthority(x);
});
test('T12 base SHA drift invalidates H1 while retaining observed base',async()=>{
 const d=db();d['pulls/'+N].base.sha=H2;d['git/ref/heads/'+BB].object.sha=H2;
 const x=await inspectInjectedDrift(target(),reader(d).read);
 assert.equal(x.status,'HOLD_STALE_BASE');
 assert.equal(x.reason,'PR_BASE_CHANGED_SINCE_CHECKPOINT');
 assert.equal(x.observed_base_sha,H2);noAuthority(x);
});
test('T12 PR base branch ref or cross-repo base spoof is rejected',async()=>{
 for(const mutate of [d=>d['pulls/'+N].base.ref='main',
   d=>d['pulls/'+N].base.repo.id=1207996454]){
  const d=db();mutate(d);
  const x=await inspectInjectedDrift(target(),reader(d).read);
  assert.equal(x.source_verified,false);noAuthority(x);
 }
});
test('T12 corrupted PR URL and old-repo link refuse before provider reads',async()=>{
 for(const url of ['https://github.com/reallaksh19/Common/pull/'+N,
   'https://github.com/'+R+'/pull/308','https://github.com/'+R+'/issues/'+N]){
  const rr=reader(db());
  const x=await inspectInjectedDrift({...target(),entry_url:url},rr.read);
  assert.equal(rr.calls(),0);assert.equal(x.reason,'INPUT_INVALID');noAuthority(x);
 }
});
test('T12 PR provider html_url points to another PR and is rejected',async()=>{
 const d=db();d['pulls/'+N].html_url='https://github.com/'+R+'/pull/308';
 const x=await inspectInjectedDrift(target(),reader(d).read);
 assert.equal(x.reason,'PR_PROVIDER_IDENTITY_INVALID');noAuthority(x);
});
test('T12 parent and #289 link mismatch forbid current source',async()=>{
 for(const n of [5,289]){
  const d=db();d['issues/'+n].html_url='https://github.com/reallaksh19/Common/issues/'+n;
  const x=await inspectInjectedDrift(target(),reader(d).read);
  assert.equal(x.reason,'ISSUE_LINK_IDENTITY_INVALID');noAuthority(x);
 }
});
test('T12 missing leaf, source owner or successor link cannot be silently skipped',async()=>{
 for(const n of [20,30,288,294]){
  const d=db();delete d['issues/'+n];
  const x=await inspectInjectedDrift(target(),reader(d).read);
  assert.equal(x.reason,'PROVIDER_READ_UNVERIFIED');noAuthority(x);
 }
});
test('T12 injected forged reviewer, adopted policy and E claims never mint permission',async()=>{
 const d=db();d['pulls/'+N].reviewer_qualified=true;
 d['pulls/'+N].evidence_admitted=true;d['pulls/'+N].writer_authorized=true;
 const x=await inspectInjectedDrift(target(),reader(d).read);
 assert.equal(x.source_verified,true);
 noAuthority(x);
});
test('T12 no raw transport secrets leaked in refusal',async()=>{
 const rr=reader(db(),(n)=>{if(n===2)throw Error('PRIVATE_GITHUB_TOKEN_UNSAFE')});
 const x=await inspectInjectedDrift(target(),rr.read);
 assert.equal(x.reason,'PROVIDER_READ_UNVERIFIED');noAuthority(x);
});
test('T12 invalid SHA, bad repository, untrusted runner or unsafe branch path refuse',async()=>{
 for(const t of [
  {...target(),head_expected_sha:'not-a-sha'},
  {...target(),repository:'reallaksh19/Common'},
  {...target(),repository_id:1207996454},
  {...target(),head_branch:'../bad'},
  {...target(),writer_authorized:true},
 ]){
  const rr=reader(db());
  const x=await inspectInjectedDrift(t,rr.read);
  assert.equal(x.reason,'INPUT_INVALID');assert.equal(rr.calls(),0);noAuthority(x);
 }
});
