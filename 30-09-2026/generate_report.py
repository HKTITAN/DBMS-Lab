"""
DBMS Lab — 30-09-2026
=====================

Builds `DBMS_Lab_Aggregates_Report.pdf` from `employee.sql` (SQLite).

Run
---
    python generate_report.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
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
OUT_PDF = ROOT / "DBMS_Lab_Aggregates_Report.pdf"

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

LAB_DATE = "30 September 2026"

EMPLOYEE_ATTRIBUTES = [
    "sr no",
    "employee name",
    "job",
    "department",
    "salary",
    "city",
]


def sql_kw(word: str) -> str:
    """Courier SQL keyword for question text (word is a trusted literal)."""
    return f"<font face='Courier'>{word}</font>"


QUESTIONS = [
    {
        "num": "1",
        "html": (
            f"Create a table {sql_kw('employee')} with the following attributes:"
        ),
        "subitems": EMPLOYEE_ATTRIBUTES,
    },
    {
        "num": "2",
        "html": "Insert 16 rows in the above mentioned table.",
        "note": (
            "Four departments: CSE (5), Mechanical (4), ECE (4) and Civil (3). "
            "Salaries are spread so each aggregate and each "
            f"{sql_kw('HAVING')} filter returns a different set. "
            "Five cities have two employees; the other cities have one."
        ),
    },
    {
        "num": "3",
        "html": (
            "Display the total number of employees from the employee table "
            f"using {sql_kw('COUNT')}."
        ),
    },
    {
        "num": "4",
        "html": (
            "Display the number of distinct departments from the employee table "
            f"using {sql_kw('COUNT')}."
        ),
    },
    {
        "num": "5",
        "html": (
            "Display the total salary of all employees from the employee table "
            f"using {sql_kw('SUM')}."
        ),
    },
    {
        "num": "6",
        "html": (
            "Display the average salary of all employees from the employee table "
            f"using {sql_kw('AVG')}."
        ),
    },
    {
        "num": "7",
        "html": (
            "Display the maximum and minimum salary from the employee table "
            f"using {sql_kw('MAX')} and {sql_kw('MIN')}."
        ),
    },
    {
        "num": "8",
        "html": (
            "Display the number of employees, total salary, average salary, "
            "highest salary and lowest salary of each department using "
            f"{sql_kw('COUNT')}, {sql_kw('SUM')}, {sql_kw('AVG')}, "
            f"{sql_kw('MAX')}, {sql_kw('MIN')} and {sql_kw('GROUP BY')}."
        ),
    },
    {
        "num": "9",
        "html": (
            "Display the department and average salary of departments whose "
            "average salary is greater than 55000 using "
            f"{sql_kw('GROUP BY')} and {sql_kw('HAVING')}."
        ),
    },
    {
        "num": "10",
        "html": (
            "Display the department and the number of employees for departments "
            "that have more than 3 employees using "
            f"{sql_kw('GROUP BY')} and {sql_kw('HAVING')}."
        ),
    },
    {
        "num": "11",
        "html": (
            "Display the number of employees, total salary and average salary "
            f"of the CSE department using {sql_kw('WHERE')} with "
            f"{sql_kw('COUNT')}, {sql_kw('SUM')} and {sql_kw('AVG')}."
        ),
    },
    {
        "num": "12",
        "html": (
            "Display the cities that have more than one employee using "
            f"{sql_kw('GROUP BY')} and {sql_kw('HAVING')}."
        ),
    },
]

SQL_SOLUTIONS = [
    (
        "1",
        "CREATE TABLE employee (\n"
        "    sr_no INTEGER PRIMARY KEY,\n"
        "    employee_name TEXT NOT NULL,\n"
        "    job TEXT NOT NULL,\n"
        "    department TEXT NOT NULL,\n"
        "    salary NUMERIC(10, 2) NOT NULL CHECK (salary > 0),\n"
        "    city TEXT NOT NULL\n"
        ");",
    ),
    (
        "2",
        "INSERT INTO employee\n"
        "    (sr_no, employee_name, job, department, salary, city)\n"
        "VALUES\n"
        "    (1,  'Rajesh Kumar',  'Professor',           'CSE',        92000.00, 'Delhi'),\n"
        "    (2,  'Ananya Sharma', 'Associate Professor', 'CSE',        78000.00, 'Bangalore'),\n"
        "    (3,  'Fatima Khan',   'Assistant Professor', 'CSE',        56000.00, 'Bangalore'),\n"
        "    (4,  'Karan Iyer',    'Lab Instructor',      'CSE',        42000.00, 'Mumbai'),\n"
        "    (5,  'Dev Patel',     'Teaching Assistant',  'CSE',        28000.00, 'Ahmedabad'),\n"
        "    (6,  'Vikram Singh',  'Professor',           'Mechanical', 88000.00, 'Hyderabad'),\n"
        "    (7,  'Rohan Mehta',   'Associate Professor', 'Mechanical', 64000.00, 'Mumbai'),\n"
        "    (8,  'Arjun Patel',   'Assistant Professor', 'Mechanical', 48000.00, 'Pune'),\n"
        "    (9,  'Mohit Jain',    'Lab Instructor',      'Mechanical', 32000.00, 'Jaipur'),\n"
        "    (10, 'Priya Nair',    'Professor',           'ECE',        90000.00, 'Chennai'),\n"
        "    (11, 'Neha Gupta',    'Associate Professor', 'ECE',        58000.00, 'Delhi'),\n"
        "    (12, 'Meera Joshi',   'Assistant Professor', 'ECE',        51000.00, 'Chennai'),\n"
        "    (13, 'Kavya Menon',   'Lab Instructor',      'ECE',        36000.00, 'Kochi'),\n"
        "    (14, 'Sneha Reddy',   'Associate Professor', 'Civil',      60000.00, 'Hyderabad'),\n"
        "    (15, 'Rahul Das',     'Assistant Professor', 'Civil',      45000.00, 'Kolkata'),\n"
        "    (16, 'Tushar Rao',    'Lab Instructor',      'Civil',      30000.00, 'Nagpur');",
    ),
    ("3", "SELECT COUNT(*) AS employee_count\nFROM employee;"),
    ("4", "SELECT COUNT(DISTINCT department) AS department_count\nFROM employee;"),
    ("5", "SELECT SUM(salary) AS total_salary\nFROM employee;"),
    ("6", "SELECT AVG(salary) AS average_salary\nFROM employee;"),
    (
        "7",
        "SELECT MAX(salary) AS maximum_salary,\n"
        "       MIN(salary) AS minimum_salary\n"
        "FROM employee;",
    ),
    (
        "8",
        "SELECT department,\n"
        "       COUNT(*)    AS employee_count,\n"
        "       SUM(salary) AS total_salary,\n"
        "       AVG(salary) AS average_salary,\n"
        "       MAX(salary) AS highest_salary,\n"
        "       MIN(salary) AS lowest_salary\n"
        "FROM employee\n"
        "GROUP BY department\n"
        "ORDER BY department;",
    ),
    (
        "9",
        "SELECT department,\n"
        "       AVG(salary) AS average_salary\n"
        "FROM employee\n"
        "GROUP BY department\n"
        "HAVING AVG(salary) > 55000\n"
        "ORDER BY department;",
    ),
    (
        "10",
        "SELECT department,\n"
        "       COUNT(*) AS employee_count\n"
        "FROM employee\n"
        "GROUP BY department\n"
        "HAVING COUNT(*) > 3\n"
        "ORDER BY department;",
    ),
    (
        "11",
        "SELECT COUNT(*)    AS employee_count,\n"
        "       SUM(salary) AS total_salary,\n"
        "       AVG(salary) AS average_salary\n"
        "FROM employee\n"
        "WHERE department = 'CSE';",
    ),
    (
        "12",
        "SELECT city,\n"
        "       COUNT(*) AS employee_count\n"
        "FROM employee\n"
        "GROUP BY city\n"
        "HAVING COUNT(*) > 1\n"
        "ORDER BY city;",
    ),
]


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


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


def assert_results(conn: sqlite3.Connection) -> None:
    """Fail the build if the captured output would not match the written results."""
    one = lambda sql: conn.execute(sql).fetchone()
    all_rows = lambda sql: conn.execute(sql).fetchall()

    count, total, average, maximum, minimum = one(
        "SELECT COUNT(*), SUM(salary), AVG(salary), MAX(salary), MIN(salary) FROM employee"
    )
    if (count, total, average, maximum, minimum) != (16, 898000, 56125.0, 92000, 28000):
        raise AssertionError(
            f"overall aggregates changed: {(count, total, average, maximum, minimum)}"
        )
    if one("SELECT COUNT(DISTINCT department) FROM employee") != (4,):
        raise AssertionError("distinct department count changed")

    by_dept = all_rows(
        "SELECT department, COUNT(*), SUM(salary), AVG(salary), MAX(salary), MIN(salary) "
        "FROM employee GROUP BY department ORDER BY department"
    )
    expected_dept = [
        ("CSE", 5, 296000, 59200.0, 92000, 28000),
        ("Civil", 3, 135000, 45000.0, 60000, 30000),
        ("ECE", 4, 235000, 58750.0, 90000, 36000),
        ("Mechanical", 4, 232000, 58000.0, 88000, 32000),
    ]
    if by_dept != expected_dept:
        raise AssertionError(f"department aggregates changed: {by_dept}")

    having_avg = all_rows(
        "SELECT department, AVG(salary) FROM employee GROUP BY department "
        "HAVING AVG(salary) > 55000 ORDER BY department"
    )
    if having_avg != [("CSE", 59200.0), ("ECE", 58750.0), ("Mechanical", 58000.0)]:
        raise AssertionError(f"HAVING average changed: {having_avg}")

    having_count = all_rows(
        "SELECT department, COUNT(*) FROM employee GROUP BY department "
        "HAVING COUNT(*) > 3 ORDER BY department"
    )
    if having_count != [("CSE", 5), ("ECE", 4), ("Mechanical", 4)]:
        raise AssertionError(f"HAVING count changed: {having_count}")

    cse = one(
        "SELECT COUNT(*), SUM(salary), AVG(salary) FROM employee WHERE department = 'CSE'"
    )
    if cse != (5, 296000, 59200.0):
        raise AssertionError(f"CSE aggregates changed: {cse}")

    cities = all_rows(
        "SELECT city, COUNT(*) FROM employee GROUP BY city "
        "HAVING COUNT(*) > 1 ORDER BY city"
    )
    if cities != [
        ("Bangalore", 2), ("Chennai", 2), ("Delhi", 2), ("Hyderabad", 2), ("Mumbai", 2),
    ]:
        raise AssertionError(f"city counts changed: {cities}")


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
                    n = cur.rowcount if cur.rowcount is not None and cur.rowcount >= 0 else conn.total_changes
                    chunks.append(f"-- {n} row(s) inserted")
                else:
                    chunks.append("-- OK")
                chunks.append("")
        assert_results(conn)
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
    "sqlcell": ParagraphStyle(
        "sqlcell", parent=_base["Normal"], fontName="Courier", fontSize=6.5, leading=8.2,
        textColor=colors.HexColor("#111111"),
    ),
    "qcell": ParagraphStyle(
        "qcell", parent=_base["Normal"], fontName="Helvetica", fontSize=8.5, leading=11.5,
    ),
    "qnum": ParagraphStyle(
        "qnum", parent=_base["Normal"], fontName="Helvetica-Bold", fontSize=9.5,
        leading=13.5, alignment=TA_LEFT, textColor=NAVY,
    ),
    "qtext": ParagraphStyle(
        "qtext", parent=_base["Normal"], fontName="Helvetica", fontSize=9.5,
        leading=13.5, alignment=TA_LEFT, textColor=colors.HexColor("#1A1A1A"),
    ),
    "qsub": ParagraphStyle(
        "qsub", parent=_base["Normal"], fontName="Helvetica", fontSize=9,
        leading=12.5, leftIndent=14, alignment=TA_LEFT,
        textColor=colors.HexColor("#1A1A1A"),
    ),
    "qnote": ParagraphStyle(
        "qnote", parent=_base["Normal"], fontName="Helvetica-Oblique", fontSize=8.5,
        leading=11.5, alignment=TA_LEFT, textColor=GREY, spaceBefore=2,
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


def questions_flow() -> list:
    """Numbered lab-sheet list: wrapping questions, indented attributes on 1."""
    num_w = 1.55 * cm
    text_w = CONTENT_W - num_w
    flow: list = []
    for q in QUESTIONS:
        body = [Paragraph(q["html"], S["qtext"])]
        for attr in q.get("subitems") or []:
            body.append(Paragraph(f"&ndash;&nbsp;&nbsp;{_esc(attr)}", S["qsub"]))
        if q.get("note"):
            body.append(Paragraph(q["note"], S["qnote"]))
        row = Table(
            [[Paragraph(_esc(q["num"]) + ".", S["qnum"]), body]],
            colWidths=[num_w, text_w],
        )
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 6),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        flow.append(row)
    return flow


def solutions_table():
    header = [
        Paragraph("Q. No.", S["cellb"]),
        Paragraph("SQL solution", S["cellb"]),
    ]
    data = [header]
    for num, sql in SQL_SOLUTIONS:
        data.append([
            Paragraph(num, S["qcell"]),
            Paragraph(_esc(sql).replace("\n", "<br/>"), S["sqlcell"]),
        ])
    t = Table(data, colWidths=[CONTENT_W * 0.14, CONTENT_W * 0.86], hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]))
    return t


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
            st, "5",
            "Aggregate Functions",
            "SUM, AVG, MAX, MIN, COUNT, GROUP BY, HAVING",
            "employee (16 rows; CSE, Mechanical, ECE, Civil)",
            LAB_DATE,
        )

    st.append(heading("1. Aim"))
    st.append(para(
        "To create an <font face='Courier'>employee</font> table, insert 16 rows "
        "across four departments, and answer the lab questions with aggregate "
        "functions: <font face='Courier'>COUNT</font>, <font face='Courier'>SUM</font>, "
        "<font face='Courier'>AVG</font>, <font face='Courier'>MAX</font> and "
        "<font face='Courier'>MIN</font>, including <font face='Courier'>GROUP BY</font> "
        "and <font face='Courier'>HAVING</font>."
    ))

    st.append(heading("2. Theory"))
    st.append(sub("2.1 Aggregate functions"))
    st.append(para(
        "An aggregate function computes one value from many rows. "
        "<font face='Courier'>COUNT(*)</font> counts rows. "
        "<font face='Courier'>SUM(salary)</font> adds the salary column. "
        "<font face='Courier'>AVG(salary)</font> is the arithmetic mean. "
        "<font face='Courier'>MAX</font> and <font face='Courier'>MIN</font> return "
        "the largest and smallest values. Without <font face='Courier'>GROUP BY</font>, "
        "each aggregate covers the whole table and the query returns one row. "
        "SQLite prints this table's average as 56125.0 because "
        "<font face='Courier'>AVG</font> returns a real number even when the mean "
        "is a whole number of rupees. <font face='Courier'>SUM</font> of these "
        "whole-number salaries prints as the integer 898000."
    ))
    st.append(sub("2.2 COUNT and COUNT DISTINCT"))
    st.append(para(
        "<font face='Courier'>COUNT(*)</font> counts rows, so question 3 returns 16. "
        "<font face='Courier'>COUNT(DISTINCT department)</font> counts different "
        "values of that column. Ten of the sixteen rows repeat a department name, "
        "so question 4 returns 4: CSE, Mechanical, ECE and Civil."
    ))
    st.append(sub("2.3 GROUP BY"))
    st.append(para(
        "<font face='Courier'>GROUP BY department</font> makes one group per "
        "distinct department, then evaluates the aggregates inside each group. "
        "Every column in the <font face='Courier'>SELECT</font> list must be "
        "either grouped or aggregated. Question 8 therefore returns four rows, "
        "each with its own count, total, average, highest salary and lowest salary."
    ))
    st.append(sub("2.4 WHERE and HAVING"))
    st.append(para(
        "<font face='Courier'>WHERE</font> filters rows before the aggregates run. "
        "Question 11 uses it to keep only CSE, then computes one count, one total "
        "and one average for those five rows. "
        "<font face='Courier'>HAVING</font> filters groups after the aggregates "
        "are computed, so it can test <font face='Courier'>AVG(salary)</font> or "
        "<font face='Courier'>COUNT(*)</font>. "
        "<font face='Courier'>WHERE AVG(salary) &gt; 55000</font> is illegal. "
        "Question 9 keeps departments whose average is above 55000 (Civil at "
        "45000.0 drops out). Question 10 keeps departments with more than three "
        "employees (Civil, with three, drops out). Question 12 groups by city "
        "and keeps the five cities that appear twice."
    ))

    st.append(heading("3. Schema"))
    st.append(para(
        "One table, <font face='Courier'>employee</font>, holds six attributes. "
        "<font face='Courier'>sr_no</font> is the employee number (primary key). "
        "<font face='Courier'>department</font> and <font face='Courier'>city</font> "
        "are stored as names so <font face='Courier'>GROUP BY</font> results can "
        "be read without a second lookup. <font face='Courier'>salary</font> is a "
        "positive monthly amount in rupees."
    ))
    st.append(table(
        [
            ["Attribute", "Type", "Constraint", "Role"],
            ["sr_no", "INTEGER", "PRIMARY KEY", "Employee number"],
            ["employee_name", "TEXT", "NOT NULL", "Employee name"],
            ["job", "TEXT", "NOT NULL", "Job title"],
            ["department", "TEXT", "NOT NULL", "Department name"],
            ["salary", "NUMERIC(10,2)", "NOT NULL, CHECK &gt; 0", "Monthly salary (Rs)"],
            ["city", "TEXT", "NOT NULL", "Work city"],
        ],
        col_widths=[CONTENT_W * 0.22, CONTENT_W * 0.20, CONTENT_W * 0.28, CONTENT_W * 0.22],
        pad=4,
    ))

    st.append(heading("4. Questions"))
    st.append(para(
        "Twelve lab questions. Questions 1 and 2 build the table. "
        "Questions 3–7 are aggregates over every employee. "
        "Question 8 groups by department. Questions 9, 10 and 12 filter groups "
        f"with {sql_kw('HAVING')}. Question 11 filters rows with {sql_kw('WHERE')} "
        "before the aggregates, which is how a single department is summarised."
    ))
    st.extend(questions_flow())

    st.append(heading("5. Procedure"))
    st.append(para(
        "Drop <font face='Courier'>employee</font> if it already exists so the "
        "script can be re-run. Create the table, insert the 16 rows, then run "
        "each query in order. Grouped results are ordered so the same script "
        "prints the same rows on every run. The SQL for each question:"
    ))
    st.append(solutions_table())

    st.append(heading("6. Source Code"))
    st.append(para(
        "SQLite script used in the lab compiler "
        "(<font face='Courier'>30-09-2026/employee.sql</font>). "
        "For the class SQL Server, run <font face='Courier'>employee.sqlserver.sql</font>."
    ))
    st.append(code_block(sql_text, size=6.2, leading=7.6))

    st.append(heading("7. Output"))
    st.append(para(
        "The script was executed in SQLite in memory. "
        "<font face='Courier'>CREATE</font> prints a status line and "
        "<font face='Courier'>INSERT</font> prints the row count. "
        "Each <font face='Courier'>SELECT</font> prints the result set that "
        "SQLite returned. Whole-number salaries print as integers; "
        "<font face='Courier'>AVG</font> prints a real (56125.0, 59200.0, "
        "58750.0, and so on)."
    ))
    st.append(code_block(output, size=5.5, leading=6.7))

    st.append(heading("8. Results"))
    st.append(para(
        "Sixteen employees load successfully. Every question returns a "
        "non-empty result on this seed. The figures below are the row counts "
        "and values from the SQLite run in section 7."
    ))
    st.append(table(
        [
            ["Q. No.", "Rows", "What the result shows"],
            ["1", "—", "Table employee created with 6 attributes"],
            ["2", "16", "16 rows inserted across CSE, Mechanical, ECE and Civil"],
            ["3", "1", "COUNT(*) = 16 employees"],
            ["4", "1", "COUNT(DISTINCT department) = 4"],
            ["5", "1", "SUM(salary) = 898000"],
            ["6", "1", "AVG(salary) = 56125.0"],
            ["7", "1", "MAX = 92000 and MIN = 28000"],
            ["8", "4", "COUNT, SUM, AVG, MAX and MIN for each of the 4 departments"],
            ["9", "3", "CSE (59200.0), ECE (58750.0), Mechanical (58000.0); Civil excluded"],
            ["10", "3", "CSE (5), ECE (4), Mechanical (4); Civil has only 3"],
            ["11", "1", "CSE only: 5 employees, total 296000, average 59200.0"],
            ["12", "5", "Bangalore, Chennai, Delhi, Hyderabad and Mumbai, 2 each"],
        ],
        col_widths=[CONTENT_W * 0.12, CONTENT_W * 0.10, CONTENT_W * 0.68],
        pad=4,
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "Department totals from question 8 add up to the overall total: "
        "296000 + 135000 + 235000 + 232000 = 898000, and 5 + 3 + 4 + 4 = 16. "
        "The CSE row of that result is the same triple question 11 prints on "
        "its own (5, 296000, 59200.0). Questions 9 and 10 both drop Civil, "
        "for different reasons: its average is 45000.0, and it has only three "
        "employees. Question 12 keeps the five cities that are shared and drops "
        "Ahmedabad, Pune, Jaipur, Kochi, Kolkata and Nagpur."
    ))

    st.append(heading("9. Conclusion"))
    st.append(para(
        "Aggregate functions collapse many rows into one value. "
        "<font face='Courier'>COUNT</font> answers how many, "
        "<font face='Courier'>SUM</font> and <font face='Courier'>AVG</font> "
        "answer how much, and <font face='Courier'>MAX</font> / "
        "<font face='Courier'>MIN</font> answer the extremes. "
        "<font face='Courier'>GROUP BY</font> repeats that collapse once per "
        "group. <font face='Courier'>WHERE</font> chooses the rows that enter "
        "the calculation; <font face='Courier'>HAVING</font> chooses which "
        "groups survive it. These are the tools for summary questions: "
        "how many employees, how much they earn, and which groups pass a test."
    ))
    return st


def build() -> None:
    st = build_story(include_cover=True)
    write_report(
        OUT_PDF,
        f"DBMS Lab · 30-09-2026 · Aggregate Functions · {STUDENT['name']}",
        st,
    )
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
