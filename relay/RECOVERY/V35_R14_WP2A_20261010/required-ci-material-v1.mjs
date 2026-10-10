/* WP2-A/U02: describe current selected checks separately from effective required checks.
 * This NEVER admits E, reviewer, Owner, DELP, lease or writer authority.
 * A successful GitHub Action on its own is never proof that it was required.
 */
import {createHash} from 'node:crypto';
const REPO='reallakshman19/Common', REPO_ID=1412133785;
const SHA=/^[0-9a-f]{40}$/;
const BRANCH=/^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const validBranch=x=>typeof x==='string'&&BRANCH.test(x)&&!x.includes('..')&&!x.includes('//')&&!x.endsWith('/');
const digest=o=>'sha256:'+createHash('sha256').update('wp2a-u02-v1\0'+JSON.stringify(o)).digest('hex');
const sort=(a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b));
class SourceFault extends Error {
  constructor(code){super(code);this.code=code;}
}
const requireSource=(ok,code)=>{if(!ok)throw new SourceFault(code);};
function refusal(grade,errors,selected=[],required=[],failureStage=null,failureReason=null){
  return {
    schema:'common-v35-wp2a-u02-ci-observation-v1',
    source_grade:grade,observed:false,selected_checks_observed:false,errors,
    failure_stage:failureStage,failure_reason:failureReason,
    selected_checks:selected,required_checks:required,
    required_check_policy:'UNKNOWN',required_checks_result:'UNKNOWN',
    evidence_admitted:false,programme_progress:null,writer_authorized:false,
    owner_authenticated:false,reviewer_qualified:false,snapshot_sha256:null,
  };
}
function validateInput(input){
  if(!obj(input)||Object.keys(input).some(x=>!['repository','repository_id','pr_number','head_sha','base_branch'].includes(x)))return ['INPUT_SHAPE_INVALID'];
  const e=[];
  if(input.repository!==REPO||input.repository_id!==REPO_ID)e.push('CURRENT_REPOSITORY_MISMATCH');
  if(!Number.isSafeInteger(input.pr_number)||input.pr_number<1)e.push('PR_NUMBER_INVALID');
  if(!SHA.test(input.head_sha||''))e.push('CANDIDATE_SHA_INVALID');
  if(!validBranch(input.base_branch))e.push('BASE_BRANCH_INVALID');
  return e;
}
const path=input=>({
  pr:'pulls/'+input.pr_number,
  checks:'commits/'+input.head_sha+'/check-runs?per_page=100',
  status:'commits/'+input.head_sha+'/status?per_page=100',
  classic:'branches/'+encodeURIComponent(input.base_branch)+'/protection/required_status_checks',
  rules:'rules/branches/'+encodeURIComponent(input.base_branch),
});
function mustRead(x){if(x===null||x===undefined||obj(x)&&x.__provider_error)throw Error('PROVIDER_NOT_VERIFIED');return x;}
async function identity(input,read){
  const pr=mustRead(await read(REPO,path(input).pr));
  if(!obj(pr)||pr.number!==input.pr_number||pr.html_url!=='https://github.com/'+REPO+'/pull/'+input.pr_number||
    pr.head?.sha!==input.head_sha||pr.base?.ref!==input.base_branch||
    pr.head?.repo?.id!==REPO_ID||pr.base?.repo?.id!==REPO_ID||
    pr.head.repo.full_name!==REPO||pr.base.repo.full_name!==REPO)throw new SourceFault('PR_HEAD_BASE_OR_REPO_MISMATCH');
  return {head_sha:pr.head.sha,base_branch:pr.base.ref,pr_number:pr.number};
}
function selected(input,checkRuns,combined){
  if(!obj(checkRuns)||!Number.isSafeInteger(checkRuns.total_count)||!Array.isArray(checkRuns.check_runs)||
    checkRuns.total_count!==checkRuns.check_runs.length||checkRuns.check_runs.length>100||
    !obj(combined)||combined.sha!==input.head_sha||!Array.isArray(combined.statuses)||
    !Number.isSafeInteger(combined.total_count)||combined.total_count!==combined.statuses.length||combined.statuses.length>100)
    throw new SourceFault('SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID');
  const runIds=new Set();
  const completed=new Set(['success','failure','neutral','cancelled','skipped','timed_out',
    'action_required','startup_failure','stale']);
  const states=new Set(['queued','in_progress','completed','waiting','pending','requested']);
  const runs=checkRuns.check_runs.map(x=>{
    if(!obj(x)||!Number.isSafeInteger(x.id)||x.id<=0||runIds.has(x.id)||
      typeof x.name!=='string'||!x.name||
      x.head_sha!==input.head_sha||!states.has(x.status)||
      (x.status==='completed'?!completed.has(x.conclusion):x.conclusion!==null&&x.conclusion!==undefined)||
      !Number.isSafeInteger(x.app?.id)||x.app.id<=0)
      throw new SourceFault('CHECK_RUN_SHAPE_OR_SHA_INVALID');
    runIds.add(x.id);
    return {kind:'CHECK_RUN',name:x.name,app_id:x.app.id,run_id:x.id,
      state:x.status,conclusion:x.status==='completed'?x.conclusion:null};
  });
  const statuses=combined.statuses.map(x=>{
    if(!obj(x)||typeof x.context!=='string'||!x.context||!['success','failure','error','pending'].includes(x.state))
      throw new SourceFault('COMMIT_STATUS_SHAPE_INVALID');
    return {kind:'COMMIT_STATUS',name:x.context,app_id:null,run_id:null,state:x.state,conclusion:null};
  });
  return [...runs,...statuses].sort(sort);
}
function required(classic,rules){
  if(!obj(classic)||!Array.isArray(classic.contexts)||!Array.isArray(classic.checks)||!Array.isArray(rules))
    throw Error('REQUIRED_POLICY_NOT_READABLE');
  const refs=[];
  const add=(name,appId,origin)=>{
    if(typeof name!=='string'||!name||!(appId===null||Number.isSafeInteger(appId)))throw Error('REQUIRED_CHECK_MALFORMED');
    refs.push({name,app_id:appId,origin});
  };
  for(const n of classic.contexts)add(n,null,'CLASSIC');
  for(const c of classic.checks){if(!obj(c))throw Error('CLASSIC_CHECK_MALFORMED');add(c.context,c.app_id??null,'CLASSIC');}
  for(const rule of rules){
    if(!obj(rule)||typeof rule.type!=='string')throw Error('RULE_MALFORMED');
    if(rule.type!=='required_status_checks')continue;
    const rc=rule.parameters?.required_status_checks;
    if(!Array.isArray(rc))throw Error('RULE_REQUIRED_CHECKS_MALFORMED');
    for(const c of rc){if(!obj(c))throw Error('RULE_REQUIRED_CHECK_MALFORMED');add(c.context,c.integration_id??null,'RULESET');}
  }
  return refs.sort(sort).filter((v,i,a)=>i===0||JSON.stringify(v)!==JSON.stringify(a[i-1]));
}
function evaluate(req,selectedItems){
  if(!req.length)return 'NO_REQUIRED_CHECKS_OBSERVED';
  let pending=false;
  for(const r of req){
    const matches=selectedItems.filter(x=>x.name===r.name&&(r.app_id===null||x.kind==='CHECK_RUN'&&x.app_id===r.app_id));
    if(matches.length!==1){pending=true;continue;}
    const x=matches[0];
    if(x.kind==='CHECK_RUN'&&x.state==='completed'&&x.conclusion==='success')continue;
    if(x.kind==='COMMIT_STATUS'&&x.state==='success')continue;
    if(x.kind==='CHECK_RUN'&&x.state==='completed'&&['failure','timed_out','cancelled','action_required'].includes(x.conclusion)||
      x.kind==='COMMIT_STATUS'&&['failure','error'].includes(x.state))return 'REQUIRED_CHECK_FAILED';
    pending=true;
  }
  return pending?'REQUIRED_CHECK_PENDING_OR_AMBIGUOUS':'ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS';
}
export async function observeSelectedRequiredCi(input,read){
  // A caller-provided reader is untrusted regardless of provider-shaped responses.
  return observeWithGrade(input,read,'CALLER_INJECTED_UNATTESTED');
}
async function observeWithGrade(input,read,grade){
  const bad=validateInput(input);
  if(bad.length)return refusal(grade,bad);
  if(typeof read!=='function')return refusal(grade,['PROVIDER_READER_MISSING']);
  let stage='INITIAL_PR';
  try{
    const initial=await identity(input,read),paths=path(input);
    stage='FIRST_SELECTED';
    const [checkRuns,combined,classic,rules]=(await Promise.allSettled([
      read(REPO,paths.checks),read(REPO,paths.status),read(REPO,paths.classic),read(REPO,paths.rules),
    ])).map(x=>x.status==='fulfilled'?x.value:{__provider_error:true});
    requireSource(checkRuns!==null&&checkRuns!==undefined&&
      !checkRuns.__provider_error,'CHECK_RUNS_GET_UNVERIFIED');
    requireSource(combined!==null&&combined!==undefined&&
      !combined.__provider_error,'COMMIT_STATUS_GET_UNVERIFIED');
    const chosen=selected(input,checkRuns,combined);
    let policy=null;
    try{policy=required(mustRead(classic),mustRead(rules));}catch{/* UNKNOWN is not empty policy */}
    stage='MIDDLE_PR';
    const final=await identity(input,read);
    stage='SECOND_SELECTED';
    const [check2,status2,classic2,rules2]=(await Promise.allSettled([
      read(REPO,paths.checks),read(REPO,paths.status),read(REPO,paths.classic),read(REPO,paths.rules),
    ])).map(x=>x.status==='fulfilled'?x.value:{__provider_error:true});
    requireSource(check2!==null&&check2!==undefined&&
      !check2.__provider_error,'CHECK_RUNS_GET_UNVERIFIED');
    requireSource(status2!==null&&status2!==undefined&&
      !status2.__provider_error,'COMMIT_STATUS_GET_UNVERIFIED');
    const chosen2=selected(input,check2,status2);
    let policy2=null;
    try{policy2=required(mustRead(classic2),mustRead(rules2));}catch{/* UNKNOWN */}
    stage='FINAL_PR';
    const end=await identity(input,read);
    stage='SOURCE_READBACK';
    requireSource(JSON.stringify(final)===JSON.stringify(end),'PR_READBACK_CHANGED');
    requireSource(JSON.stringify(chosen)===JSON.stringify(chosen2),'SELECTED_CHECKS_DRIFT');
    requireSource(JSON.stringify(policy)===JSON.stringify(policy2),'REQUIRED_POLICY_DRIFT');
    const result=policy2===null?'UNKNOWN':evaluate(policy2,chosen2);
    const vector={repository:REPO,repository_id:REPO_ID,...end,selected_checks:chosen2,required_checks:policy2??[],required_checks_result:result};
    return {schema:'common-v35-wp2a-u02-ci-observation-v1',source_grade:grade,observed:policy2!==null,
      selected_checks_observed:true,errors:[],failure_stage:null,failure_reason:null,
      selected_checks:chosen2,required_checks:policy2??[],
      required_check_policy:policy2===null?'UNKNOWN':'OBSERVED_CLASSIC_AND_RULESET',
      required_checks_result:result,snapshot_sha256:digest(vector),
      evidence_admitted:false,programme_progress:null,writer_authorized:false,
      owner_authenticated:false,reviewer_qualified:false};
  }catch(error){
    // No caller-controlled provider exception messages or response values.
    return refusal(grade,['CI_MATERIAL_OR_POLICY_UNVERIFIED'],[],[],
      stage,error instanceof SourceFault?error.code:null);
  }
}
async function githubGet(repo,path,token){
  if(repo!==REPO||!(/^(pulls\/[1-9][0-9]*|commits\/[a-f0-9]{40}\/(?:check-runs\?per_page=100|status\?per_page=100)|branches\/[A-Za-z0-9._%/-]+\/protection\/required_status_checks|rules\/branches\/[A-Za-z0-9._%/-]+)$/.test(path))||path.includes('..'))
    throw Error('ROUTE_DENIED');
  const endpoint='https://api.github.com/repos/'+REPO+'/'+path;
  const headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',
    'User-Agent':'common-v35-wp2a-readonly-ci'};
  if(token)headers.Authorization='Bearer '+token;
  const res=await fetch(endpoint,{method:'GET',redirect:'error',headers,signal:AbortSignal.timeout(15000)});
  if(res.status!==200||res.redirected||res.url!==endpoint)throw Error('PROVIDER_STATUS_UNKNOWN');
  if(/rel=["']next["']/.test(res.headers.get('link')||''))throw Error('PAGINATION_INCOMPLETE');
  const raw=await res.text();
  if(Buffer.byteLength(raw,'utf8')>2000000)throw Error('PROVIDER_SIZE_EXCEEDED');
  return JSON.parse(raw);
}
export async function observeLiveSelectedRequiredCi(input,{token=process.env.GITHUB_TOKEN||''}={}){
  return observeWithGrade(input,(repo,p)=>githubGet(repo,p,token),'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
