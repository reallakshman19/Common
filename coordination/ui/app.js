/**
 * Coordination Cockpit — SPA
 * All data fetched on-demand from the Python REST server.
 * Paginated, lazy-loaded, virtual-scroll for large lists.
 * Multi-project via /api/projects + /api/manifest?project=ID
 */

// ── State ──────────────────────────────────────────────────────────────────
const S = {
  projects: [],          // [{id, name, description}]
  currentProject: null,  // project id string
  manifest: null,        // full manifest for current project
  currentView: 'overview',
  currentSession: 'ALL',
  currentTab: 'ALL',
  search: '',
  polls: {},             // view -> interval handles
  cache: {},             // simple request-level cache
};

// ── API helpers ─────────────────────────────────────────────────────────────
const BASE = '';  // same origin

async function api(path, params = {}) {
  if (S.currentProject && !params.project) params.project = S.currentProject;
  const qs = new URLSearchParams(params).toString();
  const url = `${BASE}/api/${path}${qs ? '?' + qs : ''}`;
  const cacheKey = url;
  if (S.cache[cacheKey] && Date.now() - S.cache[cacheKey].ts < 10_000) {
    return S.cache[cacheKey].data;
  }
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  const data = await res.json();
  S.cache[cacheKey] = { ts: Date.now(), data };
  return data;
}

function clearCache() { S.cache = {}; }

// ── Init ────────────────────────────────────────────────────────────────────
async function init() {
  setupEvents();

  try {
    S.projects = await api('projects', {});
  } catch (e) {
    setStatus('OFFLINE – start server', true);
    renderOfflineBanner();
    return;
  }

  // Populate project select
  const sel = $('projSelect');
  sel.innerHTML = S.projects.map(p =>
    `<option value="${p.id}">${esc(p.name)}</option>`
  ).join('');
  S.currentProject = S.projects[0]?.id;
  sel.value = S.currentProject;

  await loadProject();
  startPolling();
}

async function loadProject(force = false) {
  try {
    if (force) clearCache();
    const data = await api('manifest');
    S.manifest = data;
    const proj = data.project;
    $('repoLink').href = proj.repo_url || '#';
    $('repoLink').textContent = proj.name;
    $('commitChip').textContent = (proj.commit || '').slice(0, 8) || '';
    updateKPIs(data.summary);
    renderSidebar(data.sessions);
    renderView(S.currentView, true);
    setStatus(`Synced ${new Date().toLocaleTimeString()}`, false);
  } catch (e) {
    setStatus('Server error', true);
  }
}

// ── Events ───────────────────────────────────────────────────────────────────
function setupEvents() {
  // Nav tabs
  qsa('.ntab').forEach(t => t.addEventListener('click', () => {
    qsa('.ntab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    S.currentView = t.dataset.view;
    renderView(S.currentView, true);
  }));

  // Project select
  $('projSelect').addEventListener('change', e => {
    S.currentProject = e.target.value;
    S.manifest = null;
    S.currentSession = 'ALL';
    S.currentTab = 'ALL';
    clearCache();
    loadProject();
  });

  // Search
  let searchTimer;
  $('globalSearch').addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      S.search = e.target.value.trim();
      renderView(S.currentView, true);
    }, 280);
  });

  // Sync
  $('syncBtn').addEventListener('click', () => loadProject(true));

  // Theme
  $('themeBtn').addEventListener('click', () => {
    const body = document.body;
    body.classList.toggle('light');
    document.querySelector('html').dataset.theme = body.classList.contains('light') ? 'light' : 'dark';
  });

  // Modal
  $('modal-close').addEventListener('click', closeModal);
  $('modal-bg').addEventListener('click', e => { if (e.target.id === 'modal-bg') closeModal(); });
}

// ── KPIs ─────────────────────────────────────────────────────────────────────
function updateKPIs(summary) {
  const { total_decisions: d, total_checkpoints: c, total_handovers: h,
          total_files: f, total_tabs: t, decision_statuses: st } = summary;
  $('cnt-decisions').textContent = d;
  $('cnt-checkpoints').textContent = c;
  $('cnt-handovers').textContent = h;

  const open = st?.OPEN || 0, ans = st?.ANSWERED || 0;

  if (S.currentView === 'overview') {
    const strip = el('div', 'kpi-strip');
    strip.innerHTML = [
      kpi('Tabs', t, `${summary.total_sessions} Sessions`),
      kpi('Decisions', d, `${open} Open · ${ans} Answered`),
      kpi('Handovers', h, 'BuddyRunner artifacts'),
      kpi('Checkpoints', c, 'Milestones & plan revisions'),
      kpi('Files', f, 'All coordination assets'),
    ].join('');
    setContent([strip]);
  }
}

function kpi(label, val, sub) {
  return `<div class="kpi"><div class="kpi-lbl">${label}</div>
  <div class="kpi-val">${val}</div>
  <div class="kpi-sub">${esc(sub)}</div></div>`;
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
function renderSidebar(sessions) {
  const sb = $('sidebar');
  sb.innerHTML = '';

  sessions.forEach(sess => {
    const lbl = el('div', 'sess-label');
    lbl.textContent = sess.id.replace('Session_', '');
    sb.appendChild(lbl);

    sess.tabs.forEach(tab => {
      const node = el('div', 'tab-node');
      if (tab.name === S.currentTab && sess.id === S.currentSession) {
        node.classList.add('active');
      }
      const total = Object.values(tab.counts || {}).reduce((a, b) => a + b, 0);
      node.innerHTML = `<span class="tn">${esc(tab.title.replace(/Tab\d+_?/, ''))}</span>
        <span class="tab-ct">${total}</span>`;
      node.title = tab.name;
      node.addEventListener('click', () => {
        qsa('.tab-node').forEach(n => n.classList.remove('active'));
        node.classList.add('active');
        S.currentSession = sess.id;
        S.currentTab = tab.name;
        clearCache();
        renderView(S.currentView, true);
      });
      sb.appendChild(node);
    });
  });

  // "All" reset
  const allNode = el('div', 'tab-node');
  allNode.textContent = '⊞ All Sessions';
  allNode.style.cssText = 'margin-top:.5rem; color: var(--accent);';
  allNode.addEventListener('click', () => {
    S.currentSession = 'ALL'; S.currentTab = 'ALL';
    qsa('.tab-node').forEach(n => n.classList.remove('active'));
    clearCache();
    renderView(S.currentView, true);
  });
  sb.appendChild(allNode);
}

// ── View router ───────────────────────────────────────────────────────────────
function renderView(view, reset = false) {
  if (reset) clearCache();
  switch (view) {
    case 'overview':    renderOverview(); break;
    case 'decisions':   renderDecisions(1); break;
    case 'qrt':         renderQrt(); break;
    case 'checkpoints': renderCheckpoints(1); break;
    case 'handovers':   renderHandovers(1); break;
    case 'receipts':    renderReceipts(); break;
    case 'explorer':    renderExplorer(); break;
  }
}

// ── Overview ─────────────────────────────────────────────────────────────────
function renderOverview() {
  if (!S.manifest) return;
  const strip = el('div', 'kpi-strip');
  const sum = S.manifest.summary;
  const st = sum.decision_statuses || {};
  strip.innerHTML = [
    kpi('Tabs', sum.total_tabs, `${sum.total_sessions} Sessions`),
    kpi('Decisions', sum.total_decisions, `${st.OPEN||0} Open · ${st.ANSWERED||0} Answered`),
    kpi('Handovers', sum.total_handovers, 'BuddyRunner artifacts'),
    kpi('Checkpoints', sum.total_checkpoints, 'Milestones & plan revisions'),
    kpi('Files', sum.total_files, 'All coordination assets'),
  ].join('');

  const sessContainer = el('div');
  const sessions = S.manifest.sessions || [];
  const filtered = S.currentSession === 'ALL' ? sessions
    : sessions.filter(s => s.id === S.currentSession);

  filtered.forEach(sess => {
    const h3 = el('div', 'section-title');
    h3.innerHTML = `📁 ${esc(sess.id.replace('Session_', 'Session '))} <span class="chip">${sess.tabs.length} tabs</span>`;

    const grid = el('div', 'tab-grid');
    sess.tabs.forEach(tab => {
      if (S.search) {
        const txt = (tab.name + tab.title + tab.chat + tab.issue).toLowerCase();
        if (!txt.includes(S.search.toLowerCase())) return;
      }
      const card = el('div', 'tab-card');
      const statusClass = statusBadge(tab.status);
      const cnt = tab.counts || {};
      card.innerHTML = `
        <div class="tc-head">
          <div class="tc-title">${esc(tab.title.replace(/Tab\d+_?/, ''))}</div>
          <span class="badge ${statusClass}">${esc(tab.status)}</span>
        </div>
        <div class="tc-meta">
          ${tab.chat ? `<span>chat: ${esc(tab.chat)}</span>` : ''}
          ${tab.issue ? `<span>issue: ${esc(tab.issue)}</span>` : ''}
          ${tab.plan ? `<span>plan: ${esc(tab.plan)}</span>` : ''}
        </div>
        <div class="tc-stats">
          <div><div class="ts-num">${cnt.decisions||0}</div><div class="ts-lbl">Decisions</div></div>
          <div><div class="ts-num">${cnt.checkpoints||0}</div><div class="ts-lbl">Checkpoints</div></div>
          <div><div class="ts-num">${cnt.handovers||0}</div><div class="ts-lbl">Handovers</div></div>
          <div><div class="ts-num">${cnt.evidence||0}</div><div class="ts-lbl">Evidence</div></div>
        </div>`;
      card.addEventListener('click', () => openTabModal(sess.id, tab));
      grid.appendChild(card);
    });

    const wrap = el('div');
    wrap.appendChild(h3);
    wrap.appendChild(grid);
    sessContainer.appendChild(wrap);
  });

  setContent([strip, sessContainer]);
}

// ── Decisions — Virtual Scroll ────────────────────────────────────────────────
const DEC = { items: [], page: 1, limit: 80, total: 0, pages: 1,
              filterStatus: 'ALL', vScroll: null };

async function renderDecisions(page = 1) {
  DEC.page = page;
  const params = { page, limit: DEC.limit };
  if (S.currentSession !== 'ALL') params.session = S.currentSession;
  if (S.currentTab !== 'ALL') params.tab = S.currentTab;
  if (DEC.filterStatus !== 'ALL') params.status = DEC.filterStatus;
  if (S.search) params.q = S.search;

  let data;
  try { data = await api('decisions', params); }
  catch { return; }

  DEC.items = data.items;
  DEC.total = data.total;
  DEC.pages = data.pages;

  // Build controls
  const ctrl = el('div', 'ctrl-bar');
  ctrl.innerHTML = `
    <label>Status</label>
    <select id="decStatusFilter">
      ${['ALL','OPEN','ANSWERED','APPROVAL EVIDENCE','HOLD','OWNER CORRECTION','VERIFIED','UNKNOWN']
          .map(s => `<option value="${s}" ${s===DEC.filterStatus?'selected':''}>${s}</option>`).join('')}
    </select>
    <span class="spacer"></span>
    <span class="dim mono">${data.total} decisions</span>`;
  ctrl.querySelector('#decStatusFilter').addEventListener('change', e => {
    DEC.filterStatus = e.target.value;
    renderDecisions(1);
  });

  // Virtual scroll list
  const colHeaders = ['Date','Tab','ID','Status','Description','Link'];
  const colWidths = [95, 130, 110, 120, null, 50]; // null = flex:1
  const wrap = buildVList(DEC.items, colHeaders, colWidths, renderDecRow, d => openDecModal(d));

  // Pagination
  const pager = buildPager(DEC.page, DEC.pages, p => renderDecisions(p));

  setContent([ctrl, wrap, pager]);
}

function renderDecRow(d, wrap) {
  const date = el('div', 'vrow-date'); date.textContent = d.date || '—';
  const tab = el('div', 'vrow-tab');
  tab.innerHTML = `<strong class="mono" style="font-size:.75rem;color:var(--accent)">${esc(d.tab.replace(/Tab\d+_?/, ''))}</strong>`;
  const id = el('div', 'vrow-id'); id.textContent = d.id || '—';
  const st = el('div', 'vrow-status');
  st.innerHTML = `<span class="badge ${statusBadge(d.status)}">${esc(d.status)}</span>`;
  const desc = el('div', 'vrow-desc'); desc.textContent = d.description;
  const link = el('div', 'vrow-link');
  if (d.link) link.innerHTML = `<a href="${esc(d.link)}" target="_blank" rel="noopener">↗</a>`;
  wrap.append(date, tab, id, st, desc, link);
}

function openDecModal(d) {
  modalOpen(`Decision: ${d.id || d.status}`, `
    <div class="row" style="margin-bottom:.75rem;flex-wrap:wrap;gap:.5rem;">
      <span class="badge ${statusBadge(d.status)}">${esc(d.status)}</span>
      <span class="chip">${esc(d.session)} / ${esc(d.tab)}</span>
      ${d.chat ? `<span class="chip">chat: ${esc(d.chat)}</span>` : ''}
      ${d.date ? `<span class="chip">${esc(d.date)}</span>` : ''}
    </div>
    <p style="line-height:1.6;margin-bottom:1rem;">${esc(d.description)}</p>
    ${d.link ? `<a href="${esc(d.link)}" target="_blank" rel="noopener"
      style="color:var(--accent);font-weight:600;">↗ Open evidence link</a>` : ''}
  `);
}

// ── QRT 28-Cell ───────────────────────────────────────────────────────────────
async function renderQrt() {
  let board;
  try { board = await api('qrt'); }
  catch { setContent([emptyEl('QRT board not found. Start the server.')]);return; }

  const cells = board.cells || [];
  const demands = ['RETRIEVE','REPRESENT','EXPLAIN','MODEL','JUSTIFY','COMPARE','GENERALIZE'];
  const bands = ['D1','D2','D3','D4'];

  const outer = el('div', 'qrt-outer');
  const h = el('div', 'section-title');
  h.innerHTML = `🧩 IMO 28-Cell QRT Board
    <span class="badge b-hold">ACCEPTED: 0/28</span>
    <span class="badge b-active">BANDS: D1–D4</span>`;

  const grid = el('div', 'qrt-grid');

  // Column headers
  grid.appendChild(el('div')); // corner
  demands.forEach(d => {
    const ch = el('div', 'qrt-ch');
    ch.textContent = d;
    grid.appendChild(ch);
  });

  bands.forEach(band => {
    const rh = el('div', 'qrt-rh');
    rh.textContent = band;
    grid.appendChild(rh);

    demands.forEach(dem => {
      const cid = `QRT-${dem}-${band}`;
      const c = cells.find(x => x.id === cid) || { id: cid, band, demand: dem, agent: `AGENT-${band}`, state: 'UNSTARTED' };
      const cell = el('div', 'qrt-cell');
      const stClass = `st-${c.state || 'UNSTARTED'}`;
      cell.innerHTML = `<div>
        <div class="qrt-cid">${esc(c.id)}</div>
        <span class="qrt-state ${stClass}">${esc(c.state || 'UNSTARTED')}</span>
      </div>
      <div class="qrt-agent">${esc(c.agent || '')}</div>`;
      cell.addEventListener('click', () => modalOpen(`QRT: ${c.id}`,
        `<pre class="code">${esc(JSON.stringify(c, null, 2))}</pre>`));
      grid.appendChild(cell);
    });
  });

  outer.appendChild(h);
  outer.appendChild(grid);
  setContent([outer]);
}

// ── Checkpoints — paginated timeline ─────────────────────────────────────────
async function renderCheckpoints(page = 1) {
  const params = { page, limit: 40 };
  if (S.currentSession !== 'ALL') params.session = S.currentSession;
  if (S.currentTab !== 'ALL') params.tab = S.currentTab;
  if (S.search) params.q = S.search;

  let data;
  try { data = await api('checkpoints', params); }
  catch { return; }

  const tl = el('div', 'timeline');
  data.items.forEach(cp => {
    const item = el('div', 'titem');
    const dot = el('div', 'titem-dot');
    const head = el('div', 'titem-head');
    const title = el('div', 'titem-title');
    title.textContent = cp.title;
    const meta = el('div', 'row');
    meta.innerHTML = `<span class="chip">${esc(cp.tab)}</span>
      ${cp.chat ? `<span class="chip dim">chat: ${esc(cp.chat)}</span>` : ''}`;
    head.appendChild(title);
    head.appendChild(meta);
    const body = el('div', 'titem-body');
    body.textContent = cp.body || '';
    item.appendChild(dot);
    item.appendChild(head);
    item.appendChild(body);
    item.addEventListener('click', () => modalOpen(cp.title,
      `<div class="row" style="margin-bottom:.75rem;">
        <span class="chip">${esc(cp.session)} / ${esc(cp.tab)}</span>
        ${cp.chat ? `<span class="chip">chat: ${esc(cp.chat)}</span>` : ''}
       </div>
       <pre class="code" style="white-space:pre-wrap;">${esc(cp.body || '')}</pre>`));
    tl.appendChild(item);
  });

  const pager = buildPager(page, data.pages, p => renderCheckpoints(p));
  const info = el('div', 'ctrl-bar');
  info.innerHTML = `<span class="dim mono">${data.total} checkpoints</span>`;
  setContent([info, tl, pager]);
}

// ── Handovers ─────────────────────────────────────────────────────────────────
async function renderHandovers(page = 1) {
  const params = { page, limit: 60 };
  if (S.currentSession !== 'ALL') params.session = S.currentSession;
  if (S.currentTab !== 'ALL') params.tab = S.currentTab;
  if (S.search) params.q = S.search;

  let data;
  try { data = await api('handovers', params); }
  catch { return; }

  const ctrl = el('div', 'ctrl-bar');
  ctrl.innerHTML = `<span class="dim mono">${data.total} handovers</span>`;

  const list = el('div');
  data.items.forEach(h => {
    const item = el('div', 'ho-item');
    item.innerHTML = `
      <div>
        <div class="ho-name">${esc(h.filename)}</div>
        <div class="ho-sub">${esc(h.session)} / ${esc(h.tab)}
          ${h.handover_id ? ` · <span class="mono">${esc(h.handover_id)}</span>` : ''}
        </div>
      </div>
      <div class="col" style="align-items:flex-end;">
        <span class="badge b-active">${esc(h.stage)}</span>
        <span class="dim" style="font-size:.72rem;">${h.size.toLocaleString()} B · ${h.updated}</span>
      </div>`;
    item.addEventListener('click', () => loadFileModal(h.path, h.filename));
    list.appendChild(item);
  });

  const pager = buildPager(page, data.pages, p => renderHandovers(p));
  setContent([ctrl, list, pager]);
}

// ── Receipts ───────────────────────────────────────────────────────────────────
async function renderReceipts() {
  let tab;
  try { tab = await api('tab', { session: S.currentSession === 'ALL' ? 'Session_Oct09' : S.currentSession,
                                  tab: S.currentTab === 'ALL' ? 'Tab2_imo_core2_core1a' : S.currentTab }); }
  catch { tab = { json_receipts: [] }; }

  // Also get all from manifest
  const allReceipts = [];
  (S.manifest?.sessions || []).forEach(sess => {
    sess.tabs.forEach(t => {
      // We don't have receipts in manifest — fetch tab on click
    });
  });

  const grid = el('div', 'receipts-grid');
  const receipts = (tab.json_receipts || []).filter(r => {
    if (!S.search) return true;
    return (r.filename + r.schema).toLowerCase().includes(S.search.toLowerCase());
  });

  if (!receipts.length) {
    const emptyDiv = emptyEl('Select a specific tab in the sidebar to view its JSON receipts, or use the File Explorer.');
    setContent([emptyDiv]);
    return;
  }

  receipts.forEach(r => {
    const card = el('div', 'tab-card');
    card.innerHTML = `
      <div class="tc-head">
        <div class="tc-title" style="font-size:.85rem;">${esc(r.filename)}</div>
        <span class="badge b-answered" style="font-size:.65rem;">${esc(r.schema).slice(0,20)}</span>
      </div>
      <div class="dim mono" style="font-size:.7rem;">${r.size.toLocaleString()} bytes</div>`;
    card.addEventListener('click', () => modalOpen(r.filename,
      `<span class="chip" style="margin-bottom:.75rem;display:inline-block;">${esc(r.schema)}</span>
       <pre class="code">${esc(JSON.stringify(r.data, null, 2))}</pre>`));
    grid.appendChild(card);
  });
  setContent([grid]);
}

// ── File Explorer ─────────────────────────────────────────────────────────────
async function renderExplorer() {
  let data;
  try { data = await api('files', { limit: 300, ...(S.search ? { q: S.search } : {}) }); }
  catch { return; }

  const layout = el('div', 'explorer-layout');
  const sidebar = el('div', 'file-sidebar');
  const pane = el('div', 'file-pane');
  pane.innerHTML = '<p class="muted">Click a file on the left to view its content.</p>';

  const extIcon = ext => ({ '.md': '📄', '.json': '🧾', '.log': '📝', '.csv': '📊' }[ext] || '📎');

  data.items.forEach(f => {
    const node = el('div', 'fnode');
    node.innerHTML = `<span>${extIcon(f.ext)}</span><span title="${esc(f.path)}">${esc(f.path)}</span>`;
    node.addEventListener('click', async () => {
      qsa('.fnode').forEach(n => n.classList.remove('active'));
      node.classList.add('active');
      pane.innerHTML = '<p class="muted">Loading…</p>';
      try {
        const res = await fetch(`/api/file?project=${S.currentProject}&path=${encodeURIComponent(f.path)}`);
        if (!res.ok) throw new Error(res.status);
        const text = await res.text();
        pane.innerHTML = `<div class="row" style="margin-bottom:.75rem;">
            <strong class="mono">${esc(f.name)}</strong>
            <span class="chip dim">${f.size.toLocaleString()} B</span>
          </div>
          <pre class="code">${esc(text)}</pre>`;
      } catch {
        pane.innerHTML = '<p class="muted">Failed to load file content.</p>';
      }
    });
    sidebar.appendChild(node);
  });

  if (data.pages > 1) {
    const note = el('div', 'dim');
    note.style.cssText = 'font-size:.72rem;padding:.5rem;';
    note.textContent = `Showing ${data.limit} of ${data.total} files. Use search to narrow down.`;
    sidebar.appendChild(note);
  }

  layout.append(sidebar, pane);
  setContent([layout]);
}

// ── Virtual scroll list builder ──────────────────────────────────────────────
const ROW_H = 58;

function buildVList(items, cols, widths, renderRow, onClick) {
  const wrap = el('div', 'vlist-wrap');

  // Header
  const head = el('div', 'vlist-head');
  cols.forEach((c, i) => {
    const h = el('div');
    h.textContent = c;
    if (widths[i]) h.style.width = widths[i] + 'px';
    else h.style.flex = '1';
    head.appendChild(h);
  });
  wrap.appendChild(head);

  // Viewport
  const vp = el('div', 'vlist-viewport');
  const spacer = el('div', 'vlist-spacer');
  spacer.style.height = (items.length * ROW_H) + 'px';
  vp.appendChild(spacer);
  wrap.appendChild(vp);

  let rendered = {};

  function paint() {
    const scrollTop = vp.scrollTop;
    const viewH = vp.clientHeight;
    const startIdx = Math.max(0, Math.floor(scrollTop / ROW_H) - 3);
    const endIdx = Math.min(items.length, Math.ceil((scrollTop + viewH) / ROW_H) + 3);

    // Remove out-of-view rows
    Object.keys(rendered).forEach(k => {
      const i = +k;
      if (i < startIdx || i >= endIdx) { rendered[k].remove(); delete rendered[k]; }
    });

    // Add new rows
    for (let i = startIdx; i < endIdx; i++) {
      if (rendered[i]) continue;
      const row = el('div', 'vrow');
      row.style.top = (i * ROW_H) + 'px';
      row.style.height = ROW_H + 'px';
      renderRow(items[i], row);
      row.addEventListener('click', () => onClick && onClick(items[i]));
      vp.appendChild(row);
      rendered[i] = row;
    }
  }

  vp.addEventListener('scroll', paint, { passive: true });
  requestAnimationFrame(paint);
  return wrap;
}

// ── Pagination bar ────────────────────────────────────────────────────────────
function buildPager(page, pages, onPage) {
  if (pages <= 1) return el('div');
  const bar = el('div', 'pagination');
  const prev = el('button', 'btn'); prev.textContent = '← Prev';
  prev.disabled = page <= 1;
  prev.addEventListener('click', () => onPage(page - 1));
  const info = el('span', 'page-info');
  info.textContent = `Page ${page} / ${pages}`;
  const next = el('button', 'btn'); next.textContent = 'Next →';
  next.disabled = page >= pages;
  next.addEventListener('click', () => onPage(page + 1));
  bar.append(prev, info, next);
  return bar;
}

// ── Modals ────────────────────────────────────────────────────────────────────
function modalOpen(title, html) {
  $('modal-title').textContent = title;
  $('modal-body').innerHTML = html;
  $('modal-bg').classList.add('open');
}
function closeModal() { $('modal-bg').classList.remove('open'); }

async function loadFileModal(relPath, title) {
  modalOpen(title || relPath, '<p class="muted">Loading…</p>');
  try {
    const res = await fetch(`/api/file?project=${S.currentProject}&path=${encodeURIComponent(relPath)}`);
    const text = await res.text();
    $('modal-body').innerHTML = `<pre class="code">${esc(text)}</pre>`;
  } catch {
    $('modal-body').innerHTML = '<p class="muted">Could not load file content.</p>';
  }
}

function openTabModal(sessId, tab) {
  const cnt = tab.counts || {};
  modalOpen(`${sessId} / ${tab.title}`, `
    <div class="row" style="gap:.5rem;margin-bottom:1rem;flex-wrap:wrap;">
      <span class="badge ${statusBadge(tab.status)}">${esc(tab.status)}</span>
      ${tab.chat ? `<span class="chip">chat: ${esc(tab.chat)}</span>` : ''}
      ${tab.issue ? `<span class="chip">issue: ${esc(tab.issue)}</span>` : ''}
      ${tab.plan ? `<span class="chip">plan: ${esc(tab.plan)}</span>` : ''}
    </div>
    <div class="kpi-strip" style="margin-bottom:1rem;">
      ${kpi('Decisions', cnt.decisions||0, '')}
      ${kpi('Checkpoints', cnt.checkpoints||0, '')}
      ${kpi('Handovers', cnt.handovers||0, '')}
      ${kpi('Evidence', cnt.evidence||0, '')}
    </div>
    <p class="muted" style="font-size:.82rem;">
      Click a view in the top navigation bar and use the sidebar to filter this tab's data.
    </p>`);
}

// ── Polling ────────────────────────────────────────────────────────────────────
let pollTimer;
function startPolling() {
  clearInterval(pollTimer);
  pollTimer = setInterval(() => loadProject(true), 15_000);
}

// ── Status / connection ───────────────────────────────────────────────────────
function setStatus(text, offline) {
  $('statusText').textContent = text;
  $('statusDot').className = 'dot' + (offline ? ' offline' : '');
}

function renderOfflineBanner() {
  setContent([el('div', 'empty', `
    <h2 style="margin-bottom:.75rem;">🔌 Server not running</h2>
    <p>Start the Python server to use the live dashboard:</p>
    <pre class="code" style="margin-top:1rem;text-align:left;display:inline-block;">
python coordination_ui.py --serve</pre>`)]);
}

// ── DOM helpers ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const qsa = sel => [...document.querySelectorAll(sel)];

function el(tag, cls = '', inner = '') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (inner) e.innerHTML = inner;
  return e;
}

function emptyEl(msg) {
  const d = el('div', 'empty');
  d.textContent = msg;
  return d;
}

function setContent(nodes) {
  const c = $('content');
  c.innerHTML = '';
  nodes.forEach(n => n && c.appendChild(n));
}

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function statusBadge(status) {
  if (!status) return 'b-unknown';
  const s = status.toUpperCase();
  if (s.includes('OPEN')) return 'b-open';
  if (s.includes('ANSWERED') || s.includes('APPROVAL')) return 'b-answered';
  if (s.includes('HOLD')) return 'b-hold';
  if (s.includes('ACTIVE') || s.includes('VERIFIED')) return 'b-active';
  return 'b-unknown';
}

// ── Boot ────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', init);
