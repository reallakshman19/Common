/* #294 T11: read-only PR-only cold entrant rehearsal for T05's real
 * WP2-A→WP2-B candidate PR #308.  NO chat, approved graph, Local authority,
 * independent successor, adopted policy, DELP/writer or release admission.
 * A PR-only link is a starting locator, not permission to resume source writes.
 */
import {pathToFileURL} from 'node:url';
const REPO='reallakshman19/Common',ID=1412133785;
const HEAD='087cf43193febffc31375e71359e767489d3ae68';
const BASE='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const PR_BRANCH='codex/294-t05-wp2a-wp2b-negative-same-head';
const BASE_BRANCH='codex/294-t01-wp2a-u02-u03-u04-pinned';
const URL='https://github.com/'+REPO+'/pull/308';
const ISSUES=[5,20,30,294,289,288];
const SHA=/^[a-f0-9]{40}$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const INJECTED='CALLER_INJECTED_UNATTESTED',NATIVE='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
const canonical=x=>JSON.stringify(x);
function hold(reason,grade,observations=0){
 return Object.freeze({
  schema:'common-v35-294-t11-pr-only-cold-entry-v1',
  entry_url:URL,entry_pr:308,repository:REPO,
  expected_source_head:HEAD,
  observation_grade:grade,source_verified:false,
  material_status:'UNKNOWN',reason,
  source_identity:null,observations,
  owner_authenticated:false,admitted_plan_graph:false,
  evidence_admitted:false,independent_successor_qualified:false,
  reviewer_qualified:false,required_ci_qualified:false,
  delp_projection:'NOT_CALCULATED',programme_progress:null,
  writer_authorized:false,publisher_authorized:false,
  local_responsibility_complete:false,
  next_permitted_action:'READ_ONLY_RECONCILE_D1_D5_AND_REAL_SUCCESSOR',
 });
}
async function run(read,grade,entry){
 if(entry!==URL)return hold('ENTRY_PR_NOT_PINNED',grade);
 if(typeof read!=='function')return hold('PROVIDER_READER_MISSING',grade);
 let rounds=0;
 try{
  async function snap(){
   // One serial, finite current-provider route set. No comments or bodies
   // copied out; no retconning the old PR292 or PR306 source.
   const repo=await read(REPO,'');
   const pr=await read(REPO,'pulls/308');
   if(!obj(repo)||repo.id!==ID||repo.full_name!==REPO||
      !obj(pr)||pr.number!==308||pr.html_url!==URL||pr.state!=='open'||
      pr.head?.repo?.id!==ID||pr.base?.repo?.id!==ID||
      pr.head?.repo?.full_name!==REPO||pr.base?.repo?.full_name!==REPO||
      pr.head?.ref!==PR_BRANCH||pr.base?.ref!==BASE_BRANCH)
     throw 'PR_OR_REPOSITORY_IDENTITY_UNVERIFIED';
   if(!SHA.test(pr.head?.sha||'')||!SHA.test(pr.base?.sha||''))
     throw 'SOURCE_SHA_MALFORMED';
   if(pr.head.sha!==HEAD||pr.base.sha!==BASE)
     throw 'PR_SOURCE_HEAD_OR_BASE_STALE';
   const head=await read(REPO,'git/ref/heads/'+PR_BRANCH);
   const base=await read(REPO,'git/ref/heads/'+BASE_BRANCH);
   if(head?.ref!=='refs/heads/'+PR_BRANCH||head?.object?.sha!==HEAD||
      base?.ref!=='refs/heads/'+BASE_BRANCH||base?.object?.sha!==BASE)
     throw 'SOURCE_BRANCH_REF_STALE';
   for(const issueNumber of ISSUES){
    const issue=await read(REPO,'issues/'+issueNumber);
    if(!obj(issue)||issue.number!==issueNumber||issue.state!=='open'||
       issue.html_url!=='https://github.com/'+REPO+'/issues/'+issueNumber||
       Object.hasOwn(issue,'pull_request'))
      throw 'SOURCE_ISSUE_NOT_VERIFIED';
   }
   rounds++;
   return {
    repository_id:ID,pr_number:308,pr_head:HEAD,pr_branch:PR_BRANCH,
    base_head:BASE,base_branch:BASE_BRANCH,
    source_owner_issue:20,negative_consumer_issue:30,
    coordination_issue:294,programme_issue:5,owner_decisions_issue:289,
    independent_successor_issue:288,
   };
  }
  const first=await snap();
  const second=await snap();
  if(canonical(first)!==canonical(second))return hold('SOURCE_CHANGED_BETWEEN_READS',grade,rounds);
  return Object.freeze({...hold(null,grade,rounds),
   source_verified:true,material_status:'PR_SOURCE_CURRENT_READ_ONLY',
   source_identity:Object.freeze(second),
   // No Owner source/policy/accepted E follows merely from structural PR GET.
   reason:'OWNER_D1_D5_AND_INDEPENDENT_SUCCESSOR_UNRESOLVED',
  });
 }catch(error){
  // Only fixed trusted codes; NEVER raw untrusted HTTP/error text.
  const codes=new Set(['PR_OR_REPOSITORY_IDENTITY_UNVERIFIED',
   'SOURCE_SHA_MALFORMED','PR_SOURCE_HEAD_OR_BASE_STALE',
   'SOURCE_BRANCH_REF_STALE','SOURCE_ISSUE_NOT_VERIFIED']);
  return hold(codes.has(error)?error:'PROVIDER_READ_UNVERIFIED',grade,rounds);
 }
}
export const inspectInjectedPrOnly=(entry,read)=>run(read,INJECTED,entry);
export async function inspectNativePrOnly(entry=URL,opts={}){
 const {nativeGithubGet}=await import('../../MIGRATIONS/V35_COMMON_CUTOVER_20261009/audit-native-provider-v1.mjs');
 return run((r,p)=>nativeGithubGet(r,p,{token:opts.token??process.env.GITHUB_TOKEN??''}),NATIVE,entry);
}
export const PR_ONLY_ENTRY=URL;
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const runHead=process.env.SOURCE_CANDIDATE_SHA||'';
 if(runHead!==HEAD||process.env.PR_ONLY_ENTRY_URL!==URL){
  console.log(JSON.stringify(hold('RUNNER_PIN_MISMATCH',NATIVE)));
  process.exitCode=1;
 }else{
  const x=await inspectNativePrOnly();
  console.log(JSON.stringify(x,null,2));
  // A correctly fenced source is a successful read-only rehearsal only.
  console.log('T11_PR_ONLY_COLD_REHEARSAL='+(x.source_verified?'CURRENT_SOURCE_HOLD':'UNKNOWN_HOLD'));
  if(!x.source_verified)process.exitCode=1;
 }
}
