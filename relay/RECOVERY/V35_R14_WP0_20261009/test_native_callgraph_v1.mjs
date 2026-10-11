/* WP0 source-call-graph falsifier, read-only. This is a static, exact-tree
 * local ESM closure, NOT a runtime attestation or provider-Evidence bridge.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {dirname, resolve, relative} from 'node:path';
import {fileURLToPath} from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '../../..');
const relayDir = resolve(root, 'skills/engineering-relay-v1');
const fullchain = resolve(relayDir, 'full-chain-rehearsal-v1.mjs');
const slurp = p => readFileSync(p, 'utf8');

function localEsmClosure(entry) {
  const seen = new Set();
  const allEdges = [];
  const external = new Set();
  const imports = new Map();
  const pending = [entry];
  while (pending.length) {
    const file = pending.pop();
    if (seen.has(file)) continue;
    assert.ok(existsSync(file), 'import target missing: ' + file);
    assert.ok(!relative(relayDir, file).startsWith('..'), 'relative import escapes RELAY: ' + file);
    seen.add(file);
    const source = slurp(file);
    const statements = [...source.matchAll(/^\s*import\s+(?:[^;\n]*?\s+from\s+)?['"]([^'"]+)['"]/gm)];
    const count = (source.match(/^\s*import\s/gm) || []).length;
    assert.equal(statements.length, count, 'unparsed import syntax in ' + file);
    imports.set(file, statements.map(m => m[1]));
    for (const match of statements) {
      const target = match[1];
      allEdges.push([file,target]);
      if (target.startsWith('.')) {
        assert.ok(target.endsWith('.mjs'), 'unexpected local ESM extension: ' + target);
        pending.push(resolve(dirname(file), target));
      } else {
        external.add(target);
      }
    }
    assert.doesNotMatch(source, /\bimport\s*\(/, 'unmapped dynamic import in ' + file);
    // Test import declarations for node:child_process separately; a general '.exec(' can be RegExp.exec.
    assert.doesNotMatch(source, /\b(?:spawn|execFile|fork)\s*\(/, 'unmapped subprocess call in ' + file);
  }
  return {seen,allEdges,external,imports};
}

test('real RELAY R3/R12/R9/R11/R4 full-chain static closure has bounded native modules', () => {
  const m = localEsmClosure(fullchain);
  for (const leaf of [
    'full-chain-rehearsal-v1.mjs',
    'provider-facts-v1.mjs',
    'candidate-verification-v1.mjs',
    'observed-frontier-v1.mjs',
    'trust-preflight-v1.mjs',
    'projection-preview-v1.mjs',
  ]) assert.ok(m.seen.has(resolve(relayDir, leaf)), 'missing live module: ' + leaf);
  assert.ok(m.seen.size >= 6);
  console.log('WP0_RELAY_MODULES=' + m.seen.size + ' IMPORT_EDGES=' + m.allEdges.length);
});

test('RELAY native call closure has NO programme DELP or Python subprocess link', () => {
  const m = localEsmClosure(fullchain);
  assert.ok(![...m.seen].some(p => /delp_projection|diagnostic_delp_bridge|continuity_projection/.test(p)));
  assert.ok(![...m.external].some(p => /child_process|worker_threads/.test(p)));
  // Deliberately prove absence of an import/call edge, NOT absence of
  // data-only material facts; R3/R12 currentness remains valuable.
  console.log('WP0_NATIVE_RELAY_TO_CANONICAL_DELP=UNCONNECTED');
});

test('V3.2 C6 already imports and calls native DELP.project', () => {
  const source = slurp(resolve(root, 'skills/engineering-pr-delivery-v3.2/scripts/handover_context.py'));
  assert.match(source, /import delp_projection_v32 as delp/);
  assert.match(source, /projection\s*=\s*delp\.project\(\s*graph,\s*facts,\s*observed_after\s*\)/);
  assert.match(source, /source_bound_responsibility_core\(/);
  // Import and syntax inspection is not an executed C6 successor test.
  console.log('WP0_C6_EXISTING_PROJECT_CALLSITE=SOURCE_VERIFIED');
});

test('V3.5 read model independently calls its own DELP (not programme RELAY)', () => {
  const source = slurp(resolve(root,'skills/engineering-pr-delivery-v3.5/scripts/integration_read_model_v35.py'));
  assert.match(source, /import delp_projection_v35 as DELP/);
  assert.match(source, /derived\s*=\s*DELP\.project\(/);
  console.log('WP0_V35_READ_MODEL_OWN_DEL P=SOURCE_VERIFIED'.replace('DEL P','DELP'));
});
