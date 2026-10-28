import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {indexCiiV14} from './candidate/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/cii-index.js';
import {inspectElementPair} from './candidate/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/element.js';
import {createTestDom} from './candidate/tests/helpers/vnext-dom-env.mjs';

const source=readFileSync(new URL('./fixtures/SYNTH_V14_SOURCE.cii',import.meta.url));
const target=readFileSync(new URL('./fixtures/SYNTH_V14_TARGET0.cii',import.meta.url));
const text=source.toString('ascii');
const edit=(section,row,field,value)=>{
  const lines=text.split('\r\n');
  const start=lines.findIndex(x=>x.trimEnd()==='#$ '+section)+1+row;
  assert.ok(start>row,'section exists');
  const a=2+13*field,b=a+13;
  lines[start]=lines[start].slice(0,a)+String(value).padStart(13)+lines[start].slice(b);
  return Buffer.from(lines.join('\r\n'),'ascii');
};
let passed=0,failed=0;
const reject=(label,bytes)=>{
  try{indexCiiV14(bytes);failed++;console.log('FAIL expected rejection:',label);}
  catch(e){passed++;console.log('PASS rejected:',label,e.message);}
};
assert.equal(indexCiiV14(source).counts.NUMELT,2);passed++;console.log('PASS positive public synthetic');
assert.equal(indexCiiV14(edit('CONTROL',2,5,1)).counts.IZUP,1);passed++;console.log('PASS IZUP=1 positive');
for(const [label,section,row,field,value] of [
  ['NUMELT mismatch','CONTROL',0,0,3],['negative nozzle','CONTROL',0,1,-1],
  ['negative hanger','CONTROL',0,2,-1],['IZUP99','CONTROL',2,5,99],
  ['RRMAT nonnumeric','MISCEL_1',0,0,'ABC'],['RRMAT700','MISCEL_1',0,0,700],
  ['negative restraint node','RESTRANT',0,0,-500],['negative CNode','RESTRANT',0,5,-5],
  ['zero node nonzero type','RESTRANT',0,0,0],['out of range restraint pointer','ELEMENTS',12,3,2],
  ['shared restraint pointer','ELEMENTS',27,3,1],['orphan restraint','ELEMENTS',12,3,0],
  ['negative ELEMENTS FROM','ELEMENTS',0,0,-400],
  ['out of range BEND pointer','ELEMENTS',12,0,999]
])reject(label,edit(section,row,field,value));
const zeroSlot=edit('RESTRANT',4,2,123);
reject('empty restraint slot with nonzero stiffness',zeroSlot);
reject('lowercase marker',Buffer.from(text.replace('#$ CONTROL','#$ control')));
reject('indented marker',Buffer.from(text.replace('#$ CONTROL','  #$ CONTROL')));
reject('duplicate marker',Buffer.from(text+'#$ CONTROL\r\n'));
const d=indexCiiV14(source);
assert.equal(inspectElementPair(null,d,{targetFrom:'500',targetTo:'400'}).target.entries.length,0);passed++;
assert.equal(d.byNode.get(500).incidents.length,2);passed++;
assert.equal(d.byNode.get(500).rigids.length,1);passed++;
assert.equal(d.byNode.get(500).restraints[0].slot,1);passed++;
assert.equal(d.elements[0].fields[1].typedNumber,30);assert.equal(d.elements[1].fields[1].typedNumber,20);passed++;
assert.equal(d.readOnly,true);passed++;
console.log('Parser/ownership probes:',{passed,failed});

// Controlled DOM evidence only. Begin with an actually approved Normal plan.
const dom=createTestDom();
await import('./candidate/tabs/cii-workspace/cii-fnr-vnext/ui/app.js?n01-probe');
const {makeDemoCii}=await import('./candidate/tabs/cii-workspace/cii-fnr-vnext/ui/demo-loader.js');
const normalBytes=Buffer.from(makeDemoCii());
dom.targetFile.files=[{name:'NORMAL_SYNTH.cii',arrayBuffer:async()=>normalBytes.buffer.slice(normalBytes.byteOffset,normalBytes.byteOffset+normalBytes.byteLength)}];
await dom.targetFile.dispatchEvent({type:'change'});
for(const [key,value] of [['find','OLD-A'],['replace','NEW-A']]){
  const input=dom.root.querySelector('[data-field="'+key+'"]');input.value=value;
  await input.dispatchEvent({type:'input'});
}
await dom.btnRun.click();assert.equal(dom.tbodyProposals.children.length,1);
await dom.btnApproveAll.click();assert.equal(dom.btnValidate.disabled,false);
const before={claims:dom.tbodyProposals.children.length,validateDisabled:dom.btnValidate.disabled};
await dom.tabProperty.click();await dom.tabNormal.click();
const after={claims:dom.tbodyProposals.children.length,validateDisabled:dom.btnValidate.disabled};
console.log('NORMAL approval roundtrip via Property:',JSON.stringify({before,after}));
assert.equal(after.claims,0);assert.equal(after.validateDisabled,true);

// Independent Property intake and A/B selectors, including a stale async load.
await dom.tabProperty.click();
dom.ptTargetFile.files=[{name:'TARGET0_SYNTH.cii',arrayBuffer:async()=>target.buffer.slice(target.byteOffset,target.byteOffset+target.byteLength)}];
await dom.ptTargetFile.dispatchEvent({type:'change'});
dom.ptSourceFile.files=[{name:'SOURCE_SYNTH.cii',arrayBuffer:async()=>source.buffer.slice(source.byteOffset,source.byteOffset+source.byteLength)}];
await dom.ptSourceFile.dispatchEvent({type:'change'});
dom.ptInputs.targetFrom.value='840';dom.ptInputs.targetTo.value='850';
dom.ptInputs.sourceFrom.value='400';dom.ptInputs.sourceTo.value='500';
await dom.ptRun.click();assert.equal(dom.ptResults.children.length,2);
await dom.ptModeNode.click();assert.equal(dom.ptResults.children.length,0);
dom.ptInputs.targetNode.value='850';dom.ptInputs.sourceNode.value='500';
await dom.ptRun.click();assert.equal(dom.ptResults.children.length,2);
let release;
dom.ptTargetFile.files=[{name:'SLOW.cii',arrayBuffer:()=>new Promise(resolve=>{release=()=>resolve(source.buffer.slice(source.byteOffset,source.byteOffset+source.byteLength));})}];
const pending=dom.ptTargetFile.dispatchEvent({type:'change'});
assert.equal(dom.ptResults.children.length,0);
dom.ptTargetFile.files=[{name:'FAST.cii',arrayBuffer:async()=>target.buffer.slice(target.byteOffset,target.byteOffset+target.byteLength)}];
await dom.ptTargetFile.dispatchEvent({type:'change'});release();await pending;
assert.match(dom.propertyPanel.querySelector('[data-pt-file-status="target"]').textContent,/FAST.cii/);
console.log('PASS controlled DOM: SOURCE/TARGET intake, exact pairs, A/B clear, stale async target rejected');

// Nodal's own approved state is independent from the new panel's file intake.
await dom.tabNodal.click();
console.log('Limit: Nodal startup/reload writer gates covered by exact existing nodal-ui test; browser/Windows NOT_RUN');
console.log('All observations complete; expected-rejection failures are intentionally preserved.');

const nd=createTestDom();
await import('./candidate/tabs/cii-workspace/cii-fnr-vnext/ui/app.js?n01-nodal-preservation');
await nd.tabNodal.click();
const row=values=>values.map((x,i)=>String(x).padStart(i?13:15)).join('');
const nb=Buffer.from(makeDemoCii().replace(row([2,0,0,1,0,0]),row([1,0,0,1,0,0])));
nd.targetFile.files=[{name:'NODAL_SYNTH.cii',arrayBuffer:async()=>nb.buffer.slice(nb.byteOffset,nb.byteOffset+nb.byteLength)}];
await nd.targetFile.dispatchEvent({type:'change'});
nd.nodalElements.nodalCsv.files=[{name:'node.csv',text:async()=> 'Node,Replace\n100,NODE-RENAMED\n'}];
await nd.nodalElements.nodalCsv.dispatchEvent({type:'change'});
await nd.nodalElements.nodalPreview.click();
await nd.nodalElements.nodalApproveAll.click();
assert.equal(nd.nodalElements.nodalValidate.disabled,false);
const nodalBefore=nd.nodalElements.nodalCount.textContent;
await nd.tabProperty.click();
nd.ptTargetFile.files=[{name:'PROPERTY_SYNTH.cii',arrayBuffer:async()=>target.buffer.slice(target.byteOffset,target.byteOffset+target.byteLength)}];
await nd.ptTargetFile.dispatchEvent({type:'change'});
await nd.ptModeNode.click();
await nd.tabNodal.click();
assert.equal(nd.nodalElements.nodalCount.textContent,nodalBefore);
assert.equal(nd.nodalElements.nodalValidate.disabled,false);
console.log('PASS controlled DOM: approved Nodal state survives Property visit, independent TARGET0 intake and mode switch');
process.exitCode=failed?1:0;
