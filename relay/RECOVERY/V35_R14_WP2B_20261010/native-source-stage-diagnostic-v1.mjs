/* WP2-B: post-failure read-only source diagnostics, NEVER an admission path.
 * These separately reacquired source observations are NOT the original U04
 * vector, not atomic and not evidence for DELP or a live writer.
 */
const CODE=/^[A-Z][A-Z0-9_]{0,100}$/;
const tokens=a=>Array.isArray(a)?a.filter(x=>typeof x==='string'&&CODE.test(x)).slice(0,8):[];
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const stage=(v,ok,details={})=>({
  status:object(v)&&ok(v)?'OBSERVED':'UNKNOWN',
  reason_codes:object(v)?tokens(v.errors):['SOURCE_RESULT_NOT_OBJECT'],
  ...details,
});
const marker=(value,allowed)=>allowed.includes(value)?value:'UNKNOWN';
const DIGEST=/^sha256:[a-f0-9]{64}$/;

/** Two *post-failure* U02 observations: a movement indicator, NOT an U04 witness. */
export function comparePostFailureCiWindow(first,last){
  const valid=x=>object(x)&&x.selected_checks_observed===true&&
    x.source_grade==='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'&&
    typeof x.snapshot_sha256==='string'&&DIGEST.test(x.snapshot_sha256);
  const status=!valid(first)||!valid(last)?'UNVERIFIED':
    first.snapshot_sha256===last.snapshot_sha256?'STABLE':'CHANGED';
  return {
    basis:'SEPARATE_POST_FAILURE_NON_ATOMIC_U02_SAMPLES',
    selected_check_window:status,
    required_policy:'UNKNOWN_UNTIL_INDEPENDENTLY_VERIFIED',
    admission:'NOT_ADMITTED',evidence_admitted:false,
    programme_progress:null,writer_authorized:false,
  };
}

export function summarizeSourceStageDiagnostics(candidate,ci,evidence,ciRecheck=null){
  const candidateStage=stage(candidate,x=>x.current===true&&x.material_observation==='MATCH_AT_OBSERVATION');
  const ciStage=stage(ci,x=>x.selected_checks_observed===true,{
    required_policy:marker(ci?.required_check_policy,['UNKNOWN','OBSERVED_CLASSIC_AND_RULESET']),
    required_result:marker(ci?.required_checks_result,[
      'UNKNOWN','ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS','NO_REQUIRED_CHECKS_OBSERVED',
      'REQUIRED_CHECK_FAILED','REQUIRED_CHECK_PENDING_OR_AMBIGUOUS',
    ]),
  });
  const evidenceStage=stage(evidence,x=>x.material_observed===true,{
    comment_currentness:marker(evidence?.source_currentness,[
      'UNKNOWN','MATCH_AT_OBSERVATION','STALE_CANDIDATE_HEAD',
    ]),
  });
  return {
    schema:'common-wp2b-postfailure-stages-v1',
    basis:'INDEPENDENT_POST_FAILURE_NON_ATOMIC_READS',
    stages:{candidate:candidateStage,ci:ciStage,evidence:evidenceStage},
    ci_window:comparePostFailureCiWindow(ci,ciRecheck),
    // These are invariant: this is an untrusted diagnostic, not a U04 witness.
    admission:'NOT_ADMITTED',evidence_admitted:false,owner_authenticated:false,
    reviewer_qualified:false,delp_projector_invoked:false,
    programme_progress:null,writer_authorized:false,
  };
}

export async function diagnoseLiveNativeSourceStages(locator,opts={}){
  const [{observeLiveCurrentCandidate:candidate},
    {observeLiveSelectedRequiredCi:ci},
    {observeLiveEvidenceComment:evidence}]=await Promise.all([
      import('../V35_R14_WP2A_20261010/current-candidate-material-v1.mjs'),
      import('../V35_R14_WP2A_20261010/required-ci-material-v1.mjs'),
      import('../V35_R14_WP2A_20261010/task-evidence-comment-v1.mjs'),
    ]);
  // Do not feed these separate observations back to U04 or WP2-B admissibility.
  const inputs={
    candidate:{repository:locator.repository,repository_id:locator.repository_id,
      root_issue:locator.root_issue,leaf_issue:locator.leaf_issue,
      pr_number:locator.pr_number,expected_candidate_sha:locator.candidate_head_sha,
      expected_base_ref:locator.base_branch},
    ci:{repository:locator.repository,repository_id:locator.repository_id,
      pr_number:locator.pr_number,head_sha:locator.candidate_head_sha,
      base_branch:locator.base_branch},
    evidence:{repository:locator.repository,repository_id:locator.repository_id,
      root_issue:locator.root_issue,leaf_issue:locator.leaf_issue,
      pr_number:locator.pr_number,evidence_comment_id:locator.evidence_comment_id,
      claimed_head_sha:locator.evidence_claimed_head_sha,
      expected_author_login:locator.expected_author_login},
  };
  const safe=async (fn,params)=>{
    try{return await fn(params,opts);}catch{return {errors:['DIAGNOSTIC_READ_THROWN']};}
  };
  // Serial, bounded by each producer's existing native GET timeouts.
  const a=await safe(candidate,inputs.candidate);
  const b=await safe(ci,inputs.ci);
  const c=await safe(evidence,inputs.evidence);
  // Additional U02-only read detects potential movement after the failed U04;
  // it never recovers, replaces, or authorizes the original U04 result.
  const ciRecheck=await safe(ci,inputs.ci);
  return summarizeSourceStageDiagnostics(a,b,c,ciRecheck);
}
