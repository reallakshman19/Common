/* V35-294-T03: read-only, non-authoritative diagnosis of U02's two CI reads.
 * NEVER changes U02 equality, retries, required policy, evidence or custody.
 * Check names/status contexts are hashed; no provider body or token is logged.
 */
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {observeSelectedRequiredCi} from './required-ci-material-v1.mjs';

const REPO='reallakshman19/Common';
const HEAD=/^[0-9a-f]{40}$/;
const tag=s=>createHash('sha256').update('v35-294-t03-v1\0'+String(s)).digest('hex').slice(0,16);
const cmp=(a,b)=>String(a).localeCompare(String(b));
function capture(checks,status){
  if(!checks||!status||!Array.isArray(checks.check_runs)||!Array.isArray(status.statuses)||
      !Number.isSafeInteger(checks.total_count)||checks.total_count!==checks.check_runs.length)return null;
  const items=[];
  for(const x of checks.check_runs){
    if(!Number.isSafeInteger(x.id)||typeof x.name!=='string'||!x.app||!Number.isSafeInteger(x.app.id))return null;
    items.push({key:'r:'+x.id,kind:'CHECK_RUN',run_id:x.id,name_hash:tag(x.name),app_id:x.app.id,state:x.status,conclusion:x.conclusion??null});
  }
  // GitHub may emit more than one commit status with the same context. Preserve
  // multiplicity without relying on the provider's array ordering.
  const statuses=status.statuses.map(x=>({name_hash:tag(x.context),state:x.state})).sort((a,b)=>cmp(a.name_hash,b.name_hash)||cmp(a.state,b.state));
  const seen=new Map();
  for(const s of statuses){
    const n=seen.get(s.name_hash)||0;seen.set(s.name_hash,n+1);
    items.push({key:'s:'+s.name_hash+':'+n,kind:'COMMIT_STATUS',run_id:null,name_hash:s.name_hash,app_id:null,state:s.state,conclusion:null});
  }
  if(items.length>200)return null;
  return items.sort((a,b)=>cmp(a.key,b.key));
}
function safeView(x){return {kind:x.kind,run_id:x.run_id,name_hash:x.name_hash,old_state:x.state,old_conclusion:x.conclusion,app_id:x.app_id};}
export function compareSelectedSnapshots(first,second){
  if(!Array.isArray(first)||!Array.isArray(second))return null;
  const a=new Map(first.map(x=>[x.key,x])),b=new Map(second.map(x=>[x.key,x]));
  if(a.size!==first.length||b.size!==second.length)return null;
  let added=0,removed=0,changed=0;
  const details=[];
  for(const [k,v] of a){
    const n=b.get(k);
    if(!n){removed++;details.push({...safeView(v),change:'REMOVED'});continue;}
    if(JSON.stringify(v)!==JSON.stringify(n)){
      changed++;details.push({...safeView(v),change:'TRANSITION',new_state:n.state,new_conclusion:n.conclusion,
        new_app_id:n.app_id,new_name_hash:n.name_hash});
    }
  }
  for(const [k,v] of b)if(!a.has(k)){added++;details.push({...safeView(v),change:'ADDED'});}
  const classification=added||removed?(changed?'MEMBERSHIP_AND_TRANSITION':'MEMBERSHIP_ONLY'):(changed?'TRANSITION_ONLY':'STABLE');
  details.sort((x,y)=>cmp(x.change,y.change)||cmp(x.run_id,y.run_id)||cmp(x.name_hash,y.name_hash));
  return {classification,first_count:first.length,second_count:second.length,
    added_count:added,removed_count:removed,transition_count:changed,
    details:details.slice(0,12),details_truncated:details.length>12};
}
export async function diagnoseU02SelectedDrift(input,read){
  const checks=[],statuses=[];
  const wrapped=async(r,p)=>{
    const response=await read(r,p);
    if(p.endsWith('/check-runs?per_page=100'))checks.push(response);
    if(p.endsWith('/status?per_page=100'))statuses.push(response);
    return response;
  };
  const result=await observeSelectedRequiredCi(input,wrapped);
  const left=checks.length>=1&&statuses.length>=1?capture(checks[0],statuses[0]):null;
  const right=checks.length>=2&&statuses.length>=2?capture(checks[1],statuses[1]):null;
  const delta=compareSelectedSnapshots(left,right);
  return {
    schema:'common-v35-294-t03-selected-drift-diagnostic-v1',
    tested_head_sha:input?.head_sha??null,pr_number:input?.pr_number??null,
    authority:'DIAGNOSIS_ONLY_CALLER_INJECTED_UNATTESTED',
    u02_failure_stage:result.failure_stage,u02_failure_reason:result.failure_reason,
    u02_selected_checks_observed:result.selected_checks_observed,
    u02_required_policy:result.required_check_policy,
    selected_delta:delta,diagnosis:delta?delta.classification:'INCOMPLETE_SOURCE_WINDOW',
    evidence_admitted:false,writer_authorized:false,programme_progress:null,
    positive_ci_qualified:false,
  };
}
async function readNative(r,p,token){
  if(r!==REPO||!(/^(pulls\/[1-9][0-9]*|commits\/[a-f0-9]{40}\/(?:check-runs\?per_page=100|status\?per_page=100)|branches\/[A-Za-z0-9._%/-]+\/protection\/required_status_checks|rules\/branches\/[A-Za-z0-9._%/-]+)$/.test(p))||p.includes('..'))throw Error('ROUTE_DENIED');
  const endpoint='https://api.github.com/repos/'+REPO+'/'+p;
  const headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'v35-294-t03-readonly'};
  if(token)headers.Authorization='Bearer '+token;
  const res=await fetch(endpoint,{headers,redirect:'error',signal:AbortSignal.timeout(15000)});
  if(res.status!==200||res.redirected||res.url!==endpoint||/rel=["']next["']/.test(res.headers.get('link')||''))throw Error('PROVIDER_NOT_VERIFIED');
  const body=await res.text();
  if(Buffer.byteLength(body,'utf8')>2000000)throw Error('RESPONSE_TOO_LARGE');
  return JSON.parse(body);
}
async function main(){
  const head=process.env.CANDIDATE_HEAD_SHA||'',pr=Number(process.env.CANDIDATE_PR_NUMBER),base=process.env.CANDIDATE_BASE_REF||'';
  if(!HEAD.test(head)||pr!==306||!base||base.includes('..'))throw Error('INVALID_PINNED_INPUT');
  const result=await diagnoseU02SelectedDrift({repository:REPO,repository_id:1412133785,pr_number:pr,head_sha:head,base_branch:base},
    (r,p)=>readNative(r,p,process.env.GITHUB_TOKEN||''));
  console.log(JSON.stringify(result,null,2));
  console.log('T03_DIAGNOSTIC_ONLY='+result.diagnosis+'; NO_EVIDENCE_ADMISSION');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  main().catch(()=>{console.error('T03_DIAGNOSTIC_UNVERIFIED; no provider body disclosed');process.exitCode=1;});
}
