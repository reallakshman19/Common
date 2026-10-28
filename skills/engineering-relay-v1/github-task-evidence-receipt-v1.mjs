/* RELAY RESET R10: OBSERVE a PUBLIC GitHub comment, never accept its claims.
 * Mutable provider source, read twice; no Owner authentication or GitHub writes.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';

export class PublicEvidenceError extends Error {
  constructor(code,why){super(code+': '+why);this.name='PublicEvidenceError';this.code=code;}
}
const fail=(code,why)=>{throw new PublicEvidenceError(code,why);};
const MAX_HTTP=192*1024,MAX_BODY=64*1024;
const REPO=/^[A-Za-z0-9-]{1,39}\/[A-Za-z0-9_.-]{1,100}$/;
const hash=v=>createHash('sha256').update(v).digest('hex');
const validNumber=n=>Number.isSafeInteger(n)&&n>0;
const validISO=v=>typeof v==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(v)&&Number.isFinite(Date.parse(v));
function exact(v,keys,label){
 if(!v||typeof v!=='object'||Array.isArray(v)||
   keys.some(k=>!Object.hasOwn(v,k))||Object.keys(v).some(k=>!keys.includes(k)))
   fail('INVALID',label+' invalid shape');
}
const freeze=root=>{
 const q=[root],seen=new Set();
 while(q.length){const o=q.pop();if(!o||typeof o!=='object'||seen.has(o))continue;
  seen.add(o);for(const v of Object.values(o))if(v&&typeof v==='object')q.push(v);
  Object.freeze(o);
 }return root;
};
function scope(raw){
 let s;try{s=JSON.parse(canonicalJSON(raw));}catch{fail('INVALID','unsafe comment scope');}
 exact(s,['repository','parent_issue','task_issue','comment_id'],'comment scope');
 if(!REPO.test(s.repository)||!validNumber(s.parent_issue)||
   !validNumber(s.task_issue)||s.parent_issue===s.task_issue||!validNumber(s.comment_id))
   fail('INVALID','invalid exact repo/parent/task/comment');
 return s;
}
async function decode(r,url){
 if(!r||r.status!==200||r.redirected===true||r.url!==url)
   fail('UNKNOWN','provider not an exact HTTP 200');
 const n=r.headers?.get?.('content-length');
 if(n!==null&&n!==undefined&&n!==''){
  const size=Number(n);if(!Number.isSafeInteger(size)||size<0||size>MAX_HTTP)
   fail('UNKNOWN','provider response size invalid');
 }
 let buf;
 if(r.body?.getReader){
  const reader=r.body.getReader(),parts=[];let size=0;
  try{while(true){
   const next=await reader.read();if(next.done)break;
   size+=next.value.byteLength;if(size>MAX_HTTP)fail('UNKNOWN','provider stream too large');
   parts.push(Buffer.from(next.value));
  }}finally{reader.releaseLock();}
  buf=Buffer.concat(parts);
 }else if(typeof r.text==='function'){
  const text=await r.text();
  if(typeof text!=='string')fail('UNKNOWN','provider response not UTF8');
  buf=Buffer.from(text,'utf8');
  if(buf.length>MAX_HTTP)fail('UNKNOWN','provider response too large');
 }else fail('UNKNOWN','response body missing');
 let decoded,raw;try{decoded=new TextDecoder('utf-8',{fatal:true}).decode(buf);raw=JSON.parse(decoded);}
 catch{fail('UNKNOWN','invalid provider UTF8/JSON');}
 return raw;
}
function fact(item,s){
 if(!item||typeof item!=='object'||Array.isArray(item))fail('REFUTED','comment object invalid');
 const root='https://github.com/'+s.repository+'/issues/'+s.task_issue;
 const api='https://api.github.com/repos/'+s.repository;
 if(item.id!==s.comment_id||
   item.url!==api+'/issues/comments/'+s.comment_id||
   item.issue_url!==api+'/issues/'+s.task_issue||
   item.html_url!==root+'#issuecomment-'+s.comment_id||
   !validISO(item.created_at)||!validISO(item.updated_at)||
   Date.parse(item.updated_at)<Date.parse(item.created_at)||
   !item.user||typeof item.user.login!=='string'||
   !/^[A-Za-z0-9-]{1,39}$/.test(item.user.login)||
   !validNumber(item.user.id)||typeof item.body!=='string'||
   !item.body.trim()||Buffer.byteLength(item.body,'utf8')>MAX_BODY)
   fail('REFUTED','comment scope, author, date, or body invalid');
 // No text content escapes, even when original comment is already public.
 return {
  comment_id:s.comment_id,task_issue:s.task_issue,parent_issue:s.parent_issue,
  repository:s.repository,source_url:item.html_url,source_api_url:item.url,
  author_login:item.user.login,author_id:item.user.id,
  created_at:item.created_at,updated_at:item.updated_at,
  body_sha256:hash(Buffer.from(item.body,'utf8')),
  body_byte_count:Buffer.byteLength(item.body,'utf8'),
  marker_present:item.body.includes('TASK_EVIDENCE END'),
  producer_assertions_not_adjudicated:true
 };
}
export async function observePublicTaskEvidence(rawScope,options={}){
 const s=scope(rawScope);
 if(!options||typeof options!=='object'||Array.isArray(options)||
   Object.keys(options).some(k=>!['fetchImpl','readToken'].includes(k)))
   fail('INVALID','read-only observer options only');
 if(options.readToken!==undefined&&(typeof options.readToken!=='string'||
   !/^[\x21-\x7e]{1,400}$/.test(options.readToken)))
   fail('INVALID','read token invalid');
 const injected=Object.hasOwn(options,'fetchImpl');
 const fetcher=injected?options.fetchImpl:globalThis.fetch;
 if(typeof fetcher!=='function')fail('UNKNOWN','HTTPS client unavailable');
 const url='https://api.github.com/repos/'+s.repository+'/issues/comments/'+s.comment_id;
 const headers={Accept:'application/vnd.github+json',
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'relay-public-evidence-v1'};
 if(options.readToken)headers.Authorization='Bearer '+options.readToken;
 async function get(){
  let response;try{response=await fetcher(url,{method:'GET',redirect:'error',cache:'no-store',headers});}
  catch{fail('UNKNOWN','provider fetch failed');}
  return fact(await decode(response,url),s);
 }
 const first=await get(),second=await get();
 if(canonicalJSON(first)!==canonicalJSON(second))
   fail('STALE','GitHub comment changed between bounded reads');
 const core={schema:'relay-public-task-evidence-receipt-v1',
  ...second,provider_read_count:2,
  provider_source:injected?'INJECTED_UNVERIFIED':'NATIVE_GITHUB_COMMENT_GET',
  consistency:'COMMENT_DOUBLE_READ_NON_ATOMIC',
  observation:'PRODUCER_ASSERTED_PUBLIC_COMMENT_NOT_ACCEPTED',
  author_is_owner_authenticated:false,
  independent_reviewer_accepted:false,task_evidence_accepted:false,
  authorization_granted:false,live_writer_enabled:false};
 return freeze({...core,receipt_sha256:hash(canonicalJSON(core))});
}
