import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { verifyElementSection, verifyNodeSection, verifyReverseSection } from './qualification-guards.mjs';
const oracle = JSON.parse(fs.readFileSync(new URL('./physical-oracle.json', import.meta.url)));
const headers = ['Element #','FROM → TO','Branch','T1 stored raw','P1 stored raw','Fluid density stored raw','Qualification'];
const makeElement = e => ({title:`SOURCE · FROM ${e.fromNode} → TO ${e.toNode} · 1 element(s)`,tables:[{headers:[...headers],rows:[[String(e.ordinal),`${e.fromNode} → ${e.toNode}`,e.branch,...e.fields.map(f=>`${f.identity}: ${f.lexeme} [bytes ${f.byteStart}–${f.byteEnd}]`),'HOLD: effective process semantics / identity not qualified']]}]});
const makeNode = () => ({title:'SOURCE · Numeric Node 500',tables:[{headers:['Family','Owning element #','Occurrence','Evidence / HOLD'],rows:structuredClone(oracle.node.rows)}]});
for (const e of oracle.elements) test(`literal physical fields of element ${e.ordinal} accepted`,()=>{
  const actual = verifyElementSection(makeElement(e),e);
  assert.equal(actual.p1, e.ordinal===1?30:20);
  assert.equal(actual.density,1.01);
});
const mutations = [
  ['pressure 130 cannot satisfy 30',r=>r[4]=r[4].replace(': 30 ',': 130 ')],
  ['wrong pressure cannot hide in byte span',r=>r[4]='PRESSURE_1_STORED: 999 [bytes 30–604]'],
  ['temperature 1200 cannot satisfy 200',r=>r[3]=r[3].replace(': 200 ',': 1200 ')],
  ['density 11.01 cannot satisfy 1.01',r=>r[5]=r[5].replace(': 1.01 ',': 11.01 ')],
  ['correct values at wrong physical address fail',r=>r[4]=r[4].replace('591–604','1591–1604')],
  ['wrong field identity fails',r=>r[4]=r[4].replace('PRESSURE_1_STORED','TEMPERATURE_1_STORED')],
  ['wrong ordinal fails',r=>r[0]='10'],
  ['reversed member fails',r=>r[1]='500 → 400'],
  ['unqualified field cannot claim accepted semantics',r=>r[6]='ACCEPTED']
];
for(const [name,mutate] of mutations)test(name,()=>{const s=makeElement(oracle.elements[0]);mutate(s.tables[0].rows[0]);assert.throws(()=>verifyElementSection(s,oracle.elements[0]));});
test('extra parallel element cannot pass unique selection',()=>{const s=makeElement(oracle.elements[0]);s.tables[0].rows.push([...s.tables[0].rows[0]]);assert.throws(()=>verifyElementSection(s,oracle.elements[0]));});
test('complete node ownership witness accepted',()=>assert.equal(verifyNodeSection(makeNode(),oracle.node).rigid[1],'1'));
for(const [name,family,col,value] of [
  ['wrong owner','RESTRANT',1,'10'],['pointer 10 prefix','RESTRANT',2,'Pointer 10 · Slot 1'],
  ['wrong slot','RESTRANT',2,'Pointer 1 · Slot 10'],['type 10 prefix','RESTRANT',3,'Type 10 · CNode 0 · semantics partial'],
  ['wrong connection node','RESTRANT',3,'Type 1 · CNode 10 · semantics partial'],
  ['wrong displacement specification','DISPLMNT',2,'Pointer 1 · Specification 10'],
  ['rigid weight 1000 prefix','RIGID',3,'Weight raw 1000 · element-owned, semantics partial']
])test(name,()=>{const s=makeNode();s.tables[0].rows.find(r=>r[0]===family)[col]=value;assert.throws(()=>verifyNodeSection(s,oracle.node));});
test('missing incident rejected',()=>{const s=makeNode();s.tables[0].rows.shift();assert.throws(()=>verifyNodeSection(s,oracle.node));});
test('duplicate attachment rejected',()=>{const s=makeNode();s.tables[0].rows.push([...s.tables[0].rows[2]]);assert.throws(()=>verifyNodeSection(s,oracle.node));});
test('reverse orientation has no rows',()=>{const s={title:'SOURCE · FROM 500 → TO 400 · 0 element(s)',tables:[{headers,rows:[]}]};verifyReverseSection(s);s.tables[0].rows.push(['wrong']);assert.throws(()=>verifyReverseSection(s));});
