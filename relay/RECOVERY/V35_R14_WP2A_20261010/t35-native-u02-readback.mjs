/* #294 T35: exact-worktree native U02 double-read witness. Negative-only.
 * Never retries away selected-check drift or grants effective required CI/E/DELP/writer.
 */
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {observeLiveSelectedRequiredCi} from './required-ci-material-v1.mjs';

const REPO='reallakshman19/Common',RID=1412133785;
const SHA=/^[a-f0-9]{40}$/;
const NO={evidence_admitted:false,owner_authenticated:false,
 reviewer_qualified:false,required_ci_qualified:false,
 writer_authorized:false,release_ready:false,
 programme_progress:null,delp_projection:'NOT_CALCULATED'};
export function t35ReadbackVerdict(input,result,worktreeHead){
 const out={schema:'v35-294-t35-u02-native-readback-v1',
  candidate_head_sha:input?.head_sha??null,observed_head_sha:worktreeHead??null,
  status:'SOURCE_UNVERIFIED',
  failure_stage:null,failure_reason:null,
  selected_checks_observed:false,required_policy:'UNKNOWN',
  source_grade:'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION',
  ...NO};
 if(input?.repository!==REPO||input?.repository_id!==RID||
    !Number.isSafeInteger(input?.pr_number)||input.pr_number<1||
    !SHA.test(input.head_sha||'')||worktreeHead!==input.head_sha||
    typeof input.base_branch!=='string'||!input.base_branch||
    result?.schema!=='common-v35-wp2a-u02-ci-observation-v1'||
    result?.source_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
    result?.evidence_admitted!==false||
    result?.writer_authorized!==false||
    result?.owner_authenticated!==false||
    result?.reviewer_qualified!==false||
    result?.programme_progress!==null||
    !['UNKNOWN','OBSERVED_CLASSIC_AND_RULESET'].includes(result?.required_check_policy)||
    !Array.isArray(result?.errors)||typeof result?.selected_checks_observed!=='boolean')
  return out;
 const failure= result.errors.length>0;
 if(failure&&(result.selected_checks_observed!==false||result.failure_stage===null||
   typeof result.failure_stage!=='string'))
  return out;
 if(!failure&&(result.selected_checks_observed!==true||result.failure_stage!==null||
   result.failure_reason!==null))
  return out;
 const safeStage=new Set(['INITIAL_PR','FIRST_SELECTED','MIDDLE_PR','SECOND_SELECTED','FINAL_PR','SOURCE_READBACK']);
 const safeReason=new Set([
  'PR_HEAD_BASE_OR_REPO_MISMATCH','CHECK_RUNS_GET_UNVERIFIED',
  'COMMIT_STATUS_GET_UNVERIFIED','SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID',
  'CHECK_RUN_SHAPE_OR_SHA_INVALID','COMMIT_STATUS_SHAPE_INVALID',
  'PR_READBACK_CHANGED','SELECTED_CHECKS_DRIFT','REQUIRED_POLICY_DRIFT',
 ]);
 if(failure&&(!safeStage.has(result.failure_stage)||
     !(result.failure_reason===null||safeReason.has(result.failure_reason))))
  return out;
 return {...out,
  status:failure?'NATIVE_DOUBLE_READ_REFUSAL_NOT_ADMITTED':'NATIVE_DOUBLE_READ_DIAGNOSTIC_NOT_ADMITTED',
  failure_stage:failure?result.failure_stage:null,
  failure_reason:failure?result.failure_reason:null,
  selected_checks_observed:result.selected_checks_observed,
  required_policy:result.required_check_policy};
}
async function main(){
 const head=process.env.CANDIDATE_HEAD_SHA||'';
 const input={repository:REPO,repository_id:RID,
  pr_number:Number(process.env.CANDIDATE_PR_NUMBER),
  head_sha:head,base_branch:process.env.CANDIDATE_BASE_REF||''};
 const worktree=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
 if(!SHA.test(head)||worktree!==head)throw Error('T35_WORKTREE_HEAD_UNVERIFIED');
 const native=await observeLiveSelectedRequiredCi(input,{token:process.env.GITHUB_TOKEN||''});
 const verdict=t35ReadbackVerdict(input,native,worktree);
 console.log(JSON.stringify(verdict,null,2));
 if(verdict.status==='SOURCE_UNVERIFIED')process.exitCode=2;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)
 main().catch(()=>{console.error('T35_NATIVE_READBACK_UNVERIFIED');process.exitCode=2});
