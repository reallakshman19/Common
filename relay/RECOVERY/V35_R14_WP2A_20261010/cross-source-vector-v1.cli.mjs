/* U04 native source vector smoke; read-only, deliberately stale U02 comment.
 * The expected PR HEAD and base branch come only from the PR event.
 */
import {observeLiveCrossSource} from './cross-source-vector-v1.mjs';
const result=await observeLiveCrossSource({
 repository:'reallakshman19/Common',repository_id:1412133785,
 root_issue:5,leaf_issue:20,pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
 candidate_head_sha:process.env.CANDIDATE_HEAD_SHA,
 base_branch:process.env.CANDIDATE_BASE_REF,
 evidence_comment_id:6089537374,
 evidence_claimed_head_sha:'4d90d0ff8a72d843c632d44ed4bc90b2a7da3ca1',
 expected_author_login:'reallakshman19',
});
console.log(JSON.stringify(result,null,2));
// Comment 6089537374 is a real historical PR27/PR21 author claim. It is
// deliberately *not* a PR331 author comment; never count a refusal as a
// positive current-source join, or manufacture a new comment/pr binding.
const knownNegative=result.source_consistent===false&&
 result.failure_stage==='JOIN'&&result.failure_round==='FIRST'&&
 result.failure_reason==='JOIN_U03_SOURCE_UNVERIFIED'&&
 result.evidence_admitted===false&&result.writer_authorized===false;
console.log('U04_HISTORICAL_FOREIGN_PR_BINDING='+
  (knownNegative?'REJECTED_AS_REQUIRED':'UNVERIFIED_OTHER_EDGE'));
// This smoke is a positive-join job, so even an EXPECTED negative remains red.
// N02 source tests separately assert the exact CURRENT_PR_BINDING_MISSING reason.
process.exitCode=1;
