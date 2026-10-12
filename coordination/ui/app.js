/**
 * Control Tower Cockpit v3 — Hardened Front-End Application
 * Dual-Mode: Local Stored Projection API vs Static Published Snapshot.
 * Zero external dependencies. Strict CSP and safe DOM rendering.
 */
(function() {
  'use strict';

  // Application State
  const state = {
    mode: 'DETECTING', // 'LOCAL_API' | 'STATIC_SNAPSHOT' | 'ERROR'
    currentView: 'portfolio',
    currentProject: '',
    searchQuery: '',
    metadata: {},
    viewsData: {
      portfolio: [],
      works: [],
      assignments: [],
      evidence: [],
      recovery: [],
      unassigned: []
    }
  };

  // DOM Elements
  const el = {
    modeChip: document.getElementById('modeChip'),
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    telMode: document.getElementById('telMode'),
    telGeneration: document.getElementById('telGeneration'),
    telAsOf: document.getElementById('telAsOf'),
    telStaleness: document.getElementById('telStaleness'),
    projSelect: document.getElementById('projSelect'),
    globalSearch: document.getElementById('globalSearch'),
    refreshBtn: document.getElementById('refreshBtn'),
    themeBtn: document.getElementById('themeBtn'),
    navtabs: document.getElementById('navtabs'),
    content: document.getElementById('content'),
    tabUnassigned: document.getElementById('tabUnassigned')
  };

  /**
   * Validates and sanitizes URLs before setting href.
   * Only permits https: links to github.com or trusted domains.
   */
  function safeHref(url) {
    if (!url || typeof url !== 'string') return null;
    const stripped = url.trim();
    if (!stripped.startsWith('https://')) return null;
    try {
      const parsed = new URL(stripped);
      if (parsed.protocol !== 'https:') return null;
      const host = parsed.hostname.toLowerCase();
      if (host === 'github.com' || host === 'raw.githubusercontent.com' || host.endsWith('.github.com')) {
        return stripped;
      }
    } catch (e) {
      return null;
    }
    return null;
  }

  /**
   * Helper to construct safe DOM elements with textContent.
   */
  function h(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'className') {
        node.className = v;
      } else if (k === 'textContent') {
        node.textContent = v;
      } else if (k === 'href') {
        const safe = safeHref(v);
        if (safe) {
          node.setAttribute('href', safe);
          node.setAttribute('target', '_blank');
          node.setAttribute('rel', 'noopener noreferrer');
        }
      } else if (k.startsWith('data-')) {
        node.setAttribute(k, v);
      } else if (k === 'title') {
        node.title = v;
      }
    }
    if (typeof children === 'string') {
      node.textContent = children;
    } else if (Array.isArray(children)) {
      for (const c of children) {
        if (typeof c === 'string') {
          node.appendChild(document.createTextNode(c));
        } else if (c instanceof Node) {
          node.appendChild(c);
        }
      }
    }
    return node;
  }

  /**
   * Computes age in seconds and determines freshness state.
   */
  function evaluateFreshness(asOfUtc) {
    if (!asOfUtc) return { state: 'UNKNOWN', label: 'Unknown' };
    try {
      const then = new Date(asOfUtc);
      const now = new Date();
      const diffSec = Math.floor((now - then) / 1000);
      if (diffSec < 0) return { state: 'UNKNOWN', label: 'Future timestamp' };
      if (diffSec <= 1800) return { state: 'FRESH', label: `${diffSec}s ago` };
      if (diffSec <= 7200) return { state: 'STALE', label: `${Math.floor(diffSec / 60)}m ago (STALE)` };
      return { state: 'STALE', label: `${Math.floor(diffSec / 3600)}h ago (STALE)` };
    } catch (e) {
      return { state: 'UNKNOWN', label: 'Invalid date' };
    }
  }

  /**
   * Badge element generator.
   */
  function badge(text, type = 'gray') {
    return h('span', { className: `badge badge-${type}`, textContent: text || '–' });
  }

  /**
   * Determines badge style for various statuses.
   */
  function statusBadge(val) {
    const str = String(val || '').toUpperCase();
    if (str === 'REACHABLE' || str === 'EXACT_HEAD_PASSED' || str === 'ALIVE' || str === 'FRESH' || str === 'ACTIVE' || str === 'ATTRIBUTED') {
      return badge(str, 'green');
    }
    if (str === 'RATE_LIMITED' || str === 'OLD_HEAD' || str === 'PENDING' || str === 'STALE' || str === 'UNATTRIBUTED') {
      return badge(str, 'amber');
    }
    if (str === 'FAILED' || str === 'PROBE_FAILURE' || str === 'LOADFAIL' || str === 'NOBOX') {
      return badge(str, 'red');
    }
    return badge(str || 'UNKNOWN', 'gray');
  }

  /**
   * Data Loading: Dual Mode Detection
   */
  async function loadData() {
    el.content.replaceChildren(h('div', { className: 'loading-spinner', textContent: 'Loading Control Tower projections…' }));

    const isLocalHost = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';

    if (isLocalHost) {
      try {
        await loadLocalApi();
        return;
      } catch (err) {
        console.warn('Local projection API unavailable:', err);
        showError('LOCAL STORED PROJECTION UNAVAILABLE: Local projection database is not materialized or server is unavailable.');
        return;
      }
    }

    // Static mode for GitHub Pages or static hosts
    try {
      await loadStaticSnapshot();
    } catch (err) {
      console.error('Failed to load static public snapshot:', err);
      showError('STATIC PUBLISHED SNAPSHOT UNAVAILABLE: Could not load ./public_snapshot.json');
    }
  }

  /**
   * Loads from pre-materialized local read API.
   */
  async function loadLocalApi() {
    const basePath = window.location.pathname.includes('/ui') ? '../api/v3/projections' : '/api/v3/projections';
    const initRes = await fetch(`${basePath}?view=portfolio&limit=50`);
    if (!initRes.ok) {
      throw new Error(`API returned HTTP ${initRes.status}`);
    }
    const initData = await initRes.json();
    state.mode = 'LOCAL_API';
    state.metadata = {
      generation: initData.generation,
      digest: initData.projection_digest,
      asOfUtc: initData.as_of_utc,
      publishedAt: null
    };

    // Load each view
    const views = ['portfolio', 'works', 'assignments', 'evidence', 'recovery', 'unassigned_observations'];
    for (const v of views) {
      const res = await fetch(`${basePath}?view=${v}&limit=200`);
      if (res.ok) {
        const d = await res.json();
        const targetKey = v === 'unassigned_observations' ? 'unassigned' : v;
        state.viewsData[targetKey] = d.items || [];
      }
    }

    if (el.tabUnassigned) {
      el.tabUnassigned.style.display = 'inline-flex';
    }

    updateTelemetry();
    populateProjectSelector();
    renderCurrentView();
  }

  /**
   * Loads from static public_snapshot.json.
   */
  async function loadStaticSnapshot() {
    const res = await fetch('./public_snapshot.json');
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const snap = await res.json();
    state.mode = 'STATIC_SNAPSHOT';
    state.metadata = {
      generation: snap.source_generation,
      digest: snap.content_digest,
      asOfUtc: snap.as_of_utc,
      publishedAt: snap.published_at_utc,
      policyVersion: snap.policy_version
    };

    state.viewsData.portfolio = snap.portfolio || [];
    state.viewsData.works = snap.works || [];
    state.viewsData.assignments = snap.assignments || [];
    state.viewsData.evidence = snap.evidence || [];
    state.viewsData.recovery = snap.recovery || [];
    state.viewsData.unassigned = [];

    if (el.tabUnassigned) {
      el.tabUnassigned.style.display = 'none';
    }

    updateTelemetry();
    populateProjectSelector();
    renderCurrentView();
  }

  /**
   * Updates Telemetry Bar and Header Status.
   */
  function updateTelemetry() {
    const meta = state.metadata;
    const fresh = evaluateFreshness(meta.asOfUtc);

    if (state.mode === 'LOCAL_API') {
      el.modeChip.textContent = 'LOCAL STORED PROJECTION';
      el.modeChip.className = 'chip badge-green';
      el.statusDot.className = 'dot ' + (fresh.state === 'FRESH' ? 'dot-green' : 'dot-amber');
      el.statusText.textContent = `Local Stored (${meta.generation ? meta.generation.substring(0, 8) : '–'})`;
      el.telMode.textContent = 'Mode: LOCAL STORED PROJECTION';
    } else {
      el.modeChip.textContent = 'STATIC PUBLISHED SNAPSHOT';
      el.modeChip.className = 'chip badge-gray';
      el.statusDot.className = 'dot ' + (fresh.state === 'FRESH' ? 'dot-green' : 'dot-amber');
      el.statusText.textContent = `Static Snapshot (${meta.publishedAt || 'Offline'})`;
      el.telMode.textContent = 'Mode: STATIC PUBLISHED SNAPSHOT';
    }

    el.telGeneration.textContent = `Gen: ${meta.generation ? meta.generation.substring(0, 12) : '–'}…`;
    el.telAsOf.textContent = `Source as-of: ${meta.asOfUtc || '–'}`;
    el.telStaleness.replaceChildren(
      document.createTextNode('Freshness: '),
      badge(fresh.label, fresh.state === 'FRESH' ? 'green' : 'amber')
    );

    // Update counts
    for (const [k, v] of Object.entries(state.viewsData)) {
      const cntEl = document.getElementById(`cnt-${k}`);
      if (cntEl) cntEl.textContent = v.length;
    }
  }

  function showError(msg) {
    el.modeChip.textContent = 'ERROR';
    el.modeChip.className = 'chip badge-red';
    el.statusDot.className = 'dot dot-red';
    el.statusText.textContent = 'Unavailable';
    el.content.replaceChildren(h('div', { className: 'empty' }, [
      h('div', { textContent: '⚠️ ' + msg }),
      h('div', { className: 'muted', textContent: 'No silent fallback is permitted under Control Tower policy.' })
    ]));
  }

  /**
   * Populates project dropdown filter.
   */
  function populateProjectSelector() {
    const projects = new Set();
    state.viewsData.portfolio.forEach(p => p.project_id && projects.add(p.project_id));
    state.viewsData.works.forEach(w => w.project_id && projects.add(w.project_id));

    el.projSelect.replaceChildren(h('option', { value: '' }, 'All Projects'));
    for (const pid of Array.from(projects).sort()) {
      el.projSelect.appendChild(h('option', { value: pid }, pid));
    }
    el.projSelect.value = state.currentProject;
  }

  /**
   * Filter helper by project and search term.
   */
  function filterItems(items) {
    let result = items;
    if (state.currentProject) {
      result = result.filter(x => x.project_id === state.currentProject);
    }
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      result = result.filter(x => JSON.stringify(x).toLowerCase().includes(q));
    }
    return result;
  }

  /**
   * View Renderers
   */
  function renderCurrentView() {
    switch (state.currentView) {
      case 'portfolio':
        renderPortfolioView();
        break;
      case 'works':
        renderWorksView();
        break;
      case 'assignments':
        renderAssignmentsView();
        break;
      case 'evidence':
        renderEvidenceView();
        break;
      case 'recovery':
        renderRecoveryView();
        break;
      case 'unassigned':
        renderUnassignedView();
        break;
    }
  }

  function renderPortfolioView() {
    const items = filterItems(state.viewsData.portfolio);
    if (!items.length) {
      el.content.replaceChildren(h('div', { className: 'empty', textContent: 'No portfolio items found.' }));
      return;
    }

    const table = h('table', { className: 'data-table' }, [
      h('thead', {}, [
        h('tr', {}, [
          h('th', {}, 'Project ID'),
          h('th', {}, 'Name'),
          h('th', {}, 'Provider Reachability'),
          h('th', {}, 'Works'),
          h('th', {}, 'Assignments (Active / Total)'),
          h('th', {}, 'Coordinator State'),
          h('th', {}, 'Evidence Count'),
          h('th', {}, 'Latest Evidence')
        ])
      ]),
      h('tbody', {}, items.map(p => h('tr', {}, [
        h('td', { className: 'mono', textContent: p.project_id }),
        h('td', { textContent: p.name }),
        h('td', {}, [statusBadge(p.provider_reachability)]),
        h('td', { textContent: String(p.work_count ?? '0') }),
        h('td', { textContent: `${p.registered_active_assignments ?? 0} / ${p.registered_assignments ?? 0}` }),
        h('td', {}, [statusBadge(p.coordinator_source_state)]),
        h('td', { textContent: String(p.evidence_count ?? '0') }),
        h('td', { className: 'muted', textContent: p.latest_evidence_at_utc || '–' })
      ])))
    ]);

    el.content.replaceChildren(h('div', { className: 'table-container' }, [table]));
  }

  function renderWorksView() {
    const items = filterItems(state.viewsData.works);
    if (!items.length) {
      el.content.replaceChildren(h('div', { className: 'empty', textContent: 'No works found.' }));
      return;
    }

    const table = h('table', { className: 'data-table' }, [
      h('thead', {}, [
        h('tr', {}, [
          h('th', {}, 'Work ID'),
          h('th', {}, 'Project'),
          h('th', {}, 'AIM ID'),
          h('th', {}, 'Label SHA'),
          h('th', {}, 'Issue Ref'),
          h('th', {}, 'Candidate PR'),
          h('th', {}, 'Candidate Head'),
          h('th', {}, 'CI Status'),
          h('th', {}, 'Evidenced Tasks'),
          h('th', {}, 'Acceptance Status')
        ])
      ]),
      h('tbody', {}, items.map(w => h('tr', {}, [
        h('td', { className: 'mono', textContent: w.work_id }),
        h('td', { textContent: w.project_id }),
        h('td', { textContent: w.aim_id }),
        h('td', { className: 'mono muted', textContent: (w.label_sha || '–').substring(0, 10) }),
        h('td', {}, w.issue_ref ? [h('a', { href: w.issue_ref, textContent: 'Issue' })] : ['–']),
        h('td', {}, w.candidate_pr_ref ? [h('a', { href: w.candidate_pr_ref, textContent: 'PR' })] : ['–']),
        h('td', { className: 'mono muted', textContent: (w.candidate_head_sha || '–').substring(0, 10) }),
        h('td', {}, [statusBadge(w.ci_status)]),
        h('td', { textContent: String(w.evidenced_tasks ?? '–') }),
        h('td', {}, [statusBadge(w.acceptance_status)])
      ])))
    ]);

    el.content.replaceChildren(h('div', { className: 'table-container' }, [table]));
  }

  function renderAssignmentsView() {
    const items = filterItems(state.viewsData.assignments);
    if (!items.length) {
      el.content.replaceChildren(h('div', { className: 'empty', textContent: 'No assignments found.' }));
      return;
    }

    const table = h('table', { className: 'data-table' }, [
      h('thead', {}, [
        h('tr', {}, [
          h('th', {}, 'Tab'),
          h('th', {}, 'Status'),
          h('th', {}, 'Aim'),
          h('th', {}, 'Plan'),
          h('th', {}, 'AC'),
          h('th', {}, 'CI'),
          h('th', {}, 'Meter'),
          h('th', {}, 'Due'),
          h('th', {}, 'Checked'),
          h('th', {}, 'Next'),
          h('th', {}, 'Probe'),
          h('th', {}, 'State'),
          h('th', {}, 'Work')
        ])
      ]),
      h('tbody', {}, items.map(a => h('tr', {}, [
        h('td', { className: 'mono', textContent: a.tab }),
        h('td', { textContent: a.status }),
        h('td', { textContent: a.aim }),
        h('td', { textContent: a.plan }),
        h('td', { textContent: a.ac }),
        h('td', { textContent: a.ci }),
        h('td', { textContent: a.meter }),
        h('td', { textContent: a.due }),
        h('td', { textContent: a.checked }),
        h('td', { textContent: a.next }),
        h('td', {}, [statusBadge(a.probe_status)]),
        h('td', {}, [statusBadge(a.assignment_state)]),
        h('td', { className: 'mono muted', textContent: a.work_id || '–' })
      ])))
    ]);

    el.content.replaceChildren(h('div', { className: 'table-container' }, [table]));
  }

  function renderEvidenceView() {
    const items = filterItems(state.viewsData.evidence);
    if (!items.length) {
      el.content.replaceChildren(h('div', { className: 'empty', textContent: 'No evidence records found.' }));
      return;
    }

    const table = h('table', { className: 'data-table' }, [
      h('thead', {}, [
        h('tr', {}, [
          h('th', {}, 'Task ID'),
          h('th', {}, 'Project'),
          h('th', {}, 'Child Issue'),
          h('th', {}, 'Candidate SHA'),
          h('th', {}, 'Candidate Text'),
          h('th', {}, 'Attribution'),
          h('th', {}, 'Proof'),
          h('th', {}, 'Author'),
          h('th', {}, 'Created At')
        ])
      ]),
      h('tbody', {}, items.map(e => h('tr', {}, [
        h('td', { className: 'mono', textContent: e.task_id }),
        h('td', { textContent: e.project_id }),
        h('td', { textContent: e.child_issue }),
        h('td', { className: 'mono muted', textContent: (e.candidate_sha || '–').substring(0, 10) }),
        h('td', { textContent: e.candidate_text || '–' }),
        h('td', {}, [statusBadge(e.attribution)]),
        h('td', {}, e.source_ref ? [h('a', { href: e.source_ref, textContent: 'Proof Link' })] : ['–']),
        h('td', { textContent: e.author }),
        h('td', { className: 'muted', textContent: e.created_at })
      ])))
    ]);

    el.content.replaceChildren(h('div', { className: 'table-container' }, [table]));
  }

  function renderRecoveryView() {
    const items = filterItems(state.viewsData.recovery);
    if (!items.length) {
      el.content.replaceChildren(h('div', { className: 'empty', textContent: 'No anomalies recorded. Recovery log is clear.' }));
      return;
    }

    const table = h('table', { className: 'data-table' }, [
      h('thead', {}, [
        h('tr', {}, [
          h('th', {}, 'Anomaly Type'),
          h('th', {}, 'Project'),
          h('th', {}, 'Assignment ID'),
          h('th', {}, 'Probe Status'),
          h('th', {}, 'Verbatim Status'),
          h('th', {}, 'Detected At'),
          h('th', {}, 'Coordinator Next')
        ])
      ]),
      h('tbody', {}, items.map(r => h('tr', {}, [
        h('td', {}, [statusBadge(r.anomaly_type)]),
        h('td', { textContent: r.project_id }),
        h('td', { className: 'mono muted', textContent: r.assignment_id || '–' }),
        h('td', {}, [statusBadge(r.probe_status)]),
        h('td', { textContent: r.status_verbatim || '–' }),
        h('td', { className: 'muted', textContent: r.detected_at_utc }),
        h('td', { textContent: r.coordinator_next || '–' })
      ])))
    ]);

    el.content.replaceChildren(h('div', { className: 'table-container' }, [table]));
  }

  function renderUnassignedView() {
    const items = filterItems(state.viewsData.unassigned);
    if (!items.length) {
      el.content.replaceChildren(h('div', { className: 'empty', textContent: 'No unassigned tab observations.' }));
      return;
    }

    const table = h('table', { className: 'data-table' }, [
      h('thead', {}, [
        h('tr', {}, [
          h('th', {}, 'Tab'),
          h('th', {}, 'Project'),
          h('th', {}, 'Probe Status'),
          h('th', {}, 'Verbatim Status'),
          h('th', {}, 'Aim'),
          h('th', {}, 'Next'),
          h('th', {}, 'Conflicts')
        ])
      ]),
      h('tbody', {}, items.map(u => h('tr', {}, [
        h('td', { className: 'mono', textContent: u.tab }),
        h('td', { textContent: u.project_id }),
        h('td', {}, [statusBadge(u.probe_status)]),
        h('td', { textContent: u.status }),
        h('td', { textContent: u.aim }),
        h('td', { textContent: u.next }),
        h('td', { textContent: (u.conflicts || []).join(', ') || '–' })
      ])))
    ]);

    el.content.replaceChildren(h('div', { className: 'table-container' }, [table]));
  }

  // Event Listeners
  el.navtabs.addEventListener('click', (e) => {
    const target = e.target.closest('.ntab');
    if (!target) return;
    document.querySelectorAll('.ntab').forEach(t => t.classList.remove('active'));
    target.classList.add('active');
    state.currentView = target.dataset.view;
    renderCurrentView();
  });

  el.projSelect.addEventListener('change', () => {
    state.currentProject = el.projSelect.value;
    renderCurrentView();
  });

  el.globalSearch.addEventListener('input', () => {
    state.searchQuery = el.globalSearch.value;
    renderCurrentView();
  });

  el.refreshBtn.addEventListener('click', () => {
    loadData();
  });

  el.themeBtn.addEventListener('click', () => {
    const doc = document.documentElement;
    const isDark = doc.getAttribute('data-theme') === 'dark';
    doc.setAttribute('data-theme', isDark ? 'light' : 'dark');
  });

  // Initialization
  loadData();
})();
