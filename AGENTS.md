# Agent notes — DBMS Lab Hub

Static SPA: `index.html` + `/app.js` + `/styles.css` + `/labs.json`. Path routing is client-side; Vercel (`vercel.json`) and `npx serve` (`serve.json`) rewrite these URLs to `index.html`:

- `/` — lab list
- `/practical-file` — compiled practical-file PDF
- `/lab/:id` and `/lab/:id/:tab` — per-lab report / SQL / schema (or directory embed)

Hub scripts and styles **must stay root-absolute** (`/app.js`, `/styles.css`). Relative `href="app.js"` breaks after a refresh on `/lab/...`.

## PDFs (Chrome mobile, iOS Chrome, desktop)

Do **not** embed PDFs with `<iframe src="*.pdf">` or a browser PDF plugin. Chrome on phones (Android Chrome and iOS Chrome) and desktop Chrome’s plugin often cannot touch/wheel-scroll that pattern inside a clipped, fixed-height frame.

Use `mountPdfViewer` in `app.js`:

- Lazy-load PDF.js only when a PDF view opens
- Render pages as stacked canvases in **document** flow (the viewport is the only scroller — no `overflow` on `html`/`body`, no nested iframe)
- Keep canvases `pointer-events: none` so a finger-drag scrolls the page
- Always show **Open PDF** (`target="_blank"`) and **Download** as a native-viewer fallback

Do not put `overflow: hidden`, `position: sticky` on the PDF chrome, or a viewport-capped height on `.pdf-viewer`, `.pdf-pages`, `.content`, or `.app`. `.content` uses `flex: 1 0 auto` so Chrome cannot trap the stack in a viewport-tall flex item.

## Local

```bash
npx serve .          # applies serve.json rewrites
python -m http.server 8080   # home works; /practical-file and /lab/* 404 without rewrites
```

Regenerate reports with the `generate_report.py` scripts and `generate_practical_file.py` (Python 3, reportlab, pypdf).
