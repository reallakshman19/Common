/* Recovery #5 M0: structural provider-identity *reference* gate.
 * Offline, read-only. Content checks cannot authenticate actual GitHub provider GETs,
 * Owner intentions, independent reviews, current HEAD, or grant any writer right.
 */
const SHA = /^[0-9a-f]{40}$/;
const NAME = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const BRANCH = /^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
const plain = v => v !== null && typeof v === 'object' && !Array.isArray(v) &&
  Object.getPrototypeOf(v) === Object.prototype;
const exact = (v, fields) => plain(v) &&
  Object.keys(v).length === fields.length && fields.every(k => Object.hasOwn(v, k));
const numeric = x => Number.isSafeInteger(x) && x > 0;
const linkFor = (name, kind, n) => 'https://github.com/' + name + '/' +
  (kind === 'ISSUE' ? 'issues' : 'pull') + '/' + n;

export function validateMigrationManifest(v) {
  const faults = [];
  const bad = (code, detail='') => faults.push(detail ? code + ':' + detail : code);
  if (!exact(v,['schema','source_scope','observed_date','recovery_issue','repositories','objects','branches','trust_gates']))
    return result(['BAD_ROOT_SHAPE']);
  if (v.schema !== 'common-v35-repository-cutover-manifest-v1' ||
      v.source_scope !== 'PUBLIC_PROVIDER_CENSUS_ONLY' ||
      !/^\d{4}-\d{2}-\d{2}$/.test(v.observed_date) || !numeric(v.recovery_issue))
    bad('BAD_MANIFEST_IDENTITY');
  const repos = v.repositories;
  if (!exact(repos,['historical','destination'])) return result(['BAD_REPOSITORY_PAIR']);
  const validRepo = o => exact(o,['provider','repository_id','full_name','main_sha']) &&
    o.provider === 'github' && numeric(o.repository_id) && NAME.test(o.full_name) &&
    SHA.test(o.main_sha);
  if (!validRepo(repos.historical) || !validRepo(repos.destination))
    return result(['BAD_REPOSITORY_REFERENCE']);
  if (repos.historical.repository_id === repos.destination.repository_id ||
      repos.historical.full_name === repos.destination.full_name)
    bad('IDENTICAL_REPOSITORY_NOT_MIGRATION');
  const ref = (r, expected, kind) => exact(r,['repository_id','number','url']) &&
    r.repository_id === expected.repository_id && numeric(r.number) &&
    r.url === linkFor(expected.full_name,kind,r.number);
  const usedOld = new Set(), usedNew = new Set();
  if (!Array.isArray(v.objects) || !v.objects.length) bad('MISSING_OBJECTS');
  else for (const [i,o] of v.objects.entries()) {
    if (!exact(o,['kind','origin','destination','relation','authority']) ||
        !['ISSUE','PR'].includes(o.kind) || o.authority !== 'NOT_TRANSFERRED') {
      bad('BAD_OBJECT_SHAPE',String(i)); continue;
    }
    if (!ref(o.origin,repos.historical,o.kind)) bad('ORIGIN_NAMESPACE_MISMATCH',String(i));
    const oid = o.kind + ':' + String(o.origin?.number);
    if (usedOld.has(oid)) bad('DUPLICATE_ORIGIN',oid); usedOld.add(oid);
    const historical = o.relation === 'HISTORICAL_ONLY';
    const allowed = o.kind === 'ISSUE' ? ['HISTORICAL_ONLY','PURPOSE_CONTINUATION'] :
      ['HISTORICAL_ONLY','SOURCE_BRANCH_CONTINUATION','RELATED_NEW_IMPLEMENTATION'];
    if (!allowed.includes(o.relation)) bad('UNAUTHORIZED_RELATION',oid);
    if (historical && o.destination !== null) bad('HISTORICAL_ONLY_HAS_DESTINATION',oid);
    if (!historical) {
      if (!ref(o.destination,repos.destination,o.kind)) bad('DESTINATION_NAMESPACE_MISMATCH',oid);
      const did = o.kind + ':' + String(o.destination?.number);
      if (usedNew.has(did)) bad('DUPLICATE_DESTINATION',did); usedNew.add(did);
    }
  }
  const branches = v.branches;
  if (!Array.isArray(branches) || !branches.length) bad('MISSING_BRANCHES');
  else {
    const usedPr = new Set(), usedPath = new Set();
    for (const [i,b] of branches.entries()) {
      if (!exact(b,['origin_pr','branch','origin_head_sha','destination_head_sha','relation','ahead_commits']) ||
          !numeric(b.origin_pr) || !BRANCH.test(b.branch) || b.branch.includes('..') ||
          !SHA.test(b.origin_head_sha) || !SHA.test(b.destination_head_sha) ||
          !Number.isSafeInteger(b.ahead_commits) || b.ahead_commits < 0) {
        bad('BAD_BRANCH_SHAPE',String(i)); continue;
      }
      if (usedPr.has(b.origin_pr) || usedPath.has(b.branch)) bad('DUPLICATE_BRANCH',String(i));
      usedPr.add(b.origin_pr); usedPath.add(b.branch);
      if (!usedOld.has('PR:' + b.origin_pr)) bad('BRANCH_WITHOUT_ORIGIN_PR',String(i));
      if (b.origin_head_sha === b.destination_head_sha) {
        if (b.relation !== 'EXACT_HEAD_MATCH' || b.ahead_commits !== 0)
          bad('FALSE_EXACT_HEAD_CLASSIFICATION',String(i));
      } else if (b.relation !== 'SOURCE_ADVANCED' || b.ahead_commits < 1) {
        bad('UNVERIFIED_HEAD_CHANGE_CLASSIFICATION',String(i));
      }
    }
  }
  const gates = v.trust_gates;
  if (!exact(gates,['owner_original_source','reviewer_authority','source_reference_authority','exclusive_writer_lease','live_publisher','accepted_programme_acs']) ||
      gates.owner_original_source !== 'UNKNOWN' ||
      gates.reviewer_authority !== 'NOT_TRANSFERRED' ||
      gates.source_reference_authority !== 'UNATTESTED' ||
      gates.exclusive_writer_lease !== 'NOT_PROVEN' ||
      gates.live_publisher !== 'OFF' || gates.accepted_programme_acs !== 0)
    bad('FORGED_AUTHORITY_OR_PROGRESS');
  return result(faults);
  function result(errors) {
    return Object.freeze({schema:'common-v35-m0-validation-result-v1',
      valid:errors.length===0,errors:Object.freeze(errors),
      provider_identity:'CALLER_REFERENCED_NOT_LIVE_ATTESTED',
      owner_authority:'NOT_AUTHENTICATED',
      reviewer_authority:'NOT_QUALIFIED',
      writer_authorization:'NOT_GRANTED',
      programme_acceptance:'NOT_EVALUATED'});
  }
}
