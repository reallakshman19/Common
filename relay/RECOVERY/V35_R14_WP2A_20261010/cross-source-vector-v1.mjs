/* WP2-A/U04: one read-only source vector across EXISTING U01/U02/U03.
 * It derives NO percentage, acceptance, Owner/reviewer identity, writer grant,
 * lease or DELP policy. Six nested stage observations are non-atomic.
 */
import {createHash} from 'node:crypto';
const REPO='reallakshman19/Common', ID=1412133785, SHA=/^[a-f0-9]{40}$/;
const OBJ=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const POS=x=>Number.isSafeInteger(x)&&x>0;
const G_INJECTED='CALLER_INJECTED_UNATTESTED';
const G_NATIVE='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
const HASH=x=>'sha256:'+createHash('sha256').update('wp2a-cross-source-v1\0'+JSON.stringify(x)).digest('hex');
const DIGEST=/^sha256:[0-9a-f]{64}$/;
class JoinError extends Error {
  constructor(code){super(code);this.code=code;}
}
const check=(condition,code)=>{if(!condition)throw new JoinError(code);};
function refuse(grade,error,failureStage=null,failureRound=null,failureReason=null) {
  return Object.freeze({
    schema:'common-v35-wp2a-u04-cross-source-v1',source_grade:grade,
    source_consistent:false,material_status:'UNKNOWN',error,
    failure_stage:failureStage,failure_round:failureRound,
    failure_reason:failureReason,
    source_vector:null,source_vector_sha256:null,
    evidence_admitted:false,owner_authenticated:false,reviewer_qualified:false,
    required_ci_qualified:false,delp_projection:'NOT_CALCULATED',
    programme_progress:null,writer_authorized:false,successor_lease:'NOT_PROVEN',
  });
}
function validInput(i) {
  return OBJ(i)&&Object.keys(i).sort().join('|')===
    ['repository','repository_id','root_issue','leaf_issue','pr_number',
     'candidate_head_sha','base_branch','evidence_comment_id',
     'evidence_claimed_head_sha','expected_author_login'].sort().join('|') &&
    i.repository===REPO&&i.repository_id===ID&&
    [i.root_issue,i.leaf_issue,i.pr_number,i.evidence_comment_id].every(POS)&&
    i.root_issue!==i.leaf_issue&&SHA.test(i.candidate_head_sha)&&
    SHA.test(i.evidence_claimed_head_sha)&&
    typeof i.base_branch==='string'&&/^[A-Za-z0-9][A-Za-z0-9._/-]*$/.test(i.base_branch)&&
    !i.base_branch.includes('..')&&!i.base_branch.includes('//')&&
    typeof i.expected_author_login==='string'&&
    /^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i.test(i.expected_author_login);
}
function taskArgs(i) {
  return {
    candidate:{repository:REPO,repository_id:ID,root_issue:i.root_issue,leaf_issue:i.leaf_issue,
      pr_number:i.pr_number,expected_candidate_sha:i.candidate_head_sha,expected_base_ref:i.base_branch},
    ci:{repository:REPO,repository_id:ID,pr_number:i.pr_number,
      head_sha:i.candidate_head_sha,base_branch:i.base_branch},
    evidence:{repository:REPO,repository_id:ID,root_issue:i.root_issue,leaf_issue:i.leaf_issue,
      pr_number:i.pr_number,evidence_comment_id:i.evidence_comment_id,
      claimed_head_sha:i.evidence_claimed_head_sha,expected_author_login:i.expected_author_login},
  };
}
function verifyOutput(i,out,grade) {
  // Each reason is a fixed source-controlled code, never raw HTTP or comment data.
  check(OBJ(out),'JOIN_OUTPUT_MALFORMED');
  const {candidate:a,ci:b,evidence:c}=out;
  check(OBJ(a),'JOIN_U01_OUTPUT_MALFORMED');
  check(OBJ(b),'JOIN_U02_OUTPUT_MALFORMED');
  check(OBJ(c),'JOIN_U03_OUTPUT_MALFORMED');
  check(a.source_grade===grade&&b.source_grade===grade&&c.source_grade===grade,
        'JOIN_SOURCE_GRADE_MISMATCH');
  check(a.current===true&&a.material_observation==='MATCH_AT_OBSERVATION'&&
        DIGEST.test(a.source_vector_sha256||'')&&OBJ(a.source_vector),
        'JOIN_U01_SOURCE_UNVERIFIED');
  check(b.selected_checks_observed===true&&DIGEST.test(b.snapshot_sha256||''),
        'JOIN_U02_SOURCE_UNVERIFIED');
  check(c.material_observed===true&&DIGEST.test(c.source_receipt_sha256||'')&&
        OBJ(c.source_receipt),'JOIN_U03_SOURCE_UNVERIFIED');
  for(const [value,code] of [[a,'JOIN_U01_AUTHORITY_FORGED'],
    [b,'JOIN_U02_AUTHORITY_FORGED'],[c,'JOIN_U03_AUTHORITY_FORGED']]){
    check(value.evidence_admitted===false&&value.writer_authorized===false&&
          value.programme_progress===null,code);
  }
  const v=a.source_vector,e=c.source_receipt;
  check(v.repository===REPO&&v.provider_repo_id===ID&&v.root_issue===i.root_issue&&
        v.leaf_issue===i.leaf_issue&&v.pr_number===i.pr_number&&
        v.candidate_sha===i.candidate_head_sha&&v.base_branch===i.base_branch,
        'JOIN_U01_BINDING_MISMATCH');
  check(e.repository===REPO&&e.repository_id===ID&&
        e.root_issue===i.root_issue&&e.leaf_issue===i.leaf_issue&&
        e.pr_number===i.pr_number&&e.current_pr_head_sha===i.candidate_head_sha&&
        e.claimed_head_sha===i.evidence_claimed_head_sha&&
        e.comment_id===i.evidence_comment_id&&
        e.comment_author_login===i.expected_author_login,
        'JOIN_U03_BINDING_MISMATCH');
  check(c.source_currentness===(i.candidate_head_sha===i.evidence_claimed_head_sha?
    'MATCH_AT_OBSERVATION':'STALE_CANDIDATE_HEAD'),
    'JOIN_EVIDENCE_CURRENTNESS_MISMATCH');
  check(b.required_check_policy!=='UNKNOWN'||b.required_checks_result==='UNKNOWN',
        'JOIN_REQUIRED_CI_POLICY_MISMATCH');
  return {
    repository:REPO,repository_id:ID,root_issue:i.root_issue,
    leaf_issue:i.leaf_issue,pr_number:i.pr_number,
    candidate_sha:i.candidate_head_sha,base_branch:i.base_branch,
    candidate_source_sha256:a.source_vector_sha256,
    selected_required_ci_sha256:b.snapshot_sha256,
    required_ci_policy:b.required_check_policy,
    required_ci_result:b.required_checks_result,
    evidence_comment_id:i.evidence_comment_id,
    evidence_comment_sha256:c.source_receipt_sha256,
    evidence_claimed_head_sha:i.evidence_claimed_head_sha,
    evidence_currentness:c.source_currentness,
  };
}
async function observe(i,readers,grade) {
  if(!validInput(i))return refuse(grade,'INPUT_CONTRACT_INVALID');
  if(!OBJ(readers)||['candidate','ci','evidence'].some(k=>typeof readers[k]!=='function'))
    return refuse(grade,'SOURCE_READER_MISSING');
  // The stage labels are an allowlist, not provider error/response content.
  // Preserve original U04 refusal and the exact six-read maximum.
  let failureStage='U01',failureRound='FIRST';
  try {
    const args=taskArgs(i);
    const acquire=async()=>{
      // Deliberately serial: all role observations see a bounded order.
      failureStage='U01';
      const a=await readers.candidate(args.candidate);
      failureStage='U02';
      const b=await readers.ci(args.ci);
      failureStage='U03';
      const c=await readers.evidence(args.evidence);
      failureStage='JOIN';
      return verifyOutput(i,{candidate:a,ci:b,evidence:c},grade);
    };
    const first=await acquire();
    failureRound='SECOND';
    const last=await acquire();
    if(JSON.stringify(first)!==JSON.stringify(last))
      return refuse(grade,'SOURCE_VECTOR_CHANGED_DURING_REOBSERVATION',
                    'SECOND_ROUND_DRIFT','SECOND');
    return Object.freeze({
      schema:'common-v35-wp2a-u04-cross-source-v1',source_grade:grade,
      source_consistent:true,
      material_status:last.evidence_currentness==='STALE_CANDIDATE_HEAD'?
        'CONSISTENT_HISTORICAL_EVIDENCE_ONLY':'CONSISTENT_AUTHOR_CLAIM_ONLY',
      error:null,failure_stage:null,failure_round:null,failure_reason:null,
      source_vector:Object.freeze(last),
      source_vector_sha256:HASH(last),
      evidence_admitted:false,owner_authenticated:false,reviewer_qualified:false,
      required_ci_qualified:false,delp_projection:'NOT_CALCULATED',
      programme_progress:null,writer_authorized:false,successor_lease:'NOT_PROVEN',
    });
  } catch(error){
    return refuse(grade,'SOURCE_MATERIAL_UNVERIFIED',failureStage,failureRound,
      failureStage==='JOIN'&&error instanceof JoinError?error.code:null);
  }
}
export const observeCrossSource=(i,readers)=>observe(i,readers,G_INJECTED);
export async function observeLiveCrossSource(i,opts={}) {
  const [{observeLiveCurrentCandidate:current},{observeLiveSelectedRequiredCi:ci},
    {observeLiveEvidenceComment:evidence}]=await Promise.all([
    import('./current-candidate-material-v1.mjs'),
    import('./required-ci-material-v1.mjs'),
    import('./task-evidence-comment-v1.mjs'),
  ]);
  return observe(i,{
    candidate:x=>current(x,opts),
    ci:x=>ci(x,opts),
    evidence:x=>evidence(x,opts),
  },G_NATIVE);
}
