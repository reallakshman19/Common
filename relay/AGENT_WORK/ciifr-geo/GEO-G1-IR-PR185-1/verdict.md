## CIIFR-GEO-IR-PR185-1 — scoped verdict: FAIL; browser/GPU acceptance BLOCKED

READ_ONLY independent-review operation, 2026-10-26. **Do not accept/merge PR185 on this evidence.** One reproducible current-viewer lifecycle defect is below. Native functionality has useful bounded support; actual served-browser/GPU/Owner acceptance is unestablished.

### Subject, actual receipt and source authority

Reviewed exactly PR185 head `7f9ea25931777dda85686ad7cc9a1a011132a23c`, tree `a6a2ea6820e97fbdedc2e1e96718dc2a26a67e3d`, base PR183 `3a1bec9524c8a14e4b0a90a23d628f0b5d47aaf6` / tree `00f7825a271c4e68f650eebede40d0d62aea32f6`. GitHub GET before and after review returned that same live head/base. Commit ancestry was GET-read: report commit → `e96c3ece478da065becef9a856d2e585fe5dc88b` → exact PR183 base.

I obtained the immutable changed-file bytes and recursive Git tree myself through the public GitHub connector. In an isolated review workspace, I copied the available base checkout, verified its HEAD/tree, overlaid only the 13 actual PR files from immutable GitHub, and calculated Git blob identities (`SHA1("blob "+length+"\\0"+bytes)`). **8,564 unchanged + 13 changed = all 8,577 tracked blob files match the requested remote tree, including a post-execution recheck with zero mismatches.** The local checkout HEAD remains the base; the tested candidate is the verified file overlay, not a claimed local PR185 commit. No product repairs/branch writes/merge occurred.

Requirements came from #186/#180, the [Owner-outcome concept](https://github.com/reallakshman19/Common/blob/ca196c6ea5f5599a7c19cff9a828f1cf785a9f9c/oracle-cycles/ciifr/continuity/payload/CONCEPT_NOTE.md), [plan/Card A](https://github.com/reallakshman19/Common/blob/ca196c6ea5f5599a7c19cff9a828f1cf785a9f9c/oracle-cycles/ciifr/continuity/payload/ROADMAP_AND_IMPLEMENTATION_PLAN.md), and the [pinned implementation brief/dispatch/unblock sources](https://github.com/reallakshman19/Common/tree/b8fa4ac3953c2c3ba1081ff6c49447a4e1a9e007/relay/AGENT_WORK/ciifr-geo/GEO-G1-VIEWER-INTEGRATION-1). I applied the [Independent Reviewer skill](https://github.com/reallakshman19/Common/blob/b8fa4ac3953c2c3ba1081ff6c49447a4e1a9e007/skills/agent-work/independent-review/SKILL.md), INDEPENDENCE.md and APPLYING_GUIDANCE.md at that revision. Common PR518's output note was inspected as **proposed custody**, not canonical publication or reviewer receipt; my actual GitHub byte access above establishes this review's receipt.

### Independence and exposure

- I am a separate non-author reviewer process assigned this task; I made no PR185 or PR183 candidate contributions. This process was not given the author's prior conversation. This alone is **not proof of distinct principal**.
- Principal/human identity: **UNKNOWN**. GitHub connector `get_user_login` returned `reallakshman19` (same shared account that displays candidate authorship). No independent GitHub-account approval is inferred and no formal APPROVE review was submitted.
- Actual exposure: coordinating assignment; #186/#180; PR185 description, workreport, diff, candidate/tests; Oracle-authored framework, concept, plan, relay; shared base cache and its full verified source; Common PR518. Fresh context does not establish host isolation or lack of prior upstream influence.
- The coordinating Oracle authored PR183 and supplied assets/briefs. Its source/fixture premises are shared lineage, not independent approval of its affected seam.
- Expected behavior was reconstructed from current-session ownership and Owner requirements. I selected the concurrent old/new **app-level enable-completion** falsifier after source inspection; it is not an author-supplied expected answer. Existing mathematical/tests are replayed author/contributor oracles, with that limit. The new falsifier's expected value is simply: completion of revoked request A must not dispose current request B.
- Test-only review scripts do not alter candidate authorship. They do not authenticate a distinct principal.

### Finding F1 — P2: obsolete viewer startup can dispose the current viewer

[app.js lines 92–104](https://github.com/reallakshman19/XML_Compare_Utilities/blob/7f9ea25931777dda85686ad7cc9a1a011132a23c/prototypes/ciifr-map/app.js#L92), particularly line93 and the unconditional error cleanup at103, act on shared current UI/bridge state after an `await` without owning the request.

Minimal sequence:

1. Run Method C and start enabling viewer A; pause its asynchronous factory.
2. Change projection (or replace/revoke inputs), run the current comparison, enable viewer B.
3. Complete A. The real bridge correctly rejects/disposes stale A and returns `false`.
4. Old `toggleViewer()` resumes at line93 and calls `disableGpu()`, disposing **current B** and changing its UI to SVG. A late rejection similarly reaches unconditional cleanup at103.

Actual native reproducer executes **unchanged exact app.js bytes, real XML intake/session/scene and real bridge**. Only the DOM rendering and WebGL factory are synthetic; it is not a served-browser result. Real supplied XML, manual anchors3790/3830/3840, then XZ→XY were used.

Observed new-before-old completion:
```text
BEFORE_OLD_COMPLETION { active: true, disposed: [], projection: 'XY', label: 'Use SVG viewer' }
AFTER_OLD_COMPLETION  { active: false, disposed: [1, 2], projection: 'XY', label: 'Use existing 3D viewer' }
DEFECT_REPRODUCED: old app continuation disposed newer viewer #2; current exports remain unchanged
```

The alternative **FIFO** release of old/new pending startups in the same turn also reproduced disposal of current viewer2. This ordering models concurrent await-import completions; the real bridge continuations can both run before obsolete app cleanup. JSON/CSV/SVG current export strings were byte-identical across the first ordering: this finding is unwanted lifecycle/UI teardown, **not observed evidence corruption**.

Existing bridge tests cover bridge generation rejection; they never import app.js and do not catch its obsolete cleanup. Thus all21 native tests can pass while F1 survives.

Correction needed: make post-await success/error/finally UI cleanup request-owned, so obsolete requests cannot disable or relabel a newer viewer. Do not weaken the real bridge's stale rejection. Re-review the repaired exact head; no repair was performed here.

### Actual execution and bounded results

Host: Linux, Node **v24.22.1**; test-only `@xmldom/xmldom` **0.9.12** measured from the actual installed package (not the author's reported0.9.8); Python native launcher. `CIIFR_TEST_RUNTIME=/workspace/scratch/ca71d2f89cf7/map-test-runtime`.

| Check | Actual result and scope |
|---|---|
| Base `node --test prototypes/ciifr-map/tests/*.test.mjs` at verified PR183 | **PASS18/18**, actual execution. |
| Same command on exact PR185 file overlay | **PASS21/21**, actual execution; includes real XML, transform-once, side/hash identities, all TARGET links, ELEMENT-only semantics, scope, stale session/export and synthetic SVG/table/bridge cases. These do not execute a browser. |
| `python prototypes/ciifr-map/tests/http_smoke.py` | **PASS**,30 ES modules delivered through actual HTTP. |
| `python prototypes/ciifr-map/tests/viewer_http_smoke.py` | **PASS**, official asset hash/license, viewer/Worker HTTP/MIME and hidden-route denylist. |
| Review `node --experimental-vm-modules ../repro-stale-enable-realxml.mjs` (from candidate root, adjust relative path) and `--fifo` | **FAIL lifecycle expectation**, defect reproduced in both orders; script exits0 when its defect assertions succeed. Synthetic DOM/factory, real app/session/bridge. |
| Existing Chromium binary via Playwright, headless + SwiftShader | **BLOCKED before page creation**: after correcting missing temporary directory with task-local TMPDIR, Chromium exited **SIGTRAP**. No page, SVG journey, WebGL context or GPU pixel pick was executed. No repeated install/retry campaign. |

Native source inspection covered all13 changed files and consequential unchanged compare/intake/scene/pick/evidence/shared viewer/Worker/camera/navigation paths. No source inspection is labelled browser PASS.

### Actual inputs/assets and lineage

| Actual bytes measured | Size | SHA256 |
|---|---:|---|
| S1-F05.xml |882735| `1154c980d08344b1f803cda3bd9884b169753148b150641a745c9bfcb15de995` |
| S1-R4.xml |1426775| `a332dd7b2551faae51de3c016941762c3b795cdf19073b373817354e309526e6` |
| public Benchmark/S1.CII |108330| `9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b` |
| pinned Three ESM |670681| `3e690ac7d180b0aadf0891bea39eec643e29e2d3e75c99b18689518665f69ba6` |
| MIT LICENSE |1081| `852e0e8699169bf9f6fdc6bda3e682d078dcbc738b5d33e74df594721bff271d` |

Fixture Git blobs were included in the complete candidate-tree comparison. I additionally executed unchanged `prepare-fixtures.py` functions with output redirected to a separate review-only directory, using historical converter Git objects F05 `a67487023bcafc13d68b62dbfc9bb74c61b3c64c`, R4 `9da244e7670a21d963def16543679a6d983d5ba7`; both regenerated XMLs and manifest were byte-identical. **This proves reproducible one-original fixture lineage, not independent engineering-model correspondence.** No protected Owner model pair or protected original-CII claim was qualified.

Candidate Three Git blob `9807b610d02fd0a1833fa7ceae44239652c78f3c` and LICENSE `d07e209686512b9ac93d7df5481a4a6f622093e7` matched the independently GET-read official `mrdoob/three.js` immutable tree at `d04539a76736ff500cae883d6a38b3dd8643c548`; official license text was read. This is asset custody, not renderer qualification.

### NOT_RUN, surviving wrong case and next action

**NOT_RUN/BLOCKED:** actual served-browser SVG/GPU linked picks with reused TARGET alternatives; overlay/split/common-scale and named projection correctness; real delayed Worker/pick plus source/projection changes; real switch/dispose/recreate; real unavailable-WebGL UI fallback; real downloaded current-result export parity; actual frame/pick/performance/memory measurements; Windows launcher; Owner trial and independent-model engineering correspondence.

A plausible wrong GPU model/axis/scale/pixel mapping can survive every green native/HTTP check because none rendered or picked pixels. A native fake factory cannot establish real WebGL resource cleanup or successful startup. F1 remains a separate **known FAIL**, not erased by these missing checks.

Next: keep draft PR185 acceptance/merge held; route a bounded author correction for F1 and a request-owned completion regression, then independently review the **new exact head** including affected dependencies. On a functioning browser/WebGL host, execute #186's full current-input SVG↔GPU/overlay/split/pick/projection/stale-callback/fallback/export journey and retain Owner decision separately. Do not ask the PR183 author/Oracle to independently approve its own seam.

### Complete review-only reproducer

Place this script next to a `candidate/` directory containing the verified PR185 tree, set `CIIFR_TEST_RUNTIME` to an npm prefix with actual xmldom0.9.12, and run:
```sh
CIIFR_TEST_RUNTIME=/path/to/test-prefix node --experimental-vm-modules repro-stale-enable-realxml.mjs
CIIFR_TEST_RUNTIME=/path/to/test-prefix node --experimental-vm-modules repro-stale-enable-realxml.mjs --fifo
```

Reproducer SHA256: `82cf3ba3449e6e45e139b917893f58925f89344e022f11b590c4c963c434fdd4`.

```js
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {createRequire} from 'node:module';
import {createGeoViewerBridge} from './candidate/prototypes/ciifr-map/geo-viewer-bridge.js';
import {createPreviewSession} from './candidate/prototypes/ciifr-map/compare.js';
import {readXmlGraph} from './candidate/prototypes/ciifr-map/xml-intake.js';
import {exportPreview} from './candidate/prototypes/ciifr-map/evidence.js';

// Executes exact app.js + real session/intake/scene/bridge; only DOM rendering and
// WebGL factory are synthetic. This is explicitly NOT served-browser execution.
const runtime=process.env.CIIFR_TEST_RUNTIME||'/workspace/scratch/ca71d2f89cf7/map-test-runtime';
const {DOMParser}=createRequire(runtime+'/package.json')('@xmldom/xmldom');
const session=createPreviewSession({read:(bytes,options)=>readXmlGraph(bytes,{...options,cryptoRef:webcrypto,
 parser:new DOMParser({onError:(level,message)=>{throw Error(level+':'+message);}})})});
for(const [side,name]of [['SOURCE','S1-F05.xml'],['TARGET','S1-R4.xml']])
 await session.load(side,new Uint8Array(readFileSync(new URL('./candidate/prototypes/ciifr-map/tests/fixtures/'+name,import.meta.url))),name);
for(const n of ['3790','3830','3840'])session.addAnchor(n,n);
const elements=new Map();
const el=id=>elements.get(id)||elements.set(id,{id,hidden:false,disabled:false,textContent:'',
 value:id==='projection'?'XZ':id==='viewer-layout'?'overlay':'100',listeners:{},
 classList:{toggle(){}},replaceChildren(){},addEventListener(k,f){this.listeners[k]=f;}}).get(id);
const fifo=process.argv.includes('--fifo');
let bridge,releaseOld,releaseNew,calls=0;const disposed=[];
const makeViewer=async()=>{
 const id=++calls;
 if(id===1)await new Promise(r=>releaseOld=r);
 if(id===2&&fifo)await new Promise(r=>releaseNew=r);
 return {setModels(){},setMode(){},fitAll(){},getStateSnapshot(){return {runtimeRevision:1};},
 toggleCameraType(){},setStandardView(){},setSelection(){},dispose(){disposed.push(id);}};
};
const context=vm.createContext({document:{getElementById:el,querySelectorAll:()=>[]},window:{addEventListener(){}},console,setTimeout});
const modules={
 './compare.js':{createPreviewSession:()=>session},'./evidence.js':{exportPreview},
 './view.js':{graphInfo(){},renderAnchors(){},renderRows(){},selectedDetails(){return '';},mountScene(){return {}; }},
 './geo-viewer-bridge.js':{createGeoViewerBridge:opts=>bridge=createGeoViewerBridge({...opts,makeViewer})},
};
const app=new vm.SourceTextModule(readFileSync(new URL('./candidate/prototypes/ciifr-map/app.js',import.meta.url),'utf8'),{context});
await app.link(spec=>{const e=modules[spec];return new vm.SyntheticModule(Object.keys(e),function(){for(const [k,v]of Object.entries(e))this.setExport(k,v);},{context});});
await app.evaluate();
el('run').listeners.click();
const oldEnable=el('toggle-gpu').listeners.click();
el('projection').value='XY';el('projection').listeners.input();
el('run').listeners.click();
const newEnable=el('toggle-gpu').listeners.click();
if(fifo){
 // Both await the same newly loaded module in production; release in FIFO order
 // in one turn so both real bridge continuations queue before old app cleanup.
 releaseOld();releaseNew();await Promise.all([oldEnable,newEnable]);
 console.log('FIFO_COMPLETION',{active:bridge.isActive(),disposed:[...disposed],projection:session.current().projection,label:el('toggle-gpu').textContent});
 assert.equal(bridge.isActive(),false);assert.deepEqual(disposed,[1,2]);
 console.log('DEFECT_REPRODUCED: FIFO old/new startup completion also disposes current viewer #2');
}else{
await newEnable;
assert.equal(bridge.isActive(),true);assert.equal(el('gpu-host').hidden,false);
const beforeExports=['json','csv','svg'].map(k=>exportPreview(session,k));
console.log('BEFORE_OLD_COMPLETION',{active:bridge.isActive(),disposed:[...disposed],projection:session.current().projection,label:el('toggle-gpu').textContent});
releaseOld();await oldEnable;
console.log('AFTER_OLD_COMPLETION',{active:bridge.isActive(),disposed:[...disposed],projection:session.current().projection,label:el('toggle-gpu').textContent});
assert.equal(bridge.isActive(),false);assert.deepEqual(disposed,[1,2]);
assert.deepEqual(['json','csv','svg'].map(k=>exportPreview(session,k)),beforeExports);
console.log('DEFECT_REPRODUCED: old app continuation disposed newer viewer #2; current exports remain unchanged');
}
```

