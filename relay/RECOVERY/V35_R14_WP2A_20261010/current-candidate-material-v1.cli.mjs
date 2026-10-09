import {observeLiveCurrentCandidate} from './current-candidate-material-v1.mjs';

const result=await observeLiveCurrentCandidate({
  repository:'reallakshman19/Common',
  repository_id:1412133785,
  root_issue:5,
  leaf_issue:20,
  pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
  expected_candidate_sha:process.env.CANDIDATE_HEAD_SHA,
  expected_base_ref:process.env.CANDIDATE_BASE_REF,
});
console.log(JSON.stringify(result,null,2));
if (!result.current || result.evidence_admitted || result.writer_authorized) {
  process.exitCode=1;
}
