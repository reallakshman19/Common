/* Common #294 T17-T21: additive diagnostic-only probes. No DELP, E, CI waiver or writer. */
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
const REPO='reallakshman19/Common',ID=1412133785,SHA=/^[a-f0-9]{40}$/;
const NO={evidence_admitted:false,owner_authenticated:false,reviewer_qualified:false,required_ci_qualified:false,writer_authorized:false,programme_progress:null,delp_projection:'NOT_CALCULATED'};
const id=x=>x?.repository===REPO&&x?.repository_id===ID&&Number.isSafeInteger(x.pr_number)&&x.pr_number>0&&SHA.test(x.head_sha||'')&&/^[A-Za-z0-9][A-Za-z0-9._/-]*$/.test(x.base_branch||'')&&!x.base_branch.includes('..');
/* T22: a diagnostic diff must agree with U02's actual refusal and its own arithmetic. */
function t22DeltaValid(d,reason){
 if(!d||!['STABLE','TRANSITION_ONLY','MEMBERSHIP_ONLY','MEMBERSHIP_AND_TRANSITION'].includes(d.classification))return false;
 for(const k of ['first_count','second_count','added_count','removed_count','transition_count'])
  if(!Number.isSafeInteger(d[k])||d[k]<0||d[k]>200)return false;
 if(d.first_count>200||d.second_count>200||d.second_count!==d.first_count+d.added_count-d.removed_count)return false;
 if(!Array.isArray(d.details)||d.details.length>12||typeof d.details_truncated!=='boolean')return false;
 const member=d.added_count+d.removed_count>0,changing=d.transition_count>0;
 const grade=!member&&!changing?'STABLE':member&&changing?'MEMBERSHIP_AND_TRANSITION':member?'MEMBERSHIP_ONLY':'TRANSITION_ONLY';
 if(d.classification!==grade)return false;
 if(reason==='SELECTED_CHECKS_DRIFT')return grade!=='STABLE';
 return reason===null&&grade==='STABLE';
}
export async function t17(input,diagnose,reader){
 const b={schema:'v35-294-t17',source_grade:'CALLER_INJECTED_UNATTESTED',head_sha:input?.head_sha??null,...NO};
 if(!id(input)||typeof diagnose!=='function'||typeof reader!=='function')return {...b,verdict:'SOURCE_UNVERIFIED',delta:null};
 try{const x=await diagnose(input,reader),d=x?.selected_delta;
  if(x.authority!=='DIAGNOSIS_ONLY_CALLER_INJECTED_UNATTESTED'||x.tested_head_sha!==input.head_sha||x.pr_number!==input.pr_number||x.evidence_admitted!==false||x.positive_ci_qualified!==false||!t22DeltaValid(d,x.u02_failure_reason))return {...b,verdict:'SOURCE_UNVERIFIED',delta:null};
  const first=(d.details||[]).find(y=>Number.isSafeInteger(y.run_id)&&['ADDED','REMOVED','TRANSITION'].includes(y.change));
  return {...b,verdict:x.u02_failure_reason==='SELECTED_CHECKS_DRIFT'?'SELECTED_CHECKS_DRIFT':'DIAGNOSTIC_ONLY',delta:{classification:d.classification,first_count:d.first_count,second_count:d.second_count,added:d.added_count,removed:d.removed_count,transition:d.transition_count,first_job_id:first?.run_id??null,first_change:first?.change??null,old_state:first?.old_state??null,new_state:first?.new_state??null}};
 }catch{return {...b,verdict:'SOURCE_UNVERIFIED',delta:null}}
}
/* T23: an inner U03 fault is causal only for the SAME U04 observation
 * and matching original outer round. Never infer a missing round as FIRST. */
export function t18(x){
 const b={schema:'v35-294-t18',source_grade:'CALLER_INJECTED_UNATTESTED',...NO};
 if(x?.diagnostic_only!==true||x?.source_grade!=='CALLER_INJECTED_UNATTESTED'||
   x?.source_material_attested!==false||x?.positive_fact_admitted!==false||
   !Array.isArray(x?.u03_rounds)||!Number.isSafeInteger(x?.u03_round_count)||
   x.u03_round_count!==x.u03_rounds.length||x.u03_round_count>2||
   !Number.isSafeInteger(x?.original_u04_subreader_calls)||
   x.original_u04_subreader_calls<0||x.original_u04_subreader_calls>6||
   x.no_extra_subreader_calls!==true)return {...b,verdict:'UNVERIFIED',inner:null};
 const bad=x.u03_rounds.find(z=>z?.material_observed===false);
 const join=x.original_u04_failure_stage==='JOIN'&&x.original_u04_failure_reason==='JOIN_U03_SOURCE_UNVERIFIED';
 if(join&&x.result_class!=='U03_NESTED_REFUSAL_CAUSES_JOIN')return {...b,verdict:'UNVERIFIED',inner:null};
 if(join&&!bad)return {...b,verdict:'INNER_REASON_NOT_CAPTURED',inner:null};
 if(!join&&bad)return {...b,verdict:'INNER_NOT_CAUSAL',inner:null};
 if(!join)return {...b,verdict:'NO_U03_REFUSAL_IN_SAMPLE',inner:null};
 if(!['FIRST','SECOND'].includes(bad.outer_round)||bad.outer_round!==x.original_u04_failure_round||
    !['FIRST_READ','FIRST_VALIDATE','SECOND_READ','SECOND_VALIDATE','SECOND_ROUND_DRIFT'].includes(bad.failure_stage)||
    !(/^[A-Z][A-Z0-9_]{0,79}$/.test(bad.failure_reason||'')))
   return {...b,verdict:'INNER_REASON_NOT_CAPTURED',inner:null};
 return {...b,verdict:'SAME_INVOCATION_U03_REASON',
    inner:{stage:bad.failure_stage,reason:bad.failure_reason,outer_round:bad.outer_round}};
}
/* T24: count app-scoped requirements without promoting inaccessible policy
 * to an empty requirement set. Complete page proofs are mandatory. */
export function t19(classic,rules){
 const b={schema:'v35-294-t19',policy:'UNKNOWN',required_count:null,...NO};
 if(classic?.status!==200||rules?.status!==200)
  return {...b,reason:classic?.status!==200?'CLASSIC_GET_UNVERIFIED':'RULES_GET_UNVERIFIED'};
 if(classic.page_complete!==true||rules.page_complete!==true)
  return {...b,reason:'POLICY_PAGINATION_UNVERIFIED'};
 if(!Array.isArray(classic.data?.contexts)||!Array.isArray(classic.data?.checks)||!Array.isArray(rules.data))
  return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
 const refs=new Set(),add=(origin,name,app)=>{
  if(typeof name!=='string'||!name||name.length>250||
    !(app===null||(Number.isSafeInteger(app)&&app>=-1)))return false;
  refs.add(JSON.stringify([origin,name,app]));return true;
 };
 const app=x=>x===undefined?null:x;
 const namedChecks=new Set();
 for(const c of classic.data.checks){
  if(!c||typeof c!=='object'||!add('CLASSIC',c.context,app(c.app_id)))
   return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
  namedChecks.add(c.context);
 }
 for(const c of classic.data.contexts)
  if(typeof c!=='string'||!c)return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
  else if(!namedChecks.has(c)&&!add('CLASSIC',c,null))
    return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
 for(const rule of rules.data){
  if(!rule||typeof rule.type!=='string')return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
  if(rule.type==='required_status_checks'){
   if(!Array.isArray(rule.parameters?.required_status_checks))
    return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
   for(const c of rule.parameters.required_status_checks)
    if(!c||!add('RULESET',c.context,app(c.integration_id)))
      return {...b,reason:'POLICY_SHAPE_UNVERIFIED'};
  }
 }
 const n=refs.size;
 return {...b,policy:'OBSERVED_DIAGNOSTIC_ONLY',required_count:n,
  reason:n?'REQUIREMENTS_PRESENT':'EMPTY_POLICY_READABLE'};
}
/* T26: Historical original-U04 execution is not evidence about this PR HEAD.
 * The T04 native fixture is pinned to historical PR306 and its recorded HEAD.
 * This binding ONLY describes that scope: it cannot elevate source grade. */
export function t26U03SourceScope(current,original){
 const b={schema:'v35-294-t26-u03-source-scope-v1',relationship:'UNVERIFIED',
  observer_pr_number:null,observer_head_sha:null,
  current_pr_u03_verified:false,source_grade:'CALLER_INJECTED_UNATTESTED',...NO};
 if(!id(current)||!original||original.diagnostic_only!==true||
    original.source_grade!=='CALLER_INJECTED_UNATTESTED'||
    original.source_material_attested!==false||
    original.positive_fact_admitted!==false||
    !SHA.test(original.tested_candidate_head||''))
  return b;
 // Source fixture createNativeT04Input is fixed to original PR306.
 const historicPr=306, historicHead='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
 if(original.tested_candidate_head!==historicHead)return b;
 return {...b,observer_pr_number:historicPr,observer_head_sha:historicHead,
  relationship:current.pr_number===historicPr&&current.head_sha===historicHead?
    'SAME_HEAD_DIAGNOSTIC_ONLY':'HISTORICAL_PROXY_NOT_CURRENT'};
}
/* T27: preserve actual failed/pending known checks at the exact SHA.
 * This observes one existing check-runs response; it does NOT decide what
 * branch protection requires and cannot grant evidence or CI clearance. */
export function t27ObservedExactHeadChecks(input,response){
 const b={schema:'v35-294-t27-exact-head-ci-negative-v1',
   observation_grade:'CALLER_INJECTED_UNATTESTED',
   observed_head_sha:input?.head_sha??null,observation_status:'UNKNOWN',
   observed_known_jobs:[],known_failure_count:0,known_pending_count:0,
   known_nonpass_count:0,
   required_check_policy:'UNKNOWN',...NO};
 if(!id(input)||response?.status!==200||response.page_complete!==true)
   return {...b,reason:'CI_GET_UNVERIFIED'};
 const data=response.data;
 if(!data||!Number.isSafeInteger(data.total_count)||!Array.isArray(data.check_runs)||
    data.total_count!==data.check_runs.length||data.check_runs.length>100)
   return {...b,reason:'CI_PAGE_OR_RESPONSE_UNVERIFIED'};
 const allow=new Set(['validate-v3-1-foundation',
  'live-selected-required-ci (windows-latest)','live-selected-required-ci (ubuntu-latest)']);
 const legalStatus=new Set(['queued','in_progress','completed','waiting','pending','requested']);
 const legalConclusion=new Set(['success','failure','timed_out','cancelled','neutral','skipped',
  'action_required','startup_failure','stale']);
 const rows=[];
 for(const x of data.check_runs){
  if(!x||!Number.isSafeInteger(x.id)||x.id<=0||!Number.isSafeInteger(x.app?.id)||
     typeof x.name!=='string'||x.head_sha!==input.head_sha||!legalStatus.has(x.status)||
     (x.status==='completed'&&!legalConclusion.has(x.conclusion))||
     (x.status!=='completed'&&x.conclusion!=null))
   return {...b,reason:'CI_IDENTITY_OR_SHAPE_UNVERIFIED'};
  if(!allow.has(x.name))continue;
  const state=x.status,conclusion=state==='completed'?x.conclusion:null;
  rows.push({name:x.name,check_run_id:x.id,state,conclusion});
 }
 // Refuse two copies of the same check-run identity.
 const ids=rows.map(x=>x.check_run_id);
 if(ids.length!==new Set(ids).size)return {...b,reason:'CI_DUPLICATE_ID_UNVERIFIED'};
 rows.sort((a,b)=>a.name.localeCompare(b.name)||a.check_run_id-b.check_run_id);
 const failed=rows.filter(x=>x.state==='completed'&&
   ['failure','timed_out','cancelled','action_required','startup_failure'].includes(x.conclusion)).length;
 const pending=rows.filter(x=>x.state!=='completed').length;
 // A completed neutral/skipped/stale check is neither success nor pending.
 // It is a separate non-passing outcome; never summarize it as clear.
 const nonpass=rows.filter(x=>x.state==='completed'&&
   ['neutral','skipped','stale'].includes(x.conclusion)).length;
 const grade=failed?'KNOWN_FAILED_CHECK_OBSERVED':
   nonpass?'KNOWN_NONPASS_CHECK_OBSERVED':
   pending?'KNOWN_PENDING_CHECK_OBSERVED':
   rows.length?'KNOWN_CHECKS_COMPLETED_NONFAIL_DIAGNOSTIC_ONLY':
   'NO_KNOWN_CHECK_OBSERVED';
 return {...b,observation_status:grade,
   observed_known_jobs:rows.slice(0,12),known_failure_count:failed,
   known_pending_count:pending,known_nonpass_count:nonpass};
}
export function t20(paths){
 const b={schema:'v35-294-t20',release_ready:false,required_ci_policy:'UNKNOWN',...NO};
 if(!Array.isArray(paths)||paths.length>10000||paths.some(p=>typeof p!=='string'||p.includes('..')))return {...b,verdict:'INVENTORY_UNVERIFIED',missing:[]};
 const expected=['.github/workflows/engineering-pr-delivery-v2.5.yml','.github/workflows/engineering-pr-delivery-v3.yml'];const missing=expected.filter(p=>!paths.includes(p));
 return {...b,verdict:missing.length?'RETIRED_WORKFLOW_PATHS_ABSENT':'LEGACY_PATHS_PRESENT',missing};
}
/* T25: a stable diagnostic is never a qualified Owner/effective-CI gate.
 * The fold is deliberately incapable of returning a release-ready result. */
export function t21(v){
 const b={schema:'v35-294-t21',first_failed_edge:null,verdict:'HOLD_DIAGNOSTIC',
  release_ready:false,unproven_gates:['OWNER_D1_D5','EFFECTIVE_REQUIRED_CI',
    'V31_EXACT_HEAD','U03_HISTORICAL_CAUSE','INDEPENDENT_REVIEW','LOCAL_CUSTODY'],...NO};
 if(!v||v.ci?.schema!=='v35-294-t17'||v.u03?.schema!=='v35-294-t18'||
  v.u03_scope?.schema!=='v35-294-t26-u03-source-scope-v1'||
  v.policy?.schema!=='v35-294-t19'||v.legacy?.schema!=='v35-294-t20'||
  Object.values(v).some(x=>x?.evidence_admitted!==false||x?.writer_authorized!==false))
  return {...b,first_failed_edge:'INPUT_UNVERIFIED'};
 if(v.ci.verdict!=='DIAGNOSTIC_ONLY'||v.ci.delta?.classification!=='STABLE')
  return {...b,first_failed_edge:'U02'};
 if(v.u03_scope.relationship!=='SAME_HEAD_DIAGNOSTIC_ONLY')
  return {...b,first_failed_edge:'U03_HISTORICAL_PROXY_NOT_CURRENT'};
 if(!['NO_U03_REFUSAL_IN_SAMPLE','SAME_INVOCATION_U03_REASON'].includes(v.u03.verdict))
  return {...b,first_failed_edge:'U03_UNVERIFIED'};
 if(v.u03.verdict==='SAME_INVOCATION_U03_REASON')
  return {...b,first_failed_edge:'U03'};
 if(v.policy.policy!=='OBSERVED_DIAGNOSTIC_ONLY')
  return {...b,first_failed_edge:'REQUIRED_POLICY'};
 if(v.legacy.verdict!=='LEGACY_PATHS_PRESENT')
  return {...b,first_failed_edge:'V31_WORKFLOW_PATHS'};
 // No native, independently verified required-status-check policy or V3.1
 // exact-head run is supplied here. Neither can be inferred from a path list.
 return {...b,first_failed_edge:'EFFECTIVE_CI_AND_V31_NOT_QUALIFIED'};
}
async function main(){
 const sha=process.env.CANDIDATE_HEAD_SHA||'',pr=Number(process.env.CANDIDATE_PR_NUMBER),base=process.env.CANDIDATE_BASE_REF||'';
 const input={repository:REPO,repository_id:ID,pr_number:pr,head_sha:sha,base_branch:base};if(!id(input)||execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim()!==sha)throw Error('HEAD_UNVERIFIED');
 const read=async path=>{if(!/^(pulls\/[1-9]\d*|commits\/[a-f0-9]{40}\/(check-runs\?per_page=100|status\?per_page=100)|branches\/[A-Za-z0-9._%/-]+\/protection\/required_status_checks|rules\/branches\/[A-Za-z0-9._%/-]+)$/.test(path)||path.includes('..'))throw Error('ROUTE');const url='https://api.github.com/repos/'+REPO+'/'+path;const headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'v35-294-batch-readonly'};if(process.env.GITHUB_TOKEN)headers.Authorization='Bearer '+process.env.GITHUB_TOKEN;let res=await fetch(url,{headers,redirect:'error',signal:AbortSignal.timeout(15000)});if(res.status!==200||res.redirected||res.url!==url||/rel=["']next["']/.test(res.headers.get('link')||''))return {status:res.status,data:null,page_complete:false};const raw=await res.text();if(Buffer.byteLength(raw)>2000000)throw Error('SIZE');return {status:200,data:JSON.parse(raw),page_complete:true}};
 const {diagnoseU02SelectedDrift}=await import('./t03-selected-ci-drift.mjs');
 const ci=await t17(input,diagnoseU02SelectedDrift,async(r,p)=>{if(r!==REPO)throw Error('REPO');const res=await read(p);if(res.status!==200)throw Error('UNREADABLE');return res.data});
 const {diagnoseU03OriginalCycle,createNativeT04Input,nativeT04Readers}=await import('./t04-u03-original-cycle.mjs');
 const historical='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
 const originalU03=await diagnoseU03OriginalCycle(createNativeT04Input(historical),nativeT04Readers({token:process.env.GITHUB_TOKEN||''}));
 const u03=t18(originalU03),u03_scope=t26U03SourceScope(input,originalU03);
 const policy=t19(await read('branches/'+encodeURIComponent(base)+'/protection/required_status_checks').catch(()=>({status:null})),await read('rules/branches/'+encodeURIComponent(base)).catch(()=>({status:null})));
 const checks=t27ObservedExactHeadChecks(input,
  await read('commits/'+sha+'/check-runs?per_page=100').catch(()=>({status:null,page_complete:false})));
 const files=execFileSync('git',['ls-tree','-r','--name-only','HEAD','--','.github/workflows'],{encoding:'utf8'}).trim().split('\n').filter(Boolean),legacy=t20(files);
 console.log(JSON.stringify({head_sha:sha,ci,u03,u03_scope,policy,legacy,checks,fold:t21({ci,u03,u03_scope,policy,legacy})},null,2));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(()=>{console.error('T17_T21_READ_ONLY_UNVERIFIED');process.exitCode=1});
