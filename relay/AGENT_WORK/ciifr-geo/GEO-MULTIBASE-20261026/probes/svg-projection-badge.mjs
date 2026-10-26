import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {webcrypto} from 'node:crypto';
import {createGeometryWorkbench} from '../geo-multibase-work/prototypes/ciifr-map/workbench.js';
import {readXmlGraph} from '../geo-multibase-work/prototypes/ciifr-map/xml-intake.js';
import {cameraPresentation} from '../geo-multibase-work/prototypes/ciifr-map/camera-presentation.js';

// Reviewer probe: actual app module and original XML/workbench; a controlled DOM
// captures labels and registered handlers. This is not a browser-layout test.
assert(vm.SourceTextModule, 'Run with --experimental-vm-modules');
const {DOMParser}=createRequire('/workspace/scratch/ca71d2f89cf7/map-test-runtime/package.json')('@xmldom/xmldom');
const wb=createGeometryWorkbench({read:(bytes,options)=>readXmlGraph(bytes,{...options,cryptoRef:webcrypto,
  parser:new DOMParser({onError:(level,message)=>{throw Error(level+':'+message);}})})});
for (const [side,file] of [['SOURCE','S1-F05.xml'],['TARGET','S1-R4.xml']])
  await wb.load(side,new Uint8Array(readFileSync(new URL('../geo-multibase-work/prototypes/ciifr-map/tests/fixtures/'+file,import.meta.url))),file);
for (const tab of ['A','B']) {
  wb.switchTab(tab);wb.addAnchor('3790','3790');wb.setProjection(tab==='A'?'XZ':'XY');wb.run();
}
wb.switchTab('A');
const nodes=new Map();
const el=id=>nodes.get(id)||nodes.set(id,{id,value:id==='projection'?'XZ':id.startsWith('tol-')?'100':'',
  textContent:'',hidden:false,disabled:false,listeners:{},dataset:{},style:{},classList:{toggle(){}},
  setAttribute(){},replaceChildren(){},append(){},addEventListener(event,fn){this.listeners[event]=fn;}}).get(id);
const tabs=['A','B','C'].map(id=>Object.assign(el('tab-'+id),{dataset:{comparison:id}}));
let mountedProjection=null;
const context=vm.createContext({document:{getElementById:el,
  querySelectorAll:q=>q==='[data-comparison]'?tabs:[]},window:{addEventListener(){}},console,setTimeout});
const modules={
  './workbench.js':{createGeometryWorkbench:()=>wb},
  './workbench-export.js':{exportWorkbench(){}},
  './multibase-view.js':{renderWorkbenchRows(){},workbenchSummary(){return 'Controlled summary';}},
  './review-viewport.js':{setupReviewViewport(){}},
  './camera-presentation.js':{cameraPresentation},
  './view.js':{graphInfo(){return '';},renderAnchors(){},readableSelection(){return '';},selectedDetails(){return '';},
    selectedGeometryObjects(){return [];},mountScene(result){mountedProjection=result.projection;return {}; }},
  './geo-viewer-bridge.js':{createGeoViewerBridge:()=>({isActive:()=>false,disable(){},setSelection(){}})},
};
const source=process.env.REVIEW_APP_SOURCE||new URL('../geo-multibase-work/prototypes/ciifr-map/app.js',import.meta.url);
const app=new vm.SourceTextModule(readFileSync(source,'utf8'),{context});
await app.link(spec=>{
  const exports=modules[spec];assert(exports,'Unexpected import '+spec);
  return new vm.SyntheticModule(Object.keys(exports),function(){for(const [k,v]of Object.entries(exports))this.setExport(k,v);},{context});
});
await app.evaluate();
el('run').listeners.click();
const observations=[];
function record(stage,expected) {
  observations.push({stage,expected,actualBase:wb.active,result:wb.current().projection,
    selector:el('projection').value,heading:el('projection-label').textContent,
    mountedProjection,badge:el('camera-state').textContent});
}
record('A original XZ','XZ');
el('projection').value='ISO';el('projection').listeners.input();record('A changes to ISO','ISO');
el('tab-B').listeners.click();record('Switch B saved XY','XY');
el('tab-A').listeners.click();record('Return A saved ISO','ISO');
el('projection').value='YZ';el('projection').listeners.input();record('A changes to YZ','YZ');
console.log(JSON.stringify(observations,null,2));
for(const o of observations) {
  assert.equal(o.result,o.expected,o.stage+' actual evidence projection');
  assert.equal(o.selector,o.expected,o.stage+' selector');
  assert.equal(o.mountedProjection,o.expected,o.stage+' mounted scene');
  assert(o.heading.includes('Evidence projection · '+o.expected),o.stage+' heading');
  assert.equal(o.badge,'SVG evidence view · '+o.expected,o.stage+' badge must agree with actual active evidence');
}
console.log('Independent actual-app SVG projection/base badge invariant PASS');
