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
               title: str, rows: list[str], header_color=NAVY) -> None:
    d.add(Rect(x, y, w, h, fillColor=WHITE, strokeColor=NAVY, strokeWidth=1.2))
    d.add(Rect(x, y + h - 18, w, 18, fillColor=header_color, strokeColor=NAVY, strokeWidth=0))
    _label(d, x + w / 2, y + h - 13, title, size=9, bold=True, color=WHITE)
    row_h = (h - 22) / max(len(rows), 1)
    for i, row in enumerate(rows):
        ry = y + h - 22 - (i + 0.65) * row_h
        _label(d, x + 6, ry, row, size=7, color=colors.HexColor("#1A1A1A"), anchor="start")


def schema_er_diagram(width: float) -> Drawing:
    d = Drawing(width, 155)
    left_w, right_w = width * 0.38, width * 0.38
    left_x = width * 0.06
    right_x = width * 0.56
    y = 18

    _table_box(
        d, left_x, y, left_w, 118, "departments",
        ["PK  deptID   INTEGER", "    deptName TEXT", "", "6 rows (deptID 1–6)"],
    )
    _table_box(
        d, right_x, y, right_w, 118, "employees",
        ["PK  empID    INTEGER", "    empName  TEXT", "FK  deptID   INTEGER", "    salary   NUMERIC", "", "7 rows"],
    )

    ax, ay = left_x + left_w, y + 72
    bx, by = right_x, y + 72
    d.add(Line(ax, ay, bx, by, strokeColor=ACCENT, strokeWidth=1.5))
    # arrowhead
    d.add(Line(bx, by, bx - 8, by + 4, strokeColor=ACCENT, strokeWidth=1.5))
    d.add(Line(bx, by, bx - 8, by - 4, strokeColor=ACCENT, strokeWidth=1.5))
    _label(d, (ax + bx) / 2, ay + 10, "deptID", size=7.5, bold=True, color=ACCENT)

    _label(d, width / 2, 8, "Figure 1 — Schema: employees.deptID references departments.deptID",
           size=7.5, color=GREY)
    return d


def _venn_pair(d: Drawing, cx: float, cy: float, r: float,
               mode: str, title: str) -> None:
    """Draw two overlapping circles; mode = inner | left | right | natural."""
    lx, rx = cx - r * 0.55, cx + r * 0.55
    left_c = Circle(lx, cy, r, fillColor=LEFT_ONLY, strokeColor=NAVY, strokeWidth=1, fillOpacity=0.55)
    right_c = Circle(rx, cy, r, fillColor=RIGHT_ONLY, strokeColor=NAVY, strokeWidth=1, fillOpacity=0.55)
    d.add(left_c)
    d.add(right_c)

    overlap = Circle(cx, cy, r * 0.45, fillColor=MATCH_FILL, strokeColor=ACCENT,
                     strokeWidth=1.2, fillOpacity=0.9)
    if mode in ("inner", "natural"):
        d.add(overlap)
    elif mode == "left":
        d.add(Circle(lx, cy, r, fillColor=LEFT_ONLY, strokeColor=NAVY, strokeWidth=1.2, fillOpacity=0.75))
        d.add(overlap)
    elif mode == "right":
        d.add(Circle(rx, cy, r, fillColor=RIGHT_ONLY, strokeColor=NAVY, strokeWidth=1.2, fillOpacity=0.75))
        d.add(overlap)

    _label(d, lx, cy + r + 10, "employees", size=6.5, color=NAVY)
    _label(d, rx, cy + r + 10, "departments", size=6.5, color=NAVY)
    _label(d, cx, cy - r - 8, title, size=7.5, bold=True, color=NAVY)


def join_venn_overview(width: float) -> Drawing:
    d = Drawing(width, 230)
    cell_w = width / 2
    specs = [
        (cell_w * 0.5, 165, "inner", "INNER JOIN"),
        (cell_w * 1.5, 165, "natural", "NATURAL JOIN"),
        (cell_w * 0.5, 55, "left", "LEFT OUTER JOIN"),
        (cell_w * 1.5, 55, "right", "RIGHT OUTER JOIN"),
    ]
    for cx, cy, mode, title in specs:
        _venn_pair(d, cx, cy, 34, mode, title)

    legend_y = 8
    for i, (label, fill) in enumerate([
        ("Matched rows", MATCH_FILL),
        ("Left table preserved", LEFT_ONLY),
        ("Right table preserved", RIGHT_ONLY),
    ]):
        lx = 12 + i * (width / 3.2)
        d.add(Rect(lx, legend_y, 10, 10, fillColor=fill, strokeColor=NAVY, strokeWidth=0.6))
        _label(d, lx + 14, legend_y + 2, label, size=6.5, color=GREY, anchor="start")

    _label(d, width / 2, 218, "Figure 2 — Join types as set operations (NATURAL ≡ INNER when deptID is the only common column)",
           size=7.5, color=GREY)
    return d


def data_mapping_diagram(width: float) -> Drawing:
    """Lines connect matching deptIDs; orphans highlighted."""
    d = Drawing(width, 210)
    dept_rows = [
        (1, "Eng & Tech"),
        (2, "Management"),
        (3, "Law"),
        (4, "Agriculture"),
        (5, "Medical"),
        (6, "Humanities"),
    ]
    emp_rows = [
        (1, "Ananya", 1),
        (2, "Rohan", 2),
        (3, "Priya", 3),
        (4, "Vikram", 4),
        (5, "Fatima", 1),
        (6, "Arjun", 5),
        (7, "Neha", 99),
    ]
    dept_ids = {did for did, _ in dept_rows}
    emp_dept_ids = {did for _, _, did in emp_rows}
    matched = dept_ids & emp_dept_ids
    orphan_emp = [e for e in emp_rows if e[2] not in dept_ids]
    orphan_dept = [r for r in dept_rows if r[0] not in emp_dept_ids]

    left_x, right_x = 8, width - 108
    box_w = 100
    top_y = 175
    row_h = 22

    _table_box(d, left_x, top_y - len(emp_rows) * row_h - 4, box_w,
               len(emp_rows) * row_h + 22, "employees",
               [f"{eid}. {name[:8]:<8} dept={did}" for eid, name, did in emp_rows])
    _table_box(d, right_x, top_y - len(dept_rows) * row_h - 4, box_w,
               len(dept_rows) * row_h + 22, "departments",
               [f"{did}. {name[:12]}" for did, name in dept_rows])

    def row_center(idx: int, count: int, base_y: float) -> float:
        return base_y - 14 - idx * row_h - row_h / 2

    emp_base = top_y - 4
    dept_base = top_y - 4
    for i, (_, _, did) in enumerate(emp_rows):
        if did not in dept_ids:
            continue
        dept_idx = next(j for j, (d_id, _) in enumerate(dept_rows) if d_id == did)
        y1 = row_center(i, len(emp_rows), emp_base)
        y2 = row_center(dept_idx, len(dept_rows), dept_base)
        d.add(Line(left_x + box_w, y1, right_x, y2, strokeColor=ACCENT, strokeWidth=0.8))

    for i, (_, _, did) in enumerate(emp_rows):
        if did not in dept_ids:
            y = row_center(i, len(emp_rows), emp_base)
            d.add(Rect(left_x + 2, y - 8, box_w - 4, 16, fillColor=ORPHAN, fillOpacity=0.45,
                       strokeColor=colors.HexColor("#C0392B"), strokeWidth=0.8, strokeDashArray=[3, 2]))
            _label(d, left_x + box_w + 14, y, "no match → LEFT JOIN keeps", size=6, color=colors.HexColor("#C0392B"), anchor="start")

    for j, (did, _) in enumerate(dept_rows):
        if did not in emp_dept_ids:
            y = row_center(j, len(dept_rows), dept_base)
            d.add(Rect(right_x + 2, y - 8, box_w - 4, 16, fillColor=RIGHT_ONLY, fillOpacity=0.55,
                       strokeColor=colors.HexColor("#27AE60"), strokeWidth=0.8, strokeDashArray=[3, 2]))
            _label(d, right_x - 8, y, "← RIGHT JOIN keeps", size=6, color=colors.HexColor("#27AE60"), anchor="end")

    _label(d, width / 2, 6, "Figure 3 — Row matching on deptID (solid = match, dashed = preserved by outer join)",
           size=7.5, color=GREY)
    return d


def join_result_snapshot(width: float) -> Drawing:
    """Mini result grids coloured by join outcome."""
    d = Drawing(width, 175)
    joins = [
        ("INNER / NATURAL", "6 rows", MATCH_FILL, "Only matched pairs"),
        ("LEFT OUTER", "7 rows", LEFT_ONLY, "+ Neha (NULL dept)"),
        ("RIGHT OUTER", "7 rows", RIGHT_ONLY, "+ Humanities (NULL emp)"),
    ]
    card_w = (width - 24) / 3
    for i, (name, count, fill, note) in enumerate(joins):
        x = 8 + i * (card_w + 4)
        d.add(Rect(x, 30, card_w, 120, fillColor=WHITE, strokeColor=NAVY, strokeWidth=1))
        d.add(Rect(x, 130, card_w, 20, fillColor=NAVY, strokeColor=NAVY, strokeWidth=0))
        _label(d, x + card_w / 2, 137, name, size=7, bold=True, color=WHITE)
        d.add(Rect(x + 10, 78, card_w - 20, 42, fillColor=fill, strokeColor=ACCENT, strokeWidth=0.8, fillOpacity=0.7))
        _label(d, x + card_w / 2, 96, count, size=16, bold=True, color=NAVY)
        _label(d, x + card_w / 2, 52, note, size=6.5, color=GREY)

    _label(d, width / 2, 12, "Figure 4 — Result set sizes from this lab dataset",
           size=7.5, color=GREY)
    return d


def figure(drawing: Drawing, caption: str | None = None) -> list:
    items: list = [Spacer(1, 0.2 * cm), DrawingFlowable(drawing), Spacer(1, 0.15 * cm)]
    if caption:
        cap_style = ParagraphStyle(
            "fig_cap", parent=S["body"], fontSize=8, alignment=TA_CENTER,
            textColor=GREY, spaceAfter=6,
        )
        items.append(Paragraph(caption, cap_style))
    return items


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
        "SQL Joins — NATURAL, INNER, and OUTER",
        "NATURAL JOIN, INNER JOIN, LEFT OUTER JOIN, RIGHT OUTER JOIN",
        "departments (6 rows) + employees (7 rows) linked by deptID",
        LAB_DATE,
    )

    st.append(heading("1. Aim"))
    st.append(para(
        "To combine rows from two related tables — "
        "<font face='Courier'>departments</font> and "
        "<font face='Courier'>employees</font> — using "
        "<font face='Courier'>NATURAL JOIN</font>, "
        "<font face='Courier'>INNER JOIN</font>, "
        "<font face='Courier'>LEFT OUTER JOIN</font>, and "
        "<font face='Courier'>RIGHT OUTER JOIN</font>, and to observe how "
        "each join type handles unmatched rows."
    ))

    st.append(heading("2. Theory"))
    st.append(sub("2.1 NATURAL JOIN"))
    st.append(para(
        "A <font face='Courier'>NATURAL JOIN</font> automatically matches rows "
        "on every column that appears in both tables with the same name. Here, "
        "both tables share <font face='Courier'>deptID</font>, so the join "
        "condition is implicit. Only rows with a matching "
        "<font face='Courier'>deptID</font> in both tables are returned."
    ))
    st.append(sub("2.2 INNER JOIN"))
    st.append(para(
        "An <font face='Courier'>INNER JOIN</font> returns only the rows where "
        "the join condition is satisfied. "
        "<font face='Courier'>INNER JOIN departments ON employees.deptID = "
        "departments.deptID</font> produces the same result as "
        "<font face='Courier'>NATURAL JOIN</font> when "
        "<font face='Courier'>deptID</font> is the sole common column."
    ))
    st.append(sub("2.3 LEFT OUTER JOIN"))
    st.append(para(
        "A <font face='Courier'>LEFT OUTER JOIN</font> keeps every row from the "
        "left table. If no match exists in the right table, the right-hand "
        "columns are filled with <font face='Courier'>NULL</font>. Employee "
        "<font face='Courier'>Neha Gupta</font> (deptID 99) has no matching "
        "department and therefore appears with a null department name."
    ))
    st.append(sub("2.4 RIGHT OUTER JOIN"))
    st.append(para(
        "A <font face='Courier'>RIGHT OUTER JOIN</font> keeps every row from the "
        "right table. Unmatched left-hand columns become "
        "<font face='Courier'>NULL</font>. "
        "<font face='Courier'>School of Humanities</font> (deptID 6) has no "
        "employees and therefore appears with null employee fields."
    ))
    st.extend(figure(join_venn_overview(CONTENT_W)))

    st.append(heading("3. Schema"))
    st.append(para(
        "Two tables share the column <font face='Courier'>deptID</font>. "
        "The diagram below shows how they relate before any join is applied."
    ))
    st.extend(figure(schema_er_diagram(CONTENT_W)))
    st.append(table(
        [
            ["Table", "Attribute", "Type", "Role"],
            ["departments", "deptID", "INTEGER / INT", "Primary key"],
            ["departments", "deptName", "TEXT / VARCHAR", "School name"],
            ["employees", "empID", "INTEGER / INT", "Primary key"],
            ["employees", "empName", "TEXT / VARCHAR", "Employee name"],
            ["employees", "deptID", "INTEGER / INT", "Join key → departments"],
            ["employees", "salary", "NUMERIC(10,2)", "Monthly salary"],
        ],
        col_widths=[CONTENT_W * 0.18, CONTENT_W * 0.22, CONTENT_W * 0.22, CONTENT_W * 0.28],
        pad=4,
    ))

    st.append(heading("4. Procedure"))
    st.append(para("1. Create <font face='Courier'>departments</font> and <font face='Courier'>employees</font> with a shared <font face='Courier'>deptID</font> column."))
    st.append(para("2. Insert six departments and seven employees, including deliberate mismatches for outer joins."))
    st.append(para("3. Display both base tables."))
    st.append(para("4. Run <font face='Courier'>NATURAL JOIN</font> and <font face='Courier'>INNER JOIN</font> — expect six matched rows."))
    st.append(para("5. Run <font face='Courier'>LEFT OUTER JOIN</font> — expect seven rows (one employee without a department)."))
    st.append(para("6. Run <font face='Courier'>RIGHT OUTER JOIN</font> — expect seven rows (one department without employees)."))
    st.extend(figure(data_mapping_diagram(CONTENT_W)))

    st.append(heading("5. Source Code"))
    st.append(code_block(sql_text, size=6.4, leading=8.0))

    st.append(heading("6. Output"))
    st.append(para(
        "The script was executed in SQLite. Each query's result set is shown "
        "below in execution order."
    ))
    st.append(code_block(output, size=6.2, leading=7.8))

    st.append(heading("7. Results"))
    st.extend(figure(join_result_snapshot(CONTENT_W)))
    st.append(table(
        [
            ["Join type", "Rows returned", "Unmatched handling"],
            ["NATURAL JOIN", "6", "Drops non-matching rows from both sides"],
            ["INNER JOIN", "6", "Same as NATURAL JOIN here"],
            ["LEFT OUTER JOIN", "7", "Keeps Neha Gupta (deptID 99); deptName is NULL"],
            ["RIGHT OUTER JOIN", "7", "Keeps Humanities (deptID 6); employee cols are NULL"],
        ],
        col_widths=[CONTENT_W * 0.24, CONTENT_W * 0.18, CONTENT_W * 0.48],
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "<font face='Courier'>INNER JOIN</font> and "
        "<font face='Courier'>NATURAL JOIN</font> return only the six employees "
        "whose <font face='Courier'>deptID</font> exists in "
        "<font face='Courier'>departments</font>. "
        "<font face='Courier'>LEFT OUTER JOIN</font> adds the orphan employee; "
        "<font face='Courier'>RIGHT OUTER JOIN</font> adds the department with "
        "no staff. Together they illustrate how outer joins preserve rows that "
        "inner joins would discard."
    ))

    st.append(heading("8. Conclusion"))
    st.append(para(
        "Joins combine related tables on a common key. "
        "<font face='Courier'>INNER JOIN</font> and "
        "<font face='Courier'>NATURAL JOIN</font> return only matching pairs. "
        "Outer joins extend one side: "
        "<font face='Courier'>LEFT OUTER JOIN</font> keeps all employees, "
        "<font face='Courier'>RIGHT OUTER JOIN</font> keeps all departments. "
        "Choosing the correct join depends on whether unmatched rows from the "
        "left, right, or neither side must appear in the result."
    ))

    write_report(
        OUT_PDF,
        "DBMS Lab · 02-09-2026 · SQL Joins · Harshit Khemani",
        st,
    )
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
