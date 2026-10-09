/* M0-U3: double-read current GitHub PR HEADs without rewriting source history.
 * A mutable destination head is an OBSERVATION, not a migrated review/check.
 * This module cannot grant Owner, Reviewer, DELP or writer authority.
 * Caller-provided readers are always graded INJECTED_UNATTESTED.
 */
import {validateMigrationManifest} from './validate-migration-manifest-v1.mjs';
import {auditNativeProvider,nativeGithubGet} from './audit-native-provider-v1.mjs';

const SHA = /^[0-9a-f]{40}$/;
const clone = v => JSON.parse(JSON.stringify(v));
const isMap = v => v !== null && typeof v === 'object' && !Array.isArray(v);
const safeNumber = x => Number.isSafeInteger(x) && x >= 0;
const refusal = errors => Object.freeze({
  schema:'common-v35-moving-head-observation-v1',
  current:false,
  errors:Object.freeze(errors),
  source_grade:'INJECTED_UNATTESTED',
  owner_authenticated:false,reviewer_qualified:false,
  evidence_accepted:false,writer_authorized:false,
  programme_acceptance:'NOT_EVALUATED',
  source_vector:null,
  manifest_advanced:false,
});

export async function observeMovingHeads(manifest,read) {
  const structural = validateMigrationManifest(manifest);
  if(!structural.valid) return refusal(['BAD_REFERENCE_MANIFEST:'+structural.errors.join(',')]);
  if(typeof read !== 'function') return refusal(['NO_PROVIDER_READER']);
  const next = clone(manifest);
  const errors=[];
  const d = next.repositories.destination, old = next.repositories.historical;
  const branches = new Map(next.branches.map(b=>[b.origin_pr,b]));
  const mapped = next.objects.filter(x=>x.kind==='PR' && x.destination !== null);
  const early=[];
  const doRead=async(slug,path)=>{
    try {
      const obj=await read(slug,path);
      if(!isMap(obj))throw Error('not object');
      return obj;
    }catch {
      errors.push('PROVIDER_READ_FAILED:'+slug+'/'+path);
      return null;
    }
  };

  // FIRST provider read: HEAD and branch must name the same current native commit.
  for(const mapping of mapped){
    const b=branches.get(mapping.origin.number);
    if(!b){errors.push('UNMAPPED_DESTINATION_BRANCH:'+mapping.origin.number);continue;}
    const pr=await doRead(d.full_name,'pulls/'+mapping.destination.number);
    const ref=await doRead(d.full_name,'git/ref/heads/'+b.branch);
    if (!pr||!ref||pr.number!==mapping.destination.number||
        pr.html_url!=='https://github.com/'+d.full_name+'/pull/'+mapping.destination.number||
        pr.head?.ref!==b.branch || pr.head?.repo?.full_name!==d.full_name||
        pr.base?.repo?.full_name!==d.full_name||
        !SHA.test(String(pr.head?.sha||'')) ||
        ref.ref!=='refs/heads/'+b.branch||ref.object?.sha!==pr.head.sha){
      errors.push('MOVING_PR_OR_BRANCH_MISMATCH:'+mapping.destination.number);
      continue;
    }
    // Verify current exact ancestry with a NATIVE compare, not a caller-entered
    // ahead count. Changing source HEAD changes a SOURCE OBSERVATION only.
    const cmp=await doRead(d.full_name,
      'compare/'+b.origin_head_sha+'...'+pr.head.sha);
    if (!cmp || (cmp.status !== 'identical' && cmp.status !== 'ahead') ||
        !safeNumber(cmp.ahead_by) || cmp.behind_by!==0 ||
        (cmp.status==='identical' && (cmp.ahead_by!==0 || b.origin_head_sha!==pr.head.sha)) ||
        (cmp.status==='ahead' && (cmp.ahead_by<1 || b.origin_head_sha===pr.head.sha))){
      errors.push('MOVING_SOURCE_ANCESTRY_INVALID:'+mapping.origin.number);
      continue;
    }
    b.destination_head_sha=pr.head.sha;
    b.ahead_commits=cmp.ahead_by;
    b.relation=cmp.status==='identical'?'EXACT_HEAD_MATCH':'SOURCE_ADVANCED';
    early.push({old_pr:mapping.origin.number,new_pr:mapping.destination.number,
      new_head_sha:pr.head.sha,branch:b.branch,
      ahead:cmp.ahead_by});
  }
  if(errors.length) return refusal(errors);
  const refreshed=validateMigrationManifest(next);
  if(!refreshed.valid) return refusal(['REFRESHED_REFERENCE_INVALID:'+refreshed.errors.join(',')]);

  // SECOND fresh fetch: full native old/new source read, old-HEAD constancy,
  // new issue/PR namespace, new refs and compare ancestry. Never cache the
  // first read's response; a concurrent push MUST be marked stale.
  const audited=await auditNativeProvider(next,read);
  if (!audited.current) return refusal(['REFRESH_REQUIRED',...audited.errors]);

  const source_vector=early.map(x=>Object.freeze({...x}));
  const changed=next.branches.some((b,i)=>
    b.destination_head_sha!==manifest.branches[i].destination_head_sha ||
    b.ahead_commits!==manifest.branches[i].ahead_commits);
  return Object.freeze({
    schema:'common-v35-moving-head-observation-v1',
    current:true, errors:Object.freeze([]),
    source_grade:'INJECTED_UNATTESTED',
    owner_authenticated:false,reviewer_qualified:false,
    evidence_accepted:false,writer_authorized:false,
    programme_acceptance:'NOT_EVALUATED',
    source_vector:Object.freeze(source_vector),
    manifest_advanced:changed,
  });
}

// This fixed production-path reader is the only wrapper permitted to grade
// successful material as a bounded NATIVE GitHub GET. No injectable transport.
export async function observeLiveMovingHeads(manifest,{token=''}={}) {
  const r=await observeMovingHeads(manifest,
    (slug,path)=>nativeGithubGet(slug,path,{token}));
  return Object.freeze({...r,source_grade:r.current ?
    'NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION' : 'NOT_CURRENT_OR_UNVERIFIED'});
}
