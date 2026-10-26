import {readFileSync} from 'node:fs';
import {projectWorkbenchPoint} from '../geo-multibase-work/workbench3d/viewer/workbench-viewer.js';
import * as THREE from '../geo-multibase-work/prototypes/ciifr-map/vendor/three-0.160.0/three.module.min.js';
const source=readFileSync(process.env.NATIVE_VIEWER_METHOD_SOURCE || new URL('../geo-multibase-work/workbench3d/viewer/workbench-viewer.js',import.meta.url),'utf8');
const at=source.indexOf('    projectPointForPane(xyz, pane ='),open=source.indexOf('{',at);let depth=1,end=open+1;
while(depth&&end<source.length){if(source[end]==='{')depth++;if(source[end]==='}')depth--;end++;}
const method=source.slice(at,end),host={clientWidth:1200,clientHeight:600},origin=new THREE.Vector3();
const camera=new THREE.PerspectiveCamera(55,2,.1,10000);camera.position.set(0,0,100);camera.lookAt(0,0,0);camera.updateMatrixWorld();
const fn=new Function('THREE','camera','sceneOrigin','host','mode','projectWorkbenchPoint','let projectionCamera=null;return ({'+method+'}).projectPointForPane;')(THREE,camera,origin,host,'side-by-side',projectWorkbenchPoint);
const xyz=[10,0,0],actual=fn(xyz,'source');
const correct=camera.clone();correct.aspect=1;correct.updateProjectionMatrix();correct.updateMatrixWorld();
const ndc=new THREE.Vector3(...xyz).project(correct),expected={x:(ndc.x+1)/2*600,y:(1-ndc.y)/2*600};
console.log(JSON.stringify({claim:'split HUD uses current-pane aspect before asynchronous render',actual,expected,pixelError:Math.hypot(actual.x-expected.x,actual.y-expected.y)}));
if(Math.abs(actual.x-expected.x)>1e-8)process.exitCode=1;
