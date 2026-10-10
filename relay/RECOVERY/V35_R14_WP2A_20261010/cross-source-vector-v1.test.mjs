import test from 'node:test';
import assert from 'node:assert/strict';
import {observeCrossSource} from './cross-source-vector-v1.mjs';
const REPO='reallakshman19/Common',ID=1412133785;
const H1='a'.repeat(40),H2='b'.repeat(40),SHA=x=>'sha256:'+x.repeat(64);
const BASE='recovery/5-m0-reference-identity-census-20261009';
const input=()=>({
  repository:REPO,repository_id:ID,root_issue:5,leaf_issue:20,pr_number:21,
  candidate_head_sha:H2,base_branch:BASE,evidence_comment_id:6089024942,
  evidence_claimed_head_sha:H1,expected_author_login:'reallakshman19',
});
function outputs(i=input(),grade='CALLER_INJECTED_UNATTESTED') {
  const common={source_grade:grade,evidence_admitted:false,programme_progress:null,writer_authorized:false};
  return {
    candidate:{...common,current:true,material_observation:'MATCH_AT_OBSERVATION',
      source_vector_sha256:SHA('a'),source_vector:{
        repository:REPO,provider_repo_id:ID,root_issue:5,leaf_issue:20,pr_number:21,
        candidate_sha:i.candidate_head_sha,base_branch:BASE,
      }},
    ci:{...common,selected_checks_observed:true,snapshot_sha256:SHA('b'),
      required_check_policy:'UNKNOWN',required_checks_result:'UNKNOWN'},
    evidence:{...common,material_observed:true,source_receipt_sha256:SHA('c'),
      source_currentness:i.candidate_head_sha===i.evidence_claimed_head_sha?
        'MATCH_AT_OBSERVATION':'STALE_CANDIDATE_HEAD',
      source_receipt:{
        repository:REPO,repository_id:ID,root_issue:5,leaf_issue:20,
        pr_number:21,comment_id:6089024942,comment_author_login:'reallakshman19',
        current_pr_head_sha:i.candidate_head_sha,claimed_head_sha:i.evidence_claimed_head_sha,
      }},
  };
}
function readers(out=outputs(),fn=()=>{}) {
  let call=0;
  return Object.fromEntries(['candidate','ci','evidence'].map(k=>[k,async args=>{
    fn(++call,k,args,out);
    return structuredClone(out[k]);
  }]));
}
const noGrant=r=>{
  assert.equal(r.evidence_admitted,false);assert.equal(r.owner_authenticated,false);
  assert.equal(r.reviewer_qualified,false);assert.equal(r.required_ci_qualified,false);
  assert.equal(r.delp_projection,'NOT_CALCULATED');assert.equal(r.programme_progress,null);
  assert.equal(r.writer_authorized,false);assert.equal(r.successor_lease,'NOT_PROVEN');
};
test('U04 original-cycle U01/U02/U03 faults identify allowlisted stage and round',async()=>{
  for(const stage of ['U01','U02','U03']){
    for(const round of ['FIRST','SECOND']){
      const out=outputs();
      let n=0,reads=0;
      const r=await observeCrossSource(input(),{
        candidate:async()=>{reads++;if(stage==='U01'&&++n===(round==='FIRST'?1:2))
          throw Error('PRIVATE_PROVIDER_MESSAGE_DO_NOT_LEAK');return structuredClone(out.candidate);},
        ci:async()=>{reads++;if(stage==='U02'&&(round==='FIRST'?reads===2:reads===5))
          throw Error('PRIVATE_PROVIDER_MESSAGE_DO_NOT_LEAK');return structuredClone(out.ci);},
        evidence:async()=>{reads++;if(stage==='U03'&&(round==='FIRST'?reads===3:reads===6))
          throw Error('PRIVATE_PROVIDER_MESSAGE_DO_NOT_LEAK');return structuredClone(out.evidence);},
      });
      assert.equal(r.error,'SOURCE_MATERIAL_UNVERIFIED',stage+' '+round);
      assert.equal(r.failure_stage,stage,stage+' '+round);
      assert.equal(r.failure_round,round,stage+' '+round);
      assert.equal(r.source_consistent,false);assert.equal(r.material_status,'UNKNOWN');
      assert.ok(reads<=(round==='FIRST'?3:6));assert.equal(r.source_vector,null);
      assert.ok(!JSON.stringify(r).includes('PRIVATE_PROVIDER_MESSAGE_DO_NOT_LEAK'));
      noGrant(r);
    }
  }
});
test('U04 JOIN rejected output is classified separately from HTTP provider fault',async()=>{
  const out=outputs();out.candidate.source_vector.candidate_sha=H1;
  const r=await observeCrossSource(input(),readers(out));
  assert.equal(r.error,'SOURCE_MATERIAL_UNVERIFIED');
  assert.equal(r.failure_stage,'JOIN');assert.equal(r.failure_round,'FIRST');
  assert.equal(r.material_status,'UNKNOWN');noGrant(r);
});
test('U04 second-round JOIN misbinding stays UNKNOWN and does not replay as E',async()=>{
  const out=outputs();
  const r=await observeCrossSource(input(),readers(out,(n,k,args,o)=>{
    if(n===4)o.candidate.source_vector.candidate_sha=H1;
  }));
  assert.equal(r.error,'SOURCE_MATERIAL_UNVERIFIED');
  assert.equal(r.failure_stage,'JOIN');assert.equal(r.failure_round,'SECOND');
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 second-round material drift has its own symbolic stage',async()=>{
  const out=outputs();
  const r=await observeCrossSource(input(),readers(out,(n,k,args,o)=>{
    if(n===4)o.ci.snapshot_sha256=SHA('d');
  }));
  assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');
  assert.equal(r.failure_stage,'SECOND_ROUND_DRIFT');
  assert.equal(r.failure_round,'SECOND');
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 success and invalid input cannot impersonate a native failure stage',async()=>{
  const good=await observeCrossSource(input(),readers());
  assert.equal(good.error,null);assert.equal(good.failure_stage,null);
  assert.equal(good.failure_round,null);noGrant(good);
  const bad=await observeCrossSource({...input(),repository:'reallaksh19/Common'},readers());
  assert.equal(bad.error,'INPUT_CONTRACT_INVALID');
  assert.equal(bad.failure_stage,null);assert.equal(bad.failure_round,null);noGrant(bad);
});
test('U04 historical author comment remains visible only as stale material',async()=>{
  let calls=0;const r=await observeCrossSource(input(),readers(outputs(),()=>calls++));
  assert.equal(calls,6);assert.equal(r.source_consistent,true);
  assert.equal(r.material_status,'CONSISTENT_HISTORICAL_EVIDENCE_ONLY');
  assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');
  assert.equal(r.source_vector.evidence_currentness,'STALE_CANDIDATE_HEAD');
  assert.equal(r.source_vector.required_ci_result,'UNKNOWN');
  assert.match(r.source_vector_sha256,/^sha256:[a-f0-9]{64}$/);
  noGrant(r);
});
test('U04 consistent CURRENT author claim does not become accepted evidence',async()=>{
  const i={...input(),candidate_head_sha:H1};
  const r=await observeCrossSource(i,readers(outputs(i)));
  assert.equal(r.source_consistent,true);
  assert.equal(r.material_status,'CONSISTENT_AUTHOR_CLAIM_ONLY');noGrant(r);
});
test('U04 same source vectors produce deterministic digest',async()=>{
  const a=await observeCrossSource(input(),readers());
  const b=await observeCrossSource(input(),readers());
  assert.equal(a.source_vector_sha256,b.source_vector_sha256);
});
test('U04 injecting a native-grade flag cannot turn caller into native',async()=>{
  const r=await observeCrossSource(input(),readers(outputs()),{native:true});
  assert.equal(r.source_grade,'CALLER_INJECTED_UNATTESTED');noGrant(r);
});
test('U04 supposed native sub-stage is rejected from an injected reader',async()=>{
  const r=await observeCrossSource(input(),readers(outputs(input(),'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION')));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 wrong current repo never invokes subordinate stages',async()=>{
  let calls=0;const r=await observeCrossSource({...input(),repository:'reallaksh19/Common'},
    readers(outputs(),()=>calls++));
  assert.equal(calls,0);assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 invented caller authority keys forbidden',async()=>{
  const r=await observeCrossSource({...input(),evidence_admitted:true},readers());
  assert.equal(r.source_consistent,false);assert.equal(r.error,'INPUT_CONTRACT_INVALID');noGrant(r);
});
test('U04 missing source function refuses a partial vector',async()=>{
  const r=await observeCrossSource(input(),{candidate:async()=>outputs().candidate});
  assert.equal(r.error,'SOURCE_READER_MISSING');noGrant(r);
});
test('U04 U01 observed PR head cannot differ from expected head',async()=>{
  const o=outputs();o.candidate.source_vector.candidate_sha=H1;
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.error,'SOURCE_MATERIAL_UNVERIFIED');noGrant(r);
});
test('U04 U01 leaf issue cannot be swapped for parent',async()=>{
  const o=outputs();o.candidate.source_vector.leaf_issue=5;
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 U02 required-check UNKNOWN cannot be claimed PASS',async()=>{
  const o=outputs();o.ci.required_checks_result='ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS';
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 U02 missing selected checks not interchangeable with required policy',async()=>{
  const o=outputs();o.ci.selected_checks_observed=false;
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 forged DELP evidence admission refused',async()=>{
  const o=outputs();o.evidence.evidence_admitted=true;
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 forged writer permission or computed P100 refused',async()=>{
  const o=outputs();o.candidate.writer_authorized=true;o.candidate.programme_progress=100;
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 original/current evidence source roles cannot collapse',async()=>{
  const o=outputs();o.evidence.source_receipt.claimed_head_sha=H2;
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 comment digest changes between rounds and invalidates vector',async()=>{
  const o=outputs(),r=await observeCrossSource(input(),readers(o,(n,k,a,d)=>{
    if(n===4)d.evidence.source_receipt_sha256=SHA('d');
  }));
  assert.equal(r.source_consistent,false);
  assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');noGrant(r);
});
test('U04 check runs change between rounds and invalidate vector',async()=>{
  const o=outputs(),r=await observeCrossSource(input(),readers(o,(n,k,a,d)=>{
    if(n===4)d.ci.snapshot_sha256=SHA('d');
  }));
  assert.equal(r.source_consistent,false);
  assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');noGrant(r);
});
test('U04 current PR head changes between rounds and invalidates vector',async()=>{
  const o=outputs(),r=await observeCrossSource(input(),readers(o,(n,k,a,d)=>{
    if(n===4)d.candidate.source_vector_sha256=SHA('d');
  }));
  assert.equal(r.source_consistent,false);
  assert.equal(r.error,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION');noGrant(r);
});
test('U04 failed provider round remains UNKNOWN and never grants state',async()=>{
  let n=0;const r=await observeCrossSource(input(),{
    candidate:async()=>{n++;if(n===2)throw Error('HTTP 429');return outputs().candidate;},
    ci:async()=>outputs().ci,evidence:async()=>outputs().evidence,
  });
  assert.equal(r.source_consistent,false);noGrant(r);
});
test('U04 current author account requires exact current leaf binding',async()=>{
  const o=outputs();o.evidence.source_receipt.comment_author_login='imposter';
  const r=await observeCrossSource(input(),readers(o));
  assert.equal(r.source_consistent,false);noGrant(r);
});
