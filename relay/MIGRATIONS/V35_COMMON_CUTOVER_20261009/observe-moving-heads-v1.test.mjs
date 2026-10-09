import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {observeMovingHeads} from './observe-moving-heads-v1.mjs';

const m=JSON.parse(readFileSync(new URL('./migration-manifest-v1.json',import.meta.url),'utf8'));
const clone=x=>structuredClone(x);
const k=(r,path)=>r+'|'+path;
const href=(slug,kind,n)=>'https://github.com/'+slug+'/'+
 (kind==='PR'?'pull':'issues')+'/'+n;
function fixture(){
  const v=clone(m), origin=v.repositories.historical, dest=v.repositories.destination,
    records=new Map(),reads=new Map(), bmap=new Map(v.branches.map(b=>[b.origin_pr,b]));
  for(const r of [origin,dest]){
    records.set(k(r.full_name,''),{id:r.repository_id,full_name:r.full_name,default_branch:'main'});
    records.set(k(r.full_name,'git/ref/heads/main'),{ref:'refs/heads/main',object:{sha:r.main_sha}});
  }
  for(const o of v.objects){
    const b=bmap.get(o.origin.number);
    function item(r,link,destination){
      return {number:link.number,html_url:href(r.full_name,o.kind,link.number),state:'open',
        ...(o.kind==='PR'?{
          head:{sha:destination?b.destination_head_sha:b.origin_head_sha,
            ref:b.branch,repo:{full_name:r.full_name}},
          base:{repo:{full_name:r.full_name}}
        }:{})};
    }
    records.set(k(origin.full_name,(o.kind==='PR'?'pulls/':'issues/')+o.origin.number),
      item(origin,o.origin,false));
    if(o.destination)records.set(k(dest.full_name,
      (o.kind==='PR'?'pulls/':'issues/')+o.destination.number),
      item(dest,o.destination,true));
  }
  for(const b of v.branches){
    records.set(k(dest.full_name,'git/ref/heads/'+b.branch),
      {ref:'refs/heads/'+b.branch,object:{sha:b.destination_head_sha}});
    if(b.relation==='SOURCE_ADVANCED'){
      records.set(k(dest.full_name,
        'compare/'+b.origin_head_sha+'...'+b.destination_head_sha),
        {status:'ahead',ahead_by:b.ahead_commits,behind_by:0});
    }
  }
  const read=async(slug,path)=>{
    const name=k(slug,path),n=(reads.get(name)||0)+1;
    reads.set(name,n);
    const data=records.get(name);
    if(!data)throw Error('NATIVE GET NOT FOUND');
    return clone(data);
  };
  return {v,records,reads,read,origin,dest};
}
function move(f,oldNumber,newNumber,newSha,ahead){
  const b=f.v.branches.find(x=>x.origin_pr===oldNumber);
  const pull=f.records.get(k(f.dest.full_name,'pulls/'+newNumber));
  pull.head.sha=newSha;
  f.records.get(k(f.dest.full_name,'git/ref/heads/'+b.branch)).object.sha=newSha;
  f.records.set(k(f.dest.full_name,'compare/'+b.origin_head_sha+'...'+newSha),
    {status:'ahead',ahead_by:ahead,behind_by:0});
}
const reject=(r,fragment)=>{
  assert.equal(r.current,false,JSON.stringify(r));
  assert.ok(r.errors.some(e=>e.includes(fragment)),JSON.stringify(r));
  assert.equal(r.source_grade,'INJECTED_UNATTESTED');
  assert.equal(r.writer_authorized,false);
  assert.equal(r.reviewer_qualified,false);
  assert.equal(r.evidence_accepted,false);
  assert.equal(r.programme_acceptance,'NOT_EVALUATED');
};

test('positive: unchanged source, native GET-shaped double-read remains UNATTESTED',async()=>{
  const f=fixture(),r=await observeMovingHeads(f.v,f.read);
  assert.equal(r.current,true,JSON.stringify(r));
  assert.equal(r.source_grade,'INJECTED_UNATTESTED');
  assert.equal(r.manifest_advanced,false);
  assert.equal(r.source_vector.length,2);
  assert.equal(r.writer_authorized,false);
  assert.equal(r.owner_authenticated,false);
  assert.equal(f.reads.get(k(f.dest.full_name,'pulls/3')),2);
  assert.equal(f.reads.get(k(f.dest.full_name,'git/ref/heads/docs/relay-890-continuity-md-v1')),2);
});
test('positive: later Runner PR3 moves but original manifest is never mutated',async()=>{
  const f=fixture(),before=JSON.stringify(f.v),sha='f'.repeat(40);
  move(f,893,3,sha,99);
  const r=await observeMovingHeads(f.v,f.read);
  assert.equal(r.current,true,JSON.stringify(r));
  assert.equal(r.manifest_advanced,true);
  assert.equal(r.source_vector.find(x=>x.old_pr===893).new_head_sha,sha);
  assert.equal(JSON.stringify(f.v),before);
  assert.equal(r.writer_authorized,false);
  assert.equal(r.source_grade,'INJECTED_UNATTESTED');
});
test('negative: a second new commit between first and second PR reads fails closed',async()=>{
  const f=fixture(),first=f.read;
  f.read=async (slug,path)=>{
    const n=(f.reads.get(k(slug,path))||0);
    if(slug===f.dest.full_name&&path==='pulls/3'&&n===1){
      move(f,893,3,'f'.repeat(40),100);
    }
    return first(slug,path);
  };
  reject(await observeMovingHeads(f.v,f.read),'REFRESH_REQUIRED');
});
test('negative: branch changes between first PR and branch read',async()=>{
  const f=fixture();
  const b=f.v.branches.find(x=>x.origin_pr===893);
  f.records.get(k(f.dest.full_name,'git/ref/heads/'+b.branch)).object.sha='f'.repeat(40);
  reject(await observeMovingHeads(f.v,f.read),'MOVING_PR_OR_BRANCH_MISMATCH');
});
test('negative: fast-forward claim is actually divergence, not ancestry',async()=>{
  const f=fixture(),b=f.v.branches.find(x=>x.origin_pr===893);
  f.records.get(k(f.dest.full_name,'compare/'+b.origin_head_sha+'...'+b.destination_head_sha)).behind_by=1;
  reject(await observeMovingHeads(f.v,f.read),'MOVING_SOURCE_ANCESTRY_INVALID');
});
test('negative: wrong new PR repo ID and wrong base repo',async()=>{
  const f=fixture();f.records.get(k(f.dest.full_name,'pulls/3')).base.repo.full_name=f.origin.full_name;
  reject(await observeMovingHeads(f.v,f.read),'MOVING_PR_OR_BRANCH_MISMATCH');
});
test('negative: missing current GitHub response remains UNKNOWN',async()=>{
  const f=fixture();f.records.delete(k(f.dest.full_name,'pulls/2'));
  reject(await observeMovingHeads(f.v,f.read),'PROVIDER_READ_FAILED');
});
test('negative: bad structural provenance and forged AC cannot reach provider reader',async()=>{
  const f=fixture(); f.v.trust_gates.accepted_programme_acs=8;
  let calls=0;const result=await observeMovingHeads(f.v,async()=>{calls++;return {}});
  reject(result,'BAD_REFERENCE_MANIFEST');
  assert.equal(calls,0);
});
test('negative: old source moves between first and second reader phase',async()=>{
  const f=fixture(),orig=f.read;
  f.read=async (slug,path)=>{
    if(slug===f.origin.full_name && path==='pulls/893') {
      f.records.get(k(slug,path)).head.sha='c'.repeat(40);
    }
    return orig(slug,path);
  };
  reject(await observeMovingHeads(f.v,f.read),'REFRESH_REQUIRED');
});


test('positive: destination main advances while immutable origin and source roles are preserved',async()=>{
  const f=fixture(),before=JSON.stringify(f.v),newMain='d'.repeat(40);
  f.records.get(k(f.dest.full_name,'git/ref/heads/main')).object.sha=newMain;
  const r=await observeMovingHeads(f.v,f.read);
  assert.equal(r.current,true,JSON.stringify(r));
  assert.equal(r.destination_main_sha,newMain);
  assert.equal(r.historical_main_sha,f.origin.main_sha);
  assert.equal(r.manifest_advanced,true);
  assert.equal(r.source_grade,'INJECTED_UNATTESTED');
  assert.equal(JSON.stringify(f.v),before);
  assert.equal(f.reads.get(k(f.dest.full_name,'git/ref/heads/main')),2);
  assert.equal(r.writer_authorized,false);
});
test('negative: new default branch moves between first and second GET',async()=>{
  const f=fixture(),base=f.read;
  f.read=async(slug,path)=>{
    if(slug===f.dest.full_name && path==='git/ref/heads/main' &&
       f.reads.get(k(slug,path))===1){
      f.records.get(k(slug,path)).object.sha='d'.repeat(40);
    }
    return base(slug,path);
  };
  reject(await observeMovingHeads(f.v,f.read),'REFRESH_REQUIRED');
});
test('negative: historical default branch must not be silently refreshed',async()=>{
  const f=fixture();
  f.records.get(k(f.origin.full_name,'git/ref/heads/main')).object.sha='d'.repeat(40);
  reject(await observeMovingHeads(f.v,f.read),'STALE_MAIN_HEAD');
});
test('negative: malformed current destination main reference is rejected',async()=>{
  const f=fixture();
  f.records.get(k(f.dest.full_name,'git/ref/heads/main')).ref='refs/heads/other';
  reject(await observeMovingHeads(f.v,f.read),'MOVING_MAIN_REF_INVALID');
});
