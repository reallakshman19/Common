import assert from 'node:assert/strict';
import {searchResolution} from '../geo-multibase-work/prototypes/ciifr-map/resolution-search.js';
const I=[[1,0,0],[0,1,0],[0,0,1]], sum=a=>a.reduce((s,x)=>s+x,0), close=(a,b)=>Math.abs(a-b)<1e-7;
function fixture(fixed, options, pins={}) {
 const nodes=[],targets=[],unique=[],groups=[];
 const pair=(group,source,target,d)=>{const s=[source*100,source*30,source*-10],t=s.map((x,i)=>x-d[i]);
  if(!nodes.some(n=>n.id===String(source)))nodes.push({id:String(source),xyz:s,component:0});
  targets.push({id:target,xyz:t,component:0});
  return {key:target,source:String(source),target,targetKey:target,groupKey:group,sourceComponent:0,targetComponent:0};};
 fixed.forEach((d,i)=>unique.push(pair('u'+i,i,'u'+i,d)));
 options.forEach((ds,i)=>groups.push({key:'g'+i,source:String(i+fixed.length),options:ds.map((d,j)=>pair('g'+i,i+fixed.length,'g'+i+'o'+j,d))}));
 return {snapshotId:'ir-fixture',source:{nodeIndex:new Map(nodes.map(n=>[n.id,n]))},target:{nodeIndex:new Map(targets.map(n=>[n.id,n]))},
  union:{unique,groups},pins,policy:{mode:'TRANSLATION',rotation:I},fixed,options};
}
function allChoices(input,at=0,vector=[]) {if(at===input.options.length)return[vector];return input.options[at].flatMap((_,j)=>allChoices(input,at+1,[...vector,j]));}
function scores(input,v) {const d=[...input.fixed,...v.map((j,i)=>input.options[i][j])];const avg=[0,1,2].map(i=>sum(d.map(x=>x[i]))/d.length);
 const errors=d.map(x=>sum(x.map((c,i)=>Math.abs(avg[i]-c))));return {e:v.map((_,i)=>sum(errors.filter((_,j)=>j!==input.fixed.length+i))),total:sum(errors)};}
function expected(input) {const table=allChoices(input).map(v=>({v,...scores(input,v)}));let r=table.filter(row=>input.union.groups.every((g,i)=>!input.pins[g.key]||g.options[row.v[i]].key===input.pins[g.key]));
 r=r.map(row=>{const regrets=row.v.map((j,i)=>row.e[i]-Math.min(...table.filter(t=>t.v.every((k,g)=>g===i||k===row.v[g])).map(t=>t.e[i]))).filter((_,i)=>!input.pins['g'+i]);return {...row,rank:[Math.max(0,...regrets),sum(regrets),row.total]};});
 for(let s=0;s<3;s++){const min=Math.min(...r.map(x=>x.rank[s]));r=r.filter(x=>x.rank[s]<=min+1e-6);}
 return r.sort((a,b)=>JSON.stringify(a.v).localeCompare(JSON.stringify(b.v)))[0];}
const cycle=fixture([[-8,-2,-3]],[[[-5,-8,-7],[-3,6,5]],[[4,-6,4],[6,2,1]]]);
const actual=await searchResolution(cycle), ex=expected(cycle);
assert.equal(actual.status,'COUPLED_COMPROMISE');assert.deepEqual(actual.chosen.choices,['g0o0','g1o0']);
assert(close(actual.recommendations[1].regret,2/3));assert.equal(actual.recommendations[1].recommendedPairKey,'g1o1');
let state=123456789;const rand=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state%41-20;};
for(let test=0;test<120;test++){
 const groups=2+test%2, fixed=Array.from({length:1+test%2},()=>[rand(),rand(),rand()]);
 const opts=Array.from({length:groups},()=>Array.from({length:2},()=>[rand(),rand(),rand()]));
 const f=fixture(fixed,opts,test%4===0?{g0:'g0o1'}:{}), e=expected(f), a=await searchResolution(f);
 const v=a.chosen.choices.map(x=>Number(x.slice(-1)));
 assert.deepEqual(v,e.v,'fixture '+test+' expected independent minmax selection');
 const own=scores(f,v);assert(close(a.chosen.total,own.total));
 a.chosen.scores.forEach((x,i)=>assert(close(x,own.e[i]),'whole group excluded '+test));
 assert.equal(a.exact,true);assert.equal(a.completeSlices,true);
}
const partial=await searchResolution(cycle,{maxCases:1});assert.equal(partial.exact,false);assert.equal(partial.status,'BEST_FOUND_PARTIAL');
assert(partial.recommendations.every(r=>r.regretBoundKind==='LOWER_BOUND'));
console.log(JSON.stringify({cycleChoice:actual.chosen.choices,cycleStatus:actual.status,cycleRegrets:actual.recommendations.map(r=>r.regret),independentRandomCases:120,partialStatus:partial.status}));
const rotated=fixture([[-8,-2,-3]],[[[-5,-8,-7],[-3,6,5]],[[4,-6,4],[6,2,1]]]);
const R=[[0,-1,0],[1,0,0],[0,0,1]];
for(const p of [...rotated.union.unique,...rotated.union.groups.flatMap(g=>g.options)]) {
 const s=rotated.source.nodeIndex.get(p.source).xyz,t=rotated.target.nodeIndex.get(p.target).xyz;
 const required=s.map((x,i)=>x-t[i]); const rs=R.map(row=>sum(row.map((x,i)=>x*s[i])));
 rotated.target.nodeIndex.get(p.target).xyz=rs.map((x,i)=>x-required[i]);
}
rotated.policy.rotation=R;
const ar=await searchResolution(rotated),er=expected(rotated);
assert.deepEqual(ar.chosen.choices,er.v.map((j,i)=>'g'+i+'o'+j));
const own=scores(rotated,er.v);ar.chosen.scores.forEach((x,i)=>assert(close(x,own.e[i])));
console.log(JSON.stringify({rotatedRetainedOrientation:'PASS',choices:ar.chosen.choices,scores:ar.chosen.scores}));
