# Agent notes — DBMS Lab Hub

Static SPA: `index.html` + `/app.js` + `/styles.css` + `/labs.json`. Path routing is client-side; Vercel (`vercel.json`) and `npx serve` (`serve.json`) rewrite these URLs to `index.html`:

- `/` — lab list
- `/practical-file` — compiled practical-file PDF
- `/lab/:id` and `/lab/:id/:tab` — per-lab report / SQL / schema (or directory embed)

Hub scripts and styles **must stay root-absolute** (`/app.js`, `/styles.css`). Relative `href="app.js"` breaks after a refresh on `/lab/...`.

## PDFs (iPhone)

Do **not** embed PDFs with `<iframe src="*.pdf">` or a browser PDF plugin. iOS Safari and iOS Chrome often cannot touch-scroll that pattern, especially inside `overflow: hidden` + a fixed-height frame.

Use `mountPdfViewer` in `app.js`:

- Lazy-load PDF.js only when a PDF view opens
- Render pages as stacked canvases in **document** flow (no nested iframe scroller)
- Keep canvases `pointer-events: none` so finger-drag scrolls the page
- Always show **Open PDF** (`target="_blank"`) and **Download** as a native-viewer fallback

Do not put `overflow: hidden` or a viewport-capped height on `.pdf-viewer`, `.pdf-pages`, `.content`, or `.app`. `.content` uses `flex: 1 0 auto` so iOS cannot trap the stack in a viewport-tall flex item.

## Local

```bash
npx serve .          # applies serve.json rewrites
python -m http.server 8080   # home works; /practical-file and /lab/* 404 without rewrites
```

Regenerate reports with the `generate_report.py` scripts and `generate_practical_file.py` (Python 3, reportlab, pypdf).
