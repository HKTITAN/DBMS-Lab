'use strict';

/* ============================================================
   DBMS Lab Hub — browse reports, run lab SQL in-browser
   ============================================================ */

let SQLmod = null;
let db = null;
let labs = [];
let currentLab = null;
let editorCM = null;
let labSqlText = '';
let labSetup = [];
let labExamples = [];
let queriesRun = 0;

const ICON_PATHS = {
  play: '<path d="M6 4.5v15l13-7.5-13-7.5Z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
  arrow: '<path d="M19 12H5M12 5l-7 7 7 7"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>',
  db: '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.66 3.58 3 8 3s8-1.34 8-3V6"/>',
  external: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><path d="M15 3h6v6"/><path d="M10 14 21 3"/>',
};

function icon(name) {
  return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICON_PATHS[name] || ''}</svg>`;
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}

/* ============================================================
   SQL parsing
   ============================================================ */

function stripSqlComments(sql) {
  const lines = [];
  for (const line of sql.split('\n')) {
    const trimmed = line.trim();
    if (trimmed.startsWith('--')) continue;
    if (line.includes('--')) {
      lines.push(line.slice(0, line.indexOf('--')));
    } else {
      lines.push(line);
    }
  }
  return lines.join('\n');
}

function splitStatements(sql) {
  return stripSqlComments(sql)
    .split(';')
    .map((s) => s.trim())
    .filter(Boolean);
}

function stmtKind(stmt) {
  return stmt.trim().split(/\s+/)[0].toUpperCase();
}

function parseLabSql(text) {
  const statements = splitStatements(text);
  const setup = [];
  const examples = [];
  const rawLines = text.split('\n');
  let pendingLabel = '';

  for (const line of rawLines) {
    const m = line.match(/^\s*--\s*(\d+[a-z]?\.\s*.+)$/i);
    if (m) pendingLabel = m[1].replace(/^\d+[a-z]?\.\s*/, '').trim();
    else if (line.trim().startsWith('--') && !line.match(/^\s*--\s*-+/)) {
      const label = line.replace(/^\s*--\s*/, '').trim();
      if (label && !label.startsWith('=') && label.length < 80) pendingLabel = label;
    }
  }

  let exampleIdx = 0;
  for (const stmt of statements) {
    const kind = stmtKind(stmt);
    if (kind === 'SELECT' || kind === 'PRAGMA') {
      const label = pendingLabel || `Query ${++exampleIdx}`;
      examples.push({ label, sql: stmt + ';' });
      pendingLabel = '';
    } else {
      setup.push(stmt);
      if (kind !== 'INSERT' && kind !== 'CREATE' && kind !== 'DROP' && kind !== 'ALTER') {
        pendingLabel = '';
      }
    }
  }

  return { setup, examples, statements };
}

/* ============================================================
   DB helpers
   ============================================================ */

function quoteIdent(id) {
  return '"' + String(id).replace(/"/g, '""') + '"';
}

function runSetup(stmts) {
  if (db) { try { db.close(); } catch (e) { /* noop */ } }
  db = new SQLmod.Database();
  db.exec('PRAGMA foreign_keys = ON;');
  for (const stmt of stmts) db.exec(stmt);
}

function runSQL(sqlText) {
  try {
    const started = performance.now();
    const results = db.exec(sqlText);
    const elapsedMs = performance.now() - started;
    queriesRun += 1;
    return { ok: true, results, elapsedMs, rowsModified: db.getRowsModified() };
  } catch (err) {
    queriesRun += 1;
    return { ok: false, error: err.message };
  }
}

function listUserTables() {
  const res = db.exec("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
  if (!res.length) return [];
  return res[0].values.map((r) => r[0]);
}

function getColumnInfo(table) {
  const res = db.exec(`PRAGMA table_info(${quoteIdent(table)})`);
  if (!res.length) return [];
  return res[0].values.map((r) => r[1]);
}

function refreshHintTables() {
  if (!editorCM) return;
  const hints = {};
  listUserTables().forEach((t) => { hints[t] = getColumnInfo(t); });
  editorCM.setOption('hintOptions', { tables: hints });
}

/* ============================================================
   Routing
   ============================================================ */

function parseRoute() {
  const hash = location.hash.replace(/^#\/?/, '');
  if (!hash || hash === 'home') return { view: 'home' };
  const m = hash.match(/^lab\/([^/]+)(?:\/(\w+))?$/);
  if (m) return { view: 'lab', id: m[1], tab: m[2] || 'report' };
  return { view: 'home' };
}

function navigate(view, id, tab) {
  if (view === 'home') location.hash = '#/';
  else location.hash = `#/lab/${id}${tab && tab !== 'report' ? `/${tab}` : ''}`;
}

window.addEventListener('hashchange', render);

/* ============================================================
   Data loading
   ============================================================ */

async function fetchText(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Could not load ${path} (${res.status})`);
  return res.text();
}

async function loadLabAssets(lab) {
  let combined = '';
  if (lab.sqlFile) {
    combined = await fetchText(`${lab.folder}/${lab.sqlFile}`);
  } else if (lab.sqlSetup) {
    const parts = await Promise.all(lab.sqlSetup.map((f) => fetchText(`${lab.folder}/${f}`)));
    combined = parts.join('\n\n');
  }

  labSqlText = combined;
  const parsed = parseLabSql(combined);
  labSetup = parsed.setup;
  labExamples = parsed.examples.length ? parsed.examples : [
    { label: 'List tables', sql: "SELECT name, type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%';" },
  ];
}

/* ============================================================
   Toasts
   ============================================================ */

function showToast(kind, message) {
  const stack = document.getElementById('toastStack');
  const toast = document.createElement('div');
  toast.className = `toast toast-${kind}`;
  toast.setAttribute('role', 'status');
  toast.innerHTML = `${icon(kind === 'error' ? 'alert' : kind === 'success' ? 'check' : 'info')}<span></span>`;
  toast.querySelector('span').textContent = message;
  stack.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('leaving');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ============================================================
   Render: Home
   ============================================================ */

function renderHome() {
  currentLab = null;
  editorCM = null;
  document.getElementById('brandSub').textContent = 'SGT University · Reports & SQL Playground';
  document.getElementById('topbarActions').innerHTML = '';

  const main = document.getElementById('main-content');
  main.innerHTML = `
    <section class="hero">
      <h2>Lab Sessions</h2>
      <p class="hero-sub">Open experiment reports as PDFs and run each lab's SQL in a real in-browser SQLite engine.</p>
    </section>
    <div class="lab-grid" id="labGrid"></div>
  `;

  const grid = main.querySelector('#labGrid');
  labs.forEach((lab) => grid.appendChild(buildLabCard(lab)));
}

function buildLabCard(lab) {
  const card = document.createElement('article');
  card.className = 'lab-card';
  card.style.setProperty('--lab-color', lab.color);
  card.innerHTML = `
    <div class="lab-card-accent"></div>
    <div class="lab-card-body">
      <span class="lab-date">Exp ${lab.experiment} · ${escapeHtml(lab.date)}</span>
      <h3>${escapeHtml(lab.title)}</h3>
      <p class="lab-sub">${escapeHtml(lab.subtitle)}</p>
      <p class="lab-topic">${escapeHtml(lab.topic)}</p>
      <div class="lab-card-actions">
        ${lab.report ? `<button class="btn btn-primary btn-sm" data-action="report" type="button">${icon('file')} Report</button>` : ''}
        <button class="btn btn-info btn-sm" data-action="sql" type="button">${icon('play')} Run SQL</button>
        ${lab.legacyApp ? `<a class="btn btn-neutral btn-sm" href="${escapeHtml(lab.legacyApp)}" target="_blank" rel="noopener">${icon('external')} Full app</a>` : ''}
      </div>
    </div>
  `;

  card.querySelector('[data-action="report"]')?.addEventListener('click', () => navigate('lab', lab.id, 'report'));
  card.querySelector('[data-action="sql"]')?.addEventListener('click', () => navigate('lab', lab.id, 'sql'));
  card.addEventListener('click', (ev) => {
    if (ev.target.closest('button, a')) return;
    navigate('lab', lab.id, lab.report ? 'report' : 'sql');
  });

  return card;
}

/* ============================================================
   Render: Lab detail
   ============================================================ */

async function renderLab(id, tab) {
  const lab = labs.find((l) => l.id === id);
  if (!lab) { navigate('home'); return; }

  currentLab = lab;
  const hasReport = !!lab.report;
  const effectiveTab = tab === 'report' && !hasReport ? 'sql' : tab;

  document.getElementById('brandSub').textContent = `${lab.date} · ${lab.title}`;
  document.getElementById('topbarActions').innerHTML = `
    <button class="btn btn-neutral btn-sm" id="backBtn" type="button">${icon('arrow')} All labs</button>
  `;
  document.getElementById('backBtn').addEventListener('click', () => navigate('home'));

  const main = document.getElementById('main-content');
  main.innerHTML = `
    <div class="lab-header">
      <div>
        <span class="lab-date">Experiment ${escapeHtml(lab.experiment)}</span>
        <h2>${escapeHtml(lab.title)}</h2>
        <p class="hero-sub">${escapeHtml(lab.subtitle)}</p>
      </div>
      ${lab.legacyApp ? `<a class="btn btn-neutral btn-sm" href="${escapeHtml(lab.legacyApp)}" target="_blank" rel="noopener">${icon('external')} Open full interactive app</a>` : ''}
    </div>
    <nav class="tabbar" role="tablist" aria-label="Lab views">
      ${hasReport ? `<button class="tab" role="tab" data-tab="report" aria-selected="${effectiveTab === 'report'}">${icon('file')}<span class="tab-label">Report</span></button>` : ''}
      <button class="tab" role="tab" data-tab="sql" aria-selected="${effectiveTab === 'sql'}">${icon('play')}<span class="tab-label">SQL Playground</span></button>
      <button class="tab" role="tab" data-tab="schema" aria-selected="${effectiveTab === 'schema'}">${icon('db')}<span class="tab-label">Schema</span></button>
    </nav>
    <section class="panel" id="labPanel"></section>
  `;

  main.querySelectorAll('.tab').forEach((btn) => {
    btn.addEventListener('click', () => navigate('lab', lab.id, btn.dataset.tab));
  });

  try {
    await loadLabAssets(lab);
    runSetup(labSetup);
  } catch (err) {
    document.getElementById('labPanel').innerHTML = `
      <div class="banner banner-error">${icon('alert')}<div><strong>Could not load lab SQL.</strong><br>${escapeHtml(err.message)}<br><small>Serve this folder over HTTP (e.g. GitHub Pages or <code>python -m http.server</code>).</small></div></div>`;
    return;
  }

  if (effectiveTab === 'report') renderReportPanel();
  else if (effectiveTab === 'sql') renderSqlPanel();
  else renderSchemaPanel();
}

function renderReportPanel() {
  const panel = document.getElementById('labPanel');
  const pdfUrl = `${currentLab.folder}/${currentLab.report}`;
  panel.innerHTML = `
    <div class="panel-head">
      <div><h3>Lab Report (PDF)</h3><p class="sub">${escapeHtml(currentLab.report)}</p></div>
      <a class="btn btn-neutral btn-sm" href="${escapeHtml(pdfUrl)}" target="_blank" rel="noopener">${icon('external')} Open in new tab</a>
    </div>
    <div class="pdf-frame-wrap">
      <iframe class="pdf-frame" src="${escapeHtml(pdfUrl)}" title="Lab report PDF"></iframe>
    </div>
  `;
}

function renderSqlPanel() {
  const panel = document.getElementById('labPanel');
  panel.innerHTML = `
    <div class="panel-head">
      <div><h3>SQL Playground</h3><p class="sub">Real SQLite via sql.js · ${escapeHtml(currentLab.sqlFile || currentLab.sqlSetup?.join(' + ') || '')}</p></div>
      <button class="btn btn-danger-ghost btn-sm" id="resetDbBtn" type="button">Reset database</button>
    </div>
    <div class="compiler-layout">
      <div class="editor-card">
        <div class="chip-row" id="exampleChips"></div>
        <div class="cm-shell" id="editorHost"></div>
        <div class="editor-toolbar">
          <span class="kbd-hint"><kbd>Ctrl</kbd>/<kbd>⌘</kbd>+<kbd>Enter</kbd> to run</span>
          <button class="btn btn-primary" id="runBtn" type="button">${icon('play')} Run query</button>
        </div>
      </div>
      <div class="results-card" id="resultsCard">
        <div class="banner banner-empty">${icon('info')}<div>Run a query to see results here.</div></div>
      </div>
    </div>
    <details class="source-details">
      <summary>View full lab SQL source</summary>
      <pre class="source-pre">${escapeHtml(labSqlText)}</pre>
    </details>
  `;

  const chips = panel.querySelector('#exampleChips');
  labExamples.forEach((ex) => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chip';
    chip.textContent = ex.label;
    chip.addEventListener('click', () => { editorCM.setValue(ex.sql); editorCM.focus(); });
    chips.appendChild(chip);
  });

  editorCM = CodeMirror(panel.querySelector('#editorHost'), {
    value: labExamples[0]?.sql || 'SELECT 1;',
    mode: 'text/x-sql',
    theme: 'default',
    lineNumbers: true,
    matchBrackets: true,
    styleActiveLine: true,
    extraKeys: { 'Ctrl-Enter': runEditorQuery, 'Cmd-Enter': runEditorQuery, 'Ctrl-Space': 'autocomplete' },
  });
  refreshHintTables();

  panel.querySelector('#runBtn').addEventListener('click', runEditorQuery);
  panel.querySelector('#resetDbBtn').addEventListener('click', () => {
    runSetup(labSetup);
    refreshHintTables();
    showToast('info', 'Database reset to lab defaults.');
  });
}

function runEditorQuery() {
  if (!editorCM) return;
  const sql = editorCM.getValue().trim();
  if (!sql) return;
  renderQueryResult(runSQL(sql));
  refreshHintTables();
}

function renderQueryResult(result) {
  const card = document.getElementById('resultsCard');
  card.innerHTML = '';

  if (!result.ok) {
    card.innerHTML = `<div class="banner banner-error">${icon('alert')}<div><strong>Query failed.</strong><br>${escapeHtml(result.error)}</div></div>`;
    return;
  }

  const meta = document.createElement('div');
  meta.className = 'result-meta';
  meta.innerHTML = `<span class="ok">${icon('check')} Success</span><span>${result.elapsedMs.toFixed(1)} ms</span>`;
  card.appendChild(meta);

  if (!result.results.length) {
    const rowsWord = result.rowsModified === 1 ? 'row' : 'rows';
    meta.insertAdjacentHTML('beforeend', `<span>${result.rowsModified} ${rowsWord} affected</span>`);
    card.insertAdjacentHTML('beforeend', `<div class="banner banner-success">${icon('check')}<div>Statement executed — no result set.</div></div>`);
    return;
  }

  result.results.forEach(({ columns, values }) => {
    meta.insertAdjacentHTML('beforeend', `<span>${values.length} row${values.length === 1 ? '' : 's'}</span>`);
    const wrap = document.createElement('div');
    wrap.className = 'data-table-wrap scroll-x';
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `<thead><tr>${columns.map((c) => `<th>${escapeHtml(c)}</th>`).join('')}</tr></thead>`;
    const tbody = document.createElement('tbody');
    values.forEach((row) => {
      const tr = document.createElement('tr');
      row.forEach((cell) => {
        const td = document.createElement('td');
        if (cell === null) td.innerHTML = '<span class="null-value">NULL</span>';
        else td.textContent = cell;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    card.appendChild(wrap);
  });
}

function renderSchemaPanel() {
  const panel = document.getElementById('labPanel');
  const tables = listUserTables();

  if (!tables.length) {
    panel.innerHTML = `<div class="empty-state">${icon('info')}<strong>No tables</strong><p>Reset the database from the SQL Playground tab.</p></div>`;
    return;
  }

  let html = `<div class="panel-head"><div><h3>Live Schema</h3><p class="sub">From the in-memory database for this lab.</p></div></div><div class="schema-stack">`;
  tables.forEach((t) => {
    const cols = getColumnInfo(t);
    const countRes = db.exec(`SELECT COUNT(*) FROM ${quoteIdent(t)}`);
    const count = countRes[0]?.values[0][0] ?? 0;
    const createRes = db.exec(`SELECT sql FROM sqlite_master WHERE type='table' AND name=${quoteIdent(t)}`);
    const ddl = createRes[0]?.values[0][0] || '';
    html += `
      <div class="card schema-card">
        <div class="schema-card-head">
          <h4>${escapeHtml(t)}</h4>
          <span class="schema-count">${count} row${count === 1 ? '' : 's'}</span>
        </div>
        <p class="schema-cols">${cols.map(escapeHtml).join(' · ')}</p>
        <pre class="source-pre source-pre-sm">${escapeHtml(ddl)};</pre>
      </div>`;
  });
  html += '</div>';
  panel.innerHTML = html;
}

/* ============================================================
   Main render + init
   ============================================================ */

async function render() {
  const route = parseRoute();
  if (route.view === 'home') {
    renderHome();
    return;
  }
  await renderLab(route.id, route.tab);
}

async function init() {
  try {
    const res = await fetch('labs.json');
    labs = await res.json();
  } catch (err) {
    document.getElementById('main-content').innerHTML = `
      <div class="banner banner-error">${icon('alert')}<div><strong>Could not load labs.json</strong><br>${escapeHtml(err.message)}</div></div>`;
    return;
  }

  try {
    SQLmod = await initSqlJs({ locateFile: (f) => `https://cdn.jsdelivr.net/npm/sql.js@1.14.2/dist/${f}` });
  } catch (err) {
    document.getElementById('main-content').innerHTML = `
      <div class="banner banner-error">${icon('alert')}<div><strong>Could not start sql.js</strong><br>${escapeHtml(err.message)}</div></div>`;
    return;
  }

  if (!location.hash) location.hash = '#/';
  await render();
}

document.addEventListener('DOMContentLoaded', init);
