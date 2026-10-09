/* WP2-B real provider GET negative admission; issue #30 comment is historic.
 * Must never grant E, Owner, reviewer, lease, DELP or publisher.
 */
import {inspectLivePreAdmission} from './pre-admission-boundary-v1.mjs';
const result=await inspectLivePreAdmission({
 repository:'reallakshman19/Common',repository_id:1412133785,
 root_issue:5,leaf_issue:30,
 pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
 candidate_head_sha:process.env.CANDIDATE_HEAD_SHA,
 base_branch:process.env.CANDIDATE_BASE_REF,
 evidence_comment_id:6090013793,
 evidence_claimed_head_sha:'18de77d3176d87dd347ed95ad313ae330935bf27',
 expected_author_login:'reallakshman19',
 facts_schema_line:'V35',
});
console.log(JSON.stringify(result,null,2));
if(result.source_status!=='REFERENCES_COHERENT_BUT_UNADMITTED'||
 result.observation_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
 !result.admission_blockers.includes('EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN')||
 result.admission!=='NOT_ADMITTED'||result.evidence_admitted!==false||
 result.delp_projector_invoked!==false||result.programme_progress!==null||
 result.writer_authorized!==false||result.owner_authenticated!==false||
 result.reviewer_qualified!==false)process.exitCode=1;
