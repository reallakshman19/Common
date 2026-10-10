import test from 'node:test';
import assert from 'node:assert/strict';
import {foldHandover} from './t16-diagnostic-handover.mjs';
const G='CALLER_INJECTED_UNATTESTED',H='087cf43193febffc31375e71359e767489d3ae68';
const B='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const common={observation_grade:G,evidence_admitted:false,delp_invoked:false,
 writer_authorized:false,publisher_authorized:false,programme_progress:null};
function values(){return [
 {...common,status:'CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD',
  index_authority:'NOT_GOVERNED_NOT_CANONICAL',r4_independent_trial:'NOT_RUN',
  provider_pass_count:2},
 {...common,status:'SOURCE_BLOBS_CURRENT_READ_ONLY_HOLD',provider_pass_count:2,
   verified_blob_count:16},
 {...common,status:'AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD',
   provider_pass_count:2,comment_owner_authenticated:false,
   claim_grade:'AUTHOR_DIAGNOSTIC_ONLY_UNATTESTED_OWNER'},
 {status:'CURRENT_SOURCE_PR308_AFTER_CHAIN',observation_grade:G,
  observed_head_sha:H,observed_base_sha:B}
];}
function negatives(v){
 assert.equal(v.handover_class,'CODER_GENERATED_DIAGNOSTIC_ONLY');
 assert.equal(v.canonical_index,'NOT_QUALIFIED');
 assert.equal(v.independent_successor,'NOT_RUN');
 assert.equal(v.evidence_admitted,false);assert.equal(v.delp_invoked,false);
 assert.equal(v.writer_authorized,false);assert.equal(v.publisher_authorized,false);
 assert.equal(v.programme_progress,null);assert.equal(v.owner_authenticated,false);
 assert.equal(v.no_chat_successor_executed,false);
}
test('T16 complete three stage source chain + last read only produces HOLD handover',()=>{
 const a=values(),v=foldHandover(...a);
 assert.equal(v.status,'READ_ONLY_HANDOVER_READY_HOLD');
 assert.equal(v.source_currentness,'SOURCE_PR308_LAST_READ_CURRENT_NOT_ATOMIC');
 assert.equal(v.next_permitted_action,'OWNER_D1_D5_AND_GOVERNED_INDEX_PLUS_EXTERNAL_B_REQUIRED');negatives(v);
});
test('T16 first failure is index with wrong/unknown source links',()=>{
 const a=values();a[0].status='HOLD_LINK_OR_PROVIDER';
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'INDEX_NOT_VERIFIED');negatives(v);
});
test('T16 source blob mismatch refuses handover even with live index',()=>{
 const a=values();a[1].status='HOLD_SOURCE_BLOBS';
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'BLOBS_NOT_VERIFIED');negatives(v);
});
test('T16 comment text drift refuses handover even with valid SHA links',()=>{
 const a=values();a[2].status='HOLD_COMMENT_DRIFT';
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'COMMENTS_NOT_VERIFIED');negatives(v);
});
test('T16 source moved after all 3 validations denies stale read',()=>{
 const a=values();a[3].observed_head_sha='a'.repeat(40);
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'LINKED_SOURCE_CONTRACT_INCOMPLETE');negatives(v);
});
test('T16 missing final physical read denies handover',()=>{
 const a=values();a[3]=null;
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'LAST_NOT_VERIFIED');negatives(v);
});
test('T16 link source count 15/16 cannot claim complete original source',()=>{
 const a=values();a[1].verified_blob_count=15;
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'LINKED_SOURCE_CONTRACT_INCOMPLETE');negatives(v);
});
test('T16 index claims to be canonical -> even current links cannot create qualification',()=>{
 const a=values();a[0].index_authority='OWNER_APPROVED_CANONICAL';
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'LINKED_SOURCE_CONTRACT_INCOMPLETE');negatives(v);
});
test('T16 false author evidence acceptance is rejected',()=>{
 const a=values();a[2].evidence_admitted=true;
 const v=foldHandover(...a);
 assert.equal(v.first_failure,'COMMENTS_CLAIMS_AUTHORITY');negatives(v);
});
test('T16 injected test results cannot be relabeled as native',()=>{
 const a=values(),v=foldHandover(...a,{native:true});
 assert.equal(v.status,'HOLD_FAILED_SOURCE_EDGE');
 assert.equal(v.first_failure,'INDEX_NOT_VERIFIED');negatives(v);
});
test('T16 native-shaped source with spoofed first stage is rejected',()=>{
 const a=values();for(const stage of a)stage.observation_grade='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
 a[0].evidence_admitted=true;
 const v=foldHandover(...a,{native:true});
 assert.equal(v.first_failure,'INDEX_CLAIMS_AUTHORITY');negatives(v);
});
