"""
DBMS Lab — 02-09-2026
=====================

Builds `DBMS_Lab_Joins_Report.pdf` from `joins.sql` (SQLite).

Run
---
    python generate_report.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
SQL_PATH = ROOT / "joins.sql"
OUT_PDF = ROOT / "DBMS_Lab_Joins_Report.pdf"

STUDENT = {
    "name": "Harshit Khemani",
    "roll": "241302081",
    "programme": "B.Tech CSE (AI/ML)",
    "section": "Section - C",
    "department": "Department of CSE",
    "school": "School of Engineering and Technology",
    "university": "SGT University",
}

NAVY = colors.HexColor("#14375E")
ACCENT = colors.HexColor("#2E75B6")
LIGHT = colors.HexColor("#EAF1F8")
GREY = colors.HexColor("#5A6672")
RULE = colors.HexColor("#C6D3E2")
MATCH_FILL = colors.HexColor("#B8D4F0")
LEFT_ONLY = colors.HexColor("#FFE8A3")
RIGHT_ONLY = colors.HexColor("#C8E6C9")
ORPHAN = colors.HexColor("#F5C6CB")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

LAB_DATE = "02 September 2026"


def _strip_sql_comments(sql: str) -> str:
    lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if "--" in line:
            line = line[: line.index("--")]
        lines.append(line)
    return "\n".join(lines)


def split_statements(sql: str) -> list[str]:
    body = _strip_sql_comments(sql)
    return [part.strip() for part in body.split(";") if part.strip()]


def format_result(columns: list[str], rows: list[tuple]) -> str:
    if not columns:
        return "(no result set)"
    str_rows = [[str("" if v is None else v) for v in row] for row in rows]
    widths = [len(c) for c in columns]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    header = "  ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    rule = "  ".join("-" * widths[i] for i in range(len(columns)))
    body = [
        "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))
        for row in str_rows
    ]
    return "\n".join([header, rule, *body]) if body else "\n".join([header, rule])


def wrap_line(prefix: str, text: str, width: int = 96) -> list[str]:
    if len(prefix) + len(text) <= width:
        return [prefix + text]
    lines: list[str] = []
    rest = text
    first = prefix
    cont = " " * len(prefix)
    while rest:
        budget = width - len(first)
        if len(rest) <= budget:
            lines.append(first + rest)
            break
        cut = rest.rfind(" ", 0, budget)
        if cut <= 0:
            cut = budget
        lines.append(first + rest[:cut].rstrip())
        rest = rest[cut:].lstrip()
        first = cont
    return lines


def preview_stmt(stmt: str) -> str:
    raw_lines = [ln.rstrip() for ln in stmt.strip().splitlines() if ln.strip()]
    out: list[str] = []
    for i, line in enumerate(raw_lines):
        prefix = "SQL> " if i == 0 else "     "
        out.extend(wrap_line(prefix, line))
    if out:
        out[-1] = out[-1] + ";"
    return "\n".join(out)


def run_sql(sql_text: str) -> str:
    statements = split_statements(sql_text)
    conn = sqlite3.connect(":memory:")
    chunks: list[str] = []
    try:
        for stmt in statements:
            chunks.append(preview_stmt(stmt))
            cur = conn.execute(stmt)
            if cur.description:
                columns = [col[0] for col in cur.description]
                rows = cur.fetchall()
                chunks.append(format_result(columns, rows))
                chunks.append("")
            else:
                kind = stmt.lstrip().split()[0].upper()
                if kind == "INSERT":
                    chunks.append(f"-- {conn.total_changes} row(s) inserted")
                else:
                    chunks.append("-- OK")
                chunks.append("")
    finally:
        conn.close()
    return "\n".join(chunks).rstrip() + "\n"


_base = getSampleStyleSheet()
S = {
    "body": ParagraphStyle(
        "body", parent=_base["Normal"], fontName="Helvetica", fontSize=9.5,
        leading=14, alignment=TA_JUSTIFY, spaceAfter=7, textColor=colors.HexColor("#1A1A1A"),
    ),
    "h1": ParagraphStyle(
        "h1", parent=_base["Heading1"], fontName="Helvetica-Bold", fontSize=16,
        leading=20, textColor=NAVY, spaceBefore=4, spaceAfter=10,
    ),
    "h2": ParagraphStyle(
        "h2", parent=_base["Heading2"], fontName="Helvetica-Bold", fontSize=12,
        leading=15, textColor=NAVY, spaceBefore=12, spaceAfter=6,
    ),
    "h3": ParagraphStyle(
        "h3", parent=_base["Heading3"], fontName="Helvetica-Bold", fontSize=10.5,
        leading=13, textColor=ACCENT, spaceBefore=9, spaceAfter=4,
    ),
    "cell": ParagraphStyle(
        "cell", parent=_base["Normal"], fontName="Helvetica", fontSize=8.5, leading=11.5,
    ),
    "cellb": ParagraphStyle(
        "cellb", parent=_base["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11.5,
        textColor=colors.white,
    ),
    "cover_center": ParagraphStyle(
        "cover_center", parent=_base["Normal"], fontName="Helvetica", fontSize=11,
        leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#1A1A1A"), spaceAfter=4,
    ),
}


class Report(BaseDocTemplate):
    def __init__(self, filename, footer_text, **kw):
        self.footer_text = footer_text
        super().__init__(
            filename, pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=MARGIN, bottomMargin=MARGIN + 0.4 * cm, **kw,
        )
        frame = Frame(
            MARGIN, MARGIN + 0.4 * cm, CONTENT_W,
            PAGE_H - 2 * MARGIN - 0.4 * cm, id="main",
        )
        self.addPageTemplates([
            PageTemplate(id="title", frames=[frame]),
            PageTemplate(id="content", frames=[frame], onPage=self._footer),
        ])

    def _footer(self, canv, doc):
        canv.saveState()
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(MARGIN, MARGIN + 0.15 * cm, PAGE_W - MARGIN, MARGIN + 0.15 * cm)
        canv.setFont("Helvetica", 7.5)
        canv.setFillColor(GREY)
        canv.drawString(MARGIN, MARGIN - 0.15 * cm, self.footer_text)
        canv.drawRightString(PAGE_W - MARGIN, MARGIN - 0.15 * cm, str(canv.getPageNumber()))
        canv.restoreState()


def para(text):
    return Paragraph(text, S["body"])


def heading(text):
    return Paragraph(text, S["h1"])


def sub(text):
    return Paragraph(text, S["h2"])


def accent_rule(frac=0.35):
    rule = Table([[""]], colWidths=[CONTENT_W * frac], rowHeights=[2])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)]))
    rule.hAlign = "CENTER"
    return rule


def table(rows, col_widths=None, pad=5):
    data = []
    for r, row in enumerate(rows):
        style = S["cellb"] if r == 0 else S["cell"]
        data.append([Paragraph(str(c), style) for c in row])
    t = Table(data, colWidths=col_widths, hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]))
    return KeepTogether([t])


def code_block(text: str, size=7.0, leading=8.5):
    style = ParagraphStyle(
        "code_listing", fontName="Courier", fontSize=size, leading=leading,
        textColor=colors.HexColor("#111111"),
    )
    return Preformatted(text.rstrip() + "\n", style)


class DrawingFlowable(Flowable):
    def __init__(self, drawing: Drawing):
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def wrap(self, availWidth, availHeight):
        scale = min(availWidth / self.drawing.width, 1.0)
        self._scale = scale
        return self.drawing.width * scale, self.drawing.height * scale

    def draw(self):
        self.canv.saveState()
        self.canv.scale(self._scale, self._scale)
        renderPDF.draw(self.drawing, self.canv, 0, 0)
        self.canv.restoreState()


def _label(d: Drawing, x: float, y: float, text: str, size: float = 8,
           bold: bool = False, color=NAVY, anchor: str = "middle") -> None:
    d.add(String(x, y, text, fontName="Helvetica-Bold" if bold else "Helvetica",
                 fontSize=size, fillColor=color, textAnchor=anchor))


def _table_box(d: Drawing, x: float, y: float, w: float, h: float,
               title: str, rows: list[str], header_color=NAVY,
               highlight_rows: set[int] | None = None,
               highlight_fill=ORPHAN) -> None:
    highlight_rows = highlight_rows or set()
    d.add(Rect(x, y, w, h, fillColor=WHITE, strokeColor=NAVY, strokeWidth=1.2))
    d.add(Rect(x, y + h - 18, w, 18, fillColor=header_color, strokeColor=NAVY, strokeWidth=0))
    _label(d, x + w / 2, y + h - 13, title, size=9, bold=True, color=WHITE)
    row_h = (h - 22) / max(len(rows), 1)
    for i, row in enumerate(rows):
        ry = y + h - 22 - (i + 0.65) * row_h
        if i in highlight_rows:
            d.add(Rect(x + 2, ry - row_h * 0.35, w - 4, row_h * 0.9,
                       fillColor=highlight_fill, fillOpacity=0.55,
                       strokeColor=colors.HexColor("#C0392B"), strokeWidth=0.6,
                       strokeDashArray=[2, 2]))
        _label(d, x + 6, ry, row, size=7, color=colors.HexColor("#1A1A1A"), anchor="start")


def _venn_pair(d: Drawing, cx: float, cy: float, r: float, mode: str) -> None:
    """Two overlapping circles; mode = inner | left | right | natural."""
    lx, rx = cx - r * 0.62, cx + r * 0.62
    d.add(Circle(lx, cy, r, fillColor=LEFT_ONLY, strokeColor=NAVY,
                 strokeWidth=1, fillOpacity=0.5))
    d.add(Circle(rx, cy, r, fillColor=RIGHT_ONLY, strokeColor=NAVY,
                 strokeWidth=1, fillOpacity=0.5))
    overlap = Circle(cx, cy, r * 0.4, fillColor=MATCH_FILL, strokeColor=ACCENT,
                     strokeWidth=1.2, fillOpacity=0.92)
    if mode in ("inner", "natural"):
        d.add(overlap)
    elif mode == "left":
        d.add(Circle(lx, cy, r, fillColor=LEFT_ONLY, strokeColor=NAVY,
                     strokeWidth=1.2, fillOpacity=0.72))
        d.add(overlap)
    elif mode == "right":
        d.add(Circle(rx, cy, r, fillColor=RIGHT_ONLY, strokeColor=NAVY,
                     strokeWidth=1.2, fillOpacity=0.72))
        d.add(overlap)
    _label(d, lx, cy + r + 14, "emps", size=6.5, color=NAVY)
    _label(d, rx, cy + r + 14, "depts", size=6.5, color=NAVY)


def _legend_chip(d: Drawing, x: float, y: float, fill, label: str) -> None:
    d.add(Rect(x, y, 11, 11, fillColor=fill, strokeColor=NAVY, strokeWidth=0.6))
    _label(d, x + 15, y + 2, label, size=6.5, color=GREY, anchor="start")


def cross_join_diagram(width: float) -> Drawing:
    """Cartesian product: every employee row paired with every department row."""
    d = Drawing(width, 148)
    left_x, mid_x = 10, width * 0.42
    box_w = width * 0.28
    top_y = 118
    row_h = 20

    _table_box(d, left_x, top_y - 4 * row_h - 4, box_w, 4 * row_h + 22, "departments",
               ["1  Eng & Tech", "2  Management", "3  Law", "… 6 rows total"])
    _table_box(d, mid_x, top_y - 2 * row_h - 4, box_w, 2 * row_h + 22, "employees",
               ["1  Ananya", "2  Rohan", "… 7 rows total"])

    grid_x = width * 0.72
    cell = 22
    pairs = [("1·1", "1·2"), ("2·1", "2·2"), ("3·1", "3·2")]
    for ri, row in enumerate(pairs):
        for ci, cell_label in enumerate(row):
            gx = grid_x + ci * (cell + 4)
            gy = 88 - ri * (cell + 6)
            d.add(Rect(gx, gy, cell, cell, fillColor=LIGHT, strokeColor=ACCENT, strokeWidth=0.8))
            _label(d, gx + cell / 2, gy + cell / 2 - 3, cell_label, size=6, color=NAVY)

    _label(d, grid_x + cell + 2, 28, "×", size=16, bold=True, color=ACCENT)
    _label(d, grid_x + cell + 2, 12, "6 × 7 = 42 rows", size=8, bold=True, color=NAVY)
    d.add(Line(left_x + box_w + 4, 70, grid_x - 6, 70, strokeColor=GREY, strokeWidth=0.8,
               strokeDashArray=[3, 3]))
    _label(d, (left_x + box_w + grid_x) / 2, 76, "no join condition", size=7, color=GREY)
    return d


def natural_join_diagram(width: float) -> Drawing:
    d = Drawing(width, 128)
    _venn_pair(d, width * 0.32, 68, 32, "natural")
    note_x = width * 0.58
    _label(d, note_x, 98, "Implicit match on", size=7.5, color=NAVY, anchor="start")
    _label(d, note_x, 84, "shared column deptID", size=7.5, bold=True, color=ACCENT, anchor="start")
    _label(d, note_x, 66, "6 matched rows returned", size=7, color=GREY, anchor="start")
    _label(d, note_x, 52, "Neha (dept 99) dropped", size=7, color=GREY, anchor="start")
    _label(d, note_x, 38, "Humanities dropped", size=7, color=GREY, anchor="start")
    _legend_chip(d, note_x, 18, MATCH_FILL, "Matched rows")
    _legend_chip(d, note_x + 90, 18, ORPHAN, "Dropped orphans")
    return d


def inner_join_diagram(width: float) -> Drawing:
    d = Drawing(width, 128)
    _venn_pair(d, width * 0.32, 68, 32, "inner")
    note_x = width * 0.58
    _label(d, note_x, 98, "Explicit ON clause:", size=7.5, color=NAVY, anchor="start")
    _label(d, note_x, 84, "e.deptID = d.deptID", size=7, bold=True, color=ACCENT, anchor="start")
    _label(d, note_x, 66, "Only overlapping rows", size=7, color=GREY, anchor="start")
    _label(d, note_x, 52, "returned (6 rows)", size=7, color=GREY, anchor="start")
    _legend_chip(d, note_x, 18, MATCH_FILL, "Matched rows only")
    return d


def left_outer_join_diagram(width: float) -> Drawing:
    d = Drawing(width, 142)
    box_w = width * 0.44
    _table_box(
        d, 10, 24, box_w, 100, "employees (left table)",
        ["Ananya   dept=1", "Rohan    dept=2", "Priya    dept=3", "Neha     dept=99  ← no match"],
        highlight_rows={3}, highlight_fill=ORPHAN,
    )
    _venn_pair(d, width * 0.76, 74, 28, "left")
    _label(d, width / 2, 8, "All left rows kept — right columns NULL when unmatched",
           size=6.5, color=colors.HexColor("#C0392B"))
    return d


def right_outer_join_diagram(width: float) -> Drawing:
    d = Drawing(width, 142)
    box_w = width * 0.44
    _table_box(
        d, 10, 24, box_w, 100, "departments (right table)",
        ["1  Eng & Tech", "2  Management", "3  Law", "6  Humanities  ← no employees"],
        highlight_rows={3}, highlight_fill=RIGHT_ONLY,
    )
    _venn_pair(d, width * 0.76, 74, 28, "right")
    _label(d, width / 2, 8, "All right rows kept — left columns NULL when unmatched",
           size=6.5, color=colors.HexColor("#27AE60"))
    return d


def self_join_diagram(width: float) -> Drawing:
    d = Drawing(width, 118)
    box_w = width * 0.36
    left_x = width * 0.06
    right_x = width * 0.56
    y = 22

    _table_box(d, left_x, y, box_w, 68, "employees e",
               ["empID", "empName", "managerID"], header_color=ACCENT)
    _table_box(d, right_x, y, box_w, 68, "employees m",
               ["empID", "empName", "managerID"], header_color=NAVY)

    ax, ay = left_x + box_w, y + 34
    bx, by = right_x, y + 34
    d.add(Line(ax, ay, bx, by, strokeColor=ACCENT, strokeWidth=1.5))
    d.add(Line(bx, by, bx - 8, by + 4, strokeColor=ACCENT, strokeWidth=1.5))
    d.add(Line(bx, by, bx - 8, by - 4, strokeColor=ACCENT, strokeWidth=1.5))
    _label(d, (ax + bx) / 2, ay + 12, "e.managerID = m.empID", size=7.5, bold=True, color=ACCENT)
    _label(d, width / 2, 8, "Same table twice — two aliases", size=7, color=GREY)
    return d


def schema_er_diagram(width: float) -> Drawing:
    d = Drawing(width, 148)
    left_w, right_w = width * 0.38, width * 0.38
    left_x = width * 0.06
    right_x = width * 0.56
    y = 14

    _table_box(
        d, left_x, y, left_w, 112, "departments",
        ["PK  deptID   INTEGER", "    deptName TEXT", "", "6 rows (deptID 1–6)"],
    )
    _table_box(
        d, right_x, y, right_w, 112, "employees",
        ["PK  empID      INTEGER", "    empName    TEXT", "FK  deptID     INTEGER",
         "FK  managerID  INTEGER", "    salary     NUMERIC", "", "7 rows"],
    )

    ax, ay = left_x + left_w, y + 72
    bx, by = right_x, y + 72
    d.add(Line(ax, ay, bx, by, strokeColor=ACCENT, strokeWidth=1.5))
    d.add(Line(bx, by, bx - 8, by + 4, strokeColor=ACCENT, strokeWidth=1.5))
    d.add(Line(bx, by, bx - 8, by - 4, strokeColor=ACCENT, strokeWidth=1.5))
    _label(d, (ax + bx) / 2, ay + 10, "deptID", size=7.5, bold=True, color=ACCENT)

    loop_x = right_x + right_w * 0.5
    loop_y = y + 24
    d.add(Circle(loop_x, loop_y, 12, fillColor=LIGHT, strokeColor=ACCENT, strokeWidth=1))
    _label(d, loop_x, loop_y - 3, "mgr", size=6, bold=True, color=ACCENT)
    _label(d, loop_x, loop_y - 18, "managerID → empID", size=6.5, color=GREY)
    return d


def figure(drawing: Drawing, caption: str | None = None) -> list:
    items: list = [Spacer(1, 0.25 * cm), DrawingFlowable(drawing), Spacer(1, 0.2 * cm)]
    if caption:
        cap_style = ParagraphStyle(
            "fig_cap", parent=S["body"], fontSize=8, alignment=TA_CENTER,
            textColor=GREY, spaceAfter=10, leading=11,
        )
        items.append(Paragraph(caption, cap_style))
    return items


def theory_block(title: str, body: str, drawing: Drawing, caption: str) -> list:
    """Keep subsection text and its figure together on one page when possible."""
    block = [
        sub(title),
        para(body),
        *figure(drawing, caption),
    ]
    return [KeepTogether(block)]


def cover(st, exp_no: str, title: str, methods: str, dataset: str, lab_date: str):
    st.append(NextPageTemplate("content"))
    st.append(Spacer(1, 1.4 * cm))
    st.append(Paragraph(STUDENT["university"].upper(), ParagraphStyle(
        "u", parent=S["cover_center"], fontName="Helvetica-Bold", fontSize=13, textColor=NAVY,
    )))
    st.append(Paragraph(STUDENT["school"], S["cover_center"]))
    st.append(Paragraph(STUDENT["department"], S["cover_center"]))
    st.append(Spacer(1, 0.6 * cm))
    st.append(accent_rule(0.45))
    st.append(Spacer(1, 0.5 * cm))
    st.append(Paragraph("DATABASE MANAGEMENT SYSTEMS LABORATORY", ParagraphStyle(
        "lab", parent=S["cover_center"], fontSize=10, textColor=ACCENT, fontName="Helvetica-Bold",
    )))
    st.append(Spacer(1, 0.25 * cm))
    st.append(Paragraph(f"Experiment {exp_no}", ParagraphStyle(
        "en", parent=S["cover_center"], fontSize=11, textColor=GREY, fontName="Helvetica-Bold",
    )))
    st.append(Spacer(1, 0.35 * cm))
    st.append(Paragraph(title, ParagraphStyle(
        "t", parent=S["cover_center"], fontName="Helvetica-Bold", fontSize=14,
        leading=19, textColor=NAVY,
    )))
    st.append(Spacer(1, 0.7 * cm))
    st.append(table(
        [
            ["Field", "Details"],
            ["Student", STUDENT["name"]],
            ["Roll No.", STUDENT["roll"]],
            ["Programme", STUDENT["programme"]],
            ["Section", STUDENT["section"]],
            ["Lab Date", lab_date],
            ["Dataset", dataset],
            ["Methods", methods],
        ],
        col_widths=[CONTENT_W * 0.28, CONTENT_W * 0.62],
    ))
    st.append(PageBreak())


def write_report(path: Path, footer: str, story: list) -> None:
    doc = Report(str(path), footer_text=footer)
    doc.multiBuild(story)


def build() -> None:
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    output = run_sql(sql_text)

    st = []
    cover(
        st, "3",
        "SQL Joins — CROSS, NATURAL, INNER, OUTER & SELF",
        "CROSS JOIN, NATURAL JOIN, INNER JOIN, LEFT/RIGHT OUTER JOIN, SELF JOIN",
        "departments (6) + employees (7) · deptID + managerID",
        LAB_DATE,
    )

    st.append(heading("1. Aim"))
    st.append(para(
        "To combine rows from related tables using "
        "<font face='Courier'>CROSS JOIN</font>, "
        "<font face='Courier'>NATURAL JOIN</font>, "
        "<font face='Courier'>INNER JOIN</font>, "
        "<font face='Courier'>LEFT OUTER JOIN</font>, "
        "<font face='Courier'>RIGHT OUTER JOIN</font>, and "
        "<font face='Courier'>SELF JOIN</font>; to compare how each join "
        "type treats unmatched rows; and to understand when to use each one."
    ))

    st.append(heading("2. Theory"))

    st.extend(theory_block(
        "2.1 CROSS JOIN",
        "A <font face='Courier'>CROSS JOIN</font> returns the Cartesian product "
        "of two tables: every row from the first table is paired with every row "
        "from the second. There is no join condition. With 6 departments and "
        "7 employees the result has 6 × 7 = <b>42 rows</b>. Cross joins are "
        "rare in everyday queries but useful for generating combinations "
        "(e.g. all size–colour pairs) or as a building block for other joins.",
        cross_join_diagram(CONTENT_W),
        "<i>Figure 1</i> — CROSS JOIN pairs every department row with every employee row (42 combinations).",
    ))

    st.extend(theory_block(
        "2.2 NATURAL JOIN",
        "A <font face='Courier'>NATURAL JOIN</font> automatically matches rows "
        "on every column that appears in both tables with the same name. Here, "
        "both tables share <font face='Courier'>deptID</font>, so the condition "
        "is implicit. Only rows with a matching <font face='Courier'>deptID</font> "
        "in both tables are returned — the same six rows as "
        "<font face='Courier'>INNER JOIN</font> when "
        "<font face='Courier'>deptID</font> is the sole common column. "
        "(SQL Server does not support <font face='Courier'>NATURAL JOIN</font>; "
        "use an explicit <font face='Courier'>INNER JOIN</font> instead.)",
        natural_join_diagram(CONTENT_W),
        "<i>Figure 2</i> — NATURAL JOIN keeps only rows where <font face='Courier'>deptID</font> matches in both tables.",
    ))

    st.extend(theory_block(
        "2.3 INNER JOIN",
        "An <font face='Courier'>INNER JOIN</font> returns only rows where the "
        "explicit join condition is satisfied. Unmatched rows from either table "
        "are discarded. It is the most common join: use it when you only want "
        "records that have a partner on both sides.",
        inner_join_diagram(CONTENT_W),
        "<i>Figure 3</i> — INNER JOIN returns only the overlapping region (6 matched rows).",
    ))

    st.extend(theory_block(
        "2.4 LEFT OUTER JOIN",
        "A <font face='Courier'>LEFT OUTER JOIN</font> keeps every row from the "
        "left table. If no match exists in the right table, the right-hand "
        "columns are filled with <font face='Courier'>NULL</font>. Employee "
        "<font face='Courier'>Neha Gupta</font> (deptID 99) has no matching "
        "department and therefore appears with a null department name.",
        left_outer_join_diagram(CONTENT_W),
        "<i>Figure 4</i> — LEFT OUTER JOIN preserves Neha (deptID 99) even though no department matches.",
    ))

    st.extend(theory_block(
        "2.5 RIGHT OUTER JOIN",
        "A <font face='Courier'>RIGHT OUTER JOIN</font> keeps every row from the "
        "right table. Unmatched left-hand columns become "
        "<font face='Courier'>NULL</font>. "
        "<font face='Courier'>School of Humanities</font> (deptID 6) has no "
        "employees and therefore appears with null employee fields. A "
        "<font face='Courier'>RIGHT JOIN</font> can always be rewritten as a "
        "<font face='Courier'>LEFT JOIN</font> by swapping the table order.",
        right_outer_join_diagram(CONTENT_W),
        "<i>Figure 5</i> — RIGHT OUTER JOIN preserves Humanities (deptID 6) even though no employee belongs to it.",
    ))

    st.extend(theory_block(
        "2.6 SELF JOIN",
        "A <font face='Courier'>SELF JOIN</font> joins a table to itself using "
        "two different aliases. It is not a separate SQL keyword — it is an "
        "<font face='Courier'>INNER</font> or <font face='Courier'>LEFT JOIN</font> "
        "where both sides are the same table. Here, "
        "<font face='Courier'>employees e</font> is joined to "
        "<font face='Courier'>employees m</font> on "
        "<font face='Courier'>e.managerID = m.empID</font> to list each "
        "employee alongside their manager's name.",
        self_join_diagram(CONTENT_W),
        "<i>Figure 6</i> — SELF JOIN: the same table appears twice with different aliases.",
    ))

    st.append(sub("2.7 Differences between all join types"))
    st.append(table(
        [
            ["Join type", "Join condition?", "Unmatched rows", "Typical use"],
            ["CROSS JOIN", "None (Cartesian product)", "N/A — all combinations", "Generate all pairs"],
            ["NATURAL JOIN", "Implicit (same column names)", "Dropped from both sides", "Quick join on shared key"],
            ["INNER JOIN", "Explicit ON clause", "Dropped from both sides", "Only matching records"],
            ["LEFT OUTER JOIN", "Explicit ON clause", "Left kept; right NULL", "Keep all from left table"],
            ["RIGHT OUTER JOIN", "Explicit ON clause", "Right kept; left NULL", "Keep all from right table"],
            ["SELF JOIN", "Explicit ON (same table)", "Depends on INNER/LEFT used", "Hierarchies, comparisons"],
        ],
        col_widths=[CONTENT_W * 0.18, CONTENT_W * 0.22, CONTENT_W * 0.28, CONTENT_W * 0.22],
        pad=3,
    ))
    st.append(Spacer(1, 0.25 * cm))
    st.append(para(
        "<b>Key distinctions:</b> "
        "<font face='Courier'>CROSS JOIN</font> multiplies rows with no filter. "
        "<font face='Courier'>INNER</font> and <font face='Courier'>NATURAL</font> "
        "return only matches. "
        "<font face='Courier'>LEFT</font> and <font face='Courier'>RIGHT OUTER</font> "
        "preserve one side's orphans. "
        "<font face='Courier'>SELF JOIN</font> is a technique (same table, two "
        "aliases), not a separate result category — it uses inner or outer join "
        "semantics on a single table."
    ))

    st.append(heading("3. Schema"))
    st.append(para(
        "Two tables are linked by <font face='Courier'>deptID</font>. "
        "<font face='Courier'>employees</font> also references itself through "
        "<font face='Courier'>managerID</font> for the self join (see Figure 6)."
    ))
    st.extend(figure(
        schema_er_diagram(CONTENT_W),
        "<i>Figure 7</i> — Schema: <font face='Courier'>employees.deptID</font> references "
        "<font face='Courier'>departments.deptID</font>; <font face='Courier'>managerID</font> is a self-reference.",
    ))
    st.append(table(
        [
            ["Table", "Attribute", "Type", "Role"],
            ["departments", "deptID", "INTEGER / INT", "Primary key"],
            ["departments", "deptName", "TEXT / VARCHAR", "School name"],
            ["employees", "empID", "INTEGER / INT", "Primary key"],
            ["employees", "empName", "TEXT / VARCHAR", "Employee name"],
            ["employees", "deptID", "INTEGER / INT", "FK → departments"],
            ["employees", "managerID", "INTEGER / INT", "FK → employees (self)"],
            ["employees", "salary", "NUMERIC(10,2)", "Monthly salary"],
        ],
        col_widths=[CONTENT_W * 0.16, CONTENT_W * 0.2, CONTENT_W * 0.2, CONTENT_W * 0.34],
        pad=4,
    ))

    st.append(heading("4. Procedure"))
    st.append(para("1. Create <font face='Courier'>departments</font> and <font face='Courier'>employees</font> (with <font face='Courier'>managerID</font> for self join)."))
    st.append(para("2. Insert six departments and seven employees, including deliberate mismatches for outer joins."))
    st.append(para("3. Display both base tables."))
    st.append(para("4. Run <font face='Courier'>CROSS JOIN</font> — expect 42 rows (count shown; sample limited to 8)."))
    st.append(para("5. Run <font face='Courier'>NATURAL JOIN</font> and <font face='Courier'>INNER JOIN</font> — expect six matched rows."))
    st.append(para("6. Run <font face='Courier'>LEFT OUTER JOIN</font> — expect seven rows (one employee without a department)."))
    st.append(para("7. Run <font face='Courier'>RIGHT OUTER JOIN</font> — expect seven rows (one department without employees)."))
    st.append(para("8. Run <font face='Courier'>SELF JOIN</font> — expect seven rows listing each employee and their manager."))

    st.append(heading("5. Source Code"))
    st.append(code_block(sql_text, size=6.4, leading=8.0))

    st.append(heading("6. Output"))
    st.append(para(
        "The script was executed in SQLite. Each query's result set is shown "
        "below in execution order."
    ))
    st.append(code_block(output, size=6.2, leading=7.8))

    st.append(heading("7. Results"))
    st.append(para("Row counts returned by each join on this dataset:"))
    st.append(table(
        [
            ["Join type", "Rows returned", "Unmatched handling"],
            ["CROSS JOIN", "42", "No condition — every dept × every employee"],
            ["NATURAL JOIN", "6", "Drops non-matching rows from both sides"],
            ["INNER JOIN", "6", "Same as NATURAL JOIN here"],
            ["LEFT OUTER JOIN", "7", "Keeps Neha Gupta (deptID 99); deptName is NULL"],
            ["RIGHT OUTER JOIN", "7", "Keeps Humanities (deptID 6); employee cols are NULL"],
            ["SELF JOIN", "7", "All employees; Ananya has NULL manager (top of chain)"],
        ],
        col_widths=[CONTENT_W * 0.22, CONTENT_W * 0.14, CONTENT_W * 0.54],
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "<font face='Courier'>CROSS JOIN</font> produces the largest result because "
        "it ignores relationships entirely. "
        "<font face='Courier'>INNER JOIN</font> and "
        "<font face='Courier'>NATURAL JOIN</font> return only the six employees "
        "whose <font face='Courier'>deptID</font> exists in "
        "<font face='Courier'>departments</font>. Outer joins add the orphan "
        "employee (left) or orphan department (right). "
        "<font face='Courier'>SELF JOIN</font> does not change row count here "
        "because a <font face='Courier'>LEFT JOIN</font> keeps every employee "
        "and simply leaves the manager column null for Ananya Sharma, who has "
        "no manager."
    ))

    st.append(heading("8. Conclusion"))
    st.append(para(
        "SQL joins answer different questions about related data. "
        "<font face='Courier'>CROSS JOIN</font> asks &ldquo;every combination?&rdquo; "
        "<font face='Courier'>INNER JOIN</font> asks &ldquo;only matches?&rdquo; "
        "Outer joins ask &ldquo;keep everyone from this side even without a match?&rdquo; "
        "<font face='Courier'>SELF JOIN</font> asks &ldquo;how do rows in this "
        "table relate to other rows in the same table?&rdquo; Choosing the right "
        "join depends on whether you need all combinations, only matches, or "
        "orphan rows from a specific side."
    ))

    write_report(
        OUT_PDF,
        "DBMS Lab · 02-09-2026 · SQL Joins · Harshit Khemani",
        st,
    )
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
