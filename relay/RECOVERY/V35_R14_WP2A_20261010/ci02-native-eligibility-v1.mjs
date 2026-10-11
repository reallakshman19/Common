/* CI02: observe one actual in-repository pull-request source window only.
 * This validates the execution envelope, NOT the material's admissibility.
 * No new source authority, reviewer, DELP, evidence, or writer is granted.
 */
const REPO='reallakshman19/Common';
const SHA=/^[a-f0-9]{40}$/;
const BRANCH=/^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
export function parseCi02NativeEnvelope(env){
  if(!env||env.GITHUB_EVENT_NAME!=='pull_request'||
     env.CANDIDATE_REPOSITORY!==REPO||env.CANDIDATE_HEAD_REPO!==REPO)return null;
  const num=Number(env.CANDIDATE_PR_NUMBER);
  const sha=env.CANDIDATE_HEAD_SHA;
  const base=env.CANDIDATE_BASE_REF;
  if(!Number.isSafeInteger(num)||num<1||
     !SHA.test(sha||'')||
     typeof base!=='string'||!BRANCH.test(base)||base.includes('..')||
     base.includes('//')||base.endsWith('/'))return null;
  return Object.freeze({pr:num,sha,base,repository:REPO});
}
