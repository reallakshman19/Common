/* U04 native source vector smoke; read-only, deliberately stale U02 comment.
 * The expected PR HEAD and base branch come only from the PR event.
 */
import {observeLiveCrossSource} from './cross-source-vector-v1.mjs';
const result=await observeLiveCrossSource({
 repository:'reallakshman19/Common',repository_id:1412133785,
 root_issue:5,leaf_issue:20,pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
 candidate_head_sha:process.env.CANDIDATE_HEAD_SHA,
 base_branch:process.env.CANDIDATE_BASE_REF,
 evidence_comment_id:6089024942,
 evidence_claimed_head_sha:'f5a30225aea6adde20cef67ca5ab1111a11c3800',
 expected_author_login:'reallakshman19',
});
console.log(JSON.stringify(result,null,2));
if(!result.source_consistent||result.source_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
 result.material_status!=='CONSISTENT_HISTORICAL_EVIDENCE_ONLY'||
 result.evidence_admitted!==false||result.writer_authorized!==false)
 process.exitCode=1;
