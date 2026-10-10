/* #294 T04: observe U03 inside the ORIGINAL U04 acquisition order.
 * Each actual U01/U02/U03 reader is called once per original U04 cycle.
 * Downshift every upstream provenance grade to CALLER_INJECTED_UNATTESTED:
 * this wrapper is diagnostic and cannot manufacture NATIVE U04 authority.
 * No extra provider GETs, U03 retries, body values, acceptance or writers.
 */
import {pathToFileURL} from 'node:url';
import {observeCrossSource} from './cross-source-vector-v1.mjs';
import {observeLiveCurrentCandidate} from './current-candidate-material-v1.mjs';
import {observeLiveSelectedRequiredCi} from './required-ci-material-v1.mjs';
import {observeLiveEvidenceComment} from './task-evidence-comment-v1.mjs';

const REPO='reallakshman19/Common';
const HISTORIC_HEAD='19af5077fccdd9328f51efc6e316c345b1b4ca78';
const HISTORIC_COMMENT=6098434621;
const BASE='recovery/5-wp2a-u05-integrated-regression-20261010';
const INJECTED='CALLER_INJECTED_UNATTESTED';
const NATIVE='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
const SHA=/^[a-f0-9]{40}$/;
const U03_STAGES=new Set(['FIRST_READ','FIRST_VALIDATE','SECOND_READ','SECOND_VALIDATE','SECOND_ROUND_DRIFT']);
const SAFE_REASON=/^[A-Z][A-Z0-9_]{0,79}$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
function downgrade(x){return obj(x)?{...x,source_grade:INJECTED}:x;}
function safeReason(x){return typeof x==='string'&&SAFE_REASON.test(x)?x:null;}
function safeStage(x){return U03_STAGES.has(x)?x:null;}
function u03Record(x,outerRound){
 return {
   outer_round:outerRound,
   material_observed:x?.material_observed===true,
   source_currentness:x?.source_currentness==='STALE_CANDIDATE_HEAD'?'STALE_CANDIDATE_HEAD':
     x?.source_currentness==='MATCH_AT_OBSERVATION'?'MATCH_AT_OBSERVATION':'UNKNOWN',
   failure_stage:safeStage(x?.failure_stage),
   failure_reason:safeReason(x?.failure_reason),
   source_grade:x?.source_grade===NATIVE?'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION':
     x?.source_grade===INJECTED?INJECTED:'UNKNOWN',
   actor_grade:x?.actor_grade==='GITHUB_ACCOUNT_OBSERVED_NOT_OWNER_AUTHENTICATED'?
     'GITHUB_ACCOUNT_OBSERVED_NOT_OWNER_AUTHENTICATED':'NOT_VERIFIED',
   evidence_admitted:false,
 };
}
function classify(result,records){
 const last=records.at(-1);
 const explicit=records.find(x=>!x.material_observed);
 if(result.failure_stage==='JOIN'&&result.failure_reason==='JOIN_U03_SOURCE_UNVERIFIED'&&
    last&&!last.material_observed)
   return 'U03_NESTED_REFUSAL_CAUSES_JOIN';
 if(explicit)return 'U03_NESTED_REFUSAL_WITH_OTHER_JOIN_OR_STAGE';
 if(result.failure_stage==='SECOND_ROUND_DRIFT')return 'OUTER_SOURCE_VECTOR_DRIFT';
 if(result.source_consistent)return 'DIAGNOSTIC_HISTORICAL_SOURCE_OBSERVED';
 if(result.failure_stage==='JOIN'&&result.failure_reason==='JOIN_U02_SOURCE_UNVERIFIED')
   return 'U02_JOIN_BLOCKED_WITH_U03_OBSERVED';
 if(result.failure_stage==='JOIN'&&result.failure_reason==='JOIN_U01_SOURCE_UNVERIFIED')
   return 'U01_JOIN_BLOCKED_WITH_U03_OBSERVED';
 return 'NO_U03_ROOT_CAUSE_OBSERVED';
}
/** Bounded caller-injected bridge to the original U04 join algorithm.
 * No caller argument can elevate its grade to a native authoritative vector.
 */
export async function diagnoseU03OriginalCycle(i,readers){
 const records=[];
 let round='FIRST',calls=0;
 const guarded=(key,fn)=>async x=>{
   calls++;
   const actual=await fn(x);
   if(key==='evidence')records.push(u03Record(actual,round));
   if(key==='evidence')round='SECOND'; // U04 will next either JOIN then restart, or stop.
   return downgrade(actual);
 };
 const result=await observeCrossSource(i,{
   candidate:guarded('candidate',readers.candidate),
   ci:guarded('ci',readers.ci),
   evidence:guarded('evidence',readers.evidence),
 });
 // Never export receipt, actor ID, comment body, source data, auth or raw error.
 return {
   schema:'common-v35-294-t04-u03-original-cycle-diagnostic-v1',
   tested_candidate_head:i?.candidate_head_sha??null,
   source_grade:INJECTED,
   diagnostic_only:true,
   original_u04_failure_stage:result.failure_stage,
   original_u04_failure_round:result.failure_round,
   original_u04_failure_reason:safeReason(result.failure_reason),
   original_u04_source_consistent:result.source_consistent===true,
   result_class:classify(result,records),
   u03_rounds:records,
   u03_round_count:records.length,
   original_u04_subreader_calls:calls,
   no_extra_subreader_calls:calls<=6,
   source_material_attested:false,
   positive_fact_admitted:false,
   effective_required_ci_qualified:false,
   owner_authenticated:false,
   reviewer_qualified:false,
   delp_projection:'NOT_CALCULATED',
   programme_progress:null,
   writer_authorized:false,
   successor_lease:'NOT_PROVEN',
 };
}
export const createNativeT04Input=head=>({
  repository:REPO,repository_id:1412133785,root_issue:5,leaf_issue:20,pr_number:306,
  candidate_head_sha:head,base_branch:BASE,evidence_comment_id:HISTORIC_COMMENT,
  evidence_claimed_head_sha:HISTORIC_HEAD,expected_author_login:'reallakshman19',
});
export const nativeT04Readers=opts=>({
 candidate:x=>observeLiveCurrentCandidate(x,opts),
 ci:x=>observeLiveSelectedRequiredCi(x,opts),
 evidence:x=>observeLiveEvidenceComment(x,opts),
});
async function main(){
 const head=process.env.CANDIDATE_HEAD_SHA||'',pr=Number(process.env.CANDIDATE_PR_NUMBER),
   base=process.env.CANDIDATE_BASE_REF||'';
 if(!SHA.test(head)||head===HISTORIC_HEAD||pr!==306||base!==BASE)
   throw Error('INVALID_EXACT_HEAD_INPUT');
 const records=[];
 for(let n=1;n<=5;n++){
   const r=await diagnoseU03OriginalCycle(createNativeT04Input(head),
     nativeT04Readers({token:process.env.GITHUB_TOKEN||''}));
   records.push({sample:n,...r});
   if(r.result_class==='U03_NESTED_REFUSAL_CAUSES_JOIN')break;
 }
 const witnessed=records.find(x=>x.result_class==='U03_NESTED_REFUSAL_CAUSES_JOIN');
 console.log(JSON.stringify({
   schema:'common-v35-294-t04-native-sampled-diagnostic-v1',
   candidate_head:head,samples:records,
   historical_u04_join_u03_failures:'OBSERVED_PREVIOUS_HEADS_ONLY',
   same_cycle_u03_refusal_reproduced:!!witnessed,
   diagnosis:witnessed?'U03_NESTED_FAILURE_SYMBOLICALLY_ISOLATED':'HISTORICAL_U03_CAUSE_NOT_REPRODUCED_IN_SAMPLES',
   native_positive_admitted:false,
   effective_required_ci_qualified:false,
   writer_authorized:false,
 },null,2));
 console.log('T04_READ_ONLY_DIAGNOSTIC='+ (witnessed?'U03_REFUSAL_REPRODUCED':'NOT_REPRODUCED')+'; NO_AUTHORITY');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 main().catch(()=>{console.error('T04_READ_ONLY_SOURCE_UNVERIFIED; no provider response disclosed');process.exitCode=1;});
}
