import test from 'node:test';
import assert from 'node:assert/strict';
import {observeNativeWithUnknownRetry} from './native-read-retry-v1.mjs';
const UNKNOWN = Object.freeze({source_status:'UNKNOWN',admission:'NOT_ADMITTED',source_digest:null});
const COHERENT = Object.freeze({source_status:'REFERENCES_COHERENT_BUT_UNADMITTED',admission:'NOT_ADMITTED',source_digest:'sha256:test-only'});
const REFUTED = Object.freeze({source_status:'REFUTED',admission:'NOT_ADMITTED',source_digest:null});
const LOCATOR = Object.freeze({pr_number:292});

test('one coherent native observation requires one read only', async () => {
  let calls=0; const logged=[];
  const result=await observeNativeWithUnknownRetry(LOCATOR,async p=>{assert.equal(p,LOCATOR);calls++;return COHERENT},x=>logged.push(JSON.parse(x)));
  assert.equal(result,COHERENT); assert.equal(calls,1); assert.deepEqual(logged.map(x=>x.native_read_attempt),[1]);
});
test('a provider UNKNOWN receives exactly one new complete read', async () => {
  const observed=[UNKNOWN,COHERENT]; const logged=[];
  const result=await observeNativeWithUnknownRetry(LOCATOR,async()=>observed.shift(),x=>logged.push(JSON.parse(x)));
  assert.equal(result,COHERENT); assert.equal(observed.length,0); assert.equal(logged[0].source_status,'UNKNOWN');assert.deepEqual(logged.map(x=>x.native_read_attempt),[1,2]);
});
test('two UNKNOWN reads remain UNKNOWN rather than becoming success', async () => {
  let calls=0;const logged=[];
  const result=await observeNativeWithUnknownRetry(LOCATOR,async()=>{calls++;return UNKNOWN},x=>logged.push(JSON.parse(x)));
  assert.equal(result,UNKNOWN);assert.equal(calls,2);assert.equal(logged.length,2);assert.ok(logged.every(x=>x.admission==='NOT_ADMITTED'));
});
test('REFUTED is never retried or converted to coherent', async () => {
  let calls=0;
  const result=await observeNativeWithUnknownRetry(LOCATOR,async()=>{calls++;return REFUTED},()=>{});
  assert.equal(result,REFUTED);assert.equal(calls,1);
});
test('read transport errors propagate: never hide provider errors', async () => {
  let calls=0;
  await assert.rejects(observeNativeWithUnknownRetry(LOCATOR,async()=>{calls++;throw new Error('HTTP 403')},()=>{}),/HTTP 403/);
  assert.equal(calls,1);
});
test('invalid native data cannot be retried or presented as authority', async () => {
  let logged=0;
  await assert.rejects(observeNativeWithUnknownRetry(LOCATOR,async()=>({admission:'ADMITTED'}),()=>{logged++}),/NATIVE_READ_RESULT_INVALID/);
  assert.equal(logged,0);
});
test('the helper cannot change the caller-provided admission fields', async () => {
  const malicious={source_status:'REFERENCES_COHERENT_BUT_UNADMITTED',admission:'FAKE_ADMITTED',writer_authorized:true};
  const result=await observeNativeWithUnknownRetry(LOCATOR,async()=>malicious,()=>{});
  assert.equal(result,malicious); // This is an I/O helper, NOT a verifier. The CLI's hard gates remain mandatory.
  assert.equal(result.admission,'FAKE_ADMITTED');
});
test('the logger cannot approve or transform the actual returned result', async () => {
  const received=[];
  const result=await observeNativeWithUnknownRetry(LOCATOR,async()=>UNKNOWN,x=>received.push(x));
  assert.equal(result,UNKNOWN);assert.equal(result.admission,'NOT_ADMITTED');assert.equal(received.length,2);
});

test('caller-supplied attempt field cannot forge helper-owned retry audit sequence', async () => {
  const first=Object.freeze({source_status:'UNKNOWN',admission:'NOT_ADMITTED',native_read_attempt:900});
  const second=Object.freeze({source_status:'REFERENCES_COHERENT_BUT_UNADMITTED',admission:'NOT_ADMITTED',native_read_attempt:999});
  const logged=[];
  const inputs=[first,second];
  const returned=await observeNativeWithUnknownRetry(LOCATOR,async()=>inputs.shift(),line=>logged.push(JSON.parse(line)));
  assert.equal(returned,second);
  assert.equal(returned.native_read_attempt,999); // Returned observation is never modified or laundered.
  assert.deepEqual(logged.map(x=>x.native_read_attempt),[1,2]);
  assert.ok(logged.every(x=>x.admission==='NOT_ADMITTED'));
});
