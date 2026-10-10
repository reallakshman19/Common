/* #294 T16: T13 index + T14 original bytes + T15 comment meaning
 * → one narrow READ-ONLY handover consumer. These physical GET rounds are
 * SERIAL AND NON-ATOMIC. No Local lease, no genuine independent cold B,
 * no admitted E, no release and no second DELP.
 */
import {pathToFileURL} from 'node:url';
import {inspectNativeCandidate} from './t13-r4-index-candidate.mjs';
import {inspectNativeSourceBlobs} from './t14-source-blob-closure.mjs';
import {inspectNativeComments} from './t15-comment-provenance.mjs';

const H='087cf43193febffc31375e71359e767489d3ae68';
const B='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const REPO='reallakshman19/Common';
const G='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
function allNoAuthority(v){
 return v&&v.evidence_admitted===false&&v.delp_invoked===false&&
 v.writer_authorized===false&&v.publisher_authorized===false&&
 v.programme_progress===null;
}
function result(status,firstFailure,steps,grade,source){
 return Object.freeze({
  schema:'common-v35-294-t16-diagnostic-handover-v1',
  status,first_failure:firstFailure,
  chain_grade:grade,
  original_candidate:REPO+'/pull/308',
  exact_source_head:H,
  base_head:B,
  source_currentness:source,
  index_status:steps.index?.status||'NOT_RUN',
  blobs_status:steps.blobs?.status||'NOT_RUN',
  comments_status:steps.comments?.status||'NOT_RUN',
  last_read_status:steps.last?.status||'NOT_RUN',
  canonical_index:'NOT_QUALIFIED',
  independent_successor:'NOT_RUN',
  handover_class:'CODER_GENERATED_DIAGNOSTIC_ONLY',
  no_chat_successor_executed:false,
  owner_authenticated:false,admitted_graph:false,
  required_ci_qualified:false,independent_review_qualified:false,
  evidence_admitted:false,delp_invoked:false,programme_progress:null,
  writer_authorized:false,publisher_authorized:false,
  next_permitted_action:status==='READ_ONLY_HANDOVER_READY_HOLD'?
    'OWNER_D1_D5_AND_GOVERNED_INDEX_PLUS_EXTERNAL_B_REQUIRED':
    'REFETCH_FIRST_FAILED_SOURCE_EDGE_READ_ONLY',
 });
}
export function foldHandover(index,blobs,comments,last,{native=false}={}){
 const steps={index,blobs,comments,last};
 const required=[
  ['index', 'CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD'],
  ['blobs', 'SOURCE_BLOBS_CURRENT_READ_ONLY_HOLD'],
  ['comments', 'AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD'],
  ['last','CURRENT_SOURCE_PR308_AFTER_CHAIN'],
 ];
 let failure=null;
 for(const [key,want] of required){
  const v=steps[key];
  if(!v||v.status!==want||v.observation_grade!==
       (native?G:'CALLER_INJECTED_UNATTESTED')){
   failure=key.toUpperCase()+'_NOT_VERIFIED';break;
  }
  if(key!=='last'&&!allNoAuthority(v)){
   failure=key.toUpperCase()+'_CLAIMS_AUTHORITY';break;
  }
 }
 if(!failure && (index.index_authority!=='NOT_GOVERNED_NOT_CANONICAL'||
     index.r4_independent_trial!=='NOT_RUN'||
     index.provider_pass_count!==2||blobs.provider_pass_count!==2||
     blobs.verified_blob_count!==16||comments.provider_pass_count!==2||
     comments.comment_owner_authenticated!==false||
     comments.claim_grade!=='AUTHOR_DIAGNOSTIC_ONLY_UNATTESTED_OWNER'||
     last.observed_head_sha!==H||last.observed_base_sha!==B))
   failure='LINKED_SOURCE_CONTRACT_INCOMPLETE';
 const ready=!failure;
 return result(ready?'READ_ONLY_HANDOVER_READY_HOLD':'HOLD_FAILED_SOURCE_EDGE',
    failure,steps,native?'NATIVE_SERIAL_NONATOMIC_GET':'CALLER_INJECTED_UNATTESTED',
    ready?'SOURCE_PR308_LAST_READ_CURRENT_NOT_ATOMIC':'UNKNOWN');
}
export async function inspectNativeHandover(testedSha,{token=process.env.GITHUB_TOKEN??''}={}){
 // All calls explicitly sequential; no injection may mint native grade.
 const index=await inspectNativeCandidate(testedSha,{token});
 if(index.status!=='CANDIDATE_LINKS_CURRENT_READ_ONLY_HOLD')
  return foldHandover(index,null,null,null,{native:true});
 const blobs=await inspectNativeSourceBlobs({token});
 if(blobs.status!=='SOURCE_BLOBS_CURRENT_READ_ONLY_HOLD')
  return foldHandover(index,blobs,null,null,{native:true});
 const comments=await inspectNativeComments({token});
 if(comments.status!=='AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD')
  return foldHandover(index,blobs,comments,null,{native:true});
 let last={status:'UNKNOWN',observation_grade:G};
 try{
  const url='https://api.github.com/repos/'+REPO+'/pulls/308';
  const headers={'Accept':'application/vnd.github+json',
    'X-GitHub-Api-Version':'2022-11-28','User-Agent':'common-v35-294-t16-readonly'};
  if(token)headers.Authorization='Bearer '+token;
  const res=await fetch(url,{method:'GET',headers,
    redirect:'error',signal:AbortSignal.timeout(15000)});
  if(res.status===200&&!res.redirected&&res.url===url){
   const p=await res.json();
   if(p.number===308&&p.state==='open'&&p.head?.sha===H&&p.base?.sha===B&&
      p.head?.repo?.full_name===REPO&&p.base?.repo?.full_name===REPO)
    last={status:'CURRENT_SOURCE_PR308_AFTER_CHAIN',observation_grade:G,
      observed_head_sha:H,observed_base_sha:B};
  }
 }catch{/* fail closed */}
 return foldHandover(index,blobs,comments,last,{native:true});
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const testedSha=process.env.TESTED_CANDIDATE_HEAD||'';
 const out=await inspectNativeHandover(testedSha);
 console.log(JSON.stringify(out,null,2));
 if(out.status!=='READ_ONLY_HANDOVER_READY_HOLD')process.exitCode=1;
 else console.log('T16_HANDBACK=SOURCE_BYTES_PLUS_COMMENT_CLAIMS_PLUS_DRAFT_INDEX_CURRENT_READ_ONLY; OWNER=HOLD; B=NOT_RUN; E=NONE; DELP=OFF');
}
