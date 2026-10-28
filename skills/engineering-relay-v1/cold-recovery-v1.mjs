/* RELAY RESET R8: link-only cold PROCESS synthetic recovery, never Owner authority.
 * No issue writes, no private session corpus, no independent-agent impersonation.
 */
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {rehearseNativeFullChain} from './full-chain-rehearsal-v1.mjs';
import {canonicalJSON} from './provenance-v1.mjs';

export class ColdRecoveryError extends Error {
  constructor(code,message){super(code+': '+message);this.name='ColdRecoveryError';this.code=code;}
}
const fail=(code,why)=>{throw new ColdRecoveryError(code,why);};
const HEX=/^[0-9a-f]{64}$/,SHA=/^[0-9a-f]{40}$/;
const REPO=/^[A-Za-z0-9-]{1,39}\/[A-Za-z0-9_.-]{1,100}$/;
const MANIFEST_PATH='skills/engineering-relay-v1/fixtures/cold-synthetic-recovery-manifest-v1.json';
const LIMIT=32768;
const digest=b=>createHash('sha256').update(b).digest('hex');
const gitBlob=b=>createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');
function exact(v,keys,where){
  if(!v||typeof v!=='object'||Array.isArray(v)||
    Object.keys(v).some(k=>!keys.includes(k))||
    keys.some(k=>!Object.hasOwn(v,k)))
    fail('INVALID',where+' unexpected or missing keys');
}
function canonicalSafe(v){
  try{return JSON.parse(canonicalJSON(v));}
  catch{fail('INVALID','manifest unsafe canonical JSON');}
}
function pin(raw){
  exact(raw,['manifest_url','manifest_sha256','pr_url','expected_head_sha'],'cold pin');
  if(!HEX.test(raw.manifest_sha256)||!SHA.test(raw.expected_head_sha))
    fail('INVALID','expected SHA256 and PR HEAD required');
  const m=typeof raw.manifest_url==='string'&&
    /^https:\/\/github\.com\/([^/?#]+\/[^/?#]+)\/blob\/([0-9a-f]{40})\/(.+)$/.exec(raw.manifest_url);
  const p=typeof raw.pr_url==='string'&&
    /^https:\/\/github\.com\/([^/?#]+\/[^/?#]+)\/pull\/([1-9][0-9]*)$/.exec(raw.pr_url);
  if(!m||!p||!REPO.test(m[1])||!REPO.test(p[1])||
    m[1]!==p[1]||m[2]!==raw.expected_head_sha||m[3]!==MANIFEST_PATH||
    !Number.isSafeInteger(Number(p[2])))
    fail('SCOPE_MISMATCH','immutable manifest permalink and PR pin do not agree');
  return {repo:m[1],commit:m[2],pr:Number(p[2]),path:m[3],
    ...raw};
}
function manifestCore(bytes,expected,repo){
  if(!Buffer.isBuffer(bytes)||bytes.length<1||bytes.length>LIMIT||
    digest(bytes)!==expected)
    fail('DIGEST_MISMATCH','pinned cold manifest bytes not equal expected SHA256');
  let manifest;
  try{manifest=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}
  catch{fail('INVALID','non-JSON or invalid UTF8 manifest');}
  const m=canonicalSafe(manifest);
  exact(m,['schema','repository','parent_issue','trust','source_template',
    'provider_scope_template','owner_seed','bindings',
    'authorization_granted','independently_accepted','live_writer_enabled'],'manifest');
  if(m.schema!=='relay-cold-synthetic-manifest-v1'||
    m.repository!==repo||!REPO.test(repo)||!Number.isSafeInteger(m.parent_issue)||
    m.parent_issue<1||m.trust!=='SYNTHETIC_PRODUCER_ASSERTED_NOT_OWNER_AUTHENTICATED'||
    m.authorization_granted!==false||m.independently_accepted!==false||
    m.live_writer_enabled!==false)
    fail('UNTRUSTED','manifest does not meet producer-only synthetic scope');
  exact(m.source_template,
    ['path','source_sha','bundle_sha256','tip_sha256'],'source template');
  if(m.source_template.path!=='skills/engineering-relay-v1/fixtures/b2a-synthetic-journal-v1.json'||
    !SHA.test(m.source_template.source_sha)||
    !HEX.test(m.source_template.bundle_sha256)||
    !HEX.test(m.source_template.tip_sha256))
    fail('UNTRUSTED','source path and expected hashes invalid');
  exact(m.provider_scope_template,['child_issues','workflow_paths'],'provider template');
  if(!Array.isArray(m.provider_scope_template.child_issues)||
    m.provider_scope_template.child_issues.length!==1||
    m.provider_scope_template.child_issues.some(n=>!Number.isSafeInteger(n)||n<1||n===m.parent_issue)||
    !Array.isArray(m.provider_scope_template.workflow_paths)||
    m.provider_scope_template.workflow_paths.length!==1||
    m.provider_scope_template.workflow_paths[0]!=='.github/workflows/relay-reset-cold-process.yml')
    fail('UNTRUSTED','provider paths and child scope not bounded to R8');
  exact(m.owner_seed,['schema','parent_issue','owner_intents','claims',
    'responsibilities','sessions','task_evidence','research_findings','owner_decisions'],'synthetic R1 seed');
  // A recomputed SHA is not an authenticated Owner grant. Strictly pin
  // nested source assertions so forged decisions or alternate origins cannot
  // arrive through this public synthetic-only recovery channel.
  const seed=m.owner_seed,intent=seed.owner_intents?.[0],
    claim=seed.claims?.[0],work=seed.responsibilities?.[0];
  if(seed.parent_issue!==repo+'#'+m.parent_issue||
    seed.schema!=='relay-provenance-v1'||
    !Array.isArray(seed.owner_intents)||seed.owner_intents.length!==1||
    !Array.isArray(seed.claims)||seed.claims.length!==1||
    !Array.isArray(seed.responsibilities)||seed.responsibilities.length!==1||
    !Array.isArray(seed.sessions)||seed.sessions.length!==0||
    !Array.isArray(seed.task_evidence)||seed.task_evidence.length!==0||
    !Array.isArray(seed.research_findings)||seed.research_findings.length!==0||
    !Array.isArray(seed.owner_decisions)||seed.owner_decisions.length!==0||
    !Array.isArray(m.bindings)||m.bindings.length!==1)
    fail('UNTRUSTED','synthetic graph cannot contain live decisions or source facts');
  exact(intent,['id','raw_text','original_source','first_durable_mirror'],'synthetic OwnerIntent');
  exact(intent.original_source,['kind','status','locator'],'synthetic origin');
  exact(claim,['id','intent_ids','criterion'],'synthetic claim');
  exact(work,['id','claim_ids','depends_on','scope','write_surface'],'synthetic work');
  exact(m.bindings[0],['event_id','intent_id'],'synthetic binding');
  if(intent.id!=='OI-1'||
    intent.raw_text!=='SYNTHETIC OWNER REQUEST: verify immutable GitHub content; not a real chat'||
    intent.original_source.kind!=='CHAT'||
    intent.original_source.status!=='UNKNOWN'||
    intent.original_source.locator!==null||
    intent.first_durable_mirror!=='https://github.com/'+repo+'/issues/'+m.parent_issue||
    claim.id!=='AC3'||claim.criterion!=='SYNTHETIC intent to module evidence trace'||
    !Array.isArray(claim.intent_ids)||claim.intent_ids.length!==1||claim.intent_ids[0]!=='OI-1'||
    work.id!=='R2-B2A'||work.scope!=='Synthetic native custody and trace'||
    !Array.isArray(work.claim_ids)||work.claim_ids.length!==1||work.claim_ids[0]!=='AC3'||
    !Array.isArray(work.depends_on)||work.depends_on.length!==0||
    !Array.isArray(work.write_surface)||work.write_surface.length!==1||
    work.write_surface[0]!=='skills/engineering-relay-v1/github-journal-lineage-v1.mjs'||
    m.bindings[0].event_id!=='EV-1'||m.bindings[0].intent_id!=='OI-1'||
    m.source_template.source_sha!=='28841b5cfed9e9b6057a1a6f09090adcc512e1b8'||
    m.source_template.bundle_sha256!=='79c2bc0b84f23a862e3ce7cef300c1b2dd1c4b90d00a448a8f1a269d1ddb0e9d'||
    m.source_template.tip_sha256!=='3077376e2d5fe849de1450d9f2cc8e6d350742dc0d98969a36e778000d052660')
    fail('UNTRUSTED','manifest changed synthetic provenance or expected immutable bytes');
  return m;
}
async function boundedResponse(res,url){
  if(!res||res.status!==200||res.url!==url||res.redirected===true)
    fail('UNKNOWN','GitHub immutable manifest read unavailable');
  const declared=res.headers?.get?.('content-length');
  if(declared!==null&&declared!==undefined&&declared!==''){
    const n=Number(declared);
    if(!Number.isSafeInteger(n)||n<0||n>LIMIT*2)fail('UNKNOWN','unbounded Content-Length');
  }
  let buf;
  if(res.body?.getReader){
    const reader=res.body.getReader();const parts=[];let n=0;
    try{while(true){
      const {value,done}=await reader.read();if(done)break;
      n+=value.byteLength;if(n>LIMIT*2)fail('UNKNOWN','oversized streamed GitHub JSON');
      parts.push(Buffer.from(value));
    }}finally{reader.releaseLock();}
    buf=Buffer.concat(parts);
  } else if(typeof res.text==='function'){
    const str=await res.text();
    if(typeof str!=='string'||Buffer.byteLength(str,'utf8')>LIMIT*2)
      fail('UNKNOWN','oversized native GitHub response');
    buf=Buffer.from(str,'utf8');
  }else fail('UNKNOWN','no response body');
  try{return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(buf));}
  catch{fail('UNKNOWN','invalid GitHub manifest response JSON');}
}
function decodeContents(data,scope){
  if(!data||typeof data!=='object'||Array.isArray(data)||
    data.type!=='file'||data.path!==scope.path||
    data.name!=='cold-synthetic-recovery-manifest-v1.json'||
    data.encoding!=='base64'||typeof data.content!=='string'||
    !Number.isSafeInteger(data.size)||data.size<1||data.size>LIMIT||
    !SHA.test(data.sha))
    fail('REFUTED','GitHub content is not bounded exact manifest');
  const raw=data.content.replace(/\n/g,'');
  if(!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(raw))
    fail('REFUTED','base64 noncanonical');
  const bytes=Buffer.from(raw,'base64');
  if(bytes.length!==data.size||bytes.toString('base64')!==raw||
    gitBlob(bytes)!==data.sha)
    fail('REFUTED','Git blob SHA1 or byte count mismatch');
  return bytes;
}
/** Public validators for negative tests, no transport identity promotion. */
function deepFreeze(root){
  const seen=new Set(),stack=[root];
  while(stack.length){
    const v=stack.pop();if(!v||typeof v!=='object'||seen.has(v))continue;
    seen.add(v);
    for(const item of Object.values(v))if(item&&typeof item==='object')stack.push(item);
    Object.freeze(v);
  }
  return root;
}
export function validatePinnedManifest(rawPin,bytes){
  const p=pin(rawPin);
  const m=manifestCore(bytes,p.manifest_sha256,p.repo);
  return deepFreeze({pin:p,manifest:m,manifest_sha256:p.manifest_sha256});
}
function createSpec(p,m){
  return {
    source_spec:{repository:p.repo,parent_issue:p.repo+'#'+m.parent_issue,
      commit_sha:p.commit,path:m.source_template.path,
      source_sha:m.source_template.source_sha,
      bundle_sha256:m.source_template.bundle_sha256,tip_sha256:m.source_template.tip_sha256},
    provider_scope:{repository:p.repo,parent_issue:m.parent_issue,
      child_issues:m.provider_scope_template.child_issues,
      workflow_paths:m.provider_scope_template.workflow_paths,
      pull_requests:[{number:p.pr,expected_head_sha:p.commit}]},
    owner_seed:m.owner_seed,bindings:m.bindings
  };
}
export async function recoverFromPinnedGitHubManifest(rawPin,options={}){
  const p=pin(rawPin);
  exact(options,['readToken'],'read-only options');
  const token=options.readToken;
  if(token!==undefined&&(typeof token!=='string'||!/^[\x21-\x7e]{1,400}$/.test(token)))
    fail('INVALID','invalid read-only token format');
  const headers={Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',
    'User-Agent':'relay-cold-process-readonly'};
  if(token)headers.Authorization='Bearer '+token;
  const url='https://api.github.com/repos/'+p.repo+'/contents/'+p.path+'?ref='+p.commit;
  let response;
  try{response=await fetch(url,{method:'GET',redirect:'error',cache:'no-store',headers});}
  catch{fail('UNKNOWN','native manifest GitHub GET failed');}
  const payload=await boundedResponse(response,url);
  const bytes=decodeContents(payload,p);
  const m=manifestCore(bytes,p.manifest_sha256,p.repo);
  // All material facts are recovered in this process from pinned public URLs.
  // No test-supplied R1 seed or mutable issue/PR title is an authority.
  const actual=await rehearseNativeFullChain(createSpec(p,m),{
    sourceRead:{readToken:token},providerRead:{readToken:token},
    evaluation:{evaluated_at:new Date(Date.now()+15000).toISOString(),max_age_seconds:600}
  });
  if(actual.source_commit_sha!==p.commit||
    actual.pr_heads.length!==1||actual.pr_heads[0].number!==p.pr||
    actual.pr_heads[0].head_sha!==p.commit||
    actual.status!=='NATIVE_GITHUB_SYNTHETIC_REHEARSAL_UNANCHORED'||
    actual.live_writer_enabled!==false||actual.authorization_granted!==false)
    fail('SOURCE_DRIFT','cold process did not reconstruct matching GitHub head');
  return Object.freeze({
    schema:'relay-cold-process-proof-v1',
    recovery_mode:'FRESH_PROCESS_READ_ONLY_NOT_INDEPENDENT_AGENT',
    manifest_url:p.manifest_url,manifest_sha256:p.manifest_sha256,
    current_pr_url:p.pr_url,expected_head_sha:p.commit,
    source_lineage_sha256:actual.github_source_lineage_sha256,
    provider_snapshot_sha256:actual.provider_snapshot_sha256,
    r4_projection_sha256:actual.r4_projection_sha256,
    candidate_state_sha256:actual.candidate_state_sha256,
    trust_preflight_sha256:actual.trust_preflight_sha256,
    public_task_evidence_observation:actual.public_task_evidence_observation,
    // Optional R10 read intentionally absent in the synthetic-only R8 CLI.
    full_chain_sha256:actual.full_chain_sha256,
    event_count:actual.event_count,session_count:actual.session_count,
    original_chat_source:'UNKNOWN',source_attribution:'SYNTHETIC_PRODUCER_ASSERTED',
    externally_anchored:false,owner_message_authenticated:false,
    independently_accepted:false,authorization_granted:false,live_writer_enabled:false
  });
}
async function command(argv){
  if(argv.length!==4||argv[0]!=='--manifest-url'||argv[2]!=='--expected-manifest-sha256')
    fail('CLI_USAGE','expected immutable manifest URL and sha256');
  const manifest_url=argv[1],manifest_sha256=argv[3];
  const pr_url=process.env.RELAY_COLD_PR_URL;
  const expected_head_sha=process.env.RELAY_COLD_EXPECTED_HEAD_SHA;
  const out=await recoverFromPinnedGitHubManifest({
    manifest_url,manifest_sha256,pr_url,expected_head_sha
  },{readToken:process.env.RELAY_COLD_READ_TOKEN});
  process.stdout.write('RELAY_COLD_PROCESS_PROOF '+JSON.stringify(out)+'\n');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  command(process.argv.slice(2)).catch(e=>{
    // No source text, token or response bodies in public log errors.
    process.stderr.write('RELAY_COLD_PROCESS_REFUSED '+(e?.code??'UNKNOWN')+'\n');
    process.exitCode=1;
  });
}
