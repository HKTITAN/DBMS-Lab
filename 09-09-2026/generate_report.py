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

# Sheet numbered CREATE + INSERT as two "1." items; shown as 1(a) / 1(b).
EMPLOYEE_ATTRIBUTES = [
    "sr no",
    "employee name",
    "job",
    "manager",
    "hire date",
    "salary",
    "department no",
    "city",
]


def sql_kw(word: str) -> str:
    """Courier SQL keyword for question text (word is a trusted literal)."""
    return f"<font face='Courier'>{word}</font>"


QUESTIONS = [
    {
        "num": "1(a)",
        "html": (
            f"Create a table {sql_kw('employee')} with the following attributes:"
        ),
        "subitems": EMPLOYEE_ATTRIBUTES,
    },
    {
        "num": "1(b)",
        "html": "Insert 10 rows in the above mentioned table.",
    },
    {
        "num": "2",
        "html": f"{sql_kw('SELECT')} all the details from the employee table.",
    },
    {
        "num": "3",
        "html": (
            f"Select only {sql_kw('DISTINCT')} department number from the "
            "employee table."
        ),
        "note": "The lab sheet wrote &ldquo;distant&rdquo; for this question.",
    },
    {
        "num": "4",
        "html": f"{sql_kw('SELECT')} all department numbers from the employee table.",
    },
    {
        "num": "5",
        "html": (
            f"{sql_kw('SELECT')} employee name, salary "
            f"{sql_kw('WHERE')} salary is &gt; 30000 rs from the employee table."
        ),
    },
    {
        "num": "6",
        "html": (
            f"{sql_kw('SELECT')} employee name, hire date "
            f"{sql_kw('WHERE')} city is not Delhi from the employee table."
        ),
    },
    {
        "num": "7",
        "html": (
            f"{sql_kw('SELECT')} employee name, hire date "
            f"{sql_kw('WHERE')} city is either Delhi or Mumbai from the "
            "employee table."
        ),
    },
    {
        "num": "8",
        "html": (
            f"{sql_kw('SELECT')} employee number, employee name "
            f"{sql_kw('WHERE')} salary is {sql_kw('BETWEEN')} 30000 rs and "
            "50000 rs."
        ),
    },
    {
        "num": "9",
        "html": (
            f"{sql_kw('SELECT')} employee number, employee name "
            f"{sql_kw('WHERE')} salary is {sql_kw('NOT BETWEEN')} 30000 and "
            "50000 from the employee table."
        ),
    },
    {
        "num": "10",
        "html": (
            f"{sql_kw('SELECT')} all the details {sql_kw('WHERE')} city is "
            "among the following: Delhi, Mumbai, Chennai, Bangalore."
        ),
    },
    {
        "num": "11",
        "html": (
            f"{sql_kw('SELECT')} all the details {sql_kw('WHERE')} city is not "
            "Mumbai, Delhi or Chennai from the employee table."
        ),
    },
    {
        "num": "12",
        "html": (
            f"{sql_kw('SELECT')} all the details from the employee table and "
            f"{sql_kw('ORDER BY')} employee names in descending order."
        ),
    },
    {
        "num": "13",
        "html": (
            "Display the list of employees in ascending order from the "
            "employee table."
        ),
    },
    {
        "num": "14",
        "html": (
            f"Create a table {sql_kw('cse')} (CSE students) with the following "
            "attributes:"
        ),
        "subitems": ["roll no", "student name", "city"],
    },
    {
        "num": "15",
        "html": f"Insert 5 rows in the {sql_kw('cse')} table.",
    },
    {
        "num": "16",
        "html": (
            f"Create a table {sql_kw('mechanical')} (Mechanical students) with "
            "the following attributes:"
        ),
        "subitems": ["roll no", "student name", "city"],
    },
    {
        "num": "17",
        "html": f"Insert 5 rows in the {sql_kw('mechanical')} table.",
        "note": (
            "Two rows also appear in <font face='Courier'>cse</font> "
            "(Amit Verma / Delhi and Sneha Reddy / Hyderabad) so "
            f"{sql_kw('INTERSECT')} is non-empty."
        ),
    },
    {
        "num": "18",
        "html": f"{sql_kw('SELECT')} all the details from the {sql_kw('cse')} table.",
    },
    {
        "num": "19",
        "html": (
            f"{sql_kw('SELECT')} all the details from the "
            f"{sql_kw('mechanical')} table."
        ),
    },
    {
        "num": "20",
        "html": (
            f"{sql_kw('SELECT')} the {sql_kw('UNION')} of {sql_kw('cse')} and "
            f"{sql_kw('mechanical')}."
        ),
    },
    {
        "num": "21",
        "html": (
            f"{sql_kw('SELECT')} the {sql_kw('UNION ALL')} of {sql_kw('cse')} "
            f"and {sql_kw('mechanical')}."
        ),
    },
    {
        "num": "22",
        "html": (
            f"{sql_kw('SELECT')} the {sql_kw('INTERSECT')} of {sql_kw('cse')} "
            f"and {sql_kw('mechanical')}."
        ),
    },
]

SQL_SOLUTIONS = [
    (
        "1(a)",
        "CREATE TABLE employee (\n"
        "    sr_no INTEGER PRIMARY KEY,\n"
        "    employee_name TEXT NOT NULL,\n"
        "    job TEXT NOT NULL,\n"
        "    manager TEXT,\n"
        "    hire_date DATE NOT NULL,\n"
        "    salary NUMERIC(10, 2) NOT NULL CHECK (salary > 0),\n"
        "    department_no INTEGER NOT NULL,\n"
        "    city TEXT NOT NULL\n"
        ");",
    ),
    (
        "1(b)",
        "INSERT INTO employee\n"
        "    (sr_no, employee_name, job, manager, hire_date, salary, department_no, city)\n"
        "VALUES\n"
        "    (1,  'Rajesh Kumar',    'General Manager',    NULL,            '2018-03-12', 85000.00, 10, 'Delhi'),\n"
        "    (2,  'Ananya Sharma',   'Software Engineer',  'Rajesh Kumar',  '2021-07-01', 45000.00, 20, 'Bangalore'),\n"
        "    (3,  'Rohan Mehta',     'Accountant',         'Rajesh Kumar',  '2020-01-15', 28000.00, 30, 'Mumbai'),\n"
        "    (4,  'Priya Nair',      'HR Executive',       'Rajesh Kumar',  '2022-04-20', 32000.00, 40, 'Chennai'),\n"
        "    (5,  'Vikram Singh',    'Sales Manager',      'Rajesh Kumar',  '2019-11-08', 52000.00, 50, 'Hyderabad'),\n"
        "    (6,  'Fatima Khan',     'Software Engineer',  'Ananya Sharma', '2023-02-14', 38000.00, 20, 'Bangalore'),\n"
        "    (7,  'Arjun Patel',     'Clerk',              'Rohan Mehta',   '2024-06-01', 18000.00, 30, 'Pune'),\n"
        "    (8,  'Neha Gupta',      'Marketing Analyst',  'Rajesh Kumar',  '2021-09-10', 35000.00, 60, 'Delhi'),\n"
        "    (9,  'Karan Iyer',      'Database Admin',     'Ananya Sharma', '2020-12-05', 48000.00, 20, 'Mumbai'),\n"
        "    (10, 'Meera Joshi',     'Receptionist',       'Priya Nair',    '2023-08-22', 22000.00, 40, 'Chennai');",
    ),
    ("2", "SELECT * FROM employee;"),
    ("3", "SELECT DISTINCT department_no FROM employee;"),
    ("4", "SELECT department_no FROM employee;"),
    (
        "5",
        "SELECT employee_name, salary\n"
        "FROM employee\n"
        "WHERE salary > 30000;",
    ),
    (
        "6",
        "SELECT employee_name, hire_date\n"
        "FROM employee\n"
        "WHERE city <> 'Delhi';",
    ),
    (
        "7",
        "SELECT employee_name, hire_date\n"
        "FROM employee\n"
        "WHERE city = 'Delhi' OR city = 'Mumbai';",
    ),
    (
        "8",
        "SELECT sr_no, employee_name\n"
        "FROM employee\n"
        "WHERE salary BETWEEN 30000 AND 50000;",
    ),
    (
        "9",
        "SELECT sr_no, employee_name\n"
        "FROM employee\n"
        "WHERE salary NOT BETWEEN 30000 AND 50000;",
    ),
    (
        "10",
        "SELECT *\n"
        "FROM employee\n"
        "WHERE city IN ('Delhi', 'Mumbai', 'Chennai', 'Bangalore');",
    ),
    (
        "11",
        "SELECT *\n"
        "FROM employee\n"
        "WHERE city NOT IN ('Mumbai', 'Delhi', 'Chennai');",
    ),
    (
        "12",
        "SELECT *\n"
        "FROM employee\n"
        "ORDER BY employee_name DESC;",
    ),
    (
        "13",
        "SELECT *\n"
        "FROM employee\n"
        "ORDER BY employee_name ASC;",
    ),
    (
        "14",
        "CREATE TABLE cse (\n"
        "    roll_no INTEGER PRIMARY KEY,\n"
        "    student_name TEXT NOT NULL,\n"
        "    city TEXT NOT NULL\n"
        ");",
    ),
    (
        "15",
        "INSERT INTO cse (roll_no, student_name, city)\n"
        "VALUES\n"
        "    (1, 'Amit Verma',   'Delhi'),\n"
        "    (2, 'Rahul Das',    'Kolkata'),\n"
        "    (3, 'Sneha Reddy',  'Hyderabad'),\n"
        "    (4, 'Isha Kapoor',  'Chandigarh'),\n"
        "    (5, 'Dev Patel',    'Ahmedabad');",
    ),
    (
        "16",
        "CREATE TABLE mechanical (\n"
        "    roll_no INTEGER PRIMARY KEY,\n"
        "    student_name TEXT NOT NULL,\n"
        "    city TEXT NOT NULL\n"
        ");",
    ),
    (
        "17",
        "INSERT INTO mechanical (roll_no, student_name, city)\n"
        "VALUES\n"
        "    (1, 'Amit Verma',   'Delhi'),\n"
        "    (3, 'Sneha Reddy',  'Hyderabad'),\n"
        "    (6, 'Mohit Jain',   'Jaipur'),\n"
        "    (7, 'Kavya Menon',  'Kochi'),\n"
        "    (8, 'Tushar Rao',   'Nagpur');",
    ),
    ("18", "SELECT * FROM cse;"),
    ("19", "SELECT * FROM mechanical;"),
    (
        "20",
        "SELECT * FROM cse\n"
        "UNION\n"
        "SELECT * FROM mechanical\n"
        "ORDER BY roll_no;",
    ),
    (
        "21",
        "SELECT * FROM cse\n"
        "UNION ALL\n"
        "SELECT * FROM mechanical\n"
        "ORDER BY roll_no;",
    ),
    (
        "22",
        "SELECT * FROM cse\n"
        "INTERSECT\n"
        "SELECT * FROM mechanical\n"
        "ORDER BY roll_no;",
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
    """Numbered lab-sheet list: wrapping questions, nested attributes on 1(a)."""
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
            st, "4",
            "SELECT Queries — DISTINCT, WHERE, BETWEEN, IN, ORDER BY, UNION, INTERSECT",
            "SELECT, DISTINCT, WHERE, BETWEEN, IN, ORDER BY, UNION, UNION ALL, INTERSECT",
            "employee (10 rows); cse and mechanical (5 students each, 2 shared)",
            LAB_DATE,
        )

    st.append(heading("1. Aim"))
    st.append(para(
        "To answer the lab questions below: create an "
        "<font face='Courier'>employee</font> table with the given attributes, "
        "insert 10 rows, and run the listed "
        "<font face='Courier'>SELECT</font> queries "
        "(<font face='Courier'>DISTINCT</font>, <font face='Courier'>WHERE</font>, "
        "<font face='Courier'>BETWEEN</font>, <font face='Courier'>IN</font>, "
        "<font face='Courier'>ORDER BY</font>). Then create compatible "
        "<font face='Courier'>cse</font> and <font face='Courier'>mechanical</font> "
        "student tables and combine them with "
        "<font face='Courier'>UNION</font>, <font face='Courier'>UNION ALL</font>, "
        "and <font face='Courier'>INTERSECT</font>."
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
        "the result. Question 3 on the lab sheet asks for a &ldquo;distant&rdquo; "
        "department number; that is <font face='Courier'>DISTINCT</font>. "
        "<font face='Courier'>SELECT department_no</font> lists a department once "
        "per employee (question 4); "
        "<font face='Courier'>SELECT DISTINCT department_no</font> lists each "
        "department number only once."
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
    st.append(sub("2.7 UNION"))
    st.append(para(
        "<font face='Courier'>UNION</font> stacks two compatible "
        "<font face='Courier'>SELECT</font> results and keeps each distinct row "
        "once. Both sides must return the same number of columns with comparable "
        "types. Duplicate rows that appear in both "
        "<font face='Courier'>cse</font> and <font face='Courier'>mechanical</font> "
        "are listed only once. Column names in the result come from the first "
        "<font face='Courier'>SELECT</font>."
    ))
    st.append(sub("2.8 UNION ALL"))
    st.append(para(
        "<font face='Courier'>UNION ALL</font> also stacks two results but does "
        "<b>not</b> remove duplicates. A row that exists in both tables appears "
        "twice. Use it when every occurrence matters, or when the extra distinct "
        "pass of <font face='Courier'>UNION</font> is unnecessary. Here five CSE "
        "rows plus five Mechanical rows yield ten rows."
    ))
    st.append(sub("2.9 INTERSECT"))
    st.append(para(
        "<font face='Courier'>INTERSECT</font> keeps rows that appear in "
        "<b>both</b> results. Entire rows must match "
        "(<font face='Courier'>roll_no</font>, <font face='Courier'>student_name</font>, "
        "and <font face='Courier'>city</font>). Amit Verma / Delhi and Sneha Reddy / "
        "Hyderabad were inserted into both tables, so the intersection has two rows. "
        "SQLite and SQL Server both support <font face='Courier'>INTERSECT</font>."
    ))

    st.append(heading("3. Schema"))
    st.append(para(
        "Three tables. <font face='Courier'>employee</font> holds eight attributes "
        "for questions 1–13. <font face='Courier'>sr_no</font> is the employee "
        "number (primary key). <font face='Courier'>manager</font> stores the "
        "manager's name, or <font face='Courier'>NULL</font> for the top manager. "
        "<font face='Courier'>cse</font> and <font face='Courier'>mechanical</font> "
        "are compatible three-column student lists for questions 14–22."
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
    st.append(Spacer(1, 0.25 * cm))
    st.append(para(
        "<font face='Courier'>cse</font> and <font face='Courier'>mechanical</font> "
        "share the same three attributes so they can be combined with set operators:"
    ))
    st.append(table(
        [
            ["Attribute", "Type", "Constraint", "Role"],
            ["roll_no", "INTEGER", "PRIMARY KEY", "Student roll number"],
            ["student_name", "TEXT", "NOT NULL", "Student name"],
            ["city", "TEXT", "NOT NULL", "Home city"],
        ],
        col_widths=[CONTENT_W * 0.22, CONTENT_W * 0.20, CONTENT_W * 0.24, CONTENT_W * 0.24],
        pad=4,
    ))

    st.append(heading("4. Questions"))
    st.append(para(
        "The lab sheet numbered both "
        f"{sql_kw('CREATE')} and {sql_kw('INSERT')} as <b>1</b>; they are shown "
        "here as <b>1(a)</b> and <b>1(b)</b>. Question 3 wrote "
        "&ldquo;distant&rdquo;; the SQL keyword is "
        f"{sql_kw('DISTINCT')}. Employee number is stored as "
        f"{sql_kw('sr_no')}. Questions <b>14–22</b> are the CSE / Mechanical "
        f"{sql_kw('UNION')}, {sql_kw('UNION ALL')}, and {sql_kw('INTERSECT')} "
        "exercise: create both student tables, list their rows, then combine them."
    ))
    st.extend(questions_flow())

    st.append(heading("5. Procedure"))
    st.append(para(
        "Drop <font face='Courier'>employee</font>, <font face='Courier'>cse</font>, "
        "and <font face='Courier'>mechanical</font> if they already exist so the "
        "script can be re-run. Then answer each lab question in order. "
        "City values on <font face='Courier'>employee</font> are stored in title "
        "case (Delhi, Mumbai, &hellip;) and matched with that same casing. "
        "Set-operation results are ordered by <font face='Courier'>roll_no</font>. "
        "The SQL for each question:"
    ))
    st.append(solutions_table())

    st.append(heading("6. Source Code"))
    st.append(para(
        "SQLite script used in the lab compiler "
        "(<font face='Courier'>09-09-2026/employee.sql</font>). "
        "For the class SQL Server, run <font face='Courier'>employee.sqlserver.sql</font>."
    ))
    st.append(code_block(sql_text, size=6.4, leading=7.8))

    st.append(heading("7. Output"))
    st.append(para(
        "The script was executed in SQLite in memory. "
        "<font face='Courier'>CREATE</font> and <font face='Courier'>INSERT</font> "
        "print a status line; each <font face='Courier'>SELECT</font> prints its "
        "result set. <font face='Courier'>NULL</font> in the manager column is "
        "shown as an empty cell."
    ))
    st.append(code_block(output, size=5.6, leading=6.9))

    st.append(heading("8. Results"))
    st.append(para(
        "Ten employees load successfully, then five CSE students and five "
        "Mechanical students. Each lab question returns a non-empty result on "
        "this seed data:"
    ))
    st.append(table(
        [
            ["Q. No.", "Rows", "What the result shows"],
            ["1(a)", "—", "Table employee created with 8 attributes"],
            ["1(b)", "10", "10 rows inserted"],
            ["2", "10", "All details from the employee table"],
            ["3", "6", "DISTINCT department numbers: 10, 20, 30, 40, 50, 60"],
            ["4", "10", "All department numbers (dept 20 appears three times)"],
            ["5", "7", "Employee name and salary where salary is &gt; 30000 rs"],
            ["6", "8", "Employee name and hire date where city is not Delhi"],
            ["7", "4", "Employee name and hire date where city is Delhi or Mumbai"],
            ["8", "5", "Employee number and name where salary is between 30000 rs and 50000 rs"],
            ["9", "5", "Employee number and name where salary is not between 30000 and 50000"],
            ["10", "8", "All details where city is Delhi, Mumbai, Chennai, or Bangalore"],
            ["11", "4", "All details where city is not Mumbai, Delhi, or Chennai"],
            ["12", "10", "All details ordered by employee names descending"],
            ["13", "10", "List of employees in ascending order"],
            ["14", "—", "Table cse created (roll no, student name, city)"],
            ["15", "5", "5 CSE students inserted"],
            ["16", "—", "Table mechanical created with the same attributes"],
            ["17", "5", "5 Mechanical students inserted (2 rows also in cse)"],
            ["18", "5", "All details from the cse table"],
            ["19", "5", "All details from the mechanical table"],
            ["20", "8", "UNION — unique rows from either table (5 + 5 − 2)"],
            ["21", "10", "UNION ALL — all rows including the 2 duplicates"],
            ["22", "2", "INTERSECT — Amit Verma / Delhi and Sneha Reddy / Hyderabad"],
        ],
        col_widths=[CONTENT_W * 0.16, CONTENT_W * 0.10, CONTENT_W * 0.64],
        pad=4,
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "Question 3 (<font face='Courier'>DISTINCT</font>) collapses ten department "
        "values to six unique numbers; question 4 lists all ten. Questions 8 and 9 "
        "partition salaries with no overlap (5 + 5 = 10). Question 11 keeps "
        "Bangalore, Hyderabad, and Pune — cities that are not Mumbai, Delhi, or Chennai. "
        "Questions 20–22 show the set-operator identities on this seed: "
        "<font face='Courier'>UNION</font> has 8 rows, "
        "<font face='Courier'>UNION ALL</font> has 10, and "
        "<font face='Courier'>INTERSECT</font> has the 2 shared students."
    ))

    st.append(heading("9. Conclusion"))
    st.append(para(
        "A single <font face='Courier'>SELECT</font> can project columns, remove "
        "duplicates, filter with comparison and set predicates, and sort the "
        "result. <font face='Courier'>DISTINCT</font> answers &ldquo;which unique "
        "values exist?&rdquo; <font face='Courier'>WHERE</font> answers "
        "&ldquo;which rows match this condition?&rdquo; "
        "<font face='Courier'>BETWEEN</font> and <font face='Courier'>IN</font> "
        "express ranges and lists clearly. <font face='Courier'>ORDER BY</font> "
        "changes presentation only. "
        "<font face='Courier'>UNION</font> / <font face='Courier'>UNION ALL</font> / "
        "<font face='Courier'>INTERSECT</font> combine two compatible queries: "
        "unique rows from either side, every row including duplicates, or only "
        "rows common to both. Together these clauses are the core of everyday "
        "retrieval in SQL."
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
