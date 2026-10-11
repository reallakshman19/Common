/* #294 T05: one SAME-HEAD real WP2-A U04 -> WP2-B B01-B03 consumer.
 * WP2-B source is the exact Git blob copied from PR #292, and source
 * ref pins are asserted in CI. Read-only / no retries that upgrade E.
 */
import {inspectLivePreAdmission} from '../V35_R14_WP2B_20261010/pre-admission-boundary-v1.mjs';
import {parseCi02NativeEnvelope} from './ci02-native-eligibility-v1.mjs';
const REPO='reallakshman19/Common';
const CLAIMED='0dbb64b99482e94cd3155074472f600a6d915373',COMMENT=6099896350;
const current=parseCi02NativeEnvelope(process.env);
if(!current||current.sha===CLAIMED){
 console.log('T05_NATIVE_INPUT=INVALID_CANDIDATE_HEAD_OR_PR');
 process.exitCode=1;
}else{
 const {pr,sha:candidate,base}=current;
 console.log('CI02_T05_NATIVE_STARTED='+JSON.stringify({pr,head:candidate,base,repository:REPO}));
 const locator={
  repository:REPO,repository_id:1412133785,root_issue:5,leaf_issue:20,
  pr_number:pr,candidate_head_sha:candidate,base_branch:base,
  evidence_comment_id:COMMENT,evidence_claimed_head_sha:CLAIMED,
  expected_author_login:'reallakshman19',facts_schema_line:'V35',
 };
 const blocked=[
  'ORIGINAL_OWNER_SOURCE_NOT_AUTHENTICATED',
  'EVIDENCE_POLICY_VERSION_NOT_ADOPTED',
  'TWO_INDEPENDENT_REVIEW_VERDICTS_MISSING',
  'R12_R3_NATIVE_WITNESS_NOT_TRANSFERRED',
  'U3_POSITIVE_ADMISSION_NOT_IMPLEMENTED',
  'CANONICAL_PROGRAMME_DELP_NOT_SELECTED',
  'LIVE_PUBLISHER_NOT_AUTHORIZED',
 ];
 const samples=[];
 for(let n=1;n<=5;n++){
  // Each sample is a NEW original one-shot native reader invocation, not
  // a cached retry or conversion of an UNKNOWN observation into accepted E.
  const r=await inspectLivePreAdmission(locator);
  const safe={
   sample:n,source_status:r.source_status,observation_grade:r.observation_grade,
   admission:r.admission,source_digest:r.source_digest,
   blockers:r.admission_blockers,
   evidence_admitted:r.evidence_admitted,owner_authenticated:r.owner_authenticated,
   reviewer_qualified:r.reviewer_qualified,programme_progress:r.programme_progress,
   delp_projector_invoked:r.delp_projector_invoked,writer_authorized:r.writer_authorized,
   target_delp_policy:r.target_delp_policy,
  };
  samples.push(safe);
  const held=r.schema==='common-v35-r12-u3-delp-pre-admission-v1'&&
   r.observation_grade==='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'&&
   r.admission==='NOT_ADMITTED'&&r.evidence_admitted===false&&
   r.owner_authenticated===false&&r.reviewer_qualified===false&&
   r.programme_progress===null&&r.delp_projector_invoked===false&&
   r.writer_authorized===false&&r.target_delp_policy==='NOT_ADOPTED'&&
   blocked.every(x=>r.admission_blockers.includes(x))&&
   (r.source_status==='UNKNOWN'&&r.source_digest===null||
    r.source_status==='REFERENCES_COHERENT_BUT_UNADMITTED'&&
      /^sha256:[a-f0-9]{64}$/.test(r.source_digest||''));
  if(!held){console.log(JSON.stringify({failure:'T05_NEGATIVE_CONTRACT_NOT_PROVEN',samples},null,2));process.exitCode=1;break;}
  if(r.source_status==='REFERENCES_COHERENT_BUT_UNADMITTED')break;
 }
 const coherent=samples.some(x=>x.source_status==='REFERENCES_COHERENT_BUT_UNADMITTED');
 console.log(JSON.stringify({
  schema:'common-v35-294-t05-native-original-pre-admission-v1',
  repository:REPO,pr_number:pr,tested_head:candidate,source_commit_grading:'LIVE_NATIVE_SOURCE_NON_ADMISSION',
  diagnostic_samples:samples.length,coherent_original_source_observed:coherent,
  measured_status:coherent?'NATIVE_SAME_HEAD_REFERENCES_COHERENT_BUT_NOT_ADMITTED':'NATIVE_SAME_HEAD_SOURCE_UNKNOWN_HOLD',
  evidence_admitted:false,delp_projector_invoked:false,writer_authorized:false,
  samples,
 },null,2));
 console.log('T05_NATIVE_CONSUMER='+(coherent?'COHERENT_NOT_ADMITTED':'HOLD_SOURCE_UNVERIFIED')+'; NO DELP OR WRITER');
 if(!coherent)process.exitCode=1;
}
