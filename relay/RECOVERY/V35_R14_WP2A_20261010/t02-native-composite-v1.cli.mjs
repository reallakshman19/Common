/* #294 T02: one physical original-cycle U01->U02->U03->U04 native GET witness.
 * This is an intentionally read-only, fail-closed diagnostic. The comment from
 * #20 cites the PREVIOUS T01 source HEAD; it is not accepted E or Owner intent.
 * No retries, second projector, source privilege, merge or writer authority.
 */
import {observeLiveCrossSource} from './cross-source-vector-v1.mjs';

const HISTORIC_HEAD='19af5077fccdd9328f51efc6e316c345b1b4ca78';
const HISTORIC_COMMENT_ID=6098434621;
const REPO='reallakshman19/Common';
const expectedPr=306;
const sha=process.env.CANDIDATE_HEAD_SHA||'';
const branch=process.env.CANDIDATE_BASE_REF||'';
const pr=Number(process.env.CANDIDATE_PR_NUMBER);

const candidateValid=pr===expectedPr&&/^[0-9a-f]{40}$/.test(sha)&&
 sha!==HISTORIC_HEAD&&branch==='recovery/5-wp2a-u05-integrated-regression-20261010';
if(!candidateValid){
 console.log('T02_NATIVE_COMPOSITE=INPUT_CONTRACT_INVALID');
 process.exitCode=1;
}else{
 const r=await observeLiveCrossSource({
  repository:REPO,repository_id:1412133785,root_issue:5,leaf_issue:20,
  pr_number:pr,candidate_head_sha:sha,base_branch:branch,
  evidence_comment_id:HISTORIC_COMMENT_ID,evidence_claimed_head_sha:HISTORIC_HEAD,
  expected_author_login:'reallakshman19',
 });
 console.log(JSON.stringify(r,null,2));
 const noAuthority=r.evidence_admitted===false&&r.owner_authenticated===false&&
  r.reviewer_qualified===false&&r.required_ci_qualified===false&&
  r.delp_projection==='NOT_CALCULATED'&&r.programme_progress===null&&
  r.writer_authorized===false&&r.successor_lease==='NOT_PROVEN';
 const currentAndHistorical=r.source_consistent===true&&
  r.source_grade==='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'&&
  r.material_status==='CONSISTENT_HISTORICAL_EVIDENCE_ONLY'&&
  r.source_vector?.repository===REPO&&
  r.source_vector?.repository_id===1412133785&&
  r.source_vector?.root_issue===5&&r.source_vector?.leaf_issue===20&&
  r.source_vector?.pr_number===expectedPr&&
  r.source_vector?.candidate_sha===sha&&r.source_vector?.base_branch===branch&&
  r.source_vector?.evidence_comment_id===HISTORIC_COMMENT_ID&&
  r.source_vector?.evidence_claimed_head_sha===HISTORIC_HEAD&&
  r.source_vector?.evidence_currentness==='STALE_CANDIDATE_HEAD';
 const ok=noAuthority&&currentAndHistorical;
 console.log('T02_NATIVE_COMPOSITE='+(ok?'CONSISTENT_HISTORICAL_ONLY':'HOLD_UNVERIFIED'));
 if(!ok)process.exitCode=1;
}
