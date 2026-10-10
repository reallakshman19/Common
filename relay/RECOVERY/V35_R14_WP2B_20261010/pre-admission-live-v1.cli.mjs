/* WP2-B native GET negative admission; B05 #30 comment is historic H1 on PR292.
 * Must never grant E, Owner, reviewer, lease, DELP or publisher.
 */
import {inspectLivePreAdmission} from './pre-admission-boundary-v1.mjs';
const locator={
 repository:'reallakshman19/Common',repository_id:1412133785,
 root_issue:5,leaf_issue:30,
 pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
 candidate_head_sha:process.env.CANDIDATE_HEAD_SHA,
 base_branch:process.env.CANDIDATE_BASE_REF,
 evidence_comment_id:6093641044,
 evidence_claimed_head_sha:'64e494f6cc4bca5764b1b94ff4fe58d16da29d30',
 expected_author_login:'reallakshman19',
 facts_schema_line:'V35',
};
// At most one complete *new* native GET observation after an UNKNOWN result.
// Each attempt is retained in raw CI logs. This is NOT a way to re-grade a
// REFUTED, stale or non-admitted observation and never supplies R3 authority.
let result;
for(let attempt=1;attempt<=2;attempt++){
 result=await inspectLivePreAdmission(locator);
 console.log(JSON.stringify({native_read_attempt:attempt,...result},null,2));
 if(result.source_status!=='UNKNOWN')break;
}
if(result.source_status!=='REFERENCES_COHERENT_BUT_UNADMITTED'||
 result.observation_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
 !result.admission_blockers.includes('EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN')||
 result.admission!=='NOT_ADMITTED'||result.evidence_admitted!==false||
 result.delp_projector_invoked!==false||result.programme_progress!==null||
 result.writer_authorized!==false||result.owner_authenticated!==false||
 result.reviewer_qualified!==false)process.exitCode=1;
