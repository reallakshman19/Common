import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const root = new URL('../geo-vnext-tab-20261027/', import.meta.url);
const read = p => fs.readFile(new URL(p, root), 'utf8');
const geoPath = 'tabs/cii-workspace/cii-fnr-vnext/ui/geo-tab.js';
const actual = await import(new URL(geoPath, root));
const source = await read(geoPath);
const observations=[];
function checkModule(module) {
 for (const prefix of ['', '/XML_Compare_Utilities', '/a/docs/deep']) for (const mirror of ['', '/docs']) {
  const base=`https://review.invalid${prefix}${mirror}/tabs/cii-workspace/cii-fnr-vnext/ui/geo-tab.js`;
  assert.equal(module.geometryWorkbenchUrl(base), `https://review.invalid${prefix}/prototypes/ciifr-map/index.html`);
 }
 let navigations=0,src=null;
 const frame={getAttribute:()=>src,setAttribute:(k,v)=>{assert.equal(k,'src');src=v;navigations++;}};
 const link={};const panel={querySelector:s=>s.includes('open')?link:frame};
 module.renderGeometryTab(panel,false);assert.equal(navigations,0);
 for(let i=0;i<20;i++){module.renderGeometryTab(panel,true);module.renderGeometryTab(panel,false);}
 assert.equal(navigations,1);assert.equal(link.href,src);assert.equal(panel.hidden,true);
 return {navigations,url:src,transitions:40};
}
observations.push({check:'module-routes-and-retention',...checkModule(actual)});
for (const [name,bad] of [
 ['wrong-docs-route',source.replace('../../../../../prototypes/','../../../../prototypes/')],
 ['reload-on-return',source.replace("if (!frame.getAttribute('src')) frame.setAttribute('src', url);","frame.setAttribute('src', url);")]
]){
 assert.notEqual(bad,source);
 const substituted=bad.replaceAll('import.meta.url',JSON.stringify(pathToFileURL(new URL(geoPath,root).pathname).href));
 const module=await import('data:text/javascript;base64,'+Buffer.from(substituted).toString('base64'));
 let rejected=false;try{checkModule(module);}catch(e){rejected=true;observations.push({check:'seeded-defect',defect:name,rejected:true,error:e.message});}
 assert.equal(rejected,true,name+' must be rejected');
}
const {createTestDom,MockElement}=await import(new URL('tests/helpers/vnext-dom-env.mjs',root));
const dom=createTestDom();
const panel=new MockElement('section',{'data-ciifr-geo-panel':''});
const frame=new MockElement('iframe',{'data-ciifr-geo-frame':''});
const link=new MockElement('a',{'data-ciifr-geo-open':''});
const button=new MockElement('button',{'data-tab':'CIIFR_GEO'});
const invalid=new MockElement('button',{'data-tab':'NOT_A_REAL_TAB'});
const child=new MockElement('span');button.append(child);panel.append(link,frame);dom.root.append(button,panel,invalid);
let count=0;const setter=frame.setAttribute.bind(frame);frame.setAttribute=(k,v)=>{if(k==='src')count++;return setter(k,v);};
await import(new URL('tabs/cii-workspace/cii-fnr-vnext/ui/app.js?independent=1',root));
assert.equal(panel.hidden,true);assert.equal(frame.getAttribute('src'),null);
await invalid.click();assert.equal(dom.tabNormal.getAttribute('aria-selected'),'true');
await child.click();assert.equal(panel.hidden,false);assert.equal(button.getAttribute('aria-selected'),'true');
for (const tab of ['NORMAL','GEOMETRY','LINE_NODE','CONFIG','CIIFR_GEO','CIIFR_GEO','NORMAL','CIIFR_GEO']) {
 await dom.root.querySelector(`[data-tab="${tab}"]`).click();
 assert.equal(panel.hidden,tab!=='CIIFR_GEO');
 assert.equal(dom.root.querySelector('[data-config-area]').hidden,tab!=='CONFIG');
 assert.equal(dom.root.querySelector('[data-workspace]').hidden,tab==='CONFIG'||tab==='CIIFR_GEO');
 assert.equal(dom.root.querySelectorAll('[aria-selected="true"]').length,1);
}
assert.equal(count,1);assert.equal(dom.btnExport.disabled,true);
observations.push({check:'actual-app-alternate-transitions',navigationCount:count,unknownTabIgnored:true,nestedClick:true,panelsExclusive:true});
for(const mirror of ['','docs/']){
 const ui=await read(mirror+'tabs/cii-workspace/cii-workspace-find-replace-ui.js');
 const markup=await read(mirror+'tabs/cii-workspace/cii-workspace-find-replace.js');
 assert.match(markup,/<iframe data-ciifr-vnext-frame[^>]*allow="fullscreen" allowfullscreen/);
 assert.match(ui,/if \(showingVnext && !vnextFrame.hasAttribute\('src'\)\) vnextFrame.src = vnextUrl/);
 for(const prefix of ['','/XML_Compare_Utilities']){
  const url=`https://review.invalid${prefix}/${mirror}tabs/cii-workspace/cii-workspace-find-replace-ui.js`;
  const relative=mirror?'../../cii-fnr-vnext.html':'../../docs/cii-fnr-vnext.html';
  assert.equal(new URL(relative,url).href,`https://review.invalid${prefix}/docs/cii-fnr-vnext.html`);
 }
}
console.log(JSON.stringify({status:'PASS',observation:'LOCAL_EXECUTION_CONTROLLED_DOM_NOT_BROWSER',observations},null,2));
