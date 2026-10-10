/* WP2-B GET-only smoke configuration: historical stale and current author-claim
 * diagnostic modes. Neither path can accept evidence or invoke a writer.
 */
const SHA=/^[a-f0-9]{40}$/;
const DIGEST=/^sha256:[a-f0-9]{64}$/;
const PR=/^[1-9][0-9]*$/;
const BASE=/^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
const HISTORICAL_ID=6093641044;
const HISTORICAL_HEAD='64e494f6cc4bca5764b1b94ff4fe58d16da29d30';
const has=(x,k)=>Object.hasOwn(x,k);
const positive=x=>typeof x==='string'&&PR.test(x)&&Number.isSafeInteger(Number(x));

export function buildNativeSmokeConfig(env){
  if(!env||typeof env!=='object'||
     !positive(env.CANDIDATE_PR_NUMBER)||!SHA.test(env.CANDIDATE_HEAD_SHA||'')||
     typeof env.CANDIDATE_BASE_REF!=='string'||
     !BASE.test(env.CANDIDATE_BASE_REF)||env.CANDIDATE_BASE_REF.includes('..')||
     env.CANDIDATE_BASE_REF.includes('//')||env.CANDIDATE_BASE_REF.endsWith('/'))
    throw new TypeError('CANDIDATE_CONFIG_INVALID');
  const c=has(env,'CURRENT_EVIDENCE_COMMENT_ID');
  const h=has(env,'CURRENT_EVIDENCE_CLAIMED_HEAD_SHA');
  if(c!==h)throw new TypeError('CURRENT_EVIDENCE_CONFIG_INVALID');
  if(c&&(!positive(env.CURRENT_EVIDENCE_COMMENT_ID)||
         !SHA.test(env.CURRENT_EVIDENCE_CLAIMED_HEAD_SHA||'')))
    throw new TypeError('CURRENT_EVIDENCE_CONFIG_INVALID');
  if(c&&env.CURRENT_EVIDENCE_CLAIMED_HEAD_SHA!==env.CANDIDATE_HEAD_SHA)
    throw new TypeError('CURRENT_EVIDENCE_HEAD_NOT_CURRENT');
  return {
    mode:c?'CURRENT_AUTHOR_CLAIM':'HISTORICAL_STALE',
    locator:{
      repository:'reallakshman19/Common',repository_id:1412133785,
      root_issue:5,leaf_issue:30,
      pr_number:Number(env.CANDIDATE_PR_NUMBER),
      candidate_head_sha:env.CANDIDATE_HEAD_SHA,
      base_branch:env.CANDIDATE_BASE_REF,
      evidence_comment_id:c?Number(env.CURRENT_EVIDENCE_COMMENT_ID):HISTORICAL_ID,
      evidence_claimed_head_sha:c?env.CURRENT_EVIDENCE_CLAIMED_HEAD_SHA:HISTORICAL_HEAD,
      expected_author_login:'reallakshman19',
      facts_schema_line:'V35',
    },
  };
}

export function qualifiesNegativeSmoke(r,mode){
  if(!r||typeof r!=='object'||Array.isArray(r)||!Array.isArray(r.admission_blockers)||
     r.source_status!=='REFERENCES_COHERENT_BUT_UNADMITTED'||
     r.observation_grade!=='NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION'||
     !DIGEST.test(r.source_digest||'')||
     r.admission!=='NOT_ADMITTED'||r.evidence_admitted!==false||
     r.delp_projector_invoked!==false||r.programme_progress!==null||
     r.writer_authorized!==false||r.owner_authenticated!==false||
     r.reviewer_qualified!==false)return false;
  const stale=r.admission_blockers.includes('EVIDENCE_CANDIDATE_STALE_OR_UNKNOWN');
  if(mode==='HISTORICAL_STALE')return stale;
  if(mode==='CURRENT_AUTHOR_CLAIM')return !stale&&
    r.admission_blockers.includes('EVIDENCE_POLICY_VERSION_NOT_ADOPTED')&&
    r.admission_blockers.includes('U3_POSITIVE_ADMISSION_NOT_IMPLEMENTED');
  return false;
}
