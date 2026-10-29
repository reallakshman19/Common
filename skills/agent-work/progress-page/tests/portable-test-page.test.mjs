import assert from 'node:assert/strict';
import test from 'node:test';
import {testPageModel,testPagePacket} from '../viewer/test-page.js';
import {HOME_VIEWS,HOME_SUBTABS} from '../viewer/lifecycle.js';
const SRC='https://github.com/acme/work/issues/12';
const p={index:{project:{key:'demo',aim:'Owner intent',aimSrc:SRC},milestones:{M1:{wbs:'1.1',name:'Step',capSrc:SRC}}},
cards:{one:{milestone:'M1',label:'One task',src:SRC}},
audit:{events:[{id:'R-1',card:'one',kind:'UPDATE',at:'2026-10-29T01:00:00Z',
source:SRC,summary:'Original issue linked; no PASS',rev:'R1',actor:'Page writer'}]}};
test('project-level optional test route does not modify Page or post a live event',()=>{
 assert.ok(HOME_VIEWS.includes('test')&&HOME_SUBTABS.some(([id])=>id==='test'));
 const before=JSON.stringify(p),m=testPageModel(p,{cardId:'one',mode:'ACTION',needsOwner:true});
 assert.equal(m.stage,'NEEDS_OWNER');
 assert.ok(m.badges.some(b=>b.id==='demo/WBS/1.1'));
 assert.match(testPagePacket(m),/DEMONSTRATION ONLY/);
 assert.doesNotMatch(testPagePacket(m),/CYCLE_TIMELINE_CARD v2/);
 assert.equal(JSON.stringify(p),before);
});
test('Info handoff remains simulated; source-derived Info comes from the existing audit',()=>{
 const info=testPageModel(p,{mode:'INFO',cardId:'one'});
 assert.equal(info.stage,'HANDED_OFF');assert.match(info.description,/review remains open/);
 const auto=testPageModel(p,{mode:'INFO_AUTO',cardId:'one'});
 assert.equal(auto.first.auditId,'R-1');
 assert.match(testPagePacket(auto),/R-1/);
});
test('missing project WBS and audit show no fake Info event',()=>{
 const m=testPageModel({index:{project:{key:'empty'}},cards:{}},{mode:'INFO_AUTO'});
 assert.equal(m.first,null);assert.equal(m.canCopy,false);assert.equal(m.wbs,'UNSCOPED');
});
