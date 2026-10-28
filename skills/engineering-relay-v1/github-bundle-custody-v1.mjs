/* RELAY RESET #825 / R2-B2a — exact GitHub committed bundle readback ONLY.
 * Native GitHub Contents GET pins repo/path/full commit SHA, verifies Git blob SHA1,
 * and passes byte-identical contents to actual merged R2-B1 cold journal replay.
 * GitHub content integrity != human Owner authorization or accepted TaskEvidence.
 */
import {createHash} from 'node:crypto';
import {verifyPortableJournal} from './session-bundle-v1.mjs';
import {canonicalJSON} from './provenance-v1.mjs';

export class CustodyError extends Error {
  constructor(code,message){super(code+': '+message);this.name='CustodyError';this.code=code;}
}
const SHA=/^[0-9a-f]{40}$/,HASH=/^[0-9a-f]{64}$/;
const REPO=/^([A-Za-z0-9-]{1,39})\/([A-Za-z0-9_.-]{1,100})$/;
const MAX_BUNDLE=4*1024*1024,MAX_RESPONSE=6*1024*1024;
const fail=(code,message)=>{throw new CustodyError(code,message);};
function fields(v,names,where) {
  if(!v||typeof v!=='object'||Array.isArray(v)||
    names.some(n=>!Object.hasOwn(v,n))||
    Object.keys(v).some(n=>!names.includes(n)))fail('INVALID',where+' unexpected or missing keys');
}
function sha256(x){return createHash('sha256').update(x).digest('hex');}
function gitBlobSHA(buf){
  return createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');
}
function checked(spec) {
  fields(spec,['repository','parent_issue','commit_sha','path','source_sha','bundle_sha256','tip_sha256'],'source specification');
  const m=typeof spec.repository==='string'&&REPO.exec(spec.repository);
  const parent=typeof spec.parent_issue==='string'&&/^([A-Za-z0-9-]+\/[A-Za-z0-9_.-]+)#[1-9][0-9]*$/.exec(spec.parent_issue);
  if(!m||m[2]==='.'||m[2]==='..'||!SHA.test(spec.commit_sha)||
    !SHA.test(spec.source_sha)||!HASH.test(spec.bundle_sha256)||!HASH.test(spec.tip_sha256)||
    !parent||parent[1].toLowerCase()!==spec.repository.toLowerCase()||
    typeof spec.path!=='string'||spec.path.length>240||
    !/^[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*$/.test(spec.path)||
    spec.path.split('/').some(x=>x==='.'||x==='..'||x==='')||
    !/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(m[1]))
    fail('INVALID','invalid pinned repository/parent/commit/path/digest');
  const api='https://api.github.com/repos/'+spec.repository+'/contents/'+spec.path+
    '?ref='+spec.commit_sha;
  const html='https://github.com/'+spec.repository+'/blob/'+spec.commit_sha+'/'+spec.path;
  return {api,html,name:spec.path.split('/').at(-1)};
}
async function boundedJSON(res,url) {
  if(!res||res.status!==200)fail('UNKNOWN','GitHub unavailable or file not found');
  if(res.redirected===true||res.url!==url)fail('UNKNOWN','redirect or response URL differs');
  const rawLength=res.headers?.get?.('content-length');
  if(rawLength!==null&&rawLength!==undefined&&rawLength!=='') {
    const n=Number(rawLength);
    if(Number.isFinite(n)&&n>MAX_RESPONSE)fail('UNKNOWN','GitHub response exceeds read limit');
  }
  let bytes;
  if(res.body?.getReader) {
    const reader=res.body.getReader(),parts=[];
    let n=0;
    try{while(true){const {value,done}=await reader.read();if(done)break;
      n+=value.byteLength;
      if(n>MAX_RESPONSE)fail('UNKNOWN','GitHub response exceeded stream limit');
      parts.push(Buffer.from(value));
    }}finally{reader.releaseLock();}
    bytes=Buffer.concat(parts);
  } else if(typeof res.text==='function') {
    const text=await res.text();
    if(typeof text!=='string'||Buffer.byteLength(text,'utf8')>MAX_RESPONSE)
      fail('UNKNOWN','response text exceeds limit');
    bytes=Buffer.from(text,'utf8');
  } else fail('UNKNOWN','missing GitHub response body');
  let json;
  try{json=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}
  catch{fail('UNKNOWN','invalid provider JSON/UTF8');}
  if(!json||typeof json!=='object'||Array.isArray(json))fail('REFUTED','provider payload is not a file object');
  return json;
}
function decodedBlob(p,spec,bound) {
  if(p.type!=='file'||p.path!==spec.path||p.name!==bound.name||
    typeof p.sha!=='string'||!SHA.test(p.sha)||
    p.encoding!=='base64'||typeof p.content!=='string'||
    !Number.isSafeInteger(p.size)||p.size<1||p.size>MAX_BUNDLE)
    fail('REFUTED','provider path/size/type/encoding/SHA claim invalid');
  const b64=p.content.replace(/\n/g,'');
  if(!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(b64))
    fail('REFUTED','noncanonical base64 in native blob content');
  const data=Buffer.from(b64,'base64');
  if(data.length!==p.size||data.toString('base64')!==b64||
    data.length>MAX_BUNDLE||gitBlobSHA(data)!==p.sha)
    fail('REFUTED','provider Git blob SHA1 or decoded byte count mismatch');
  if(sha256(data)!==spec.bundle_sha256)
    fail('REFUTED','native GitHub content differs from independently expected SHA256');
  return data;
}

/**
 * Input is an independently supplied immutable GitHub commit, exact path,
 * independent SHA256 and journal tip. Never accepts a branch/moving ref.
 * Injected transport proves parsing only; native default fetch proves present
 * committed provider bytes, NOT human authorship or an independent trust root.
 */
async function readInternal(rawSpec,options={}) {
  let spec;
  try{spec=JSON.parse(canonicalJSON(rawSpec));}
  catch{fail('INVALID','source specification contains unsafe JSON');}
  if(!options||typeof options!=='object'||Array.isArray(options)||
     Object.keys(options).some(k=>!['fetchImpl','readToken'].includes(k)))
    fail('INVALID','unexpected read-only options');
  const bound=checked(spec);
  const injected=Object.hasOwn(options,'fetchImpl');
  const fetcher=injected?options.fetchImpl:globalThis.fetch;
  if(typeof fetcher!=='function')fail('UNKNOWN','HTTPS fetch unavailable');
  if(options.readToken!==undefined && (typeof options.readToken!=='string'||
     !/^[\x21-\x7e]{1,400}$/.test(options.readToken)))fail('INVALID','invalid read-token form');
  const headers={Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',
    'User-Agent':'relay-reset-b2a-custody-readonly'};
  if(options.readToken)headers.Authorization='Bearer '+options.readToken;
  let response;
  try{response=await fetcher(bound.api,{method:'GET',redirect:'error',
    cache:'no-store',headers});}
  catch{fail('UNKNOWN','native GitHub GET failed');}
  const provider=await boundedJSON(response,bound.api);
  const data=decodedBlob(provider,spec,bound);
  let replay;
  try {
    replay=await verifyPortableJournal(data,{
      repository:spec.repository,parent_issue:spec.parent_issue,
      source_sha:spec.source_sha,bundle_sha256:spec.bundle_sha256,
      tip_sha256:spec.tip_sha256
    });
  } catch(e) { fail('REFUTED','real R2-B1 cold replay rejected GitHub bundle: '+e.code); }
  if(replay.authorization_granted!==false||replay.externally_anchored!==false)
    fail('REFUTED','R2-B1 falsely elevated authority');
  const custody=Object.freeze({
    schema:'relay-github-content-custody-v1',
    status:injected?'INJECTED_UNVERIFIED':'GITHUB_COMMITTED_BYTES_OBSERVED',
    repository:spec.repository,parent_issue:spec.parent_issue,
    commit_sha:spec.commit_sha,path:spec.path,github_source_url:bound.html,
    git_blob_sha1:provider.sha,bundle_sha256:spec.bundle_sha256,
    source_sha:spec.source_sha,tip:Object.freeze({...replay.tip}),
    event_count:replay.event_count,session_ids:Object.freeze(replay.session_ids.slice()),
    policy_sha256:replay.policy_sha256,
    original_chat_source:'UNKNOWN',source_attribution:'PRODUCER_ASSERTED_UNVERIFIED',
    real_r2b1_replayed:true,provider_bytes_observed:!injected,
    externally_anchored:false,owner_message_authenticated:false,
    authorization_granted:false,independently_accepted:false,live_writer_enabled:false
  });
  // The consumer view is available only by an explicit in-process API; the
  // longstanding public summary-only API NEVER includes raw event text.
  return Object.freeze({custody,replay});
}

/** Status/commit/blob/tip summary only; no raw event text released. */
export async function readCommittedPortableJournal(rawSpec,options={}) {
  return (await readInternal(rawSpec,options)).custody;
}

/** Opt-in INTERNAL recovery view. Read-only; may contain PUBLIC session text.
 * Never send the replay object to GitHub issues, logs or public status surfaces.
 * The single verified native GET and R2-B1 disk replay are shared with summary API.
 */
export async function readCommittedPortableJournalForLineage(rawSpec,options={}) {
  return readInternal(rawSpec,options);
}
