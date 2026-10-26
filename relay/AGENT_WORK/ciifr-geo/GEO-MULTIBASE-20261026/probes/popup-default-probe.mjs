import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const path=process.env.REVIEW_VIEWPORT_SOURCE || '/workspace/scratch/ca71d2f89cf7/geo-multibase-work/prototypes/ciifr-map/review-viewport.js';
const {setupReviewViewport}=await import(pathToFileURL(path));
function shell(native=false){
 const elements=new Map(),events={},bounds={left:100,top:200,width:1400,height:936};
 const number=(v,fallback)=>v===''||v==null?fallback:Number.parseFloat(v);
 const el=id=>{if(elements.has(id))return elements.get(id);const node={id,hidden:false,style:{},listeners:{},attrs:{},
  classList:{toggle(){}},addEventListener(k,f){this.listeners[k]=f;},setAttribute(k,v){this.attrs[k]=v;},focus(){},setPointerCapture(){},
  getBoundingClientRect(){if(id==='review-surface')return bounds;const s=this.style;return{left:bounds.left+number(s.left,526),top:bounds.top+number(s.top,-8),width:Math.min(number(s.width,850),number(s.maxWidth,Infinity)),height:Math.min(number(s.height,920),number(s.maxHeight,Infinity))};}};elements.set(id,node);return node;};
 const doc={body:el('body'),addEventListener:(k,f)=>events[k]=f};
 el('review-surface').requestFullscreen=async()=>{if(native)doc.fullscreenElement=el('review-surface');else throw Error('simulated native refusal');};
 doc.exitFullscreen=async()=>{throw Error('simulated exit refusal');};
 const api=setupReviewViewport({byId:el,documentRef:doc});return{el,doc,events,api,bounds};
}
const h=shell();h.el('toggle-fullscreen').listeners.click();await Promise.resolve();await Promise.resolve();
const box=h.el('ledger-panel').getBoundingClientRect(),left=box.left-h.bounds.left,top=box.top-h.bounds.top;
console.log(JSON.stringify({fixture:'controlled same measured936px surface / inherited920px popup',popupHeight:box.height,ratio:box.height/h.bounds.height,left,top,right:h.bounds.width-left-box.width,bottom:h.bounds.height-top-box.height,label:h.el('toggle-fullscreen').textContent}));
assert(box.height<=h.bounds.height*.45+1,'default popup must leave a majority of drawing visible');
assert(left>=0&&top>=0&&left+box.width<=h.bounds.width&&top+box.height<=h.bounds.height);
assert.equal(h.el('toggle-fullscreen').textContent,'Exit expanded view');
h.el('close-ledger').listeners.click();assert.equal(h.el('ledger-panel').hidden,true);h.el('show-ledger').listeners.click();assert.equal(h.el('ledger-panel').hidden,false);
const n=shell(true);n.el('toggle-fullscreen').listeners.click();await Promise.resolve();await Promise.resolve();assert.equal(n.el('toggle-fullscreen').textContent,'Exit fullscreen');
n.el('toggle-fullscreen').listeners.click();await Promise.resolve();await Promise.resolve();assert.equal(n.api.isExpanded(),true);assert.equal(n.el('toggle-fullscreen').textContent,'Exit fullscreen (Esc)');
n.doc.fullscreenElement=null;n.events.fullscreenchange();assert.equal(n.api.isExpanded(),false);assert.equal(n.el('toggle-fullscreen').textContent,'Fullscreen');
console.log(JSON.stringify({defaultPlacement:'PASS',expandedVsNativeLabels:'PASS',closeReopen:'PASS',refusedNativeExitRecovery:'PASS',browserLayoutExecuted:false}));
