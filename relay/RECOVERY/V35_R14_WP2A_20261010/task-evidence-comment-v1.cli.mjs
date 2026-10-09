/* Real GitHub read-only U03 historical receipt smoke; intentionally stale to PR HEAD. */
import {observeLiveEvidenceComment} from './task-evidence-comment-v1.mjs';
const result=await observeLiveEvidenceComment({
 repository:'reallakshman19/Common',repository_id:1412133785,
 root_issue:5,leaf_issue:20,pr_number:21,evidence_comment_id:6089024942,
 claimed_head_sha:'f5a30225aea6adde20cef67ca5ab1111a11c3800',
 expected_author_login:'reallakshman19',
});
console.log(JSON.stringify(result,null,2));
if(!result.material_observed||
 result.source_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
 result.source_currentness!=='STALE_CANDIDATE_HEAD'||
 result.evidence_admitted!==false||result.writer_authorized!==false)process.exitCode=1;
