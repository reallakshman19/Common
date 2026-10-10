/* WP2-B B01-B03: read-only pre-admission diagnostic.
 * THIS MODULE HAS NO POSITIVE ADMISSION PATH AND NEVER CALLS DELP OR A WRITER.
 * The input is a candidate locator, not Owner policy, review or an R3 witness.
 */
import {createHash} from 'node:crypto';
import {observeCrossSource,observeLiveCrossSource}
  from '../V35_R14_WP2A_20261010/cross-source-vector-v1.mjs';

const REPO='reallakshman19/Common',REPO_ID=1412133785;
const SCHEMA='common-v35-r12-u3-delp-pre-admission-v1';
const FACTS_SCHEMAS=Object.freeze({
  V32:'relay-v3.2-delp-checkpoint-facts',
  V35:'relay-v3.5-delp-checkpoint-facts',
});
const SHA=/^[a-f0-9]{40}$/,DIGEST=/^sha256:[a-f0-9]{64}$/;
const OBJ=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const POS=x=>Number.isSafeInteger(x)&&x>0;
const allowed=['repository','repository_id','root_issue','leaf_issue','pr_number',
  'candidate_head_sha','base_branch','evidence_comment_id',
  'evidence_claimed_head_sha','expected_author_login','facts_schema_line'];
const baseKeys=allowed.filter(x=>x!=='facts_schema_line');
const stable=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function inputValid(i){
  return OBJ(i)&&Object.keys(i).length===allowed.length&&
    allowed.every(x=>Object.hasOwn(i,x))&&
    i.repository===REPO&&i.repository_id===REPO_ID&&
    [i.root_issue,i.leaf_issue,i.pr_number,i.evidence_comment_id].every(POS)&&
    i.root_issue!==i.leaf_issue&&SHA.test(i.candidate_head_sha)&&
    SHA.test(i.evidence_claimed_head_sha)&&
    typeof i.base_branch==='string'&&/^[A-Za-z0-9][A-Za-z0-9._/-]*$/.test(i.base_branch)&&
    !i.base_branch.includes('..')&&!i.base_branch.includes('//')&&!i.base_branch.endsWith('/')&&
    typeof i.expected_author_login==='string'&&
    /^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i.test(i.expected_author_login)&&
    Object.hasOwn(FACTS_SCHEMAS,i.facts_schema_line);
}
const normalizeInput=i=>Object.fromEntries(baseKeys.map(k=>[k,i[k]]));
const uniq=x=>[...new Set(x)];
const fingerprint=v=>'sha256:'+createHash('sha256').update('common-wp2b-source-v1\0'+JSON.stringify(v)).digest('hex');
function diagnostic(i,stage,grade){
  const failures=[];
  if(!OBJ(stage)||stage.schema!=='common-v35-wp2a-u04-cross-source-v1'||
    stage.source_consistent!==true||!OBJ(stage.source_vector)||
    !DIGEST.test(stage.source_vector_sha256||'')||
    stage.error!==null||
    !['CONSISTENT_HISTORICAL_EVIDENCE_ONLY','CONSISTENT_AUTHOR_CLAIM_ONLY'].includes(stage.material_status)
  )failures.push('CROSS_SOURCE_NOT_VERIFIED');
  if(!failures.length){
    const v=stage.source_vector;
    if(stage.source_grade!==grade||stage.evidence_admitted!==false||
       stage.writer_authorized!==false||stage.programme_progress!==null||
       stage.owner_authenticated!==false||stage.reviewer_qualified!==false||
       stage.required_ci_qualified!==false||
       v.repository!==REPO||v.repository_id!==REPO_ID||
       v.root_issue!==i.root_issue||v.leaf_issue!==i.leaf_issue||
       v.pr_number!==i.pr_number||v.candidate_sha!==i.candidate_head_sha||
       v.base_branch!==i.base_branch||
       v.evidence_comment_id!==i.evidence_comment_id||
       v.evidence_claimed_head_sha!==i.evidence_claimed_head_sha||
       !DIGEST.test(v.candidate_source_sha256||'')||
       !DIGEST.test(v.selected_required_ci_sha256||'')||
       !DIGEST.test(v.evidence_comment_sha256||''))
       failures.push('CROSS_SOURCE_BINDING_OR_AUTHORITY_INVALID');
    if(v.required_ci_policy!=='OBSERVED_CLASSIC_AND_RULESET'||
       v.required_ci_result!=='ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS')
       failures.push('REQUIRED_CI_NOT_QUALIFIED');
    if(v.evidence_currentness!=='MATCH_AT_OBSERVATION')
       failures.push('EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN');
  }
  // Even with complete factual material these are separate external gates,
  // not caller-supplied booleans, source grades, GitHub bodies or SHA hashes.
  failures.push('ORIGINAL_OWNER_SOURCE_NOT_AUTHENTICATED');
  failures.push('EVIDENCE_POLICY_VERSION_NOT_ADOPTED');
  failures.push('TWO_INDEPENDENT_REVIEW_VERDICTS_MISSING');
  failures.push('R12_R3_NATIVE_WITNESS_NOT_TRANSFERRED');
  failures.push('U3_POSITIVE_ADMISSION_NOT_IMPLEMENTED');
  failures.push('CANONICAL_PROGRAMME_DELP_NOT_SELECTED');
  failures.push('LIVE_PUBLISHER_NOT_AUTHORIZED');
  return {
    schema:SCHEMA,
    candidate_facts_schema:FACTS_SCHEMAS[i.facts_schema_line],
    target_delp_policy:'NOT_ADOPTED',
    observation_grade:grade,
    source_status:failures.some(x=>x.startsWith('CROSS_SOURCE'))?'UNKNOWN':
      'REFERENCES_COHERENT_BUT_UNADMITTED',
    source_digest:OBJ(stage)&&stage.source_consistent===true&&
      DIGEST.test(stage.source_vector_sha256||'')&&
      !failures.some(x=>x.startsWith('CROSS_SOURCE'))?
      fingerprint({candidate:i.candidate_head_sha,predecessor:stage.source_vector_sha256}):null,
    admission:'NOT_ADMITTED',
    admission_blockers:uniq(failures),
    owner_authenticated:false,reviewer_qualified:false,
    evidence_admitted:false,programme_progress:null,
    delp_projector_invoked:false,writer_authorized:false,
    runner_lease:'NOT_PROVEN',
  };
}
function refusal(reason,grade){
  return {
    schema:SCHEMA,candidate_facts_schema:null,target_delp_policy:'NOT_ADOPTED',
    observation_grade:grade,source_status:'UNKNOWN',source_digest:null,
    admission:'NOT_ADMITTED',admission_blockers:[reason],
    owner_authenticated:false,reviewer_qualified:false,
    evidence_admitted:false,programme_progress:null,
    delp_projector_invoked:false,writer_authorized:false,
    runner_lease:'NOT_PROVEN',
  };
}
/** Injected shared-provider material: never native, even if the reader fakes it. */
export async function inspectPreAdmission(i,readers){
  const grade='CALLER_INJECTED_UNATTESTED';
  if(!inputValid(i))return refusal('INPUT_CONTRACT_OR_FACTS_SCHEMA_INVALID',grade);
  if(!OBJ(readers)||['candidate','ci','evidence'].some(k=>typeof readers[k]!=='function'))
    return refusal('PROVIDER_READERS_MISSING',grade);
  try{
    const stage=await observeCrossSource(normalizeInput(i),readers);
    return diagnostic(i,stage,grade);
  }catch{return refusal('PRE_ADMISSION_READ_FAILED',grade);}
}
/** Native path uses only the actual U04 physical provider readers; no caller-supplied grade. */
export async function inspectLivePreAdmission(i,opts={}){
  const grade='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION';
  if(!inputValid(i))return refusal('INPUT_CONTRACT_OR_FACTS_SCHEMA_INVALID',grade);
  try{
    const stage=await observeLiveCrossSource(normalizeInput(i),opts);
    return diagnostic(i,stage,grade);
  }catch{return refusal('PRE_ADMISSION_READ_FAILED',grade);}
}
