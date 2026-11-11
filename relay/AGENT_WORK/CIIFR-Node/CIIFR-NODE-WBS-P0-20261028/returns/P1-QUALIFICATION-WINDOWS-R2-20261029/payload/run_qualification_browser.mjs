import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';

const ROOT_DIR = 'C:\\Users\\reall\\Documents\\antigravity\\resilient-tesla';
const CANDIDATE_DIR = path.join(ROOT_DIR, 'CIIFR-Node-P12-20261029-152402');
const EVIDENCE_DIR = path.join(ROOT_DIR, 'evidence-private-20261029');
const SRC_FIXTURE = path.join(EVIDENCE_DIR, 'SYNTH_V14_SOURCE.cii');
const TGT_FIXTURE = path.join(EVIDENCE_DIR, 'SYNTH_V14_TARGET0.cii');

const EXPECTED_SRC_SHA = 'c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b';
const EXPECTED_TGT_SHA = '0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661';

const SERVED_MODULES_TO_VERIFY = [
  'docs/cii-fnr-vnext.html',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/app.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/panel.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/cii-index.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/element.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/node.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/nodal-panel.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/writer.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/physical.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/source-provenance.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/normal-node-closure.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/ui/geo-tab.js',
  'docs/tabs/cii-workspace/cii-fnr-vnext/normal/plan.js'
];

async function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

async function fetchBuffer(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', reject);
  });
}

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function gitBlobSha(buf) {
  return crypto.createHash('sha1').update(Buffer.concat([
    Buffer.from(`blob ${buf.length}\0`),
    buf
  ])).digest('hex');
}

class BrowserSession {
  constructor(browserName, exePath, port, profileName) {
    this.browserName = browserName;
    this.exePath = exePath;
    this.port = port;
    this.profileDir = path.join(ROOT_DIR, profileName);
    this.proc = null;
    this.ws = null;
    this.msgId = 0;
    this.consoleLogs = [];
    this.pageErrors = [];
    this.networkRequests = [];
  }

  async start() {
    if (!fs.existsSync(this.profileDir)) fs.mkdirSync(this.profileDir, { recursive: true });
    this.proc = spawn(this.exePath, [
      '--headless=new',
      '--disable-gpu',
      `--remote-debugging-port=${this.port}`,
      `--user-data-dir=${this.profileDir}`,
      '--no-first-run',
      '--no-default-browser-check',
      'about:blank'
    ], { stdio: 'ignore' });

    let version = null;
    for (let i = 0; i < 30; i++) {
      try {
        version = await getJson(`http://127.0.0.1:${this.port}/json/version`);
        break;
      } catch {
        await new Promise(r => setTimeout(r, 200));
      }
    }
    if (!version) throw new Error(`Failed to connect to ${this.browserName} on port ${this.port}`);
    this.version = version;

    const targets = await getJson(`http://127.0.0.1:${this.port}/json/list`);
    const pageTarget = targets.find(t => t.type === 'page') || targets[0];
    this.wsUrl = pageTarget.webSocketDebuggerUrl;

    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.method === 'Console.messageAdded') {
        this.consoleLogs.push(msg.params.message);
      } else if (msg.method === 'Runtime.consoleAPICalled') {
        this.consoleLogs.push({
          type: msg.params.type,
          text: msg.params.args.map(a => a.value || a.description).join(' ')
        });
      } else if (msg.method === 'Runtime.exceptionThrown') {
        this.pageErrors.push(msg.params.exceptionDetails);
      } else if (msg.method === 'Network.requestWillBeSent') {
        this.networkRequests.push(msg.params.request);
      }
    };

    await this.send('Page.enable');
    await this.send('Runtime.enable');
    await this.send('Network.enable');
    await this.send('Console.enable');
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.msgId;
      const handler = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id === id) {
          this.ws.removeEventListener('message', handler);
          if (msg.error) reject(new Error(`${method} failed: ${JSON.stringify(msg.error)}`));
          else resolve(msg.result);
        }
      };
      this.ws.addEventListener('message', handler);
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true
    });
    if (res.exceptionDetails) {
      throw new Error(`Eval exception: ${res.exceptionDetails.text} (${JSON.stringify(res.exceptionDetails)})`);
    }
    return res.result.value;
  }

  async screenshot(filename) {
    const res = await this.send('Page.captureScreenshot', { format: 'png' });
    const buf = Buffer.from(res.data, 'base64');
    const outPath = path.join(EVIDENCE_DIR, filename);
    fs.writeFileSync(outPath, buf);
    return outPath;
  }

  async close() {
    if (this.ws) {
      try { this.ws.close(); } catch {}
    }
    if (this.proc) {
      try { this.proc.kill(); } catch {}
    }
  }
}

async function verifyServedModuleIntegrity() {
  console.log(`\nVerifying served HTTP module integrity against candidate disk tree...`);
  const verification = [];
  for (const relPath of SERVED_MODULES_TO_VERIFY) {
    const url = `http://127.0.0.1:8765/${relPath.replace(/\\/g, '/')}`;
    const httpBuf = await fetchBuffer(url);
    const diskPath = path.join(CANDIDATE_DIR, relPath);
    const diskBuf = fs.readFileSync(diskPath);

    const httpSha = sha256(httpBuf);
    const diskSha = sha256(diskBuf);
    const diskBlob = gitBlobSha(diskBuf);

    if (httpSha !== diskSha) {
      throw new Error(`Served HTTP module integrity mismatch for ${relPath}: HTTP=${httpSha} Disk=${diskSha}`);
    }

    verification.push({
      path: relPath,
      bytes: diskBuf.length,
      sha256: diskSha,
      gitBlob: diskBlob,
      match: true
    });
  }
  console.log(`All ${verification.length} served HTTP modules verified identical to disk candidate tree.`);
  return verification;
}

async function runBrowserTests(session) {
  console.log(`\n======================================================`);
  console.log(`Starting Qualification Suite on: ${session.browserName}`);
  console.log(`Browser Product: ${session.version.Browser}`);
  console.log(`User-Agent: ${session.version['User-Agent']}`);
  console.log(`======================================================`);

  const results = {
    browser: session.browserName,
    productVersion: session.version.Browser,
    servedSourceVerification: await verifyServedModuleIntegrity(),
    cases: {}
  };

  // Pre-check fixture hashes on disk
  const srcDiskBytes = fs.readFileSync(SRC_FIXTURE);
  const tgtDiskBytes = fs.readFileSync(TGT_FIXTURE);
  const initialSrcHash = sha256(srcDiskBytes);
  const initialTgtHash = sha256(tgtDiskBytes);
  if (initialSrcHash !== EXPECTED_SRC_SHA || initialTgtHash !== EXPECTED_TGT_SHA) {
    throw new Error(`Public fixture disk hash mismatch!`);
  }

  // 1. Navigate to http://127.0.0.1:8765/docs/cii-fnr-vnext.html
  console.log(`[Step 1] Navigating to http://127.0.0.1:8765/docs/cii-fnr-vnext.html...`);
  await session.send('Page.navigate', { url: 'http://127.0.0.1:8765/docs/cii-fnr-vnext.html' });
  await new Promise(r => setTimeout(r, 1200));

  const pageTitle = await session.eval('document.title');
  const h1Text = await session.eval('document.querySelector("h1").innerText');
  console.log(`Page Title: ${pageTitle}`);
  console.log(`Header: ${h1Text}`);
  if (session.pageErrors.length > 0) {
    throw new Error(`Page load had errors: ${JSON.stringify(session.pageErrors)}`);
  }

  // ==========================================
  // CASE 1: Committed Normal Demo
  // ==========================================
  console.log(`\n[Case 1] Exercising committed Normal demo...`);
  await session.eval(`
    (async () => {
      document.querySelector('[data-tab="NORMAL"]').click();
      document.querySelector('[data-load-demo]').click();
    })()
  `);
  // Wait for demo to load
  await new Promise(r => setTimeout(r, 1000));
  const demoStatus = await session.eval('document.querySelector("[data-demo-status]").textContent');
  console.log(`Demo Status: ${demoStatus}`);

  // Generate proposals
  await session.eval('document.querySelector("[data-run]").click()');
  await new Promise(r => setTimeout(r, 600));

  const claimText = await session.eval('document.querySelector("[data-status]").textContent');
  const proposalRows = await session.eval('document.querySelectorAll("[data-proposals] tr").length');
  console.log(`Proposals generated: ${proposalRows} rows. Status: "${claimText}"`);

  // Approve proposal 0, reject proposal 1
  await session.eval(`
    (() => {
      const s0 = document.querySelectorAll('[data-decision]')[0];
      if (s0) {
        s0.value = 'APPROVED';
        s0.dispatchEvent(new Event('change', { bubbles: true }));
      }
      const s1 = document.querySelectorAll('[data-decision]')[1];
      if (s1) {
        s1.value = 'REJECTED';
        s1.dispatchEvent(new Event('change', { bubbles: true }));
      }
    })()
  `);
  await new Promise(r => setTimeout(r, 300));

  // Click Validate
  await session.eval('document.querySelector("[data-validate]").click()');
  await new Promise(r => setTimeout(r, 400));

  const validateStatus = await session.eval('document.querySelector("[data-status]").textContent');
  const applyDisabled = await session.eval('document.querySelector("[data-apply]").disabled');
  const exportDisabledBeforeApply = await session.eval('document.querySelector("[data-export]").disabled');
  console.log(`Validation result: "${validateStatus}", Apply disabled: ${applyDisabled}, Export disabled: ${exportDisabledBeforeApply}`);

  // Click Apply
  await session.eval('document.querySelector("[data-apply]").click()');
  await new Promise(r => setTimeout(r, 400));

  const applyStatus = await session.eval('document.querySelector("[data-status]").textContent');
  const exportDisabledAfterApply = await session.eval('document.querySelector("[data-export]").disabled');
  const target1Hash = await session.eval('document.querySelector("[data-hash1]").textContent');
  console.log(`Apply result: "${applyStatus}", Export disabled: ${exportDisabledAfterApply}, Target1 hash: ${target1Hash}`);

  results.cases.case1_normal_demo = {
    status: 'PASS',
    proposalRows,
    claimStatus: claimText,
    validateStatus,
    applyStatus,
    target1Hash,
    exportEnabled: !exportDisabledAfterApply
  };

  await session.screenshot(`${session.browserName}-01-normal-demo.png`);

  // Record baseline decision values in Normal tab prior to Property visit
  const beforePropertyDecisions = await session.eval(`
    Array.from(document.querySelectorAll('[data-decision]')).map(sel => ({
      id: sel.dataset.decision,
      value: sel.value
    }))
  `);
  console.log(`Recorded before-Property Normal decisions count: ${beforePropertyDecisions.length}`);

  // ==========================================
  // CASE 2: Visit Property, load independent fixtures, inspect element/node, return to Normal
  // ==========================================
  console.log(`\n[Case 2] Visiting Property Transfer tab, loading public fixtures, testing element & node, verifying state preservation...`);
  
  // Click Property Transfer tab
  await session.eval('document.querySelector(\'[data-tab="PROPERTY_TRANSFER"]\').click()');
  await new Promise(r => setTimeout(r, 400));

  const ptHidden = await session.eval('document.querySelector("[data-property-transfer-area]").hidden');
  const wsHidden = await session.eval('document.querySelector("[data-workspace]").hidden');
  console.log(`Property Transfer active: panel hidden=${ptHidden}, workspace hidden=${wsHidden}`);

  // Load public fixtures into Property tab via DataTransfer / File
  const srcBase64 = srcDiskBytes.toString('base64');
  const tgtBase64 = tgtDiskBytes.toString('base64');

  await session.eval(`
    (async () => {
      function b64ToUint8(b64) {
        const bin = atob(b64);
        const u = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
        return u;
      }
      const srcU = b64ToUint8("${srcBase64}");
      const tgtU = b64ToUint8("${tgtBase64}");

      const srcFile = new File([srcU], "SYNTH_V14_SOURCE.cii", { type: "application/octet-stream" });
      const tgtFile = new File([tgtU], "SYNTH_V14_TARGET0.cii", { type: "application/octet-stream" });

      const setFile = (input, file) => {
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      };

      setFile(document.querySelector('[data-pt-file="source"]'), srcFile);
      setFile(document.querySelector('[data-pt-file="target"]'), tgtFile);
    })()
  `);

  await new Promise(r => setTimeout(r, 600));

  const srcStatus = await session.eval('document.querySelector(\'[data-pt-file-status="source"]\').textContent');
  const tgtStatus = await session.eval('document.querySelector(\'[data-pt-file-status="target"]\').textContent');
  console.log(`Property Source status: "${srcStatus}"`);
  console.log(`Property Target status: "${tgtStatus}"`);

  // Path A: ELEMENT mode inspection
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-mode="ELEMENT"]').click();
      document.querySelector('[data-pt-input="sourceFrom"]').value = '400';
      document.querySelector('[data-pt-input="sourceTo"]').value = '500';
      document.querySelector('[data-pt-input="targetFrom"]').value = '840';
      document.querySelector('[data-pt-input="targetTo"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 400));

  const elemResultText = await session.eval('document.querySelector("[data-pt-results]").innerText');
  const elemStatus = await session.eval('document.querySelector("[data-pt-status]").textContent');
  console.log(`Element inspection status: "${elemStatus}"`);
  console.log(`Element result snippet:\n${elemResultText.slice(0, 300)}...`);

  // Path B: NODE mode inspection
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-mode="NODE"]').click();
      document.querySelector('[data-pt-input="sourceNode"]').value = '500';
      document.querySelector('[data-pt-input="targetNode"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 400));

  const nodeResultText = await session.eval('document.querySelector("[data-pt-results]").innerText');
  const nodeStatus = await session.eval('document.querySelector("[data-pt-status]").textContent');
  console.log(`Node inspection status: "${nodeStatus}"`);
  console.log(`Node result snippet:\n${nodeResultText.slice(0, 350)}...`);

  await session.screenshot(`${session.browserName}-02-property-node-inspection.png`);

  // Return to Normal tab and strictly verify preserved state and individual decision values!
  await session.eval('document.querySelector(\'[data-tab="NORMAL"]\').click()');
  await new Promise(r => setTimeout(r, 300));

  const restoredProposals = await session.eval('document.querySelectorAll("[data-proposals] tr").length');
  const restoredExportDisabled = await session.eval('document.querySelector("[data-export]").disabled');
  const restoredHash = await session.eval('document.querySelector("[data-hash1]").textContent');
  const restoredDecisions = await session.eval(`
    Array.from(document.querySelectorAll('[data-decision]')).map(sel => ({
      id: sel.dataset.decision,
      value: sel.value
    }))
  `);
  console.log(`Returned to Normal: proposals=${restoredProposals}, exportDisabled=${restoredExportDisabled}, hash=${restoredHash}, decisionsCount=${restoredDecisions.length}`);

  if (restoredProposals !== proposalRows || restoredExportDisabled !== false || restoredHash !== target1Hash) {
    throw new Error(`Normal state was NOT preserved across Property Transfer visit!`);
  }
  if (beforePropertyDecisions.length < 2 || restoredDecisions.length !== beforePropertyDecisions.length) {
    throw new Error(`Normal decision count mismatch: before=${beforePropertyDecisions.length}, restored=${restoredDecisions.length}`);
  }
  for (let i = 0; i < beforePropertyDecisions.length; i++) {
    const b = beforePropertyDecisions[i];
    const a = restoredDecisions[i];
    if (a.id !== b.id || a.value !== b.value) {
      throw new Error(`Normal decision value mismatch at row ${i}: before id=${b.id} val=${b.value}, restored id=${a.id} val=${a.value}`);
    }
  }
  if (restoredDecisions[0].value !== 'APPROVED' || restoredDecisions[1].value !== 'REJECTED') {
    throw new Error(`Expected proposal 0 APPROVED and proposal 1 REJECTED, got: ${JSON.stringify(restoredDecisions.slice(0, 2))}`);
  }

  // Nodal tab test
  console.log(`Testing Nodal tab state preservation...`);
  await session.eval('document.querySelector(\'[data-tab="NODAL"]\').click()');
  await new Promise(r => setTimeout(r, 300));

  // Load valid Nodal TARGET0 (makeDemoCii with NUMELT=1)
  await session.eval(`
    (async () => {
      function row(v) { return v.map((x, i) => String(x).padStart(i ? 13 : 15, ' ')).join(''); }
      const title = 'LINE-DEMO';
      const lineLabel = ' '.repeat(7) + String(title.length).padStart(5, ' ') + ' ' + title.padEnd(67, ' ');
      const element = Array.from({ length: 15 }, (_, index) => {
        if (index === 0) return row(['100.0', '110.0', 120, 0, 0, 0]);
        if (index === 10) return lineLabel;
        if (index === 13) return row([0, 0, 0, 0, 0, 1]);
        return row([0, 0, 0, 0, 0, 0]);
      });
      const lines = [
        '#$ VERSION', row([5, 14, 1252]),
        '#$ CONTROL', row([1, 0, 0, 1, 0, 0]),
        '#$ ELEMENTS', ...element,
        '#$ NODENAME', '  ' + 'OLD-A'.padEnd(26, ' ') + 'OLD-B'.padEnd(25, ' ')
      ];
      const text = lines.join('\\r\\n') + '\\r\\n';
      const targetFile = new File([text], "nodal-target0.cii", { type: "application/octet-stream" });
      const dtTarget = new DataTransfer();
      dtTarget.items.add(targetFile);
      const targetInput = document.querySelector('[data-file="target"]');
      targetInput.files = dtTarget.files;
      targetInput.dispatchEvent(new Event('change', { bubbles: true }));

      const nodalCsvText = "Find (Info only),FindNode,ReplaceName\\nOLD-A,100,NODE-NEW\\n";
      const csvFile = new File([nodalCsvText], "nodes.csv", { type: "text/csv" });
      const dtCsv = new DataTransfer();
      dtCsv.items.add(csvFile);
      const csvInput = document.querySelector('[data-nodal-csv]');
      csvInput.files = dtCsv.files;
      csvInput.dispatchEvent(new Event('change', { bubbles: true }));
    })()
  `);
  await new Promise(r => setTimeout(r, 600));

  // Click Nodal preview
  await session.eval('document.querySelector("[data-nodal-preview]").click()');
  await new Promise(r => setTimeout(r, 400));

  // Click Approve All
  await session.eval('document.querySelector("[data-nodal-approve-all]").click()');
  await new Promise(r => setTimeout(r, 300));

  // Click Validate
  await session.eval('document.querySelector("[data-nodal-validate]").click()');
  await new Promise(r => setTimeout(r, 500));

  // Click Apply
  await session.eval('document.querySelector("[data-nodal-apply]").click()');
  await new Promise(r => setTimeout(r, 400));

  const nodalTargetHash = await session.eval('document.querySelector("[data-nodal-targethash]").textContent');
  const nodalExportDisabled = await session.eval('document.querySelector("[data-nodal-export]").disabled');
  console.log(`Nodal applied hash: ${nodalTargetHash}, export disabled: ${nodalExportDisabled}`);

  if (nodalExportDisabled) {
    const nodalStatusText = await session.eval('document.querySelector("[data-nodal-status]").textContent');
    throw new Error(`Nodal failed to reach applied state! Status: "${nodalStatusText}"`);
  }

  // Visit Property tab, then return to Nodal
  await session.eval('document.querySelector(\'[data-tab="PROPERTY_TRANSFER"]\').click()');
  await new Promise(r => setTimeout(r, 400));
  await session.eval('document.querySelector(\'[data-tab="NODAL"]\').click()');
  await new Promise(r => setTimeout(r, 400));

  const restoredNodalHash = await session.eval('document.querySelector("[data-nodal-targethash]").textContent');
  const restoredNodalExport = await session.eval('document.querySelector("[data-nodal-export]").disabled');
  console.log(`Returned to Nodal: hash=${restoredNodalHash}, exportDisabled=${restoredNodalExport}`);

  if (restoredNodalHash !== nodalTargetHash || restoredNodalExport !== false) {
    throw new Error(`Nodal state was NOT preserved across Property Transfer visit!`);
  }

  results.cases.case2_property_isolation = {
    status: 'PASS',
    sourceStatus: srcStatus,
    targetStatus: tgtStatus,
    normalStatePreserved: true,
    normalDecisionsMatchedCount: restoredDecisions.length,
    nodalStatePreserved: true
  };

  // ==========================================
  // CASE 3: Invalidation and Pending-CSV Controlled Delay
  // ==========================================
  console.log(`\n[Case 3] Testing rule invalidation and pending-CSV controlled delay...`);
  await session.eval('document.querySelector(\'[data-tab="NORMAL"]\').click()');
  await new Promise(r => setTimeout(r, 300));

  // Re-establish applied state on NORMAL before testing rule edit revocation
  await session.eval('document.querySelector("[data-run]").click()');
  await new Promise(r => setTimeout(r, 400));
  await session.eval(`
    (() => {
      const s0 = document.querySelectorAll('[data-decision]')[0];
      if (s0) { s0.value = 'APPROVED'; s0.dispatchEvent(new Event('change', { bubbles: true })); }
      document.querySelector('[data-validate]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 400));
  await session.eval('document.querySelector("[data-apply]").click()');
  await new Promise(r => setTimeout(r, 400));

  // Assert precondition: established valid state before rule mutation
  const preExportDisabled = await session.eval('document.querySelector("[data-export]").disabled');
  const preClaimsCount = await session.eval('document.querySelectorAll("[data-proposals] tr").length');
  console.log(`Pre-mutation Normal state: exportDisabled=${preExportDisabled}, claimsCount=${preClaimsCount}`);
  if (preExportDisabled !== false || preClaimsCount === 0) {
    throw new Error(`Precondition failed: export is not eligible before rule mutation (disabled=${preExportDisabled}, claims=${preClaimsCount})`);
  }

  // Modify a rule in Normal -> verify immediate revocation
  await session.eval(`
    (() => {
      const replaceInput = document.querySelector('[data-row-index="0"] [data-field="replace"]');
      replaceInput.value = 'MUTATED';
      replaceInput.dispatchEvent(new Event('input', { bubbles: true }));
    })()
  `);
  await new Promise(r => setTimeout(r, 200));

  const exportRevokedOnRuleEdit = await session.eval('document.querySelector("[data-export]").disabled');
  const proposalsClearedOnRuleEdit = await session.eval('document.querySelectorAll("[data-proposals] tr").length');
  console.log(`Rule edit revocation: exportDisabled=${exportRevokedOnRuleEdit}, proposalsCount=${proposalsClearedOnRuleEdit}`);
  if (!exportRevokedOnRuleEdit || proposalsClearedOnRuleEdit !== 0) {
    throw new Error(`Rule edit did NOT revoke authority!`);
  }

  // Restore rule and regenerate/reapprove
  await session.eval(`
    (() => {
      const replaceInput = document.querySelector('[data-row-index="0"] [data-field="replace"]');
      replaceInput.value = 'NEW-A';
      replaceInput.dispatchEvent(new Event('input', { bubbles: true }));
      document.querySelector('[data-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 400));
  await session.eval(`
    (() => {
      const sel = document.querySelector('[data-decision]');
      if (sel) { sel.value = 'APPROVED'; sel.dispatchEvent(new Event('change', { bubbles: true })); }
      document.querySelector('[data-validate]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 400));
  await session.eval('document.querySelector("[data-apply]").click()');
  await new Promise(r => setTimeout(r, 400));

  const reestablishedExport = await session.eval('document.querySelector("[data-export]").disabled');
  const reestablishedClaims = await session.eval('document.querySelectorAll("[data-proposals] tr").length');
  console.log(`Re-established export before delay test: disabled=${reestablishedExport}, claims=${reestablishedClaims}`);
  if (reestablishedExport !== false || reestablishedClaims === 0) {
    throw new Error(`Precondition failed: failed to re-establish applied state prior to delay hook test`);
  }

  // Test Pending-CSV Controlled Delay:
  // Hook File.prototype.text with labelled controlled delay and active pending indicators
  await session.eval(`
    (() => {
      window.__origFileText = File.prototype.text;
      window.__delayPromiseResolve = null;
      window.__delayActive = false;
      window.__delayPending = false;
      File.prototype.text = function() {
        if (window.__delayActive) {
          window.__delayPending = true;
          return new Promise(resolve => {
            window.__delayPromiseResolve = () => {
              window.__delayPending = false;
              window.__origFileText.call(this).then(resolve);
            };
          });
        }
        return window.__origFileText.call(this);
      };
    })()
  `);

  // Activate delay and select CSV
  await session.eval(`
    (() => {
      window.__delayActive = true;
      const csvContent = "Find,Replace\\r\\nOLD-A,DELAYED-A\\r\\nOLD-B,DELAYED-B\\r\\n";
      const file = new File([csvContent], "delayed-rules.csv", { type: "text/csv" });
      const dt = new DataTransfer();
      dt.items.add(file);
      const csvInput = document.querySelector('[data-file="csv"]');
      csvInput.files = dt.files;
      csvInput.dispatchEvent(new Event('change', { bubbles: true }));
    })()
  `);
  await new Promise(r => setTimeout(r, 100));

  // Assert precondition: delay hook is actively in flight right now
  const delayStateDuringPending = await session.eval(`({
    active: window.__delayActive,
    pending: window.__delayPending,
    hasResolver: typeof window.__delayPromiseResolve === 'function'
  })`);
  console.log(`Delay hook state while pending:`, delayStateDuringPending);
  if (!delayStateDuringPending.active || !delayStateDuringPending.pending || !delayStateDuringPending.hasResolver) {
    throw new Error(`Precondition failed: CSV read was not confirmed actively pending in flight!`);
  }

  // Check state WHILE read is actively pending:
  const exportWhilePending = await session.eval('document.querySelector("[data-export]").disabled');
  const applyWhilePending = await session.eval('document.querySelector("[data-apply]").disabled');
  const validateWhilePending = await session.eval('document.querySelector("[data-validate]").disabled');
  const claimsWhilePending = await session.eval('document.querySelectorAll("[data-proposals] tr").length');
  console.log(`While CSV read pending: exportDisabled=${exportWhilePending}, applyDisabled=${applyWhilePending}, validateDisabled=${validateWhilePending}, claimsCount=${claimsWhilePending}`);

  if (!exportWhilePending || !applyWhilePending || !validateWhilePending || claimsWhilePending !== 0) {
    throw new Error(`Authority was NOT revoked immediately when CSV was selected!`);
  }

  // Test "clear while pending"
  console.log(`Testing clear while pending...`);
  await session.eval(`
    (() => {
      const csvInput = document.querySelector('[data-file="csv"]');
      csvInput.value = '';
      csvInput.dispatchEvent(new Event('change', { bubbles: true }));
    })()
  `);
  await new Promise(r => setTimeout(r, 100));

  // Now resolve the delayed read promise
  await session.eval(`
    (() => {
      if (window.__delayPromiseResolve) {
        window.__delayPromiseResolve();
      }
    })()
  `);
  await new Promise(r => setTimeout(r, 400));

  // Verify that the old delayed read did NOT reinstall the rules after being cleared!
  const rule0ValAfterClear = await session.eval('document.querySelector(\'[data-row-index="0"] [data-field="replace"]\')?.value || ""');
  console.log(`Rule 0 replace after cleared pending read: "${rule0ValAfterClear}"`);
  if (rule0ValAfterClear === 'DELAYED-A') {
    throw new Error(`Cleared pending CSV read reinstalled rules!`);
  }

  // Now test successful delayed read
  console.log(`Testing successful completed read with delay...`);
  await session.eval(`
    (() => {
      window.__delayActive = true;
      const csvContent = "Find,Replace\\r\\nOLD-A,FRESH-A\\r\\nOLD-B,FRESH-B\\r\\n";
      const file = new File([csvContent], "fresh-delayed.csv", { type: "text/csv" });
      const dt = new DataTransfer();
      dt.items.add(file);
      const csvInput = document.querySelector('[data-file="csv"]');
      csvInput.files = dt.files;
      csvInput.dispatchEvent(new Event('change', { bubbles: true }));
    })()
  `);
  await new Promise(r => setTimeout(r, 100));

  // Verify pending state again
  const secondDelayPending = await session.eval('window.__delayPending');
  if (!secondDelayPending) {
    throw new Error(`Second delayed read was not confirmed pending`);
  }

  // Release the delay
  await session.eval(`
    (() => {
      if (window.__delayPromiseResolve) {
        window.__delayPromiseResolve();
      }
    })()
  `);
  await new Promise(r => setTimeout(r, 400));

  const rule0ValAfterSuccess = await session.eval('document.querySelector(\'[data-row-index="0"] [data-field="replace"]\')?.value || ""');
  console.log(`Rule 0 replace after completed read: "${rule0ValAfterSuccess}"`);
  if (rule0ValAfterSuccess !== 'FRESH-A') {
    throw new Error(`Delayed CSV read failed to load rules! Expected FRESH-A, got "${rule0ValAfterSuccess}"`);
  }

  // Re-run, approve, validate, apply
  await session.eval('document.querySelector("[data-run]").click()');
  await new Promise(r => setTimeout(r, 400));
  await session.eval(`
    (() => {
      const sel = document.querySelector('[data-decision]');
      if (sel) { sel.value = 'APPROVED'; sel.dispatchEvent(new Event('change', { bubbles: true })); }
      document.querySelector('[data-validate]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 400));
  await session.eval('document.querySelector("[data-apply]").click()');
  await new Promise(r => setTimeout(r, 400));

  const exportRestored = await session.eval('document.querySelector("[data-export]").disabled');
  console.log(`Export restored after fresh import: disabled=${exportRestored}`);
  if (exportRestored) {
    throw new Error(`Failed to restore export eligibility after fresh CSV load!`);
  }

  // Restore File.prototype.text
  await session.eval(`
    (() => {
      File.prototype.text = window.__origFileText;
      delete window.__origFileText;
      delete window.__delayPromiseResolve;
      delete window.__delayActive;
      delete window.__delayPending;
    })()
  `);

  results.cases.case3_invalidation_pending_csv = {
    status: 'PASS',
    preAppliedStateVerified: true,
    revokedOnRuleEdit: exportRevokedOnRuleEdit,
    delayPendingPreconditionVerified: true,
    revokedWhilePending: exportWhilePending,
    clearWhilePendingSafe: rule0ValAfterClear !== 'DELAYED-A',
    eligibilityRestored: !exportRestored
  };

  // ==========================================
  // CASE 4: Process ownership & restraint/rigid data
  // ==========================================
  console.log(`\n[Case 4] Checking process ownership, reverse orientation, restraint/rigid data...`);
  await session.eval('document.querySelector(\'[data-tab="PROPERTY_TRANSFER"]\').click()');
  await new Promise(r => setTimeout(r, 300));

  // Helper to extract parsed table rows from the Property Transfer results area
  const parseResultSections = async () => {
    return await session.eval(`
      (() => {
        const sections = Array.from(document.querySelectorAll('[data-pt-results] section.pt-result'));
        return sections.map(sec => {
          const title = sec.querySelector('h3')?.textContent || '';
          const tables = Array.from(sec.querySelectorAll('table')).map(tbl => {
            const headers = Array.from(tbl.querySelectorAll('thead th')).map(th => th.textContent.trim());
            const rows = Array.from(tbl.querySelectorAll('tbody tr')).map(tr =>
              Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
            );
            return { headers, rows };
          });
          return { title, tables };
        });
      })()
    `);
  };

  // Inspect forward element 400->500
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-mode="ELEMENT"]').click();
      document.querySelector('[data-pt-input="sourceFrom"]').value = '400';
      document.querySelector('[data-pt-input="sourceTo"]').value = '500';
      document.querySelector('[data-pt-input="targetFrom"]').value = '840';
      document.querySelector('[data-pt-input="targetTo"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 300));
  const fwd400_500 = await session.eval('document.querySelector("[data-pt-results]").innerText');
  const fwd400Sections = await parseResultSections();
  const fwd400Src = fwd400Sections.find(s => s.title.includes('SOURCE'));
  if (!fwd400Src || !fwd400Src.title.includes('400 → TO 500') || !fwd400Src.title.includes('1 element(s)')) {
    throw new Error('Case 4: Forward 400->500 SOURCE section missing or has wrong element count');
  }
  const fwd400Row = fwd400Src.tables[0]?.rows[0];
  if (!fwd400Row) throw new Error('Case 4: Forward 400->500 table row missing');
  // Column assertions: [Element #, FROM → TO, Branch, T1 stored raw, P1 stored raw, Fluid density stored raw, Qualification]
  if (fwd400Row[0] !== '1' || fwd400Row[1] !== '400 → 500' || !fwd400Row[3].includes('200') || !fwd400Row[4].includes('30') || !fwd400Row[5].includes('1.01') || !fwd400Row[6].includes('HOLD')) {
    throw new Error(`Case 4: Forward 400->500 row mismatch: ${JSON.stringify(fwd400Row)}`);
  }

  // Inspect forward element 500->600
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-input="sourceFrom"]').value = '500';
      document.querySelector('[data-pt-input="sourceTo"]').value = '600';
      document.querySelector('[data-pt-input="targetFrom"]').value = '850';
      document.querySelector('[data-pt-input="targetTo"]').value = '860';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 300));
  const fwd500_600 = await session.eval('document.querySelector("[data-pt-results]").innerText');
  const fwd500Sections = await parseResultSections();
  const fwd500Src = fwd500Sections.find(s => s.title.includes('SOURCE'));
  if (!fwd500Src || !fwd500Src.title.includes('500 → TO 600') || !fwd500Src.title.includes('1 element(s)')) {
    throw new Error('Case 4: Forward 500->600 SOURCE section missing or has wrong element count');
  }
  const fwd500Row = fwd500Src.tables[0]?.rows[0];
  if (!fwd500Row) throw new Error('Case 4: Forward 500->600 table row missing');
  if (fwd500Row[0] !== '2' || fwd500Row[1] !== '500 → 600' || !fwd500Row[3].includes('180') || !fwd500Row[4].includes('20') || !fwd500Row[5].includes('1.01') || !fwd500Row[6].includes('HOLD')) {
    throw new Error(`Case 4: Forward 500->600 row mismatch: ${JSON.stringify(fwd500Row)}`);
  }

  // Inspect reverse orientation 500->400
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-input="sourceFrom"]').value = '500';
      document.querySelector('[data-pt-input="sourceTo"]').value = '400';
      document.querySelector('[data-pt-input="targetFrom"]').value = '840';
      document.querySelector('[data-pt-input="targetTo"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 300));
  const rev500_400 = await session.eval('document.querySelector("[data-pt-results]").innerText');
  const revSections = await parseResultSections();
  const revSrc = revSections.find(s => s.title.includes('SOURCE'));
  if (!revSrc || !revSrc.title.includes('0 element(s)') || (revSrc.tables[0] && revSrc.tables[0].rows.length !== 0)) {
    throw new Error('Case 4: Reverse 500->400 did not yield 0 elements');
  }

  console.log(`Forward 400->500 contains T1=200, P1=30, Density=1.01: ${fwd400_500.includes('200') && fwd400_500.includes('30') && fwd400_500.includes('1.01')}`);
  console.log(`Forward 500->600 contains T1=180, P1=20, Density=1.01: ${fwd500_600.includes('180') && fwd500_600.includes('20') && fwd500_600.includes('1.01')}`);
  console.log(`Reverse 500->400 matches 0 elements: ${rev500_400.includes('0 element(s)')}`);

  if (!fwd400_500.includes('200') || !fwd400_500.includes('30') || !fwd400_500.includes('1.01') ||
      !fwd500_600.includes('180') || !fwd500_600.includes('20') || !fwd500_600.includes('1.01') ||
      !rev500_400.includes('0 element(s)')) {
    throw new Error(`Element orientation or process ownership check failed!`);
  }

  // Inspect node 500
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-mode="NODE"]').click();
      document.querySelector('[data-pt-input="sourceNode"]').value = '500';
      document.querySelector('[data-pt-input="targetNode"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 300));
  const node500Text = await session.eval('document.querySelector("[data-pt-results]").innerText');
  const node500Sections = await parseResultSections();
  const node500Src = node500Sections.find(s => s.title.includes('SOURCE') && s.title.includes('Numeric Node 500'));
  if (!node500Src || !node500Src.tables[0]) throw new Error('Case 4: Node 500 SOURCE table missing');
  const nRows = node500Src.tables[0].rows;

  const restrantRow = nRows.find(r => r[0] === 'RESTRANT');
  const displmntRow = nRows.find(r => r[0] === 'DISPLMNT');
  const forcmntRow = nRows.find(r => r[0] === 'FORCMNT');
  const rigidRow = nRows.find(r => r[0] === 'RIGID');

  if (!restrantRow || restrantRow[1] !== '1' || !restrantRow[2].includes('Pointer 1') || !restrantRow[2].includes('Slot 1') || !restrantRow[3].includes('Type 1') || !restrantRow[3].includes('CNode 0')) {
    throw new Error(`Case 4: Node 500 RESTRANT row mismatch: ${JSON.stringify(restrantRow)}`);
  }
  if (!displmntRow || displmntRow[1] !== '1' || !displmntRow[2].includes('Pointer 1') || !displmntRow[2].includes('Specification 1')) {
    throw new Error(`Case 4: Node 500 DISPLMNT row mismatch: ${JSON.stringify(displmntRow)}`);
  }
  if (!forcmntRow || forcmntRow[1] !== '1' || !forcmntRow[2].includes('Pointer 1') || !forcmntRow[2].includes('Specification 1')) {
    throw new Error(`Case 4: Node 500 FORCMNT row mismatch: ${JSON.stringify(forcmntRow)}`);
  }
  if (!rigidRow || rigidRow[1] !== '1' || !rigidRow[2].includes('Pointer 1') || !rigidRow[3].includes('Weight raw 100')) {
    throw new Error(`Case 4: Node 500 RIGID row mismatch: ${JSON.stringify(rigidRow)}`);
  }

  const hasRestraint = node500Text.includes('RESTRANT') && node500Text.includes('Type 1') && node500Text.includes('CNode 0');
  const hasDisplacement = node500Text.includes('DISPLMNT') && node500Text.includes('Specification 1');
  const hasForce = node500Text.includes('FORCMNT') && node500Text.includes('Specification 1');
  const hasRigid = node500Text.includes('RIGID') && node500Text.includes('Weight raw 100');
  console.log(`Node 500 records: Restraint=${hasRestraint}, Displacement=${hasDisplacement}, Force=${hasForce}, Rigid=${hasRigid}`);

  if (!hasRestraint || !hasDisplacement || !hasForce || !hasRigid) {
    throw new Error(`Node 500 attachment check failed!`);
  }

  results.cases.case4_process_and_attachments = {
    status: 'PASS',
    forward400_500_distinct: true,
    forward400_500_fields: { t1: 200, p1: 30, density: 1.01, qual: 'HOLD' },
    forward500_600_distinct: true,
    forward500_600_fields: { t1: 180, p1: 20, density: 1.01, qual: 'HOLD' },
    reverseOrientationRejected: true,
    node500AttachmentsVerified: true,
    node500AttachmentRows: {
      restrant: restrantRow,
      displmnt: displmntRow,
      forcmnt: forcmntRow,
      rigid: rigidRow
    }
  };

  // ==========================================
  // CASE 5: Challenge negative/zero endpoints, out-of-bounds pointer, dormant residue
  // ==========================================
  console.log(`\n[Case 5] Challenging UI node-query search inputs vs mutated CII file intake...`);

  // Part 5A: UI search/query box validation
  await session.eval(`
    (() => {
      document.querySelector('[data-pt-mode="ELEMENT"]').click();
      document.querySelector('[data-pt-input="sourceFrom"]').value = '-400';
      document.querySelector('[data-pt-input="sourceTo"]').value = '500';
      document.querySelector('[data-pt-input="targetFrom"]').value = '840';
      document.querySelector('[data-pt-input="targetTo"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 300));
  const uiSearchNegStatus = await session.eval('document.querySelector("[data-pt-status]").textContent');
  console.log(`UI search negative endpoint status: "${uiSearchNegStatus}"`);

  await session.eval(`
    (() => {
      document.querySelector('[data-pt-input="sourceFrom"]').value = '0';
      document.querySelector('[data-pt-input="sourceTo"]').value = '500';
      document.querySelector('[data-pt-input="targetFrom"]').value = '840';
      document.querySelector('[data-pt-input="targetTo"]').value = '850';
      document.querySelector('[data-pt-run]').click();
    })()
  `);
  await new Promise(r => setTimeout(r, 300));
  const uiSearchZeroStatus = await session.eval('document.querySelector("[data-pt-status]").textContent');
  console.log(`UI search zero endpoint status: "${uiSearchZeroStatus}"`);

  // Part 5B: Mutated CII file intake checks
  // 1. Mutated CII with negative element endpoint
  const fileNegStatus = await session.eval(`
    (async () => {
      const dt = new DataTransfer();
      function b64ToUint8(b64) {
        const bin = atob(b64);
        const u = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
        return u;
      }
      const rawTxt = new TextDecoder().decode(b64ToUint8("${tgtBase64}"));
      const lines = rawTxt.split(/\\r\\n/);
      const elmIdx = lines.indexOf('#$ ELEMENTS');
      lines[elmIdx + 1] = '           -840          850            0            0            0            0';
      const file = new File([lines.join('\\r\\n')], "SYNTH_MUTATED_NEGATIVE_ENDPOINT.cii", { type: "application/octet-stream" });
      dt.items.add(file);
      const input = document.querySelector('[data-pt-file="target"]');
      input.files = dt.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(r => setTimeout(r, 400));
      return document.querySelector('[data-pt-status]').textContent;
    })()
  `);
  console.log(`File intake negative endpoint status: "${fileNegStatus}"`);

  // 2. Mutated CII with zero element endpoint
  const fileZeroStatus = await session.eval(`
    (async () => {
      const dt = new DataTransfer();
      function b64ToUint8(b64) {
        const bin = atob(b64);
        const u = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
        return u;
      }
      const rawTxt = new TextDecoder().decode(b64ToUint8("${tgtBase64}"));
      const lines = rawTxt.split(/\\r\\n/);
      const elmIdx = lines.indexOf('#$ ELEMENTS');
      lines[elmIdx + 1] = '              0          850            0            0            0            0';
      const file = new File([lines.join('\\r\\n')], "SYNTH_MUTATED_ZERO_ENDPOINT.cii", { type: "application/octet-stream" });
      dt.items.add(file);
      const input = document.querySelector('[data-pt-file="target"]');
      input.files = dt.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(r => setTimeout(r, 400));
      return document.querySelector('[data-pt-status]').textContent;
    })()
  `);
  console.log(`File intake zero endpoint status: "${fileZeroStatus}"`);

  // 3. Mutated CII with pointer beyond CONTROL count
  const pointerBeyondControl = await session.eval(`
    (async () => {
      const dt = new DataTransfer();
      function b64ToUint8(b64) {
        const bin = atob(b64);
        const u = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
        return u;
      }
      const rawTxt = new TextDecoder().decode(b64ToUint8("${tgtBase64}"));
      const lines = rawTxt.split(/\\r\\n/);
      const elmIdx = lines.indexOf('#$ ELEMENTS');
      lines[elmIdx + 13] = '            999            1            0            1            1            1';
      const file = new File([lines.join('\\r\\n')], "SYNTH_MUTATED_BAD_POINTER.cii", { type: "application/octet-stream" });
      dt.items.add(file);
      const input = document.querySelector('[data-pt-file="target"]');
      input.files = dt.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(r => setTimeout(r, 400));
      return document.querySelector('[data-pt-status]').textContent;
    })()
  `);
  console.log(`Pointer beyond CONTROL status: "${pointerBeyondControl}"`);

  // 4. Mutated CII with dormant nonzero restraint payload
  const dormantStatus = await session.eval(`
    (async () => {
      const dt = new DataTransfer();
      function b64ToUint8(b64) {
        const bin = atob(b64);
        const u = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
        return u;
      }
      const rawTxt = new TextDecoder().decode(b64ToUint8("${tgtBase64}"));
      const lines = rawTxt.split(/\\r\\n/);
      const rAt = lines.indexOf('#$ RESTRANT');
      lines[rAt + 6] = '          999.0            0            0            0            0            0';
      const file = new File([lines.join('\\r\\n')], "SYNTH_MUTATED_DORMANT_RESIDUE.cii", { type: "application/octet-stream" });
      dt.items.add(file);
      const input = document.querySelector('[data-pt-file="target"]');
      input.files = dt.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(r => setTimeout(r, 400));
      return {
        status: document.querySelector('[data-pt-status]').textContent,
        results: document.querySelector('[data-pt-results]').innerText
      };
    })()
  `);
  console.log(`Dormant residue status: "${dormantStatus.status}"`);
  console.log(`Dormant residue UNKNOWN evidence snippet:\n${dormantStatus.results.slice(0, 300)}...`);

  // Part 5C: Verify Property has NO Apply or Export button in the DOM
  const ptApplyButton = await session.eval('document.querySelector("[data-property-transfer-area] [data-apply]")');
  const ptExportButton = await session.eval('document.querySelector("[data-property-transfer-area] [data-export]")');
  console.log(`Property Apply button exists: ${!!ptApplyButton}, Export button exists: ${!!ptExportButton}`);

  results.cases.case5_negative_zero_dormant_challenges = (() => {
    const negBlocked = uiSearchNegStatus.includes('PROPERTY_NODE_NOT_CANONICAL');
    const zeroBlocked = uiSearchZeroStatus.includes('PROPERTY_NODE_INVALID');
    const fileNeg = fileNegStatus.includes('PROPERTY_ELEMENT_ENDPOINT_NEGATIVE');
    const fileZero = fileZeroStatus.includes('PROPERTY_ELEMENT_ZERO_ENDPOINT_UNQUALIFIED');
    const ptrOk = pointerBeyondControl.includes('PROPERTY_POINTER_RANGE_BEND');
    const dormOk = dormantStatus && dormantStatus.results && dormantStatus.results.includes('UNKNOWN input evidence') && dormantStatus.results.includes('PROPERTY_RESTRAINT_DORMANT_RESIDUE');
    const noBtns = !ptApplyButton && !ptExportButton;

    if (!negBlocked || !zeroBlocked || !fileNeg || !fileZero || !ptrOk || !dormOk || !noBtns) {
      throw new Error(`Case 5 challenge check failed: one or more challenges failed to reject or report unknown evidence (negBlocked=${negBlocked}, zeroBlocked=${zeroBlocked}, fileNeg=${fileNeg}, fileZero=${fileZero}, ptrOk=${ptrOk}, dormOk=${dormOk}, noBtns=${noBtns})`);
    }

    return {
      status: 'PASS',
      uiSearchValidation: {
        negativeBlocked: negBlocked,
        zeroBlocked: zeroBlocked
      },
      caiFileIntakeParsing: {
        negativeEndpointRejected: fileNeg,
        zeroEndpointHeld: fileZero,
        pointerBeyondControlRejected: ptrOk,
        dormantResidueReportedUnknown: dormOk
      },
      noApplyOrExportInProperty: noBtns
    };
  })();

  // ==========================================
  // CASE 6: Tab Controls, Error-Free Integrity, File Immutability, Network Safety
  // ==========================================
  console.log(`\n[Case 6] Exercising all tabs, verifying error-free integrity, checking fixture immutability and network requests...`);
  const tabsToClick = ['NORMAL', 'NODAL', 'PROPERTY_TRANSFER', 'LINE_NODE', 'GEOMETRY', 'CIIFR_GEO', 'CONFIG', 'NORMAL'];
  for (const tab of tabsToClick) {
    await session.eval(`document.querySelector('[data-tab="${tab}"]').click()`);
    await new Promise(r => setTimeout(r, 150));
  }

  // Check console errors
  const consoleErrors = (session.consoleLogs || []).filter(l => l.type === 'error' || l.level === 'error');
  const pageErrorsCount = session.pageErrors ? session.pageErrors.length : 0;
  const consoleErrorsCount = consoleErrors.length;
  console.log(`Uncaught page exceptions: ${pageErrorsCount}`);
  console.log(`Console error messages: ${consoleErrorsCount}`);
  console.log(`Total console logs: ${session.consoleLogs.length}`);

  // Re-verify public fixture files on disk
  const finalSrcBytes = fs.readFileSync(SRC_FIXTURE);
  const finalTgtBytes = fs.readFileSync(TGT_FIXTURE);
  const finalSrcHash = sha256(finalSrcBytes);
  const finalTgtHash = sha256(finalTgtBytes);

  console.log(`Fixture byte comparison:`);
  console.log(`  SOURCE: before=${initialSrcHash} after=${finalSrcHash} match=${initialSrcHash === finalSrcHash}`);
  console.log(`  TARGET: before=${initialTgtHash} after=${finalTgtHash} match=${initialTgtHash === finalTgtHash}`);

  if (finalSrcHash !== EXPECTED_SRC_SHA || finalTgtHash !== EXPECTED_TGT_SHA) {
    throw new Error(`Public fixture files were mutated on disk!`);
  }

  // Check network requests
  const externalRequests = session.networkRequests.filter(req => {
    try {
      const u = new URL(req.url);
      return u.hostname !== '127.0.0.1' && u.hostname !== 'localhost';
    } catch {
      return false;
    }
  });
  console.log(`External network requests during run: ${externalRequests.length}`);
  if (externalRequests.length > 0) {
    throw new Error(`External network traffic detected! ${JSON.stringify(externalRequests)}`);
  }

  results.cases.case6_integrity_immutability = (() => {
    const pageErrorsCount = session.pageErrors ? session.pageErrors.length : 0;
    const consoleErrorsCount = (session.consoleLogs || []).filter(l => l.type === 'error' || l.level === 'error').length;
    if (pageErrorsCount > 0) {
      throw new Error(`Case 6 failed: uncaught page exceptions detected (${pageErrorsCount}): ${JSON.stringify(session.pageErrors)}`);
    }
    if (consoleErrorsCount > 0) {
      throw new Error(`Case 6 failed: console errors detected (${consoleErrorsCount}): ${JSON.stringify(consoleErrors)}`);
    }
    return {
      status: 'PASS',
      pageErrorsCount: pageErrorsCount,
      consoleErrorsCount: consoleErrorsCount,
      fixturesUnchanged: true,
      externalRequestsCount: 0
    };
  })();

  await session.screenshot(`${session.browserName}-03-complete.png`);

  console.log(`\nAll 6 browser qualification cases PASSED on ${session.browserName}!`);
  return results;
}

async function main() {
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

  const fullReport = {
    timestamp: new Date().toISOString(),
    nodeVersion: process.version,
    platform: process.platform,
    runs: []
  };

  // Run on Microsoft Edge
  const edgeSession = new BrowserSession('Microsoft Edge', edgePath, 9444, 'edge-qual-profile');
  try {
    await edgeSession.start();
    const edgeResults = await runBrowserTests(edgeSession);
    fullReport.runs.push(edgeResults);
  } finally {
    await edgeSession.close();
  }

  // Run on Google Chrome
  const chromeSession = new BrowserSession('Google Chrome', chromePath, 9445, 'chrome-qual-profile');
  try {
    await chromeSession.start();
    const chromeResults = await runBrowserTests(chromeSession);
    fullReport.runs.push(chromeResults);
  } finally {
    await chromeSession.close();
  }

  const reportJson = JSON.stringify(fullReport, null, 2);
  fs.writeFileSync(path.join(EVIDENCE_DIR, 'browser_qualification_report.json'), reportJson);
  console.log(`\nBrowser qualification report written to: ${path.join(EVIDENCE_DIR, 'browser_qualification_report.json')}`);
}

main().catch(err => {
  console.error('\nFATAL QUALIFICATION RUNNER ERROR:', err);
  process.exit(1);
});
