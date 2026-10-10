/* #294 T12: a real PR's H1→H2 head and link drift, read-only.
 * Does not call DELP, mutate provider objects, issue accepted E,
 * grant local/Owner/reviewer authority or run an independent successor.
 * A current GitHub locator is source freshness, not evidence admission.
 */
import {pathToFileURL} from 'node:url';
const REPO='reallakshman19/Common',REPO_ID=1412133785;
const ISSUE_IDS=[5,20,30,288,289,294];
const SHA=/^[a-f0-9]{40}$/;
const BRANCH=/^[A-Za-z0-9][A-Za-z0-9._/-]{0,180}$/;
const OBJ=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const URL=(kind,num)=>'https://github.com/'+REPO+'/'+kind+'/'+num;
const CLONE=x=>JSON.parse(JSON.stringify(x));
const VALID_CODES=new Set([
  'INPUT_INVALID','PR_LINK_REPO_OR_NUMBER_MISMATCH',
  'PR_PROVIDER_IDENTITY_INVALID','PR_HEAD_OR_BASE_REF_INVALID',
  'ISSUE_LINK_IDENTITY_INVALID','SOURCE_REF_DISAGREES_WITH_PR',
  'SOURCE_CHANGED_DURING_DOUBLE_READ',
  'PR_HEAD_CHANGED_SINCE_CHECKPOINT','PR_BASE_CHANGED_SINCE_CHECKPOINT',
  'PROVIDER_READ_UNVERIFIED','SOURCE_CURRENT_OWNER_HOLD',
]);
function result(grade,status,reason,snapshot=null,pass_count=0){
 const isCurrent=status==='CURRENT_SOURCE_READ_ONLY_HOLD';
 return Object.freeze({
  schema:'common-v35-294-t12-pr-head-link-drift-v1',
  status,reason:VALID_CODES.has(reason)?reason:'PROVIDER_READ_UNVERIFIED',
  observation_grade:grade,source_verified:isCurrent,
  provider_pass_count:pass_count,
  observed_head_sha:snapshot?.head_sha??null,
  observed_base_sha:snapshot?.base_sha??null,
  issue_links_verified:!!snapshot&&pass_count===2,
  source_digest:null,  // A head/PR GET is not a hash of accepted task material.
  admission:'NOT_ADMITTED',evidence_admitted:false,
  owner_authenticated:false,admitted_plan_graph:false,
  independent_successor_qualified:false,reviewer_qualified:false,
  required_ci_qualified:false,delp_projector_invoked:false,
  programme_progress:null,writer_authorized:false,
  publisher_authorized:false,local_responsibility_complete:false,
  next_permitted_action:isCurrent?
    'READ_ONLY_HOLD_D1_D5_AND_INDEPENDENT_SUCCESSOR':
    'REFETCH_PR_AND_RECONCILE_H1_H2_NO_ADMISSION',
 });
}
function valid(t){
 return OBJ(t)&&Object.keys(t).sort().join(',')===
   ['repository','repository_id','pr_number','entry_url','head_branch',
    'base_branch','head_expected_sha','base_expected_sha'].sort().join(',')&&
  t.repository===REPO&&t.repository_id===REPO_ID&&
  Number.isSafeInteger(t.pr_number)&&t.pr_number>0&&
  t.entry_url===URL('pull',t.pr_number)&&
  SHA.test(t.head_expected_sha)&&SHA.test(t.base_expected_sha)&&
  [t.head_branch,t.base_branch].every(s=>typeof s==='string'&&BRANCH.test(s)&&
   !s.includes('..')&&!s.includes('//')&&!s.endsWith('/'));
}
async function run(t,read,grade){
 if(!valid(t))return result(grade,'HOLD_INVALID_INPUT','INPUT_INVALID');
 if(typeof read!=='function')return result(grade,'HOLD_UNVERIFIED_SOURCE','PROVIDER_READ_UNVERIFIED');
 let pass=0;
 try{
  async function one(){
   const repo=await read(REPO,'');
   const pr=await read(REPO,'pulls/'+t.pr_number);
   if(!OBJ(repo)||repo.id!==REPO_ID||repo.full_name!==REPO||
      !OBJ(pr)||pr.number!==t.pr_number||pr.html_url!==t.entry_url||
      pr.state!=='open'||pr.draft!==true||
      pr.head?.repo?.full_name!==REPO||pr.head?.repo?.id!==REPO_ID||
      pr.base?.repo?.full_name!==REPO||pr.base?.repo?.id!==REPO_ID)
     throw 'PR_PROVIDER_IDENTITY_INVALID';
   const hs=pr.head?.sha,bs=pr.base?.sha;
   if(!SHA.test(hs||'')||!SHA.test(bs||'')||
      pr.head?.ref!==t.head_branch||pr.base?.ref!==t.base_branch)
     throw 'PR_HEAD_OR_BASE_REF_INVALID';
   const h=await read(REPO,'git/ref/heads/'+t.head_branch);
   const b=await read(REPO,'git/ref/heads/'+t.base_branch);
   if(!OBJ(h)||h.ref!=='refs/heads/'+t.head_branch||h.object?.sha!==hs||
      !OBJ(b)||b.ref!=='refs/heads/'+t.base_branch||b.object?.sha!==bs)
     throw 'SOURCE_REF_DISAGREES_WITH_PR';
   for(const n of ISSUE_IDS){
    const issue=await read(REPO,'issues/'+n);
    if(!OBJ(issue)||issue.number!==n||issue.state!=='open'||
       issue.html_url!==URL('issues',n)||Object.hasOwn(issue,'pull_request'))
      throw 'ISSUE_LINK_IDENTITY_INVALID';
   }
   // Late PR read fences a moving head within each provider GET pass.
   const late=await read(REPO,'pulls/'+t.pr_number);
   if(late?.head?.sha!==hs||late?.base?.sha!==bs||
      late?.head?.ref!==t.head_branch||late?.base?.ref!==t.base_branch)
     throw 'SOURCE_CHANGED_DURING_DOUBLE_READ';
   pass++;
   return {head_sha:hs,base_sha:bs,head_branch:t.head_branch,
           base_branch:t.base_branch,pr:t.pr_number};
  }
  const a=await one(),b=await one();
  if(JSON.stringify(a)!==JSON.stringify(b))
   return result(grade,'HOLD_SOURCE_DRIFT','SOURCE_CHANGED_DURING_DOUBLE_READ',null,pass);
  if(b.head_sha!==t.head_expected_sha)
   return result(grade,'HOLD_STALE_H1','PR_HEAD_CHANGED_SINCE_CHECKPOINT',b,pass);
  if(b.base_sha!==t.base_expected_sha)
   return result(grade,'HOLD_STALE_BASE','PR_BASE_CHANGED_SINCE_CHECKPOINT',b,pass);
  return result(grade,'CURRENT_SOURCE_READ_ONLY_HOLD','SOURCE_CURRENT_OWNER_HOLD',b,pass);
 }catch(err){
  const reason=VALID_CODES.has(err)?err:'PROVIDER_READ_UNVERIFIED';
  return result(grade,'HOLD_UNVERIFIED_SOURCE',reason,null,pass);
 }
}
export const inspectInjectedDrift=(target,read)=>
 run(target,read,'CALLER_INJECTED_UNATTESTED');
export async function inspectNativeDrift(target,{token=process.env.GITHUB_TOKEN??''}={}){
 const {nativeGithubGet}=await import('../../MIGRATIONS/V35_COMMON_CUTOVER_20261009/audit-native-provider-v1.mjs');
 return run(target,(repo,path)=>nativeGithubGet(repo,path,{token}),
  'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
export function targetFromEnvironment(env){
 return {
  repository:REPO,repository_id:REPO_ID,pr_number:Number(env.T12_PR_NUMBER),
  entry_url:env.T12_PR_ENTRY_URL,
  head_branch:env.T12_HEAD_BRANCH,base_branch:env.T12_BASE_BRANCH,
  head_expected_sha:env.T12_CURRENT_H2,base_expected_sha:env.T12_BASE_HEAD,
 };
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const t=targetFromEnvironment(process.env);
 const h1=process.env.T12_RECORDED_H1||'';
 if(!valid(t)||!SHA.test(h1)||h1===t.head_expected_sha||
    process.env.T12_WORKFLOW_HEAD!==t.head_expected_sha){
  console.log(JSON.stringify({status:'HOLD_INVALID_RUNNER_INPUT',admission:'NOT_ADMITTED',
   evidence_admitted:false,writer_authorized:false,delp_projector_invoked:false}));
  process.exitCode=1;
 }else{
  const [now,stale]=await Promise.all([
   inspectNativeDrift(t),
   inspectNativeDrift({...t,head_expected_sha:h1})
  ]);
  const noGrant=x=>x.admission==='NOT_ADMITTED'&&x.evidence_admitted===false&&
    x.delp_projector_invoked===false&&x.writer_authorized===false&&
    x.independent_successor_qualified===false&&x.programme_progress===null;
  console.log(JSON.stringify({
   schema:'common-v35-294-t12-live-h1-h2-original-provider-witness-v1',
   entry:t.entry_url,recorded_H1:h1,provider_current_H2:t.head_expected_sha,
   current:now,stale_historical:stale,
  },null,2));
  if(!(now.status==='CURRENT_SOURCE_READ_ONLY_HOLD'&&now.source_verified&&
    stale.status==='HOLD_STALE_H1'&&!stale.source_verified&&
    stale.reason==='PR_HEAD_CHANGED_SINCE_CHECKPOINT'&&
    stale.observed_head_sha===t.head_expected_sha&&
    now.provider_pass_count===2&&stale.provider_pass_count===2&&
    now.issue_links_verified&&stale.issue_links_verified&&
    noGrant(now)&&noGrant(stale))){
   process.exitCode=1;
  }else console.log('T12_REAL_H1_TO_H2=CURRENT_READ_ONLY_AND_STALE_REFUSED; E=NONE; DELP=OFF; WRITER=OFF');
 }
}
