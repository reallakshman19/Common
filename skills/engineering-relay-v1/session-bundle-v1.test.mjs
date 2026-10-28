import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {initJournal,appendJournal} from './session-journal-v1.mjs';
import {canonicalJSON} from './provenance-v1.mjs';
import {exportPortableJournal as exported,verifyPortableJournal as verify,BundleError} from './session-bundle-v1.mjs';

const ROOT='reallaksh19/Common',PARENT=ROOT+'#787',SOURCE='284a9f24fd88cd3caaf2a65a056adae5f13851c2';
const Z='0'.repeat(64);
const H=s=>createHash('sha256').update(s,'utf8').digest('hex');
const config=()=>({repository:ROOT,parent_issue:PARENT,source_sha:SOURCE,exported_at:'2026-10-08T17:00:00Z'});
const policy=(approvals=[])=>({schema:'relay-export-policy-v1',revision:'PRIVACY-V1',approved_public:approvals});
const expected=(b)=>({repository:ROOT,parent_issue:PARENT,source_sha:SOURCE,bundle_sha256:b.sha256,tip_sha256:b.manifest.tip.sha256});
let sequence=0;
const make=(kind,body,{visibility='PUBLIC',...extra}={})=>{
 const n=++sequence;
 return {
   event_id:'EV-'+n,session_id:'S1',responsibility_id:'R2-A',agent_id:'CODEX',
   base_sha:SOURCE,kind,recorded_at:new Date(Date.UTC(2026,9,8,17,0,n)).toISOString().replace('.000Z','Z'),
   source:{kind:'CHAT',status:'UNKNOWN',locator:null,sha256:null},
   content:{visibility,text:visibility==='PUBLIC'?body:null,sha256:H(body)},
   changed_files:[],commit_sha:null,evidence_id:null,prior_evidence_id:null,
   ...extra
 };
};
async function fixture(){
 const dir=await mkdtemp(join(tmpdir(),'relay-export-fixture-'));
 let tip=(await initJournal(dir)).tip;
 const records=[
  make('OWNER_PROMPT','Original Owner: preserve all real session steps'),
  make('AGENT_RESPONSE','Agent explicitly promises to implement source export'),
  make('TASK_EVIDENCE_START','START claimed by producer',{evidence_id:'E-START'}),
  make('CODE_CHANGE','updated module',{changed_files:['skills/engineering-relay-v1/session-bundle-v1.mjs']}),
  make('DEVIATION','Agent suggested unauthorized merger; rejected'),
  make('ERROR','private provider token: NEVER STORE THIS TEXT',{visibility:'REDACTED'}),
  make('TASK_EVIDENCE_END','END evidence remains untrusted',{
   evidence_id:'E-END',prior_evidence_id:'E-START',commit_sha:SOURCE,
   changed_files:['skills/engineering-relay-v1/session-bundle-v1.mjs']
  })
 ];
 for(const e of records)tip=(await appendJournal(dir,e,tip)).tip;
 const approved=records.filter(x=>x.content.visibility==='PUBLIC').map(x=>({
   event_id:x.event_id,content_sha256:x.content.sha256
 }));
 return {dir,records,tip,approved};
}
const capture=f=>exported(f.dir,config(),policy(f.approved));
const refused=async(p,code)=>assert.rejects(p,e=>e instanceof BundleError&&e.code===code);
const alternate=b=>JSON.parse(b.bytes);
const repr=x=>canonicalJSON(x);
test('real R2-A disk export and cold import preserve prompt, response, code and evidence',async()=>{
 const f=await fixture(),b=await capture(f);
 const v=await verify(b.bytes,expected(b));
 assert.equal(v.event_count,7);
 assert.equal(v.tip.sha256,f.tip.sha256);
 assert.equal(v.events[0].content.text,'Original Owner: preserve all real session steps');
 assert.equal(v.events[1].kind,'AGENT_RESPONSE');
 assert.equal(v.events[4].kind,'DEVIATION');
 assert.equal(v.events[6].prior_evidence_id,'E-START');
 assert.equal(v.events[6].commit_sha,SOURCE);
 assert.equal(v.events[0].source.status,'UNKNOWN');
 assert.equal(v.events[5].content.text,null);
 assert.equal(b.bytes.includes('private provider token'),false);
 assert.equal(v.authorization_granted,false);
 assert.equal(v.externally_anchored,false);
 assert.equal(v.independently_accepted,false);
 assert.equal(v.live_writer_enabled,false);
});
test('separate clean Node process can cold verify exact exported bundle and source identity',async()=>{
 const f=await fixture(),b=await capture(f);
 const root=await mkdtemp(join(tmpdir(),'relay-export-crossprocess-'));
 const filename=join(root,'bundle.json');
 await writeFile(filename,b.bytes,{mode:0o600,flag:'wx'});
 const moduleUrl=new URL('./session-bundle-v1.mjs',import.meta.url).href;
 const code='import {verifyPortableJournal} from '+JSON.stringify(moduleUrl)+';'+
   'import {readFile} from "node:fs/promises";'+
   'const result=await verifyPortableJournal(await readFile(process.argv[1],"utf8"),JSON.parse(process.argv[2]));'+
   'console.log(JSON.stringify({count:result.event_count,tip:result.tip.sha256,'+
   'owner:result.events[0].content.text,auth:result.authorization_granted}));';
 const child=spawnSync(process.execPath,['--input-type=module','-e',code,filename,JSON.stringify(expected(b))],
    {encoding:'utf8',timeout:10000});
 assert.equal(child.status,0,child.stderr);
 const parsed=JSON.parse(child.stdout.trim());
 assert.equal(parsed.count,7);
 assert.equal(parsed.tip,f.tip.sha256);
 assert.equal(parsed.owner,f.records[0].content.text);
 assert.equal(parsed.auth,false);
});
test('byte-identical re-export generates exact same portable digest',async()=>{
 const f=await fixture();
 const a=await capture(f),b=await capture(f);
 assert.equal(a.bytes,b.bytes);assert.equal(a.sha256,b.sha256);
 assert.match(a.sha256,/^[a-f0-9]{64}$/);
 assert.equal(a.manifest.policy_revision,'PRIVACY-V1');
});
test('default deny rejects exporting Owner prompt without its exact privacy approval',async()=>{
 const f=await fixture();
 await refused(exported(f.dir,config(),policy([])),'PRIVACY_DENIED');
 await refused(exported(f.dir,config(),policy(f.approved.slice(1))),'PRIVACY_DENIED');
});
test('privacy approval is bound to exact content SHA, not mere event ID',async()=>{
 const f=await fixture();
 const approvals=f.approved.map(x=>({...x}));
 approvals[0].content_sha256='a'.repeat(64);
 await refused(exported(f.dir,config(),policy(approvals)),'PRIVACY_DENIED');
});
test('unused approval and duplicate approvals cannot leak unrelated text',async()=>{
 const f=await fixture();
 const q=[...f.approved,{event_id:'EV-999',content_sha256:'a'.repeat(64)}];
 await refused(exported(f.dir,config(),policy(q)),'PRIVACY_DENIED');
 await refused(exported(f.dir,config(),policy([...f.approved,f.approved[0]])),'INVALID');
});
test('redacted private text cannot be reconstructed by exporter or consumer',async()=>{
 const f=await fixture(),b=await capture(f);
 assert.equal(b.bytes.includes('NEVER STORE THIS TEXT'),false);
 const o=await verify(b.bytes,expected(b));
 assert.equal(o.events[5].content.visibility,'REDACTED');
 assert.equal(o.events[5].content.text,null);
 assert.equal(o.original_chat_source,'UNKNOWN');
 assert.equal(o.owner_message_authenticated,false);
});
test('one-byte tampering fails independently pinned bundle checksum',async()=>{
 const f=await fixture(),b=await capture(f);
 const changed=b.bytes.replace('preserve all real session steps','erase history');
 await refused(verify(changed,expected(b)),'REFUTED');
});
test('missing middle record and renamed entry are detected by real R2 replay',async()=>{
 const f=await fixture(),b=await capture(f),v=alternate(b);
 const missing=v.entries.splice(2,1)[0];
 v.manifest.event_count-=1;v.manifest.tip.seq-=1;
 if(missing.record.content.visibility==='PUBLIC')v.manifest.public_count-=1;
 else v.manifest.redacted_count-=1;
 // The supplied digest alone is not independently authenticated; still R2-A detects gap.
 const changed=repr(v),fake={...expected(b),bundle_sha256:H(changed)};
 await refused(verify(changed,fake),'CORRUPT');
});
test('duplicated event ID and changed session actor rejected through R2-A cold replay',async()=>{
 const f=await fixture(),b=await capture(f),v=alternate(b);
 v.entries[1].record.event_id=v.entries[0].record.event_id;
 let changed=repr(v);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'CORRUPT');
 const w=alternate(b);w.entries[1].record.agent_id='ANOTHER-AGENT';
 changed=repr(w);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'CORRUPT');
});
test('forged accepted:true is refused even if caller changes external checksum',async()=>{
 const f=await fixture(),b=await capture(f),v=alternate(b);
 v.entries[0].record.accepted=true;
 const changed=repr(v);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'CORRUPT');
});
test('repository, parent or source commit transplant rejected',async()=>{
 const f=await fixture(),b=await capture(f);
 await refused(verify(b.bytes,{...expected(b),repository:'attacker/Common',parent_issue:'attacker/Common#787'}),'REFUTED');
 await refused(verify(b.bytes,{...expected(b),parent_issue:ROOT+'#999'}),'REFUTED');
 await refused(verify(b.bytes,{...expected(b),source_sha:'a'.repeat(40)}),'REFUTED');
});
test('wrong pinned journal tip refused, even with exact bundle bytes',async()=>{
 const f=await fixture(),b=await capture(f);
 await refused(verify(b.bytes,{...expected(b),tip_sha256:'a'.repeat(64)}),'REFUTED');
});
test('bundle self-downgrade claimed AUTHENTICATED cannot pass',async()=>{
 const f=await fixture(),b=await capture(f),v=alternate(b);
 v.manifest.authority_status='OWNER_AUTHENTICATED';
 const changed=repr(v);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'REFUTED');
});
test('privacy consent tampering and revision change detected against manifest digest',async()=>{
 const f=await fixture(),b=await capture(f),v=alternate(b);
 v.privacy_policy.revision='PRIVACY-V2';
 let changed=repr(v);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'REFUTED');
 const w=alternate(b);w.privacy_policy.approved_public=[];
 changed=repr(w);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'REFUTED');
});
test('unapproved PUBLIC event from altered payload refused at import',async()=>{
 const f=await fixture(),b=await capture(f),v=alternate(b);
 v.privacy_policy.approved_public=v.privacy_policy.approved_public.filter(x=>x.event_id!==f.records[0].event_id);
 v.manifest.policy_sha256=H(repr(v.privacy_policy));
 const changed=repr(v);
 await refused(verify(changed,{...expected(b),bundle_sha256:H(changed)}),'PRIVACY_DENIED');
});
test('export refuses crash debris until manually reviewed',async()=>{
 const f=await fixture();
 await writeFile(join(f.dir,'.pending-00000000-0000-4000-8000-000000000000'),'half write');
 await refused(capture(f),'UNRESOLVED');
});
test('source journal symlink cannot be used to smuggle a different root',async()=>{
 const f=await fixture(),other=await mkdtemp(join(tmpdir(),'relay-portable-link-'));
 const alias=join(other,'alias');
 await symlink(f.dir,alias,process.platform==='win32'?'junction':'dir');
 await refused(exported(alias,config(),policy(f.approved)),'INVALID');
});
test('canonical JSON and size limits are enforced before allocation/import',async()=>{
 const f=await fixture(),b=await capture(f);
 await refused(verify(' '+b.bytes,expected(b)),'INVALID');
 await refused(verify('X'.repeat(4194305),expected(b)),'LIMIT');
});
test('no records and invalid policy revision are not accepted as a portable session',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'relay-bundle-empty-'));
 await initJournal(dir);
 await refused(exported(dir,config(),policy([])),'EMPTY');
 const f=await fixture();
 await refused(exported(f.dir,config(),{...policy(f.approved),revision:'invalid revision spaces'}),'INVALID');
});
test('foreign original chat status or unapproved privacy policy cannot create human Owner trust',async()=>{
 const f=await fixture(),b=await capture(f);
 const v=await verify(b.bytes,expected(b));
 assert.equal(v.owner_message_authenticated,false);
 assert.equal(v.externally_anchored,false);
 assert.equal(v.source_attribution,'PRODUCER_ASSERTED_UNVERIFIED');
 assert.equal(v.live_writer_enabled,false);
});
