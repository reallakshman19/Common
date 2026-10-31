// Local read-only, full HTTP-served original V14 qualification. Node 22+, no NPM packages.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import net from 'node:net';
import {spawn,execFileSync} from 'node:child_process';
import os from 'node:os';
import crypto from 'node:crypto';
import {independentOracle} from './physical-oracle.mjs';

const PIN='d3fbd4041ef4434b4cf5b3c22459f06167be2729';
const arg=(k)=>{const i=process.argv.indexOf('--'+k);return i<0?null:process.argv[i+1]};
const REQUIRE=(p,m)=>{if(!p)throw Error('QUAL_GATE_'+m)};
const sleep=t=>new Promise(r=>setTimeout(r,t));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const isInside=(root,file)=>{const x=path.relative(root,file);return x===''||(!x.startsWith('..')&&!path.isAbsolute(x))};
function git(repo,...args){return execFileSync('git',['-C',repo,...args],{encoding:'utf8',timeout:15000}).trim()}
function pinnedCheckout(repo){
 const head=git(repo,'rev-parse','HEAD');REQUIRE(head===PIN,'HEAD_MISMATCH');
 REQUIRE(git(repo,'status','--porcelain','--untracked-files=no')==='','TRACKED_TREE_DIRTY');
 const served=['docs/cii-fnr-vnext.html','docs/tabs/cii-workspace/cii-fnr-vnext/ui/app.js',
  ...['cii-index.js','element.js','node.js','panel.js'].map(f=>'docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/'+f)];
 for(const file of served){REQUIRE(fs.existsSync(path.join(repo,file)),'SERVE_MISSING');
  REQUIRE(git(repo,'hash-object',file)===git(repo,'rev-parse','HEAD:'+file),'TRACKED_BLOB_MISMATCH')}
 return {head,servedFileCount:served.length};
}
async function freePort(){const s=net.createServer();await new Promise((ok,no)=>s.once('error',no).listen(0,'127.0.0.1',ok));
 const p=s.address().port;await new Promise(ok=>s.close(ok));return p}
function serverStart(root){const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
 '.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
 const server=http.createServer((req,res)=>{let pathname;
  try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400).end();return}
  const loc=path.resolve(root,'.'+pathname);if(!isInside(root,loc)||!fs.existsSync(loc)||!fs.statSync(loc).isFile()){
   res.writeHead(404).end();return}
  res.writeHead(200,{'Content-Type':types[path.extname(loc)]||'application/octet-stream',
   'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});fs.createReadStream(loc).pipe(res);
 });return server}
function browserExecutable(){
 const explicit=arg('browser');if(explicit)return path.resolve(explicit);
 const base=[process.env['PROGRAMFILES(X86)'],process.env.PROGRAMFILES,process.env.LOCALAPPDATA].filter(Boolean);
 for(const p of base){for(const rel of ['Microsoft/Edge/Application/msedge.exe','Google/Chrome/Application/chrome.exe']){
  const f=path.join(p,rel);if(fs.existsSync(f))return f}}
 if(process.platform==='linux'&&fs.existsSync('/usr/bin/chromium'))return '/usr/bin/chromium';
 throw Error('QUAL_GATE_BROWSER_NOT_FOUND');
}
async function browserStart(exe){const port=await freePort(),dir=fs.mkdtempSync(path.join(os.tmpdir(),'ciifr-p12-browser-'));
 const flags=[`--remote-debugging-port=${port}`,`--user-data-dir=${dir}`,'--headless=new','--no-first-run',
  '--no-default-browser-check','--disable-extensions','--disable-background-networking','about:blank'];
 if(process.platform==='linux')flags.unshift('--no-sandbox','--disable-dev-shm-usage');
 const proc=spawn(exe,flags,{stdio:'ignore'});
 let url=null;for(let i=0;i<90;i++){if(proc.exitCode!==null)break;
  try{const r=await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT',signal:AbortSignal.timeout(1500)});
   if(r.ok){const v=await r.json();url=v.webSocketDebuggerUrl;break}}
  catch{}await sleep(200)}
 REQUIRE(url,'CDP_NOT_AVAILABLE');return {port,dir,proc,url};
}
class CDP{
 constructor(ws){this.ws=new WebSocket(ws);this.next=0;this.pending=new Map();this.events=[];
  this.ws.onmessage=e=>{const d=JSON.parse(e.data);
   if(d.id){const item=this.pending.get(d.id);this.pending.delete(d.id);
    if(item)d.error?item.reject(Error('CDP_'+d.error.message)):item.resolve(d.result)}
   else this.events.push(d)};
 }
 async ready(){if(this.ws.readyState===1)return;await new Promise((ok,no)=>{this.ws.addEventListener('open',ok,{once:true});this.ws.addEventListener('error',no,{once:true})})}
 async send(method,params={}){const id=++this.next;return await new Promise((resolve,reject)=>{
  this.pending.set(id,{resolve,reject});this.ws.send(JSON.stringify({id,method,params}));setTimeout(()=>{
   if(this.pending.has(id)){this.pending.delete(id);reject(Error('CDP_TIMEOUT_'+method))}},20000).unref?.()})}
 async eval(expr){const r=await this.send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});
  REQUIRE(!r.exceptionDetails,'BROWSER_EVALUATION_EXCEPTION');return r.result?.value}
 async wait(expr,delay=250,attempts=100){for(let i=0;i<attempts;i++){
  const v=await this.eval(expr);if(v)return v;await sleep(delay)}throw Error('QUAL_GATE_BROWSER_WAIT_TIMEOUT')}
 close(){this.ws.close()}
}
async function execute(cdp,original,oracle,origin){
 await cdp.send('Page.enable');await cdp.send('Runtime.enable');await cdp.send('Network.enable');
 await cdp.send('Page.navigate',{url:origin+'/docs/cii-fnr-vnext.html'});
 await cdp.wait(`document.readyState === 'complete' && !!document.querySelector('[data-tab="PROPERTY_TRANSFER"]')`,300,80);
 await cdp.eval(`document.querySelector('[data-tab="PROPERTY_TRANSFER"]').click()`);
 await cdp.wait(`document.querySelector('[data-property-transfer-area]')?.hidden === false`);
 const d=await cdp.send('DOM.getDocument',{depth:1,pierce:true});
 const inp=await cdp.send('DOM.querySelector',{nodeId:d.root.nodeId,selector:'[data-pt-file="target"]'});
 REQUIRE(inp.nodeId,'ORIGINAL_FILE_INPUT_ABSENT');
 await cdp.send('DOM.setFileInputFiles',{files:[original],nodeId:inp.nodeId});
 const ingest=await cdp.wait(`(()=>{const s=document.querySelector('[data-pt-status]')?.textContent||'';
  if(s.includes('Input rejected:'))return {rejected:s};
  if(s.includes('Read-only property index ready.'))return {accepted:true};
  return null})()`,200,160);
 if(ingest.rejected){return {accepted:false,diagnostic:'ORIGINAL_INPUT_REJECTED',privateDiagnostic:ingest.rejected}}
 const receipt=await cdp.eval(`({status:document.querySelector('[data-pt-status]')?.textContent,
  file:document.querySelector('[data-pt-file-status="target"]')?.textContent,
  unknown:[...document.querySelectorAll('[data-pt-results] h4')].map(n=>n.textContent),
  noWriter:!document.querySelector('[data-property-transfer-area] [data-apply], [data-property-transfer-area] [data-export]')})`);
 REQUIRE(receipt.file.includes(oracle.private.sha256),'ORIGINAL_BROWSER_HASH_MISMATCH');
 REQUIRE(receipt.file.includes('521 elements'),'ORIGINAL_BROWSER_COUNT_MISMATCH');
 REQUIRE(receipt.unknown.length>=5&&receipt.unknown.every(s=>s.includes('UNKNOWN')),'UNKNOWN_UNREPORTED');
 REQUIRE(receipt.noWriter,'PROPERTY_WRITER_PRESENT');
 const inputs=oracle.private.witnesses.element;
 await cdp.eval(`(()=>{document.querySelector('[data-pt-input="targetFrom"]').value=${JSON.stringify(String(inputs.from))};
  document.querySelector('[data-pt-input="targetTo"]').value=${JSON.stringify(String(inputs.to))};
  document.querySelector('[data-pt-run]').click()})()`);
 const elementRows=await cdp.eval(`(()=>{const s=[...document.querySelectorAll('[data-pt-results] .pt-result')].find(x=>x.querySelector('h3')?.textContent.startsWith('TARGET0 · FROM'));
  return s?[...s.querySelectorAll('tbody tr')].map(tr=>[...tr.querySelectorAll('td')].map(td=>td.textContent)):null})()`);
 REQUIRE(JSON.stringify(elementRows)===JSON.stringify(inputs.expectedRows),'ELEMENT_WITNESS_MISMATCH');
 await cdp.eval(`document.querySelector('[data-pt-mode="NODE"]').click()`);
 const nodes=[];
 for(const item of oracle.private.witnesses.nodes){
  await cdp.eval(`(()=>{document.querySelector('[data-pt-input="targetNode"]').value=${JSON.stringify(String(item.node))};
   document.querySelector('[data-pt-run]').click()})()`);
  const rows=await cdp.eval(`(()=>{const s=[...document.querySelectorAll('[data-pt-results] .pt-result')].find(x=>x.querySelector('h3')?.textContent.startsWith('TARGET0 · Numeric Node'));
   return s?[...s.querySelectorAll('tbody tr')].map(tr=>[...tr.querySelectorAll('td')].map(td=>td.textContent)):null})()`);
  REQUIRE(JSON.stringify(rows)===JSON.stringify(item.expectedRows),'NODE_WITNESS_MISMATCH');
  nodes.push({node:item.node,expectedRows:item.expectedRows,actualRows:rows});
 }
 const exceptionEvents=cdp.events.filter(x=>x.method==='Runtime.exceptionThrown');
 REQUIRE(exceptionEvents.length===0,'BROWSER_PAGE_EXCEPTIONS');
 return {accepted:true,qualificationRows:receipt.unknown.length,elementRows,
  nodes,networkRequests:cdp.events.filter(x=>x.method==='Network.requestWillBeSent').map(x=>x.params.request.url),
  browserStatus:receipt.status,writerAbsent:receipt.noWriter};
}
async function main(){
 const repo=path.resolve(arg('repo')||''),original=path.resolve(arg('original')||'');
 const privateDir=path.resolve(arg('private-dir')||''),publicDir=path.resolve(arg('public-dir')||'');
 REQUIRE(arg('repo')&&arg('original')&&arg('private-dir')&&arg('public-dir'),'REQUIRED_ARGUMENTS');
 REQUIRE(!isInside(repo,original),'PRIVATE_ORIGINAL_INSIDE_SERVED_REPO');
 REQUIRE(fs.existsSync(original),'ORIGINAL_NOT_FOUND');
 fs.mkdirSync(privateDir,{recursive:true});fs.mkdirSync(publicDir,{recursive:true});
 const first=independentOracle(original,arg('expected-sha'));
 fs.writeFileSync(path.join(privateDir,'oracle.json'),JSON.stringify(first.private,null,2)+'\n',{flag:'wx'});
 const prelim={task:'CIIFR-NODE-P1.2-ORIGINAL-V14',candidate:PIN,qualification:'SELF_ASSESSED',
  original:'PRIVATE_VERIFIED',counts:first.public.tallies,mode:'FULL_PINNED_APP',platform:process.platform};
 let browser=null,server=null,cdp=null,priv=null,final={...prelim,status:'NOT_RUN'};
 try{
  const checkout=pinnedCheckout(repo);
  server=serverStart(repo);await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
  const url=`http://127.0.0.1:${server.address().port}`;
  browser=await browserStart(browserExecutable());cdp=new CDP(browser.url);await cdp.ready();
  priv=await execute(cdp,original,first,url);
  REQUIRE(priv.accepted,'ORIGINAL_INPUT_REJECTED');
  REQUIRE(sha(fs.readFileSync(original))===first.private.sha256,'ORIGINAL_CHANGED');
  REQUIRE(git(repo,'rev-parse','HEAD')===PIN&&git(repo,'status','--porcelain','--untracked-files=no')==='','POST_CHECKOUT_CHANGED');
  const requests=priv.networkRequests;
  REQUIRE(requests.every(u=>u.startsWith(url+'/')),'EXTERNAL_NETWORK_REQUEST');
  final={...prelim,status:'PASS',cleanCheckout:true,blobVerified:checkout.servedFileCount,
   originalBrowserInput:'PASS',elementWitness:'PASS',nodeWitnesses:'PASS',
   comparedNodeQueries:priv.nodes.length,reportedUnknownFamilies:priv.qualificationRows,
   originalImmutable:true,privateDetails:'WITHHELD'};
 }catch(e){final={...prelim,status:'NOT_RUN_OR_FAIL',code:String(e.message).split(/\s/)[0],
  originalImmutable:sha(fs.readFileSync(original))===first.private.sha256,
  details:'PRIVATE_DIAGNOSTICS_ONLY'};priv={...priv,error:String(e.stack||e)}}
 finally{
  if(priv)fs.writeFileSync(path.join(privateDir,'browser-private.json'),JSON.stringify(priv,null,2)+'\n');
  fs.writeFileSync(path.join(publicDir,'sanitized-result.json'),JSON.stringify(final,null,2)+'\n');
  if(cdp)cdp.close();if(browser){browser.proc.kill();await sleep(300);fs.rmSync(browser.dir,{force:true,recursive:true})}
  if(server)await new Promise(ok=>server.close(ok));
 }
 console.log(JSON.stringify(final,null,2));if(final.status!=='PASS')process.exitCode=2;
}
if(process.argv.includes('--help')){
 console.log('node run-windows-original.mjs --repo <PINNED_CLEAN_REPO> --original <AUTHORIZED_PRIVATE_CII> --private-dir <LOCAL_PRIVATE_OUT> --public-dir <SAFE_OUT> [--browser <EDGE_OR_CHROME_EXE>] [--expected-sha <PRIVATE_EXPECTED_SHA>]');
}else main().catch(e=>{console.error('QUALIFICATION_BLOCKED',String(e.message).split(/\s/)[0]);process.exitCode=2});
