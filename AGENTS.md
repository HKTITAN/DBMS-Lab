# Agent notes — DBMS Lab

SGT University, Semester 5, Database Management Systems. Student: **Harshit Khemani** (roll **241302081**), B.Tech CSE (AI/ML), Section C. Faculty on the practical-file cover: Dr. Poonam Sangwan.

- Repo: https://github.com/HKTITAN/DBMS-Lab
- Live: https://dbms-lab-sem5.khe.money/ (Vercel; also dbms-lab-sem5.vercel.app)
- Push/merge **`main`** to deploy. Hub shell files (`index.html`, `app.js`, `styles.css`, `labs.json`) use `Cache-Control: max-age=0, must-revalidate` in `vercel.json`.

These are working notes for editing this tree. Do not break existing labs.

## Layout

Dated lab folders `DD-MM-YYYY/` (same string as `labs.json` `id` / `folder`):

| Folder | Exp | Hub `type` | Typical files |
|--------|-----|------------|----------------|
| `19-08-2026/` | 1 | `directory` | Embedded mini-app: `index.html`, `app.js`, `styles.css`, `schema.sql`, `seed.sql` |
| `26-08-2026/` | 2 | `sql` | `employees.sql`, `employees.sqlserver.sql`, `generate_report.py`, PDF report |
| `02-09-2026/` | 3 | `sql` | `joins.sql`, `joins.sqlserver.sql`, `generate_report.py`, PDF report |
| `09-09-2026/` | 4 | `sql` | `employee.sql`, `employee.sqlserver.sql`, `generate_report.py`, PDF report |

Hub (site root): `index.html`, `app.js`, `styles.css`, `labs.json`, `vercel.json`, `serve.json`.

Compiled file: `generate_practical_file.py` → `DBMS_Practical_File.pdf` (cover logo `assets/sgt-logo.png`).

`requirements.txt`: `reportlab`, `pypdf`. Python 3.

Not in the hub: `TA-1/`, `TA-Phase-2/` (term papers), `banking_er_diagram.excalidraw`.

## How to add a lab

1. New folder `DD-MM-YYYY/` matching the lab date.
2. SQLite-first script (`DROP TABLE IF EXISTS` so it re-runs). Optional `*.sqlserver.sql` twin for the class server — same questions, T-SQL types.
3. For a PDF report lab: `generate_report.py` that writes the standalone PDF, then run it.
4. Register a newest-first object in `labs.json` (`id`/`folder` = folder name, `experiment` number, `sqlFile` + `report` for `type: "sql"`, or `directoryTabs` for `type: "directory"`).
5. Append `generate_practical_file.py` `EXPERIMENTS` and the merge path in `merge_reports()` (exp 1 is built from source; exp 2+ skip the per-report cover and stitch the body).
6. Rebuild `DBMS_Practical_File.pdf` (`python generate_practical_file.py`).
7. Update `README.md` routes + lab table. Merge to `main`.

## Reports (ReportLab)

Each `generate_report.py` has a `STUDENT` dict (name, roll, programme, section, department, school, university) and a `QUESTIONS` list.

Questions section:

- Keep **lab-sheet wording** (including sheet quirks; document them in a `note` if needed, e.g. “distant” → `DISTINCT`).
- Clean numbered list (`1(a)` / `1(b)` when the sheet used two “1.” items).
- Nest CREATE attributes as `subitems`, not a run-on sentence.

Rebuild the **standalone** PDF in the lab folder first, then the **compiled** practical file at the repo root.

## Hub

Static SPA. `vercel.json` / `serve.json` rewrite `/practical-file` and `/lab/:id/:tab` to `index.html`. Hub assets **must** be root-absolute (`/app.js`, `/styles.css`) plus `<base href="/">` so a refresh on `/lab/...` still boots.

Routes: `/` (cards from `labs.json`), `/lab/<id>/<tab>` (`report` | `sql` | `schema`, or directory tabs), `/practical-file`.

`type: "sql"`: sql.js playground (CodeMirror); `SELECT`/`PRAGMA` become chips, other statements are setup. `type: "directory"`: iframe of `/<folder>/index.html?embed=1&tab=...` (employee directory only).

**PDFs (Chrome on phones is the primary case — Android Chrome and iOS Chrome — plus desktop Chrome):** never `<iframe src="*.pdf">`. Use `mountPdfViewer` in `app.js`: lazy-load PDF.js, stacked canvases in **document** flow, canvases `pointer-events: none`, **Open PDF** (`target="_blank"`) + **Download**. Do not put `overflow: hidden`, `position: sticky` on PDF chrome, or a viewport-capped height on `.pdf-viewer` / `.pdf-pages` / `.content` / `.app`. `.content` is `flex: 1 0 auto`. Do not set `overflow` or `touch-action` on `html`/`body` (Chrome then nests a body scroller).

Local: `npx serve .` (rewrites). `python -m http.server` only serves `/`.

## Conventions

- SQLite-first, re-runnable (`DROP TABLE IF EXISTS`).
- Indian academic lab style: numbered questions, theory, schema, procedure/SQL, captured SQLite output, results, conclusion.
- Practical-file subtitle on `/practical-file` is derived from `labs.json` (do not hardcode “Experiments 1–3”).
- Do not change older experiments unless the task says so.
