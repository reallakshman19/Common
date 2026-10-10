/* #294 T14: non-admitting original source byte/identity closure at PR308.
 * Source/head links alone do not prove the original WP2-A/WP2-B bytes.
 * No Owner authorization, reviewer, evidence eligibility or DELP is inferred.
 */
import {createHash} from 'node:crypto';
const R='reallakshman19/Common',ID=1412133785;
const H='087cf43193febffc31375e71359e767489d3ae68';
const B='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const A='relay/RECOVERY/V35_R14_WP2A_20261010/';
const C='relay/RECOVERY/V35_R14_WP2B_20261010/';
export const ORIGINAL_FILES=Object.freeze([
 [A+'required-ci-material-v1.mjs','3eac046128202fdee88a5ad47bb1df82e3304ca1'],
 [A+'required-ci-material-v1.test.mjs','e1da8e166cb7e560f76f13500e629f4a0be0f877'],
 [A+'task-evidence-comment-v1.mjs','79cffd2e3d2828ac1727afad7763267768c56ad5'],
 [A+'task-evidence-comment-v1.test.mjs','e78b852d0e28c8f7a13fe66baf60662e4b7c6789'],
 [A+'cross-source-vector-v1.mjs','e5843e4ab141a49950cd8e2b380540eca8f8f938'],
 [A+'cross-source-vector-v1.test.mjs','c0074ed41ee6a35e7fe0bbc4387b89e6ccf083fb'],
 [C+'pre-admission-boundary-v1.mjs','5dc2675459bbadc9f6bba4f86b91ac0e3664a061'],
 [C+'pre-admission-boundary-v1.test.mjs','abc1779f484a87b25d1a433fba6b10ebabff4993']
]);
const SHA=/^[0-9a-f]{40}$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const digest=b=>createHash('sha1').update(Buffer.concat([Buffer.from('blob '+b.length+'\0'),b])).digest('hex');
function out(grade,reason,files=0,passes=0){
 return Object.freeze({
  schema:'common-v35-294-t14-source-byte-closure-v1',
  status:reason===null?'SOURCE_BLOBS_CURRENT_READ_ONLY_HOLD':'HOLD_SOURCE_BLOBS',
  reason,observation_grade:grade,repository:R,source_pr:308,expected_head:H,
  verified_blob_count:files,provider_pass_count:passes,
  original_bytes_verified:reason===null,
  original_files:Object.freeze(ORIGINAL_FILES.map(([path,sha])=>({path,sha}))),
  evidence_admitted:false,admission:'NOT_ADMITTED',owner_authenticated:false,
  independent_successor_qualified:false,required_ci_qualified:false,
  delp_invoked:false,programme_progress:null,
  writer_authorized:false,publisher_authorized:false,
  next_permitted_action:reason===null?'READ_ONLY_CONTINUE_TO_EVIDENCE_PROVENANCE':'REFETCH_ORIGINAL_SOURCE_AND_HOLD',
 });
}
async function inspect(read,grade){
 if(typeof read!=='function')return out(grade,'NO_READER');
 let pass=0,count=0;
 try{
  for(let i=0;i<2;i++){
   const repo=await read('');
   const pr=await read('pulls/308');
   if(!obj(repo)||repo.id!==ID||repo.full_name!==R||!obj(pr)||
      pr.number!==308||pr.state!=='open'||pr.head?.sha!==H||
      pr.base?.sha!==B||pr.head?.repo?.id!==ID||pr.base?.repo?.id!==ID)
     throw 'PR308_NOT_CURRENT';
   for(const [path,sha] of ORIGINAL_FILES){
    const meta=await read('contents/'+path+'?ref='+H);
    if(!obj(meta)||meta.type!=='file'||meta.path!==path||
      meta.sha!==sha||meta.encoding!=='base64'||
      typeof meta.content!=='string'||meta.content.length>600000||
      !/^[a-zA-Z0-9+/=\r\n]+$/.test(meta.content))throw 'BLOB_METADATA_MISMATCH';
    const raw=Buffer.from(meta.content.replace(/\s/g,''),'base64');
    if(raw.length===0||raw.length>420000||digest(raw)!==sha)
      throw 'BLOB_BYTES_MISMATCH';
    count++;
   }
   const late=await read('pulls/308');
   if(late?.head?.sha!==H||late?.base?.sha!==B)throw 'PR_MOVED_DURING_READ';
   pass++;
  }
  return out(grade,null,count,pass);
 }catch(e){
  return out(grade,['PR308_NOT_CURRENT','BLOB_METADATA_MISMATCH','BLOB_BYTES_MISMATCH','PR_MOVED_DURING_READ'].includes(e)?e:'NATIVE_GET_UNKNOWN',count,pass);
 }
}
export const inspectInjectedSourceBlobs=reader=>inspect(reader,'CALLER_INJECTED_UNATTESTED');
export async function inspectNativeSourceBlobs({token=process.env.GITHUB_TOKEN??''}={}){
 const routes=new Set(['','pulls/308',...ORIGINAL_FILES.map(([path])=>'contents/'+path+'?ref='+H)]);
 const API='https://api.github.com/repos/'+R;
 return inspect(async path=>{
  if(!routes.has(path))throw Error('OUT_OF_SCOPE');
  const url=API+(path?'/'+path:'');
  const headers={'Accept':'application/vnd.github+json',
    'X-GitHub-Api-Version':'2022-11-28','User-Agent':'common-v35-294-t14-original-bytes'};
  if(token)headers.Authorization='Bearer '+token;
  const response=await fetch(url,{method:'GET',headers,redirect:'error',signal:AbortSignal.timeout(15000)});
  if(response.status!==200||response.redirected||response.url!==url)throw Error('UNKNOWN_PROVIDER');
  const body=await response.text();
  if(Buffer.byteLength(body)>1500000)throw Error('NATIVE_READ_OVERSIZE');
  return JSON.parse(body);
 },'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
