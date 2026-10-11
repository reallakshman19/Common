/* PLAN-17 N06: tiny pure boundary for printing only source-owned WP2-B
 * non-admission facts in native T05 CLI. Never re-attest provider results.
 * No reads, retry, permission, evidence, DELP, or writer code.
 */
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const sources=Object.freeze({
 JOIN_U02_SOURCE_UNVERIFIED:Object.freeze({
  component:'U02',
  stages:['FIRST_SELECTED','SECOND_SELECTED','SOURCE_READBACK'],
  reasons:['SELECTED_CHECKS_DRIFT','REQUIRED_POLICY_DRIFT',
   'CHECK_RUNS_GET_UNVERIFIED','COMMIT_STATUS_GET_UNVERIFIED',
   'SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID','CHECK_RUN_SHAPE_OR_SHA_INVALID',
   'COMMIT_STATUS_SHAPE_INVALID','PR_READBACK_CHANGED'],
 }),
 JOIN_U03_SOURCE_UNVERIFIED:Object.freeze({
  component:'U03',
  stages:['FIRST_VALIDATE','SECOND_VALIDATE','FIRST_READ','SECOND_READ',
    'SECOND_ROUND_DRIFT'],
  reasons:['CURRENT_PR_BINDING_MISSING','HEAD_CLAIM_MISMATCH',
    'COMMENT_IDENTITY_INVALID','NOT_TASK_EVIDENCE','PR_ROLE_INVALID',
    'COMMENT_GET_UNVERIFIED','SOURCE_RECEIPT_CHANGED'],
 }),
});
export function projectNativeSourceFailure(observation){
 if(!obj(observation)||observation.schema!=='common-v35-r12-u3-delp-pre-admission-v1'||
   observation.observation_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
   observation.source_status!=='UNKNOWN'||observation.source_digest!==null||
   observation.admission!=='NOT_ADMITTED'||observation.evidence_admitted!==false||
   observation.owner_authenticated!==false||observation.reviewer_qualified!==false||
   observation.programme_progress!==null||observation.delp_projector_invoked!==false||
   observation.writer_authorized!==false||observation.target_delp_policy!=='NOT_ADOPTED')
   return null;
 const x=observation.source_failure;
 if(!obj(x)||Object.keys(x).sort().join('|')!=='component|edge|inner_reason|inner_stage|round')
   return null;
 const a=sources[x.edge];
 if(!a||a.component!==x.component||!['FIRST','SECOND'].includes(x.round)||
   !a.stages.includes(x.inner_stage)||!a.reasons.includes(x.inner_reason))
   return null;
 return Object.freeze({edge:x.edge,round:x.round,component:x.component,
   inner_stage:x.inner_stage,inner_reason:x.inner_reason});
}
