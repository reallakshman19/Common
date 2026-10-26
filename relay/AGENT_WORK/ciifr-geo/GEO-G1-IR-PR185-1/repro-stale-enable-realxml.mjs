import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {createRequire} from 'node:module';
import {createGeoViewerBridge} from './candidate/prototypes/ciifr-map/geo-viewer-bridge.js';
import {createPreviewSession} from './candidate/prototypes/ciifr-map/compare.js';
import {readXmlGraph} from './candidate/prototypes/ciifr-map/xml-intake.js';
import {exportPreview} from './candidate/prototypes/ciifr-map/evidence.js';

// Executes exact app.js + real session/intake/scene/bridge; only DOM rendering and
// WebGL factory are synthetic. This is explicitly NOT served-browser execution.
const runtime=process.env.CIIFR_TEST_RUNTIME||'/workspace/scratch/ca71d2f89cf7/map-test-runtime';
const {DOMParser}=createRequire(runtime+'/package.json')('@xmldom/xmldom');
const session=createPreviewSession({read:(bytes,options)=>readXmlGraph(bytes,{...options,cryptoRef:webcrypto,
 parser:new DOMParser({onError:(level,message)=>{throw Error(level+':'+message);}})})});
for(const [side,name]of [['SOURCE','S1-F05.xml'],['TARGET','S1-R4.xml']])
 await session.load(side,new Uint8Array(readFileSync(new URL('./candidate/prototypes/ciifr-map/tests/fixtures/'+name,import.meta.url))),name);
for(const n of ['3790','3830','3840'])session.addAnchor(n,n);
const elements=new Map();
const el=id=>elements.get(id)||elements.set(id,{id,hidden:false,disabled:false,textContent:'',
 value:id==='projection'?'XZ':id==='viewer-layout'?'overlay':'100',listeners:{},
 classList:{toggle(){}},replaceChildren(){},addEventListener(k,f){this.listeners[k]=f;}}).get(id);
const fifo=process.argv.includes('--fifo');
let bridge,releaseOld,releaseNew,calls=0;const disposed=[];
const makeViewer=async()=>{
 const id=++calls;
 if(id===1)await new Promise(r=>releaseOld=r);
 if(id===2&&fifo)await new Promise(r=>releaseNew=r);
 return {setModels(){},setMode(){},fitAll(){},getStateSnapshot(){return {runtimeRevision:1};},
 toggleCameraType(){},setStandardView(){},setSelection(){},dispose(){disposed.push(id);}};
};
const context=vm.createContext({document:{getElementById:el,querySelectorAll:()=>[]},window:{addEventListener(){}},console,setTimeout});
const modules={
 './compare.js':{createPreviewSession:()=>session},'./evidence.js':{exportPreview},
 './view.js':{graphInfo(){},renderAnchors(){},renderRows(){},selectedDetails(){return '';},mountScene(){return {}; }},
 './geo-viewer-bridge.js':{createGeoViewerBridge:opts=>bridge=createGeoViewerBridge({...opts,makeViewer})},
};
const app=new vm.SourceTextModule(readFileSync(new URL('./candidate/prototypes/ciifr-map/app.js',import.meta.url),'utf8'),{context});
await app.link(spec=>{const e=modules[spec];return new vm.SyntheticModule(Object.keys(e),function(){for(const [k,v]of Object.entries(e))this.setExport(k,v);},{context});});
await app.evaluate();
el('run').listeners.click();
const oldEnable=el('toggle-gpu').listeners.click();
el('projection').value='XY';el('projection').listeners.input();
el('run').listeners.click();
const newEnable=el('toggle-gpu').listeners.click();
if(fifo){
 // Both await the same newly loaded module in production; release in FIFO order
 // in one turn so both real bridge continuations queue before old app cleanup.
 releaseOld();releaseNew();await Promise.all([oldEnable,newEnable]);
 console.log('FIFO_COMPLETION',{active:bridge.isActive(),disposed:[...disposed],projection:session.current().projection,label:el('toggle-gpu').textContent});
 assert.equal(bridge.isActive(),false);assert.deepEqual(disposed,[1,2]);
 console.log('DEFECT_REPRODUCED: FIFO old/new startup completion also disposes current viewer #2');
}else{
await newEnable;
assert.equal(bridge.isActive(),true);assert.equal(el('gpu-host').hidden,false);
const beforeExports=['json','csv','svg'].map(k=>exportPreview(session,k));
console.log('BEFORE_OLD_COMPLETION',{active:bridge.isActive(),disposed:[...disposed],projection:session.current().projection,label:el('toggle-gpu').textContent});
releaseOld();await oldEnable;
console.log('AFTER_OLD_COMPLETION',{active:bridge.isActive(),disposed:[...disposed],projection:session.current().projection,label:el('toggle-gpu').textContent});
assert.equal(bridge.isActive(),false);assert.deepEqual(disposed,[1,2]);
assert.deepEqual(['json','csv','svg'].map(k=>exportPreview(session,k)),beforeExports);
console.log('DEFECT_REPRODUCED: old app continuation disposed newer viewer #2; current exports remain unchanged');
}
