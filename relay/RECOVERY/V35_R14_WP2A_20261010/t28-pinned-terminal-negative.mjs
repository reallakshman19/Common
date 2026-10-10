/* #294 T28 pinned real GitHub CI failure fixture. Diagnostic-only, never current E.
 * Two exact check-run IDs originate from GitHub workflow runs at immutable PR319 HEAD.
 * The fixture cannot qualify required CI, change DELP, authorize a writer or erase red CI. */
import {pathToFileURL} from 'node:url';
import {t27ObservedExactHeadChecks} from './t17-t21-readonly-batch.mjs';

export const HISTORICAL_SHA='1db18083b70005b6e228b3f40a5c206424c9704d';
export const HISTORICAL_PR=319;
export const HISTORICAL_REPO='reallakshman19/Common';
export const HISTORICAL_ROUTE='commits/'+HISTORICAL_SHA+'/check-runs?per_page=100';
const locator=Object.freeze({repository:HISTORICAL_REPO,repository_id:1412133785,
 pr_number:HISTORICAL_PR,head_sha:HISTORICAL_SHA,
 base_branch:'codex/294-t22-t25-diagnostic-contract-repairs'});
const known=Object.freeze([
 Object.freeze({name:'live-selected-required-ci (windows-latest)',check_run_id:114313556975}),
 Object.freeze({name:'validate-v3-1-foundation',check_run_id:114313557296}),
]);
const refusal=(reason)=>({schema:'v35-294-t28-pinned-terminal-negative-v1',
 inspected_pr:319,inspected_head_sha:HISTORICAL_SHA,
 relationship:'HISTORICAL_PREVIOUS_HEAD_NOT_CURRENT',
 witness:'NOT_VERIFIED',reason,
 witnessed_check_ids:[],observed_check_count:0,
 source_grade:'CALLER_INJECTED_UNATTESTED',required_policy:'UNKNOWN',
 owner_authenticated:false,reviewer_qualified:false,required_ci_qualified:false,
 evidence_admitted:false,programme_progress:null,delp_projection:'NOT_CALCULATED',
 writer_authorized:false,publisher_authorized:false,release_ready:false});
export function t28PinnedTerminalNegative(response){
 const b=refusal('HISTORICAL_PROVIDER_UNVERIFIED');
 // Only T27's existing strict identity, page completeness, total count
 // and exact check-run head-sha contract can qualify diagnostic observations.
 const view=t27ObservedExactHeadChecks(locator,response);
 if(view.observation_status==='UNKNOWN')return b;
 const observed=view.observed_known_jobs;
 if(!Array.isArray(observed))return b;
 const ids=[];
 for(const k of known){
  const same=observed.filter(x=>x.check_run_id===k.check_run_id&&x.name===k.name);
  if(same.length!==1||same[0].state!=='completed'||same[0].conclusion!=='failure')
   return refusal('EXPECTED_HISTORICAL_FAILURE_NOT_VERIFIED');
  ids.push(k.check_run_id);
 }
 return {...b,witness:'TWO_PINNED_HISTORICAL_FAILURES_VERIFIED',reason:null,
  witnessed_check_ids:ids,observed_check_count:view.observed_known_jobs.length};
}
export async function t28ReadHistoricalFailure(reader){
 if(typeof reader!=='function')return refusal('READER_NOT_AVAILABLE');
 try{
  const response=await reader(HISTORICAL_REPO,HISTORICAL_ROUTE);
  return t28PinnedTerminalNegative(response);
 }catch{return refusal('HISTORICAL_PROVIDER_UNVERIFIED');}
}
async function githubCheckRuns(repo,path){
 if(repo!==HISTORICAL_REPO||path!==HISTORICAL_ROUTE)throw Error('ROUTE_UNVERIFIED');
 const token=process.env.GITHUB_TOKEN;
 if(!token)throw Error('TOKEN_UNAVAILABLE');
 const url='https://api.github.com/repos/'+repo+'/'+path;
 const res=await fetch(url,{redirect:'error',signal:AbortSignal.timeout(15000),headers:{
  'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',
  'User-Agent':'v35-294-t28-negative-fixture',
  'Authorization':'Bearer '+token,
 }});
 if(res.status!==200||res.url!==url||res.redirected||
    /rel=["']next["']/.test(res.headers.get('link')||''))
  return {status:res.status,page_complete:false,data:null};
 const raw=await res.text();
 if(Buffer.byteLength(raw)>2_000_000)throw Error('SOURCE_SIZE_UNVERIFIED');
 return {status:200,page_complete:true,data:JSON.parse(raw)};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const result=await t28ReadHistoricalFailure(githubCheckRuns);
 console.log(JSON.stringify(result,null,2));
 if(result.witness!=='TWO_PINNED_HISTORICAL_FAILURES_VERIFIED')process.exitCode=2;
}
