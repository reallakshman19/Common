import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectInjectedPrOnly,PR_ONLY_ENTRY} from './t11-pr-only-cold-entry.mjs';

const R='reallakshman19/Common',ID=1412133785,H='087cf43193febffc31375e71359e767489d3ae68';
const B='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const HEAD='codex/294-t05-wp2a-wp2b-negative-same-head';
const BASE='codex/294-t01-wp2a-u02-u03-u04-pinned';
const ISSUES=[5,20,30,294,289,288];
function db(){
 const d={
  '':{id:ID,full_name:R},
  'pulls/308':{number:308,html_url:PR_ONLY_ENTRY,state:'open',
   head:{sha:H,ref:HEAD,repo:{id:ID,full_name:R}},
   base:{sha:B,ref:BASE,repo:{id:ID,full_name:R}}},
  ['git/ref/heads/'+HEAD]:{ref:'refs/heads/'+HEAD,object:{sha:H}},
  ['git/ref/heads/'+BASE]:{ref:'refs/heads/'+BASE,object:{sha:B}},
 };
 for(const n of ISSUES)d['issues/'+n]={number:n,state:'open',html_url:'https://github.com/'+R+'/issues/'+n};
 return d;
}
function reader(d,hook=()=>{}){
 let count=0;
 return {read:async(repo,path)=>{
  assert.equal(repo,R);
  hook(++count,path,d);
  if(!Object.hasOwn(d,path))throw Error('PRIVATE_TOKEN_SECRET');
  return structuredClone(d[path]);
 },count:()=>count};
}
function noGrant(x){
 assert.equal(x.observation_grade,'CALLER_INJECTED_UNATTESTED');
 assert.equal(x.owner_authenticated,false);
 assert.equal(x.admitted_plan_graph,false);
 assert.equal(x.evidence_admitted,false);
 assert.equal(x.independent_successor_qualified,false);
 assert.equal(x.reviewer_qualified,false);
 assert.equal(x.required_ci_qualified,false);
 assert.equal(x.writer_authorized,false);
 assert.equal(x.publisher_authorized,false);
 assert.equal(x.local_responsibility_complete,false);
 assert.equal(x.programme_progress,null);
 assert.equal(x.delp_projection,'NOT_CALCULATED');
 assert.equal(x.next_permitted_action,'READ_ONLY_RECONCILE_D1_D5_AND_REAL_SUCCESSOR');
 assert.ok(!JSON.stringify(x).includes('PRIVATE_TOKEN_SECRET'));
}
test('T11 PR-only entry can reconstruct exact PR308, origin and HOLD without old chat',async()=>{
 const d=db(),r=reader(d),x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,r.read);
 assert.equal(x.source_verified,true);
 assert.equal(x.material_status,'PR_SOURCE_CURRENT_READ_ONLY');
 assert.equal(x.source_identity.pr_head,H);
 assert.equal(x.source_identity.base_head,B);
 assert.equal(x.source_identity.negative_consumer_issue,30);
 assert.equal(x.source_identity.independent_successor_issue,288);
 assert.equal(x.observations,2);
 assert.equal(r.count(),20);
 noGrant(x);
});
test('T11 wrong PR/old-repo entry denied before any GET',async()=>{
 for(const entry of ['https://github.com/reallaksh19/Common/pull/308',
   'https://github.com/reallakshman19/Common/pull/292','https://github.com/reallakshman19/Common/pull/306']){
  const r=reader(db()),x=await inspectInjectedPrOnly(entry,r.read);
  assert.equal(x.reason,'ENTRY_PR_NOT_PINNED');
  assert.equal(r.count(),0);
  noGrant(x);
 }
});
test('T11 old repo ID spoof denied',async()=>{
 const d=db();d[''].id=1207996454;
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,reader(d).read);
 assert.equal(x.source_verified,false);
 assert.equal(x.reason,'PR_OR_REPOSITORY_IDENTITY_UNVERIFIED');noGrant(x);
});
test('T11 H1→H2 candidate head movement before read denies source',async()=>{
 const d=db();d['pulls/308'].head.sha='a'.repeat(40);
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,reader(d).read);
 assert.equal(x.reason,'PR_SOURCE_HEAD_OR_BASE_STALE');noGrant(x);
});
test('T11 H1→H2 movement between first and second rounds is fail-closed',async()=>{
 const d=db(),r=reader(d,(n,p,data)=>{
  if(n===12)data['pulls/308'].head.sha='a'.repeat(40);
 });
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,r.read);
 assert.equal(x.source_verified,false);
 assert.equal(x.reason,'PR_SOURCE_HEAD_OR_BASE_STALE');
 assert.equal(x.observations,1);noGrant(x);
});
test('T11 base SHA move detected, never inferred from same branch name',async()=>{
 const d=db();d['pulls/308'].base.sha='a'.repeat(40);
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,reader(d).read);
 assert.equal(x.reason,'PR_SOURCE_HEAD_OR_BASE_STALE');noGrant(x);
});
test('T11 provider branch ref mismatch denies native source grade',async()=>{
 const d=db();d['git/ref/heads/'+HEAD].object.sha='a'.repeat(40);
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,reader(d).read);
 assert.equal(x.reason,'SOURCE_BRANCH_REF_STALE');noGrant(x);
});
test('T11 source-owner issue is missing or forged as PR',async()=>{
 for(const change of [d=>delete d['issues/30'],d=>d['issues/20'].pull_request={}]) {
  const d=db();change(d);
  const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,reader(d).read);
  assert.equal(x.source_verified,false);
  assert.ok(['SOURCE_ISSUE_NOT_VERIFIED','PROVIDER_READ_UNVERIFIED'].includes(x.reason));
  noGrant(x);
 }
});
test('T11 provider exception is sanitized, never leaks body or passes',async()=>{
 const r=reader(db(),(n)=>{if(n===2)throw Error('PRIVATE_TOKEN_SECRET')});
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,r.read);
 assert.equal(x.reason,'PROVIDER_READ_UNVERIFIED');noGrant(x);
});
test('T11 fake policy/reviewer/status tags cannot elevate SOURCE-only provenance',async()=>{
 const d=db();
 d['pulls/308'].merged=true;d['pulls/308'].reviewer_qualified=true;
 d['pulls/308'].evidence_admitted=true;d['pulls/308'].status='success';
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,reader(d).read);
 assert.equal(x.source_verified,true);
 noGrant(x);
});
test('T11 supplied missing reader cannot create native source attestation',async()=>{
 const x=await inspectInjectedPrOnly(PR_ONLY_ENTRY,null);
 assert.equal(x.source_verified,false);
 assert.equal(x.reason,'PROVIDER_READER_MISSING');noGrant(x);
});
