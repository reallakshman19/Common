import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createTestDom} from './candidate/tests/helpers/vnext-dom-env.mjs';
import {makeDemoCii} from './candidate/tabs/cii-workspace/cii-fnr-vnext/ui/demo-loader.js';
import {indexCiiV14} from './candidate/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/cii-index.js';
const sha=b=>createHash('sha256').update(b).digest('hex');
const path='./'+(process.env.REVIEW_SUBJECT||'candidate');
const {planNormal}=await import(path+'/tabs/cii-workspace/cii-fnr-vnext/normal/plan.js');
const {validatePostimage}=await import(path+'/tabs/cii-workspace/cii-fnr-vnext/ui/writer.js');
const row=v=>v.map((x,i)=>String(x).padStart(i?13:15)).join('');
const upload=b=>({name:'independent.cii',arrayBuffer:async()=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)});
const source=await readFile(new URL('./fixtures/SYNTH_V14_SOURCE.cii',import.meta.url));
const target=await readFile(new URL('./fixtures/SYNTH_V14_TARGET0.cii',import.meta.url));
function splice(b,section,card,slot,value) {
 const lines=b.toString('ascii').split('\r\n');const n=lines.indexOf('#$ '+section)+1+card;
 const a=2+13*slot,z=a+13;lines[n]=lines[n].slice(0,a)+String(value).padStart(13)+lines[n].slice(z);
 return Buffer.from(lines.join('\r\n'),'ascii');
}
const before=[sha(source),sha(target)];
const si=indexCiiV14(source),ti=indexCiiV14(target);
assert.deepEqual(si.elements.map(e=>[e.from,e.to]),[[400,500],[500,600]]);
assert.equal(si.byNode.get(500).incidents.length,2);
assert.equal(si.byNode.get(500).restraints.length,1);
assert.deepEqual(si.elements.map(e=>e.fields.map(f=>f.typedNumber)),[[200,30,1.01],[180,20,1.01]]);
// Literal TARGET0 physical cards: first stored T1=195/P1=28; second T1=175/P1=18.
assert.deepEqual(ti.elements.map(e=>e.fields.map(f=>f.typedNumber)),[[195,28,1.01],[175,18,1.01]]);
console.log('PASS literal public-fixture endpoint, incident, restraint, T1/P1/density expectations');
for(const end of [0,1])for(const val of [-7,0,'1.5']) {
 const bad=splice(source,'ELEMENTS',0,end,val);assert.throws(()=>indexCiiV14(bad));
}
console.log('PASS endpoint negative/zero/fraction contrary cases');
const pointerLayout=[['BEND',12,0],['RIGID',12,1],['EXPJT',12,2],['RESTRANT',12,3],['DISPLMNT',12,4],['FORCMNT',12,5],['UNIFORM',13,0],['WIND',13,1],['OFFSETS',13,2],['ALLOWBLS',13,3],['SIF&TEES',13,4],['NODENAME',13,5],['REDUCERS',14,0],['FLANGES',14,1],['EQUIPMNT',14,2]];
for(const [family,card,slot] of pointerLayout)for(const bad of [-1,si.counts[family]+1,'0.5']) {
 const bytes=splice(source,'ELEMENTS',card,slot,bad);assert.throws(()=>indexCiiV14(bytes),undefined,family+':'+bad);
}
console.log('PASS all15 pointer families reject below-zero, count+1 and fractional values; explicit physical layout oracle');
for(const [family,card,slot] of pointerLayout.filter(([x])=>!['RIGID','RESTRANT','DISPLMNT','FORCMNT','NODENAME'].includes(x))) {
 const control={BEND:[1,0],EXPJT:[1,2],UNIFORM:[2,0],WIND:[2,1],OFFSETS:[2,2],ALLOWBLS:[2,3],'SIF&TEES':[2,4],REDUCERS:[0,4],FLANGES:[0,5],EQUIPMNT:[3,0]}[family];
 const b=splice(splice(source,'CONTROL',...control,1),'ELEMENTS',card,slot,1),d=indexCiiV14(b);
 assert.equal(d.elements[0].pointers[family],1);assert(d.diagnostics.some(x=>x.family===family&&x.classification==='UNKNOWN'));
}
console.log('PASS all10 non-NODENAME unsupported typed families at upper boundary1 remain UNKNOWN with missing contents');
const residue=splice(source,'RESTRANT',4,2,'1D-999');
const rd=indexCiiV14(residue).diagnostics.find(d=>d.code==='PROPERTY_RESTRAINT_DORMANT_RESIDUE');
assert(rd&&rd.classification==='UNKNOWN');assert.equal(rd.ownerElement,1);assert.equal(rd.slot,2);assert.equal(rd.pointer,1);
assert(residue.subarray(rd.byteStart,rd.byteEnd).includes(Buffer.from('1D-999')));
assert.deepEqual([sha(source),sha(target)],before);
console.log('PASS lexical underflow residue is UNKNOWN; physical span and original-input byte digests preserved');
// Reuse only the existing fixture constructor to isolate the inherited failing assertion.
const testText=await readFile(new URL('./candidate/tests/cii-fnr-vnext-branch-scope.test.mjs',import.meta.url),'utf8');
const fixtureText=testText.slice(testText.indexOf('const B2 ='),testText.indexOf('const branchRule ='));
const {syntheticTarget,B1,B2}=new Function(fixtureText+';return {syntheticTarget,B1,B2}')();
for(const branch of [B2.slice(0,-1),B2+'-WRONG',B1]) {
 const bytes=syntheticTarget(),hash=sha(bytes),plan=planNormal({tab:'NORMAL',targetBytes:bytes,originalTargetSha256:hash,rules:[{id:'independent',find:'ALIAS-OLD',replace:'NEW-4',mode:'LITERAL',flags:'g',field:'NODENAME.BOTH',scope:'BRANCH',branch}],options:{}});
 const expected=branch===B1?1:0;assert.equal(plan.claims.length,expected);
 if(branch===B1) {
  assert.equal(plan.claims[0].targetElementWitness,'3:9000:9001');assert.equal(plan.claims[0].fieldIdentity,'NODENAME.FROM');
  const result=await validatePostimage({original:bytes,originalHash:hash,plan,approvedIds:plan.claims.map(x=>x.id),tab:'NORMAL'});
  const claim=plan.claims[0];const literal=Buffer.from(bytes);literal.write('NEW-4'.padEnd(claim.byteEnd-claim.byteStart),claim.byteStart,'ascii');assert.deepEqual(Buffer.from(result.bytes),literal);
 }
 console.log('PASS independent branch oracle',JSON.stringify({branch,expected,actual:plan.claims.length}));
}
// Owning CSV changes must revoke export authority at selection, even if reading is slow.
const dom=createTestDom();await import(path+'/tabs/cii-workspace/cii-fnr-vnext/ui/app.js?independent='+Date.now());
dom.targetFile.files=[upload(Buffer.from(makeDemoCii()))];await dom.targetFile.dispatchEvent({type:'change'});
for(const [field,value] of [['find','OLD-A'],['replace','NEW-A']]) {const e=dom.root.querySelector('[data-field="'+field+'"]');e.value=value;await e.dispatchEvent({type:'input'});}
for(const button of [dom.btnRun,dom.btnApproveAll,dom.btnValidate,dom.btnApply])await button.click();
assert.equal(dom.btnExport.disabled,false);
let release;dom.csvFile.files=[{name:'changed-rules.csv',text:()=>new Promise(resolve=>{release=()=>resolve('Find,Replace\nOLD-A,NEW-C\n');})}];
const pending=dom.csvFile.dispatchEvent({type:'change'});
assert(release);const pendingState={exportDisabled:dom.btnExport.disabled,applyDisabled:dom.btnApply.disabled,validateDisabled:dom.btnValidate.disabled,claims:dom.tbodyProposals.children.length};
const downloads=[];const oldCreate=URL.createObjectURL;URL.createObjectURL=blob=>{downloads.push(blob);return 'blob:review';};
await dom.btnExport.click();URL.createObjectURL=oldCreate;
const output=downloads.length?Buffer.from(await downloads[0].arrayBuffer()).toString('ascii'):'';
console.log('OBSERVATION pending owning CSV selection',JSON.stringify({...pendingState,downloads:downloads.length,exportContainsOldApprovedReplacement:output.includes('NEW-A'),exportContainsPendingReplacement:output.includes('NEW-C')}));
release();await pending;assert.equal(dom.btnExport.disabled,true);
console.log('PASS CSV completion revokes output; FAIL selection boundary if immediate revocation is required');
