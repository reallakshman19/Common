/* V3.5 WP2-A/U03: native issue-comment material, never evidence admission. */
import {createHash} from 'node:crypto';
const REPO='reallakshman19/Common',ID=1412133785,SHA=/^[a-f0-9]{40}$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const pos=x=>Number.isSafeInteger(x)&&x>0;
const issue=n=>'https://github.com/'+REPO+'/issues/'+n;
const pr=n=>'https://github.com/'+REPO+'/pull/'+n;
const comment=(n,id)=>issue(n)+'#issuecomment-'+id;
const hash=x=>'sha256:'+createHash('sha256').update(x).digest('hex');
const denied=(grade,errors)=>({
 schema:'common-v35-wp2a-u03-comment-material-v1',source_grade:grade,
 material_observed:false,source_currentness:'UNKNOWN',errors,source_receipt:null,
 source_receipt_sha256:null,body_claim_grade:'NOT_VERIFIED',actor_grade:'NOT_VERIFIED',
 evidence_admitted:false,reviewer_qualified:false,owner_authenticated:false,
 delp_projection:'NOT_CALCULATED',programme_progress:null,writer_authorized:false,
 successor_lease:'NOT_PROVEN',
});
function contract(x){
 if(!obj(x)||Object.keys(x).some(k=>![
  'repository','repository_id','root_issue','leaf_issue','pr_number',
  'evidence_comment_id','claimed_head_sha','expected_author_login'
 ].includes(k)))return ['INPUT_SHAPE_INVALID'];
 const e=[];
 if(x.repository!==REPO||x.repository_id!==ID)e.push('CURRENT_REPOSITORY_MISMATCH');
 if(![x.root_issue,x.leaf_issue,x.pr_number,x.evidence_comment_id].every(pos)||
     x.root_issue===x.leaf_issue)e.push('ROLE_NUMBER_INVALID');
 if(!SHA.test(x.claimed_head_sha||''))e.push('CLAIMED_HEAD_INVALID');
 if(typeof x.expected_author_login!=='string'||
   !/^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i.test(x.expected_author_login))
  e.push('EXPECTED_ACTOR_LOGIN_INVALID');
 return e;
}
function bodyClaim(body,x){
 if(typeof body!=='string'||body.length>50000||!body.startsWith('## TASK_EVIDENCE'))
  throw Error('NOT_TASK_EVIDENCE');
 // Author text is a CLAIM. The \x60 character is a markdown code tick.
 const heads=[...body.matchAll(/\*\*Tested HEAD:\*\*\s*\x60([a-f0-9]{40})\x60/g)];
 if(heads.length!==1||heads[0][1]!==x.claimed_head_sha)throw Error('HEAD_CLAIM_MISMATCH');
 const links=[...body.matchAll(/\]\((https:\/\/github\.com\/[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+\/pull\/[1-9]\d*)\)/g)];
 if(!links.some(m=>m[1]===pr(x.pr_number)))throw Error('CURRENT_PR_BINDING_MISSING');
 return 'CLAIMED_TEXT_ONLY';
}
function validate(x,s){
 if(!obj(s.repo)||s.repo.id!==ID||s.repo.full_name!==REPO)throw Error('REPO_MISMATCH');
 for(const [kind,item,n] of [['ROOT',s.root,x.root_issue],['LEAF',s.leaf,x.leaf_issue]]){
  if(!obj(item)||item.number!==n||item.html_url!==issue(n)||
    Object.hasOwn(item,'pull_request')||item.state!=='open')throw Error(kind+'_INVALID');
 }
 const p=s.pr;
 if(!obj(p)||p.number!==x.pr_number||p.html_url!==pr(x.pr_number)||
   p.state!=='open'||!obj(p.head)||!obj(p.head.repo)||
   p.head.repo.id!==ID||p.head.repo.full_name!==REPO||!SHA.test(p.head.sha||''))
  throw Error('PR_ROLE_INVALID');
 const c=s.comment;
 if(!obj(c)||c.id!==x.evidence_comment_id||
   c.html_url!==comment(x.leaf_issue,x.evidence_comment_id)||
   c.issue_url!=='https://api.github.com/repos/'+REPO+'/issues/'+x.leaf_issue||
   !obj(c.user)||!pos(c.user.id)||c.user.login!==x.expected_author_login||
   (c.user.type!==undefined&&c.user.type!=='User')||
   typeof c.created_at!=='string'||typeof c.updated_at!=='string'||
   Number.isNaN(Date.parse(c.created_at))||Number.isNaN(Date.parse(c.updated_at)))
  throw Error('COMMENT_IDENTITY_INVALID');
 if(!obj(s.commit)||s.commit.sha!==x.claimed_head_sha)throw Error('COMMIT_NOT_RESOLVED');
 const grade=bodyClaim(c.body,x);
 const receipt={
  repository:REPO,repository_id:ID,root_issue:x.root_issue,leaf_issue:x.leaf_issue,
  pr_number:p.number,pr_url:pr(p.number),current_pr_head_sha:p.head.sha,
  claimed_head_sha:x.claimed_head_sha,comment_id:c.id,comment_url:c.html_url,
  comment_author_login:c.user.login,comment_author_id:c.user.id,
  comment_created_at:c.created_at,comment_updated_at:c.updated_at,
  body_sha256:hash(c.body),body_claim_grade:grade,
 };
 return {receipt,currentness:p.head.sha===x.claimed_head_sha?
  'MATCH_AT_OBSERVATION':'STALE_CANDIDATE_HEAD'};
}
async function round(x,read){
 const paths=['','issues/'+x.root_issue,'issues/'+x.leaf_issue,'pulls/'+x.pr_number,
  'issues/comments/'+x.evidence_comment_id,'commits/'+x.claimed_head_sha];
 const [repo,root,leaf,prObj,commentObj,commit]=await Promise.all(paths.map(async path=>{
  const v=await read(REPO,path);
  if(!obj(v))throw Error('INVALID_PROVIDER_RESPONSE');
  return v;
 }));
 return validate(x,{repo,root,leaf,pr:prObj,comment:commentObj,commit});
}
async function observe(x,reader,grade){
 const invalid=contract(x);
 if(invalid.length)return denied(grade,invalid);
 if(typeof reader!=='function')return denied(grade,['PROVIDER_READER_MISSING']);
 try{
  const first=await round(x,reader),second=await round(x,reader);
  if(JSON.stringify(first)!==JSON.stringify(second))
   return denied(grade,['PROVIDER_COMMENT_OR_HEAD_CHANGED_BETWEEN_READS']);
  return {
   schema:'common-v35-wp2a-u03-comment-material-v1',source_grade:grade,
   material_observed:true,source_currentness:second.currentness,errors:[],
   source_receipt:second.receipt,
   source_receipt_sha256:hash('common-v35-wp2a-task-evidence-comment-v1\0'+JSON.stringify(second.receipt)),
   body_claim_grade:'CLAIMED_TEXT_ONLY',
   actor_grade:'GITHUB_ACCOUNT_OBSERVED_NOT_OWNER_AUTHENTICATED',
   evidence_admitted:false,reviewer_qualified:false,owner_authenticated:false,
   delp_projection:'NOT_CALCULATED',programme_progress:null,writer_authorized:false,
   successor_lease:'NOT_PROVEN',
  };
 }catch{return denied(grade,['PROVIDER_SOURCE_OR_CLAIM_UNVERIFIED']);}
}
export const observeEvidenceComment=(x,read)=>observe(x,read,'CALLER_INJECTED_UNATTESTED');
async function nativeGet(repo,path,token){
 if(repo!==REPO||!/^(?:|issues\/[1-9]\d*|issues\/comments\/[1-9]\d*|pulls\/[1-9]\d*|commits\/[a-f0-9]{40})$/.test(path))
  throw Error('ROUTE_DENIED');
 const url='https://api.github.com/repos/'+REPO+(path?'/'+path:'');
 const headers={Accept:'application/vnd.github+json',
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'common-v35-wp2a-u03-readonly'};
 if(token)headers.Authorization='Bearer '+token;
 const res=await fetch(url,{method:'GET',headers,redirect:'error',signal:AbortSignal.timeout(15000)});
 if(res.status!==200||res.redirected||res.url!==url)throw Error('GITHUB_READ_NOT_VERIFIED');
 const raw=await res.text();
 if(Buffer.byteLength(raw,'utf8')>250000)throw Error('SOURCE_TOO_LARGE');
 return JSON.parse(raw);
}
export async function observeLiveEvidenceComment(x,{token=process.env.GITHUB_TOKEN||''}={}){
 return observe(x,(repo,path)=>nativeGet(repo,path,token),'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
