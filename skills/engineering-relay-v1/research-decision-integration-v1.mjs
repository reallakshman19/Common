/* R1-C real source integration. Read-only; no claim of authenticated Owner approval. */
import {createHash} from 'node:crypto';
import {validate,canonicalJSON,traceClaim} from './provenance-v1.mjs';
import {readNativeOwnerComment,SourceReceiptError} from './github-comment-source-v1.mjs';
import {evaluateDeclaredScope} from './owner-decision-scope-v1.mjs';

export class IntegrationError extends Error {
 constructor(code,message){super(code+': '+message);this.name='IntegrationError';this.code=code;}
}
function fail(code,msg){throw new IntegrationError(code,msg);}
const hex=/^[a-f0-9]{64}$/;
function checkSameIds(a,b) { return a.length===b.length&&new Set(a).size===a.length&&new Set(b).size===b.length&&a.every(x=>b.includes(x)); }
function noAuthority(status,details){
 return Object.freeze({status,authorization_granted:false,independently_accepted:false,
   requires_real_owner_grant:true,live_writer_enabled:false,...details});
}
/** Validates and uses *actual merged* R1-A, R1-B.1, R1-B.2a interfaces. */
export async function inspectResearchDecision({document,decision_id,claim_id,comment_scope,proposal,declared_grant},options={}){
 if(!options||typeof options!=='object'||Array.isArray(options)||Object.keys(options).some(k=>k!=='fetchImpl'))
   fail('INVALID_OPTIONS','only optional test fetchImpl is supported');
 validate(document);
 if(typeof decision_id!=='string'||typeof claim_id!=='string')fail('INVALID_INPUT','decision/claim IDs required');
 const ownerDecision=document.owner_decisions.find(x=>x.id===decision_id);
 if(!ownerDecision)fail('UNKNOWN_DECISION','no declared OwnerDecision with that ID');
 const claim=document.claims.find(x=>x.id===claim_id);
 if(!claim)fail('UNKNOWN_CLAIM','no acceptance claim');
 if(!claim.intent_ids.includes(ownerDecision.intent_id))fail('REFUTED_INTENT_JOIN','decision original OwnerIntent not attached to claim');
 if(ownerDecision.disposition!=='ADOPT')fail('NOT_ADOPTED','REJECT/DEFER is not research adoption');
 if(!ownerDecision.finding_ids.length)fail('MISSING_FINDINGS','decision has no research source');
 if(proposal?.decision_id!==decision_id||proposal?.claim_id!==claim_id||proposal?.action!=='RESEARCH_ADOPTION'||
    !Array.isArray(proposal.finding_ids)||!checkSameIds(proposal.finding_ids,ownerDecision.finding_ids))
   fail('REFUTED_PROPOSAL_JOIN','candidate action/decision/finding references do not match actual graph');
 if(ownerDecision.source.kind!=='GITHUB_COMMENT'||ownerDecision.source.status==='UNKNOWN'||
   typeof ownerDecision.source.digest!=='string'||!hex.test(ownerDecision.source.digest))
   fail('UNTRUSTED_DECISION_SOURCE','decision needs declared pinned GitHub comment SHA256');
 if(!comment_scope||typeof comment_scope!=='object'||Array.isArray(comment_scope))
   fail('INVALID_COMMENT_SCOPE','expected scoped GitHub native issue comment');
 const {repository,issue,comment_id}=comment_scope;
 if(typeof repository!=='string'||!Number.isSafeInteger(issue)||issue<1||!Number.isSafeInteger(comment_id)||comment_id<1)
   fail('INVALID_COMMENT_SCOPE','repo/issue/comment must be valid');
 if(repository.toLowerCase()!==document.parent_issue.split('#')[0].toLowerCase())
   fail('CROSS_REPOSITORY','comment source is outside governed repository');
 const commentUrl='https://github.com/'+repository+'/issues/'+issue+'#issuecomment-'+comment_id;
 if(ownerDecision.source.locator!==commentUrl)
   fail('REFUTED_SOURCE_LINK','declared OwnerDecision comment locator differs from native scoped URL');
 const trace=traceClaim(document,claim_id);
 const intents=trace.owner_intent_ids.map(id=>{
   const value=document.owner_intents.find(x=>x.id===id);
   return Object.freeze({id,raw_text:value.raw_text,
     original_source:Object.freeze({...value.original_source}),
     first_durable_mirror:value.first_durable_mirror});
 });
 const facts={decision_id,claim_id,owner_intents:intents,
   research_findings:ownerDecision.finding_ids.map(id=>{
     const finding=document.research_findings.find(x=>x.id===id);
     return Object.freeze({id,statement:finding.statement,verification: finding.verification});
   }),
   declared_decision_disposition:ownerDecision.disposition,
   source_locator:commentUrl};
 let observed;
 try{
   observed=await readNativeOwnerComment(comment_scope,{
     ...(Object.hasOwn(options,'fetchImpl')?{fetchImpl:options.fetchImpl}:{}),
     expectedBodySha256:ownerDecision.source.digest
   });
 }catch(e){
   if(!(e instanceof SourceReceiptError))throw e;
   return noAuthority(e.kind,Object.freeze({...facts,source_read_error:e.kind,
     reasons:Object.freeze([e.message]),declared_scope:null}));
 }
 // CRITICAL: caller-supplied proposal.source_receipt is discarded completely.
 // Only the native reader output determines candidate source status/transport.
 const derived={...proposal,source_receipt:{
   status:observed.status,transport:observed.transport,author_login:observed.author_login,
   source_url:observed.source_url,body_sha256:observed.body_sha256
 }};
 const scope=evaluateDeclaredScope(declared_grant,derived);
 const status=scope.candidate_scope_match?'MATCHES_DECLARED_POLICY_ONLY':'DECLARED_SCOPE_DENIED';
 const result={...facts,source_status:observed.status,source_transport:observed.transport,
   source_digest:observed.body_sha256,declared_scope:scope};
 const digest=createHash('sha256').update(canonicalJSON(result)).digest('hex');
 return noAuthority(status,Object.freeze({...result,reconciled_view_digest:digest}));
}
