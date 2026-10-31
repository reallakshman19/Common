// Independent byte-addressed V14 oracle. Intentionally never imports product code.
import fs from 'node:fs';
import crypto from 'node:crypto';

const AUX = ['BEND','RIGID','EXPJT','RESTRANT','DISPLMNT','FORCMNT','UNIFORM',
  'WIND','OFFSETS','ALLOWBLS','SIF&TEES','NODENAME','REDUCERS','FLANGES','EQUIPMNT'];
const COUNTS = ['BEND','RIGID','EXPJT','RESTRANT','DISPLMNT','FORCMNT',
  'UNIFORM','WIND','OFFSETS','ALLOWBLS','SIF&TEES','IZUP','EQUIPMNT'];
const CARD_WIDTH = {RIGID:1,RESTRANT:24,DISPLMNT:20,FORCMNT:20};
const REQUIRE = (ok, message) => {if(!ok) throw Error('PHYSICAL_ORACLE_'+message)};
const val = (s) => {
  const t=s.trim();
  if(!t) return 0;
  REQUIRE(/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?$/.test(t),'NUMBER');
  const n=Number(t.replace(/[Dd]/g,'E'));
  REQUIRE(Number.isFinite(n),'FINITE');return n;
};
const num = (r,a,b) => val(r.text.slice(a,b));
const six = (r,n=6) => Array.from({length:n},(_,i)=>num(r,2+13*i,15+13*i));
const cell = (r,a,b,key) => ({identity:key,lexeme:r.text.slice(a,b),
  byteStart:r.start+a,byteEnd:r.start+b});
function sectionsOf(buffer) {
  REQUIRE(buffer.every(b=>b<128),'NOT_ASCII');
  for(let i=0;i<buffer.length;i++) if(buffer[i]===10) REQUIRE(i>0 && buffer[i-1]===13,'NOT_CRLF');
  const lines=[],sections=new Map();let pos=0,sec=null;
  while(pos<buffer.length){const next=buffer.indexOf(10,pos);const stop=next<0?buffer.length:next;
    const end=buffer[stop-1]===13?stop-1:stop;
    const text=buffer.subarray(pos,end).toString('ascii');
    const m=/^#\$\s+([A-Z0-9_&]+)\s*$/.exec(text);
    if(m){REQUIRE(!sections.has(m[1]),'DUP_SECTION');sec=m[1];sections.set(sec,[])}
    else if(sec && text.trim()) sections.get(sec).push({text,start:pos,end});
    lines.push({text,start:pos,end});pos=next<0?buffer.length:next+1;
  }
  return {lines,sections};
}
function controls(sec) {
  const lines=sec.get('CONTROL'); REQUIRE(lines?.length>=4,'CONTROL');
  const v=six(lines[0]);const a=[...six(lines[1]),...six(lines[2]),...six(lines[3],1)];
  const counts=Object.fromEntries(COUNTS.map((k,i)=>[k,a[i]]));
  Object.assign(counts,{NUMELT:v[0],NUMNOZ:v[1],NOHGRS:v[2],NODENAME:v[3],REDUCERS:v[4],FLANGES:v[5]});
  REQUIRE(counts.NUMELT>0,'NUMELT');return counts;
}
function add(map,node,kind,entry){
  if(!map.has(node))map.set(node,{incidents:[],restraints:[],displacements:[],forces:[],rigids:[]});
  map.get(node)[kind].push(entry);
}
function rowText(e){return [String(e.ordinal),`${e.from} → ${e.to}`,e.branch||'(none)',
  ...e.fields.map(f=>`${f.identity}: ${f.lexeme.trim()} [bytes ${f.byteStart}–${f.byteEnd}]`),
  'HOLD: effective process semantics / identity not qualified'];}
function nodeRows(map,node){
 const o=map.get(node)||{incidents:[],restraints:[],displacements:[],forces:[],rigids:[]};
 return [
 ...o.incidents.map(e=>['ELEMENT',String(e.ordinal),`${e.from} → ${e.to}`,'Incident endpoint; element-owned properties']),
 ...o.restraints.map(e=>['RESTRANT',String(e.ownerElement),`Pointer ${e.pointer} · Slot ${e.slot}`,`Type ${e.type} · CNode ${e.cnode} · semantics partial`]),
 ...o.displacements.map(e=>['DISPLMNT',String(e.ownerElement),`Pointer ${e.pointer} · Specification ${e.specification}`,'Vectors/cases not yet qualified']),
 ...o.forces.map(e=>['FORCMNT',String(e.ownerElement),`Pointer ${e.pointer} · Specification ${e.specification}`,'Input loads only; not computed reactions']),
 ...o.rigids.map(e=>['RIGID',String(e.ownerElement),`Pointer ${e.pointer}`,`Weight raw ${e.weightLexeme} · element-owned, semantics partial`])
 ];
}
export function independentOracle(file, expectedSHA) {
 const data=fs.readFileSync(file);
 const hash=crypto.createHash('sha256').update(data).digest('hex');
 if(expectedSHA)REQUIRE(hash.toLowerCase()===expectedSHA.toLowerCase(),'INTAKE_DIGEST_MISMATCH');
 const {sections:sec,lines}=sectionsOf(data);
 const ver=sec.get('VERSION')?.[0]?.text.trim().split(/\s+/).map(Number)[1]; REQUIRE(ver===14,'VERSION');
 const counts=controls(sec);const records=sec.get('ELEMENTS');
 REQUIRE(records?.length===counts.NUMELT*15,'ELEMENT_CARDINALITY');
 const material=sec.get('MISCEL_1');const materialRows=Math.ceil(counts.NUMELT/6);
 REQUIRE(material?.length>=materialRows,'MATERIAL_ROWS');
 const materials=Array.from({length:counts.NUMELT},(_,i)=>num(material[Math.floor(i/6)],2+13*(i%6),15+13*(i%6)));
 REQUIRE(materials.every(n=>Number.isInteger(n)&&n>=1&&n<=699),'MATERIAL_IDS');
 const elements=[],byNode=new Map(),owners=Object.fromEntries(AUX.map(f=>[f,new Map()]));
 for(let i=0;i<counts.NUMELT;i++){
  const cs=records.slice(i*15,(i+1)*15);const from=num(cs[0],0,15),to=num(cs[0],15,28);
  REQUIRE(Number.isSafeInteger(from)&&from>0&&Number.isSafeInteger(to)&&to>0,'ENDPOINT_DOMAIN');
  const pointers=Object.fromEntries(AUX.map((f,j)=>[f,num(cs[12+Math.floor(j/6)],2+13*(j%6),15+13*(j%6))]));
  let branch=null;const br=cs[10].text;const declared=Number(br.slice(0,13).trim());const label=br.slice(13).trimEnd();
  if(label.startsWith('/')&&declared===label.length)branch=label;
  const e={ordinal:i+1,from,to,branch,pointers,fields:[
   cell(cs[1],41,54,'TEMPERATURE_1_STORED'),cell(cs[3],2,15,'PRESSURE_1_STORED'),
   cell(cs[5],15,28,'FLUID_DENSITY_STORED')]}; elements.push(e);
  for(const node of new Set([from,to]))add(byNode,node,'incidents',e);
  for(const [family,p] of Object.entries(pointers)){
   const total=counts[family];REQUIRE(Number.isInteger(p)&&p>=0&&p<=total,'POINTER_RANGE_'+family);
   if(p){REQUIRE(!owners[family].has(p),'POINTER_SHARED_'+family);owners[family].set(p,e)}
  }
 }
 for(const family of AUX){const tally=counts[family];REQUIRE(owners[family].size===tally,'POINTER_ORPHAN_'+family)}
 for(const [family,width] of Object.entries(CARD_WIDTH)) {
  REQUIRE((sec.get(family)?.length||0)===counts[family]*width,'AUX_CARDINALITY_'+family);
 }
 const auxRows=(family,p)=>sec.get(family).slice((p-1)*CARD_WIDTH[family],p*CARD_WIDTH[family]);
 let populatedRest=0;
 for(const [p,e] of owners.RESTRANT){const cs=auxRows('RESTRANT',p);
  for(let s=0;s<6;s++){const c=cs.slice(s*4,s*4+4),node=num(c[0],2,15),type=num(c[0],15,28),cnode=num(c[0],67,80);
   if(!node)continue; populatedRest++;add(byNode,node,'restraints',{ownerElement:e.ordinal,pointer:p,slot:s+1,type,cnode,
    byteStart:c[0].start,byteEnd:c[3].end});
  }
 }
 for(const [family,field] of [['DISPLMNT','displacements'],['FORCMNT','forces']]){
  for(const [p,e] of owners[family]){const cs=auxRows(family,p);
   for(let s=0;s<2;s++){const node=num(cs[s*10],2,15);if(node)add(byNode,node,field,{ownerElement:e.ordinal,pointer:p,specification:s+1,byteStart:cs[s*10].start})}
  }
 }
 for(const [p,e] of owners.RIGID){const r=auxRows('RIGID',p)[0];const weightLexeme=r.text.slice(2,15).trim();
  for(const node of new Set([e.from,e.to]))add(byNode,node,'rigids',{ownerElement:e.ordinal,pointer:p,weightLexeme});
 }
 const unique=new Map();for(const e of elements){const key=e.from+':'+e.to;unique.set(key,(unique.get(key)||0)+1)}
 const element=elements.find(e=>unique.get(e.from+':'+e.to)===1 && e.fields.every(x=>x.lexeme.trim()))||elements.find(e=>unique.get(e.from+':'+e.to)===1);
 const selectNode=(predicate)=>[...byNode].find(([n,v])=>predicate(v))?.[0];
 const nodeCandidates=[
   selectNode(v=>v.incidents.length>=2&&v.restraints.length>0),
   selectNode(v=>v.restraints.length>0),
   selectNode(v=>v.rigids.length>0),
   selectNode(v=>v.displacements.length>0),
   selectNode(v=>v.incidents.length>=2),
 ].filter(Boolean);
 REQUIRE(element && nodeCandidates.length>=3,'REQUIRED_WITNESSES');
 const witnesses={element:{from:element.from,to:element.to,expectedRows:[rowText(element)]},
   nodes:[...new Set(nodeCandidates)].map(n=>({node:n,expectedRows:nodeRows(byNode,n)}))};
 const tallies={version:ver,elementRecords:elements.length,elementCards:records.length,
  materialRows,restraintBlocks:counts.RESTRANT,populatedRestraintSlots:populatedRest,
  rigidRecords:counts.RIGID,displacementBlocks:counts.DISPLMNT,forceBlocks:counts.FORCMNT,
  nodeNameBlocks:counts.NODENAME};
 return {private:{sha256:hash,size:data.length,witnesses,counts,tallies},
  public:{originalIdentity:'PRIVATE_MATCHED',version:ver,tallies,
   pointerOwnership:'INDEPENDENT_FIFTEEN_FAMILY_RECONCILED',witnessNodeQueries:witnesses.nodes.length}};
}
