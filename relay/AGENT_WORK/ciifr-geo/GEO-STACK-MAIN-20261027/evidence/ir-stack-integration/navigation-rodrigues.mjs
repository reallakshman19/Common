import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import * as THREE from '../geo-navigation-work/prototypes/ciifr-map/vendor/three-0.160.0/three.module.min.js';
const source=process.env.REVIEW_NAV_SOURCE||new URL('./received-7ad4/workbench3d/viewer/workbench-navigation-controls.js',import.meta.url);
const {createWorkbenchNavigationControls}=await import(typeof source==='string'?pathToFileURL(source):source);
const vector=(a,b,fn)=>a.map((v,i)=>fn(v,b[i]));
const add=(a,b)=>vector(a,b,(x,y)=>x+y),sub=(a,b)=>vector(a,b,(x,y)=>x-y);
const scale=(a,k)=>a.map(v=>v*k),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function rotate(v,axis,theta) {
  return add(add(scale(v,Math.cos(theta)),scale(cross(axis,v),Math.sin(theta))),scale(axis,dot(axis,v)*(1-Math.cos(theta))));
}
const baseline=process.env.REVIEW_NAV_BASELINE==='1';
const axes=baseline?['Y','Z']:['X','Y','Z'];
const pivots=baseline?[null]:[null,[438023.221,-1139222.202,1184.15]];
let cases=0,maxError=0;
for(const axis of axes)for(const selectedPivot of pivots)for(const theta of [.2,-.35,Math.PI/2]) {
  const target=[438000,-1139000,1000],position=[439320,-1138511,2553];
  const camera=new THREE.PerspectiveCamera(55,1.7,.1,10000000);
  camera.position.set(...position);camera.up.set(...['X','Y','Z'].map(k=>Number(k===axis)));
  const dom={clientHeight:700,ownerDocument:{defaultView:{addEventListener(){},removeEventListener(){}}},addEventListener(){},removeEventListener(){}};
  const c=createWorkbenchNavigationControls({THREE,getCamera:()=>camera,dom,getVerticalAxis:()=>axis,onChange(){},onGestureStart(){},onGestureEnd(){}});
  c.setViewInstant(new THREE.Vector3(...position),new THREE.Vector3(...target));
  c.setPivot(selectedPivot?new THREE.Vector3(...selectedPivot):null);
  const before=camera.position.toArray(),pivot=selectedPivot||target;
  assert(Math.hypot(...sub(before,position))<1e-7,'setViewInstant must preserve the requested camera position for '+axis);
  const unit=['X','Y','Z'].map(k=>Number(k===axis));
  const expected=add(pivot,rotate(sub(before,pivot),unit,-theta));
  c.orbitBy(theta,0);
  const actual=camera.position.toArray(),error=Math.hypot(...sub(actual,expected));
  maxError=Math.max(maxError,error);
  assert(error<1e-7,axis+' pivot='+!!selectedPivot+' angle='+theta+' expected='+expected+' actual='+actual+' error='+error);
  assert(Math.hypot(...sub(c.target.toArray(),pivot))<1e-7,'orbit center must equal selected pivot or existing model center');
  assert(Math.abs(Math.hypot(...sub(actual,pivot))-Math.hypot(...sub(before,pivot)))<1e-7,'orbit preserves radius');
  c.dispose();cases++;
}
console.log(JSON.stringify({status:'PASS',oracle:'independent Rodrigues axis rotation',baselineUnchangedYZ:baseline,cases,maxError}));
