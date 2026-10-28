/* RELAY RESET R1-A: structural provenance validator (NO authority or network).
   JSON shape and links only. A valid document is NOT an authenticated Owner command,
   confirmed CI result, acceptance, writer approval or active session recorder. */
function provenanceAPI() {
  const ID = /^[A-Z][A-Z0-9._:-]{0,63}$/;
  const SHA = /^[a-f0-9]{40}$/;
  const HASH = /^[a-f0-9]{64}$/;
  const PARENT = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+#[1-9][0-9]*$/;
  const TYPES = Object.freeze(["owner_intents","claims","responsibilities","sessions","task_evidence","research_findings","owner_decisions"]);
  const MAX_ITEMS_PER_ARRAY = 10000; // Fail closed on unbounded agent/provider documents
  class ProvenanceError extends Error { constructor(message) { super(message); this.name = "ProvenanceError"; } }
  function fail(where, why) { throw new ProvenanceError(`${where}: ${why}`); }
  function obj(value, where, required, optional = []) {
    if (!value || typeof value !== "object" || Array.isArray(value)) fail(where,"expected object");
    const allowed = new Set([...required,...optional]);
    for(const k of Object.keys(value)) if(!allowed.has(k)) fail(where,`unexpected key ${k}`);
    for(const k of required) if(!Object.hasOwn(value,k)) fail(where,`missing key ${k}`);
  }
  function str(value,where) { if(typeof value !== "string" || !value.trim()) fail(where,"expected nonempty string"); }
  function arr(value,where,minimum=0) { if(!Array.isArray(value)||value.length<minimum||value.length>MAX_ITEMS_PER_ARRAY) fail(where,`expected array size ${minimum}..${MAX_ITEMS_PER_ARRAY}`); }
  function id(value,where) { if(typeof value!=="string"||!ID.test(value)) fail(where,"invalid immutable ID"); }
  function ids(value,where,min=0) { arr(value,where,min); const s=new Set(); value.forEach((x,i)=>{id(x,`${where}[${i}]`);if(s.has(x))fail(where,`duplicate reference ${x}`);s.add(x);}); }
  function one(value,options,where){if(!options.includes(value))fail(where,`expected one of ${options.join(", ")}`);}
  function source(value,where){
    obj(value,where,["kind","status","locator"],["digest"]);
    one(value.kind,["CHAT","GITHUB_ISSUE","GITHUB_COMMENT","GIT_BLOB","FILE","OTHER"],`${where}.kind`);
    one(value.status,["UNKNOWN","CLAIMED","FIRST_DURABLE_MIRROR"],`${where}.status`);
    if(value.status==="UNKNOWN"){
      if(value.locator!==null)fail(where,"unknown source must use locator=null");
    }else{
      str(value.locator,`${where}.locator`);
      if(!/^https:\/\//.test(value.locator) && !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.\/@#:-]+$/.test(value.locator))fail(where,"invalid source locator syntax");
    }
    if(Object.hasOwn(value,"digest") && (typeof value.digest!=="string"||!HASH.test(value.digest)))fail(where,"invalid SHA256 source digest");
  }
  function path(x,where){
    str(x,where);
    if(x.startsWith("/")||x.includes("\\")||x.split("/").some(seg=>!seg||seg==="."||seg==="..")) fail(where,"unsafe relative path");
  }
  function validate(doc){
    obj(doc,"document",["schema","parent_issue",...TYPES],[]);
    if(doc.schema!=="relay-provenance-v1") fail("document.schema","unsupported schema version");
    if(typeof doc.parent_issue!=="string"||!PARENT.test(doc.parent_issue))fail("document.parent_issue","must be owner/repo#number");
    const registry=new Map();
    const index={};
    for(const typ of TYPES) {
      arr(doc[typ],typ,typ==="owner_intents"?1:0);
      index[typ]=new Map();
      doc[typ].forEach((record,i)=>{
        const where=`${typ}[${i}]`;
        if(!record||typeof record!=="object"||Array.isArray(record))fail(where,"expected record object");
        id(record.id,`${where}.id`);
        if(registry.has(record.id))fail(where,`duplicate global ID ${record.id} (first in ${registry.get(record.id)})`);
        registry.set(record.id,typ);index[typ].set(record.id,record);
      });
    }
    for(const [i,v] of doc.owner_intents.entries()){
      const w=`owner_intents[${i}]`;
      obj(v,w,["id","raw_text","original_source","first_durable_mirror"]);
      str(v.raw_text,`${w}.raw_text`);source(v.original_source,`${w}.original_source`);
      if(v.first_durable_mirror!==null)str(v.first_durable_mirror,`${w}.first_durable_mirror`);
      if(v.original_source.status==="FIRST_DURABLE_MIRROR")fail(w,"a mirror is not the original source");
    }
    for(const [i,v] of doc.claims.entries()){
      const w=`claims[${i}]`;obj(v,w,["id","intent_ids","criterion"]);
      ids(v.intent_ids,`${w}.intent_ids`,1);str(v.criterion,`${w}.criterion`);
    }
    for(const [i,v] of doc.responsibilities.entries()){
      const w=`responsibilities[${i}]`;obj(v,w,["id","claim_ids","depends_on","scope","write_surface"]);
      ids(v.claim_ids,`${w}.claim_ids`,1);ids(v.depends_on,`${w}.depends_on`);
      str(v.scope,`${w}.scope`);arr(v.write_surface,`${w}.write_surface`,1);
      v.write_surface.forEach((x,j)=>path(x,`${w}.write_surface[${j}]`));
    }
    for(const [i,v] of doc.sessions.entries()){
      const w=`sessions[${i}]`;obj(v,w,["id","responsibility_id","agent_id","base_sha","changed_files","events"]);
      id(v.responsibility_id,`${w}.responsibility_id`);str(v.agent_id,`${w}.agent_id`);
      if(!SHA.test(v.base_sha))fail(w,"base_sha must be 40 lowercase hex");
      arr(v.changed_files,`${w}.changed_files`);
      v.changed_files.forEach((x,j)=>path(x,`${w}.changed_files[${j}]`));
      arr(v.events,`${w}.events`,1);
      v.events.forEach((e,j)=>{const x=`${w}.events[${j}]`;
        obj(e,x,["kind","source","summary"]);
        one(e.kind,["OWNER_PROMPT","AGENT_RESPONSE","DECISION","CODE_CHANGE","ERROR","RECOVERY"],`${x}.kind`);
        source(e.source,`${x}.source`);str(e.summary,`${x}.summary`);
      });
      if(v.changed_files.length&&!v.events.some(e=>e.kind==="CODE_CHANGE"))fail(w,"changed_files need CODE_CHANGE event");
    }
    for(const [i,v] of doc.task_evidence.entries()){
      const w=`task_evidence[${i}]`;obj(v,w,["id","responsibility_id","session_id","kind","source","commit_sha"]);
      id(v.responsibility_id,`${w}.responsibility_id`);id(v.session_id,`${w}.session_id`);
      one(v.kind,["START","END","RECOVERY_START"],`${w}.kind`);
      source(v.source,`${w}.source`);
      if(v.commit_sha!==null&&(!SHA.test(v.commit_sha)))fail(w,"invalid evidence exact commit SHA");
    }
    for(const [i,v] of doc.research_findings.entries()){
      const w=`research_findings[${i}]`;obj(v,w,["id","statement","source","verification"]);
      str(v.statement,`${w}.statement`);source(v.source,`${w}.source`);
      one(v.verification,["UNVERIFIED","SUPPORTED_CLAIM","CONTRADICTED_CLAIM"],`${w}.verification`);
    }
    for(const [i,v] of doc.owner_decisions.entries()){
      const w=`owner_decisions[${i}]`;obj(v,w,["id","intent_id","finding_ids","disposition","source"]);
      id(v.intent_id,`${w}.intent_id`);ids(v.finding_ids,`${w}.finding_ids`,1);
      one(v.disposition,["ADOPT","REJECT","DEFER"],`${w}.disposition`);source(v.source,`${w}.source`);
    }
    const check=(k,targets,where)=>{ for(const value of targets) if(!index[k].has(value))fail(where,`dangling ${k} reference ${value}`); };
    for(const v of doc.claims)check("owner_intents",v.intent_ids,`claims.${v.id}`);
    for(const v of doc.responsibilities){check("claims",v.claim_ids,`responsibilities.${v.id}`);check("responsibilities",v.depends_on,`responsibilities.${v.id}`);if(v.depends_on.includes(v.id))fail("responsibilities",`self dependency ${v.id}`);}
    for(const v of doc.sessions)check("responsibilities",[v.responsibility_id],`sessions.${v.id}`);
    for(const v of doc.task_evidence){
      check("responsibilities",[v.responsibility_id],`task_evidence.${v.id}`);
      check("sessions",[v.session_id],`task_evidence.${v.id}`);
      const session=index.sessions.get(v.session_id);
      if(session.responsibility_id!==v.responsibility_id)fail("task_evidence",`session and responsibility mismatch ${v.id}`);
      if(v.kind==="END" && session.changed_files.length && v.commit_sha===null)fail("task_evidence",`code END needs exact SHA ${v.id}`);
    }
    for(const v of doc.owner_decisions){check("owner_intents",[v.intent_id],`owner_decisions.${v.id}`);check("research_findings",v.finding_ids,`owner_decisions.${v.id}`);}
    // Iterative DFS: a legitimate deep responsibility chain must not overflow JS stack.
    const visitState=new Map(); // 1=in current path, 2=finished
    for(const root of index.responsibilities.keys()){
      if(visitState.get(root)===2)continue;
      visitState.set(root,1);
      const stack=[{id:root,next:0}];
      while(stack.length){
        const top=stack[stack.length-1];
        const deps=index.responsibilities.get(top.id).depends_on;
        if(top.next===deps.length){visitState.set(top.id,2);stack.pop();continue;}
        const dep=deps[top.next++];
        if(visitState.get(dep)===1)fail("responsibilities",`dependency cycle through ${dep}`);
        if(visitState.get(dep)!==2){visitState.set(dep,1);stack.push({id:dep,next:0});}
      }
    }
    return Object.freeze({valid:true,counts:Object.fromEntries(TYPES.map(k=>[k,doc[k].length])),no_authority_asserted:true});
  }
  function canonicalJSON(value){
    // Bounded serialization is needed even before provider authenticity is established.
    const active=new Set();
    const MAX_DEPTH=256,MAX_NODES=100000;
    let nodes=0;
    function normal(x,depth){
      if(depth>MAX_DEPTH)throw new ProvenanceError("canonical JSON nesting limit exceeded");
      if(x===null||typeof x==="string"||typeof x==="boolean")return x;
      if(typeof x==="number"){if(!Number.isFinite(x))throw new ProvenanceError("non-finite number");return x;}
      if(!x||typeof x!=="object")throw new ProvenanceError("unsupported canonical JSON type");
      if(active.has(x))throw new ProvenanceError("cyclic canonical JSON input");
      if(++nodes>MAX_NODES)throw new ProvenanceError("canonical JSON node limit exceeded");
      active.add(x);
      try{
        if(Array.isArray(x)){
          if(x.length>MAX_ITEMS_PER_ARRAY)throw new ProvenanceError("canonical JSON array size limit exceeded");
          const result=[];
          for(let i=0;i<x.length;i++){
            if(!Object.hasOwn(x,i))throw new ProvenanceError("sparse arrays unsupported");
            const descriptor=Object.getOwnPropertyDescriptor(x,String(i));
            if(!descriptor||!Object.hasOwn(descriptor,"value"))throw new ProvenanceError("accessor arrays unsupported");
            result.push(normal(descriptor.value,depth+1));
          }
          return result;
        }
        const out=Object.create(null);
        for(const k of Object.keys(x).sort()){
          const descriptor=Object.getOwnPropertyDescriptor(x,k);
          if(!descriptor||!Object.hasOwn(descriptor,"value"))throw new ProvenanceError("accessor property unsupported");
          out[k]=normal(descriptor.value,depth+1);
        }
        return out;
      }finally{active.delete(x);}
    }
    return JSON.stringify(normal(value,0));
  }
  function traceClaim(doc,claimId){
    validate(doc);
    if(!doc.claims.some(x=>x.id===claimId))fail("traceClaim",`unknown claim ${claimId}`);
    const responsibilities=doc.responsibilities.filter(r=>r.claim_ids.includes(claimId)).map(r=>r.id);
    const sessions=doc.sessions.filter(s=>responsibilities.includes(s.responsibility_id)).map(s=>s.id);
    const evidence=doc.task_evidence.filter(e=>responsibilities.includes(e.responsibility_id)).map(e=>e.id);
    const intents=doc.claims.find(c=>c.id===claimId).intent_ids.slice();
    return Object.freeze({claim_id:claimId,owner_intent_ids:intents,responsibility_ids:responsibilities,session_ids:sessions,evidence_ids:evidence});
  }
  // These are pure structural inverses. An ID link is NOT evidence authenticity.
  function ownerRecords(doc,intentIds){
    return [...new Set(intentIds)].map(intentId=>{
      const intent=doc.owner_intents.find(x=>x.id===intentId);
      // Validation guaranteed this source exists; preserve raw Owner text and the
      // crucial UNKNOWN-original-vs-first-GitHub-mirror distinction.
      return Object.freeze({
        id:intent.id,raw_text:intent.raw_text,
        original_source:Object.freeze({...intent.original_source}),
        first_durable_mirror:intent.first_durable_mirror
      });
    });
  }
  function traceEvidence(doc,evidenceId){
    validate(doc);
    const evidence=doc.task_evidence.find(x=>x.id===evidenceId);
    if(!evidence)fail("traceEvidence",`unknown evidence ${evidenceId}`);
    const session=doc.sessions.find(x=>x.id===evidence.session_id);
    const responsibility=doc.responsibilities.find(x=>x.id===evidence.responsibility_id);
    const claimIds=responsibility.claim_ids.slice();
    const intentIds=claimIds.flatMap(id=>doc.claims.find(x=>x.id===id).intent_ids);
    return Object.freeze({
      evidence_id:evidence.id,
      evidence_kind:evidence.kind,
      evidence_source_status:evidence.source.status,
      evidence_commit_sha:evidence.commit_sha,
      session_id:session.id,responsibility_id:responsibility.id,
      claim_ids:claimIds,
      changed_files:session.changed_files.slice(),
      owner_intents:ownerRecords(doc,intentIds),
      // No authority, provider verification, CI outcome or acceptance is projected.
      no_authority_asserted:true
    });
  }
  function traceModule(doc,modulePath){
    validate(doc);
    path(modulePath,"traceModule.modulePath");
    const sessions=doc.sessions.filter(x=>x.changed_files.includes(modulePath));
    const sessionIds=sessions.map(x=>x.id);
    // The module is attached to the precise sessions that changed it, not to
    // every session sharing the same responsibility.
    const evidence=doc.task_evidence.filter(x=>sessionIds.includes(x.session_id));
    const responsibilityIds=[...new Set(sessions.map(x=>x.responsibility_id))];
    const claimIds=[...new Set(responsibilityIds.flatMap(id=>
      doc.responsibilities.find(x=>x.id===id).claim_ids))];
    const intentIds=claimIds.flatMap(id=>doc.claims.find(x=>x.id===id).intent_ids);
    return Object.freeze({
      module_path:modulePath,
      session_ids:sessionIds,
      evidence_ids:evidence.map(x=>x.id),
      responsibility_ids:responsibilityIds,
      claim_ids:claimIds,
      owner_intents:ownerRecords(doc,intentIds),
      no_authority_asserted:true
    });
  }
  return Object.freeze({validate,canonicalJSON,traceClaim,traceEvidence,traceModule,ProvenanceError});
}
const API = provenanceAPI();
export const validate = API.validate;
export const canonicalJSON = API.canonicalJSON;
export const traceClaim = API.traceClaim;
export const traceEvidence = API.traceEvidence;
export const traceModule = API.traceModule;
export const ProvenanceError = API.ProvenanceError;
