/* WP2-A U02 live diagnostic: required is UNKNOWN on unreadable GitHub policy.
 * Exits nonzero only if candidate/check observation could not be verified.
 * A success exit never certifies required-CI PASS, DELP E or writer authority.
 */
import {observeLiveSelectedRequiredCi} from './required-ci-material-v1.mjs';
const result=await observeLiveSelectedRequiredCi({
  repository:'reallakshman19/Common',repository_id:1412133785,
  pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
  head_sha:process.env.CANDIDATE_HEAD_SHA,
  base_branch:process.env.CANDIDATE_BASE_REF,
});
console.log(JSON.stringify(result,null,2));
if(!result.selected_checks_observed||result.evidence_admitted!==false||result.writer_authorized!==false)
  process.exitCode=1;
