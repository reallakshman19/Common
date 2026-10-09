/* U05 PR-specific real GitHub GET composite; observation ONLY.
 * Issue comment #6089790172 cites earlier tested PR28 source commit, so
 * it MUST classify as STALE_CANDIDATE_HEAD after this CLI is committed.
 * No Owner/reviewer, required-CI, DELP E, merge or publisher promotion.
 */
import {observeLiveCrossSource} from './cross-source-vector-v1.mjs';
const r=await observeLiveCrossSource({
 repository:'reallakshman19/Common',repository_id:1412133785,
 root_issue:5,leaf_issue:20,
 pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
 candidate_head_sha:process.env.CANDIDATE_HEAD_SHA,
 base_branch:process.env.CANDIDATE_BASE_REF,
 evidence_comment_id:6089790172,
 evidence_claimed_head_sha:'cd08d01d70f4ad034fc352f4ab44079982f33636',
 expected_author_login:'reallakshman19',
});
console.log(JSON.stringify(r,null,2));
if(!r.source_consistent||
 r.source_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
 r.material_status!=='CONSISTENT_HISTORICAL_EVIDENCE_ONLY'||
 r.source_vector?.pr_number!==28||
 r.source_vector?.evidence_currentness!=='STALE_CANDIDATE_HEAD'||
 r.evidence_admitted!==false||r.required_ci_qualified!==false||
 r.writer_authorized!==false||r.programme_progress!==null)
 process.exitCode=1;
