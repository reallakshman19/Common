/* RELAY RESET R1-B.2a: PURE POLICY CANDIDATE CHECK, NEVER authorization.
 * This module has no provider/network/IO and MUST NOT be wired to a writer.
 * Matching user-supplied observations/grants can be forged; downstream needs
 * a separately trusted provider and role/grant resolver.
 */
export class ScopePolicyError extends Error {
  constructor(message){super(message);this.name='ScopePolicyError';}
}
const SHA=/^[a-f0-9]{40}$/;
const HASH=/^[a-f0-9]{64}$/;
const ISSUE=/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+#[1-9][0-9]*$/;
const NAME=/^[A-Za-z0-9_.-]{1,64}$/;
const ACTIONS=Object.freeze(['OWNER_INTENT_AMENDMENT','RESEARCH_ADOPTION','TASK_RELEASE','WRITER_SCOPE','REVIEW_VERDICT','MERGE_AUTHORITY']);
const ROLES=Object.freeze({OWNER:ACTIONS,REVIEWER:['REVIEW_VERDICT'],COORDINATOR:['TASK_RELEASE']});
const MAX_REFS=128;
function invalid(field,why){throw new ScopePolicyError(field+': '+why);}
function obj(value,keys,field){
  if(!value||typeof value!=='object'||Array.isArray(value))invalid(field,'expected object');
  for(const key of Object.keys(value))if(!keys.includes(key))invalid(field,'unexpected '+key);
  for(const key of keys)if(!Object.hasOwn(value,key))invalid(field,'missing '+key);
}
function string(value,field){if(typeof value!=='string'||!value.trim())invalid(field,'expected nonempty string');}
function checkName(value,field){if(typeof value!=='string'||!NAME.test(value))invalid(field,'invalid ID/login');}
function uniqueIds(values,field){
  if(!Array.isArray(values)||values.length<1||values.length>MAX_REFS)invalid(field,'expected 1..128 IDs');
  const seen=new Set();
  for(const v of values){checkName(v,field);if(seen.has(v))invalid(field,'duplicate ID');seen.add(v);}
}
function rfc3339(value,field){
  string(value,field);
  if(!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value)||!Number.isFinite(Date.parse(value))||
     new Date(Date.parse(value)).toISOString().replace('.000Z','Z')!==value)invalid(field,'invalid UTC timestamp');
  return Date.parse(value);
}
function validGrant(g){
  obj(g,['schema','grant_id','revision_sha','parent_issue','principal_login','role','actions','claim_ids','resources','exact_head_sha','valid_from','valid_until','revoked_at','source_comment_url','source_body_sha256'],'grant');
  if(g.schema!=='relay-declared-grant-v1')invalid('grant.schema','unsupported');
  checkName(g.grant_id,'grant.id');checkName(g.principal_login,'grant.principal_login');
  if(!SHA.test(g.revision_sha))invalid('grant.revision_sha','invalid exact commit');
  if(!ISSUE.test(g.parent_issue))invalid('grant.parent_issue','invalid issue');
  if(!Object.hasOwn(ROLES,g.role))invalid('grant.role','unsupported');
  uniqueIds(g.actions,'grant.actions');g.actions.forEach(action=>{if(!ACTIONS.includes(action))invalid('grant.actions','unknown action')});
  uniqueIds(g.claim_ids,'grant.claim_ids');
  if(!Array.isArray(g.resources)||!g.resources.length||g.resources.length>MAX_REFS)invalid('grant.resources','bad resources');
  for(const path of g.resources){
    string(path,'grant.resource');
    if(!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+#(?:[1-9][0-9]*)$/.test(path)&&
       !/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/(?:pull|issues)\/[1-9][0-9]*$/.test(path))
      invalid('grant.resource','unsupported exact resource');
  }
  if(g.exact_head_sha!==null&&(!SHA.test(g.exact_head_sha)))invalid('grant.exact_head_sha','invalid');
  const vf=rfc3339(g.valid_from,'grant.valid_from');
  const vu=g.valid_until===null?null:rfc3339(g.valid_until,'grant.valid_until');
  const revoked=g.revoked_at===null?null:rfc3339(g.revoked_at,'grant.revoked_at');
  if(vu!==null&&vu<vf)invalid('grant.valid_until','before grant');
  if(revoked!==null&&revoked<vf)invalid('grant.revoked_at','before grant');
  if(!/^https:\/\/github\.com\/[^?#]+\/issues\/[1-9][0-9]*#issuecomment-[1-9][0-9]*$/.test(g.source_comment_url))
    invalid('grant.source_comment_url','invalid native permalink syntax');
  if(!HASH.test(g.source_body_sha256))invalid('grant.source_body_sha256','invalid digest');
  return {vf,vu,revoked};
}
function validProposal(p){
  obj(p,['schema','decision_id','parent_issue','claim_id','issuer_login','role','action','resource','exact_head_sha','issued_at','finding_ids','subject_author_login','source_receipt'],'proposal');
  if(p.schema!=='relay-decision-candidate-v1')invalid('proposal.schema','unsupported');
  checkName(p.decision_id,'proposal.decision_id');
  if(!ISSUE.test(p.parent_issue))invalid('proposal.parent_issue','invalid');
  checkName(p.claim_id,'proposal.claim_id');checkName(p.issuer_login,'proposal.issuer_login');
  if(!Object.hasOwn(ROLES,p.role))invalid('proposal.role','unsupported');
  if(!ACTIONS.includes(p.action))invalid('proposal.action','unsupported');
  string(p.resource,'proposal.resource');
  if(p.exact_head_sha!==null&&!SHA.test(p.exact_head_sha))invalid('proposal.exact_head_sha','invalid');
  const time=rfc3339(p.issued_at,'proposal.issued_at');
  if(!Array.isArray(p.finding_ids)||p.finding_ids.length>MAX_REFS)invalid('proposal.finding_ids','invalid');
  for(const x of p.finding_ids)checkName(x,'proposal.finding_ids');
  if(new Set(p.finding_ids).size!==p.finding_ids.length)invalid('proposal.finding_ids','duplicates');
  if(p.subject_author_login!==null)checkName(p.subject_author_login,'proposal.subject_author_login');
  obj(p.source_receipt,['status','transport','author_login','source_url','body_sha256'],'proposal.source_receipt');
  string(p.source_receipt.status,'proposal.source_receipt.status');
  string(p.source_receipt.transport,'proposal.source_receipt.transport');
  checkName(p.source_receipt.author_login,'proposal.source_receipt.author_login');
  string(p.source_receipt.source_url,'proposal.source_receipt.source_url');
  if(!HASH.test(p.source_receipt.body_sha256))invalid('proposal.source_receipt.body_sha256','bad SHA256');
  return time;
}
function candidateResult(matches,reasons){
  return Object.freeze({
    status:matches?'MATCHES_DECLARED_POLICY_ONLY':'DECLARED_POLICY_DENIED',
    candidate_scope_match:matches,authorization_granted:false,
    trusted_issuer_verified:false,verified_original_chat:false,
    independently_accepted:false,requires_native_provider_recheck:true,
    reasons:Object.freeze(reasons)
  });
}
/** Compares UNTRUSTED data only. NEVER turn this result into permission. */
export function evaluateDeclaredScope(grant,proposal){
  const dates=validGrant(grant),issued=validProposal(proposal),why=[];
  const deny=(flag,name)=>{if(!flag)why.push(name);};
  deny(grant.parent_issue===proposal.parent_issue,'PARENT_MISMATCH');
  deny(grant.principal_login.toLowerCase()===proposal.issuer_login.toLowerCase(),'ISSUER_MISMATCH');
  deny(grant.role===proposal.role,'ROLE_MISMATCH');
  deny(ROLES[proposal.role].includes(proposal.action),'ROLE_ACTION_FORBIDDEN');
  deny(grant.actions.includes(proposal.action),'ACTION_OUT_OF_SCOPE');
  deny(grant.claim_ids.includes(proposal.claim_id),'CLAIM_OUT_OF_SCOPE');
  deny(grant.resources.includes(proposal.resource),'RESOURCE_OUT_OF_SCOPE');
  // A reset for this repo does not implicitly authorize cross-repository grants,
  // comments or resources; R7 portability will need an explicit opt-in policy.
  const repo=grant.parent_issue.split('#')[0].toLowerCase();
  const rootUrl='https://github.com/'+repo+'/';
  const insideRepo=(url)=>url.toLowerCase().startsWith(rootUrl);
  const scopedResource=(value)=>
    value.toLowerCase().startsWith(repo+'#')||insideRepo(value);
  deny(insideRepo(grant.source_comment_url),'GRANT_SOURCE_REPO_MISMATCH');
  deny(insideRepo(proposal.source_receipt.source_url),'COMMENT_REPO_MISMATCH');
  deny(scopedResource(proposal.resource),'RESOURCE_REPO_MISMATCH');
  deny(grant.exact_head_sha!==null&&proposal.exact_head_sha===grant.exact_head_sha,'EXACT_HEAD_NOT_BOUND');
  deny(issued>=dates.vf,'BEFORE_GRANT');
  deny(dates.vu===null||issued<=dates.vu,'GRANT_EXPIRED');
  deny(dates.revoked===null||issued<dates.revoked,'GRANT_REVOKED');
  deny(proposal.source_receipt.status==='PROVIDER_ISSUER_OBSERVED'&&
    proposal.source_receipt.transport==='NATIVE_FIXED_HTTPS_GET','NOT_NATIVE_SOURCE_OBSERVATION');
  deny(proposal.source_receipt.author_login.toLowerCase()===proposal.issuer_login.toLowerCase(),'RECEIPT_ISSUER_MISMATCH');
  deny(/^https:\/\/github\.com\/[^?#]+\/issues\/[1-9][0-9]*#issuecomment-[1-9][0-9]*$/.test(proposal.source_receipt.source_url),'NOT_GITHUB_COMMENT');
  if(proposal.action==='RESEARCH_ADOPTION')deny(proposal.finding_ids.length>0,'MISSING_RESEARCH_FINDING');
  else deny(proposal.finding_ids.length===0,'UNEXPECTED_RESEARCH_FINDING');
  if(proposal.action==='REVIEW_VERDICT'){
    deny(proposal.subject_author_login!==null,'MISSING_SUBJECT_AUTHOR');
    if(proposal.subject_author_login!==null)
      deny(proposal.subject_author_login.toLowerCase()!==proposal.issuer_login.toLowerCase(),'SELF_REVIEW');
  }
  // Matching a syntactically valid, caller-supplied grant is not proof that
  // it was issued by the Owner, is current, or authorizes any live operation.
  return candidateResult(why.length===0,why);
}
