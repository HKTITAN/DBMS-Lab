# Employee SQL Compiler

A DBMS lab exercise: an `employees` / `departments` schema plus a browser-based
frontend for browsing, editing, and querying it with real SQL — styled after
[Duolingo's design language](https://design.duolingo.com/).

## Run it

Just open [`index.html`](index.html) in a browser. No build step, no server,
no install. It needs internet on first load (it pulls SQLite-as-WebAssembly
and the code editor from a CDN); after that everything runs locally in-tab.

## Files

| File | What it is |
|---|---|
| [`schema.sql`](schema.sql) | `departments` + `employees` DDL — PK/FK/CHECK constraints, indexes, and an `employee_directory` view |
| [`seed.sql`](seed.sql) | 6 departments, 26 employees, 3-tier reporting structure |
| [`index.html`](index.html) / [`styles.css`](styles.css) / [`app.js`](app.js) | the frontend |
| [`avatars/`](avatars/) | the 26 seed employees' avatars, downloaded once so they load instantly offline |

## How the frontend works

- **Departments** — colorful department cards with avatar stacks of everyone in each team.
- **Data** — an editable spreadsheet-style grid for any table in the database (starts with `employees` and `departments`, and picks up any table you `CREATE` yourself). Click a cell to edit it; that fires a real `UPDATE`.
- **Schema** — live structure straight from `sqlite_master`: columns, types, PK/FK/NOT NULL/DEFAULT badges, indexes, and the exact `CREATE TABLE` text.
- **SQL Compiler** — a real SQL editor (autocomplete, syntax highlighting) running against an actual in-memory SQLite database via [sql.js](https://sql.js.org/). Nothing is simulated — `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP` all run for real.

Every screen reads from the same live database, so a grid edit shows up in
Departments immediately, and a `CREATE TABLE` in the Compiler shows up in Data
and Schema immediately.

Nothing persists or leaves the browser — reloading or hitting **Reset data**
restores the original `schema.sql` + `seed.sql` state, so it's safe to
experiment (drop a table, break a constraint, whatever the lab calls for).
**Export .sql** downloads the current state — including anything you've
changed — as a plain `.sql` file.

## Credits

- SQL engine: [sql.js](https://sql.js.org/) (SQLite compiled to WebAssembly)
- Code editor: [CodeMirror 5](https://codemirror.net/5/)
- Avatars: [DiceBear "Dylan"](https://www.dicebear.com/styles/dylan/), a remix of
  Natalia Spivak's [Dylan! The Avatar Generator](https://www.figma.com/community/file/1356575240759683500),
  licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — the 26 seed avatars are downloaded
  into [`avatars/`](avatars/) so they load instantly and work offline; anyone you add through the app gets
  their avatar generated live from the same API
- Fonts: [Baloo 2](https://fonts.google.com/specimen/Baloo+2) & [Nunito](https://fonts.google.com/specimen/Nunito) (Google Fonts)
