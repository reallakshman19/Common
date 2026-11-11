/* Read-only browser probe. Evaluate this async function only through a browser
 * adapter that permits DOM reads. It does not focus, scroll, inject or send.
 * The output always contains compact identity, status and metric signals;
 * further page reading is needed only when the planner requests a full check.
 */
async function coordinatorProbe() {
  const visible = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const text = e => e ? (e.innerText || e.textContent || e.value || '') : '';
  const hash = async value => {
    const bytes = new TextEncoder().encode(String(value).replace(/\r\n/g, '\n').trim());
    return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(x => x.toString(16).padStart(2, '0')).join('');
  };
  const id = e => e && (e.getAttribute('data-message-id') || (e.closest('[data-message-id]') || {}).getAttribute?.('data-message-id')) || '';
  const messages = [...document.querySelectorAll('[data-message-author-role]')];
  const users = messages.filter(e => e.getAttribute('data-message-author-role') === 'user');
  const assistants = messages.filter(e => e.getAttribute('data-message-author-role') === 'assistant');
  const lastUser = users[users.length - 1], lastAssistant = assistants[assistants.length - 1];
  let scroll = (lastAssistant || lastUser)?.parentElement;
  while (scroll && !(scroll.scrollHeight > scroll.clientHeight + 50 && /(auto|scroll)/.test(getComputedStyle(scroll).overflowY))) scroll = scroll.parentElement;
  scroll = scroll || document.scrollingElement;
  const atBottom = !!scroll && (getComputedStyle(scroll).flexDirection === 'column-reverse' ? Math.abs(scroll.scrollTop) < 8 : scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 8);
  const generating = [...document.querySelectorAll('[data-testid="stop-button"],button[aria-label]')].some(e => visible(e) && (e.getAttribute('data-testid') === 'stop-button' || /^stop(?: generating)?$/i.test(e.getAttribute('aria-label') || '')));
  const box = document.getElementById('prompt-textarea');
  const composer = visible(box) && !box.closest('[data-message-author-role],article,aside,[role="dialog"]') ? box : null;
  const errors = [...document.querySelectorAll('[role="alert"],[data-testid="conversation-turn-error"],[data-testid="error-message"]')]
    .filter(e => visible(e) && !e.closest('[data-message-author-role]'))
    .map(text).filter(t => /something(?: seems to have)? (?:gone|went) wrong|delivery timed out|connection interrupted|network error|unusual activity|too many requests|could not load|maximum length|conversation is too long|sign in|do not have access|don't have access/i.test(t));
  const error = errors.join(' | ').slice(0, 400);
  let state = generating ? 'GENERATING' : 'IDLE';
  if (/maximum length|conversation is too long/i.test(error)) state = 'LIMIT';
  else if (/unusual activity|too many requests/i.test(error)) state = 'UNUSUAL';
  else if (/sign in|do not have access|don't have access/i.test(error)) state = 'NOACCESS';
  else if (error) state = 'ERROR';
  else if (!composer) state = 'NOBOX';
  const out = {
    url: location.origin + location.pathname.replace(/\/$/, ''), state, at_bottom: atBottom,
    user_ids: users.map(id).filter(Boolean),
    latest_user: lastUser ? {id: id(lastUser), hash: await hash(text(lastUser))} : null,
    latest_assistant: lastAssistant ? {id: id(lastAssistant), hash: await hash(text(lastAssistant))} : null,
    draft: composer ? (composer.value ?? composer.innerText ?? composer.textContent ?? '') : '',
    live_error: error, pages: scroll?.clientHeight ? scroll.scrollHeight / scroll.clientHeight : null
  };
  out.completed_messages = assistants.filter(e => !generating || e !== lastAssistant).map(e => {
    const turn = e.closest('article') || e;
    const worked = text(turn).match(/Worked for ([^\n]+)/i);
    let minutes = null;
    if (worked) {
      const h = worked[1].match(/(\d+)\s*h/), m = worked[1].match(/(\d+)\s*m(?!s)/), s = worked[1].match(/(\d+)\s*s/);
      if (h || m || s) minutes = (+h?.[1] || 0) * 60 + (+m?.[1] || 0) + (+s?.[1] || 0) / 60;
    }
    return {id: id(e), minutes, pages: null};
  }).filter(m => m.id);
  // Only the newest completed assistant message is a fresh status source.
  out.status = {};
  if (lastAssistant && !generating) {
    const body = text(lastAssistant);
    const coord = body.match(/(?:^|\n)\s*COORD\s+(\{[^\n]+\})/m);
    if (coord) {
      try { out.status = JSON.parse(coord[1]); } catch (_) { out.status = {}; }
    } else {
      const codes = [...lastAssistant.querySelectorAll('code')].map(text);
      const line = codes.map(t => t.replace(/\s*\n\s*/g, ' ')).filter(t => /^\s*LOG\s*[:|]/.test(t)).pop()
        || (body.match(/(?:^|\n)\s*LOG\s*[:|][^\n]*/g) || []).pop() || '';
      const kv = {};
      line.split('|').slice(1).forEach(p => { const m = p.match(/^\s*([a-z_]+)\s*=\s*(.*?)\s*$/i); if (m) kv[m[1].toLowerCase()] = m[2]; });
      const ids = value => !value || /^(none|-|n\/a)$/i.test(value.trim()) ? [] : value.split(/[,;\s]+/).filter(Boolean);
      const blocker = (kv.blocker || 'NONE').match(/^([A-Z_]+)\s*:?\s*(.*)$/i);
      const ac = (kv.ac || '').match(/^(\d+)\s*\//);
      out.status = {plan_rev: (kv.plan || '').replace(/^(\S+)\s+\d+\s*\/\s*\d+$/, '$1'), done: ids(kv.done), next: ids(kv.next),
        blocker: {kind: blocker ? blocker[1].toUpperCase() : 'NONE', text: blocker ? blocker[2] : ''},
        handover: kv.handover || 'no', stage: kv.stage || ''};
      if (ac) out.status.ac = +ac[1];
      const bk = out.status.blocker.text;
      out.status.ci_kind = /failed? test|assertion|test failure|release gate/i.test(bk) ? 'test' : /billing|credits/i.test(bk) ? 'billing' : /queue/i.test(bk) ? 'queue' : /runner/i.test(bk) ? 'runner' : 'unknown';
      const y = body.match(/Decision[^\n]{0,30}?(CONTINUE\s*\/\s*NO_CHANGE|NO_CHANGE|CONTINUE|CORRECT|VERIFY_FIRST|BLOCKED_AFFECTED_TASK)/);
      if (y && /Y\s*\|\s*INTERVENTION=CLOSED/.test(body)) out.status.y_decision = y[1];
    }
  }
  return out;
}

if (typeof module !== 'undefined') module.exports = coordinatorProbe;
