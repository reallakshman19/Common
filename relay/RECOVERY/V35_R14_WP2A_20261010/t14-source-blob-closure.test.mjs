import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {ORIGINAL_FILES,inspectInjectedSourceBlobs} from './t14-source-blob-closure.mjs';
const H='087cf43193febffc31375e71359e767489d3ae68',B='4f4dfa0497169d51ab86fbc27db1598121c6f25e';
const R='reallakshman19/Common',ID=1412133785;
// The original PR308 objects are not reachable from shallow CI checkouts.
// These historical test bytes were independently fetched at immutable H;
// they are NEVER a current native provider read or accepted Owner evidence.
const source=JSON.parse(readFileSync(new URL('./t14-pr308-original-blob-bytes.fixture.json',import.meta.url),'utf8'));
assert.equal(source.source_commit,H);
assert.equal(source.schema,'v35-t14-immutable-original-pr308-byte-fixture-v1');
assert.equal(source.authority,'HISTORICAL_TEST_BYTES_ONLY_NOT_NATIVE_OR_OWNER_EVIDENCE');
assert.equal(source.files.length,ORIGINAL_FILES.length);
const byPath=new Map(source.files.map(f=>[f.path,f]));
assert.equal(byPath.size,ORIGINAL_FILES.length,'Historical source paths must be unique');
const sha=b=>createHash('sha1').update(Buffer.concat([Buffer.from('blob '+b.length+'\0'),b])).digest('hex');
function fixtures(){
 const a={'':{id:ID,full_name:R},
  'pulls/308':{number:308,state:'open',head:{sha:H,repo:{id:ID}},base:{sha:B,repo:{id:ID}}}};
 for(const [p,h] of ORIGINAL_FILES){
  const original=byPath.get(p);
  assert.ok(original,'Missing immutable original PR308 fixture: '+p);
  assert.equal(original.sha,h,'Original source metadata must retain PR308 SHA: '+p);
  assert.match(original.bytes_base64,/^[A-Za-z0-9+/]+={0,2}$/);
  const data=Buffer.from(original.bytes_base64,'base64');
  assert.equal(sha(data),h,'Original blob path and content must be exactly pinned: '+p);
  a['contents/'+p+'?ref='+H]={type:'file',path:p,sha:h,encoding:'base64',content:data.toString('base64')};
 }
 return a;
}
function reader(db,hook=()=>{}){
 let n=0;return {read:async path=>{
  hook(++n,path,db);
  if(!Object.hasOwn(db,path))throw Error('SECRET_TOKEN_NEVER_LEAK');
  return structuredClone(db[path]);
 },calls:()=>n};
}
function noAdmission(v){
 assert.equal(v.admission,'NOT_ADMITTED');assert.equal(v.evidence_admitted,false);
 assert.equal(v.owner_authenticated,false);assert.equal(v.independent_successor_qualified,false);
 assert.equal(v.delp_invoked,false);assert.equal(v.programme_progress,null);
 assert.equal(v.writer_authorized,false);assert.equal(v.publisher_authorized,false);
 assert.equal(v.observation_grade,'CALLER_INJECTED_UNATTESTED');
 assert.ok(!JSON.stringify(v).includes('SECRET_TOKEN_NEVER_LEAK'));
}
test('T14 original eight physical source blobs proven in two rounds, only read-only',async()=>{
 const f=fixtures(),r=reader(f),v=await inspectInjectedSourceBlobs(r.read);
 assert.equal(v.status,'SOURCE_BLOBS_CURRENT_READ_ONLY_HOLD');
 assert.equal(v.verified_blob_count,16);assert.equal(v.provider_pass_count,2);
 assert.equal(v.original_files.length,8);assert.equal(r.calls(),22);noAdmission(v);
});
test('T14 wrong original source byte under unchanged Git metadata refuses',async()=>{
 const db=fixtures(),path='contents/'+ORIGINAL_FILES[0][0]+'?ref='+H;
 db[path].content=Buffer.from('forged source').toString('base64');
 const v=await inspectInjectedSourceBlobs(reader(db).read);
 assert.equal(v.reason,'BLOB_BYTES_MISMATCH');noAdmission(v);
});
test('T14 changed actual blob SHA under earlier source manifest refuses',async()=>{
 const db=fixtures(),path='contents/'+ORIGINAL_FILES[7][0]+'?ref='+H;
 db[path].sha='a'.repeat(40);
 const v=await inspectInjectedSourceBlobs(reader(db).read);
 assert.equal(v.reason,'BLOB_METADATA_MISMATCH');noAdmission(v);
});
test('T14 actual PR308 moving after first read prevents old facts admission',async()=>{
 const db=fixtures(),r=reader(db,(n,route,data)=>{
  if(n===12)data['pulls/308'].head.sha='a'.repeat(40);
 });
 const v=await inspectInjectedSourceBlobs(r.read);
 assert.equal(v.status,'HOLD_SOURCE_BLOBS');assert.equal(v.reason,'PR308_NOT_CURRENT');noAdmission(v);
});
test('T14 PR moves at late GET within first pass',async()=>{
 const db=fixtures(),r=reader(db,(n,p,x)=>{
  if(n===11)x['pulls/308'].head.sha='a'.repeat(40);
 });
 const v=await inspectInjectedSourceBlobs(r.read);
 assert.equal(v.reason,'PR_MOVED_DURING_READ');noAdmission(v);
});
test('T14 old repository identity denies all source facts',async()=>{
 const db=fixtures();db[''].id=1207996454;
 const v=await inspectInjectedSourceBlobs(reader(db).read);
 assert.equal(v.reason,'PR308_NOT_CURRENT');noAdmission(v);
});
test('T14 provider failure cannot leak secrets or mint native grade',async()=>{
 const db=fixtures();const r=reader(db,(n)=>{if(n===5)throw Error('SECRET_TOKEN_NEVER_LEAK')});
 const v=await inspectInjectedSourceBlobs(r.read);
 assert.equal(v.reason,'NATIVE_GET_UNKNOWN');noAdmission(v);
});
