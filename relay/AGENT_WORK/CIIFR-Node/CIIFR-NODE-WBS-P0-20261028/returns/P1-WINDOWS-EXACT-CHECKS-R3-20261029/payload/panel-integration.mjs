// Native controlled-DOM check of the actual pinned panel, not a browser test.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { verifyElementSection, verifyNodeSection, verifyReverseSection } from './qualification-guards.mjs';
if(!process.argv[2])throw Error('Usage: node panel-integration.mjs <pinned product source directory>');
const root=path.resolve(process.argv[2]);
const identities=JSON.parse(fs.readFileSync(new URL('../evidence/r2-served-source-readback.json',import.meta.url)));
for(const x of identities.files){
  const actual=fs.readFileSync(path.join(root,x.path));
  assert.equal(crypto.createHash('sha256').update(actual).digest('hex'),x.sha256,x.path);
}
const { createTestDom }=await import(pathToFileURL(path.join(root,'tests/helpers/vnext-dom-env.mjs')));
const { mountPropertyTransfer }=await import(pathToFileURL(path.join(root,'docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/panel.js')));
const dom=createTestDom();mountPropertyTransfer(dom.root);
for(const [key,name]of [['ptSourceFile','SYNTH_V14_SOURCE.cii'],['ptTargetFile','SYNTH_V14_TARGET0.cii']]){
  const b=fs.readFileSync(new URL('./fixtures/'+name,import.meta.url));
  dom[key].files=[{name,arrayBuffer:async()=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)}];
  await dom[key].dispatchEvent({type:'change'});
}
function sections(){
  return dom.ptResults.children.filter(s=>s.tagName==='SECTION').map(s=>({title:s.querySelector('h3').textContent,tables:s.querySelectorAll('table').map(t=>({headers:t.querySelector('thead').querySelectorAll('th').map(c=>c.textContent),rows:t.querySelector('tbody').querySelectorAll('tr').map(r=>r.querySelectorAll('td').map(c=>c.textContent))}))}));
}
const oracle=JSON.parse(fs.readFileSync(new URL('./physical-oracle.json',import.meta.url)));
const observed=[];
for(const e of oracle.elements){
  await dom.ptModeElement.click();
  for(const [key,value]of Object.entries({sourceFrom:e.fromNode,sourceTo:e.toNode,targetFrom:e.ordinal===1?840:850,targetTo:e.ordinal===1?850:860}))dom.ptInputs[key].value=value;
  await dom.ptRun.click();observed.push(verifyElementSection(sections().find(s=>s.title.startsWith('SOURCE')),e));
}
dom.ptInputs.sourceFrom.value=500;dom.ptInputs.sourceTo.value=400;await dom.ptRun.click();verifyReverseSection(sections().find(s=>s.title.startsWith('SOURCE')));
await dom.ptModeNode.click();dom.ptInputs.sourceNode.value=500;dom.ptInputs.targetNode.value=850;await dom.ptRun.click();
const attachments=verifyNodeSection(sections().find(s=>s.title.startsWith('SOURCE')),oracle.node);
console.log(JSON.stringify({scope:'Actual pinned product panel in native controlled DOM; browser NOT_RUN',status:'PASS',observedElements:observed,attachments},null,2));
