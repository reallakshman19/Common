/* RELAY RESET R1-B.2b: native GitHub grant/decision source WITNESS only.
 * This never authenticates a human Owner authorization, even for two native
 * OWNER-associated GitHub comments with exact pinned bytes.
 */
import {readNativeOwnerComment,SourceReceiptError} from './github-comment-source-v1.mjs';

export class GrantWitnessError extends Error {
 constructor(code,reason){super(code+': '+reason);this.name='GrantWitnessError';this.code=code;}
}
const HASH=/^[a-f0-9]{64}$/;
const ISSUE=/^([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)#[1-9][0-9]*$/;
function bad(code,why){throw new GrantWitnessError(code,why);}
function fixedFields(obj,allowed,required,where){
 if(!obj||typeof obj!=='object'||Array.isArray(obj))bad('REFUTED',where+' must be object');
 for(const k of Object.keys(obj))if(!allowed.includes(k))bad('REFUTED',where+' unsupported '+k);
 for(const k of required)if(!Object.hasOwn(obj,k))bad('REFUTED',where+' missing '+k);
}
function spec(item,where){
 fixedFields(item,['repository','issue','comment_id','body_sha256'],['repository','issue','comment_id','body_sha256'],where);
 if(typeof item.repository!=='string'||!Number.isSafeInteger(item.issue)||item.issue<=0||
   !Number.isSafeInteger(item.comment_id)||item.comment_id<=0||!HASH.test(item.body_sha256))
   bad('REFUTED',where+' must pin repo/issue/comment ID and exact body SHA256');
}
function digestFrom(result){
 return Object.freeze({repository:result.repository,issue:result.issue,comment_id:result.comment_id,
   source_url:result.source_url,author_login:result.author_login,
   author_association:result.author_association,
   created_at:result.created_at,updated_at:result.updated_at,
   body_sha256:result.body_sha256,transport:result.transport,status:result.status});
}
function result(status,items,reason){
 return Object.freeze({status,
   observed_at_utc:new Date().toISOString(),
   grant_source:items.grant_source??null,
   decision_source:items.decision_source??null,
   reasons:Object.freeze(reason?Object.freeze([reason]):Object.freeze([])),
   // No discovered source can self-authorize an Owner decision or merge.
   authorization_granted:false,owner_grant_authenticated:false,
   human_owner_consent_verified:false,original_chat_source:'UNKNOWN',
   independently_accepted:false,live_writer_enabled:false});
}
/** One provenance observation iteration; callers must re-run for current facts. */
export async function readNativeGrantWitness(input,options={}){
 fixedFields(input,['parent_issue','grant_source','decision_source'],
   ['parent_issue','grant_source','decision_source'],'input');
 fixedFields(options,['fetchImpl'],[],'options');
 const m=typeof input.parent_issue==='string'&&input.parent_issue.match(ISSUE);
 if(!m)bad('REFUTED','governing parent must be exact owner/repo#issue');
 spec(input.grant_source,'grant_source');spec(input.decision_source,'decision_source');
 const ownerRepo=m[1].toLowerCase(),g=input.grant_source,d=input.decision_source;
 if(g.repository.toLowerCase()!==ownerRepo||d.repository.toLowerCase()!==ownerRepo)
   return result('REFUTED',{},'cross-repository source not governed by parent');
 if(g.comment_id===d.comment_id)
   return result('REFUTED',{},'grant cannot be its own decision source');
 const fetchOpt=Object.hasOwn(options,'fetchImpl')?{fetchImpl:options.fetchImpl}:{};
 let grant;
 try{grant=await readNativeOwnerComment(
   {repository:g.repository,issue:g.issue,comment_id:g.comment_id},
   {...fetchOpt,expectedBodySha256:g.body_sha256});
 }catch(e){
   if(!(e instanceof SourceReceiptError))throw e;
   return result(e.kind,{},'prior grant source: '+e.message);
 }
 let decision;
 try{decision=await readNativeOwnerComment(
   {repository:d.repository,issue:d.issue,comment_id:d.comment_id},
   {...fetchOpt,expectedBodySha256:d.body_sha256});
 }catch(e){
   if(!(e instanceof SourceReceiptError))throw e;
   return result(e.kind,{grant_source:digestFrom(grant)},'decision source: '+e.message);
 }
 const pair={grant_source:digestFrom(grant),decision_source:digestFrom(decision)};
 if(grant.author_login.toLowerCase()!==decision.author_login.toLowerCase())
   return result('REFUTED',pair,'grant/decision issuer differs');
 // Native provider issue-comment bodies are mutable. A grant changed after
 // the claimed decision was created is not an earlier immutable authority.
 if(Date.parse(grant.created_at)>=Date.parse(decision.created_at))
   return result('REFUTED',pair,'grant does not predate decision');
 if(Date.parse(grant.updated_at)>Date.parse(decision.created_at))
   return result('REFUTED',pair,'grant edited after decision was created');
 const native=grant.status==='PROVIDER_ISSUER_OBSERVED'&&decision.status==='PROVIDER_ISSUER_OBSERVED'&&
   grant.transport==='NATIVE_FIXED_HTTPS_GET'&&decision.transport==='NATIVE_FIXED_HTTPS_GET';
 return result(native?'NATIVE_SOURCE_PAIR_OBSERVED_NOT_AUTHORIZED':'INJECTED_UNVERIFIED',pair,
   native?'provider observed issuer and bytes, not genuine human authorization':'injected transport cannot prove provider origin');
}
