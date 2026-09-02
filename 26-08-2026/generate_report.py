"""
DBMS Lab — 26-08-2026
=====================

Builds `DBMS_Lab_Employees_Report.pdf` from `employees.sql` (SQLite).

Run
---
    python generate_report.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
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
SQL_PATH = ROOT / "employees.sql"
OUT_PDF = ROOT / "DBMS_Lab_Employees_Report.pdf"

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

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

LAB_DATE = "26 August 2026"


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
        st, "2",
        "CREATE TABLE and ALTER TABLE (Rename Column)",
        "CREATE TABLE, ALTER TABLE ... RENAME COLUMN",
        "Employees — 6 sample rows × 4 attributes",
        LAB_DATE,
    )

    st.append(heading("1. Aim"))
    st.append(para(
        "To create an <font face='Courier'>employees</font> table with attributes "
        "<font face='Courier'>empID</font>, <font face='Courier'>empName</font>, "
        "<font face='Courier'>department</font> and <font face='Courier'>salary</font>, "
        "insert sample records, and then rename the column "
        "<font face='Courier'>department</font> to <font face='Courier'>faculty</font> "
        "using <font face='Courier'>ALTER TABLE</font>."
    ))

    st.append(heading("2. Theory"))
    st.append(sub("2.1 CREATE TABLE"))
    st.append(para(
        "A relational table is defined by a name, a list of attributes, and "
        "constraints that protect the data. <font face='Courier'>PRIMARY KEY</font> "
        "makes <font face='Courier'>empID</font> unique and not null. "
        "<font face='Courier'>NOT NULL</font> rejects missing names and faculty "
        "values. <font face='Courier'>CHECK (salary &gt; 0)</font> rejects "
        "non-positive salaries. <font face='Courier'>NUMERIC(10, 2)</font> stores "
        "pay as a decimal with two fractional digits."
    ))
    st.append(sub("2.2 ALTER TABLE RENAME COLUMN"))
    st.append(para(
        "In SQLite and MySQL 8+, "
        "<font face='Courier'>ALTER TABLE ... RENAME COLUMN</font> changes a "
        "column's name without rewriting the stored values. After "
        "<font face='Courier'>RENAME COLUMN department TO faculty</font>, every "
        "row still holds the same school name; only the heading of that column "
        "becomes <font face='Courier'>faculty</font>. This is a schema change, "
        "not an <font face='Courier'>UPDATE</font>. Microsoft SQL Server does not "
        "accept that syntax; the equivalent is "
        "<font face='Courier'>EXEC sp_rename 'employees.department', 'faculty', "
        "'COLUMN'</font> (see <font face='Courier'>employees.sqlserver.sql</font>)."
    ))

    st.append(heading("3. Schema"))
    st.append(para(
        "The table is created with four attributes. After the rename, the third "
        "attribute is <font face='Courier'>faculty</font> instead of "
        "<font face='Courier'>department</font>."
    ))
    st.append(table(
        [
            ["Attribute", "Type", "Constraint", "Role"],
            ["empID", "INTEGER", "PRIMARY KEY", "Employee identifier"],
            ["empName", "TEXT", "NOT NULL", "Employee name"],
            ["department → faculty", "TEXT", "NOT NULL", "School / faculty name"],
            ["salary", "NUMERIC(10,2)", "NOT NULL, CHECK &gt; 0", "Monthly salary"],
        ],
        col_widths=[CONTENT_W * 0.28, CONTENT_W * 0.18, CONTENT_W * 0.22, CONTENT_W * 0.22],
        pad=4,
    ))
    st.append(Spacer(1, 0.25 * cm))
    st.append(para(
        "Sample faculty values include <b>School of Engineering and Technology</b> "
        "(the faculty named on this report's cover). The cover also lists "
        "<b>Department of CSE</b> as the student's home department; that heading "
        "is letterhead, not a fifth column in the table."
    ))

    st.append(heading("4. Procedure"))
    st.append(para("1. Drop <font face='Courier'>employees</font> if it already exists, so the script can be re-run."))
    st.append(para("2. Create the table with <font face='Courier'>empID</font>, <font face='Courier'>empName</font>, <font face='Courier'>department</font> and <font face='Courier'>salary</font>."))
    st.append(para("3. Insert six sample employees."))
    st.append(para("4. Display all rows and the column list with <font face='Courier'>PRAGMA table_info</font>."))
    st.append(para("5. Rename <font face='Courier'>department</font> to <font face='Courier'>faculty</font>."))
    st.append(para("6. Display all rows and the column list again to confirm that only the name changed."))

    st.append(heading("5. Source Code"))
    st.append(code_block(sql_text, size=6.6, leading=8.2))

    st.append(heading("6. Output"))
    st.append(para(
        "The script was executed in SQLite. "
        "<font face='Courier'>PRAGMA table_info</font> columns are "
        "<font face='Courier'>cid</font> (column index), "
        "<font face='Courier'>name</font>, <font face='Courier'>type</font>, "
        "<font face='Courier'>notnull</font>, <font face='Courier'>dflt_value</font> "
        "and <font face='Courier'>pk</font>."
    ))
    st.append(code_block(output, size=6.4, leading=8.0))

    st.append(heading("7. Results"))
    st.append(table(
        [
            ["Stage", "Third column", "Row count", "Values changed?"],
            ["Before ALTER", "department", "6", "No — original schema"],
            ["After ALTER", "faculty", "6", "No — names only"],
        ],
        col_widths=[CONTENT_W * 0.22, CONTENT_W * 0.22, CONTENT_W * 0.18, CONTENT_W * 0.28],
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "All six employees remain. School names such as School of Engineering "
        "and Technology are unchanged. The schema listing is the proof: "
        "<font face='Courier'>cid = 2</font> is named "
        "<font face='Courier'>department</font> before the statement and "
        "<font face='Courier'>faculty</font> afterwards."
    ))

    st.append(heading("8. Conclusion"))
    st.append(para(
        "An employees relation can be created with a primary key, not-null "
        "attributes and a salary check, then adjusted with "
        "<font face='Courier'>ALTER TABLE ... RENAME COLUMN</font>. Renaming "
        "<font face='Courier'>department</font> to <font face='Courier'>faculty</font> "
        "updates the schema only. The stored values do not change, which is the "
        "correct way to relabel an attribute without rewriting the table."
    ))

    write_report(
        OUT_PDF,
        "DBMS Lab · 26-08-2026 · Employees Table · Harshit Khemani",
        st,
    )
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
