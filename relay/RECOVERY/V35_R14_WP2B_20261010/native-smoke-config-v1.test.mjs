import test from 'node:test';
import assert from 'node:assert/strict';
import {buildNativeSmokeConfig, qualifiesNegativeSmoke} from './native-smoke-config-v1.mjs';
const HEAD='a'.repeat(40);
const env=()=>({CANDIDATE_PR_NUMBER:'292',CANDIDATE_HEAD_SHA:HEAD,
 CANDIDATE_BASE_REF:'recovery/5-wp2b-b01-b03-pre-admission-20261010'});
const base=()=>({source_status:'REFERENCES_COHERENT_BUT_UNADMITTED',
 observation_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION',
 source_digest:'sha256:'+'b'.repeat(64),
 admission_blockers:[], admission:'NOT_ADMITTED', evidence_admitted:false,
 delp_projector_invoked:false, programme_progress:null, writer_authorized:false,
 owner_authenticated:false,reviewer_qualified:false});

test('default remains exact historic H1 stale smoke',()=>{
 const out=buildNativeSmokeConfig(env());
 assert.equal(out.mode,'HISTORICAL_STALE');
 assert.equal(out.locator.evidence_comment_id,6093641044);
 assert.equal(out.locator.evidence_claimed_head_sha,'64e494f6cc4bca5764b1b94ff4fe58d16da29d30');
 assert.equal(out.locator.candidate_head_sha,HEAD);
});
test('explicit current comment with matching exact candidate head is read-only',()=>{
 const cfg=buildNativeSmokeConfig({...env(),CURRENT_EVIDENCE_COMMENT_ID:'6099999999',CURRENT_EVIDENCE_CLAIMED_HEAD_SHA:HEAD});
 assert.equal(cfg.mode,'CURRENT_AUTHOR_CLAIM');
 assert.equal(cfg.locator.evidence_comment_id,6099999999);
 assert.equal(cfg.locator.evidence_claimed_head_sha,HEAD);
 assert.equal(cfg.locator.expected_author_login,'reallakshman19');
 assert.equal(Object.hasOwn(cfg.locator,'admission'),false);
});
test('partial current override fails before native GET',()=>{
 assert.throws(()=>buildNativeSmokeConfig({...env(),CURRENT_EVIDENCE_COMMENT_ID:'6099999999'}),/CURRENT_EVIDENCE_CONFIG_INVALID/);
 assert.throws(()=>buildNativeSmokeConfig({...env(),CURRENT_EVIDENCE_CLAIMED_HEAD_SHA:HEAD}),/CURRENT_EVIDENCE_CONFIG_INVALID/);
});
test('bad current comment number or SHA cannot be used as input',()=>{
 for(const n of ['0','-1','12.2','abc','01',''])
  assert.throws(()=>buildNativeSmokeConfig({...env(),CURRENT_EVIDENCE_COMMENT_ID:n,CURRENT_EVIDENCE_CLAIMED_HEAD_SHA:HEAD}),/CURRENT_EVIDENCE_CONFIG_INVALID/);
 assert.throws(()=>buildNativeSmokeConfig({...env(),CURRENT_EVIDENCE_COMMENT_ID:'6099999999',CURRENT_EVIDENCE_CLAIMED_HEAD_SHA:'fake'}),/CURRENT_EVIDENCE_CONFIG_INVALID/);
});
test('current override cannot claim a different candidate HEAD',()=>{
 assert.throws(()=>buildNativeSmokeConfig({...env(),CURRENT_EVIDENCE_COMMENT_ID:'6099999999',CURRENT_EVIDENCE_CLAIMED_HEAD_SHA:'c'.repeat(40)}),/CURRENT_EVIDENCE_HEAD_NOT_CURRENT/);
});
test('missing or malformed PR/head/base inputs fail closed',()=>{
 for(const bad of [{CANDIDATE_PR_NUMBER:'0'},{CANDIDATE_HEAD_SHA:'HEAD'},{CANDIDATE_BASE_REF:''}])
  assert.throws(()=>buildNativeSmokeConfig({...env(),...bad}),/CANDIDATE_CONFIG_INVALID/);
});
test('historical smoke requires real stale classification and all negatives',()=>{
 const o=base();o.admission_blockers=['EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN'];
 assert.equal(qualifiesNegativeSmoke(o,'HISTORICAL_STALE'),true);
 assert.equal(qualifiesNegativeSmoke(o,'CURRENT_AUTHOR_CLAIM'),false);
});
test('current author material passes diagnostic only, with zero admission',()=>{
 const o=base();o.admission_blockers=['EVIDENCE_POLICY_VERSION_NOT_ADOPTED','U3_POSITIVE_ADMISSION_NOT_IMPLEMENTED'];
 assert.equal(qualifiesNegativeSmoke(o,'CURRENT_AUTHOR_CLAIM'),true);
 assert.equal(o.admission,'NOT_ADMITTED');
 assert.equal(qualifiesNegativeSmoke(o,'HISTORICAL_STALE'),false);
});
test('current mode rejects stale or absent source fingerprint',()=>{
 const o=base();o.admission_blockers=['EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN'];
 assert.equal(qualifiesNegativeSmoke(o,'CURRENT_AUTHOR_CLAIM'),false);
 o.admission_blockers=[];o.source_digest=null;
 assert.equal(qualifiesNegativeSmoke(o,'CURRENT_AUTHOR_CLAIM'),false);
});
test('no current or historical mode can launder admission or a writer',()=>{
 const o=base();o.admission_blockers=['EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN'];
 for(const [key,value] of [['admission','ADMITTED'],['evidence_admitted',true],
  ['writer_authorized',true],['owner_authenticated',true],['reviewer_qualified',true],
  ['delp_projector_invoked',true],['programme_progress',100]]){
   const modified={...o,[key]:value};
   assert.equal(qualifiesNegativeSmoke(modified,'HISTORICAL_STALE'),false,key);
  }
});
test('UNKNOWN or forged native grade is not an eligible native diagnostic',()=>{
 const o=base();o.admission_blockers=['EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN'];
 assert.equal(qualifiesNegativeSmoke({...o,source_status:'UNKNOWN'},'HISTORICAL_STALE'),false);
 assert.equal(qualifiesNegativeSmoke({...o,observation_grade:'CALLER_INJECTED_UNATTESTED'},'HISTORICAL_STALE'),false);
});
