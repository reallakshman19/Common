import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {auditNativeProvider,nativeGithubGet} from './audit-native-provider-v1.mjs';

const baseline = JSON.parse(readFileSync(new URL('./migration-manifest-v1.json',import.meta.url),'utf8'));
const clone = x => structuredClone(x);
const key = (slug,path) => slug + '|' + path;
const href = (slug,kind,n) => 'https://github.com/'+slug+'/' +
  (kind==='ISSUE'?'issues':'pull')+'/'+n;

function makeNativeFixture(manifest=baseline) {
  const m = clone(manifest);
  const got = new Map();
  const roles = m.repositories;
  for (const role of ['historical','destination']) {
    const r = roles[role];
    got.set(key(r.full_name,''),{
      id:r.repository_id,full_name:r.full_name,default_branch:'main'
    });
    got.set(key(r.full_name,'git/ref/heads/main'),{
      ref:'refs/heads/main',object:{sha:r.main_sha}
    });
  }
  const branches = new Map(m.branches.map(b=>[b.origin_pr,b]));
  function object(r,item,source) {
    const branch = branches.get(item.origin.number);
    return {
      number:source.number,
      html_url:href(r.full_name,item.kind,source.number),
      state:'open',
      ...(item.kind==='PR'?{
        draft:true,merged:false,
        head:{
          sha:r===roles.historical?branch.origin_head_sha:
            item.relation==='RELATED_NEW_IMPLEMENTATION'?'da3680459c5b48f44cda822ccf5009be4b035eef':
            branch.destination_head_sha,
          ref:r===roles.destination && item.relation==='RELATED_NEW_IMPLEMENTATION'
            ? 'integrate/v32-relay-continuity-889-890-20261009' : branch.branch,
          repo:{full_name:r.full_name}},
        base:{repo:{full_name:r.full_name}},
      }:{})
    };
  }
  for (const item of m.objects) {
    const r=roles.historical;
    got.set(key(r.full_name,(item.kind==='ISSUE'?'issues/':'pulls/')+item.origin.number),
      object(r,item,item.origin));
    if(item.destination){
      const d=roles.destination;
      got.set(key(d.full_name,(item.kind==='ISSUE'?'issues/':'pulls/')+item.destination.number),
        object(d,item,item.destination));
    }
  }
  for (const b of m.branches) {
    const slug=roles.destination.full_name;
    got.set(key(slug,'git/ref/heads/'+b.branch),{
      ref:'refs/heads/'+b.branch,object:{sha:b.destination_head_sha},
    });
    if(b.relation==='SOURCE_ADVANCED'){
      got.set(key(slug,'compare/'+b.origin_head_sha+'...'+b.destination_head_sha),{
        status:'ahead',ahead_by:b.ahead_commits,behind_by:0
      });
    }
  }
  const calls=[];
  const read = async (slug,path) => {
    calls.push(key(slug,path));
    const v=got.get(key(slug,path));
    if(!v)throw new Error('HTTP 404 or partial fixture');
    return clone(v);
  };
  return {m,got,read,calls};
}
const errors = (result, prefix) => {
  assert.equal(result.current,false,JSON.stringify(result));
  assert.ok(result.errors.some(e=>e.startsWith(prefix)), JSON.stringify(result));
  assert.equal(result.reviewed,false);
  assert.equal(result.writer_authorized,false);
  assert.equal(result.programme_acceptance,'NOT_EVALUATED');
};

test('positive provider GET verifies source/current objects with NO authority grant',async()=>{
  const f=makeNativeFixture();
  const r=await auditNativeProvider(f.m,f.read);
  assert.equal(r.current,true,JSON.stringify(r));
  assert.deepEqual(r.errors,[]);
  assert.equal(r.provider_identity,'CALLER_SUPPLIED_PROVIDER_RESPONSES_UNATTESTED');
  assert.equal(r.owner_authenticated,false);
  assert.equal(r.evidence_accepted,false);
  assert.equal(r.writer_authorized,false);
  assert.ok(f.calls.some(x=>x.endsWith('|git/ref/heads/docs/relay-890-continuity-md-v1')));
  assert.ok(f.calls.some(x=>x.includes('|compare/')));
});

test('new destination PR head drift -> REFRESH_REQUIRED',async()=>{
  const f=makeNativeFixture();
  f.got.get(key(f.m.repositories.destination.full_name,'pulls/3')).head.sha='f'.repeat(40);
  errors(await auditNativeProvider(f.m,f.read),'REFRESH_REQUIRED');
});
test('destination branch ref moved even if PR snapshot remains same -> stale',async()=>{
  const f=makeNativeFixture();let b=f.m.branches.find(x=>x.origin_pr===893);
  f.got.get(key(f.m.repositories.destination.full_name,'git/ref/heads/'+b.branch)).object.sha='f'.repeat(40);
  errors(await auditNativeProvider(f.m,f.read),'REFRESH_REQUIRED');
});
test('origin PR head moved -> stale historical source',async()=>{
  const f=makeNativeFixture();
  f.got.get(key(f.m.repositories.historical.full_name,'pulls/892')).head.sha='e'.repeat(40);
  errors(await auditNativeProvider(f.m,f.read),'REFRESH_REQUIRED');
});
test('same commit but wrong GitHub stable repository ID -> fail',async()=>{
  const f=makeNativeFixture();
  f.got.get(key(f.m.repositories.destination.full_name,'')).id=f.m.repositories.historical.repository_id;
  errors(await auditNativeProvider(f.m,f.read),'REPOSITORY_ID_MISMATCH');
});
test('old issue masquerades as PR in issues endpoint -> fail',async()=>{
  const f=makeNativeFixture();
  f.got.get(key(f.m.repositories.historical.full_name,'issues/787')).pull_request={url:'bogus'};
  errors(await auditNativeProvider(f.m,f.read),'ORIGIN_OBJECT_MISMATCH');
});
test('wrong destination PR repo or issue kind -> fail',async()=>{
  const f=makeNativeFixture();
  f.got.get(key(f.m.repositories.destination.full_name,'pulls/2')).head.repo.full_name='reallaksh19/Common';
  errors(await auditNativeProvider(f.m,f.read),'DESTINATION_OBJECT_MISMATCH');
  const w=makeNativeFixture();
  w.got.get(key(w.m.repositories.destination.full_name,'issues/1')).pull_request={};
  errors(await auditNativeProvider(w.m,w.read),'DESTINATION_OBJECT_MISMATCH');
});
test('wrong historical URL and duplicated object number -> fail closed',async()=>{
  const f=makeNativeFixture();
  f.got.get(key(f.m.repositories.historical.full_name,'pulls/891')).html_url='https://github.com/reallakshman19/Common/pull/891';
  errors(await auditNativeProvider(f.m,f.read),'ORIGIN_OBJECT_MISMATCH');
});
test('diverged or wrong ahead count not accepted as copied source',async()=>{
  const f=makeNativeFixture(),b=f.m.branches.find(x=>x.origin_pr===893);
  f.got.get(key(f.m.repositories.destination.full_name,'compare/'+b.origin_head_sha+'...'+b.destination_head_sha)).behind_by=1;
  errors(await auditNativeProvider(f.m,f.read),'ANCESTRY_OR_AHEAD_MISMATCH');
  const w=makeNativeFixture(),c=w.m.branches.find(x=>x.origin_pr===893);
  w.got.get(key(w.m.repositories.destination.full_name,'compare/'+c.origin_head_sha+'...'+c.destination_head_sha)).ahead_by+=1;
  errors(await auditNativeProvider(w.m,w.read),'ANCESTRY_OR_AHEAD_MISMATCH');
});
test('missing/403/paginated read is UNKNOWN, never acceptance',async()=>{
  const f=makeNativeFixture();
  f.got.delete(key(f.m.repositories.destination.full_name,'pulls/3'));
  errors(await auditNativeProvider(f.m,f.read),'PROVIDER_READ_FAILED');
  const w=makeNativeFixture();
  errors(await auditNativeProvider(w.m,async()=>{throw new Error('HTTP 403 RATE_LIMIT');}),'PROVIDER_READ_FAILED');
});
test('legacy structural validator still rejects escalated source state',async()=>{
  const f=makeNativeFixture();
  f.m.trust_gates.accepted_programme_acs=8;
  errors(await auditNativeProvider(f.m,f.read),'BAD_REFERENCE_MANIFEST');
});
test('native transport never follows foreign URL, redirects or wrong API response',async()=>{
  await assert.rejects(
    nativeGithubGet('evil/Other','issues/1',{fetchImpl:async()=>{throw Error('CALLED');}}),
    /PROVIDER_URL_NOT_ALLOWLISTED/);
  await assert.rejects(
    nativeGithubGet('reallakshman19/Common','issues/../../evil',{fetchImpl:async()=>{throw Error('CALLED');}}),
    /PROVIDER_URL_NOT_ALLOWLISTED/);
  await assert.rejects(nativeGithubGet('reallaksh19/Common','issues/787',{
    fetchImpl:async url=>({status:302,redirected:true,url,text:async()=>'{ }'})
  }),/GITHUB_GET_UNVERIFIED/);
  await assert.rejects(nativeGithubGet('reallaksh19/Common','issues/787',{
    fetchImpl:async url=>({status:200,redirected:false,url:'https://example.com/',text:async()=>'{ }'})
  }),/GITHUB_GET_UNVERIFIED/);
});

test('caller-injected valid GET shape cannot mint native-acquisition authority',async()=>{
  const f=makeNativeFixture();
  const out=await auditNativeProvider(f.m,f.read);
  assert.equal(out.current,true);
  assert.notEqual(out.provider_identity,'NATIVE_GET_VERIFIED_AT_OBSERVATION');
  assert.equal(out.owner_authenticated,false);
  assert.equal(out.reviewed,false);
  assert.equal(out.evidence_accepted,false);
});
