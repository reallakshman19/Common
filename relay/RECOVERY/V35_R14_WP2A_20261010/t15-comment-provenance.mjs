/* #294 T15: authored diagnostic comment-body semantics, NEVER E admission.
 * T13 checked comment URL/ID only; these live bodies must actually describe
 * correct source/negative/stale cases. Authored comments are NOT Owner grants.
 */
import {createHash} from 'node:crypto';
const R='reallakshman19/Common',ID=1412133785;
const H='087cf43193febffc31375e71359e767489d3ae68';
const T11='6a1598b0e09af0d0010a3e4c45ac3c0712799a66';
const H1='5d70e46d264909a576ccbbb074752004d1e9cb81';
const H2='eaa6ba95878e810f34c624354f7fc6e01f2e5bb0';
const API='https://api.github.com/repos/'+R,URL='https://github.com/'+R;
const COMMENTS=Object.freeze([
 {id:6099941506,kind:'T05',need:[H,'PR #308','NOT_ADMITTED']},
 {id:6100475989,kind:'T11',need:[H,T11,'PR #308']},
 {id:6100703214,kind:'T12',need:[T11,H1,H2,'HOLD_STALE_H1','NOT_ADMITTED']}
]);
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
function report(grade,status,reason,rounds=0,fingerprints=[]){
 return Object.freeze({
  schema:'common-v35-294-t15-comment-meaning-v1',
  status,reason,observation_grade:grade,provider_pass_count:rounds,
  source_pr:308,source_head:H,
  comment_ids:COMMENTS.map(x=>x.id),
  comment_fingerprints:fingerprints,
  claim_grade:'AUTHOR_DIAGNOSTIC_ONLY_UNATTESTED_OWNER',
  semantic_comments_current:status==='AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD',
  comment_owner_authenticated:false,
  evidence_admitted:false,required_ci_qualified:false,
  independent_reviewer_qualified:false,
  delp_invoked:false,programme_progress:null,
  writer_authorized:false,publisher_authorized:false,
  next_permitted_action:status==='AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD'?
   'READ_ONLY_HANDOVER_CONSUMER_WITH_NO_ADMISSION':'REFETCH_SOURCE_COMMENT_AND_HOLD',
 });
}
async function inspect(read,grade){
 if(typeof read!=='function')return report(grade,'HOLD_COMMENT','NO_READER');
 let rounds=0,previous=null;
 try{
  async function once(){
   const repository=await read('');
   const pr=await read('pulls/308');
   if(!obj(repository)||repository.full_name!==R||repository.id!==ID||
      !obj(pr)||pr.number!==308||pr.head?.sha!==H||pr.state!=='open')
     throw 'SOURCE_HEAD_CHANGED';
   const digests=[];
   for(const spec of COMMENTS){
    const comment=await read('issues/comments/'+spec.id);
    if(!obj(comment)||comment.id!==spec.id||
       comment.issue_url!==API+'/issues/294'||
       comment.html_url!==URL+'/issues/294#issuecomment-'+spec.id||
       comment.user?.login!=='reallakshman19'||
       comment.user?.id!==277598171)throw 'COMMENT_IDENTITY_CHANGED';
    const body=comment.body;
    if(typeof body!=='string'||body.length<100||body.length>25000||
       !body.includes('TASK_')&&spec.kind==='T05'||
       !spec.need.every(token=>body.includes(token)))throw 'COMMENT_SOURCE_MEANING_MISMATCH';
    digests.push(createHash('sha256').update(body).digest('hex'));
   }
   const late=await read('pulls/308');
   if(late?.head?.sha!==H)throw 'SOURCE_HEAD_CHANGED_DURING_ROUND';
   rounds++;
   return digests;
  }
  previous=await once();
  const current=await once();
  if(JSON.stringify(previous)!==JSON.stringify(current))
   return report(grade,'HOLD_COMMENT_DRIFT','COMMENT_EDITED_BETWEEN_READS',rounds);
  return report(grade,'AUTHOR_COMMENT_MEANING_MATCHES_READ_ONLY_HOLD','AUTHOR_COMMENTS_NOT_EVIDENCE_ADMISSION',rounds,current);
 }catch(e){
  const codes=['SOURCE_HEAD_CHANGED','COMMENT_IDENTITY_CHANGED','COMMENT_SOURCE_MEANING_MISMATCH','SOURCE_HEAD_CHANGED_DURING_ROUND'];
  return report(grade,'HOLD_COMMENT',codes.includes(e)?e:'PROVIDER_GET_UNKNOWN',rounds);
 }
}
export const inspectInjectedComments=read=>inspect(read,'CALLER_INJECTED_UNATTESTED');
export async function inspectNativeComments({token=process.env.GITHUB_TOKEN??''}={}){
 const paths=new Set(['','pulls/308',...COMMENTS.map(x=>'issues/comments/'+x.id)]);
 return inspect(async path=>{
  if(!paths.has(path))throw Error('NOT_ALLOWLISTED');
  const url=API+(path?'/'+path:'');
  const headers={'Accept':'application/vnd.github+json',
   'X-GitHub-Api-Version':'2022-11-28','User-Agent':'common-v35-294-t15-comment-source'};
  if(token)headers.Authorization='Bearer '+token;
  const res=await fetch(url,{method:'GET',headers,redirect:'error',signal:AbortSignal.timeout(15000)});
  if(res.status!==200||res.redirected||res.url!==url)throw Error('GET_NOT_VERIFIED');
  const data=await res.text();
  if(Buffer.byteLength(data)>1800000)throw Error('LARGE_PROVIDER');
  return JSON.parse(data);
 },'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
