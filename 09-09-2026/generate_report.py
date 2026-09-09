"""
DBMS Lab — 09-09-2026
=====================

Builds `DBMS_Lab_Employee_Select_Report.pdf` from `employee.sql` (SQLite).

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
SQL_PATH = ROOT / "employee.sql"
OUT_PDF = ROOT / "DBMS_Lab_Employee_Select_Report.pdf"

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

LAB_DATE = "09 September 2026"


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


def build_story(*, include_cover: bool = True) -> list:
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    output = run_sql(sql_text)

    st: list = []
    if include_cover:
        cover(
            st, "4",
            "SELECT Queries — DISTINCT, WHERE, BETWEEN, IN, ORDER BY",
            "SELECT, DISTINCT, WHERE, BETWEEN, IN, ORDER BY",
            "employee — 10 sample rows × 8 attributes",
            LAB_DATE,
        )

    st.append(heading("1. Aim"))
    st.append(para(
        "To create an <font face='Courier'>employee</font> table, insert ten sample "
        "records, and retrieve data with <font face='Courier'>SELECT</font> using "
        "<font face='Courier'>DISTINCT</font>, <font face='Courier'>WHERE</font> "
        "(comparison, <font face='Courier'>OR</font>, <font face='Courier'>BETWEEN</font>, "
        "<font face='Courier'>IN</font> / <font face='Courier'>NOT IN</font>), and "
        "<font face='Courier'>ORDER BY</font> in ascending and descending order."
    ))

    st.append(heading("2. Theory"))
    st.append(sub("2.1 SELECT"))
    st.append(para(
        "<font face='Courier'>SELECT</font> reads rows from a relation. "
        "<font face='Courier'>SELECT *</font> returns every column; naming columns "
        "returns only those attributes. A query without a "
        "<font face='Courier'>WHERE</font> clause returns every row that currently "
        "exists in the table."
    ))
    st.append(sub("2.2 DISTINCT"))
    st.append(para(
        "<font face='Courier'>SELECT DISTINCT</font> removes duplicate values from "
        "the result. <font face='Courier'>SELECT department_no</font> lists a "
        "department once per employee; "
        "<font face='Courier'>SELECT DISTINCT department_no</font> lists each "
        "department number only once. Use <font face='Courier'>DISTINCT</font> when "
        "the question is about unique values, not about every row."
    ))
    st.append(sub("2.3 WHERE"))
    st.append(para(
        "The <font face='Courier'>WHERE</font> clause keeps rows that satisfy a "
        "condition. Comparison operators such as <font face='Courier'>&gt;</font> "
        "and <font face='Courier'>&lt;&gt;</font> filter numbers and strings. "
        "<font face='Courier'>OR</font> keeps a row if either predicate is true "
        "(city is Delhi or Mumbai). City values in this lab are stored in title "
        "case and matched with the same casing so the filters work in SQLite "
        "without extra case-conversion functions."
    ))
    st.append(sub("2.4 BETWEEN"))
    st.append(para(
        "<font face='Courier'>BETWEEN low AND high</font> is an inclusive range: "
        "the endpoints are part of the result. "
        "<font face='Courier'>NOT BETWEEN</font> is the complement — salaries "
        "strictly below 30000 or strictly above 50000. It is equivalent to "
        "<font face='Courier'>salary &lt; 30000 OR salary &gt; 50000</font> when "
        "the range is 30000 to 50000."
    ))
    st.append(sub("2.5 IN"))
    st.append(para(
        "<font face='Courier'>IN (…)</font> tests membership in a list. "
        "<font face='Courier'>city IN ('Delhi', 'Mumbai', 'Chennai', 'Bangalore')</font> "
        "keeps those four cities. <font face='Courier'>NOT IN</font> keeps every "
        "city that is not in the list — here Bangalore, Hyderabad, and Pune remain "
        "when Mumbai, Delhi, and Chennai are excluded."
    ))
    st.append(sub("2.6 ORDER BY"))
    st.append(para(
        "<font face='Courier'>ORDER BY</font> sorts the result. "
        "<font face='Courier'>ASC</font> (the default) lists names A→Z; "
        "<font face='Courier'>DESC</font> lists them Z→A. Sorting does not change "
        "stored rows; it only changes the order of the result set."
    ))

    st.append(heading("3. Schema"))
    st.append(para(
        "One table, <font face='Courier'>employee</font>, holds eight attributes. "
        "<font face='Courier'>sr_no</font> is the employee number (primary key). "
        "<font face='Courier'>manager</font> stores the manager's name, or "
        "<font face='Courier'>NULL</font> for the top manager."
    ))
    st.append(table(
        [
            ["Attribute", "Type", "Constraint", "Role"],
            ["sr_no", "INTEGER", "PRIMARY KEY", "Employee number"],
            ["employee_name", "TEXT", "NOT NULL", "Employee name"],
            ["job", "TEXT", "NOT NULL", "Job title"],
            ["manager", "TEXT", "NULL allowed", "Manager name"],
            ["hire_date", "DATE", "NOT NULL", "Date of joining"],
            ["salary", "NUMERIC(10,2)", "NOT NULL, CHECK &gt; 0", "Monthly salary"],
            ["department_no", "INTEGER", "NOT NULL", "Department number"],
            ["city", "TEXT", "NOT NULL", "Work city"],
        ],
        col_widths=[CONTENT_W * 0.22, CONTENT_W * 0.20, CONTENT_W * 0.24, CONTENT_W * 0.24],
        pad=4,
    ))

    st.append(heading("4. Procedure"))
    st.append(para("1. Drop <font face='Courier'>employee</font> if it already exists, so the script can be re-run."))
    st.append(para("2. Create the table with the eight attributes listed above."))
    st.append(para("3. Insert ten employees with mixed salaries, cities, and department numbers."))
    st.append(para("4. Select all columns from <font face='Courier'>employee</font>."))
    st.append(para("5. Select distinct department numbers, then all department numbers without <font face='Courier'>DISTINCT</font>."))
    st.append(para("6. Filter by salary (&gt; 30000, <font face='Courier'>BETWEEN</font>, <font face='Courier'>NOT BETWEEN</font>)."))
    st.append(para("7. Filter by city (not Delhi, Delhi or Mumbai, <font face='Courier'>IN</font>, <font face='Courier'>NOT IN</font>)."))
    st.append(para("8. Sort the full table by employee name descending, then ascending."))

    st.append(heading("5. Source Code"))
    st.append(para(
        "SQLite script used in the lab compiler "
        "(<font face='Courier'>09-09-2026/employee.sql</font>). "
        "For the class SQL Server, run <font face='Courier'>employee.sqlserver.sql</font>."
    ))
    st.append(code_block(sql_text, size=6.4, leading=7.8))

    st.append(heading("6. Output"))
    st.append(para(
        "The script was executed in SQLite in memory. "
        "<font face='Courier'>CREATE</font> and <font face='Courier'>INSERT</font> "
        "print a status line; each <font face='Courier'>SELECT</font> prints its "
        "result set. <font face='Courier'>NULL</font> in the manager column is "
        "shown as an empty cell."
    ))
    st.append(code_block(output, size=5.6, leading=6.9))

    st.append(heading("7. Results"))
    st.append(para(
        "Ten employees load successfully. The filters return non-empty, distinct "
        "subsets as expected for this seed data:"
    ))
    st.append(table(
        [
            ["Query", "Rows", "What the result shows"],
            ["SELECT *", "10", "Every employee and every column"],
            ["DISTINCT department_no", "6", "Departments 10, 20, 30, 40, 50, 60"],
            ["department_no (no DISTINCT)", "10", "Duplicates kept (dept 20 appears three times)"],
            ["salary &gt; 30000", "7", "Excludes 18000, 22000, 28000"],
            ["city &lt;&gt; Delhi", "8", "Keeps everyone except Rajesh and Neha"],
            ["city Delhi OR Mumbai", "4", "Rajesh, Rohan, Neha, Karan"],
            ["salary BETWEEN 30000 AND 50000", "5", "Inclusive range; excludes low and high pay"],
            ["salary NOT BETWEEN 30000 AND 50000", "5", "Complement of the BETWEEN query"],
            ["city IN (four metros)", "8", "Drops Hyderabad and Pune"],
            ["city NOT IN (Mumbai, Delhi, Chennai)", "4", "Bangalore, Hyderabad, Pune remain"],
            ["ORDER BY name DESC / ASC", "10", "Same ten rows; opposite sort orders"],
        ],
        col_widths=[CONTENT_W * 0.36, CONTENT_W * 0.10, CONTENT_W * 0.44],
        pad=4,
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "<font face='Courier'>DISTINCT</font> collapses ten department values to "
        "six unique numbers. <font face='Courier'>BETWEEN</font> and "
        "<font face='Courier'>NOT BETWEEN</font> partition the table with no overlap "
        "(5 + 5 = 10). City membership tests leave Hyderabad and Pune only in the "
        "<font face='Courier'>NOT IN</font> result, which is the check that the "
        "seed data includes cities outside the four-metro list."
    ))

    st.append(heading("8. Conclusion"))
    st.append(para(
        "A single <font face='Courier'>SELECT</font> can project columns, remove "
        "duplicates, filter with comparison and set predicates, and sort the "
        "result. <font face='Courier'>DISTINCT</font> answers &ldquo;which unique "
        "values exist?&rdquo; <font face='Courier'>WHERE</font> answers "
        "&ldquo;which rows match this condition?&rdquo; "
        "<font face='Courier'>BETWEEN</font> and <font face='Courier'>IN</font> "
        "express ranges and lists clearly. <font face='Courier'>ORDER BY</font> "
        "changes presentation only. Together these clauses are the core of "
        "everyday retrieval in SQL."
    ))
    return st


def build() -> None:
    st = build_story(include_cover=True)
    write_report(
        OUT_PDF,
        f"DBMS Lab · 09-09-2026 · SELECT Queries · {STUDENT['name']}",
        st,
    )
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
