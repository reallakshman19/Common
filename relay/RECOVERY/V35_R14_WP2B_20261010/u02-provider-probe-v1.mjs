/* WP2-B read-only incident probe. Runs ONLY after the existing native U02
 * observation is UNKNOWN. It is a NEW non-atomic GET sample, never the U02/U04
 * observation, a source grade, a required-check verdict or an admission grant.
 * Logs no raw provider bodies, endpoint URLs, headers, tokens or check names.
 */
const REPO='reallakshman19/Common', ID=1412133785;
const SHA=/^[a-f0-9]{40}$/;
const BRANCH=/^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const valid=i=>obj(i)&&i.repository===REPO&&i.repository_id===ID&&
  Number.isSafeInteger(i.pr_number)&&i.pr_number>0&&SHA.test(i.candidate_head_sha)&&
  typeof i.base_branch==='string'&&BRANCH.test(i.base_branch)&&
  !i.base_branch.includes('..')&&!i.base_branch.includes('//')&&
  !i.base_branch.endsWith('/')&&!i.base_branch.startsWith('refs/');
const diagnostic=(readings=[])=>({
  schema:'common-wp2b-u02-endpoint-probe-v1',
  basis:'INDEPENDENT_POST_FAILURE_NON_ATOMIC_HTTP_PROBE',
  readings, admission:'NOT_ADMITTED',evidence_admitted:false,
  owner_authenticated:false,reviewer_qualified:false,
  required_ci_qualified:false,delp_projector_invoked:false,
  programme_progress:null,writer_authorized:false,
});
function shape(kind,data,i){
  if(!obj(data))return 'MALFORMED';
  switch(kind){
    case 'PR_IDENTITY':return data.number===i.pr_number&&
      data.head?.sha===i.candidate_head_sha&&data.base?.ref===i.base_branch?
      'MATCH':'MISMATCH';
    case 'SELECTED_CHECK_RUNS':return Number.isSafeInteger(data.total_count)&&
      data.total_count>=0&&Array.isArray(data.check_runs)&&
      data.check_runs.length<=100?
      data.total_count>data.check_runs.length?'PAGINATED_OR_INCOMPLETE':
      data.check_runs.every(x=>obj(x)&&Number.isSafeInteger(x.id)&&
        x.head_sha===i.candidate_head_sha&&typeof x.name==='string'&&
        typeof x.status==='string'&&Number.isSafeInteger(x.app?.id))?
        'SHAPE_COMPATIBLE':'SHAPE_OR_HEAD_MISMATCH':'MALFORMED';
    case 'COMBINED_STATUS':return data.sha===i.candidate_head_sha&&
      Array.isArray(data.statuses)?'SHAPE_COMPATIBLE':'SHAPE_OR_HEAD_MISMATCH';
    case 'CLASSIC_POLICY':return Array.isArray(data.contexts)&&
      Array.isArray(data.checks)?'SHAPE_COMPATIBLE':'MALFORMED';
    case 'BRANCH_RULES':return Array.isArray(data.rules)?'SHAPE_COMPATIBLE':'MALFORMED';
    default:return 'NOT_CHECKED';
  }
}

/** Non-authoritative GET probe. request is injectable for negative tests only. */
export async function probeU02NativeEndpoints(locator,{
  request=fetch,token='',timeoutMs=8000,
}={}){
  if(!valid(locator)||typeof request!=='function')
    return diagnostic([{endpoint:'CONFIG',http:'NOT_RUN',shape:'INVALID_INPUT'}]);
  const h=locator.candidate_head_sha,b=encodeURIComponent(locator.base_branch);
  const paths=[
    ['PR_IDENTITY','pulls/'+locator.pr_number],
    ['SELECTED_CHECK_RUNS','commits/'+h+'/check-runs?per_page=100'],
    ['COMBINED_STATUS','commits/'+h+'/status?per_page=100'],
    ['CLASSIC_POLICY','branches/'+b+'/protection/required_status_checks'],
    ['BRANCH_RULES','rules/branches/'+b],
  ];
  const headers={Accept:'application/vnd.github+json',
    'X-GitHub-Api-Version':'2022-11-28',
    'User-Agent':'common-wp2b-unknown-source-probe'};
  if(token)headers.Authorization='Bearer '+token;
  const readings=[];
  for(const [endpoint,path] of paths){
    const url='https://api.github.com/repos/'+REPO+'/'+path;
    try{
      const response=await request(url,{method:'GET',redirect:'error',headers,
        signal:AbortSignal.timeout(timeoutMs)});
      if(!response||response.redirected||response.url!==url){
        readings.push({endpoint,http:'INVALID_RESPONSE',shape:'NOT_READ'});continue;
      }
      const http=response.status===200?'OK':response.status===403?'FORBIDDEN':
        response.status===429?'RATE_LIMITED':response.status===404?'NOT_FOUND':
        'OTHER_HTTP';
      if(http!=='OK'){readings.push({endpoint,http,shape:'NOT_READ'});continue;}
      if(/rel=["']next["']/.test(response.headers?.get?.('link')||'')){
        readings.push({endpoint,http:'OK',shape:'PAGINATED_OR_INCOMPLETE'});continue;
      }
      const body=await response.text();
      if(Buffer.byteLength(body,'utf8')>2000000){
        readings.push({endpoint,http:'OK',shape:'OVERSIZE'});continue;
      }
      try{
        const parsed=JSON.parse(body);
        readings.push({endpoint,http:'OK',shape:kindShape(endpoint,parsed,locator)});
      }catch{readings.push({endpoint,http:'OK',shape:'MALFORMED'});}
    }catch{
      readings.push({endpoint,http:'TRANSPORT_UNKNOWN',shape:'NOT_READ'});
    }
  }
  return diagnostic(readings);
}
function kindShape(endpoint,parsed,locator){
  if(endpoint==='BRANCH_RULES')return Array.isArray(parsed)?'SHAPE_COMPATIBLE':'MALFORMED';
  return shape(endpoint,parsed,locator);
}
