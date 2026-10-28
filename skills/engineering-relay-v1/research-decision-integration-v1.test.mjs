import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {inspectResearchDecision as inspect,IntegrationError} from './research-decision-integration-v1.mjs';
const ROOT='reallaksh19/Common#787', SHA='16ab0ff4b90e295b8b08dffa1bcb5b24134ded1f';
const COMMENT='https://github.com/reallaksh19/Common/issues/789#issuecomment-6062832157';
const body='APPROVAL? No: candidate research discussion only';
const DIGEST=createHash('sha256').update(body).digest('hex');
const source={kind:'GITHUB_COMMENT',status:'CLAIMED',locator:COMMENT,digest:DIGEST};
const original={kind:'CHAT',status:'UNKNOWN',locator:null};
const fixture=()=>({
 schema:'relay-provenance-v1',parent_issue:ROOT,
 owner_intents:[{id:'OI-1',raw_text:'start now',original_source:original,
   first_durable_mirror:'https://github.com/reallaksh19/Common/issues/787'}],
 claims:[{id:'AC7',intent_ids:['OI-1'],criterion:'Source-backed research decision'}],
 responsibilities:[{id:'R1-C',claim_ids:['AC7'],depends_on:[],scope:'Read-only integration',
   write_surface:['skills/engineering-relay-v1/research-decision-integration-v1.mjs']}],
 sessions:[{id:'S1',responsibility_id:'R1-C',agent_id:'AGENT',base_sha:SHA,changed_files:[],
   events:[{kind:'OWNER_PROMPT',source:original,summary:'start now'}]}],
 task_evidence:[],
 research_findings:[{id:'F1',statement:'A candidate finding, not adopted just by being true',
   source:{kind:'GITHUB_ISSUE',status:'CLAIMED',locator:'https://github.com/reallaksh19/Common/issues/792'},
   verification:'SUPPORTED_CLAIM'}],
 owner_decisions:[{id:'D1',intent_id:'OI-1',finding_ids:['F1'],disposition:'ADOPT',source:{...source}}]
});
const grant=()=>({
 schema:'relay-declared-grant-v1',grant_id:'G1',revision_sha:SHA,parent_issue:ROOT,
 principal_login:'reallaksh19',role:'OWNER',actions:['RESEARCH_ADOPTION'],
 claim_ids:['AC7'],resources:[ROOT],exact_head_sha:SHA,
 valid_from:'2026-10-08T00:00:00Z',valid_until:'2026-10-09T00:00:00Z',
 revoked_at:null,source_comment_url:'https://github.com/reallaksh19/Common/issues/787#issuecomment-6064020826',
 source_body_sha256:'a'.repeat(64)
});
const proposal=()=>({
 schema:'relay-decision-candidate-v1',decision_id:'D1',parent_issue:ROOT,claim_id:'AC7',
 issuer_login:'reallaksh19',role:'OWNER',action:'RESEARCH_ADOPTION',
 resource:ROOT,exact_head_sha:SHA,issued_at:'2026-10-08T13:00:00Z',
 finding_ids:['F1'],subject_author_login:null,
 source_receipt:{status:'PROVIDER_ISSUER_OBSERVED',transport:'NATIVE_FIXED_HTTPS_GET',
   author_login:'reallaksh19',source_url:COMMENT,body_sha256:DIGEST}
});
const commentScope=()=>({repository:'reallaksh19/Common',issue:789,comment_id:6062832157});
const native=()=>({
 id:6062832157,url:'https://api.github.com/repos/reallaksh19/Common/issues/comments/6062832157',
 issue_url:'https://api.github.com/repos/reallaksh19/Common/issues/789',
 html_url:COMMENT,user:{login:'reallaksh19'},author_association:'OWNER',
 body,created_at:'2026-10-08T15:06:25Z',updated_at:'2026-10-08T15:06:25Z'
});
const clone=x=>JSON.parse(JSON.stringify(x));
const fetcher=p=>async()=>({status:200,redirected:false,
 url:'https://api.github.com/repos/reallaksh19/Common/issues/comments/6062832157',
 headers:{get:()=>null},text:async()=>JSON.stringify(p)});
const inputs=()=>({document:fixture(),decision_id:'D1',claim_id:'AC7',
 comment_scope:commentScope(),proposal:proposal(),declared_grant:grant()});
const fail=async(input,code)=>assert.rejects(inspect(input,{fetchImpl:fetcher(native())}),
 e=>e instanceof IntegrationError&&e.code===code);
test('real merged modules join research to raw Owner intent but mock cannot mint authority',async()=>{
 const v=await inspect(inputs(),{fetchImpl:fetcher(native())});
 assert.equal(v.status,'DECLARED_SCOPE_DENIED');
 assert.equal(v.declared_scope.reasons.includes('NOT_NATIVE_SOURCE_OBSERVATION'),true);
 assert.equal(v.source_status,'INJECTED_UNVERIFIED');
 assert.equal(v.source_transport,'INJECTED_UNVERIFIED');
 assert.equal(v.authorization_granted,false);
 assert.equal(v.owner_intents[0].raw_text,'start now');
 assert.equal(v.owner_intents[0].original_source.status,'UNKNOWN');
 assert.equal(v.owner_intents[0].first_durable_mirror,'https://github.com/reallaksh19/Common/issues/787');
 assert.deepEqual(v.research_findings.map(x=>x.id),['F1']);
 assert.match(v.reconciled_view_digest,/^[a-f0-9]{64}$/);
});
test('caller fabricated native receipt is discarded and not promoted',async()=>{
 const p=inputs();p.proposal.source_receipt.body_sha256='0'.repeat(64);
 p.proposal.source_receipt.source_url='https://evil.example/comment';
 const v=await inspect(p,{fetchImpl:fetcher(native())});
 assert.equal(v.status,'DECLARED_SCOPE_DENIED');
 assert.equal(v.source_digest,DIGEST);
 assert.equal(v.authorization_granted,false);
});
test('same source from same provider returns deterministic reconciliation digest',async()=>{
 const a=await inspect(inputs(),{fetchImpl:fetcher(native())});
 const b=await inspect(inputs(),{fetchImpl:fetcher(native())});
 assert.equal(a.reconciled_view_digest,b.reconciled_view_digest);
});
test('OwnerDecision from wrong OwnerIntent cannot pass claim link',async()=>{
 const p=inputs();p.document.owner_intents.push({id:'OI-2',raw_text:'different intent',original_source:original,first_durable_mirror:null});
 p.document.owner_decisions[0].intent_id='OI-2';
 await fail(p,'REFUTED_INTENT_JOIN');
});
test('non-adopted and deferred decision not mistaken for adoption',async()=>{
 for(const disposition of ['REJECT','DEFER']){
   const p=inputs();p.document.owner_decisions[0].disposition=disposition;
   await fail(p,'NOT_ADOPTED');
 }
});
test('cannot launder unrelated finding IDs through the proposal',async()=>{
 const p=inputs();p.proposal.finding_ids=['F999'];await fail(p,'REFUTED_PROPOSAL_JOIN');
});
test('cannot launder accepted finding with no OwnerDecision',async()=>{
 const p=inputs();p.document.owner_decisions=[];await fail(p,'UNKNOWN_DECISION');
});
test('wrong repository and wrong issue comment are refused before provider lookup',async()=>{
 const a=inputs();a.comment_scope.repository='attacker/Common';await fail(a,'CROSS_REPOSITORY');
 const b=inputs();b.comment_scope.issue=787;await fail(b,'REFUTED_SOURCE_LINK');
});
test('mismatched pinned digest is REFUTED, not silently reauthenticated',async()=>{
 const p=inputs();p.document.owner_decisions[0].source.digest='0'.repeat(64);
 const v=await inspect(p,{fetchImpl:fetcher(native())});
 assert.equal(v.status,'REFUTED');assert.equal(v.authorization_granted,false);
});
test('provider unavailable is UNKNOWN, not adopted',async()=>{
 const v=await inspect(inputs(),{fetchImpl:async()=>{throw Error('offline')}});
 assert.equal(v.status,'UNKNOWN');
 assert.equal(v.authorization_granted,false);
});
test('source locator in graph must be a pinned digest-bearing GitHub comment',async()=>{
 const p=inputs();delete p.document.owner_decisions[0].source.digest;
 await fail(p,'UNTRUSTED_DECISION_SOURCE');
});
test('unknown scope candidate never executes a write',async()=>{
 const p=inputs();p.declared_grant.exact_head_sha='0'.repeat(40);
 const v=await inspect(p,{fetchImpl:fetcher(native())});
 assert.equal(v.declared_scope.candidate_scope_match,false);
 assert.equal(v.declared_scope.authorization_granted,false);
 assert.equal(v.live_writer_enabled,false);
});
