/* Recovery #5 / M0 provider readback, native read-only.
 * Confirms current public GitHub object presence, branch ancestry and identity.
 * It does NOT verify an original private Owner chat, policy, review authority,
 * evidence admission, selected/required CI, or GitHub writer custody.
 */
import {validateMigrationManifest} from './validate-migration-manifest-v1.mjs';

const SHA = /^[0-9a-f]{40}$/;
const isObject = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const REFRESH = 'REFRESH_REQUIRED';
const href = (slug,kind,n) =>
  'https://github.com/' + slug + '/' + (kind === 'ISSUE' ? 'issues' : 'pull') + '/' + n;

export async function auditNativeProvider(manifest, getJSON) {
  const errors = [];
  const bad = (code, detail) => errors.push(code + ':' + String(detail).slice(0,160));
  const refusal = () => Object.freeze({
    schema: 'common-v35-native-provider-audit-v1',
    current: false,
    errors: Object.freeze([...errors]),
    provider_identity: errors.length ? 'NOT_CURRENT_OR_UNVERIFIED' : 'CALLER_SUPPLIED_PROVIDER_RESPONSES_UNATTESTED',
    reviewed: false, owner_authenticated: false, evidence_accepted: false,
    writer_authorized: false, programme_acceptance: 'NOT_EVALUATED',
  });
  const structural = validateMigrationManifest(manifest);
  if (!structural.valid) {
    bad('BAD_REFERENCE_MANIFEST', structural.errors.join(','));
    return refusal();
  }
  if (typeof getJSON !== 'function') {
    bad('NO_NATIVE_PROVIDER_READER', 'getJSON must be a function');
    return refusal();
  }
  // Fail closed on failed/partial source reads. No inferred absence from 404/403/429.
  async function read(slug, apiPath) {
    try {
      const result = await getJSON(slug,apiPath);
      if (!isObject(result)) throw new Error('not a JSON object');
      return result;
    } catch {
      bad('PROVIDER_READ_FAILED',slug + '/' + apiPath);
      return null;
    }
  }

  const repos = manifest.repositories;
  for (const role of ['historical','destination']) {
    const v = repos[role], obj = await read(v.full_name, '');
    if (!obj) continue;
    if (obj.id !== v.repository_id || obj.full_name !== v.full_name ||
        obj.default_branch !== 'main') bad('REPOSITORY_ID_MISMATCH',role);
    const main = await read(v.full_name,'git/ref/heads/main');
    if (!main || main.object?.sha !== v.main_sha ||
        main.ref !== 'refs/heads/main' || !SHA.test(String(main.object?.sha || ''))) {
      bad('STALE_MAIN_HEAD',role);
    }
  }

  const branchByPr = new Map(manifest.branches.map(b=>[b.origin_pr,b]));
  for (const item of manifest.objects) {
    const r = repos.historical, old = item.origin;
    const source = await read(r.full_name,
      (item.kind === 'ISSUE' ? 'issues/' : 'pulls/') + old.number);
    const oldOK = source && source.number === old.number &&
      source.html_url === href(r.full_name,item.kind,old.number) &&
      ['open','closed'].includes(source.state) &&
      (item.kind === 'ISSUE' ? !Object.hasOwn(source,'pull_request') :
        isObject(source.head) && SHA.test(String(source.head.sha || '')) &&
        source.head.repo?.full_name === r.full_name &&
        source.base?.repo?.full_name === r.full_name);
    if (!oldOK) bad('ORIGIN_OBJECT_MISMATCH',item.kind+'#'+old.number);
    const branch = branchByPr.get(old.number);
    if (item.kind === 'PR' && branch && oldOK &&
        (source.head.sha !== branch.origin_head_sha ||
         source.head.ref !== branch.branch)) {
      bad(REFRESH, 'origin PR#'+old.number+' head/ref changed');
    }
    if (item.destination === null) continue;

    const d = repos.destination, to = item.destination;
    const dest = await read(d.full_name,
      (item.kind === 'ISSUE' ? 'issues/' : 'pulls/') + to.number);
    const destOK = dest && dest.number === to.number &&
      dest.html_url === href(d.full_name,item.kind,to.number) &&
      ['open','closed'].includes(dest.state) &&
      (item.kind === 'ISSUE' ? !Object.hasOwn(dest,'pull_request') :
        isObject(dest.head) && SHA.test(String(dest.head.sha || '')) &&
        dest.head.repo?.full_name === d.full_name &&
        dest.base?.repo?.full_name === d.full_name);
    if (!destOK) bad('DESTINATION_OBJECT_MISMATCH',item.kind+'#'+to.number);
    // SOURCE_BRANCH_CONTINUATION is same-ref history. A
    // RELATED_NEW_IMPLEMENTATION is a different native PR with its own ref:
    // do not falsely equate it to the preserved old branch (or claim ancestry).
    if (item.kind === 'PR' && branch && destOK &&
        item.relation === 'SOURCE_BRANCH_CONTINUATION' &&
        (dest.head.sha !== branch.destination_head_sha ||
         dest.head.ref !== branch.branch)) {
      bad(REFRESH,'destination PR#'+to.number+' head/ref changed');
    }
  }

  for (const b of manifest.branches) {
    const target = await read(repos.destination.full_name,'git/ref/heads/'+b.branch);
    if (!target || target.ref !== 'refs/heads/'+b.branch ||
        target.object?.sha !== b.destination_head_sha) {
      bad(REFRESH,'destination branch for PR#'+b.origin_pr);
    }
    if (b.relation !== 'SOURCE_ADVANCED') continue;
    // Native GitHub compare attests that source was really an ancestor,
    // rather than assuming "different SHA" means an advanced branch.
    const compare = await read(repos.destination.full_name,
      'compare/'+b.origin_head_sha+'...'+b.destination_head_sha);
    if (!compare || compare.status !== 'ahead' ||
        compare.ahead_by !== b.ahead_commits || compare.behind_by !== 0) {
      bad('ANCESTRY_OR_AHEAD_MISMATCH','origin PR#'+b.origin_pr);
    }
  }
  const out = refusal();
  return Object.freeze({...out,current:errors.length===0,
    provider_identity:errors.length===0 ?
      'CALLER_SUPPLIED_PROVIDER_RESPONSES_UNATTESTED' : 'NOT_CURRENT_OR_UNVERIFIED'});
}

/* This is the ONLY public production entrypoint claiming a live GitHub GET
 * observation. The injectable verifier above *never* issues that claim.
 * JSON readback copies cannot recreate an in-process provider source.
 */
export async function auditLiveNativeGithub(manifest,{token=''}={}) {
  const result = await auditNativeProvider(manifest,(slug,path)=>
    nativeGithubGet(slug,path,{token}));
  return Object.freeze({...result,provider_identity: result.current ?
    'NATIVE_GET_VERIFIED_AT_OBSERVATION' : 'NOT_CURRENT_OR_UNVERIFIED'});
}

// Never accept caller-supplied arbitrary URLs. Only the two namespace-bounded
// slugs and finite API route forms assembled by auditNativeProvider are read.
export async function nativeGithubGet(slug,apiPath,options={}) {
  if (!['reallaksh19/Common','reallakshman19/Common'].includes(slug) ||
      !/^(?:|git\/ref\/heads\/[A-Za-z0-9._/-]+|issues\/[1-9][0-9]*|pulls\/[1-9][0-9]*|compare\/[0-9a-f]{40}\.\.\.[0-9a-f]{40})$/.test(apiPath) ||
      apiPath.includes('..') && !apiPath.includes('...')) {
    throw new Error('PROVIDER_URL_NOT_ALLOWLISTED');
  }
  const url = 'https://api.github.com/repos/' + slug + (apiPath ? '/' + apiPath : '');
  const headers = {
    'Accept':'application/vnd.github+json',
    'X-GitHub-Api-Version':'2022-11-28',
    'User-Agent':'common-v35-m0-native-readonly-audit',
  };
  if (options.token) headers.Authorization='Bearer '+options.token;
  const fetcher = options.fetchImpl || fetch;
  const res = await fetcher(url,{method:'GET',headers,redirect:'error',
    signal:AbortSignal.timeout(15000)});
  if (!res || res.status !== 200 || res.redirected === true || res.url !== url) {
    throw new Error('GITHUB_GET_UNVERIFIED');
  }
  const raw = await res.text();
  if (typeof raw !== 'string' || Buffer.byteLength(raw,'utf8') > 2_000_000)
    throw new Error('GITHUB_GET_SIZE_EXCEEDED');
  return JSON.parse(raw);
}
