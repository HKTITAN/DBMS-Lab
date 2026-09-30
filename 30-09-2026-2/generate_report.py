"""
DBMS Lab — 30-09-2026
=====================

Builds `DBMS_Lab_Nested_Queries_Report.pdf` from `employee.sql` (SQLite).

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
OUT_PDF = ROOT / "DBMS_Lab_Nested_Queries_Report.pdf"

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
            "Civil has no Professor, so "
            f"{sql_kw('NOT IN')} is non-empty. The highest salary (92000) and "
            "the second-highest salary (90000) are each earned by one employee. "
            "Neha Gupta (ECE, 58000) is above the company average and below "
            "the ECE average."
        ),
    },
    {
        "num": "3",
        "html": (
            "Display the employee name, department and salary of employees who "
            "earn more than the average salary, using a nested query."
        ),
    },
    {
        "num": "4",
        "html": (
            "Display the employee with the highest salary in each department "
            "using a subquery."
        ),
    },
    {
        "num": "5",
        "html": "Find the 2nd highest salary of the employees.",
    },
    {
        "num": "6",
        "html": (
            "Display employees who work in a department that has a Professor, "
            f"using {sql_kw('IN')} and a subquery."
        ),
    },
    {
        "num": "7",
        "html": (
            "Display employees who do not work in a department that has a "
            f"Professor, using {sql_kw('NOT IN')} and a subquery."
        ),
        "note": (
            f"{sql_kw('department')} is {sql_kw('NOT NULL')}, so the subquery "
            "cannot return NULL. A NULL in a "
            f"{sql_kw('NOT IN')} list would make the predicate unknown for every row."
        ),
    },
    {
        "num": "8",
        "html": (
            "Display employees for whom there exists a higher-paid colleague "
            "in the same department, using "
            f"{sql_kw('EXISTS')}."
        ),
    },
    {
        "num": "9",
        "html": (
            "Display employees who earn more than the average salary of their "
            "own department, using a correlated subquery."
        ),
        "note": (
            "The comparison is strict. Rahul Das earns exactly the Civil "
            "average (45000), so this question does not list him. Neha Gupta "
            "is above the company average and below the ECE average, so she "
            "is in question 3 and not in this question."
        ),
    },
    {
        "num": "10",
        "html": (
            "Display the department whose total salary is the greatest, "
            "using a nested query."
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
    (
        "3",
        "SELECT employee_name, department, salary\n"
        "FROM employee\n"
        "WHERE salary > (SELECT AVG(salary) FROM employee)\n"
        "ORDER BY salary DESC;",
    ),
    (
        "4",
        "SELECT e.employee_name, e.department, e.salary\n"
        "FROM employee AS e\n"
        "WHERE e.salary = (\n"
        "    SELECT MAX(c.salary)\n"
        "    FROM employee AS c\n"
        "    WHERE c.department = e.department\n"
        ")\n"
        "ORDER BY e.department;",
    ),
    (
        "5",
        "SELECT MAX(salary)\n"
        "FROM employee\n"
        "WHERE salary < (SELECT MAX(salary) FROM employee);",
    ),
    (
        "6",
        "SELECT employee_name, job, department, salary\n"
        "FROM employee\n"
        "WHERE department IN (\n"
        "    SELECT department\n"
        "    FROM employee\n"
        "    WHERE job = 'Professor'\n"
        ")\n"
        "ORDER BY department, employee_name;",
    ),
    (
        "7",
        "SELECT employee_name, job, department, salary\n"
        "FROM employee\n"
        "WHERE department NOT IN (\n"
        "    SELECT department\n"
        "    FROM employee\n"
        "    WHERE job = 'Professor'\n"
        ")\n"
        "ORDER BY department, employee_name;",
    ),
    (
        "8",
        "SELECT e.employee_name, e.department, e.salary\n"
        "FROM employee AS e\n"
        "WHERE EXISTS (\n"
        "    SELECT 1\n"
        "    FROM employee AS c\n"
        "    WHERE c.department = e.department\n"
        "      AND c.salary > e.salary\n"
        ")\n"
        "ORDER BY e.department, e.salary DESC;",
    ),
    (
        "9",
        "SELECT e.employee_name, e.department, e.salary\n"
        "FROM employee AS e\n"
        "WHERE e.salary > (\n"
        "    SELECT AVG(d.salary)\n"
        "    FROM employee AS d\n"
        "    WHERE d.department = e.department\n"
        ")\n"
        "ORDER BY e.department, e.salary DESC;",
    ),
    (
        "10",
        "SELECT department,\n"
        "       SUM(salary) AS total_salary\n"
        "FROM employee\n"
        "GROUP BY department\n"
        "HAVING SUM(salary) = (\n"
        "    SELECT MAX(total_salary)\n"
        "    FROM (\n"
        "        SELECT SUM(salary) AS total_salary\n"
        "        FROM employee\n"
        "        GROUP BY department\n"
        "    ) AS dept_totals\n"
        ");",
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

    if one("SELECT COUNT(*), AVG(salary) FROM employee") != (16, 56125.0):
        raise AssertionError("seed aggregates changed")

    above = all_rows(
        "SELECT employee_name FROM employee "
        "WHERE salary > (SELECT AVG(salary) FROM employee) ORDER BY salary DESC"
    )
    if [r[0] for r in above] != [
        "Rajesh Kumar", "Priya Nair", "Vikram Singh", "Ananya Sharma",
        "Rohan Mehta", "Sneha Reddy", "Neha Gupta",
    ]:
        raise AssertionError(f"above-average names changed: {above}")

    tops = all_rows(
        "SELECT e.employee_name, e.department FROM employee AS e "
        "WHERE e.salary = (SELECT MAX(c.salary) FROM employee AS c "
        "WHERE c.department = e.department) ORDER BY e.department"
    )
    if tops != [
        ("Rajesh Kumar", "CSE"),
        ("Sneha Reddy", "Civil"),
        ("Priya Nair", "ECE"),
        ("Vikram Singh", "Mechanical"),
    ]:
        raise AssertionError(f"department maxima changed: {tops}")

    second = one(
        "SELECT MAX(salary) FROM employee "
        "WHERE salary < (SELECT MAX(salary) FROM employee)"
    )
    if second != (90000,):
        raise AssertionError(f"second-highest changed: {second}")

    in_prof = one(
        "SELECT COUNT(*) FROM employee WHERE department IN "
        "(SELECT department FROM employee WHERE job = 'Professor')"
    )[0]
    not_in = all_rows(
        "SELECT employee_name FROM employee WHERE department NOT IN "
        "(SELECT department FROM employee WHERE job = 'Professor') "
        "ORDER BY employee_name"
    )
    if in_prof != 13 or [r[0] for r in not_in] != ["Rahul Das", "Sneha Reddy", "Tushar Rao"]:
        raise AssertionError(f"IN/NOT IN changed: {in_prof}, {not_in}")

    exists_n = one(
        "SELECT COUNT(*) FROM employee AS e WHERE EXISTS ("
        "SELECT 1 FROM employee AS c WHERE c.department = e.department "
        "AND c.salary > e.salary)"
    )[0]
    if exists_n != 12:
        raise AssertionError(f"EXISTS count changed: {exists_n}")

    corr = all_rows(
        "SELECT e.employee_name, e.department FROM employee AS e "
        "WHERE e.salary > (SELECT AVG(d.salary) FROM employee AS d "
        "WHERE d.department = e.department) "
        "ORDER BY e.department, e.salary DESC"
    )
    if corr != [
        ("Rajesh Kumar", "CSE"),
        ("Ananya Sharma", "CSE"),
        ("Sneha Reddy", "Civil"),
        ("Priya Nair", "ECE"),
        ("Vikram Singh", "Mechanical"),
        ("Rohan Mehta", "Mechanical"),
    ]:
        raise AssertionError(f"correlated average changed: {corr}")

    top_dept = one(
        "SELECT department, SUM(salary) FROM employee GROUP BY department "
        "HAVING SUM(salary) = (SELECT MAX(total_salary) FROM ("
        "SELECT SUM(salary) AS total_salary FROM employee GROUP BY department"
        ") AS dept_totals)"
    )
    if top_dept != ("CSE", 296000):
        raise AssertionError(f"greatest department total changed: {top_dept}")


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
    """Numbered lab-sheet list: wrapping questions, nested attributes on 1."""
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
            st, "6",
            "Nested Queries",
            "Subqueries, IN, NOT IN, EXISTS, correlated subqueries",
            "employee (16 rows; CSE, Mechanical, ECE, Civil)",
            LAB_DATE,
        )

    st.append(heading("1. Aim"))
    st.append(para(
        "To create an <font face='Courier'>employee</font> table, insert 16 rows "
        "across four departments, and answer the lab questions "
        "with nested queries: a scalar subquery, the highest salary in each "
        "department, the second-highest salary, <font face='Courier'>IN</font> / "
        "<font face='Courier'>NOT IN</font>, <font face='Courier'>EXISTS</font>, "
        "a correlated department average, and the department with the greatest "
        "total salary."
    ))

    st.append(heading("2. Theory"))
    st.append(sub("2.1 Scalar subqueries"))
    st.append(para(
        "A subquery is a <font face='Courier'>SELECT</font> inside another "
        "statement. A scalar subquery returns one value and can be compared "
        "with <font face='Courier'>&gt;</font> or <font face='Courier'>=</font>. "
        "Question 3 compares each salary with the single overall average, "
        "56125.0. That inner query does not mention the outer row, so it is "
        "uncorrelated and can be computed once."
    ))
    st.append(sub("2.2 IN and NOT IN"))
    st.append(para(
        "<font face='Courier'>IN (subquery)</font> keeps an outer row when its "
        "value appears in the inner result. Question 6 keeps employees whose "
        "department is one of the departments that contain a Professor "
        "(CSE, Mechanical, ECE). <font face='Courier'>NOT IN</font> is the "
        "complement: question 7 keeps Civil, the only department with no "
        "Professor. If the subquery could return <font face='Courier'>NULL</font>, "
        "<font face='Courier'>NOT IN</font> would be unknown for every row and "
        "the result would be empty. Here <font face='Courier'>department</font> "
        "is <font face='Courier'>NOT NULL</font>, so that trap does not apply."
    ))
    st.append(sub("2.3 EXISTS and correlated subqueries"))
    st.append(para(
        "A correlated subquery mentions a column from the outer query, so it "
        "is re-evaluated for each outer row. "
        "<font face='Courier'>EXISTS</font> is true when the inner query returns "
        "at least one row; the selected columns do not matter, which is why "
        "question 8 selects the constant 1. It lists everyone who has a "
        "colleague in the same department on a higher salary — everyone except "
        "the highest-paid person in each department. Question 4 uses the same "
        "correlation to keep the row whose salary equals the department maximum. "
        "Question 9 compares each salary with the average of that employee's "
        "own department, which is a different number from the overall average "
        "used in question 3."
    ))
    st.append(sub("2.4 Second-highest salary"))
    st.append(para(
        "Question 5 asks, word for word: &ldquo;Find the 2nd highest salary "
        "of the employees.&rdquo; The nested query is "
        "<font face='Courier'>SELECT MAX(salary) FROM employee WHERE salary "
        "&lt; (SELECT MAX(salary) FROM employee)</font>. The inner "
        "<font face='Courier'>MAX</font> is the top salary (92000). The outer "
        "<font face='Courier'>MAX</font> is the largest salary strictly below "
        "that value, which is the next distinct salary. SQLite returns one "
        "row: 90000. The same pattern still means second-highest distinct "
        "salary if two people share the top salary."
    ))
    st.append(sub("2.5 A nested aggregate"))
    st.append(para(
        "Question 10 asks which department has the greatest total salary. "
        "The inner query groups by department and the middle query takes "
        "<font face='Courier'>MAX</font> of those totals. The outer "
        "<font face='Courier'>HAVING</font> keeps the department whose "
        "<font face='Courier'>SUM(salary)</font> equals that maximum. "
        "CSE's total is 296000, which is greater than ECE (235000), "
        "Mechanical (232000) and Civil (135000)."
    ))

    st.append(heading("3. Schema"))
    st.append(para(
        "One table, <font face='Courier'>employee</font>, holds six attributes. "
        "This script creates the table and inserts the 16 rows so the lab "
        "runs on its own. "
        "<font face='Courier'>sr_no</font> is the employee number (primary key). "
        "<font face='Courier'>salary</font> is a positive monthly amount in rupees."
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
        "Ten lab questions. Questions 1 and 2 build the table. "
        "Question 3 compares each salary with one overall average. "
        "Question 4 finds the highest salary in each department. "
        "Question 5 is: Find the 2nd highest salary of the employees. "
        f"Questions 6 and 7 use {sql_kw('IN')} and {sql_kw('NOT IN')}. "
        f"Question 8 uses {sql_kw('EXISTS')}. Question 9 is a correlated "
        "department average. Question 10 nests an aggregate to find the "
        "department with the greatest total salary."
    ))
    st.extend(questions_flow())

    st.append(heading("5. Procedure"))
    st.append(para(
        "Drop <font face='Courier'>employee</font> if it already exists so the "
        "script can be re-run. Create the table, insert the 16 rows, then run "
        "each query in order. Results that return more than one row are ordered "
        "so the same script prints the same rows on every run. "
        "The SQL for each question:"
    ))
    st.append(solutions_table())

    st.append(heading("6. Source Code"))
    st.append(para(
        "SQLite script used in the lab compiler "
        "(<font face='Courier'>30-09-2026-2/employee.sql</font>). "
        "For the class SQL Server, run <font face='Courier'>employee.sqlserver.sql</font>. "
        "The folder name ends in <font face='Courier'>-2</font> because this is "
        "the second experiment dated 30 September 2026."
    ))
    st.append(code_block(sql_text, size=6.2, leading=7.6))

    st.append(heading("7. Output"))
    st.append(para(
        "The script was executed in SQLite in memory. "
        "<font face='Courier'>CREATE</font> prints a status line and "
        "<font face='Courier'>INSERT</font> prints the row count. "
        "Each <font face='Courier'>SELECT</font> prints the result set that "
        "SQLite returned. Whole-number salaries print as integers."
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
            ["3", "7", "Names earning more than the overall average 56125.0"],
            ["4", "4", "Rajesh Kumar, Sneha Reddy, Priya Nair, Vikram Singh"],
            ["5", "1", "2nd highest salary = 90000"],
            ["6", "13", "IN: employees in CSE, Mechanical or ECE (a Professor exists)"],
            ["7", "3", "NOT IN: Rahul Das, Sneha Reddy and Tushar Rao (Civil)"],
            ["8", "12", "EXISTS: everyone except the 4 department-wise top salaries"],
            ["9", "6", "Salary greater than that department's own average"],
            ["10", "1", "CSE, total salary 296000, the greatest department total"],
        ],
        col_widths=[CONTENT_W * 0.12, CONTENT_W * 0.10, CONTENT_W * 0.68],
        pad=4,
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(para(
        "Question 3 returns seven employees above 56125.0, including Neha Gupta "
        "at 58000. Question 9 returns six employees above their own department "
        "average and does not include her: the ECE average is 58750.0. "
        "Fatima Khan (56000) is below both the company average and the CSE "
        "average (59200.0). Rahul Das earns exactly the Civil average (45000), "
        "so the strict comparison in question 9 excludes him, and 45000 is also "
        "below the company average. Question 8 returns 12 rows: 16 employees "
        "minus the four department maxima that question 4 lists. "
        "Question 5 returns one value, 90000, the largest salary below 92000."
    ))

    st.append(heading("9. Conclusion"))
    st.append(para(
        "A nested query uses one result as the input of another. A scalar "
        "subquery supplies a single comparison value. "
        "<font face='Courier'>IN</font> and <font face='Courier'>NOT IN</font> "
        "test membership. <font face='Courier'>EXISTS</font> tests whether any "
        "inner row matches. When the inner query refers to the outer row it is "
        "correlated, so each employee can be compared with their own department "
        "rather than with the whole company. The same nesting also answers "
        "&ldquo;which group has the greatest total?&rdquo; by taking "
        "<font face='Courier'>MAX</font> of a grouped <font face='Courier'>SUM</font>."
    ))
    return st


def build() -> None:
    st = build_story(include_cover=True)
    write_report(
        OUT_PDF,
        f"DBMS Lab · 30-09-2026 · Nested Queries · {STUDENT['name']}",
        st,
    )
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
