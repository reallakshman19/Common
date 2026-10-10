/* #294 T13, UNADOPTED read-only repository-index candidate link probe.
 * Native verification: Github API GET candidate bytes at exact tested commit,
 * verify Git blob SHA, then confirm PR308, branches, issues and actual issue
 * comments in two separately executed bounded physical provider rounds.
 * This never authenticates Owner intent, approved graph, eligible E, DELP,
 * canonical index publication or independent R4 successor/custody.
 */
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

const REPO='reallakshman19/Common',ID=1412133785;
const API='https://api.github.com/repos/'+REPO;
const PATH='relay/RECOVERY/V35_R14_WP2A_20261010/t13-r4-index-candidate.json';
const HEAD='087cf43193febffc31375e71359e767489d3ae68';
const BASE='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const HEAD_REF='codex/294-t05-wp2a-wp2b-negative-same-head';
const BASE_REF='codex/294-t01-wp2a-u02-u03-u04-pinned';
const SOURCE_PR=308;
const ISSUES=[
 ['programme',5],['e2e_tracker',284],['coordination',294],
 ['wp2a_source',20],['wp2b_consumer',30],['owner_admission',289],
 ['cold_successor',288],['independent_review',12]
];
const COMMENTS=[
 ['t05_native_source',294,6099941506],
 ['t11_cold_entry',294,6100475989],
 ['t12_stale_refusal',294,6100703214]
];
const REASONS=[
 'BAD_TESTED_SHA','CANDIDATE_BYTES_UNVERIFIED','CANDIDATE_INDEX_SCHEMA_OR_LINK_MISMATCH',
 'REPOSITORY_ID_MISMATCH','PR308_IDENTITY_OR_SOURCE_CHANGED',
 'SOURCE_BRANCH_REF_CHANGED','ISSUE_LINK_CHANGED','EVIDENCE_COMMENT_LINK_CHANGED',
 'SOURCE_CHANGED_BETWEEN_PASSES','NATIVE_PROVIDER_GET_FAILED',
 'READ_ONLY_CANDIDATE_LINKS_CURRENT_NOT_GOVERNED'
];
const ERROR=new Set(REASONS),SHA=/^[0-9a-f]{40}$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const link=(kind,n)=>'https://github.com/'+REPO+'/'+kind+'/'+n;
const digestBuffer=b=>createHash('sha1').update(Buffer.concat([Buffer.from('blob '+b.length+'\0'),b])).digest('hex');
function report(grade,status,reason,passes=0,blob=null){
 return Object.freeze({
  schema:'common-v35-294-t13-r4-candidate-check-v1',
  candidate_class:'UNADOPTED_READ_ONLY_FIXTURE',
  index_authority:'NOT_GOVERNED_NOT_CANONICAL',
  entry_route:'REPOSITORY_INDEX_CANDIDATE_ONLY',
  status,reason:ERROR.has(reason)?reason:'NATIVE_PROVIDER_GET_FAILED',
  observation_grade:grade,
  provider_pass_count:passes,index_blob_sha:blob,
  index_links_verified:status==='CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD',
  source_head:HEAD,source_pr:SOURCE_PR,
  r4_independent_trial:'NOT_RUN',
  owner_authenticated:false,admitted_graph:false,
  effective_required_ci_qualified:false,
  evidence_admitted:false,independent_reviewer_qualified:false,
  accepted_task_facts:false,delp_invoked:false,progress:null,
  writer_authorized:false,publisher_authorized:false,
  successor_writer_custody:false,
  next_permitted_action:'RECONCILE_REAL_CANONICAL_INDEX_AND_D1_D5_READ_ONLY',
 });
}
function manifestValid(m){
 if(!obj(m)||m.schema!=='common-v35-294-t13-r4-index-candidate-v1'||
   m.kind!=='UNADOPTED_REPOSITORY_INDEX_CANDIDATE'||
   m.authority!=='CODER_READ_ONLY_FIXTURE_NOT_GOVERNED'||
   m.repository!==REPO||m.repository_id!==ID||!obj(m.source)||
   m.source.pr_number!==SOURCE_PR||m.source.head_sha!==HEAD||
   m.source.base_sha!==BASE||m.source.head_ref!==HEAD_REF||
   m.source.base_ref!==BASE_REF)return false;
 if(!Array.isArray(m.issue_links)||m.issue_links.length!==ISSUES.length||
   !ISSUES.every(([role,n],i)=>obj(m.issue_links[i])&&
     Object.keys(m.issue_links[i]).sort().join(',')==='number,role,url'&&
     m.issue_links[i].role===role&&m.issue_links[i].number===n&&
     m.issue_links[i].url===link('issues',n)))return false;
 if(!Array.isArray(m.evidence_links)||m.evidence_links.length!==COMMENTS.length||
   !COMMENTS.every(([role,n,id],i)=>obj(m.evidence_links[i])&&
     Object.keys(m.evidence_links[i]).sort().join(',')==='comment_id,issue_number,role,url'&&
     m.evidence_links[i].role===role&&m.evidence_links[i].issue_number===n&&
     m.evidence_links[i].comment_id===id&&m.evidence_links[i].url===
       link('issues',n)+'#issuecomment-'+id))return false;
 return Array.isArray(m.unresolved)&&
   m.unresolved.includes('NO_CANONICAL_INDEX')&&
   m.unresolved.includes('INDEPENDENT_R4_NOT_RUN')&&
   m.unresolved.includes('OWNER_D1_D5_PENDING')&&
   m.allowed_next_step==='READ_ONLY_RECONCILE_WITH_GOVERNED_SOURCES';
}
async function run(testedSha,get,grade){
 if(typeof testedSha!=='string'||!SHA.test(testedSha))
   return report(grade,'HOLD_INVALID_TESTED_HEAD','BAD_TESTED_SHA');
 if(typeof get!=='function')return report(grade,'HOLD_PROVIDER_UNVERIFIED','NATIVE_PROVIDER_GET_FAILED');
 let passed=0,previous=null,blob=null;
 try{
  async function once(){
   const meta=await get('contents/'+PATH+'?ref='+testedSha);
   if(!obj(meta)||meta.type!=='file'||meta.path!==PATH||
      meta.encoding!=='base64'||!SHA.test(meta.sha||'')||
      typeof meta.content!=='string'||meta.content.length>16000||
      !/^[a-zA-Z0-9+/=\r\n]+$/.test(meta.content))throw 'CANDIDATE_BYTES_UNVERIFIED';
   const raw=Buffer.from(meta.content.replace(/\s/g,''),'base64');
   if(raw.length<100||raw.length>6000||digestBuffer(raw)!==meta.sha)
     throw 'CANDIDATE_BYTES_UNVERIFIED';
   let m;
   try{m=JSON.parse(raw.toString('utf8'))}catch{throw 'CANDIDATE_BYTES_UNVERIFIED'}
   if(!manifestValid(m))throw 'CANDIDATE_INDEX_SCHEMA_OR_LINK_MISMATCH';

   const repo=await get('');
   if(!obj(repo)||repo.id!==ID||repo.full_name!==REPO)
     throw 'REPOSITORY_ID_MISMATCH';
   const pr=await get('pulls/308');
   if(!obj(pr)||pr.number!==308||pr.html_url!==link('pull',308)||
      pr.state!=='open'||pr.head?.sha!==HEAD||pr.base?.sha!==BASE||
      pr.head?.ref!==HEAD_REF||pr.base?.ref!==BASE_REF||
      pr.head?.repo?.id!==ID||pr.base?.repo?.id!==ID||
      pr.head?.repo?.full_name!==REPO||pr.base?.repo?.full_name!==REPO)
     throw 'PR308_IDENTITY_OR_SOURCE_CHANGED';
   const h=await get('git/ref/heads/'+HEAD_REF);
   const b=await get('git/ref/heads/'+BASE_REF);
   if(!obj(h)||h.ref!=='refs/heads/'+HEAD_REF||h.object?.sha!==HEAD||
      !obj(b)||b.ref!=='refs/heads/'+BASE_REF||b.object?.sha!==BASE)
     throw 'SOURCE_BRANCH_REF_CHANGED';

   for(const [,n] of ISSUES){
    const issue=await get('issues/'+n);
    if(!obj(issue)||issue.number!==n||issue.html_url!==link('issues',n)||
      issue.state!=='open'||Object.hasOwn(issue,'pull_request'))
      throw 'ISSUE_LINK_CHANGED';
   }
   for(const [,n,id] of COMMENTS){
    const comment=await get('issues/comments/'+id);
    if(!obj(comment)||comment.id!==id||
      comment.html_url!==link('issues',n)+'#issuecomment-'+id||
      comment.issue_url!==API+'/issues/'+n)
      throw 'EVIDENCE_COMMENT_LINK_CHANGED';
   }
   const late=await get('pulls/308');
   if(late?.head?.sha!==HEAD||late?.base?.sha!==BASE||
      late?.head?.ref!==HEAD_REF||late?.base?.ref!==BASE_REF)
     throw 'SOURCE_CHANGED_BETWEEN_PASSES';
   passed++;
   return {blob:meta.sha,head:HEAD,base:BASE,
     issue_numbers:ISSUES.map(x=>x[1]),comment_ids:COMMENTS.map(x=>x[2])};
  }
  previous=await once();
  const second=await once();
  if(JSON.stringify(previous)!==JSON.stringify(second))
    return report(grade,'HOLD_DRIFT','SOURCE_CHANGED_BETWEEN_PASSES',passed);
  blob=second.blob;
  return report(grade,'CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD',
    'READ_ONLY_CANDIDATE_LINKS_CURRENT_NOT_GOVERNED',passed,blob);
 }catch(error){
  return report(grade,'HOLD_LINK_OR_PROVIDER',ERROR.has(error)?error:
   'NATIVE_PROVIDER_GET_FAILED',passed);
 }
}
export const inspectInjectedCandidate=(sha,reader)=>
 run(sha,reader,'CALLER_INJECTED_UNATTESTED');
export const CANDIDATE_PATH=PATH;
export async function inspectNativeCandidate(testedSha,{token=process.env.GITHUB_TOKEN??''}={}){
 const routes=new Set([
  '', 'pulls/308','git/ref/heads/'+HEAD_REF,'git/ref/heads/'+BASE_REF,
  ...ISSUES.map(x=>'issues/'+x[1]),...COMMENTS.map(x=>'issues/comments/'+x[2]),
  'contents/'+PATH+'?ref='+testedSha
 ]);
 async function get(route){
  if(!routes.has(route))throw new Error('NOT_ALLOWLISTED');
  const url=API+(route?'/'+route:'');
  const headers={'Accept':'application/vnd.github+json',
   'X-GitHub-Api-Version':'2022-11-28',
   'User-Agent':'common-v35-294-t13-r4-probe'};
  if(token)headers.Authorization='Bearer '+token;
  const response=await fetch(url,{method:'GET',headers,
   redirect:'error',signal:AbortSignal.timeout(15000)});
  if(!response||response.status!==200||response.redirected||
     response.url!==url)throw new Error('NATIVE_GET_FAILED');
  const data=await response.text();
  if(typeof data!=='string'||Buffer.byteLength(data)>2500000)
    throw new Error('NATIVE_BODY_LIMIT');
  return JSON.parse(data);
 }
 return run(testedSha,get,'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const sha=process.env.TESTED_CANDIDATE_HEAD||'';
 const out=await inspectNativeCandidate(sha);
 console.log(JSON.stringify(out,null,2));
 if(out.status!=='CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD'||
   out.provider_pass_count!==2||out.index_blob_sha===null||
   out.r4_independent_trial!=='NOT_RUN'||out.evidence_admitted||
   out.delp_invoked||out.writer_authorized)process.exitCode=1;
 else console.log('T13_NATIVE_R4_CANDIDATE=LINKS_CURRENT_BUT_NOT_CANONICAL; R4=NOT_RUN; E=OFF; DELP=OFF; WRITER=OFF');
}
