/* WP2-A/U01: observe current new-repository issue/PR/head/base material.
 * No review, Owner, CI, evidence, programme DELP, lease or publisher authority.
 * A caller-supplied reader is NEVER native-attested even when its objects look real.
 */
import {createHash} from 'node:crypto';

const REPO='reallakshman19/Common';
const REPO_ID=1412133785;
const SHA=/^[a-f0-9]{40}$/;
const REF=/^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const positive=n=>Number.isSafeInteger(n)&&n>0;
const safeBranch=x=>typeof x==='string'&&REF.test(x)&&!x.includes('..')&&!x.includes('//')&&!x.endsWith('/')&&!x.startsWith('refs/');
const url=(type,n)=>`https://github.com/${REPO}/${type}/${n}`;

function refuse(errors,grade) {
  return Object.freeze({
    schema:'common-v35-wp2a-u01-current-candidate-material-v1',
    current:false,source_grade:grade,errors:Object.freeze([...errors]),
    material_observation:'NOT_CURRENT_OR_UNVERIFIED',source_vector:null,source_vector_sha256:null,
    ci_required_status:'UNKNOWN',task_evidence_status:'NOT_CHECKED',
    owner_authenticated:false,independent_reviewer_qualified:false,
    evidence_admitted:false,canonical_delp_projection:'NOT_CALCULATED',
    programme_progress:null,writer_authorized:false,successor_lease:'NOT_PROVEN',
  });
}

function contractErrors(input) {
  const errs=[];
  if(!obj(input)||Object.keys(input).some(k=>!['repository','repository_id','root_issue','leaf_issue','pr_number','expected_candidate_sha','expected_base_ref'].includes(k)))
    return ['INVALID_CONTRACT_SHAPE'];
  if(input.repository!==REPO||input.repository_id!==REPO_ID)errs.push('WRONG_CURRENT_REPOSITORY');
  if(!positive(input.root_issue)||!positive(input.leaf_issue)||input.root_issue===input.leaf_issue||!positive(input.pr_number))
    errs.push('INVALID_ROOT_LEAF_PR');
  if(typeof input.expected_candidate_sha!=='string'||!SHA.test(input.expected_candidate_sha))
    errs.push('INVALID_EXPECTED_HEAD');
  if(!safeBranch(input.expected_base_ref))errs.push('INVALID_EXPECTED_BASE_REF');
  return errs;
}

function extract(source,input) {
  const {repo,root,leaf,pr,head,base}=source;
  if(!obj(repo)||repo.id!==REPO_ID||repo.full_name!==REPO||typeof repo.default_branch!=='string')
    throw Error('PROVIDER_REPO_IDENTITY_MISMATCH');
  for(const [kind,node,n] of [['root',root,input.root_issue],['leaf',leaf,input.leaf_issue]]) {
    if(!obj(node)||node.number!==n||node.html_url!==url('issues',n)||
       Object.hasOwn(node,'pull_request')||node.state!=='open')
      throw Error('PROVIDER_'+kind.toUpperCase()+'_NOT_OPEN_ISSUE');
  }
  if(!obj(pr)||pr.number!==input.pr_number||pr.html_url!==url('pull',input.pr_number)||
     pr.state!=='open'||!obj(pr.head)||!obj(pr.base)||
     !obj(pr.head.repo)||!obj(pr.base.repo)||
     pr.head.repo.id!==REPO_ID||pr.base.repo.id!==REPO_ID||
     pr.head.repo.full_name!==REPO||pr.base.repo.full_name!==REPO||
     !safeBranch(pr.head.ref)||!safeBranch(pr.base.ref)||
     pr.base.ref!==input.expected_base_ref||
     !SHA.test(String(pr.head.sha||''))||!SHA.test(String(pr.base.sha||'')))
    throw Error('PROVIDER_PR_IDENTITY_OR_BASE_MISMATCH');
  if(pr.head.sha!==input.expected_candidate_sha)
    throw Error('EXPECTED_CANDIDATE_HEAD_MOVED');
  if(!obj(head)||head.ref!==`refs/heads/${pr.head.ref}`||head.object?.sha!==pr.head.sha||
     !obj(base)||base.ref!==`refs/heads/${pr.base.ref}`||base.object?.sha!==pr.base.sha)
    throw Error('PR_HEAD_OR_BASE_BRANCH_REF_MISMATCH');
  return {
    provider_repo_id:REPO_ID,repository:REPO,root_issue:root.number,leaf_issue:leaf.number,
    pr_number:pr.number,pr_url:pr.html_url,pr_state:pr.state,
    candidate_sha:pr.head.sha,candidate_branch:pr.head.ref,
    base_sha:pr.base.sha,base_branch:pr.base.ref,
    repository_default_branch:repo.default_branch,
  };
}

async function round(input,read) {
  // The allowlisted transport is fixed to one known repo and only GET routes.
  const paths=['',`issues/${input.root_issue}`,`issues/${input.leaf_issue}`,`pulls/${input.pr_number}`];
  const [repo,root,leaf,pr]=await Promise.all(paths.map(p=>read(REPO,p)));
  if(!obj(pr)||!obj(pr.head)||!obj(pr.base)||!safeBranch(pr.head.ref)||!safeBranch(pr.base.ref))
    throw Error('INVALID_PR_BEFORE_REF_READ');
  const [head,base]=await Promise.all([
    read(REPO,`git/ref/heads/${pr.head.ref}`),read(REPO,`git/ref/heads/${pr.base.ref}`),
  ]);
  return extract({repo,root,leaf,pr,head,base},input);
}

async function observe(input,read,grade) {
  const invalid=contractErrors(input);
  if(invalid.length)return refuse(invalid,grade);
  if(typeof read!=='function')return refuse(['NO_PROVIDER_READER'],grade);
  try {
    const first=await round(input,read);
    const second=await round(input,read);
    if(JSON.stringify(first)!==JSON.stringify(second))
      return refuse(['CONCURRENT_SOURCE_VECTOR_MOVE'],grade);
    // Stable canonical-field order is intentional; digest binds bytes, not authority.
    const digest=createHash('sha256').update('common-v35-wp2a-u01-v1\0'+JSON.stringify(second)).digest('hex');
    return Object.freeze({
      schema:'common-v35-wp2a-u01-current-candidate-material-v1',
      current:true,source_grade:grade,errors:[],material_observation:'MATCH_AT_OBSERVATION',
      source_vector:Object.freeze(second),source_vector_sha256:`sha256:${digest}`,
      ci_required_status:'UNKNOWN',task_evidence_status:'NOT_CHECKED',
      owner_authenticated:false,independent_reviewer_qualified:false,
      evidence_admitted:false,canonical_delp_projection:'NOT_CALCULATED',
      programme_progress:null,writer_authorized:false,successor_lease:'NOT_PROVEN',
    });
  } catch {
    // Deliberately avoid promoting error text or untrusted provider HTML to trust.
    return refuse(['PROVIDER_READ_OR_IDENTITY_FAILURE'],grade);
  }
}

/** Structural/injected test entrypoint: cannot ever claim native source provenance. */
export const observeCurrentCandidate=(input,read)=>observe(input,read,'CALLER_INJECTED_UNATTESTED');

/** Only this fixed native-GitHub GET path is eligible for a narrow source grade. */
export async function observeLiveCurrentCandidate(input,{token=process.env.GITHUB_TOKEN||''}={}) {
  const {nativeGithubGet}=await import('../../MIGRATIONS/V35_COMMON_CUTOVER_20261009/audit-native-provider-v1.mjs');
  return observe(input,(repo,path)=>nativeGithubGet(repo,path,{token}),
    'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION');
}
