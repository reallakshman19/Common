// Offline DOM fixtures: no browser connection, network or live storage.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {webcrypto} = require('node:crypto');
const source = fs.readFileSync(require('node:path').join(__dirname, 'probe.js'), 'utf8');
class Element {
  constructor(role, id, value) { this.role = role; this.id = id; this.innerText = this.textContent = value; this.parentElement = null; }
  getAttribute(key) { return key === 'data-message-author-role' ? this.role : key === 'data-message-id' ? this.id : this.attributes?.[key] || null; }
  getClientRects() { return [{}]; }
  closest(selector) { return selector === '[data-message-author-role]' && this.role ? this : null; }
  querySelectorAll() { return []; }
}
async function run({messages, alerts = [], stop = false, draft = '', bottom = true}) {
  const composer = new Element(null, null, draft);
  const scroller = {scrollHeight: 1000, clientHeight: 500, scrollTop: bottom ? 500 : 0};
  const document = {
    scrollingElement: scroller,
    querySelectorAll: selector => selector === '[data-message-author-role]' ? messages : selector.includes('role="alert"') ? alerts : stop ? [{...composer, getAttribute: k => k === 'data-testid' ? 'stop-button' : null, getClientRects: () => [{}]}] : [],
    getElementById: () => composer
  };
  const ctx = {document, location: {origin: 'https://chatgpt.com', pathname: '/c/12345678-aaaa-bbbb-cccc-000000000001'}, crypto: webcrypto, TextEncoder,
    getComputedStyle: () => ({visibility: 'visible', overflowY: 'auto', flexDirection: 'column'})};
  vm.createContext(ctx);
  vm.runInContext(source, ctx);
  return JSON.parse(JSON.stringify(await ctx.coordinatorProbe()));
}
(async () => {
  const user = new Element('user', 'u1', 'Owner task');
  const old = new Element('assistant', 'a1', 'LOG | plan=r1 | done=T1 | next=T2 | blocker=NONE | ac=1/5');
  const latest = new Element('assistant', 'a2', 'Completed. The old error said Something went wrong.');
  const p = await run({messages: [user, old, latest]});
  assert.equal(p.state, 'IDLE');
  assert.equal(p.live_error, '');
  assert.deepEqual(p.status.done, []);
  assert.equal(p.latest_assistant.id, 'a2');
  assert.equal(p.completed_messages.length, 2);
  assert.equal(p.completed_messages[1].minutes, null);
  const alert = new Element(null, null, 'Hmm...something seems to have gone wrong');
  assert.equal((await run({messages: [user, latest], alerts: [alert]})).state, 'ERROR');
  assert.equal((await run({messages: [user, latest], alerts: [latest]})).live_error, '');
  const generating = await run({messages: [user, old, latest], stop: true});
  assert.equal(generating.state, 'GENERATING');
  assert.deepEqual(generating.completed_messages.map(m => m.id), ['a1']);
  assert.deepEqual(generating.status, {});
  assert.equal((await run({messages: [user, latest], draft: 'Owner draft\nline 2'})).draft, 'Owner draft\nline 2');
  assert.equal((await run({messages: [user, latest], bottom: false})).at_bottom, false);
  const jsonFooter = new Element('assistant', 'a3', 'COORD {"plan_rev":"r2","done":["T3"],"next":["T4"],"blocker":{"kind":"OWNER","text":"D1"}}');
  assert.equal((await run({messages: [user, jsonFooter]})).status.plan_rev, 'r2');
  assert.equal((await run({messages: [user, old]})).status.plan_rev, 'r1');
  console.log('15 browser-probe assertions passed');
})().catch(e => { console.error(e); process.exitCode = 1; });
