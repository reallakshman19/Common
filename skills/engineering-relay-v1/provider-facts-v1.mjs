/* RELAY RESET R3-A #833 — read-only NATIVE GitHub facts, not human authority.
 * Ingest current provider issue/PR/head/CI snapshots, never issue title claims.
 * No journal/Owner consent verifier, writer, automatic handover or live scoreboard.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';

export class ProviderFactsError extends Error {
  constructor(code,why){super(code+': '+why);this.name='ProviderFactsError';this.code=code;}
}
const fail=(code,why)=>{throw new ProviderFactsError(code,why);};
const REPO=/^([a-zA-Z0-9-]{1,39})\/([a-zA-Z0-9_.-]{1,100})$/;
const SHA=/^[0-9a-f]{40}$/;
const MAX_RESPONSE=2*1024*1024,MAX_WORKFLOWS=8;
function only(v,keys,label){
  if(!v||typeof v!=='object'||Array.isArray(v)||
    Object.keys(v).some(k=>!keys.includes(k))||
    keys.some(k=>!Object.hasOwn(v,k)))fail('INVALID',label+' missing or unexpected keys');
}
function number(v){return Number.isSafeInteger(v)&&v>0;}
function iso(v){
  return typeof v==='string'&&Number.isFinite(Date.parse(v))&&
    /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(v);
}
function scoped(v){
  let s;
  try{s=JSON.parse(canonicalJSON(v));}catch{fail('INVALID','non-canonical or unsafe source scope');}
  only(s,['repository','parent_issue','child_issues','pull_requests','workflow_paths'],'scope');
  const m=typeof s.repository==='string'&&REPO.exec(s.repository);
  if(!m||!/^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$/.test(m[1])||
    ['.','..'].includes(m[2])||!number(s.parent_issue))fail('INVALID','repository or parent invalid');
  if(!Array.isArray(s.child_issues)||s.child_issues.length>3||
    s.child_issues.some(n=>!number(n)||n===s.parent_issue)||
    new Set(s.child_issues).size!==s.child_issues.length)fail('INVALID','child issues invalid');
  if(!Array.isArray(s.pull_requests)||s.pull_requests.length<1||s.pull_requests.length>4)
    fail('INVALID','expected 1..4 pull requests');
  const ids=new Set();
  for(const p of s.pull_requests) {
    only(p,['number','expected_head_sha'],'pull request scope');
    if(!number(p.number)||ids.has(p.number)||
      !(p.expected_head_sha===null||SHA.test(p.expected_head_sha)))
      fail('INVALID','duplicate/invalid PR or expected SHA');ids.add(p.number);
  }
  if(!Array.isArray(s.workflow_paths)||s.workflow_paths.length<1||s.workflow_paths.length>MAX_WORKFLOWS||
    new Set(s.workflow_paths).size!==s.workflow_paths.length||
    s.workflow_paths.some(x=>typeof x!=='string'||x.length>160||
      !/^\.github\/workflows\/[A-Za-z0-9_.-]+\.ya?ml$/.test(x)))
    fail('INVALID','unbounded/invalid expected CI workflow paths');
  return s;
}
function sourceURL(repo,part){return 'https://api.github.com/repos/'+repo+'/'+part;}
async function bounded(response,url) {
  if(!response||response.status!==200)fail('UNKNOWN','GitHub unavailable or native API status not 200');
  if(response.redirected===true||response.url!==url)fail('UNKNOWN','redirect or altered response URL');
  const declared=response.headers?.get?.('content-length');
  if(declared!==null&&declared!==undefined&&declared!==''){
    const n=Number(declared);
    if(!Number.isFinite(n)||n<0||n>MAX_RESPONSE)fail('UNKNOWN','unbounded native response length');
  }
  let raw;
  if(response.body?.getReader){
    const reader=response.body.getReader(),parts=[];let size=0;
    try{
      while(true){
        const {value,done}=await reader.read();if(done)break;
        size+=value.byteLength;
        if(size>MAX_RESPONSE)fail('UNKNOWN','response stream oversized');
        parts.push(Buffer.from(value));
      }
    } finally{reader.releaseLock();}
    try{raw=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(parts));}
    catch{fail('UNKNOWN','invalid native UTF8');}
  }else if(typeof response.text==='function'){
    raw=await response.text();
    if(typeof raw!=='string'||Buffer.byteLength(raw,'utf8')>MAX_RESPONSE)
      fail('UNKNOWN','oversized/native response text invalid');
  }else fail('UNKNOWN','missing HTTP body');
  try{return JSON.parse(raw);}catch{fail('UNKNOWN','malformed native response JSON');}
}
function protectProvider(v,label){
  if(!v||typeof v!=='object'||Array.isArray(v))fail('REFUTED',label+' provider object invalid');
  return v;
}
function issueFact(v,repository,n){
  protectProvider(v,'issue');
  const html='https://github.com/'+repository+'/issues/'+n;
  if(v.number!==n||v.url!==sourceURL(repository,'issues/'+n)||
    v.html_url!==html||!['open','closed'].includes(v.state)||
    typeof v.title!=='string'||!v.title.trim()||
    !iso(v.created_at)||!iso(v.updated_at)||
    Date.parse(v.created_at)>Date.parse(v.updated_at)||
    Object.hasOwn(v,'pull_request'))
    fail('REFUTED','issue identity/dates invalid or target is really a PR');
  return Object.freeze({
    number:n,source_url:html,state:v.state,title:v.title,
    updated_at:v.updated_at,observed_from:'GITHUB_ISSUES_API',
    // Provider issue title/body is NOT a review verdict nor Owner instruction.
    scoreboard_text_not_authority:true
  });
}
function prFact(v,repository,spec){
  protectProvider(v,'pull');
  const n=spec.number,html='https://github.com/'+repository+'/pull/'+n;
  if(v.number!==n||v.url!==sourceURL(repository,'pulls/'+n)||
    v.html_url!==html||!['open','closed'].includes(v.state)||
    typeof v.draft!=='boolean'||typeof v.merged!=='boolean'||
    !v.head||!v.base||!SHA.test(v.head.sha)||!SHA.test(v.base.sha)||
    v.head.repo?.full_name?.toLowerCase()!==repository.toLowerCase()||
    v.base.repo?.full_name?.toLowerCase()!==repository.toLowerCase()||
    typeof v.title!=='string'||!v.title.trim()||
    !iso(v.created_at)||!iso(v.updated_at)||
    Date.parse(v.created_at)>Date.parse(v.updated_at))
    fail('REFUTED','PR identity, refs or dates disagree with scope');
  if(v.merged&&v.state!=='closed')fail('REFUTED','merged PR cannot be open');
  const currentness=spec.expected_head_sha===null?'UNPINNED':
    (v.head.sha===spec.expected_head_sha?'MATCH':'STALE');
  return Object.freeze({
    number:n,source_url:html,state:v.state,title:v.title,
    draft:v.draft,merged:v.merged,
    head_sha:v.head.sha,base_sha:v.base.sha,
    head_ref:v.head.ref,base_ref:v.base.ref,
    updated_at:v.updated_at,currentness,
    expected_head_sha:spec.expected_head_sha,
    observed_from:'GITHUB_PULLS_API',
    // No claims about review approval; see separate review APIs and policies.
    author_supplied_description_not_authority:true
  });
}
function workflowResult(payload,repository,head,paths){
  protectProvider(payload,'Actions');
  if(!Number.isSafeInteger(payload.total_count)||payload.total_count<0||
    !Array.isArray(payload.workflow_runs)||payload.workflow_runs.length>100)
    fail('REFUTED','unbounded/invalid Actions response');
  // The first 100 entries are not proof of absent runs if GitHub paginated.
  if(payload.total_count<payload.workflow_runs.length)
    fail('REFUTED','Actions total_count fewer than supplied workflow runs');
  if(payload.total_count>100)return paths.map(path=>({
    path,state:'UNKNOWN',reason:'UNREAD_PAGINATED_RESULTS',run_id:null,
    source_url:null,head_sha:head
  }));
  const relevant=new Map();
  for(const run of payload.workflow_runs){
    if(!run||typeof run!=='object'||Array.isArray(run))fail('REFUTED','invalid Actions entry');
    if(run.head_sha!==head)continue; // Provider may return unrelated entries. Never trust their outcomes.
    const path=typeof run.path==='string'?run.path.split('@')[0]:null;
    if(!paths.includes(path))continue;
    if(!Number.isSafeInteger(run.id)||run.id<1||
      run.html_url!=='https://github.com/'+repository+'/actions/runs/'+run.id||
      typeof run.status!=='string'||!iso(run.created_at)||
      !(typeof run.conclusion==='string'||run.conclusion===null))
      fail('REFUTED','invalid provider Actions run for expected workflow');
    const old=relevant.get(path);
    if(!old||Date.parse(run.created_at)>Date.parse(old.created_at)||
      (Date.parse(run.created_at)===Date.parse(old.created_at)&&run.id>old.id))
      relevant.set(path,run);
  }
  return paths.map(path=>{
    const run=relevant.get(path);
    if(!run)return {path,state:'UNKNOWN',reason:'NO_EXACT_HEAD_RUN_OBSERVED',
      run_id:null,source_url:null,head_sha:head};
    const state=run.status!=='completed'?'PENDING':
      (run.conclusion==='success'?'PASS':'FAIL');
    return {path,state,reason:state==='PASS'?'EXACT_HEAD_HOSTED_SUCCESS':
      state==='PENDING'?'EXACT_HEAD_HOSTED_IN_PROGRESS':'EXACT_HEAD_HOSTED_NON_SUCCESS',
      run_id:run.id,source_url:run.html_url,head_sha:head,
      run_status:run.status,run_conclusion:run.conclusion};
  });
}
function snapshotDigest(value){return createHash('sha256').update(canonicalJSON(value)).digest('hex');}
// Ephemeral R3-source capability: only this native reader can enroll the exact
// frozen object it returned. Neither JSON nor SHA256 carries the capability.
// Cross-process consumers must re-acquire from R3 and cannot restore the mark.
const nativeReadSnapshots=new WeakSet();
export function hasNativeProviderAcquisition(snapshot){
  return !!snapshot&&typeof snapshot==='object'&&nativeReadSnapshots.has(snapshot);
}
function freezeSnapshot(root){
  // The digest is over this entire provider view; callers must not mutate a
  // nested PR/CI fact after digest computation and keep a misleading checksum.
  const seen=new Set(),stack=[root];
  while(stack.length){
    const item=stack.pop();
    if(!item||typeof item!=='object'||seen.has(item))continue;
    seen.add(item);
    for(const value of Object.values(item))if(value&&typeof value==='object')stack.push(value);
    Object.freeze(item);
  }
  return root;
}

/** A new provider-current read each call; no cache, no mutations.
 * It represents the scope's issues/PRs/head-workflows, NOT source history
 * or Owner authorization. Fail closed on provider uncertainty.
 */
export async function reconcileGitHubFacts(rawScope,options={}){
  const scope=scoped(rawScope);
  if(!options||typeof options!=='object'||Array.isArray(options)||
    Object.keys(options).some(k=>!['fetchImpl','readToken','observedAt'].includes(k)))
    fail('INVALID','unknown native reader options');
  const injected=Object.hasOwn(options,'fetchImpl');
  const fetcher=injected?options.fetchImpl:globalThis.fetch;
  if(typeof fetcher!=='function')fail('UNKNOWN','native HTTPS fetch not available');
  if(options.readToken!==undefined&&(typeof options.readToken!=='string'||
    !/^[\x21-\x7e]{1,400}$/.test(options.readToken)))fail('INVALID','invalid read-only token');
  const observed=options.observedAt??new Date().toISOString();
  if(!iso(observed))fail('INVALID','invalid snapshot observed time');
  const hdr={Accept:'application/vnd.github+json',
    'X-GitHub-Api-Version':'2022-11-28','User-Agent':'relay-reset-r3-native-facts-v1'};
  if(options.readToken)hdr.Authorization='Bearer '+options.readToken;
  let reads=0;
  async function get(part){
    const url=sourceURL(scope.repository,part);reads++;
    let response;
    try{response=await fetcher(url,{method:'GET',redirect:'error',cache:'no-store',headers:hdr});}
    catch{fail('UNKNOWN','native read failed');}
    return bounded(response,url);
  }
  const parent=issueFact(await get('issues/'+scope.parent_issue),scope.repository,scope.parent_issue);
  const children=[];
  for(const n of scope.child_issues)
    children.push(issueFact(await get('issues/'+n),scope.repository,n));
  const prs=[];
  for(const p of scope.pull_requests){
    const fact=prFact(await get('pulls/'+p.number),scope.repository,p);
    const facts=workflowResult(
      await get('actions/runs?head_sha='+fact.head_sha+'&per_page=100'),
      scope.repository,fact.head_sha,scope.workflow_paths);
    // Re-read the PR after its CI. The first head is not a current-state
    // guarantee if a force-push, draft toggle, merge or title change races us.
    const after=prFact(await get('pulls/'+p.number),scope.repository,p);
    if(fact.head_sha!==after.head_sha||fact.base_sha!==after.base_sha||
      fact.head_ref!==after.head_ref||fact.base_ref!==after.base_ref||
      fact.draft!==after.draft||fact.merged!==after.merged||
      fact.state!==after.state||fact.title!==after.title||
      fact.updated_at!==after.updated_at)
      fail('STALE','PR changed while fetching exact-head CI; repeat entire read');
    prs.push(Object.freeze({...after,ci_workflows:Object.freeze(facts)}));
  }
  const core={
    schema:'relay-provider-facts-v1',repository:scope.repository,observed_at:observed,
    parent_issue:parent,child_issues:children,pr_facts:prs,
    relationship_assertion:'CALLER_SCOPED_UNVERIFIED',
    provider_transport:injected?'INJECTED_UNVERIFIED':'NATIVE_GITHUB_GET',
    read_count:reads,source_state:injected?'INJECTED_UNVERIFIED':'PROVIDER_OBSERVED',
    consistency:'PR_DOUBLE_READ_NON_ATOMIC',
    evidence_acceptance:'NOT_EVALUATED',human_review:'NOT_EVALUATED',
    owner_intent:'NOT_AUTHENTICATED',independent_journal_tip:'NOT_ANCHORED',
    actual_next:'UNDETERMINED_PROVIDER_ONLY_REQUIRES_LINEAGE_AND_ACCEPTED_EVIDENCE',
    // Critical: even a matching PR + success CI is NEVER accepted TASK_EVIDENCE.
    authorization_granted:false,independently_accepted:false,live_writer_enabled:false
  };
  const result=freezeSnapshot({...core,snapshot_sha256:snapshotDigest(core)});
  if(!injected)nativeReadSnapshots.add(result);
  return result;
}
