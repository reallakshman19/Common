import {createHash} from 'node:crypto';
/* R1-B.1: provider-source observation only. Valid origin != Owner approval. */
export class SourceReceiptError extends Error {
 constructor(kind,reason){super(kind+': '+reason);this.name='SourceReceiptError';this.kind=kind;}
}
const MAX=1048576,HEX=/^[a-f0-9]{64}$/,REPO=/^([A-Za-z0-9-]{1,39})\/([A-Za-z0-9_.-]{1,100})$/;
function error(kind,reason){throw new SourceReceiptError(kind,reason)}
const refute=why=>error('REFUTED',why),unknown=why=>error('UNKNOWN',why);
function only(obj,keys,label){
 if(!obj||typeof obj!=='object'||Array.isArray(obj))refute(label+' invalid object');
 for(const key of Object.keys(obj))if(!keys.includes(key))refute(label+' unexpected key '+key);
}
function scope(spec){
 only(spec,['repository','issue','comment_id'],'scope');
 const m=typeof spec.repository==='string'&&REPO.exec(spec.repository);
 if(!m||m[2]==='.'||m[2]==='..'||!(/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(m[1]))||!Number.isSafeInteger(spec.issue)||spec.issue<=0||!Number.isSafeInteger(spec.comment_id)||spec.comment_id<=0)refute('invalid scope');
 const owner=m[1],stem='https://api.github.com/repos/'+m[1]+'/'+m[2];
 return {owner,
  api:stem+'/issues/comments/'+spec.comment_id,
  issue:stem+'/issues/'+spec.issue,
  html:'https://github.com/'+m[1]+'/'+m[2]+'/issues/'+spec.issue+'#issuecomment-'+spec.comment_id};
}
async function jsonBounded(response){
 if(!response||response.status!==200)unknown('native GitHub HTTP status not 200');
 if(response.redirected===true)unknown('redirect refused');
 const size=Number(response.headers?.get?.('content-length'));
 if(Number.isFinite(size)&&size>MAX)unknown('response size too large');
 let raw;
 if(response.body?.getReader){
  const rd=response.body.getReader(),parts=[];let total=0;
  try{while(true){const {value,done}=await rd.read();if(done)break;total+=value.byteLength;
    if(total>MAX)unknown('response stream too large');parts.push(Buffer.from(value));}}
  finally{rd.releaseLock();}
  try{raw=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(parts));}
  catch{unknown('invalid UTF-8 response');}
 }else if(typeof response.text==='function'){
  raw=await response.text();if(Buffer.byteLength(raw,'utf8')>MAX)unknown('response text too large');
 }else unknown('missing response body');
 try{return JSON.parse(raw)}catch{unknown('malformed JSON response');}
}
export async function readNativeOwnerComment(spec,options={}){
 const bound=scope(spec);
 only(options,['fetchImpl','expectedBodySha256'],'options');
 const expected=options.expectedBodySha256??null;
 if(expected!==null&&(typeof expected!=='string'||!HEX.test(expected)))refute('bad expected sha256');
 const injected=Object.hasOwn(options,'fetchImpl');
 const fetcher=injected?options.fetchImpl:globalThis.fetch;
 if(typeof fetcher!=='function')unknown('fetch unavailable');
 let response;
 try{response=await fetcher(bound.api,{method:'GET',redirect:'error',cache:'no-store',
  headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'relay-reset-comment-source-v1'}});}
 catch{unknown('native HTTPS read failed');}
 if(response?.url!==bound.api)unknown('response URL missing or differs');
 const p=await jsonBounded(response);
 if(!p||typeof p!=='object'||Array.isArray(p))refute('native payload is not object');
 if(p.id!==spec.comment_id||p.url!==bound.api||p.issue_url!==bound.issue||p.html_url!==bound.html)refute('native URL/issue/comment identity mismatch');
 if(!p.user||typeof p.user.login!=='string'||p.user.login.toLowerCase()!==bound.owner.toLowerCase()||p.author_association!=='OWNER')refute('native issuer not repository Owner');
 if(typeof p.body!=='string'||!p.body.trim()||Buffer.byteLength(p.body,'utf8')>MAX)refute('missing/oversized body');
 const t=/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;
 if(typeof p.created_at!=='string'||typeof p.updated_at!=='string'||!t.test(p.created_at)||!t.test(p.updated_at)||
  !Number.isFinite(Date.parse(p.created_at))||!Number.isFinite(Date.parse(p.updated_at))||Date.parse(p.created_at)>Date.parse(p.updated_at))refute('invalid timestamps');
 const digest=createHash('sha256').update(p.body,'utf8').digest('hex');
 if(expected!==null&&expected!==digest)refute('body digest changed');
 return Object.freeze({kind:'GITHUB_NATIVE_COMMENT',status:injected?'INJECTED_UNVERIFIED':'PROVIDER_ISSUER_OBSERVED',
  repository:spec.repository,issue:spec.issue,comment_id:spec.comment_id,
  source_url:bound.html,api_url:bound.api,author_login:p.user.login,
  author_association:'OWNER',created_at:p.created_at,updated_at:p.updated_at,
  body_sha256:digest,body_bytes:Buffer.byteLength(p.body,'utf8'),
  transport:injected?'INJECTED_UNVERIFIED':'NATIVE_FIXED_HTTPS_GET',
  original_chat_source:'UNKNOWN',authority_granted:false,semantic_accepted:false});
}
