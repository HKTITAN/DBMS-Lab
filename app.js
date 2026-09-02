'use strict';

/* DBMS Lab Hub — path-based routing, per-lab pages, embedded directory */

let SQLmod = null;
let db = null;
let labs = [];
let currentLab = null;
let editorCM = null;
let labSqlText = '';
let labSetup = [];
let labExamples = [];

const ICON_PATHS = {
  play: '<path d="M6 4.5v15l13-7.5-13-7.5Z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
  arrow: '<path d="M19 12H5M12 5l-7 7 7 7"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>',
  db: '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.66 3.58 3 8 3s8-1.34 8-3V6"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  table: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M9 10v10"/>',
  code: '<path d="m8 9-3 3 3 3"/><path d="m16 9 3 3-3 3"/><path d="M13 6 11 18"/>',
};

function icon(name) {
  return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICON_PATHS[name] || ''}</svg>`;
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}

function quoteIdent(id) {
  return '"' + String(id).replace(/"/g, '""') + '"';
}

/** Always resolve static assets from site root (not from /lab/:id/...). */
function assetUrl(path) {
  if (/^https?:\/\//i.test(path)) return path;
  const clean = String(path).replace(/^\/+/, '');
  return `/${clean}`;
}

/* ── Routing ─────────────────────────────────────────────── */

function parseRoute() {
  const path = location.pathname.replace(/\/$/, '') || '/';
  if (path === '/' || path === '/index.html') return { view: 'home' };
  const m = path.match(/^\/lab\/([^/]+)(?:\/([^/]+))?$/);
  if (!m) return { view: 'home' };
  return { view: 'lab', id: m[1], tab: m[2] || null };
}

function labHref(id, tab) {
  return tab ? `/lab/${id}/${tab}` : `/lab/${id}`;
}

function defaultTab(lab) {
  if (lab.type === 'directory') return lab.defaultTab || 'departments';
  if (lab.report) return lab.defaultTab || 'report';
  return 'sql';
}

function sqlTabs(lab) {
  const tabs = [];
  if (lab.report) tabs.push({ id: 'report', label: 'Report', icon: 'file' });
  tabs.push({ id: 'sql', label: 'SQL Playground', icon: 'play' });
  tabs.push({ id: 'schema', label: 'Schema', icon: 'db' });
  return tabs;
}

function labTabs(lab) {
  if (lab.type === 'directory') {
    return (lab.directoryTabs || []).map((t) => ({
      id: t.id,
      label: t.label,
      icon: t.id === 'compiler' ? 'code' : t.id === 'data' ? 'table' : t.id === 'schema' ? 'db' : 'grid',
    }));
  }
  return sqlTabs(lab);
}

function setPageTitle(title) {
  document.title = title ? `${title} · DBMS Lab` : 'DBMS Lab Hub';
}

/* ── SQL parsing ───────────────────────────────────────── */

function stripSqlComments(sql) {
  const lines = [];
  for (const line of sql.split('\n')) {
    if (line.trim().startsWith('--')) continue;
    lines.push(line.includes('--') ? line.slice(0, line.indexOf('--')) : line);
  }
  return lines.join('\n');
}

function splitStatements(sql) {
  return stripSqlComments(sql).split(';').map((s) => s.trim()).filter(Boolean);
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
      examples.push({ label: pendingLabel || `Query ${++exampleIdx}`, sql: stmt + ';' });
      pendingLabel = '';
    } else {
      setup.push(stmt);
      if (!['INSERT', 'CREATE', 'DROP', 'ALTER'].includes(kind)) pendingLabel = '';
    }
  }
  return { setup, examples };
}

/* ── DB ──────────────────────────────────────────────────── */

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
    return { ok: true, results, elapsedMs: performance.now() - started, rowsModified: db.getRowsModified() };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

function listUserTables() {
  const res = db.exec("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
  return res.length ? res[0].values.map((r) => r[0]) : [];
}

function getColumnInfo(table) {
  const res = db.exec(`PRAGMA table_info(${quoteIdent(table)})`);
  return res.length ? res[0].values.map((r) => r[1]) : [];
}

function refreshHintTables() {
  if (!editorCM) return;
  const hints = {};
  listUserTables().forEach((t) => { hints[t] = getColumnInfo(t); });
  editorCM.setOption('hintOptions', { tables: hints });
}

async function fetchText(path) {
  const url = assetUrl(path);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Could not load ${url} (${res.status})`);
  return res.text();
}

async function loadLabAssets(lab) {
  let combined = '';
  if (lab.sqlFile) combined = await fetchText(`${lab.folder}/${lab.sqlFile}`);
  else if (lab.sqlSetup) {
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

/* ── Toasts ──────────────────────────────────────────────── */

function showToast(kind, message) {
  const stack = document.getElementById('toastStack');
  const toast = document.createElement('div');
  toast.className = `toast toast-${kind}`;
  toast.setAttribute('role', 'status');
  toast.innerHTML = `${icon(kind === 'error' ? 'alert' : kind === 'success' ? 'check' : 'info')}<span></span>`;
  toast.querySelector('span').textContent = message;
  stack.appendChild(toast);
  setTimeout(() => { toast.classList.add('leaving'); setTimeout(() => toast.remove(), 300); }, 3500);
}

/* ── Tab bar (real links) ────────────────────────────────── */

function renderTabBar(lab, activeTab) {
  const tabs = labTabs(lab);
  return `
    <nav class="tabbar" aria-label="${escapeHtml(lab.title)} sections">
      ${tabs.map((t) => {
        const current = t.id === activeTab;
        return `<a class="tab${current ? ' is-active' : ''}" href="${labHref(lab.id, t.id)}"${current ? ' aria-current="page"' : ''}>${icon(t.icon)}<span class="tab-label">${escapeHtml(t.label)}</span></a>`;
      }).join('')}
    </nav>`;
}

function renderTopbarActions(lab) {
  const el = document.getElementById('topbarActions');
  el.innerHTML = lab
    ? `<a class="btn btn-neutral btn-sm" href="/">${icon('arrow')} All Labs</a>`
    : '';
}

/* ── Home ────────────────────────────────────────────────── */

function renderHome() {
  currentLab = null;
  editorCM = null;
  setPageTitle(null);
  document.getElementById('brandSub').textContent = 'SGT University · Semester 5';
  renderTopbarActions(null);

  const main = document.getElementById('main-content');
  main.innerHTML = `
    <section class="hero">
      <h1 class="page-title">Lab Sessions</h1>
      <p class="hero-sub">Pick an experiment — read the report, run SQL, and explore schemas. Everything stays in this app.</p>
      <div class="home-stats" aria-label="Course overview">
        <span class="stat-pill"><strong>${labs.length}</strong> labs</span>
        <span class="stat-pill">SQLite in-browser</span>
        <span class="stat-pill">Semester 5</span>
      </div>
    </section>
    <div class="lab-grid" id="labGrid"></div>
  `;

  const grid = main.querySelector('#labGrid');
  labs.forEach((lab) => grid.appendChild(buildLabCard(lab)));
}

function buildLabCard(lab) {
  const tab = defaultTab(lab);
  const href = labHref(lab.id, tab);
  const link = document.createElement('a');
  link.className = 'lab-card';
  link.href = href;
  link.style.setProperty('--lab-color', lab.color);
  const monogram = lab.experiment || lab.id.slice(0, 2);
  link.innerHTML = `
    <div class="lab-card-top">
      <span class="lab-monogram" aria-hidden="true">${escapeHtml(monogram)}</span>
      <div class="lab-card-head">
        <span class="lab-date">Exp ${escapeHtml(lab.experiment)} · ${escapeHtml(lab.date)}</span>
        <h2 class="lab-card-title">${escapeHtml(lab.title)}</h2>
      </div>
    </div>
    <div class="lab-card-body">
      <p class="lab-sub">${escapeHtml(lab.subtitle)}</p>
      <p class="lab-topic">${escapeHtml(lab.topic)}</p>
      <span class="lab-card-cta">${icon('play')} Open lab</span>
    </div>
  `;
  return link;
}

/* ── Lab shell ───────────────────────────────────────────── */

async function renderLab(id, tab) {
  const lab = labs.find((l) => l.id === id);
  if (!lab) {
    history.replaceState(null, '', '/');
    renderHome();
    return;
  }

  const tabs = labTabs(lab).map((t) => t.id);
  let activeTab = tab || defaultTab(lab);
  if (!tabs.includes(activeTab)) activeTab = defaultTab(lab);

  if (!tab || tab !== activeTab) {
    history.replaceState(null, '', labHref(id, activeTab));
  }

  if (editorCM) {
    editorCM.getWrapperElement()?.remove();
    editorCM = null;
  }

  currentLab = lab;
  setPageTitle(`${lab.title} — ${labTabs(lab).find((t) => t.id === activeTab)?.label || activeTab}`);
  document.getElementById('brandSub').textContent = `${lab.date} · Experiment ${lab.experiment}`;
  renderTopbarActions(lab);

  const main = document.getElementById('main-content');
  main.innerHTML = `
    <div class="lab-header">
      <div>
        <span class="lab-date">Experiment ${escapeHtml(lab.experiment)}</span>
        <h1 class="page-title">${escapeHtml(lab.title)}</h1>
        <p class="hero-sub">${escapeHtml(lab.subtitle)}</p>
      </div>
    </div>
    ${renderTabBar(lab, activeTab)}
    <section class="panel" id="labPanel" aria-live="polite"></section>
  `;

  if (lab.type === 'directory') {
    renderDirectoryPanel(activeTab);
    return;
  }

  if (activeTab === 'report') {
    renderReportPanel();
    return;
  }

  try {
    await loadLabAssets(lab);
    runSetup(labSetup);
  } catch (err) {
    document.getElementById('labPanel').innerHTML = `
      <div class="banner banner-error">${icon('alert')}<div><strong>Could not load lab SQL.</strong><br>${escapeHtml(err.message)}</div></div>`;
    return;
  }

  if (activeTab === 'sql') renderSqlPanel();
  else renderSchemaPanel();
}

function renderDirectoryPanel(tab) {
  const panel = document.getElementById('labPanel');
  const src = assetUrl(`${currentLab.folder}/index.html?embed=1&tab=${encodeURIComponent(tab)}`);
  panel.innerHTML = `
    <div class="embed-wrap">
      <iframe class="embed-frame" src="${src}" title="${escapeHtml(currentLab.title)} — ${escapeHtml(tab)}" loading="lazy"></iframe>
    </div>
  `;
}

function renderReportPanel() {
  const panel = document.getElementById('labPanel');
  const pdfUrl = assetUrl(`${currentLab.folder}/${currentLab.report}`);
  panel.innerHTML = `
    <div class="panel-head">
      <div><h2 class="panel-title">Lab Report</h2><p class="sub">${escapeHtml(currentLab.report)}</p></div>
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
      <div><h2 class="panel-title">SQL Playground</h2><p class="sub">Real SQLite via sql.js · ${escapeHtml(currentLab.sqlFile || '')}</p></div>
      <button class="btn btn-danger-ghost btn-sm" id="resetDbBtn" type="button">Reset database</button>
    </div>
    <div class="compiler-layout">
      <div class="editor-card">
        <div class="chip-row" id="exampleChips"></div>
        <div class="cm-shell" id="editorHost"></div>
        <div class="editor-toolbar">
          <span class="kbd-hint"><kbd>Ctrl</kbd>+<kbd>Enter</kbd> to run</span>
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

  const runBtn = panel.querySelector('#runBtn');
  runBtn.addEventListener('click', runEditorQuery);
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
  const runBtn = document.getElementById('runBtn');
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.setAttribute('aria-busy', 'true');
  }
  renderQueryResult(runSQL(sql));
  refreshHintTables();
  if (runBtn) {
    runBtn.disabled = false;
    runBtn.removeAttribute('aria-busy');
  }
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
  meta.innerHTML = `<span class="ok">${icon('check')} Success</span><span class="metric">${result.elapsedMs.toFixed(1)}&nbsp;ms</span>`;
  card.appendChild(meta);

  if (!result.results.length) {
    const rowsWord = result.rowsModified === 1 ? 'row' : 'rows';
    meta.insertAdjacentHTML('beforeend', `<span class="metric">${result.rowsModified} ${rowsWord} affected</span>`);
    card.insertAdjacentHTML('beforeend', `<div class="banner banner-success">${icon('check')}<div>Statement executed — no result set.</div></div>`);
    return;
  }

  result.results.forEach(({ columns, values }) => {
    meta.insertAdjacentHTML('beforeend', `<span class="metric">${values.length} row${values.length === 1 ? '' : 's'}</span>`);
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

  let html = `<div class="panel-head"><div><h2 class="panel-title">Live Schema</h2><p class="sub">From the in-memory database for this lab.</p></div></div><div class="schema-stack">`;
  tables.forEach((t) => {
    const cols = getColumnInfo(t);
    const countRes = db.exec(`SELECT COUNT(*) FROM ${quoteIdent(t)}`);
    const count = countRes[0]?.values[0][0] ?? 0;
    const createRes = db.exec(`SELECT sql FROM sqlite_master WHERE type='table' AND name=${quoteIdent(t)}`);
    const ddl = createRes[0]?.values[0][0] || '';
    html += `
      <div class="card schema-card">
        <div class="schema-card-head">
          <h3 class="schema-name">${escapeHtml(t)}</h3>
          <span class="schema-count">${count} row${count === 1 ? '' : 's'}</span>
        </div>
        <p class="schema-cols">${cols.map(escapeHtml).join(' · ')}</p>
        <pre class="source-pre source-pre-sm">${escapeHtml(ddl)};</pre>
      </div>`;
  });
  html += '</div>';
  panel.innerHTML = html;
}

/* ── Init ────────────────────────────────────────────────── */

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
    labs = await (await fetch('/labs.json')).json();
  } catch (err) {
    document.getElementById('main-content').innerHTML = `
      <div class="banner banner-error">${icon('alert')}<div><strong>Could not load labs.json</strong><br>${escapeHtml(err.message)}</div></div>`;
    return;
  }

  try {
    SQLmod = await initSqlJs({ locateFile: (f) => `https://cdn.jsdelivr.net/npm/sql.js@1.14.2/dist/${f}` });
  } catch (err) {
    document.getElementById('main-content').innerHTML = `
      <div class="banner banner-error">${icon('alert')}<div><strong>Could not start sql.js</strong><br>${escapeHtml(err.message)}<br><small>Check your internet connection and reload.</small></div></div>`;
    return;
  }

  document.getElementById('loadingShell')?.remove();
  window.addEventListener('popstate', render);
  document.addEventListener('click', onDocumentClick);
  await render();
}

function onDocumentClick(event) {
  if (event.defaultPrevented || event.button !== 0) return;
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const anchor = event.target.closest('a[href]');
  if (!anchor || anchor.target === '_blank' || anchor.hasAttribute('download')) return;
  const url = new URL(anchor.href, location.origin);
  if (url.origin !== location.origin) return;
  const path = url.pathname.replace(/\/$/, '') || '/';
  if (path === location.pathname.replace(/\/$/, '') && url.search === location.search) return;
  event.preventDefault();
  history.pushState(null, '', path + url.search + url.hash);
  render();
}

document.addEventListener('DOMContentLoaded', init);
