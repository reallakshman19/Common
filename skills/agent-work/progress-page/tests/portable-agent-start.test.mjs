import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { agentStartModel, agentStartText, agentStartTaskText, agentStartHref } from '../viewer/agent-start.js';
import { wbsGroups } from '../viewer/progress.js';
import { checkpointModel, cycleSource, cycleSummary } from '../viewer/checkpoint.js';
import { onboardingModel } from '../viewer/onboarding.js';
import { HOME_VIEWS, CONTINUITY_VIEWS, CONTINUITY_SUBTABS, PRIMARY_TABS, primaryTabActive } from '../viewer/lifecycle.js';

const gh = 'https://github.com/example/work/issues/';
const project = {
  index: {
    project: {key:'demo',title:'Demo',aim:'Deliver a reviewed, runnable result',aimSrc:gh+'1'},
    revisions:[{id:'R1',status:'current'}],
    chats:{builder:{label:'Builder',id8:'abcd1234'},reviewer:{label:'Reviewer',id8:'dcba4321'}},
    groups:{'demo-onboarding':{title:'Onboarding',order:1}},
    milestones:{
      M1:{wbs:'1.1',name:'Scoped work',full:'Original bounded purpose and checked deliverable',order:1,cap:'NOT_DEMONSTRATED',
        canDo:'Only synthetic checks; Writer remains HOLD.',capSrc:gh+'2'},
      M2:{wbs:'2.1',name:'Other work',order:2}
    }
  },
  cards: {
    first:{milestone:'M1',group:'demo-onboarding',label:'First task',state:'VERIFIED',
      who:{chat:'builder',role:'builder'},now:'Evidence recorded, real trial still HOLD',
      next:{actor:'Oracle',text:'Inspect fixture witness'},src:gh+'11',
      refs:[{u:gh+'12',l:'Contrary observation',k:'issue'}]},
    second:{milestone:'M1',group:'demo-onboarding',label:'Second task',state:'BLOCKED',
      who:{chat:'reviewer',role:'reviewer'},now:'Independent second task is BLOCKED',
      next:{actor:'Reviewer',text:'Review failed case'},src:gh+'21'},
    foreign:{milestone:'M2',label:'Unrelated task',state:'IN_PROGRESS',src:gh+'31'},
    closed:{milestone:'M1',label:'Old superseded task',state:'VERIFIED',closed:true,src:gh+'41'}
  },fixtures:{repository:[],pending:[]}
};
const initial=JSON.stringify(project);
const family=wbsGroups(project.index).find(x=>x.key==='wbs:1');
const opts={family,step:'M1',revision:'R1'};

test('two cards have distinct task packets and a complete independent milestone export',()=>{
  const a=agentStartModel(project,{...opts,cardId:'first'});
  const b=agentStartModel(project,{...opts,cardId:'second'});
  assert.equal(a.selected.id,'first');assert.equal(b.selected.id,'second');
  assert.equal(a.selected.recipient,'Builder · abcd1234');
  assert.equal(a.work.length,2,'related records remain visible');
  const x=agentStartTaskText(a),y=agentStartTaskText(b);
  assert.notEqual(x,y);assert.match(x,/Task ID: first/);
  assert.match(x,/not an acknowledged assignment/);
  assert.match(x,/NOT_RECORDED/);
  assert.match(x,/Writer remains HOLD/);
  assert.match(x,/Contrary observation/);
  assert.ok(x.includes(gh+'11')&&x.includes(gh+'12'));
  assert.ok(!x.includes('Independent second task is BLOCKED'));
  assert.ok(!x.includes('Task ID: second'));
  assert.match(y,/Task ID: second/);
  const all=agentStartText(a);
  assert.match(all,/WORK ITEM first/);assert.match(all,/WORK ITEM second/);
  assert.equal(JSON.stringify(project),initial,'view selection cannot write task state');
});
test('wrong-milestone, unknown and closed tasks cannot select or export another card',()=>{
  for(const id of ['foreign','missing','closed']){
    const m=agentStartModel(project,{...opts,cardId:id});
    assert.equal(m.selectionError,true,id);
    assert.equal(m.selected,null,id);
    assert.equal(agentStartTaskText(m),null,id);
  }
  const legacy=agentStartModel(project,opts);
  assert.equal(legacy.mode,'step');assert.equal(legacy.selected,null);
  assert.match(agentStartText(legacy),/WORK ITEM second/);
});
test('legacy URL remains and selected task segment is encoded',()=>{
  assert.equal(agentStartHref('demo','R1','wbs:1','M1'),'#/demo/start/R1/wbs%3A1/M1');
  assert.equal(agentStartHref('demo','R1','wbs:1','M1','first/task'),
    '#/demo/start/R1/wbs%3A1/M1/first%2Ftask');
});
test('malformed and unknown-project task URLs fail without fallback',()=>{
  const app=readFileSync(new URL('../viewer/app.js',import.meta.url),'utf8');
  const begin=app.indexOf('function route()'),end=app.indexOf('// An older revision');
  assert.ok(begin>=0 && end>begin);
  const source=app.slice(begin,end);
  const run=hash=>runInNewContext(source+'\nroute();',{
    hash,state:{projects:[{key:'demo'}],data:{demo:project}},
    VIEWS:['start','progress'],isActive:()=>true
  });
  for(const hash of ['#/unknown/start/R1/wbs%3A1/M1/first',
    '#/__proto__/start/R1/wbs%3A1/M1/first',
    '#/demo/start/R1/wbs%3A1/M1/%ZZ',
    '#/demo/start/R1/wbs%3A1/M1/first/extra',
    '#/demo/start/R1/wbs%3A1/M1/']){
    const route=run(hash);assert.equal(route.key,null,hash);
    assert.match(route.routeError,/No (?:project or )?task was substituted/);
  }
  const valid=run('#/demo/start/R1/wbs%3A1/M1/first');
  assert.equal(valid.key,'demo');assert.equal(valid.cardId,'first');
  assert.equal(valid.routeError,null);
  const older=run('#/demo/start/R1/wbs%3A1/M1');
  assert.equal(older.key,'demo');assert.equal(older.routeError,false);
});
test('onboarding stays bound to explicitly chosen card and recipient',()=>{
  assert.equal(onboardingModel(project,{cardId:'second'}).cardId,'second');
  assert.equal(onboardingModel(project,{cardId:'first'}).cardId,'first');
  assert.equal(onboardingModel(project,{cardId:'foreign'}),null);
  assert.equal(onboardingModel(project,{cardId:'missing'}),null);
});

test('all projects use recorded workstream purpose; central navigation retains legacy routes',()=>{
  const first=agentStartModel(project).choices.find(g=>g.key==='wbs:1');
  assert.equal(first.title,'Scoped work');
  assert.equal(first.description,'Original bounded purpose and checked deliverable');
  assert.deepEqual(PRIMARY_TABS.map(([id])=>id),['home','progress','continuity']);
  assert.deepEqual(CONTINUITY_SUBTABS.map(([id])=>id),
    ['continuity','start','oracle-continuity','home-risks','fixtures']);
  assert.deepEqual(CONTINUITY_VIEWS,CONTINUITY_SUBTABS.map(([id])=>id));
  assert.ok(HOME_VIEWS.includes('actions') && HOME_VIEWS.includes('timeline'));
  for(const route of ['start','oracle-continuity','home-risks','fixtures']){
    assert.equal(primaryTabActive('continuity',route),true,route);
    assert.equal(primaryTabActive('home',route),false,route);
  }
  assert.equal(primaryTabActive('home','home'),true);
  assert.equal(primaryTabActive('progress','progress'),true);
  assert.equal(JSON.stringify(project),initial,'navigation is a read-only view');
});

test('portable shell keeps one header and breakpoint discipline without an agent workflow change',()=>{
  const life=readFileSync(new URL('../viewer/lifecycle.js',import.meta.url),'utf8');
  const app=readFileSync(new URL('../viewer/app.js',import.meta.url),'utf8');
  const css=readFileSync(new URL('../viewer/viewer.css',import.meta.url),'utf8');
  const home=readFileSync(new URL('../viewer/actions.js',import.meta.url),'utf8');
  assert.doesNotMatch(life,/if\s*\(c\.view\s*===\s*'start'\)/);
  assert.match(life,/const brief = el\('details', 'project-brief'\)/);
  assert.match(home,/home-owner-aim/);
  assert.doesNotMatch(app,/route\(\)\.v\s*!==\s*'start'/);
  assert.doesNotMatch(css,/main:has\(\.agent-start\)/);
  assert.match(css,/html\{scrollbar-gutter:stable\}/);
  assert.match(css,/@media\(min-width:1100px\) and \(max-width:1279px\)/);
  assert.match(css,/\.views\{flex-wrap:nowrap;overflow-x:auto/);
  assert.equal(JSON.stringify(project),initial);
});

test('portable checkpoint uses existing evidence and never invents native Cycle assignments',()=>{
  const before=JSON.stringify(project);
  const m=checkpointModel(project,{pageFetch:{status:'ok',observedAt:'2026-10-27T18:00:00Z'}});
  assert.equal(m.scope,'Project');
  assert.equal(m.cycle.status,'UNMAPPED');
  assert.equal(m.last.state,'BLOCKED');
  assert.ok(m.aimSource);
  assert.equal(m.pageFetch.status,'ok');
  const family=wbsGroups(project.index).find(g=>g.key==='wbs:1');
  const w=checkpointModel(project,{family});
  assert.equal(w.purpose,'Original bounded purpose and checked deliverable');
  assert.equal(w.cycle.status,'OUT_OF_SCOPE');
  assert.equal(JSON.stringify(project),before);
});
test('canonical source mapping fails closed across project, inactive and unrelated WBS',()=>{
  const b={pageProject:'demo',project:'demo',scope:'wbs:1',
    url:'https://raw.githubusercontent.com/reallakshman19/Common/main/oracle-cycles/demo/CURRENT.json'};
  assert.equal(cycleSource(b,'demo'),b.url);
  assert.equal(cycleSource(b,'other'),null);
  assert.equal(cycleSource({...b,url:b.url.replace('/main/','/branch/')},'demo'),null);
  const c={schema:'oracle-cycle-current/v1',project:'demo',mode:'standalone',activation:'ACTIVE',revision:2,
    progress_projection:{repository:'reallakshman19/progress-page',project_key:'demo',publication_status:'PROGRESS_UPDATE_PENDING'},
    next:{recipient_role:'owner',status:'AWAIT_OWNER',instruction:'Review native result',evidence_ref:'https://github.com/example/r/issues/1'}};
  assert.equal(cycleSummary(c,b,'demo').actor,'owner');
  assert.equal(cycleSummary({...c,project:'wrong'},b,'demo').status,'INVALID');
  assert.equal(cycleSummary({...c,activation:'DISABLED'},b,'demo').status,'INACTIVE');
  const one=wbsGroups(project.index).find(g=>g.key==='wbs:1');
  const two=wbsGroups(project.index).find(g=>g.key==='wbs:2');
  assert.equal(checkpointModel(project,{family:one,cycle:c,binding:b}).cycle.status,'OBSERVED');
  assert.equal(checkpointModel(project,{family:two,cycle:c,binding:b}).cycle.status,'OUT_OF_SCOPE');
});
