# DBMS Lab

SGT University — Database Management Systems laboratory work by **Harshit Khemani** (241302081).

## Web app

Open [`index.html`](index.html) or visit the [GitHub Pages site](https://hktitan.github.io/DBMS-Lab/) to:

- Browse all lab sessions in one place
- View experiment reports as PDFs
- Run each lab's SQL in a real in-browser SQLite engine ([sql.js](https://sql.js.org/))

> **Note:** The hub needs to be served over HTTP (GitHub Pages, VS Code Live Server, or `python -m http.server`). Opening `index.html` directly from the filesystem won't load SQL files.

### Local server

```bash
python -m http.server 8080
# then open http://localhost:8080
```

## Lab sessions

| Date | Topic | Files |
|------|-------|-------|
| [19-08-2026](19-08-2026/) | Employee directory — schema, CRUD, views | Full interactive app |
| [26-08-2026](26-08-2026/) | CREATE TABLE & ALTER TABLE (rename column) | `employees.sql`, PDF report |
| [02-09-2026](02-09-2026/) | SQL Joins (CROSS, NATURAL, INNER, OUTER, SELF) | `joins.sql`, PDF report |

## Regenerating PDF reports

```bash
cd 26-08-2026 && python generate_report.py
cd 02-09-2026 && python generate_report.py
```

Requires Python 3 and `reportlab`.

## Stack

- **SQL engine:** [sql.js](https://sql.js.org/) (SQLite → WebAssembly)
- **Editor:** [CodeMirror 5](https://codemirror.net/5/)
- **PDF reports:** generated with ReportLab
