'use strict';

/* ============================================================
   Embedded SQL (kept byte-identical to schema.sql / seed.sql so
   the compiler's "Reset data" always matches the files on disk)
   ============================================================ */

const SCHEMA_SQL = `
PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS employee_directory;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    description   TEXT,
    color_hex     TEXT NOT NULL DEFAULT '#1CB0F6'
);

CREATE TABLE employees (
    employee_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    email             TEXT NOT NULL UNIQUE,
    job_title         TEXT NOT NULL,
    department_id     INTEGER NOT NULL REFERENCES departments (department_id) ON DELETE RESTRICT,
    manager_id        INTEGER REFERENCES employees (employee_id) ON DELETE SET NULL,
    salary            NUMERIC(10,2) NOT NULL CHECK (salary > 0),
    hire_date         TEXT NOT NULL,
    employment_status TEXT NOT NULL DEFAULT 'active'
                        CHECK (employment_status IN ('active', 'remote', 'on_leave')),
    avatar_seed       TEXT NOT NULL
);

CREATE INDEX idx_employees_department ON employees (department_id);
CREATE INDEX idx_employees_manager    ON employees (manager_id);

CREATE VIEW employee_directory AS
SELECT
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.job_title,
    d.name                             AS department_name,
    d.color_hex                        AS department_color,
    m.first_name || ' ' || m.last_name AS manager_name,
    e.salary,
    e.hire_date,
    e.employment_status,
    e.avatar_seed
FROM employees e
JOIN departments d ON d.department_id = e.department_id
LEFT JOIN employees m ON m.employee_id = e.manager_id;
`;

const SEED_SQL = `
INSERT INTO departments (name, description, color_hex) VALUES
    ('Engineering', 'Builds and ships the product.',                 '#1CB0F6'),
    ('Design',      'Shapes how the product looks, feels, and flows.', '#CE82FF'),
    ('Marketing',   'Tells the world what we''re building.',         '#FF9600'),
    ('Sales',       'Turns interest into customers.',                '#FFC800'),
    ('People Ops',  'Hires, supports, and grows the team.',          '#FF86D0'),
    ('Finance',     'Keeps the lights on and the numbers honest.',   '#1CC0C0');

INSERT INTO employees (first_name, last_name, email, job_title, department_id, manager_id, salary, hire_date, employment_status, avatar_seed) VALUES
    ('Sam', 'Okafor', 'sam.okafor@orbitly.io', 'Chief Executive Officer',
        (SELECT department_id FROM departments WHERE name = 'Engineering'), NULL,
        210000, '2018-01-15', 'active', 'sam.okafor@orbitly.io');

INSERT INTO employees (first_name, last_name, email, job_title, department_id, manager_id, salary, hire_date, employment_status, avatar_seed) VALUES
    ('Priya', 'Nair', 'priya.nair@orbitly.io', 'VP of Engineering',
        (SELECT department_id FROM departments WHERE name = 'Engineering'),
        (SELECT employee_id FROM employees WHERE email = 'sam.okafor@orbitly.io'),
        175000, '2018-06-01', 'active', 'priya.nair@orbitly.io'),
    ('Elena', 'Petrova', 'elena.petrova@orbitly.io', 'Head of Design',
        (SELECT department_id FROM departments WHERE name = 'Design'),
        (SELECT employee_id FROM employees WHERE email = 'sam.okafor@orbitly.io'),
        158000, '2019-01-10', 'active', 'elena.petrova@orbitly.io'),
    ('Grace', 'Adeyemi', 'grace.adeyemi@orbitly.io', 'VP of Marketing',
        (SELECT department_id FROM departments WHERE name = 'Marketing'),
        (SELECT employee_id FROM employees WHERE email = 'sam.okafor@orbitly.io'),
        152000, '2019-08-05', 'active', 'grace.adeyemi@orbitly.io'),
    ('Isabella', 'Rossi', 'isabella.rossi@orbitly.io', 'VP of Sales',
        (SELECT department_id FROM departments WHERE name = 'Sales'),
        (SELECT employee_id FROM employees WHERE email = 'sam.okafor@orbitly.io'),
        160000, '2018-11-20', 'active', 'isabella.rossi@orbitly.io'),
    ('Olivia', 'Martins', 'olivia.martins@orbitly.io', 'Head of People',
        (SELECT department_id FROM departments WHERE name = 'People Ops'),
        (SELECT employee_id FROM employees WHERE email = 'sam.okafor@orbitly.io'),
        140000, '2019-04-02', 'active', 'olivia.martins@orbitly.io'),
    ('Benjamin', 'Cohen', 'benjamin.cohen@orbitly.io', 'Chief Financial Officer',
        (SELECT department_id FROM departments WHERE name = 'Finance'),
        (SELECT employee_id FROM employees WHERE email = 'sam.okafor@orbitly.io'),
        175000, '2018-09-17', 'active', 'benjamin.cohen@orbitly.io');

INSERT INTO employees (first_name, last_name, email, job_title, department_id, manager_id, salary, hire_date, employment_status, avatar_seed) VALUES
    ('Diego', 'Fernandez', 'diego.fernandez@orbitly.io', 'Senior Backend Engineer',
        (SELECT department_id FROM departments WHERE name = 'Engineering'),
        (SELECT employee_id FROM employees WHERE email = 'priya.nair@orbitly.io'),
        145000, '2019-03-11', 'active', 'diego.fernandez@orbitly.io'),
    ('Wei', 'Zhang', 'wei.zhang@orbitly.io', 'Frontend Engineer',
        (SELECT department_id FROM departments WHERE name = 'Engineering'),
        (SELECT employee_id FROM employees WHERE email = 'priya.nair@orbitly.io'),
        118000, '2021-02-08', 'active', 'wei.zhang@orbitly.io'),
    ('Fatima', 'Al-Sayed', 'fatima.alsayed@orbitly.io', 'DevOps Engineer',
        (SELECT department_id FROM departments WHERE name = 'Engineering'),
        (SELECT employee_id FROM employees WHERE email = 'priya.nair@orbitly.io'),
        132000, '2020-09-21', 'remote', 'fatima.alsayed@orbitly.io'),
    ('Noah', 'Kim', 'noah.kim@orbitly.io', 'Junior Engineer',
        (SELECT department_id FROM departments WHERE name = 'Engineering'),
        (SELECT employee_id FROM employees WHERE email = 'priya.nair@orbitly.io'),
        92000, '2023-07-03', 'active', 'noah.kim@orbitly.io'),
    ('Marcus', 'Webb', 'marcus.webb@orbitly.io', 'Senior Product Designer',
        (SELECT department_id FROM departments WHERE name = 'Design'),
        (SELECT employee_id FROM employees WHERE email = 'elena.petrova@orbitly.io'),
        128000, '2020-05-18', 'active', 'marcus.webb@orbitly.io'),
    ('Aiko', 'Tanaka', 'aiko.tanaka@orbitly.io', 'UX Researcher',
        (SELECT department_id FROM departments WHERE name = 'Design'),
        (SELECT employee_id FROM employees WHERE email = 'elena.petrova@orbitly.io'),
        104000, '2022-01-24', 'active', 'aiko.tanaka@orbitly.io'),
    ('Leo', 'Novak', 'leo.novak@orbitly.io', 'Visual Designer',
        (SELECT department_id FROM departments WHERE name = 'Design'),
        (SELECT employee_id FROM employees WHERE email = 'elena.petrova@orbitly.io'),
        95000, '2023-02-14', 'on_leave', 'leo.novak@orbitly.io'),
    ('Tomas', 'Rieger', 'tomas.rieger@orbitly.io', 'Content Strategist',
        (SELECT department_id FROM departments WHERE name = 'Marketing'),
        (SELECT employee_id FROM employees WHERE email = 'grace.adeyemi@orbitly.io'),
        98000, '2021-11-01', 'active', 'tomas.rieger@orbitly.io'),
    ('Hana', 'Suzuki', 'hana.suzuki@orbitly.io', 'Growth Marketer',
        (SELECT department_id FROM departments WHERE name = 'Marketing'),
        (SELECT employee_id FROM employees WHERE email = 'grace.adeyemi@orbitly.io'),
        101000, '2022-04-19', 'active', 'hana.suzuki@orbitly.io'),
    ('Owen', 'Brady', 'owen.brady@orbitly.io', 'Social Media Manager',
        (SELECT department_id FROM departments WHERE name = 'Marketing'),
        (SELECT employee_id FROM employees WHERE email = 'grace.adeyemi@orbitly.io'),
        86000, '2023-09-01', 'active', 'owen.brady@orbitly.io'),
    ('Karan', 'Mehta', 'karan.mehta@orbitly.io', 'Account Executive',
        (SELECT department_id FROM departments WHERE name = 'Sales'),
        (SELECT employee_id FROM employees WHERE email = 'isabella.rossi@orbitly.io'),
        112000, '2020-01-13', 'active', 'karan.mehta@orbitly.io'),
    ('Chloe', 'Bennett', 'chloe.bennett@orbitly.io', 'Account Executive',
        (SELECT department_id FROM departments WHERE name = 'Sales'),
        (SELECT employee_id FROM employees WHERE email = 'isabella.rossi@orbitly.io'),
        110000, '2021-06-07', 'active', 'chloe.bennett@orbitly.io'),
    ('Yusuf', 'Demir', 'yusuf.demir@orbitly.io', 'Sales Development Rep',
        (SELECT department_id FROM departments WHERE name = 'Sales'),
        (SELECT employee_id FROM employees WHERE email = 'isabella.rossi@orbitly.io'),
        78000, '2023-03-27', 'active', 'yusuf.demir@orbitly.io'),
    ('Mei', 'Lin', 'mei.lin@orbitly.io', 'Sales Development Rep',
        (SELECT department_id FROM departments WHERE name = 'Sales'),
        (SELECT employee_id FROM employees WHERE email = 'isabella.rossi@orbitly.io'),
        78000, '2023-10-16', 'remote', 'mei.lin@orbitly.io'),
    ('Jonas', 'Weber', 'jonas.weber@orbitly.io', 'Recruiter',
        (SELECT department_id FROM departments WHERE name = 'People Ops'),
        (SELECT employee_id FROM employees WHERE email = 'olivia.martins@orbitly.io'),
        92000, '2021-08-23', 'active', 'jonas.weber@orbitly.io'),
    ('Ana Cristina', 'Silva', 'ana.silva@orbitly.io', 'HR Business Partner',
        (SELECT department_id FROM departments WHERE name = 'People Ops'),
        (SELECT employee_id FROM employees WHERE email = 'olivia.martins@orbitly.io'),
        98000, '2022-07-11', 'active', 'ana.silva@orbitly.io'),
    ('Ravi', 'Chandran', 'ravi.chandran@orbitly.io', 'Financial Analyst',
        (SELECT department_id FROM departments WHERE name = 'Finance'),
        (SELECT employee_id FROM employees WHERE email = 'benjamin.cohen@orbitly.io'),
        105000, '2020-12-04', 'active', 'ravi.chandran@orbitly.io'),
    ('Sofia', 'Kowalski', 'sofia.kowalski@orbitly.io', 'Accountant',
        (SELECT department_id FROM departments WHERE name = 'Finance'),
        (SELECT employee_id FROM employees WHERE email = 'benjamin.cohen@orbitly.io'),
        96000, '2021-05-16', 'active', 'sofia.kowalski@orbitly.io'),
    ('Daniel', 'Osei', 'daniel.osei@orbitly.io', 'Payroll Specialist',
        (SELECT department_id FROM departments WHERE name = 'Finance'),
        (SELECT employee_id FROM employees WHERE email = 'benjamin.cohen@orbitly.io'),
        89000, '2022-10-30', 'on_leave', 'daniel.osei@orbitly.io');
`;

const EXAMPLE_QUERIES = [
  { label: 'All employees', sql: "SELECT * FROM employee_directory\nORDER BY department_name, salary DESC;" },
  { label: 'Headcount by department', sql: "SELECT d.name AS department, COUNT(*) AS headcount, ROUND(AVG(e.salary)) AS avg_salary\nFROM employees e\nJOIN departments d ON d.department_id = e.department_id\nGROUP BY d.name\nORDER BY headcount DESC;" },
  { label: 'Who reports to whom', sql: "SELECT m.first_name || ' ' || m.last_name AS manager,\n       e.first_name || ' ' || e.last_name AS report\nFROM employees e\nJOIN employees m ON m.employee_id = e.manager_id\nORDER BY manager;" },
  { label: 'Highest paid per dept', sql: "SELECT d.name AS department, e.first_name || ' ' || e.last_name AS employee, e.salary\nFROM employees e\nJOIN departments d ON d.department_id = e.department_id\nWHERE e.salary = (\n  SELECT MAX(salary) FROM employees e2 WHERE e2.department_id = e.department_id\n)\nORDER BY e.salary DESC;" },
  { label: 'On leave or remote', sql: "SELECT first_name, last_name, job_title, employment_status\nFROM employees\nWHERE employment_status != 'active';" },
  { label: 'Give Engineering a raise', sql: "UPDATE employees\nSET salary = ROUND(salary * 1.05)\nWHERE department_id = (\n  SELECT department_id FROM departments WHERE name = 'Engineering'\n);" },
];

/* ============================================================
   State
   ============================================================ */

let SQLmod = null;
let db = null;
let activeTab = 'departments';
let activeDataTable = 'employees';
let editorCM = null;
let queryHistory = [];
let queriesRun = 0;

/* ============================================================
   Icons (single hand-drawn set, styled entirely via .icon in CSS)
   ============================================================ */

const ICON_PATHS = {
  play: '<path d="M6 4.5v15l13-7.5-13-7.5Z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  trash: '<path d="M4 7h16M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2m-7 0 1 12a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2l1-12"/>',
};
function icon(name) {
  return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICON_PATHS[name] || ''}</svg>`;
}

/* ============================================================
   Init
   ============================================================ */

async function init() {
  wireTabs();
  document.getElementById('resetBtn').addEventListener('click', handleReset);
  document.getElementById('exportBtn').addEventListener('click', handleExport);

  try {
    SQLmod = await initSqlJs({ locateFile: (f) => `https://cdn.jsdelivr.net/npm/sql.js@1.14.2/dist/${f}` });
  } catch (err) {
    showFatalError(err);
    return;
  }

  loadFreshDatabase();
  switchTab('departments');
}

function loadFreshDatabase() {
  if (db) { try { db.close(); } catch (e) { /* already closed */ } }
  db = new SQLmod.Database();
  try {
    db.exec('PRAGMA foreign_keys = ON;');
    db.exec(SCHEMA_SQL);
    db.exec(SEED_SQL);
  } catch (err) {
    showFatalError(err);
    return;
  }
  queryHistory = [];
  queriesRun = 0;
}

function handleReset() {
  loadFreshDatabase();
  const panel = document.getElementById('panel-compiler');
  if (panel) panel.dataset.built = '';
  editorCM = null;
  switchTab(activeTab);
  showToast('info', 'Database reset to the original sample data.');
}

function showFatalError(err) {
  const main = document.getElementById('main-content');
  main.innerHTML = `
    <div class="empty-state">
      ${icon('alert')}
      <strong>Couldn't start the SQL engine</strong>
      <p>${escapeHtml(err && err.message ? err.message : String(err))}</p>
      <p>This page loads SQLite compiled to WebAssembly from a CDN on first run &mdash; check your internet connection and reload.</p>
    </div>`;
}

document.addEventListener('DOMContentLoaded', init);

/* ============================================================
   DB helpers
   ============================================================ */

function quoteIdent(id) {
  return '"' + String(id).replace(/"/g, '""') + '"';
}

function queryAll(sql) {
  const res = db.exec(sql);
  if (!res.length) return { columns: [], rows: [] };
  return { columns: res[0].columns, rows: res[0].values };
}

function queryAllParams(sql, params) {
  const stmt = db.prepare(sql);
  stmt.bind(params);
  const columns = stmt.getColumnNames();
  const rows = [];
  while (stmt.step()) rows.push(stmt.get());
  stmt.free();
  return { columns, rows };
}

function scalar(sql) {
  const res = db.exec(sql);
  return res.length ? res[0].values[0][0] : null;
}

function runParamStatement(sql, params) {
  const stmt = db.prepare(sql);
  stmt.bind(params);
  stmt.step();
  stmt.free();
  return db.getRowsModified();
}

function rowToObj(columns, row) {
  const o = {};
  columns.forEach((c, i) => { o[c] = row[i]; });
  return o;
}

function runSQL(sqlText) {
  const startedAt = performance.now();
  try {
    const results = db.exec(sqlText);
    const elapsedMs = performance.now() - startedAt;
    const rowsModified = db.getRowsModified();
    queriesRun += 1;
    queryHistory.unshift({ sql: sqlText, ok: true, ts: Date.now() });
    if (queryHistory.length > 25) queryHistory.length = 25;
    return { ok: true, results, elapsedMs, rowsModified };
  } catch (err) {
    queriesRun += 1;
    queryHistory.unshift({ sql: sqlText, ok: false, ts: Date.now() });
    if (queryHistory.length > 25) queryHistory.length = 25;
    return { ok: false, error: err.message };
  }
}

function listUserTables() {
  const { rows } = queryAll("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
  return rows.map((r) => r[0]);
}

function getColumnInfo(table) {
  const { rows } = queryAll(`PRAGMA table_info(${quoteIdent(table)})`);
  return rows.map((r) => ({ cid: r[0], name: r[1], type: r[2], notnull: !!r[3], dflt: r[4], pk: r[5] }));
}

function getForeignKeys(table) {
  const { rows } = queryAll(`PRAGMA foreign_key_list(${quoteIdent(table)})`);
  return rows.map((r) => ({ table: r[2], from: r[3], to: r[4] }));
}

function getDepartments() {
  const { columns, rows } = queryAll('SELECT department_id, name, description, color_hex FROM departments ORDER BY name');
  return rows.map((r) => rowToObj(columns, r));
}

function getAllEmployeesBasic() {
  const { columns, rows } = queryAll('SELECT employee_id, first_name, last_name FROM employees');
  return rows.map((r) => rowToObj(columns, r));
}

/* ============================================================
   Small formatting / safety helpers
   ============================================================ */

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}

function formatMoney(n) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(Number(n) || 0);
}

function humanizeColumnName(name) {
  return name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function humanizeStatus(s) {
  return { active: 'Active', remote: 'Remote', on_leave: 'On leave' }[s] || s;
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function unquoteDefault(dflt) {
  if (dflt === null || dflt === undefined) return null;
  const s = String(dflt).trim();
  if (s.length >= 2 && s.startsWith("'") && s.endsWith("'")) return s.slice(1, -1).replace(/''/g, "'");
  return s;
}

function hexToRgb(hex) {
  const m = String(hex || '').replace('#', '');
  const full = m.length === 3 ? m.split('').map((c) => c + c).join('') : m;
  const bigint = parseInt(full, 16);
  return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
}

function darken(hex, amount) {
  const { r, g, b } = hexToRgb(hex);
  const f = (c) => Math.max(0, Math.round(c * (1 - amount)));
  return `rgb(${f(r)}, ${f(g)}, ${f(b)})`;
}

// Pre-downloaded locally so the 26 seed employees' avatars load instantly and
// work offline (see avatars/ and README.md). Anything not in this map — a
// newly added employee, or an edited avatar_seed — falls back to the live
// DiceBear API below.
const LOCAL_AVATARS = {
  'sam.okafor@orbitly.io': 'avatars/sam-okafor.svg',
  'priya.nair@orbitly.io': 'avatars/priya-nair.svg',
  'elena.petrova@orbitly.io': 'avatars/elena-petrova.svg',
  'grace.adeyemi@orbitly.io': 'avatars/grace-adeyemi.svg',
  'isabella.rossi@orbitly.io': 'avatars/isabella-rossi.svg',
  'olivia.martins@orbitly.io': 'avatars/olivia-martins.svg',
  'benjamin.cohen@orbitly.io': 'avatars/benjamin-cohen.svg',
  'diego.fernandez@orbitly.io': 'avatars/diego-fernandez.svg',
  'wei.zhang@orbitly.io': 'avatars/wei-zhang.svg',
  'fatima.alsayed@orbitly.io': 'avatars/fatima-alsayed.svg',
  'noah.kim@orbitly.io': 'avatars/noah-kim.svg',
  'marcus.webb@orbitly.io': 'avatars/marcus-webb.svg',
  'aiko.tanaka@orbitly.io': 'avatars/aiko-tanaka.svg',
  'leo.novak@orbitly.io': 'avatars/leo-novak.svg',
  'tomas.rieger@orbitly.io': 'avatars/tomas-rieger.svg',
  'hana.suzuki@orbitly.io': 'avatars/hana-suzuki.svg',
  'owen.brady@orbitly.io': 'avatars/owen-brady.svg',
  'karan.mehta@orbitly.io': 'avatars/karan-mehta.svg',
  'chloe.bennett@orbitly.io': 'avatars/chloe-bennett.svg',
  'yusuf.demir@orbitly.io': 'avatars/yusuf-demir.svg',
  'mei.lin@orbitly.io': 'avatars/mei-lin.svg',
  'jonas.weber@orbitly.io': 'avatars/jonas-weber.svg',
  'ana.silva@orbitly.io': 'avatars/ana-silva.svg',
  'ravi.chandran@orbitly.io': 'avatars/ravi-chandran.svg',
  'sofia.kowalski@orbitly.io': 'avatars/sofia-kowalski.svg',
  'daniel.osei@orbitly.io': 'avatars/daniel-osei.svg',
};

function avatarUrl(seed) {
  if (seed && LOCAL_AVATARS[seed]) return LOCAL_AVATARS[seed];
  return `https://api.dicebear.com/10.x/dylan/svg?seed=${encodeURIComponent(seed || 'employee')}&backgroundColor=00000000`;
}

function bannerHTML(kind, message) {
  const iconName = kind === 'error' ? 'alert' : kind === 'success' ? 'check' : 'info';
  const cls = kind === 'error' ? 'banner-error' : kind === 'success' ? 'banner-success' : 'banner-empty';
  return `<div class="banner ${cls}">${icon(iconName)}<div>${escapeHtml(message)}</div></div>`;
}

function emptyStateNode(title, sub) {
  const div = document.createElement('div');
  div.className = 'empty-state';
  div.innerHTML = `${icon('info')}<strong>${escapeHtml(title)}</strong><p>${escapeHtml(sub)}</p>`;
  return div;
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
  const duration = Math.min(6000, Math.max(2200, message.length * 60));
  setTimeout(() => {
    toast.classList.add('leaving');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

/* ============================================================
   Tabs
   ============================================================ */

function wireTabs() {
  const tabs = Array.from(document.querySelectorAll('.tab'));
  tabs.forEach((tabBtn, i) => {
    tabBtn.addEventListener('click', () => switchTab(tabBtn.dataset.tab));
    tabBtn.addEventListener('keydown', (ev) => {
      if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
      ev.preventDefault();
      const next = tabs[(i + (ev.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
      next.focus();
      switchTab(next.dataset.tab);
    });
  });
}

function switchTab(name) {
  activeTab = name;
  document.querySelectorAll('.tab').forEach((t) => {
    const selected = t.dataset.tab === name;
    t.setAttribute('aria-selected', String(selected));
    t.tabIndex = selected ? 0 : -1;
  });
  document.querySelectorAll('.panel').forEach((p) => { p.hidden = p.id !== `panel-${name}`; });

  if (name === 'departments') renderDepartments();
  else if (name === 'data') renderDataTab();
  else if (name === 'schema') renderSchema();
  else if (name === 'compiler') { renderCompilerChrome(); if (editorCM) editorCM.refresh(); }

  renderTopbarStats();
}

function renderTopbarStats() {
  const el = document.getElementById('topbarStats');
  if (!db) { el.innerHTML = ''; return; }
  const deptCount = scalar('SELECT COUNT(*) FROM departments');
  const empCount = scalar('SELECT COUNT(*) FROM employees');
  el.innerHTML = `
    <span class="stat-pill">${icon('info')}<strong>${deptCount}</strong><span class="label">departments</span></span>
    <span class="stat-pill">${icon('info')}<strong>${empCount}</strong><span class="label">employees</span></span>
    <span class="stat-pill">${icon('play')}<strong>${queriesRun}</strong><span class="label">${queriesRun === 1 ? 'query run' : 'queries run'}</span></span>
  `;
}

function syncAfterMutation() {
  renderTopbarStats();
  if (activeTab === 'departments') renderDepartments();
  else if (activeTab === 'data') renderDataTab();
  else if (activeTab === 'schema') renderSchema();
  if (editorCM) refreshHintTables();
}

/* ============================================================
   Departments tab
   ============================================================ */

function renderDepartments() {
  const panel = document.getElementById('panel-departments');
  const depts = getDepartments();
  panel.innerHTML = `
    <div class="panel-head">
      <div><h2>Departments</h2><p class="sub">${depts.length} department${depts.length === 1 ? '' : 's'} &middot; click through to see everyone in Data.</p></div>
    </div>
    <div class="dept-grid" id="deptGrid"></div>
  `;
  const grid = panel.querySelector('#deptGrid');
  if (!depts.length) {
    grid.replaceWith(emptyStateNode('No departments yet', 'Insert one from the SQL Compiler tab.'));
    return;
  }
  depts.forEach((dept) => grid.appendChild(buildDeptCard(dept)));
}

function buildDeptCard(dept) {
  const { columns, rows } = queryAllParams(
    'SELECT employee_id, first_name, last_name, job_title, avatar_seed, salary FROM employees WHERE department_id = ? ORDER BY salary DESC',
    [dept.department_id]
  );
  const emps = rows.map((r) => rowToObj(columns, r));
  const totalPayroll = emps.reduce((sum, e) => sum + Number(e.salary), 0);
  const initial = (dept.name || '?').trim().charAt(0).toUpperCase() || '?';

  const card = document.createElement('article');
  card.className = 'dept-card';
  card.style.setProperty('--dc', dept.color_hex);
  card.style.setProperty('--dc-dark', darken(dept.color_hex, 0.22));

  card.innerHTML = `
    <div class="dept-card-top">
      <span class="dept-monogram">${escapeHtml(initial)}</span>
      <div class="dept-card-title">
        <h3>${escapeHtml(dept.name)}</h3>
        <p>${escapeHtml(dept.description || 'No description yet.')}</p>
      </div>
      <span class="dept-count">${emps.length} ${emps.length === 1 ? 'person' : 'people'}</span>
    </div>
    <div class="avatar-stack" id="stack-${dept.department_id}"></div>
    <div class="dept-card-footer">
      <span class="dept-payroll">Payroll <strong>${formatMoney(totalPayroll)}</strong>/yr</span>
      <button class="btn-text" type="button">View in Data &rarr;</button>
    </div>
  `;

  const stackEl = card.querySelector('.avatar-stack');
  if (!emps.length) {
    stackEl.innerHTML = `<span style="font-size:.8rem;color:var(--ink-faint);">Nobody here yet.</span>`;
  } else {
    const shown = emps.slice(0, 6);
    shown.forEach((e) => stackEl.appendChild(buildAvatarImg(e, 'avatar-sm', dept.color_hex)));
    if (emps.length > shown.length) {
      const overflow = document.createElement('span');
      overflow.className = 'overflow-badge';
      overflow.textContent = `+${emps.length - shown.length}`;
      stackEl.appendChild(overflow);
    }
  }

  card.querySelector('.btn-text').addEventListener('click', () => {
    switchTab('data');
    setActiveDataTable('employees');
  });

  return card;
}

function buildAvatarImg(emp, sizeClass, ringColor) {
  const img = document.createElement('img');
  img.className = `avatar ${sizeClass}`;
  img.dataset.ring = '1';
  img.style.setProperty('--ring', ringColor || 'var(--line)');
  img.src = avatarUrl(emp.avatar_seed);
  img.alt = `${emp.first_name} ${emp.last_name}`;
  img.title = `${emp.first_name} ${emp.last_name} — ${emp.job_title}`;
  img.loading = 'lazy';
  img.width = 34;
  img.height = 34;
  return img;
}

/* ============================================================
   Data tab (generic grid, driven by PRAGMA introspection)
   ============================================================ */

function setActiveDataTable(t) {
  activeDataTable = t;
  renderDataTab();
}

function renderDataTab() {
  const panel = document.getElementById('panel-data');
  const tables = listUserTables();
  if (!tables.includes(activeDataTable)) activeDataTable = tables[0] || null;

  panel.innerHTML = `
    <div class="panel-head">
      <div><h2>Data</h2><p class="sub">Click any cell to edit &mdash; it runs a real <code>UPDATE</code> statement.</p></div>
    </div>
    <div class="grid-toolbar">
      <div class="table-picker" id="tablePicker"></div>
      <button class="btn btn-primary btn-sm" id="addRowBtn" type="button" ${activeDataTable ? '' : 'disabled'}>${icon('plus')} Add row</button>
    </div>
    <div class="data-table-wrap scroll-x" id="dataTableWrap"></div>
  `;

  const picker = panel.querySelector('#tablePicker');
  tables.forEach((t) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = t;
    b.setAttribute('aria-pressed', String(t === activeDataTable));
    b.addEventListener('click', () => setActiveDataTable(t));
    picker.appendChild(b);
  });

  const addBtn = panel.querySelector('#addRowBtn');
  if (activeDataTable) addBtn.addEventListener('click', () => openAddRowModal(activeDataTable));

  renderDataGrid(panel.querySelector('#dataTableWrap'), activeDataTable);
}

function cellRenderCtx(table) {
  const isEmployees = table === 'employees';
  return {
    isEmployees,
    deptMap: isEmployees ? Object.fromEntries(getDepartments().map((d) => [String(d.department_id), d])) : {},
    empNameMap: isEmployees ? Object.fromEntries(getAllEmployeesBasic().map((e) => [String(e.employee_id), `${e.first_name} ${e.last_name}`])) : {},
  };
}

function renderDataGrid(container, table) {
  if (!table) {
    container.replaceWith(emptyStateNode('No tables yet', 'Create one from the SQL Compiler tab, e.g. CREATE TABLE ...'));
    return;
  }
  const cols = getColumnInfo(table);
  const pkCols = cols.filter((c) => c.pk);
  const { rows } = queryAll(`SELECT * FROM ${quoteIdent(table)}`);

  container.innerHTML = '';
  if (!rows.length) {
    container.appendChild(emptyStateNode('No rows yet', 'Use "Add row" above, or INSERT via the SQL Compiler.'));
    return;
  }
  if (pkCols.length !== 1) {
    container.appendChild(emptyStateNode('Read-only view', `"${table}" has no single primary key, so the grid can't safely target a row to edit. Use the SQL Compiler instead.`));
    container.appendChild(buildPlainTable(cols, rows));
    return;
  }

  const pkColName = pkCols[0].name;
  const pkIndex = cols.findIndex((c) => c.pk);
  const fks = getForeignKeys(table);
  const fkByCol = Object.fromEntries(fks.map((fk) => [fk.from, fk]));
  const ctx = cellRenderCtx(table);

  const tableEl = document.createElement('table');
  tableEl.className = 'data-table';
  const thead = document.createElement('thead');
  const headRow = document.createElement('tr');
  cols.forEach((c) => {
    const th = document.createElement('th');
    th.textContent = humanizeColumnName(c.name);
    headRow.appendChild(th);
  });
  headRow.appendChild(document.createElement('th'));
  thead.appendChild(headRow);
  tableEl.appendChild(thead);

  const tbody = document.createElement('tbody');
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    const pkValue = row[pkIndex];
    cols.forEach((c, i) => {
      const td = document.createElement('td');
      const value = row[i];
      if (c.pk) {
        td.className = 'pk-cell';
        td.textContent = value;
      } else {
        td.classList.add('editable');
        td.tabIndex = 0;
        renderDisplayValue(td, value, c, ctx);
        const startEdit = () => beginCellEdit(td, table, c, fkByCol[c.name], value, pkValue, pkColName, ctx);
        td.addEventListener('click', startEdit);
        td.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') startEdit(); });
      }
      tr.appendChild(td);
    });
    const tdActions = document.createElement('td');
    tdActions.className = 'row-actions';
    tdActions.appendChild(buildDeleteButton(table, pkColName, pkValue));
    tr.appendChild(tdActions);
    tbody.appendChild(tr);
  });
  tableEl.appendChild(tbody);
  container.appendChild(tableEl);
}

function buildPlainTable(cols, rows) {
  const wrap = document.createElement('div');
  wrap.className = 'data-table-wrap scroll-x';
  wrap.style.marginTop = 'var(--sp-4)';
  const t = document.createElement('table');
  t.className = 'data-table';
  t.innerHTML = `<thead><tr>${cols.map((c) => `<th>${escapeHtml(humanizeColumnName(c.name))}</th>`).join('')}</tr></thead>`;
  const tbody = document.createElement('tbody');
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    row.forEach((cell) => {
      const td = document.createElement('td');
      if (cell === null) td.innerHTML = '<span class="null-value">NULL</span>';
      else td.textContent = cell;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  t.appendChild(tbody);
  wrap.appendChild(t);
  return wrap;
}

function renderDisplayValue(td, value, col, ctx) {
  td.innerHTML = '';
  const shownValue = value === null || value === undefined || value === '' ? 'empty' : (col.name === 'salary' ? formatMoney(value) : String(value));
  td.setAttribute('aria-label', `${humanizeColumnName(col.name)}: ${shownValue}. Press Enter to edit.`);
  if (value === null || value === undefined) {
    const span = document.createElement('span');
    span.className = 'null-value';
    span.textContent = 'NULL';
    td.appendChild(span);
    return;
  }
  if (ctx.isEmployees) {
    if (col.name === 'department_id') { td.appendChild(buildDeptTag(ctx.deptMap[String(value)])); return; }
    if (col.name === 'manager_id') { td.textContent = ctx.empNameMap[String(value)] || `#${value}`; return; }
    if (col.name === 'salary') { td.classList.add('money'); td.textContent = formatMoney(value); return; }
    if (col.name === 'employment_status') { td.appendChild(buildStatusPill(value)); return; }
    if (col.name === 'avatar_seed') {
      const wrap = document.createElement('div');
      wrap.className = 'person';
      const img = document.createElement('img');
      img.className = 'avatar avatar-sm';
      img.src = avatarUrl(value);
      img.alt = '';
      img.loading = 'lazy';
      img.width = 34;
      img.height = 34;
      const code = document.createElement('code');
      code.style.fontSize = '.78rem';
      code.style.color = 'var(--ink-soft)';
      code.textContent = value;
      wrap.append(img, code);
      td.appendChild(wrap);
      return;
    }
  }
  td.textContent = value;
}

function buildDeptTag(dept) {
  const span = document.createElement('span');
  span.className = 'dept-tag';
  if (!dept) { span.textContent = 'Unknown'; return span; }
  span.style.setProperty('--tag-color', dept.color_hex);
  const dot = document.createElement('span');
  dot.className = 'dot';
  span.append(dot, document.createTextNode(dept.name));
  return span;
}

function buildStatusPill(status) {
  const span = document.createElement('span');
  span.className = `status-pill status-${status}`;
  const dot = document.createElement('span');
  dot.className = 'dot';
  span.append(dot, document.createTextNode(humanizeStatus(status)));
  return span;
}

function buildFieldEditor(table, col, fk, currentValue) {
  if (fk) {
    const select = document.createElement('select');
    if (!col.notnull) {
      const noneOpt = document.createElement('option');
      noneOpt.value = '';
      noneOpt.textContent = '— None —';
      select.appendChild(noneOpt);
    }
    const { columns, rows } = queryAll(`SELECT * FROM ${quoteIdent(fk.table)}`);
    const pkIdx = columns.indexOf(fk.to);
    const firstIdx = columns.indexOf('first_name');
    const lastIdx = columns.indexOf('last_name');
    const labelIdx = ['name', 'title', 'label', 'full_name', 'email'].reduce((found, cand) => (found >= 0 ? found : columns.indexOf(cand)), -1);
    rows.forEach((r) => {
      const opt = document.createElement('option');
      opt.value = r[pkIdx];
      opt.textContent = firstIdx >= 0 && lastIdx >= 0 ? `${r[firstIdx]} ${r[lastIdx]}` : (labelIdx >= 0 ? String(r[labelIdx]) : `#${r[pkIdx]}`);
      if (currentValue !== null && currentValue !== undefined && String(r[pkIdx]) === String(currentValue)) opt.selected = true;
      select.appendChild(opt);
    });
    if (currentValue === null || currentValue === undefined) select.value = '';
    return select;
  }
  if (col.name === 'employment_status') {
    const select = document.createElement('select');
    ['active', 'remote', 'on_leave'].forEach((v) => {
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = humanizeStatus(v);
      if (v === currentValue) opt.selected = true;
      select.appendChild(opt);
    });
    return select;
  }
  const input = document.createElement('input');
  const t = (col.type || '').toUpperCase();
  if (col.name.endsWith('_date')) input.type = 'date';
  else if (t.includes('INT') || t.includes('REAL') || t.includes('NUMERIC') || t.includes('DOUBLE') || t.includes('FLOA')) input.type = 'number';
  else input.type = 'text';
  if (col.name === 'salary') { input.step = '1000'; input.min = '0'; }
  input.value = currentValue === null || currentValue === undefined ? '' : currentValue;
  return input;
}

function readFieldEditorValue(input, col) {
  const t = (col.type || '').toUpperCase();
  const coerce = (raw) => {
    if (t.includes('INT')) return parseInt(raw, 10);
    if (t.includes('REAL') || t.includes('NUMERIC') || t.includes('DOUBLE') || t.includes('FLOA')) return parseFloat(raw);
    return raw;
  };
  if (input.tagName === 'SELECT') return input.value === '' ? null : coerce(input.value);
  if (input.value === '') return col.notnull ? '' : null;
  return coerce(input.value);
}

function beginCellEdit(td, table, col, fk, currentValue, pkValue, pkColName, ctx) {
  if (td.querySelector('.cell-editor')) return;
  const input = buildFieldEditor(table, col, fk, currentValue);
  input.classList.add('cell-editor');
  td.innerHTML = '';
  td.appendChild(input);
  input.focus();
  if (input.select) input.select();

  let settled = false;
  const commit = () => {
    if (settled) return;
    settled = true;
    const newValue = readFieldEditorValue(input, col);
    if (String(newValue) === String(currentValue)) { renderDisplayValue(td, currentValue, col, ctx); return; }
    try {
      runParamStatement(`UPDATE ${quoteIdent(table)} SET ${quoteIdent(col.name)} = ? WHERE ${quoteIdent(pkColName)} = ?`, [newValue, pkValue]);
      showToast('success', `Saved ${humanizeColumnName(col.name)}.`);
      syncAfterMutation();
    } catch (err) {
      showToast('error', err.message);
      renderDisplayValue(td, currentValue, col, ctx);
    }
  };
  const cancel = () => { settled = true; renderDisplayValue(td, currentValue, col, ctx); };

  input.addEventListener('blur', commit);
  input.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter' && input.tagName !== 'SELECT') { ev.preventDefault(); input.blur(); }
    else if (ev.key === 'Escape') { ev.preventDefault(); cancel(); }
  });
  if (input.tagName === 'SELECT') input.addEventListener('change', () => input.blur());
}

function buildDeleteButton(table, pkCol, pkValue) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'icon-btn danger';
  btn.innerHTML = icon('trash');
  btn.setAttribute('aria-label', 'Delete row');
  btn.addEventListener('click', () => {
    const td = btn.closest('td');
    td.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'row-delete-confirm';
    wrap.append('Delete?');
    const yes = document.createElement('button');
    yes.type = 'button';
    yes.className = 'btn-text';
    yes.style.color = 'var(--danger-dark)';
    yes.textContent = 'Yes';
    yes.addEventListener('click', () => {
      try {
        runParamStatement(`DELETE FROM ${quoteIdent(table)} WHERE ${quoteIdent(pkCol)} = ?`, [pkValue]);
        showToast('success', 'Row deleted.');
      } catch (err) {
        showToast('error', err.message);
      }
      syncAfterMutation();
    });
    const no = document.createElement('button');
    no.type = 'button';
    no.className = 'btn-text';
    no.textContent = 'Cancel';
    no.addEventListener('click', () => syncAfterMutation());
    wrap.append(yes, no);
    td.appendChild(wrap);
  });
  return btn;
}

/* ============================================================
   Add row modal (generic, built from PRAGMA table_info)
   ============================================================ */

function openAddRowModal(table) {
  const cols = getColumnInfo(table).filter((c) => !(c.pk && (c.type || '').toUpperCase().includes('INT')));
  const fks = getForeignKeys(table);
  const fkByCol = Object.fromEntries(fks.map((fk) => [fk.from, fk]));
  const previouslyFocused = document.activeElement;

  const scrim = document.getElementById('modalScrim');
  scrim.innerHTML = '';
  scrim.hidden = false;

  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'modalTitle');
  modal.innerHTML = `
    <div class="modal-head">
      <div><h2 id="modalTitle">Add to ${escapeHtml(table)}</h2><p>Runs a real <code>INSERT</code> statement.</p></div>
      <button class="icon-btn" id="modalClose" type="button" aria-label="Close">${icon('x')}</button>
    </div>
    <div class="form-grid" id="modalFields"></div>
    <div id="modalError"></div>
    <div class="modal-actions">
      <button class="btn btn-neutral" type="button" id="modalCancel">Cancel</button>
      <button class="btn btn-primary" type="button" id="modalSubmit">${icon('plus')} Add row</button>
    </div>
  `;
  scrim.appendChild(modal);

  const fieldsWrap = modal.querySelector('#modalFields');
  const editors = [];
  cols.forEach((col) => {
    const field = document.createElement('div');
    field.className = 'field';
    const label = document.createElement('label');
    const editorId = `f_${col.name}`;
    label.textContent = humanizeColumnName(col.name) + (col.notnull && col.dflt === null ? ' *' : '');
    label.htmlFor = editorId;
    const initial = unquoteDefault(col.dflt) ?? (col.name === 'hire_date' ? todayISO() : '');
    const editor = buildFieldEditor(table, col, fkByCol[col.name], initial);
    editor.id = editorId;
    field.append(label, editor);
    fieldsWrap.appendChild(field);
    editors.push({ col, editor });
  });

  if (table === 'employees') {
    const emailField = editors.find((e) => e.col.name === 'email');
    const seedField = editors.find((e) => e.col.name === 'avatar_seed');
    if (emailField && seedField) {
      let seedTouched = false;
      seedField.editor.addEventListener('input', () => { seedTouched = true; });
      emailField.editor.addEventListener('input', () => { if (!seedTouched) seedField.editor.value = emailField.editor.value; });
    }
  }

  const close = () => {
    scrim.hidden = true;
    scrim.innerHTML = '';
    document.removeEventListener('keydown', keyHandler);
    scrim.removeEventListener('click', scrimClickHandler);
    if (previouslyFocused && previouslyFocused.focus) previouslyFocused.focus();
  };
  const scrimClickHandler = (ev) => { if (ev.target === scrim) close(); };
  const keyHandler = (ev) => {
    if (ev.key === 'Escape') { close(); return; }
    if (ev.key !== 'Tab') return;
    const focusable = Array.from(modal.querySelectorAll('button, input, select, textarea, [tabindex]:not([tabindex="-1"])'))
      .filter((el) => !el.disabled && el.offsetParent !== null);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
    else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
  };
  modal.querySelector('#modalClose').addEventListener('click', close);
  modal.querySelector('#modalCancel').addEventListener('click', close);
  scrim.addEventListener('click', scrimClickHandler);
  document.addEventListener('keydown', keyHandler);

  modal.querySelector('#modalSubmit').addEventListener('click', () => {
    const errorBox = modal.querySelector('#modalError');
    errorBox.innerHTML = '';
    const colNames = [];
    const values = [];
    for (const { col, editor } of editors) {
      const v = readFieldEditorValue(editor, col);
      if (col.notnull && col.dflt === null && (v === null || v === '')) {
        errorBox.innerHTML = bannerHTML('error', `${humanizeColumnName(col.name)} is required.`);
        editor.focus();
        return;
      }
      colNames.push(col.name);
      values.push(v);
    }
    const sql = `INSERT INTO ${quoteIdent(table)} (${colNames.map(quoteIdent).join(', ')}) VALUES (${colNames.map(() => '?').join(', ')})`;
    try {
      runParamStatement(sql, values);
      showToast('success', table === 'employees' ? 'Welcome to the team!' : 'Row added.');
      close();
      syncAfterMutation();
    } catch (err) {
      errorBox.innerHTML = bannerHTML('error', err.message);
    }
  });

  if (editors[0]) editors[0].editor.focus();
}

/* ============================================================
   Schema tab
   ============================================================ */

function renderSchema() {
  const panel = document.getElementById('panel-schema');
  panel.innerHTML = `
    <div class="panel-head">
      <div><h2>Schema</h2><p class="sub">Live structure of the in-memory database, straight from <code>sqlite_master</code>.</p></div>
    </div>
    <div class="schema-stack" id="schemaStack"></div>
  `;
  const stack = panel.querySelector('#schemaStack');
  const { columns, rows } = queryAll("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY (type='table') DESC, (type='view') DESC, name");
  if (!rows.length) {
    stack.appendChild(emptyStateNode('Nothing defined yet', 'CREATE TABLE from the SQL Compiler tab to see it here.'));
    return;
  }
  rows.forEach((r) => stack.appendChild(buildSchemaCard(rowToObj(columns, r))));
  // CodeMirror measures line height against real layout; each card was built
  // detached from the document, so re-measure now that it's actually mounted.
  stack.querySelectorAll('.CodeMirror').forEach((el) => el.CodeMirror.refresh());
}

function buildSchemaCard(obj) {
  const card = document.createElement('div');
  card.className = 'card';
  const head = document.createElement('div');
  head.className = 'schema-card-head';
  head.innerHTML = `<h3>${escapeHtml(obj.name)}</h3><span class="schema-kind">${escapeHtml(obj.type)}</span>`;
  card.appendChild(head);

  if (obj.type === 'table') {
    const count = scalar(`SELECT COUNT(*) FROM ${quoteIdent(obj.name)}`);
    const countSpan = document.createElement('span');
    countSpan.className = 'schema-count';
    countSpan.textContent = `${count} row${count === 1 ? '' : 's'}`;
    head.appendChild(countSpan);

    const cols = getColumnInfo(obj.name);
    const fks = getForeignKeys(obj.name);
    const fkByCol = Object.fromEntries(fks.map((fk) => [fk.from, fk]));

    const colTable = document.createElement('table');
    colTable.className = 'col-table';
    colTable.innerHTML = '<thead><tr><th>Column</th><th>Type</th><th>Constraints</th></tr></thead>';
    const tbody = document.createElement('tbody');
    cols.forEach((c) => {
      const badges = [];
      if (c.pk) badges.push('<span class="badge badge-pk">PK</span>');
      if (fkByCol[c.name]) badges.push(`<span class="badge badge-fk">FK &rarr; ${escapeHtml(fkByCol[c.name].table)}</span>`);
      if (c.notnull && !c.pk) badges.push('<span class="badge badge-notnull">NOT NULL</span>');
      if (c.dflt !== null && c.dflt !== undefined) badges.push(`<span class="badge badge-default">DEFAULT ${escapeHtml(String(c.dflt))}</span>`);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="col-name">${escapeHtml(c.name)}</td>
        <td class="col-type">${escapeHtml(c.type || '—')}</td>
        <td><div class="badge-row">${badges.join('') || '—'}</div></td>
      `;
      tbody.appendChild(tr);
    });
    colTable.appendChild(tbody);
    card.appendChild(colTable);

    const indexRows = queryAllParams("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name = ? AND sql IS NOT NULL", [obj.name]);
    if (indexRows.rows.length) {
      const label = document.createElement('div');
      label.className = 'sql-block-label';
      label.textContent = 'Indexes';
      card.appendChild(label);
      const list = document.createElement('div');
      list.style.cssText = 'display:flex;flex-direction:column;gap:4px;margin-bottom:var(--sp-4)';
      indexRows.rows.forEach((r) => {
        const code = document.createElement('code');
        code.style.cssText = 'font-family:var(--font-mono);font-size:.8rem;color:var(--ink-soft);';
        code.textContent = r[1];
        list.appendChild(code);
      });
      card.appendChild(list);
    }
  }

  const sqlLabel = document.createElement('div');
  sqlLabel.className = 'sql-block-label';
  sqlLabel.textContent = obj.type === 'view' ? 'View definition' : 'CREATE TABLE';
  card.appendChild(sqlLabel);
  const cmHost = document.createElement('div');
  cmHost.className = 'cm-shell-readonly';
  card.appendChild(cmHost);
  CodeMirror(cmHost, {
    value: obj.sql + ';',
    mode: 'text/x-sql',
    theme: 'default',
    readOnly: true,
    lineNumbers: false,
    viewportMargin: Infinity,
  });

  return card;
}

/* ============================================================
   SQL Compiler tab
   ============================================================ */

function renderCompilerChrome() {
  const panel = document.getElementById('panel-compiler');
  if (panel.dataset.built === '1') return;
  panel.dataset.built = '1';
  panel.innerHTML = `
    <div class="panel-head">
      <div><h2>SQL Compiler</h2><p class="sub">Real SQLite (via sql.js), running entirely in your browser.</p></div>
    </div>
    <div class="compiler-layout">
      <div class="editor-card">
        <div class="chip-row" id="exampleChips"></div>
        <div class="cm-shell" id="editorHost"></div>
        <div class="editor-toolbar">
          <span class="kbd-hint"><kbd>Ctrl</kbd>/<kbd>&#8984;</kbd>+<kbd>Enter</kbd> to run</span>
          <button class="btn btn-primary" id="runBtn" type="button">${icon('play')} Run query</button>
        </div>
      </div>
      <div class="results-card" id="resultsCard" aria-live="polite">${bannerHTML('empty', 'Run a query to see results here.')}</div>
    </div>
    <div class="card" style="margin-top:var(--sp-5)">
      <div class="sql-block-label">History (this session)</div>
      <div class="history-list" id="historyList"></div>
    </div>
  `;

  const chipsWrap = panel.querySelector('#exampleChips');
  EXAMPLE_QUERIES.forEach((q) => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chip';
    chip.textContent = q.label;
    chip.addEventListener('click', () => { editorCM.setValue(q.sql); editorCM.focus(); });
    chipsWrap.appendChild(chip);
  });

  editorCM = CodeMirror(panel.querySelector('#editorHost'), {
    value: EXAMPLE_QUERIES[0].sql,
    mode: 'text/x-sql',
    theme: 'default',
    lineNumbers: true,
    matchBrackets: true,
    styleActiveLine: true,
    extraKeys: { 'Ctrl-Enter': runCompiler, 'Cmd-Enter': runCompiler, 'Ctrl-Space': 'autocomplete' },
  });
  refreshHintTables();

  panel.querySelector('#runBtn').addEventListener('click', runCompiler);
  renderHistory();
}

function refreshHintTables() {
  if (!editorCM) return;
  const tableHints = {};
  listUserTables().forEach((t) => { tableHints[t] = getColumnInfo(t).map((c) => c.name); });
  editorCM.setOption('hintOptions', { tables: tableHints });
}

function runCompiler() {
  if (!editorCM) return;
  const sqlText = editorCM.getValue().trim();
  if (!sqlText) return;
  const result = runSQL(sqlText);
  renderCompilerResult(result);
  renderHistory();
  if (result.ok) syncAfterMutation();
  else renderTopbarStats();
}

function renderCompilerResult(result) {
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

  if (result.results.length === 0) {
    const rowsWord = result.rowsModified === 1 ? 'row' : 'rows';
    meta.insertAdjacentHTML('beforeend', `<span>${result.rowsModified} ${rowsWord} affected</span>`);
    card.insertAdjacentHTML('beforeend', bannerHTML('success', 'Statement executed — no result set to display.'));
    return;
  }

  result.results.forEach(({ columns, values }) => {
    meta.insertAdjacentHTML('beforeend', `<span>${values.length} row${values.length === 1 ? '' : 's'}</span>`);
    const wrap = document.createElement('div');
    wrap.className = 'data-table-wrap scroll-x';
    const t = document.createElement('table');
    t.className = 'data-table';
    t.innerHTML = `<thead><tr>${columns.map((c) => `<th>${escapeHtml(c)}</th>`).join('')}</tr></thead>`;
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
    t.appendChild(tbody);
    wrap.appendChild(t);
    card.appendChild(wrap);
  });
}

function renderHistory() {
  const list = document.getElementById('historyList');
  if (!list) return;
  list.innerHTML = '';
  if (!queryHistory.length) {
    list.innerHTML = '<p style="color:var(--ink-faint);font-size:.85rem;">Nothing run yet this session.</p>';
    return;
  }
  queryHistory.forEach((entry) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `history-item${entry.ok ? '' : ' err'}`;
    btn.innerHTML = `${icon(entry.ok ? 'check' : 'alert')}<span></span>`;
    btn.querySelector('span').textContent = entry.sql.replace(/\s+/g, ' ').trim();
    btn.title = entry.sql;
    btn.addEventListener('click', () => { editorCM.setValue(entry.sql); editorCM.focus(); });
    list.appendChild(btn);
  });
}

/* ============================================================
   Export
   ============================================================ */

function sqlLiteral(v) {
  if (v === null || v === undefined) return 'NULL';
  if (typeof v === 'number') return String(v);
  return `'${String(v).replace(/'/g, "''")}'`;
}

function exportDatabaseAsSQL() {
  const parts = ['-- Exported from Employee SQL Compiler', `-- ${new Date().toString()}`, ''];
  const { rows: objRows } = queryAll("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY (type='table') DESC, (type='view') DESC");
  objRows.forEach(([, , sql]) => parts.push(sql + ';'));
  parts.push('');
  listUserTables().forEach((t) => {
    const cols = getColumnInfo(t).map((c) => c.name);
    const { rows } = queryAll(`SELECT * FROM ${quoteIdent(t)}`);
    rows.forEach((row) => {
      const vals = row.map(sqlLiteral).join(', ');
      parts.push(`INSERT INTO ${quoteIdent(t)} (${cols.map(quoteIdent).join(', ')}) VALUES (${vals});`);
    });
  });
  return parts.join('\n');
}

function downloadTextFile(filename, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function handleExport() {
  if (!db) return;
  downloadTextFile('employees-export.sql', exportDatabaseAsSQL());
  showToast('success', 'Exported the current database as SQL.');
}
